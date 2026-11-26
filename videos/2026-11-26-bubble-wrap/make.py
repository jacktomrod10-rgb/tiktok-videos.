"""Episode 9 (long): Bubble wrap was invented as wallpaper.
    python3 -I videos/2026-11-26-bubble-wrap/make.py tts | stills ... | render videos/2026-11-26-bubble-wrap.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "bubble-wrap", episode=9, title="What was *bubble wrap* invented for?",
    lines=[
        "Bubble wrap was invented to go on your walls.",
        "In nineteen fifty-seven, two inventors sealed two shower curtains together, trapping air in bubbles, and tried to sell it as textured wallpaper.",
        "It didn't catch on. So they pitched it as greenhouse insulation. That didn't take off either.",
        "Then, in nineteen fifty-nine, I B M launched a new computer, the fourteen oh one, and needed a way to ship it without damage.",
        "Their company, Sealed Air, pitched the bubbles as packaging, and I B M used it to protect the computer on its way to customers.",
        "The fourteen oh one became by far the best-selling computer yet, and bubble wrap finally had its job.",
        "But in twenty fifteen, Sealed Air unveiled a version that doesn't pop.",
        "Its bubbles are linked in columns. Squeeze one, and the air just flows into its neighbours, so it's much harder to burst.",
        "It ships flat, and gets pumped full of air where it's used. And the company said the poppable original wasn't going anywhere.",
        "So which would you have bought? A, bubble wallpaper. B, a bubble greenhouse. Or C, bubble wrap that won't pop. Comment A, B or C.",
        "Follow for more everyday genius.",
    ],
    display=[
        "Bubble wrap was invented to go on your *walls*.",
        "In *1957*, two inventors sealed two *shower curtains* together, trapping air in bubbles, and tried to sell it as textured *wallpaper*.",
        "It didn't catch *on*. So they pitched it as *greenhouse* insulation. That didn't take off *either*.",
        "Then, in *1959*, *IBM* launched a new computer, the *1401*, and needed a way to ship it without *damage*.",
        "Their company, *Sealed Air*, pitched the bubbles as *packaging*, and IBM used it to protect the computer on its way to *customers*.",
        "The *1401* became by far the *best-selling* computer yet, and bubble wrap finally had its *job*.",
        "But in *2015*, Sealed Air unveiled a version that *doesn't pop*.",
        "Its bubbles are *linked* in columns. Squeeze one, and the air just flows into its *neighbours*, so it's much harder to *burst*.",
        "It ships *flat*, and gets pumped full of air where it's used. And the company said the *poppable* original wasn't going anywhere.",
        "So which would you have bought? *A*, bubble wallpaper. *B*, a bubble greenhouse. Or *C*, bubble wrap that won't pop. Comment *A*, *B* or *C*.",
        "Follow for more everyday *genius*.",
    ],
)

BUB, BUB_E, BUB_S = (208, 234, 252), (112, 160, 206), (132, 176, 214)
SHEET = (158, 199, 231)
FLAT = (196, 216, 236)
WALL, FLOOR, FLOOR_D = (226, 206, 172), (150, 104, 66), (122, 82, 50)
SOFA, SOFA_D = (214, 96, 74), (176, 70, 54)
CURT_A, CURT_B = (90, 150, 230), (60, 186, 168)
GLASS = (176, 222, 214)
CAB, CAB_D, CAB_L = (128, 144, 170), (88, 102, 126), (172, 188, 210)
TAPE = (222, 188, 120)
TRUCK, TRUCK_D = (226, 88, 82), (180, 60, 58)
POT, LEAF = (196, 104, 62), (70, 190, 110)
SKIN, SKIN_D, NAIL = (238, 190, 152), (206, 152, 116), (252, 226, 210)

# ---------------- drawings ----------------
def bubble(p, x, y, r):
    if r < 1.5: return
    p.circle(x + r * 0.10, y + r * 0.14, r, fill=BUB_S)
    p.circle(x, y, r, fill=BUB, outline=BUB_E, width=max(1.0, r * 0.07))
    p.ell([x - r * 0.62, y - r * 0.64, x - r * 0.06, y - r * 0.22], fill=WHITE)

def flat_bubble(p, x, y, r):
    p.ell([x - r * 0.95, y - r * 0.32, x + r * 0.95, y + r * 0.32], fill=BUB_S)
    p.line([(x - r * 0.6, y), (x - r * 0.15, y - r * 0.16), (x + r * 0.2, y + r * 0.1), (x + r * 0.6, y - r * 0.06)], BUB_E, max(1.0, r * 0.09))

def bubble_grid(box, gap):
    x0, y0, x1, y1 = box
    out, i, y = [], 0, y0 + gap * 0.55
    while y < y1 - gap * 0.35:
        j, x = 0, x0 + gap * 0.55 + (gap / 2 if i % 2 else 0)
        while x < x1 - gap * 0.35:
            out.append((i, j, x, y)); x += gap; j += 1
        y += gap * 0.87; i += 1
    return out

def sheet(p, box, gap=52, base=SHEET, size=None, pops=None):
    """Bubble wrap. size(x, y) -> 0..1 bubble size; pops: {(i, j): 0..1} (a bubble swells, then goes flat)."""
    r = gap * 0.38
    if base: p.rect(box, fill=base)
    for i, j, x, y in bubble_grid(box, gap):
        k = size(x, y) if size else 1.0
        u = pops.get((i, j), 0.0) if pops else 0.0
        if u >= 0.5: flat_bubble(p, x, y, r); continue
        bubble(p, x, y, r * k * (1 + 0.3 * math.sin(u * math.pi)))

def burst(p, x, y, u, r=40):
    """Little starburst + POP! text, u 0..1."""
    if 0 < u < 1:
        s = math.sin(u * math.pi)
        sparkle(p, x, y, r * s)
        for k in range(6):
            a = k * math.pi / 3 + 0.3
            p.circle(x + math.cos(a) * r * 1.3 * u, y + math.sin(a) * r * 1.3 * u, 6 * s + 1, fill=WHITE)
        p.text((x, y - r * 1.4 - 12 * u), "POP!", f2("anton", max(8, int(46 * s))), YEL)

def capsule_pts(tip, ang, length, width, n=10):
    th = math.radians(ang); d = (math.cos(th), math.sin(th)); r = width / 2
    c1 = (tip[0] + d[0] * r, tip[1] + d[1] * r)
    c2 = (tip[0] + d[0] * (length - r), tip[1] + d[1] * (length - r))
    pts = []
    for i in range(n + 1):
        f = th + math.radians(90 + 180 * i / n)
        pts.append((c1[0] + r * math.cos(f), c1[1] + r * math.sin(f)))
    for i in range(n + 1):
        f = th + math.radians(-90 + 180 * i / n)
        pts.append((c2[0] + r * math.cos(f), c2[1] + r * math.sin(f)))
    return pts

def along(tip, ang, dist, side=0.0):
    th = math.radians(ang)
    return (tip[0] + math.cos(th) * dist - math.sin(th) * side, tip[1] + math.sin(th) * dist + math.cos(th) * side)

def finger(p, tip, ang=55, length=380, width=118):
    p.poly(capsule_pts(along(tip, ang, -4), ang, length + 8, width + 8), SKIN_D)
    p.poly(capsule_pts(tip, ang, length, width), SKIN)
    p.poly(capsule_pts(along(tip, ang, 14, -6), ang, 104, width * 0.62), NAIL)
    a, b = along(tip, ang, 200, -width * 0.32), along(tip, ang, 200, width * 0.32)
    p.line([a, b], SKIN_D, 5)

def room(p, t):
    """Living room papered in bubble wrap (the hook)."""
    p.rect([100, 340, 980, 975], fill=WALL)
    pops = {ij: prog(t, tt, tt + 0.22) for tt, ij in HOOK_POPS}
    sheet(p, [100, 340, 800, 975], gap=54, pops=pops)
    h = 635 * eo(prog(t, 0.0, 1.0))                     # last strip still rolling down
    if h > 4: sheet(p, [800, 340, 980, 340 + h], gap=54)
    if h < 634: p.rr([788, 340 + h - 24, 992, 340 + h + 24], 24, fill=SHEET, outline=BUB_E, width=3)
    p.line([(800, 340), (800, 340 + h)], BUB_E, 3)
    # picture frame
    p.rr([228, 438, 472, 642], 10, fill=BRASS, outline=BRASS_D, width=4)
    p.rect([250, 460, 450, 620], fill=(120, 180, 235))
    p.circle(400, 505, 26, fill=YEL)
    p.poly([(250, 620), (330, 540), (410, 620)], GREEN)
    p.poly([(360, 620), (420, 570), (450, 600), (450, 620)], (40, 170, 120))
    # floor and skirting
    p.rect([100, 975, 980, 1125], fill=FLOOR)
    for x in (260, 470, 690, 900): p.line([(x, 990), (x - 30, 1125)], FLOOR_D, 4)
    p.rect([100, 958, 980, 982], fill=WHITE)
    # sofa
    p.rr([200, 750, 640, 880], 34, fill=SOFA_D)
    p.rr([210, 830, 630, 950], 26, fill=SOFA)
    p.line([(420, 840), (420, 940)], SOFA_D, 5)
    for x0 in (160, 600): p.rr([x0, 800, x0 + 80, 965], 30, fill=SOFA)
    # lamp
    p.line([(880, 600), (880, 955)], DARK, 9)
    p.ell([835, 948, 925, 978], fill=DARK)
    glow = 0.5 + 0.5 * math.sin(t * 3)
    p.poly([(815, 610), (945, 610), (918, 522), (842, 522)], (255, 214 + int(20 * glow), 110))
    for tt, (i, j) in HOOK_POPS:
        x = 100 + 54 * 0.55 + j * 54 + (27 if i % 2 else 0); y = 340 + 54 * 0.55 + i * 54 * 0.87
        burst(p, x, y, prog(t, tt + 0.05, tt + 0.6), r=34)

HOOK_POPS = [(0.9, (1, 9)), (1.5, (7, 1)), (2.1, (4, 10)), (2.7, (3, 11))]

def curtain(p, x0, y0, x1, y1, col, pattern):
    w = x1 - x0
    p.rect([x0, y0, x1, y1], fill=col)
    dark = tuple(int(c * 0.82) for c in col)
    if pattern == "stripes":
        for k in range(5):
            yy = y0 + 40 + k * (y1 - y0 - 40) / 5
            p.rect([x0, yy, x1, yy + 26], fill=WHITE)
    else:
        for r in range(int((y1 - y0 - 40) / 64)):
            for c in range(5):
                p.circle(x0 + w * (c + 0.5 + (0.5 if r % 2 else 0)) / 5.5, y0 + 50 + r * 64, 13, fill=WHITE)
    for k in range(1, 6):
        xx = x0 + w * k / 6
        p.line([(xx, y0 + 8), (xx, y1)], dark, 6)
    for k in range(7):
        p.circle(x0 + 18 + k * (w - 36) / 6, y0, 13, outline=EDGE, width=5)

def wall_roll(p, x0, y0, x1, y1):
    p.rr([x0, y0, x1, y1], 30, fill=SHEET)
    sheet(p, [x0 + 20, y0 + 6, x1 - 50, y1 - 6], gap=40, base=None)
    p.ell([x1 - 60, y0, x1, y1], fill=BUB_S, outline=BUB_E, width=4)
    p.ell([x1 - 44, (y0 + y1) / 2 - 24, x1 - 16, (y0 + y1) / 2 + 24], fill=DARK)

def greenhouse(p, x0, y0, x1, y1, apex, sun_t, plant=True):
    """Glass house with bubble-wrapped panes. apex = roof peak y."""
    cx = (x0 + x1) / 2
    p.poly([(x0, y0), (cx, apex), (x1, y0)], GLASS)
    p.rect([x0, y0, x1, y1], fill=GLASS)
    sheet(p, [x0 + 8, y0 + 8, x1 - 8, y1 - 8], gap=(x1 - x0) / 12, base=None)
    for k in range(1, 4):
        xx = x0 + (x1 - x0) * k / 4
        p.line([(xx, y0), (xx, y1)], WHITE, 8)
    p.line([(x0, y0), (cx, apex), (x1, y0)], WHITE, 10)
    p.line([(x0, y0), (x1, y0)], WHITE, 8)
    p.rect([x0, y0, x1, y1], outline=WHITE, width=8)
    if plant:
        px, py = cx, y1 - 10
        s = (x1 - x0) / 520
        for k, ang in enumerate((-60, -90, -120)):
            a = math.radians(ang + 6 * math.sin(sun_t * 2 + k))
            tip = (px + math.cos(a) * 120 * s, py - 70 * s + math.sin(a) * 120 * s)
            p.line([(px, py - 70 * s), tip], LEAF, 10 * s + 2)
            p.circle(tip[0], tip[1], 26 * s, fill=LEAF)
        p.poly([(px - 60 * s, py - 80 * s), (px + 60 * s, py - 80 * s), (px + 44 * s, py), (px - 44 * s, py)], POT)

def computer(p, cx, base, sc, t, wrap=0.0, tape=0.0, gap=None):
    """A late-1950s mainframe: processor cabinet + tape drive. Optional bubble wrap and tape."""
    if sc <= 0.03: return
    X = lambda x: cx + x * sc
    Y = lambda y: base + y * sc
    p.rr([X(-270), Y(-440), X(40), Y(0)], 18 * sc, fill=CAB, outline=CAB_D, width=4 * sc)
    p.rr([X(-240), Y(-410), X(10), Y(-250)], 10 * sc, fill=CAB_D)
    for r in range(3):
        for c in range(6):
            on = math.sin(t * 6 + r * 1.7 + c * 2.3) > 0.2
            p.circle(X(-215 + c * 40), Y(-380 + r * 48), 11 * sc, fill=YEL if on else (70, 80, 96))
    p.line([(X(-115), Y(-225)), (X(-115), Y(-20))], CAB_D, 4 * sc)
    p.rr([X(70), Y(-480), X(270), Y(0)], 18 * sc, fill=CAB_L, outline=CAB_D, width=4 * sc)
    for k, yy in enumerate((-395, -255)):
        rx, ry, rr_ = X(170), Y(yy), 56 * sc
        p.circle(rx, ry, rr_, fill=DARK, outline=CAB_D, width=4 * sc)
        p.circle(rx, ry, 16 * sc, fill=CAB_L)
        ang = t * 3 * (1 if k == 0 else -1)
        for s in range(3):
            a_ = ang + s * 2.094
            p.line([(rx + math.cos(a_) * 20 * sc, ry + math.sin(a_) * 20 * sc),
                    (rx + math.cos(a_) * 50 * sc, ry + math.sin(a_) * 50 * sc)], CAB_L, 5 * sc)
    p.rr([X(95), Y(-170), X(245), Y(-30)], 10 * sc, fill=CAB)
    if wrap > 0:
        sheet(p, [X(-300), Y(-510), X(300), Y(-510 + 520 * wrap)], gap=gap or 54 * sc)
    if tape > 0:
        for yy in (-380, -140):
            p.rect([X(-300), Y(yy), X(-300 + 600 * tape), Y(yy + 44)], fill=TAPE)

def truck(p, ox, base, t, moving):
    bob = abs(math.sin(t * 9)) * 5 if moving else 0
    p.rr([80 + ox, base - bob, 700 + ox, base + 40 - bob], 10, fill=(64, 70, 86))
    p.rr([700 + ox, base - 190 - bob, 900 + ox, base + 40 - bob], 26, fill=TRUCK)
    p.rr([738 + ox, base - 165 - bob, 880 + ox, base - 90 - bob], 14, fill=(170, 215, 240))
    for wx in (200, 560, 800):
        p.circle(wx + ox, base + 60, 44, fill=DARK)
        p.circle(wx + ox, base + 60, 16, fill=EDGE)
        a = -t * 8 if moving else 0
        p.line([(wx + ox + math.cos(a) * 16, base + 60 + math.sin(a) * 16),
                (wx + ox + math.cos(a) * 36, base + 60 + math.sin(a) * 36)], EDGE, 6)
    return bob

def linked_col(p, x, ys, r, link, sizes=None):
    """A column of bubbles joined by air channels (link 0..1 = how much of the channel is drawn)."""
    if link > 0:
        p.rr([x - r * 0.26, ys[0], x + r * 0.26, ys[0] + (ys[-1] - ys[0]) * link], r * 0.26, fill=BUB_S, outline=BUB_E, width=3)
    for k, y in enumerate(ys):
        bubble(p, x, y, r * (sizes[k] if sizes else 1.0))

def plus_button(p, x, y, r):
    p.circle(x, y, r, fill=RED)
    p.line([(x - r * .45, y), (x + r * .45, y)], fill=WHITE, width=12)
    p.line([(x, y - r * .45), (x, y + r * .45)], fill=WHITE, width=12)

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    room(p, t)
    pill(p, 540, 1060, "IT WAS WALLPAPER", prog(t, -0.3, 0.05), size=50)

@V.scene(1)
def curtains(p, t, L):
    a, e = L(1)
    big = t < a + 1.45
    if big:
        big_number(p, t, a - 0.1, 1957, cx=540, cy=700, size=260, start=1900, dur=1.0)
        return
    pill(p, 540, 365, "1957", prog(t, a + 1.45, a + 1.75), bg=WHITE, size=44)
    kin = eo(prog(t, a + 1.45, a + 2.3))
    km = eio(prog(t, a + 2.9, a + 4.1))
    lx = lerp(lerp(-520, 90, kin), 340, km)
    rx = lerp(lerp(1460, 590, kin), 340, km)
    p.line([(60, 446), (1000, 446)], EDGE, 8)
    curtain(p, lx, 446, lx + 400, 970, CURT_A, "stripes")
    curtain(p, rx, 446, rx + 400, 970, CURT_B, "dots")
    kb = prog(t, a + 4.4, a + 6.0)
    if kb > 0:
        size = lambda x, y: clamp((kb * 1.5 - (y - 446) / 524) * 3)
        sheet(p, [340, 446, 740, 970], gap=50, base=None, size=size)
        for k, (sx, sy) in enumerate([(300, 520), (780, 620), (300, 800), (780, 900)]):
            sparkle(p, sx, sy, 22 * math.sin(math.pi * prog(t, a + 4.6 + k * 0.25, a + 5.2 + k * 0.25)))
    if t > a + 6.3:
        tg = eback(prog(t, a + 6.3, a + 6.7))
        sw = math.sin((t - a - 6.3) * 4) * 6 * (1 - prog(t, a + 6.3, a + 8.5))
        if tg > 0:
            p.line([(740, 470), (790 + sw, 520)], EDGE, 4)
            p.rr([760 + sw, 520, 760 + sw + 190 * tg, 520 + 90 * tg], 14, fill=WHITE, outline=EDGE, width=3)
            p.text((760 + sw + 95 * tg, 565), "NEW!", f2("anton", max(8, int(52 * tg))), RED)
    pill(p, 540, 1065, "2 SHOWER CURTAINS", prog(t, a + 1.9, a + 2.2) * (1 - prog(t, a + 4.3, a + 4.5)), bg=WHITE, size=42)
    pill(p, 540, 1065, "AIR TRAPPED", prog(t, a + 4.8, a + 5.1) * (1 - prog(t, a + 6.0, a + 6.2)), bg=BLUE, size=44)
    pill(p, 540, 1065, "TEXTURED WALLPAPER", prog(t, a + 6.4, a + 6.7), bg=YEL, size=44)

@V.scene(2)
def flops(p, t, L):
    a, e = L(2)
    dx = lerp(-560, 0, eo(prog(t, a - 0.3, a + 0.3)))
    wall_roll(p, 100 + dx, 440, 580 + dx, 640)
    pill(p, 340 + dx, 380, "FOR SALE", prog(t, a - 0.1, a + 0.2) * (1 - prog(t, a + 0.7, a + 0.8)), bg=WHITE, size=36)
    cross(p, 340, 540, 105, prog(t, a + 0.65, a + 0.85), shake_t=t - (a + 0.65))
    pill(p, 340, 705, "FLOP #1", prog(t, a + 0.75, a + 1.0), bg=RED, fg=WHITE, size=42)
    # sun over the greenhouse, rays turning
    if t > a + 1.2:
        ks = eback(prog(t, a + 1.2, a + 1.6))
        for k in range(8):
            ang = t * 0.8 + k * math.pi / 4
            p.line([(870 + math.cos(ang) * 62 * ks, 450 + math.sin(ang) * 62 * ks),
                    (870 + math.cos(ang) * 92 * ks, 450 + math.sin(ang) * 92 * ks)], YEL, 9)
        p.circle(870, 450, 48 * ks, fill=YEL)
    up = eo(prog(t, a + 1.25, a + 1.9))
    if up > 0:
        dy = lerp(700, 0, up)
        greenhouse(p, 440, 790 + dy, 960, 1060 + dy, 640 + dy, t)
    cross(p, 700, 880, 95, prog(t, a + 4.15, a + 4.35), shake_t=t - (a + 4.15))
    pill(p, 700, 1112, "GREENHOUSE INSULATION", prog(t, a + 1.7, a + 2.0) * (1 - prog(t, a + 4.0, a + 4.15)), bg=GREEN, size=36)
    pill(p, 700, 1112, "FLOP #2", prog(t, a + 4.25, a + 4.5), bg=RED, fg=WHITE, size=42)

@V.scene(3, 4)
def ibm(p, t, L):
    a3, e3 = L(3); a4, e4 = L(4)
    if t < a3 + 1.85:
        big_number(p, t, a3 - 0.05, 1959, cx=540, cy=680, size=260, start=1957, dur=0.8)
        return
    sk = eio(prog(t, a4 + 5.0, a4 + 5.8))
    moving = t > a4 + 5.6
    ox = lerp(-900, 0, eo(prog(t, a4 + 5.0, a4 + 5.8)))
    if sk > 0:
        # road with dashes rushing past
        p.rect([60, 985, 1000, 1000], fill=SLATE_L)
        for k in range(6):
            x = 1000 - ((t * 420 + k * 190) % 1140)
            p.rr([x, 1040, x + 100, 1054], 7, fill=(90, 106, 130))
    else:
        p.rect([80, 1000, 1000, 1012], fill=SLATE_L)
    bob = truck(p, ox, 880, t, moving) if sk > 0 else 0
    k = eback(prog(t, a3 + 1.85, a3 + 2.45))
    shake = math.sin(t * 46) * 7 * prog(t, a3 + 5.8, a3 + 6.0) * (1 - prog(t, a4 + 1.7, a4 + 2.0))
    sc = k * lerp(1.0, 0.6, sk)
    cx = lerp(540, 390, sk) + shake
    base = lerp(1000, 880, sk) - bob
    wrap = eio(prog(t, a4 + 1.8, a4 + 3.3))
    tape = eo(prog(t, a4 + 3.8, a4 + 4.6))
    computer(p, cx, base, sc, t, wrap=wrap, tape=tape)
    if prog(t, a3 + 5.8, a3 + 6.0) > 0 and t < a4 + 1.8:      # wobble marks while it shakes
        for k2, (dx, dy) in enumerate([(-320, -300), (320, -200), (-300, -80), (320, -420)]):
            u = (t * 2 + k2 * 0.33) % 1
            p.line([(cx + dx, base + dy), (cx + dx + (24 if dx > 0 else -24) * (1 + u), base + dy - 10)], WHITE, 6)
    pill(p, 540, 362, "1959", prog(t, a3 + 1.85, a3 + 2.1) * (1 - prog(t, a3 + 5.6, a3 + 5.75)), bg=WHITE, size=44)
    pill(p, 540, 362, "SHIP IT SAFELY?", prog(t, a3 + 5.85, a3 + 6.15) * (1 - prog(t, a4 - 0.25, a4 - 0.1)), bg=RED, fg=WHITE, size=42)
    pill(p, 540, 362, "SEALED AIR", prog(t, a4 + 0.25, a4 + 0.55) * (1 - prog(t, a4 + 4.9, a4 + 5.05)), bg=YEL, size=44)
    pill(p, 540, 1085, "IBM 1401", prog(t, a3 + 4.3, a3 + 4.6) * (1 - prog(t, a4 + 2.0, a4 + 2.15)), bg=WHITE, size=44)
    pill(p, 540, 1085, "PACKAGING", prog(t, a4 + 2.3, a4 + 2.6) * (1 - prog(t, a4 + 4.9, a4 + 5.05)), bg=BLUE, size=44)
    pill(p, 540, 1110, "NO DAMAGE", prog(t, a4 + 6.4, a4 + 6.7), bg=GREEN, size=44)
    tick(p, 800, 362, 52, prog(t, a4 + 6.5, a4 + 6.8))

MINIS = [(200 + c * 227, 640 + r * 200) for r in range(3) for c in range(4)]

@V.scene(5)
def best_seller(p, t, L):
    a, e = L(5)
    for i, (x, y) in enumerate(MINIS):
        k = eback(prog(t, a - 0.1 + i * 0.12, a + 0.3 + i * 0.12))
        w = eio(prog(t, a + 4.3 + i * 0.07, a + 4.8 + i * 0.07))
        computer(p, x, y, 0.3 * k, t + i, wrap=w, gap=26)
        if w >= 1:
            sparkle(p, x + 80, y - 150, 16 * math.sin(math.pi * prog(t, a + 4.8 + i * 0.07, a + 5.3 + i * 0.07)))
    pill(p, 540, 370, "BEST-SELLING COMPUTER YET", prog(t, a + 1.2, a + 1.5), bg=YEL, size=38)
    pill(p, 540, 1105, "FINALLY, A JOB", prog(t, a + 5.2, a + 5.5), bg=GREEN, size=44)

COLS = (330, 540, 750)
ROWS = (470, 590, 710, 830, 950)

@V.scene(6, 7)
def no_pop(p, t, L):
    a6, e6 = L(6); a7, e7 = L(7)
    if t < a6 + 1.2:
        big_number(p, t, a6 - 0.05, 2015, cx=540, cy=700, size=260, start=1957, dur=0.9)
        return
    pill(p, 540, 362, "2015", prog(t, a6 + 1.2, a6 + 1.45), bg=WHITE, size=44)
    kbase = eback(prog(t, a6 + 1.2, a6 + 1.6))
    if kbase > 0:
        p.rr([540 - 300 * kbase, 710 - 320 * kbase, 540 + 300 * kbase, 710 + 320 * kbase], 36, fill=FLAT)
    sq = eio(prog(t, a7 + 2.6, a7 + 3.3)) * (1 - eio(prog(t, a7 + 6.6, a7 + 7.2)))
    for c, x in enumerate(COLS):
        link = eo(prog(t, a7 + 0.15 + c * 0.25, a7 + 0.85 + c * 0.25))
        sizes = []
        for r_, y in enumerate(ROWS):
            pk = eback(prog(t, a6 + 1.4 + (r_ * 3 + c) * 0.06, a6 + 1.8 + (r_ * 3 + c) * 0.06))
            if c == 0:
                d = abs(r_ - 2)
                pk *= (1 - 0.45 * sq) if d == 0 else (1 + sq * (0.18 if d == 1 else 0.08))
            sizes.append(pk)
        linked_col(p, x, ROWS, 50, link, sizes)
    # air flowing out of the squeezed bubble into its neighbours
    if a7 + 3.1 < t < a7 + 6.2:
        for path in ([(330, 690), (330, 470)], [(330, 730), (330, 950)]):
            flow_dots(p, path, t - a7, speed=1.4, n=4, r=9, fill=WHITE)
    # finger: a quick test press in line 6, then the real squeeze in line 7
    if a6 + 2.2 < t < a7 - 0.1:
        u = eio(prog(t, a6 + 2.2, a6 + 2.8)) * (1 - eio(prog(t, a7 - 0.7, a7 - 0.1)))
        finger(p, (lerp(1000, 760, u), lerp(1150, 840, u)), ang=55)
    if t > a7 + 1.9:
        u = eio(prog(t, a7 + 1.9, a7 + 2.6)) * (1 - eio(prog(t, a7 + 6.6, a7 + 7.2)))
        edge = 330 - 50 * (1 - 0.45 * sq) + 6
        finger(p, (lerp(-200, edge, u), 712), ang=184, length=420, width=112)
    pill(p, 540, 1095, "THE NO-POP VERSION", prog(t, a6 + 2.9, a6 + 3.2) * (1 - prog(t, a7 - 0.3, a7 - 0.1)), bg=GREEN, size=42)
    pill(p, 540, 1095, "LINKED IN COLUMNS", prog(t, a7 + 0.35, a7 + 0.65) * (1 - prog(t, a7 + 3.1, a7 + 3.25)), bg=YEL, size=42)
    pill(p, 540, 1095, "AIR MOVES ALONG", prog(t, a7 + 3.35, a7 + 3.65) * (1 - prog(t, a7 + 5.5, a7 + 5.65)), bg=BLUE, size=42)
    pill(p, 540, 1095, "HARD TO BURST", prog(t, a7 + 5.75, a7 + 6.05), bg=GREEN, size=44)

POP_SEQ = []
def _pop_seq():
    import random
    rnd = random.Random(5)
    cells = [(i, j) for i, j, x, y in bubble_grid([200, 440, 880, 1000], 62)]
    picks = rnd.sample(cells, 9)
    return [(0.45 + k * 0.36, ij) for k, ij in enumerate(picks)]
POP_SEQ = _pop_seq()

@V.scene(8)
def ships_flat(p, t, L):
    a, e = L(8)
    out = eio(prog(t, a + 3.55, a + 3.95))
    if out < 1:
        ox = -1200 * out
        slide = lerp(900, 0, eo(prog(t, a - 0.3, a + 0.35)))
        x0, x1 = 300 + ox + slide, 960 + ox + slide
        p.rr([x0, 500, x1, 920], 24, fill=FLAT)
        cols = [x0 + 60 + c * 78 for c in range(8)]
        for c, x in enumerate(cols):
            g = eo(prog(t, a + 1.5 + c * 0.22, a + 2.1 + c * 0.22))
            p.rr([x - 6, 560, x + 6, 860], 6, fill=BUB_S if g > 0 else (176, 198, 222))
            for y in (560, 660, 760, 860):
                if g > 0: bubble(p, x, y, 32 * g)
                else: p.circle(x, y, 30, outline=(170, 192, 218), width=3)
        kp = eback(prog(t, a + 0.95, a + 1.3))
        if kp > 0:
            px = 70 + ox
            p.rr([px, 960 - 200 * kp, px + 170 * kp, 960], 22, fill=SLATE_L, outline=EDGE, width=4)
            p.circle(px + 85 * kp, 960 - 130 * kp, 40 * kp, fill=WHITE, outline=EDGE, width=4)
            ang = -2.2 + 2.6 * prog(t, a + 1.3, a + 3.4)
            p.line([(px + 85 * kp, 960 - 130 * kp), (px + 85 * kp + math.cos(ang) * 32 * kp, 960 - 130 * kp + math.sin(ang) * 32 * kp)], RED, 6)
            hose = [(px + 170 * kp, 900), (x0 - 40, 900), (x0 - 40, 710), (x0, 710)]
            p.line(hose, DARK, 16)
            if a + 1.2 < t < a + 3.5:
                flow_dots(p, hose, t - a, speed=1.6, n=5, r=8, fill=WHITE)
        pill(p, 540, 1095, "SHIPS FLAT", prog(t, a + 0.05, a + 0.35) * (1 - prog(t, a + 1.15, a + 1.3)), bg=WHITE, size=44)
        pill(p, 540, 1095, "PUMPED UP ON SITE", prog(t, a + 1.4, a + 1.7) * (1 - prog(t, a + 3.4, a + 3.55)), bg=BLUE, size=42)
    if t > a + 3.6:
        ox = 1200 * (1 - eio(prog(t, a + 3.6, a + 4.0)))
        p.rr([180 + ox, 420, 900 + ox, 1020], 30, fill=SHEET)
        pops = {ij: prog(t, a + 4.0 + tt, a + 4.22 + tt) for tt, ij in POP_SEQ}
        sheet(p, [200 + ox, 440, 880 + ox, 1000], gap=62, base=None, pops=pops)
        for tt, (i, j) in POP_SEQ:
            x = 200 + ox + 62 * 0.55 + j * 62 + (31 if i % 2 else 0); y = 440 + 62 * 0.55 + i * 62 * 0.87
            burst(p, x, y, prog(t, a + 4.05 + tt, a + 4.55 + tt), r=30)
        pill(p, 540, 1095, "THE ORIGINAL STAYS", prog(t, a + 4.3, a + 4.6), bg=GREEN, size=42)
        tick(p, 850, 400, 50, prog(t, a + 4.5, a + 4.8))

CARD_X = (210, 540, 870)

def card_icon(p, i, cx, cy, t):
    if i == 0:
        p.rect([cx - 90, cy - 80, cx + 90, cy + 70], fill=WALL)
        sheet(p, [cx - 90, cy - 80, cx + 90, cy + 70], gap=34, base=None)
        p.rr([cx - 40, cy - 45, cx + 40, cy + 15], 6, fill=BRASS)
        p.rect([cx - 30, cy - 35, cx + 30, cy + 5], fill=(120, 180, 235))
        p.rect([cx - 90, cy + 70, cx + 90, cy + 90], fill=FLOOR)
    elif i == 1:
        greenhouse(p, cx - 95, cy - 20, cx + 95, cy + 85, cy - 85, t, plant=False)
    else:
        linked_col(p, cx - 45, (cy - 70, cy, cy + 70), 30, 1.0)
        linked_col(p, cx + 45, (cy - 70, cy, cy + 70), 30, 1.0)

@V.scene(9, 10)
def outro(p, t, L):
    a9, e9 = L(9); a10, e10 = L(10)
    pill(p, 540, 365, "WHICH WOULD YOU BUY?", prog(t, a9 + 0.1, a9 + 0.4), bg=WHITE, size=40)
    at = (a9 + 1.35, a9 + 2.72, a9 + 4.25)
    for i, cx in enumerate(CARD_X):
        k = eback(prog(t, at[i], at[i] + 0.4))
        if k <= 0: continue
        active = at[i] <= t < (at[i + 1] if i < 2 else a9 + 6.2)
        bob = math.sin((t - at[i]) * 3 + i) * 6
        cy = 660 + bob
        w, h = 120 * k, 175 * k
        p.rr([cx - w, cy - h, cx + w, cy + h], 30, fill=(36, 52, 80), outline=YEL if active else SLATE_L, width=8 if active else 4, shadow=True)
        if k > 0.6:
            card_icon(p, i, cx, cy - 10, t)
        p.text((cx, cy + 130 * k), ("WALLPAPER", "GREENHOUSE", "NO-POP")[i], f2("dm", max(8, int(30 * k))), WHITE)
        p.circle(cx, cy - h, 46 * k, fill=YEL)
        p.text((cx, cy - h + 2), "ABC"[i], f2("anton", max(8, int(62 * k))), INK)
    pill(p, 540, 900, "COMMENT A, B OR C", prog(t, a9 + 6.2, a9 + 6.5), bg=YEL, size=46)
    if t > a10 + 0.15:
        r = 62 * eback(prog(t, a10 + 0.15, a10 + 0.55))
        plus_button(p, 540, 1080, r)
        u = (t - a10 - 0.6) % 1.2 / 1.2
        if t > a10 + 0.6:
            p.circle(540, 1080, lerp(68, 118, u), outline=YEL, width=8 * (1 - u) + 1)

@V.sounds
def cues(L):
    a1, _ = L(1); a2, _ = L(2); a4, _ = L(4); a5, _ = L(5); a7, _ = L(7); a8, _ = L(8); a9, _ = L(9); a10, _ = L(10)
    out = [(tt + 0.08, "pop") for tt, _ in HOOK_POPS]
    out += [(a1 + 4.8, "pop"), (a1 + 6.35, "ding")]
    out += [(a2 + 0.65, "thud"), (a2 + 4.15, "thud")]
    out += [(a4 + 6.5, "ding"), (a5 + 5.2, "ding"), (a7 + 5.75, "ding")]
    out += [(a8 + 4.1 + tt, "pop") for tt, _ in POP_SEQ]
    out += [(a9 + 1.35, "pop"), (a9 + 2.72, "pop"), (a9 + 4.25, "pop"), (a10 + 0.2, "pop")]
    return out

if __name__ == "__main__":
    V.main()
