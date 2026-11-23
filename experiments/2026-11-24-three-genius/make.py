"""Test format: fast list, 3 things in ~30 s. Facts reused from the verified sources of the plug, microwave and YKK videos."""
import os, sys, math, importlib.util
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *

def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
UK = _load("videos/2026-11-23-uk-plug/make.py", "m_plug")
MW = _load("videos/2026-11-23-microwave-door/make.py", "m_micro")
YK = _load("videos/2026-11-23-ykk-zips/make.py", "m_ykk")

V = Video(
    "test-three-genius", episode=None, title="3 things that are *secretly genius*",
    lines=[
        "Three things you use every day that are secretly genius.",
        "One. The UK plug. The top pin is longer, so it connects first, and pushes open shutters on the other two holes.",
        "Two. Your microwave door.",
        "The mesh holes are about a millimetre wide.",
        "But microwaves are about twelve centimetres long, so they bounce back in.",
        "Light gets through.",
        "Three. The Y K K on your zip. By one estimate, those letters are on about half the zips on Earth.",
        "Which one surprised you? Comment one, two or three. Follow for more everyday genius.",
    ],
    display=[
        "*3* things you use every day that are *secretly genius*.",
        "*1*. The UK *plug*. The top pin is *longer*, so it connects first, and pushes open *shutters* on the other two holes.",
        "*2*. Your microwave *door*.",
        "The mesh holes are about *1 mm* wide.",
        "But microwaves are about *12 cm* long, so they *bounce* back in.",
        "*Light* gets through.",
        "*3*. The *YKK* on your zip. By one estimate, those letters are on about *half* the zips on Earth.",
        "Which one *surprised* you? Comment *1*, *2* or *3*. Follow for more everyday *genius*.",
    ],
)

def zip_icon(p, x, y, s=1.0, closed=0.6):
    """Small zip: two tapes with teeth, closed from the bottom up to `closed`, and a YKK slider."""
    top, bot = y - 110 * s, y + 110 * s
    cy = bot - (bot - top) * closed
    for sx in (-1, 1):
        off = 0 if True else 0
        p.rr([x + sx * 14 * s - 16 * s, top, x + sx * 14 * s + 16 * s, bot], 6 * s, fill=(60, 70, 86))
    yy = bot - 12 * s
    i = 0
    while yy > top + 10 * s:
        gap = 0 if yy > cy else 16 * s
        sx = -1 if i % 2 else 1
        p.rr([x + sx * (6 * s + gap) - 12 * s, yy - 6 * s, x + sx * (6 * s + gap) + 12 * s, yy + 6 * s], 3 * s, fill=BRASS)
        yy -= 14 * s; i += 1
    p.rr([x - 26 * s, cy - 30 * s, x + 26 * s, cy + 22 * s], 10 * s, fill=(200, 205, 215))
    p.rr([x - 16 * s, cy + 18 * s, x + 16 * s, cy + 74 * s], 8 * s, fill=(170, 176, 186))
    p.text((x, cy + 46 * s), "YKK", f2("dm", max(8, int(15 * s))), INK)

def badge(p, t, t0, n):
    k = eback(prog(t, t0, t0 + 0.35))
    if k <= 0: return
    p.circle(140, 400, 74 * k, fill=YEL)
    p.circle(140, 400, 62 * k, fill=INK)
    p.text((140, 404), str(n), f2("anton", max(8, int(84 * k))), YEL)

@V.sounds
def sounds(L):
    return [(0.3, "pop"), (0.7, "pop"), (1.1, "pop"), (L(1)[0], "ding"), (L(1)[0] + 2.4, "thud"),
            (L(2)[0], "ding"), (L(4)[1] - 0.8, "boing"), (L(6)[0], "ding"), (L(6)[1] - 1.0, "cash"), (L(7)[0] + 0.3, "pop")]

@V.scene(0)
def intro(p, t, L):
    a, e = L(0)
    items = [(220, "plug"), (540, "micro"), (860, "zip")]
    for i, (x, kind) in enumerate(items):
        k = eback(prog(t, 0.2 + i * 0.4, 0.6 + i * 0.4))
        if k <= 0: continue
        bob = 10 * math.sin(t * 2.4 + i)
        p.circle(x, 740 + bob, 140 * k, fill=(36, 62, 98))
        if kind == "plug":
            UK.plug_face(p, x, 735 + bob, 0.42 * k)
        elif kind == "micro":
            MW.oven(p, x, 740 + bob, 0.3 * k)
        else:
            zip_icon(p, x, 740 + bob, 1.05 * k, lerp(0.2, 0.75, prog(t, 1.2, 2.2)))
        p.circle(x - 100 * k, 620 + bob, 34 * k, fill=YEL)
        p.text((x - 100 * k, 622 + bob), str(i + 1), f2("anton", max(8, int(44 * k))), INK)
    if t > e - 0.6:
        for ang, rr in [(-30, 420), (200, 410), (30, 430), (150, 420)]:
            q = math.radians(ang)
            sparkle(p, 540 + math.cos(q) * rr, 740 + math.sin(q) * rr * 0.6, 26 * eback(prog(t, e - 0.6, e - 0.3)))

@V.scene(1)
def plug(p, t, L):
    a, e = L(1)
    px = lerp(140, 430, eio(prog(t, a + 1.0, a + 2.6)))
    px = lerp(px, 625, eio(prog(t, a + 3.6, a + 4.8)))
    drop = 150 * eio(prog(t, a + 3.2, a + 3.8))
    UK.socket_block(p, drop)
    UK.side_plug(p, px, glow=prog(t, a + 1.8, a + 2.2) * (1 - prog(t, a + 3.4, a + 3.8)))
    badge(p, t, a, 1)
    pill(p, 560, 380, "LONGER TOP PIN", prog(t, a + 1.9, a + 2.3) * (1 - prog(t, a + 3.4, a + 3.7)), bg=WHITE)
    pill(p, 800, 1110, "SHUTTERS OPEN", prog(t, a + 3.7, a + 4.1), bg=ORANGE)

@V.scene(2, 5)
def micro(p, t, L):
    a, _ = L(2); a4, _ = L(4); a5, e = L(5)
    badge(p, t, a, 2)
    if t < a4 - 0.2:
        MW.oven(p, 330, 640, 0.55, door_hl=prog(t, a + 0.4, a + 0.8))
        k = eback(prog(t, a + 1.0, a + 1.5))
        mx, my, mr = 700, 800, 240 * k
        if mr > 1:
            p.line([(330, 640), (mx - mr * .7, my - mr * .7)], fill=(200, 205, 215), width=6)
            p.circle(mx, my, mr, fill=(150, 156, 166), outline=WHITE, width=10)
            step = 60 * k
            for i in range(-4, 5):
                for j in range(-4, 5):
                    x, y = mx + i * step, my + j * step
                    if (x - mx) ** 2 + (y - my) ** 2 < (mr - 30) ** 2:
                        p.circle(x, y, 19 * k, fill=(20, 22, 28))
        pill(p, 700, 1100, "HOLES ≈ 1 MM", prog(t, L(3)[0] + 0.6, L(3)[0] + 1.0))
    else:
        # the door as a wall: big waves bounce, small light waves pass
        p.rect([520, 420, 560, 1100], fill=(150, 156, 166))
        for j in range(12):
            p.circle(540, 450 + j * 55, 8, fill=(20, 22, 28))
        ph = (t - a) * 6
        MW.wave(p, 90, 500, 640, 60, 240, ph, (255, 120, 90), 10)
        MW.wave(p, 90, 500, 860, 10, 26, ph * 2, YEL, 5)
        MW.wave(p, 580, 1000, 860, 10, 26, ph * 2, YEL, 5)
        p.arrow((470, 730), (300, 730), (255, 120, 90), width=8, head=26)
        pill(p, 320, 530, "MICROWAVE · 12 CM", prog(t, a4, a4 + 0.3), bg=(255, 120, 90), fg=WHITE, size=32)
        pill(p, 790, 760, "LIGHT GETS THROUGH", prog(t, a5, a5 + 0.3), bg=YEL, size=32)
        cross(p, 760, 640, 54, prog(t, a4 + 2.4, a4 + 2.6), shake_t=t - a4 - 2.4)

@V.scene(6)
def zips(p, t, L):
    a, e = L(6)
    badge(p, t, a, 3)
    k = eio(prog(t, a + 0.2, a + 1.8))
    YK.zip_v(p, 330, 360, 1120, lerp(1000, 520, k))
    q = eo(prog(t, a + 2.6, a + 3.8))
    cx, cy, r = 760, 720, 200
    p.circle(cx, cy, r, fill=(40, 60, 90))
    if q > 0:
        p.d.pieslice([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], -90, -90 + 180 * q, fill=YEL)
    p.circle(cx, cy, r, outline=WHITE, width=6)
    pill(p, 760, 980, "≈ HALF THE WORLD'S ZIPS", prog(t, e - 1.2, e - 0.9), bg=WHITE, size=32)

@V.scene(7)
def outro(p, t, L):
    a, e = L(7)
    for i, x in enumerate((220, 540, 860)):
        k = eback(prog(t, a + 0.2 + i * 0.25, a + 0.5 + i * 0.25))
        if k <= 0: continue
        bob = 8 * math.sin(t * 3 + i)
        p.circle(x, 700 + bob, 120 * k, fill=(36, 62, 98))
        if i == 0: UK.plug_face(p, x, 695 + bob, 0.36 * k)
        elif i == 1: MW.oven(p, x, 700 + bob, 0.26 * k)
        else: zip_icon(p, x, 700 + bob, 0.9 * k, 0.75)
        pill(p, x, 880, str(i + 1), prog(t, a + 1.4 + i * 0.2, a + 1.7 + i * 0.2), bg=YEL, size=50)
    fp = prog(t, e - 1.8, e - 1.4)
    if fp > 0:
        r = 60 * eback(fp)
        p.circle(540, 1040, r, fill=RED)
        p.line([(540 - r * .45, 1040), (540 + r * .45, 1040)], fill=WHITE, width=12)
        p.line([(540, 1040 - r * .45), (540, 1040 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
