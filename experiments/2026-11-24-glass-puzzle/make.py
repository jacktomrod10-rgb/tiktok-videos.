"""Test format: brain teaser with a countdown and a reveal. Which glass fills first? Answer: glass 2.
Rules shown: water leaves a glass through whichever pipe it reaches first; a plugged pipe lets nothing through."""
import os, sys, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *

COUNT = 5.0
V = Video(
    "test-glass-puzzle", episode=None, series="EVERYDAY GENIUS · BRAIN TEASER", title="Which glass fills up *first*?",
    lines=[
        "Which glass fills up first? Comment your answer before the timer runs out.",
        "Time's up. Let's pour.",
        "The left pipe is lower down, so the water goes left first.",
        "But look closely. Glass two's exit pipe is blocked.",
        "So glass two fills up first! Did you get it right? Follow for more everyday genius.",
    ],
    display=[
        "Which glass fills up *first*? *Comment* your answer before the *timer* runs out.",
        "Time's *up*. Let's *pour*.",
        "The left pipe is *lower* down, so the water goes *left* first.",
        "But look closely. Glass *two's* exit pipe is *blocked*.",
        "So glass *two* fills up first! Did you get it *right*? Follow for more everyday *genius*.",
    ],
    holds={0: COUNT},
)

WATER, WATER_L = (70, 160, 240), (130, 200, 255)
GLASS, PIPE, PIPE_D = (220, 235, 250), (150, 160, 178), (100, 110, 128)
GW, GH = 150, 190
GL = {1: (540, 475), 2: (300, 700), 3: (780, 700), 4: (160, 960), 5: (920, 960)}

def glass(p, n, level, t, hl=0.0):
    cx, cy = GL[n]
    x0, y0, x1, y1 = cx - GW / 2, cy - GH / 2, cx + GW / 2, cy + GH / 2
    if hl > 0:
        with p.flat():
            for i in range(4):
                p.rr([x0 - 30 + i * 6, y0 - 30 + i * 6, x1 + 30 - i * 6, y1 + 30 - i * 6], 40, fill=(40 + i * 12, 120 + i * 20, 80 + i * 12))
    p.shadow([x0, y0, x1, y1 + 8], 18, dy=14, blur=14, alpha=120)
    with p.flat():
        p.rr([x0 - 7, y0 - 4, x1 + 7, y1 + 7], 20, fill=(150, 186, 214))           # glass wall
        p.rr([x0, y0, x1, y1], 14, fill=(52, 74, 104))                             # inside (see-through)
        lv = clamp(level)
        if lv > 0:
            top = y1 - (GH - 8) * lv
            wob = 4 * math.sin(t * 6 + n) * (1 if lv < 1 else 0.3)
            p.rr([x0 + 5, top + wob, x1 - 5, y1 - 5], 10, fill=WATER)
            p.rr([x0 + 5, top + wob, x1 - 5, top + wob + 12], 6, fill=WATER_L)
            for b in range(3):                                                     # bubbles
                by = y1 - 20 - ((t * 60 + b * 47) % max(10, (y1 - top - 30)))
                if by > top + 16:
                    p.circle(x0 + 40 + b * 32, by, 5, fill=(190, 225, 255))
        p.ell([x0 - 7, y0 - 14, x1 + 7, y0 + 12], fill=(170, 204, 230))            # rim
        p.ell([x0 + 4, y0 - 6, x1 - 4, y0 + 6], fill=(40, 58, 84))
        p.rr([x0 + 12, y0 + 16, x0 + 28, y1 - 24], 8, fill=(205, 228, 246))         # highlight streak
        p.rr([x1 - 22, y0 + 30, x1 - 14, y0 + 90], 4, fill=(170, 204, 230))
    p.circle(cx, y1 + 44, 27, fill=(255, 255, 255))
    p.text((cx, y1 + 46), str(n), f2("anton", 38), INK)

def pipe(p, pts, flow=0.0, t=0.0, plug=None):
    p.line(pts, PIPE_D, 30)
    p.line(pts, PIPE, 22)
    if flow > 0:
        p.line(pts, WATER, 12)
        segs = []                                           # moving highlights along the pipe
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            segs.append(((ax, ay), (bx, by), math.hypot(bx - ax, by - ay)))
        total = sum(s[2] for s in segs)
        for k in range(int(total / 40)):
            d = (k * 40 + t * 160) % total
            for (ax, ay), (bx, by), ln in segs:
                if d <= ln:
                    f = d / ln
                    p.circle(ax + (bx - ax) * f, ay + (by - ay) * f, 4, fill=WATER_L)
                    break
                d -= ln
    if plug:
        x, y = plug
        p.rr([x - 22, y - 26, x + 22, y + 26], 8, fill=(60, 50, 56))
        p.rr([x - 16, y - 20, x + 16, y + 20], 6, fill=(110, 90, 96))

# pipes: G1 low-left -> G2, G1 high-right -> G3, G2 bottom-left (plugged) -> G4, G3 bottom-right -> G5
P12 = [(465, 540), (300, 540), (300, 610)]
P13 = [(615, 410), (780, 410), (780, 610)]
P24 = [(225, 770), (160, 770), (160, 870)]
P35 = [(855, 770), (920, 770), (920, 870)]
PLUG = (190, 770)

def tap(p, t, on):
    p.rr([400, 334, 560, 360], 13, fill=(170, 176, 190))
    p.rr([420, 326, 452, 340], 6, fill=(200, 60, 60))
    p.rr([526, 346, 556, 386], 8, fill=(170, 176, 190))
    if on:
        p.rect([534, 386, 548, 562], fill=WATER)

def board(p, t, levels, flows, hl=None):
    with p.flat():
        p.rect([0, 300, 1080, 1170], fill=(28, 52, 64))                          # tiled kitchen wall
        for i in range(6):
            p.circle(540, 700, 640 - i * 90, fill=(30 + i * 4, 56 + i * 6, 70 + i * 6))
        for x in range(0, 1081, 90):
            p.rect([x - 2, 300, x + 2, 1060], fill=(22, 42, 52))
        for y in range(300, 1061, 90):
            p.rect([0, y - 2, 1080, y + 2], fill=(22, 42, 52))
        p.rect([0, 1060, 1080, 1170], fill=(120, 84, 56))                        # worktop
        p.rect([0, 1060, 1080, 1074], fill=(160, 116, 80))
        p.rect([0, 0, 1080, 299], fill=(0, 0, 0, 0))
        p.rect([0, 1171, 1080, 1920], fill=(0, 0, 0, 0))
    pipe(p, P24, flows.get("24", 0), t, plug=PLUG)
    pipe(p, P35, flows.get("35", 0), t)
    pipe(p, P12, flows.get("12", 0), t)
    pipe(p, P13, flows.get("13", 0), t)
    for n in range(1, 6):
        glass(p, n, levels.get(n, 0), t, hl=1.0 if hl == n else 0.0)

@V.sounds
def sounds(L):
    a0, e0 = L(0)
    out = [(e0 + 0.3 + i, "pop") for i in range(int(COUNT))]
    out += [(L(1)[0], "ding"), (L(1)[0] + 0.6, "whoosh"), (L(3)[0] + 1.2, "thud"), (L(4)[0] + 0.5, "cash")]
    return out

@V.scene(0)
def question(p, t, L):
    a, e = L(0)
    board(p, t, {}, {})
    tap(p, t, False)
    if t > e:
        remain = COUNT - (t - e - 0.3)
        r = 60
        cx, cy = 900, 460
        p.circle(cx, cy, r + 8, fill=(40, 46, 80))
        if remain > 0:
            p.d.pieslice([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], -90, -90 + 360 * clamp(remain / COUNT),
                         fill=RED if remain < 2 else YEL)
        p.circle(cx, cy, r - 16, fill=(20, 24, 44))
        p.text((cx, cy + 3), str(max(0, int(math.ceil(remain)))), f2("anton", 60), WHITE)
        pill(p, 190, 440, "COMMENT 1–5", prog(t, e, e + 0.3), bg=WHITE, size=36)

@V.scene(1, 4)
def reveal(p, t, L):
    a1, _ = L(1); a2, e2 = L(2); a3, e3 = L(3); a4, e4 = L(4)
    pour = t > a1 + 0.6
    g1 = 0.17 * prog(t, a1 + 0.6, a2)                       # glass 1 rises to the low pipe
    g2 = prog(t, a2 + 0.3, a4 + 0.4)                         # then everything goes to glass 2
    levels = {1: g1, 2: g2}
    flows = {"12": 1.0 if t > a2 else 0.0}
    hl = 2 if t > a4 + 0.4 else None
    board(p, t, levels, flows, hl=hl)
    tap(p, t, pour)
    if a2 + 0.5 < t < a3:
        pill(p, 300, 480, "LOWER", prog(t, a2 + 0.5, a2 + 0.8), bg=YEL, size=36)
        pill(p, 920, 410, "HIGHER", prog(t, a2 + 1.0, a2 + 1.3), bg=WHITE, size=32)
    if t > a3 + 0.8:
        k = eback(prog(t, a3 + 0.8, a3 + 1.2))
        x, y = PLUG
        p.circle(x, y, 70 * k, outline=RED, width=10)
        pill(p, 150, 660, "BLOCKED", prog(t, a3 + 1.4, a3 + 1.7) * (1 - prog(t, a4 + 0.2, a4 + 0.5)), bg=RED, fg=WHITE, size=32)
    if t > a4 + 0.4:
        tick(p, 430, 610, 50, prog(t, a4 + 0.4, a4 + 0.7))
        pill(p, 540, 1120, "GLASS 2 FILLS FIRST", prog(t, a4 + 0.6, a4 + 0.9), bg=GREEN, size=44)
        for ang, rr in [(-40, 150), (220, 150), (-140, 160), (40, 150)]:
            q = math.radians(ang)
            sparkle(p, 300 + math.cos(q) * rr, 700 + math.sin(q) * rr, 22 * eback(prog(t, a4 + 0.5, a4 + 0.9)))

if __name__ == "__main__":
    V.main()
