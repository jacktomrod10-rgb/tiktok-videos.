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
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1080, 1920, 2, 30
SERIES = "EVERYDAY GENIUS"
BUILD_ROOT = "/home/claude/build"
MODEL_DIR = os.path.expanduser("~/.cache/kokoro")
MODEL_URLS = {
    "kokoro-v1.0.int8.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
VOICE, VOICE_LANG, VOICE_SPEED = "bf_emma", "en-gb", 1.08

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
class Pen:
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)
    @staticmethod
    def _box(box):
        x0, y0, x1, y1 = box
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        return [x0 * S, y0 * S, x1 * S, y1 * S]
    def rr(self, box, r, fill=None, outline=None, width=0):
        b = self._box(box)
        r = max(0, min(r * S, (b[2] - b[0]) / 2, (b[3] - b[1]) / 2))
        self.d.rounded_rectangle(b, radius=r, fill=fill, outline=outline, width=int(width * S))
    def rect(self, box, fill=None, outline=None, width=0):
        self.d.rectangle(self._box(box), fill=fill, outline=outline, width=int(width * S))
    def ell(self, box, fill=None, outline=None, width=0):
        self.d.ellipse(self._box(box), fill=fill, outline=outline, width=int(width * S))
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
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2, fill=bg)
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

# ---------------- voice ----------------
def ensure_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    for name, url in MODEL_URLS.items():
        path = os.path.join(MODEL_DIR, name)
        if not os.path.exists(path) or os.path.getsize(path) < 1_000_000:
            subprocess.run(["curl", "-sL", "-m", "300", "-o", path, url], check=True)

def synth_lines(lines, out_dir, gap=0.30, lead=0.15):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    ensure_models()
    k = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.int8.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    chunks, info, t, sr_out = [], [], lead, 24000
    for i, text in enumerate(lines):
        samples, sr = k.create(text, voice=VOICE, speed=VOICE_SPEED, lang=VOICE_LANG)
        sr_out = sr
        samples = np.asarray(samples, dtype=np.float32)
        idx = np.where(np.abs(samples) > 0.01)[0]
        if len(idx):
            samples = samples[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
        dur = len(samples) / sr
        info.append({"i": i, "text": text, "start": round(t, 3), "dur": round(dur, 3),
                     "phonemes": k.tokenizer.phonemize(text, VOICE_LANG)})
        chunks += [samples, np.zeros(int(gap * sr), dtype=np.float32)]
        t += dur + gap
    voice = np.concatenate([np.zeros(int(lead * sr_out), dtype=np.float32)] + chunks)
    sf.write(os.path.join(out_dir, "voice.wav"), voice, sr_out)
    timing = {"sr": sr_out, "total": round(len(voice) / sr_out, 3), "lines": info}
    json.dump(timing, open(os.path.join(out_dir, "timing.json"), "w"), indent=1)
    return timing

def make_audio(out_dir, total):
    import soundfile as sf
    sr = 44100
    t = np.arange(int(total * sr)) / sr
    chords = [[130.81, 164.81, 196.00, 246.94], [110.00, 130.81, 164.81, 196.00],
              [87.31, 130.81, 164.81, 220.00], [98.00, 123.47, 146.83, 164.81]]
    pad = np.zeros_like(t)
    seg = 8.0
    for i in range(int(np.ceil(total / seg)) + 1):
        env = np.clip(1 - np.abs((t - (i * seg + seg / 2)) / (seg * 0.75)), 0, 1) ** 1.5
        for f in chords[i % 4]:
            pad += (np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.003 * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env
    pad *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * t)) * np.clip(np.minimum(t / 1.0, (total - t) / 1.5), 0, 1)
    pad /= np.max(np.abs(pad)) + 1e-9
    sf.write(os.path.join(out_dir, "pad.wav"), (pad * 0.5).astype(np.float32), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out_dir, "voice.wav"),
                    "-i", os.path.join(out_dir, "pad.wav"), "-filter_complex",
                    "[0:a]aresample=44100,highpass=f=70[v];[1:a]lowpass=f=1800,volume=0.11[m];"
                    "[v][m]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "[a]", "-ar", "44100", "-c:a", "aac", "-b:a", "192k",
                    os.path.join(out_dir, "mix.m4a")], check=True)

# ---------------- captions ----------------
CAP_FONT = None
def _cap_font():
    global CAP_FONT
    if CAP_FONT is None: CAP_FONT = ImageFont.truetype(ANTON, 92)
    return CAP_FONT

def build_chunks(display, lines_info, total):
    out = []
    for i, text in enumerate(display):
        words = text.split()
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 4 or (w.rstrip("*")[-1:] in ".,!?" and len(cur) >= 2):
                groups.append(cur); cur = []
        if cur:
            if groups and len(cur) == 1: groups[-1] += cur
            else: groups.append(cur)
        weights = [sum(len(w.replace("*", "")) + 1 for w in g) + (5 if g[-1].rstrip("*")[-1:] in ".,!?" else 0) for g in groups]
        s, d = lines_info[i]["start"], lines_info[i]["dur"]
        tw, t = sum(weights), s
        for g, wt in zip(groups, weights):
            dd = d * wt / tw
            out.append((t, t + dd, g)); t += dd
    return [(a, max(b, out[j + 1][0] if j + 1 < len(out) else total), g) for j, (a, b, g) in enumerate(out)]

_CAP_CACHE = {}
def caption_img(words):
    key = " ".join(words)
    if key in _CAP_CACHE: return _CAP_CACHE[key]
    font = _cap_font()
    toks = [(w.replace("*", "").upper(), "*" in w) for w in words]
    space, maxw, lh = 24, 900, 118
    widths = [font.getbbox(tk)[2] - font.getbbox(tk)[0] for tk, _ in toks]
    lines, cur, cw = [], [], 0
    for (tk, hl), w in zip(toks, widths):
        if cur and cw + space + w > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((tk, hl, w)); cw += (space if len(cur) > 1 else 0) + w
    lines.append(cur)
    img = Image.new("RGBA", (W, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for li, ln in enumerate(lines):
        x = (W - (sum(w for _, _, w in ln) + space * (len(ln) - 1))) / 2
        for tk, hl, w in ln:
            d.text((x, 20 + li * lh), tk, font=font, fill=YEL if hl else (255, 255, 255), stroke_width=9, stroke_fill=INK)
            x += w + space
    _CAP_CACHE[key] = img
    return img

# ---------------- the video ----------------
class Video:
    def __init__(self, slug, lines, display, episode=1, series=SERIES):
        assert len(lines) == len(display), "lines and display must have the same count"
        self.slug, self.lines, self.display, self.episode, self.series = slug, lines, display, episode, series
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
        if alpha < 1:
            small.putalpha(small.getchannel("A").point(lambda v: int(v * alpha)))
        img = self._bg.copy()
        img.paste(small, (0, 0), small)
        return self._overlay(img, t)

    def _overlay(self, img, t):
        d = ImageDraw.Draw(img)
        total = self.timing["total"]
        d.rounded_rectangle([80, 150, 1000, 158], radius=4, fill=(40, 58, 84))
        d.rounded_rectangle([80, 150, 80 + 920 * clamp(t / total), 158], radius=4, fill=YEL)
        d.text((80, 182), f"{self.series}  ·  #{self.episode:02d}", font=self._tag_font, fill=MUTED)
        for a, b, g in self._chunks:
            if a <= t < b:
                cap = caption_img(g)
                sc = lerp(0.82, 1.0, eback(prog(t, a, a + 0.14)))
                im = cap if sc == 1.0 else cap.resize((max(1, int(cap.width * sc)), max(1, int(cap.height * sc))), Image.BILINEAR)
                img.paste(im, ((W - im.width) // 2, 1270 - im.height // 2 + (cap.height - im.height) // 2), im)
                break
        return img

    # ---- outputs ----
    def tts(self):
        timing = synth_lines(self.lines, self.dir)
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
        make_audio(self.dir, self.timing["total"])
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
