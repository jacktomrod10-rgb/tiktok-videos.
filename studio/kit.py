"""Everyday Genius video toolkit.

A video script (see examples/uk_plug.py) does:

    from studio.kit import *
    V = Video("uk-plug", episode=1,
              lines=["Spoken sentence one.", ...],          # what the voice says (spell years/numbers as words)
              display=["Caption with *highlight*.", ...])   # what the captions show (digits ok), same count
    @V.scene(0)            # scene shown while line 0 is spoken
    def intro(p, t, L): ...
    @V.scene(1, 2)         # scene covering lines 1..2
    def middle(p, t, L): ...
    V.main()               # CLI: tts | stills t1 t2 .. | render

Drawing: p is a Pen working in 1080x1920 output coordinates (drawn at 2x and downsampled).
L(i) -> (start, end) seconds of spoken line i, for timing animations.
Keep visuals inside x 60..1000, y 300..1150. Captions sit at y~1270; the top bar is automatic.
"""
import os, sys, json, math, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, S, FPS = 1080, 1920, 2, 30
SERIES = "EVERYDAY GENIUS"
BUILD_ROOT = "/home/claude/build"
MODEL_DIR = os.path.expanduser("~/.cache/kokoro")
MODEL_URLS = {
    "kokoro-v1.0.int8.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
VOICE, VOICE_LANG, VOICE_SPEED = "bm_george", "en-gb", 1.08

ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
DMSANS = "/usr/share/fonts/truetype/google-fonts/ofl/dmsans/DMSans[opsz,wght].ttf"

# ---------------- palette ----------------
BG1, BG2 = (11, 20, 36), (22, 40, 66)
YEL = (255, 210, 63)
WHITE = (244, 244, 241)
EDGE = (190, 196, 205)
BRASS, BRASS_D = (217, 164, 65), (160, 116, 38)
DARK = (30, 33, 38)
SLATE, SLATE_L = (42, 53, 70), (64, 80, 104)
ORANGE = (255, 140, 66)
RED = (255, 90, 95)
GREEN = (61, 220, 151)
BLUE = (90, 170, 255)
INK = (11, 18, 32)
MUTED = (159, 179, 200)

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / max(1e-6, t1 - t0))
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eback(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, x): return a + (b - a) * x
def pulse(t, period=1.2): return 0.5 + 0.5 * math.sin(2 * math.pi * t / period)

# ---------------- fonts ----------------
def dm(size, weight="Bold"):
    f = ImageFont.truetype(DMSANS, size)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f

_F2 = {}
def f2(kind, size):
    """Font for Pen.text (size in output px). kind: 'anton' | 'dm'."""
    key = (kind, int(size))
    if key not in _F2:
        _F2[key] = ImageFont.truetype(ANTON, int(size) * S) if kind == "anton" else dm(int(size) * S)
    return _F2[key]

# ---------------- pen (2x supersampled) ----------------
LOOK = os.environ.get("EG_LOOK", "1") != "0"     # premium look: shading, shadows, glow, grain (EG_LOOK=0 to compare)

class Pen:
    SHADE_MIN = 70          # shapes at least this big (1x px, both sides) get top-lit shading
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.shade = LOOK
    @staticmethod
    def _box(box):
        x0, y0, x1, y1 = box
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        return [x0 * S, y0 * S, x1 * S, y1 * S]
    class _Flat:
        def __init__(self, pen): self.pen = pen
        def __enter__(self): self.prev = self.pen.shade; self.pen.shade = False
        def __exit__(self, *a): self.pen.shade = self.prev
    def flat(self):
        """Use `with p.flat():` around glows and layered backgrounds that must stay smooth."""
        return Pen._Flat(self)
    def _solid(self, fill):
        return isinstance(fill, tuple) and (len(fill) == 3 or (len(fill) == 4 and fill[3] == 255))
    def _shaded(self, kind, b, fill, r=0):
        """Fill a shape with a soft top-lit gradient. Returns False if the shape is not eligible."""
        if not (self.shade and self._solid(fill)): return False
        w, h = int(b[2] - b[0]), int(b[3] - b[1])
        if w < self.SHADE_MIN * S or h < self.SHADE_MIN * S or (w > 640 * S and h > 640 * S): return False
        x0, y0 = int(b[0]), int(b[1])
        if w < 900 * S or h < 600 * S:                           # objects (not panels) also cast a soft shadow
            self.shadow([b[0] / S, b[1] / S, b[2] / S, b[3] / S], r / S if kind == 'rr' else (min(w, h) / S / 2 if kind == 'ell' else 4), dy=9, blur=11, alpha=85)
        mask = Image.new("L", (w + 1, h + 1), 0)
        md = ImageDraw.Draw(mask)
        if kind == "rr": md.rounded_rectangle([0, 0, w, h], radius=r, fill=255)
        elif kind == "ell": md.ellipse([0, 0, w, h], fill=255)
        else: md.rectangle([0, 0, w, h], fill=255)
        ys = np.linspace(0.0, 1.0, h + 1, dtype=np.float32)
        fac = 1.16 - 0.34 * ys                                    # lit from above
        fac = fac + 0.10 * np.exp(-((ys - 0.05) / 0.045) ** 2)    # soft top highlight
        fac = fac - 0.10 * np.exp(-((1 - ys) / 0.06) ** 2)        # contact darkening at the bottom edge
        col = np.clip(np.array(fill[:3], np.float32)[None, :] * fac[:, None], 0, 255).astype(np.uint8)
        grad = Image.fromarray(np.ascontiguousarray(np.broadcast_to(col[:, None, :], (h + 1, w + 1, 3))), "RGB")
        self.img.paste(grad, (x0, y0), mask)
        return True
    def shadow(self, box, r=20, dy=12, blur=16, alpha=110):
        """Soft drop shadow under a card or label (draw it before the shape)."""
        if not LOOK: return
        b = self._box(box)
        pad = int(blur * S * 2)
        w, h = int(b[2] - b[0]) + 2 * pad, int(b[3] - b[1]) + 2 * pad
        if w <= 2 * pad or h <= 2 * pad: return
        q = 4                                                   # blur at quarter size, then scale up (fast)
        sm = Image.new("RGBA", (max(1, w // q), max(1, h // q)), (0, 0, 0, 0))
        ImageDraw.Draw(sm).rounded_rectangle([pad / q, pad / q, (w - pad) / q, (h - pad) / q], radius=r * S / q, fill=(4, 8, 18, alpha))
        patch = sm.filter(ImageFilter.GaussianBlur(blur * S / 2 / q)).resize((w, h), Image.BILINEAR)
        x, y = int(b[0]) - pad, int(b[1]) - pad + int(dy * S)
        cx0, cy0 = max(0, -x), max(0, -y)
        cx1, cy1 = min(w, self.img.width - x), min(h, self.img.height - y)
        if cx1 <= cx0 or cy1 <= cy0: return
        self.img.alpha_composite(patch.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))
    def rr(self, box, r, fill=None, outline=None, width=0, shadow=False):
        b = self._box(box)
        r = max(0, min(r * S, (b[2] - b[0]) / 2, (b[3] - b[1]) / 2))
        if shadow: self.shadow(box, r / S)
        if self._shaded("rr", b, fill, int(r)):
            if outline: self.d.rounded_rectangle(b, radius=r, outline=outline, width=int(width * S))
            return
        self.d.rounded_rectangle(b, radius=r, fill=fill, outline=outline, width=int(width * S))
    def rect(self, box, fill=None, outline=None, width=0):
        b = self._box(box)
        if self._shaded("rect", b, fill):
            if outline: self.d.rectangle(b, outline=outline, width=int(width * S))
            return
        self.d.rectangle(b, fill=fill, outline=outline, width=int(width * S))
    def ell(self, box, fill=None, outline=None, width=0):
        b = self._box(box)
        if self._shaded("ell", b, fill):
            if outline: self.d.ellipse(b, outline=outline, width=int(width * S))
            return
        self.d.ellipse(b, fill=fill, outline=outline, width=int(width * S))
    def circle(self, cx, cy, r, fill=None, outline=None, width=0):
        self.ell([cx - r, cy - r, cx + r, cy + r], fill, outline, width)
    def line(self, pts, fill, width):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, int(width * S)), joint="curve")
    def poly(self, pts, fill, outline=None):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline)
    def arc(self, box, start, end, fill, width):
        self.d.arc(self._box(box), start, end, fill=fill, width=int(width * S))
    def text(self, xy, s, font, fill, anchor="mm"):
        self.d.text((xy[0] * S, xy[1] * S), s, font=font, fill=fill, anchor=anchor)
    def arrow(self, a, b, fill, width=10, head=34):
        self.line([a, b], fill, width)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        l, r = ang + math.radians(150), ang - math.radians(150)
        self.poly([b, (b[0] + head * math.cos(l), b[1] + head * math.sin(l)),
                   (b[0] + head * math.cos(r), b[1] + head * math.sin(r))], fill)

# ---------------- reusable widgets ----------------
def pill(p, cx, cy, s, pop, bg=YEL, fg=INK, size=40):
    """Label pill that pops in. pop: 0..1 (use prog(...) * (1 - prog(...)) to pop out)."""
    if pop <= 0: return
    sc = eback(clamp(pop))
    font = f2("dm", max(8, int(size * sc)))
    w = len(s) * size * 0.62 * sc + 48 * sc
    h = size * 1.6 * sc
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2, fill=bg, shadow=True)
    p.text((cx, cy + 1), s, font, fg)

def sparkle(p, cx, cy, r, fill=YEL):
    p.poly([(cx, cy - r), (cx + r * .3, cy - r * .3), (cx + r, cy), (cx + r * .3, cy + r * .3),
            (cx, cy + r), (cx - r * .3, cy + r * .3), (cx - r, cy), (cx - r * .3, cy - r * .3)], fill=fill)

def tick(p, cx, cy, r, pop):
    if pop <= 0: return
    r *= eback(clamp(pop))
    p.circle(cx, cy, r, fill=GREEN)
    p.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .35), (cx + r * .5, cy - r * .35)], fill=INK, width=max(2, r * .2))

def cross(p, cx, cy, r, pop, shake_t=0.0):
    if pop <= 0: return
    r *= eback(clamp(pop))
    cx += math.sin(shake_t * 60) * 10 * (1 - clamp(shake_t / 0.4))
    p.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED, width=r * .3)
    p.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED, width=r * .3)

def big_number(p, t, t0, value, cx=540, cy=640, size=300, start=None, dur=1.0, fill=YEL, fmt="{}"):
    """Counts up from start to value beginning at t0."""
    if t < t0: return
    start = value * 0.6 if start is None else start
    k = eo(prog(t, t0, t0 + dur))
    v = lerp(start, value, k)
    v = int(round(v)) if isinstance(value, int) else round(v, 1)
    pop = eback(prog(t, t0, t0 + 0.35))
    p.text((cx, cy), fmt.format(v), f2("anton", max(10, int(size * pop))), fill)

def path_point(path, u):
    segs = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
    lens = [math.dist(a, b) for a, b in segs]
    d = (u % 1.0) * sum(lens)
    for (a, b), l in zip(segs, lens):
        if d <= l:
            k = d / max(l, 1e-6)
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        d -= l
    return path[-1]

def flow_dots(p, path, t, speed=0.5, n=8, r=13, fill=YEL):
    """Dots travelling along a polyline (current, air, water...)."""
    for k in range(n):
        x, y = path_point(path, t * speed / 2 + k / n)
        p.circle(x, y, r, fill=fill)

def bar_chart(p, t, t0, items, x0=120, y0=420, w=840, bar_h=70, gap=36, colour=YEL, size=36):
    """items: [(label, value)]; bars grow from t0, staggered."""
    vmax = max(v for _, v in items) or 1
    for i, (label, v) in enumerate(items):
        k = eo(prog(t, t0 + i * 0.15, t0 + i * 0.15 + 0.8))
        y = y0 + i * (bar_h + gap)
        p.text((x0, y - 6), label, f2("dm", size), WHITE, anchor="ls")
        p.rr([x0, y + 6, x0 + max(bar_h * .5, w * v / vmax * k), y + 6 + bar_h * .7], 12, fill=colour)

# ---------------- background ----------------
def make_bg():
    y = np.linspace(0, 1, H)[:, None, None]
    c1, c2 = np.array(BG1, float), np.array(BG2, float)
    arr = np.broadcast_to(c1 + (c2 - c1) * y, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - 540) ** 2 + (yy - 760) ** 2) / 520
    glow = np.clip(1 - d, 0, 1)[..., None] * 0.15
    arr = arr * (1 - glow) + np.array((40, 70, 110), float) * glow
    return Image.fromarray(arr.astype(np.uint8), "RGB")


# ---------------- premium finish ----------------
_BOKEH = None
def bokeh(img, t):
    """Slowly drifting soft lights in the background, for depth (only visible where scenes leave the background)."""
    global _BOKEH
    if _BOKEH is None:
        rng = np.random.default_rng(3)
        lay = Image.new("RGBA", (W, H + 600), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for _ in range(26):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H + 600), rng.uniform(18, 70)
            c = [(90, 140, 220), (120, 110, 220), (240, 200, 120)][int(rng.integers(0, 3))]
            d.ellipse([x - r, y - r, x + r, y + r], fill=c + (int(rng.uniform(18, 44)),))
        _BOKEH = lay.filter(ImageFilter.GaussianBlur(10))
    off = int((t * 14) % 600)
    piece = _BOKEH.crop((0, 600 - off, W, 600 - off + H))
    img.paste(piece, (0, 0), piece)

_GRAIN = None
def finish(img, t):
    """Glow on bright areas, local contrast, gentle colour grade and fine grain."""
    global _GRAIN
    arr = np.asarray(img, dtype=np.float32)
    q = img.resize((W // 4, H // 4), Image.BILINEAR)
    qa = np.asarray(q, dtype=np.float32)
    lum = qa @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    bright = Image.fromarray(np.clip(qa * np.clip((lum - 170) / 85, 0, 1)[..., None], 0, 255).astype(np.uint8))
    glow = np.asarray(bright.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR), dtype=np.float32)
    soft = np.asarray(q.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR), dtype=np.float32)
    arr = arr + (arr - soft) * 0.22 + glow * 0.38                 # local contrast + bloom
    g = arr.mean(axis=2, keepdims=True)
    arr = g + (arr - g) * 1.08                                     # a touch more colour
    arr = 255 * (np.clip(arr, 0, 255) / 255) ** 1.04               # deeper shadows
    if _GRAIN is None:
        rng = np.random.default_rng(11)
        _GRAIN = rng.normal(0, 1.6, (H, W, 1)).astype(np.float32)   # static fine grain: texture without bloating files
    arr = arr + _GRAIN
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

# ---------------- voice ----------------
def ensure_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for name, url in MODEL_URLS.items():
        path = os.path.join(MODEL_DIR, name)
        if not os.path.exists(path) or os.path.getsize(path) < 1_000_000:
            subprocess.run(["curl", "-sL", "-m", "300", "-o", path, url], check=True)

def _pitch(samples, sr, factor):
    import soundfile as sf, tempfile
    with tempfile.TemporaryDirectory() as td:
        a, b = os.path.join(td, "a.wav"), os.path.join(td, "b.wav")
        sf.write(a, samples, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-af", f"rubberband=pitch={factor}:formant=preserved", b], check=True)
        out, _ = sf.read(b, dtype="float32")
    return out

def synth_lines(lines, out_dir, gap=0.30, lead=0.15, voice=None, lang=None, speed=None, cast=None, holds=None):
    """lines: str (narrator) or (speaker, text). cast: {speaker: dict(voice, lang, speed, pitch)}."""
    voice, lang, speed = voice or VOICE, lang or VOICE_LANG, speed or VOICE_SPEED
    cast = cast or {}
    import soundfile as sf
    from kokoro_onnx import Kokoro
    ensure_models()
    k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.int8.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    chunks, info, t, sr_out = [], [], lead, 24000
    for i, item in enumerate(lines):
        speaker, text = (item if isinstance(item, (tuple, list)) else ("narrator", item))
        c = cast.get(speaker, {})
        v, lg, sp, pf = c.get("voice", voice), c.get("lang", lang), c.get("speed", speed), c.get("pitch", 1.0)
        samples, sr = k.create(text, voice=v, speed=sp, lang=lg)
        sr_out = sr
        samples = np.asarray(samples, dtype=np.float32)
        if abs(pf - 1.0) > 0.01:
            samples = _pitch(samples, sr, pf)
        idx = np.where(np.abs(samples) > 0.01)[0]
        if len(idx):
            samples = samples[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
        dur = len(samples) / sr
        # loudness envelope at 30 fps (for lip sync) and pauses inside the line (for caption timing)
        hop = sr // 30
        env = [float(np.sqrt(np.mean(samples[j:j + hop] ** 2))) for j in range(0, len(samples), hop)]
        peak = max(env) if env else 1.0
        env = [round(min(1.0, e / (peak * 0.7 + 1e-9)), 3) for e in env]
        pauses, run = [], 0
        for j, e in enumerate(env):
            if e < 0.06:
                run += 1
            else:
                if run >= 3 and j - run > 2:
                    pauses.append([round((j - run) / 30, 3), round(j / 30, 3)])
                run = 0
        info.append({"i": i, "speaker": speaker, "text": text, "start": round(t, 3), "dur": round(dur, 3),
                     "phonemes": k.tokenizer.phonemize(text, lg), "env": env, "pauses": pauses})
        g = gap + (holds or {}).get(i, 0.0)     # holds: extra silence after line i (music-only moments)
        chunks += [samples, np.zeros(int(g * sr), dtype=np.float32)]
        t += dur + g
    voice = np.concatenate([np.zeros(int(lead * sr_out), dtype=np.float32)] + chunks)
    sf.write(os.path.join(out_dir, "voice.wav"), voice, sr_out)
    timing = {"sr": sr_out, "total": round(len(voice) / sr_out, 3), "lines": info}
    json.dump(timing, open(os.path.join(out_dir, "timing.json"), "w"), indent=1)
    return timing

SR = 44100

def _env(n, a=0.005, d=0.3, sr=SR):
    t = np.arange(n) / sr
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))

def sfx(kind, sr=SR):
    """Synthesised sound effects: pop, whoosh, cash, ding, boing, thud."""
    rng = np.random.default_rng(7)
    if kind == "pop":
        n = int(0.09 * sr); t = np.arange(n) / sr
        f = 900 * np.exp(-t * 30) + 300
        return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(n, 0.002, 0.03)
    if kind == "whoosh":
        n = int(0.45 * sr); t = np.arange(n) / sr
        noise = rng.standard_normal(n)
        k = np.exp(-((t - 0.22) / 0.12) ** 2)
        # crude band-pass sweep: running mean difference
        lo = np.convolve(noise, np.ones(6) / 6, "same"); hi = np.convolve(noise, np.ones(40) / 40, "same")
        return 0.35 * (lo - hi) * k
    if kind == "cash":
        out = []
        for f0, d0 in ((2093, 0.25), (2637, 0.5)):
            n = int(d0 * sr); t = np.arange(n) / sr
            out.append(0.35 * (np.sin(2 * np.pi * f0 * t) + 0.4 * np.sin(2 * np.pi * f0 * 2.01 * t)) * _env(n, 0.002, d0 / 3))
        click = 0.4 * rng.standard_normal(int(0.02 * sr)) * _env(int(0.02 * sr), 0.001, 0.005)
        return np.concatenate([click, out[0], out[1]])
    if kind == "ding":
        n = int(0.8 * sr); t = np.arange(n) / sr
        return 0.4 * (np.sin(2 * np.pi * 1318.5 * t) + 0.3 * np.sin(2 * np.pi * 2637 * t)) * _env(n, 0.002, 0.25)
    if kind == "boing":
        n = int(0.35 * sr); t = np.arange(n) / sr
        f = 220 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 6)
        return 0.5 * np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(n, 0.003, 0.15)
    if kind == "thud":
        n = int(0.25 * sr); t = np.arange(n) / sr
        f = 120 * np.exp(-t * 12) + 45
        return 0.8 * np.sin(2 * np.pi * np.cumsum(f) / sr) * _env(n, 0.002, 0.08)
    return np.zeros(1)

def music(total, style="pad", sr=SR):
    t = np.arange(int(total * sr)) / sr
    out = np.zeros_like(t)
    if style == "pluck":
        # bouncy major-key arpeggio with a soft bass: I - V - vi - IV, 104 bpm eighth notes
        beat = 60 / 104 / 2
        prog_ = [[261.63, 329.63, 392.00, 523.25], [196.00, 246.94, 293.66, 392.00],
                 [220.00, 261.63, 329.63, 440.00], [174.61, 220.00, 261.63, 349.23]]
        n_steps = int(total / beat) + 1
        nl = int(0.35 * sr)
        tt = np.arange(nl) / sr
        for i in range(n_steps):
            ch = prog_[(i // 8) % 4]
            f = ch[[0, 2, 1, 3, 2, 1, 3, 2][i % 8]]
            tone = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt)) * _env(nl, 0.003, 0.09)
            a = int(i * beat * sr)
            seg = out[a:a + nl]; seg += tone[:len(seg)] * 0.5
            if i % 4 == 0:
                fb = ch[0] / 2
                bl = int(0.5 * sr); tb = np.arange(bl) / sr
                bass = np.sin(2 * np.pi * fb * tb) * _env(bl, 0.005, 0.25)
                seg2 = out[a:a + bl]; seg2 += bass[:len(seg2)] * 0.6
    else:
        chords = [[130.81, 164.81, 196.00, 246.94], [110.00, 130.81, 164.81, 196.00],
                  [87.31, 130.81, 164.81, 220.00], [98.00, 123.47, 146.83, 164.81]]
        seg = 8.0
        for i in range(int(np.ceil(total / seg)) + 1):
            env = np.clip(1 - np.abs((t - (i * seg + seg / 2)) / (seg * 0.75)), 0, 1) ** 1.5
            for f in chords[i % 4]:
                out += (np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.003 * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env
        out *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * t))
    out *= np.clip(np.minimum(t / 1.0, (total - t) / 1.5), 0, 1)
    return out / (np.max(np.abs(out)) + 1e-9)

def make_audio(out_dir, total, style="pad", cues=()):
    import soundfile as sf
    m = music(total, style)
    fx = np.zeros(int(total * SR) + SR)
    for tc, kind in cues:
        clip = sfx(kind)
        a = int(max(0, tc) * SR)
        seg = fx[a:a + len(clip)]; seg += clip[:len(seg)]
    fx = fx[:len(m)]
    sf.write(os.path.join(out_dir, "music.wav"), (m * 0.5).astype(np.float32), SR)
    sf.write(os.path.join(out_dir, "sfx.wav"), np.clip(fx, -1, 1).astype(np.float32), SR)
    mvol = "0.13" if style == "pluck" else "0.11"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out_dir, "voice.wav"),
                    "-i", os.path.join(out_dir, "music.wav"), "-i", os.path.join(out_dir, "sfx.wav"), "-filter_complex",
                    f"[0:a]aresample=44100,highpass=f=70[v];[1:a]lowpass=f=3000,volume={mvol}[m];[2:a]volume=0.32[x];"
                    "[v][m][x]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "[a]", "-ar", "44100", "-c:a", "aac", "-b:a", "192k",
                    os.path.join(out_dir, "mix.m4a")], check=True)

# ---------------- captions ----------------
CAP_FONT = None
def _cap_font():
    global CAP_FONT
    if CAP_FONT is None: CAP_FONT = ImageFont.truetype(ANTON, 92)
    return CAP_FONT

def _wweight(w):
    core = w.replace("*", "")
    return len(core) + 2 + (4 if core[-1:] in ".,!?:;" else 0)

def build_chunks(display, lines_info, total):
    """Caption chunks of up to 4 words, each with per-word timings (proportional to word length)."""
    out = []
    for i, text in enumerate(display):
        words = text.split()
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 4 or (w.rstrip("*")[-1:] in ".,!?:" and len(cur) >= 2):
                groups.append(cur); cur = []
        if cur:
            if groups and len(cur) == 1: groups[-1] += cur
            else: groups.append(cur)
        s0, d = lines_info[i]["start"], lines_info[i]["dur"]
        # phrases end at punctuation; align phrase breaks with real pauses in the audio when they match
        phrases, curp = [], []
        for w in words:
            curp.append(w)
            if w.replace("*", "")[-1:] in ".,!?:;":
                phrases.append(curp); curp = []
        if curp: phrases.append(curp)
        pauses = sorted(lines_info[i].get("pauses") or [], key=lambda q: q[1] - q[0], reverse=True)
        nb = len(phrases) - 1
        spans = None
        if nb > 0 and len(pauses) >= nb:
            use = sorted(pauses[:nb])
            edges = [0.0] + [x for q in use for x in q] + [d]
            spans = [(edges[2 * k], edges[2 * k + 1]) for k in range(nb + 1)]
            if any(b <= a for a, b in spans): spans = None
        if spans is None:
            tw = sum(_wweight(w) for w in words)
            spans, acc = [], 0.0
            for ph in phrases:
                dd = d * sum(_wweight(w) for w in ph) / tw
                spans.append((acc, acc + dd)); acc += dd
        word_t = []
        for ph, (a, b) in zip(phrases, spans):
            tw = sum(_wweight(w) for w in ph)
            t = s0 + a
            for w in ph:
                dd = (b - a) * _wweight(w) / tw
                word_t.append((t, t + dd)); t += dd
        k = 0
        for g in groups:
            wt = word_t[k:k + len(g)]; k += len(g)
            out.append([wt[0][0], wt[-1][1], g, wt])
    for j in range(len(out)):
        nxt = out[j + 1][0] if j + 1 < len(out) else total
        out[j][1] = max(out[j][1], nxt)
    return [tuple(c) for c in out]

_CAP_CACHE = {}
def caption_img(words, active=None, colour=None):
    key = (" ".join(words), active, colour)
    if key in _CAP_CACHE: return _CAP_CACHE[key]
    font = _cap_font()
    toks = [(w.replace("*", "").upper(), "*" in w) for w in words]
    space, maxw, lh = 24, 900, 118
    widths = [font.getbbox(tk)[2] - font.getbbox(tk)[0] for tk, _ in toks]
    lines, cur, cw = [], [], 0
    for idx, ((tk, hl), w) in enumerate(zip(toks, widths)):
        if cur and cw + space + w > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((tk, hl, w, idx)); cw += (space if len(cur) > 1 else 0) + w
    lines.append(cur)
    img = Image.new("RGBA", (W, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for li, ln in enumerate(lines):
        x = (W - (sum(w for _, _, w, _ in ln) + space * (len(ln) - 1))) / 2
        for tk, hl, w, idx in ln:
            y = 20 + li * lh
            if idx == active:
                bb = font.getbbox(tk)
                d.rounded_rectangle([x - 14, y + bb[1] - 12, x + w + 14, y + bb[3] + 12], radius=18, fill=INK)
                d.rounded_rectangle([x - 10, y + bb[1] - 8, x + w + 10, y + bb[3] + 8], radius=16, fill=YEL)
                d.text((x, y), tk, font=font, fill=INK)
            else:
                d.text((x, y), tk, font=font, fill=YEL if hl else (colour or (255, 255, 255)), stroke_width=9, stroke_fill=INK)
            x += w + space
    _CAP_CACHE[key] = img
    return img

def _title_img(text):
    """Headline (up to 2 lines) shown under the series tag; *word* = yellow."""
    font = ImageFont.truetype(ANTON, 54)
    words = text.split()
    lines, cur = [], []
    for w in words:
        trial = " ".join(x.replace("*", "") for x in cur + [w]).upper()
        if cur and font.getlength(trial) > 900:
            lines.append(cur); cur = []
        cur.append(w)
    lines.append(cur)
    lines = lines[:2]
    img = Image.new("RGBA", (W, 64 * len(lines) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for li, ln in enumerate(lines):
        toks = [(w.replace("*", "").upper(), "*" in w) for w in ln]
        total = sum(font.getlength(tk) for tk, _ in toks) + 16 * (len(toks) - 1)
        x = (W - total) / 2
        for tk, hl in toks:
            d.text((x, li * 64), tk, font=font, fill=YEL if hl else WHITE, stroke_width=6, stroke_fill=INK)
            x += font.getlength(tk) + 16
    return img

# ---------------- the video ----------------
class Video:
    def __init__(self, slug, lines, display, episode=1, series=SERIES, voice=None, voice_lang=None,
                 music="pad", camera=True, vignette=True, cast=None, speaker_colours=None, title=None, holds=None):
        assert len(lines) == len(display), "lines and display must have the same count"
        self.slug, self.lines, self.display, self.episode, self.series = slug, lines, display, episode, series
        self.voice, self.voice_lang = voice, voice_lang
        self.music, self.camera, self.vignette = music, camera, vignette
        self.cast, self.speaker_colours = cast or {}, speaker_colours or {}
        self.title = title          # persistent headline under the series tag (explainers)
        self.holds = holds or {}    # {line index: extra seconds of silence after it}
        self.cues = []            # (seconds, kind) sound effects; scene changes get a whoosh automatically
        self.fixed_fns = []       # drawn in the top band (y < 330), not moved by the camera
        self._vig = None
        self.dir = os.path.join(BUILD_ROOT, slug)
        os.makedirs(self.dir, exist_ok=True)
        self.scenes = []          # (first_line, last_line, fn)
        self._timing = None
        self._bg = None
        self._tag_font = dm(30)

    # decorator
    def scene(self, first, last=None):
        def deco(fn):
            self.scenes.append((first, first if last is None else last, fn))
            self.scenes.sort(key=lambda s: s[0])
            return fn
        return deco

    def fixed(self, fn):
        """Decorator: fn(p, t) draws in the top band (y < 330) and is not zoomed by the camera."""
        self.fixed_fns.append(fn)
        return fn

    def sounds(self, fn):
        """Decorator: fn(L) returns [(seconds, kind), ...] sound cues, computed from the voice timing."""
        self.cue_fn = fn
        return fn

    def speaking(self, t):
        """(speaker, loudness 0..1) for the line being spoken at time t, else (None, 0)."""
        for li in self.timing["lines"]:
            if li["start"] <= t < li["start"] + li["dur"]:
                env = li.get("env") or []
                j = int((t - li["start"]) * 30)
                return li.get("speaker", "narrator"), (env[j] if 0 <= j < len(env) else 0.0)
        return None, 0.0

    def talk(self, t, who):
        sp, amp = self.speaking(t)
        return amp if sp == who else 0.0

    def cue(self, t, kind):
        """Add a sound effect at time t: pop, whoosh, cash, ding, boing, thud."""
        self.cues.append((t, kind))

    @property
    def timing(self):
        if self._timing is None:
            path = os.path.join(self.dir, "timing.json")
            if not os.path.exists(path):
                sys.exit("run `tts` first")
            self._timing = json.load(open(path))
        return self._timing

    def L(self, i):
        li = self.timing["lines"][i]
        return li["start"], li["start"] + li["dur"]

    def bounds(self):
        total = self.timing["total"]
        out = []
        for k, (a, b, fn) in enumerate(self.scenes):
            s0 = 0.0 if k == 0 else self.timing["lines"][a]["start"] - 0.3
            out.append([s0, None, fn])
        for k in range(len(out)):
            out[k][1] = out[k + 1][0] if k + 1 < len(out) else total
        return out

    def frame(self, t):
        if self._bg is None:
            self._bg = make_bg()
            self._chunks = build_chunks(self.display, self.timing["lines"], self.timing["total"])
            self._chunk_speaker = []
            for c in self._chunks:
                sp = "narrator"
                for li in self.timing["lines"]:
                    if li["start"] - 0.05 <= c[3][0][0] < li["start"] + li["dur"] + 0.05:
                        sp = li.get("speaker", "narrator"); break
                self._chunk_speaker.append(sp)
        layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        p = Pen(layer)
        B = self.bounds()
        alpha = 1.0
        for k, (s0, s1, fn) in enumerate(B):
            if s0 <= t < s1 or (k == len(B) - 1 and t >= s0):
                fn(p, t, self.L)
                fi = prog(t, s0, s0 + 0.22) if k > 0 else 1.0
                fo = 1 - prog(t, s1 - 0.18, s1) if k < len(B) - 1 else 1.0
                alpha = min(fi, fo)
                break
        small = layer.reduce(S)
        if self.camera:
            # slow push-in per scene, alternating zoom centre for variety
            z, cx, cy = 1.0, 540, 760
            for k, (s0, s1, fn) in enumerate(B):
                if s0 <= t < s1 or (k == len(B) - 1 and t >= s0):
                    z = 1.0 + 0.045 * eio(prog(t, s0, s1))
                    cx = 540 + (30 if k % 2 else -30) * prog(t, s0, s1)
                    cy = 760
                    break
            if z > 1.001:
                w, h = W / z, H / z
                x0 = min(max(0.0, cx - w / 2), W - w)
                y0 = min(max(0.0, cy - h * (cy / H)), H - h)
                box = (x0, y0, x0 + w, y0 + h)
                small = small.resize((W, H), Image.BILINEAR, box=box)
        if alpha < 1:
            small.putalpha(small.getchannel("A").point(lambda v: int(v * alpha)))
        img = self._bg.copy()
        if LOOK:
            bokeh(img, t)
        img.paste(small, (0, 0), small)
        if self.fixed_fns:
            band = Image.new("RGBA", (W * S, 330 * S), (0, 0, 0, 0))
            bp = Pen(band)
            for fn in self.fixed_fns: fn(bp, t)
            bs = band.reduce(S)
            img.paste(bs, (0, 0), bs)
        if self.vignette:
            if self._vig is None:
                yy, xx = np.mgrid[0:H, 0:W]
                d = np.sqrt(((xx - 540) / 700) ** 2 + ((yy - 760) / 1000) ** 2)
                a = (np.clip(d - 0.55, 0, 1) * 150).astype(np.uint8)
                self._vig = Image.fromarray(np.dstack([np.zeros_like(a)] * 3 + [a]), "RGBA")
            img = img.convert("RGBA"); img.alpha_composite(self._vig); img = img.convert("RGB")
        if LOOK:
            img = finish(img, t)
        return self._overlay(img, t)

    def _overlay(self, img, t):
        d = ImageDraw.Draw(img)
        total = self.timing["total"]
        d.rounded_rectangle([80, 150, 1000, 158], radius=4, fill=(40, 58, 84))
        d.rounded_rectangle([80, 150, 80 + 920 * clamp(t / total), 158], radius=4, fill=YEL)
        tag = self.series if self.episode is None else f"{self.series}  ·  #{self.episode:02d}"
        d.text((80, 182), tag, font=self._tag_font, fill=MUTED)
        if self.title:
            if not hasattr(self, "_title_img"):
                self._title_img = _title_img(self.title)
            ti = self._title_img
            k = eback(prog(t, 0.0, 0.4))
            if k > 0:
                im = ti if k >= 0.999 else ti.resize((max(1, int(ti.width * k)), max(1, int(ti.height * k))), Image.BILINEAR)
                img.paste(im, ((W - im.width) // 2, 228 + (ti.height - im.height) // 2), im)
        for ci, (a, b, g, wt) in enumerate(self._chunks):
            if a <= t < b:
                active = None
                for wi, (ws, we) in enumerate(wt):
                    if ws <= t < we: active = wi
                cap = caption_img(g, active, self.speaker_colours.get(self._chunk_speaker[ci]))
                sc = lerp(0.82, 1.0, eback(prog(t, a, a + 0.14)))
                im = cap if sc == 1.0 else cap.resize((max(1, int(cap.width * sc)), max(1, int(cap.height * sc))), Image.BILINEAR)
                img.paste(im, ((W - im.width) // 2, 1270 - im.height // 2 + (cap.height - im.height) // 2), im)
                break
        return img

    # ---- outputs ----
    def tts(self):
        timing = synth_lines(self.lines, self.dir, voice=self.voice, lang=self.voice_lang, cast=self.cast, holds=self.holds)
        self._timing = timing
        for li in timing["lines"]:
            print(f"[{li['start']:6.2f} +{li['dur']:5.2f}] {li['text']}\n           /{li['phonemes']}/")
        print("TOTAL", timing["total"], "s")

    def stills(self, times):
        os.makedirs(os.path.join(self.dir, "stills"), exist_ok=True)
        paths = []
        for t in times:
            path = os.path.join(self.dir, "stills", f"t{t:05.1f}.png")
            self.frame(t).save(path); paths.append(path)
        sheet = os.path.join(self.dir, "stills", "sheet.png")
        subprocess.run(["convert"] + paths + ["-resize", "432x768", "+append", sheet], check=True)
        print("contact sheet:", sheet)

    def _render_scene(self, k, s0, s1):
        n0, n1 = int(round(s0 * FPS)), int(round(s1 * FPS))
        tmp, final = os.path.join(self.dir, f"scene_{k}.tmp.mp4"), os.path.join(self.dir, f"scene_{k}.mp4")
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                 "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                                 "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for n in range(n0, n1):
            proc.stdin.write(self.frame(n / FPS).tobytes())
        proc.stdin.close()
        if proc.wait() != 0: sys.exit(f"ffmpeg failed on scene {k}")
        os.replace(tmp, final)
        return final

    def render(self, out_path=None):
        B = self.bounds()
        files = [self._render_scene(k, s0, s1) for k, (s0, s1, _) in enumerate(B)]
        cues = [(s0, "whoosh") for (s0, s1, fn) in B[1:]] + list(self.cues)
        if getattr(self, "cue_fn", None):
            cues += list(self.cue_fn(self.L))
        make_audio(self.dir, self.timing["total"], self.music, cues)
        lst = os.path.join(self.dir, "list.txt")
        open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
        vid = os.path.join(self.dir, "video_only.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
        out_path = out_path or os.path.join(self.dir, f"{self.slug}.mp4")
        tmp = out_path[:-4] + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", os.path.join(self.dir, "mix.m4a"),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-shortest",
                        "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, out_path)
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", out_path],
                               capture_output=True, text=True).stdout
        print("rendered", out_path, probe.replace("\n", " "))
        return out_path

    def main(self):
        cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
        if cmd == "tts": self.tts()
        elif cmd == "stills": self.stills([float(x) for x in sys.argv[2:]])
        elif cmd == "render": self.render(sys.argv[2] if len(sys.argv) > 2 else None)
        else: print("usage: python3 script.py tts | stills t1 t2 ... | render [out.mp4]")
