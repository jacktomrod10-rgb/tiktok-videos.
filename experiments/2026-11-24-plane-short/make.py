"""Test format: short fact (~25 s). Same verified research as videos/2026-11-23-plane-windows/sources.md."""
import os, sys, math, importlib.util
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *

def _load(rel):
    spec = importlib.util.spec_from_file_location("m_" + os.path.basename(os.path.dirname(rel)).replace("-", "_"), os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
PW = _load("videos/2026-11-23-plane-windows/make.py")

V = Video(
    "test-plane-short", episode=None, title="Why are plane windows *never* square?",
    lines=[
        "Plane windows are never square. Here's why.",
        "Every flight, the cabin is pumped full of air like a balloon, so the metal stretches, then relaxes.",
        "Sharp corners squeeze all that stress into one tiny spot. Curves spread it out.",
        "In nineteen fifty-four, two Comet jets broke apart. Investigators found fatigue cracks at the corners of cabin openings.",
        "Window seat or aisle? Tell me in the comments. Follow for more everyday genius.",
    ],
    display=[
        "Plane windows are *never* square. Here's *why*.",
        "Every flight, the cabin is pumped full of air like a *balloon*, so the metal *stretches*, then relaxes.",
        "Sharp *corners* squeeze all that stress into one tiny spot. *Curves* spread it out.",
        "In *1954*, two *Comet* jets broke apart. Investigators found fatigue *cracks* at the *corners* of cabin openings.",
        "*Window* seat or *aisle*? Tell me in the *comments*. Follow for more everyday *genius*.",
    ],
)


def cabin(p, t):
    """Cabin wall behind the windows, with a soft overhead light."""
    p.rr([70, 400, 1010, 1080], 60, fill=(206, 212, 222))
    p.rr([70, 400, 1010, 470], 40, fill=(226, 230, 238))
    for i in range(5):
        p.rr([110 + i * 8, 1000 - i * 4, 970 - i * 8, 1060], 30, fill=(196 - i * 4, 202 - i * 4, 214 - i * 4))
    p.rr([440, 420, 640, 446], 13, fill=(255, 244, 210))

@V.sounds
def sounds(L):
    return [(1.4, "thud"), (1.9, "ding"), (L(2)[0] + 2.4, "thud"), (L(3)[0] + 0.4, "whoosh"), (L(3)[1] - 1.6, "thud"), (L(4)[0] + 0.2, "pop")]

@V.scene(0)
def intro(p, t, L):
    cabin(p, t)
    a = eback(prog(t, 0.05, 0.5)); b = eback(prog(t, 0.5, 0.95))
    if a > 0:
        PW.window(p, 300, 700, 260 * a, 260 * a, 6, t)
        cross(p, 300, 960, 54, prog(t, 1.3, 1.5), shake_t=t - 1.3)
    if b > 0:
        PW.window(p, 780, 700, 230 * b, 330 * b, 110 * b, t)
        tick(p, 780, 960, 54, prog(t, 1.8, 2.1))

@V.scene(1)
def pressure(p, t, L):
    a1, e1 = L(1)
    breathe = 0.5 + 0.5 * math.sin((t - a1) * 3.0) if t > a1 + 2.0 else 0.0
    sc = 1.0 + 0.12 * breathe
    PW.fuselage(p, 540, 740, 820, 150, sc)
    if t > a1 + 1.2:
        for ang in range(0, 360, 30):
            q = math.radians(ang)
            r0 = 190 * sc
            p.arrow((540 + math.cos(q) * r0 * 2.2, 740 + math.sin(q) * r0 * 0.9),
                    (540 + math.cos(q) * (r0 * 2.2 + 50), 740 + math.sin(q) * (r0 * 0.9 + 30)), ORANGE, width=8, head=22)
    pill(p, 540, 430, "PUMPED UP LIKE A BALLOON", prog(t, a1 + 1.0, a1 + 1.4) * (1 - prog(t, a1 + 3.4, a1 + 3.7)), bg=ORANGE)
    pill(p, 540, 430, "STRETCH, RELAX, REPEAT", prog(t, a1 + 3.8, a1 + 4.2))

@V.scene(2)
def corners(p, t, L):
    a, e = L(2)
    PW.flow(p, 300, 760, "round", t, prog(t, e - 1.6, e - 1.2))
    PW.flow(p, 780, 760, "square", t, prog(t, a + 1.2, a + 1.6))
    pill(p, 780, 480, "HOT SPOTS", prog(t, a + 1.2, a + 1.6), bg=RED, fg=WHITE)
    pill(p, 300, 480, "SPREAD OUT", prog(t, e - 1.6, e - 1.2), bg=YEL)

@V.scene(3)
def comet(p, t, L):
    a, e = L(3)
    big_number(p, t, a, 1954, cy=520, size=230, start=1940, dur=0.9)
    k = eo(prog(t, a + 0.3, a + 1.2))
    if k > 0:
        PW.jet(p, lerp(-200, 540, k), 860, 0.9)
    if t > a + 3.2:
        g = prog(t, a + 3.2, a + 4.4)
        pts = [(560, 852)]
        for i in range(1, int(8 * g) + 1):
            pts.append((560 + i * 18, 852 - i * 16 + (8 if i % 2 else -8)))
        p.line(pts, RED, 7)
        p.rr([540, 838, 580, 866], 6, outline=WHITE, width=4)
    pill(p, 540, 1100, "FATIGUE CRACKS AT CORNERS", prog(t, e - 2.2, e - 1.8), bg=RED, fg=WHITE)

@V.scene(4)
def outro(p, t, L):
    a, e = L(4)
    cabin(p, t)
    for i in range(3):
        k = eback(prog(t, a + i * 0.2, a + 0.45 + i * 0.2))
        if k > 0:
            PW.window(p, 230 + i * 310, 730, 150 * k, 220 * k, 72 * k, t + i, frame=(200, 206, 214))
    pill(p, 300, 440, "WINDOW?", prog(t, a + 0.2, a + 0.5), bg=YEL, size=50)
    pill(p, 780, 440, "AISLE?", prog(t, a + 0.7, a + 1.0), bg=WHITE, size=50)
    fp = prog(t, e - 1.8, e - 1.4)
    if fp > 0:
        r = 60 * eback(fp)
        p.circle(540, 1010, r, fill=RED)
        p.line([(540 - r * .45, 1010), (540 + r * .45, 1010)], fill=WHITE, width=12)
        p.line([(540, 1010 - r * .45), (540, 1010 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
