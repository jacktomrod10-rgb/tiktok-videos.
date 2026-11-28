"""Episode 11 (long): How the cat's eyes in the road clean themselves.
    python3 -I videos/2026-11-28-cats-eyes/make.py tts | stills ... | render videos/2026-11-28-cats-eyes.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "cats-eyes", episode=11, title="How do *cat's eyes* clean *themselves*?",
    lines=[
        "The cat's eyes in the road have eyelids.",
        "When a tyre squashes one, the rubber closes over the glass like an eyelid, and wipes it clean with rainwater caught in its base.",
        "Follow for one bit of everyday genius a day.",
        "Each stud is a rubber dome holding glass reflectors, sitting in a cast iron base set into the road.",
        "The glass has a mirror behind it, so it sends your headlights straight back to your eyes. That's why they glow on a pitch black road.",
        "A Yorkshireman, Percy Shaw from Halifax, patented them in nineteen thirty-four.",
        "The most famous story says he got the idea from a cat on a fence, its eyes shining in his headlights.",
        "Then, in the wartime blackouts, they got so popular that orders hit forty thousand a week.",
        "In the UK, the colours are a code. White marks the lanes, red marks the left edge, and amber marks the central reservation.",
        "So what do the green ones mean?",
        "A, a slip road or lay-by.",
        "B, a bus lane.",
        "Or C, a speed camera ahead.",
        "Comment A, B or C.",
        "Follow for more everyday genius.",
    ],
    display=[
        "The cat's eyes in the road have *eyelids*.",
        "When a *tyre* squashes one, the rubber closes over the glass like an *eyelid*, and wipes it *clean* with *rainwater* caught in its base.",
        "Follow for one bit of *everyday genius* a day.",
        "Each stud is a *rubber* dome holding *glass* reflectors, sitting in a *cast iron* base set into the road.",
        "The glass has a *mirror* behind it, so it sends your headlights *straight back* to your eyes. That's why they *glow* on a pitch black road.",
        "A Yorkshireman, *Percy Shaw* from *Halifax*, patented them in *1934*.",
        "The most famous story says he got the idea from a *cat* on a fence, its eyes *shining* in his headlights.",
        "Then, in the wartime *blackouts*, they got so popular that orders hit *40,000* a week.",
        "In the UK, the colours are a *code*. *White* marks the lanes, *red* marks the left edge, and *amber* marks the central reservation.",
        "So what do the *green* ones mean?",
        "*A*, a slip road or lay-by.",
        "*B*, a bus lane.",
        "Or *C*, a speed camera ahead.",
        "Comment *A*, *B* or *C*.",
        "Follow for more everyday *genius*.",
    ],
)

# ---------------- palette ----------------
ROAD, ROAD_L = (30, 34, 42), (48, 53, 64)
IRON, IRON_D, IRON_L = (96, 104, 118), (62, 68, 80), (132, 142, 158)
RUB, RUB_D = (232, 232, 226), (170, 172, 166)
GLASS, GLASS_DIM = (255, 246, 214), (128, 126, 116)
GLOW = (255, 226, 140)
DIRT = (104, 80, 56)
WATER, WATER_D = (84, 166, 240), (48, 108, 186)
TYRE, TYRE_L = (24, 26, 30), (58, 62, 70)
HUB = (172, 178, 188)
PAPER, PAPER_D = (246, 238, 214), (200, 188, 160)
WOOD, WOOD_D = (112, 80, 52), (80, 56, 36)
CATC = (16, 20, 28)
CATEYE = (210, 255, 150)
AMBER = (255, 170, 40)
SR_RED = (255, 70, 70)
GRN = (60, 230, 120)
MIRROR = (214, 220, 230)

def mix(c1, c2, k):
    k = clamp(k)
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))

def bump(t, a, b, c, d):
    return prog(t, a, b) * (1 - prog(t, c, d))

def at(L, i, f):
    """Time at fraction f through spoken line i."""
    a, e = L(i)
    return a + (e - a) * f

def glow_dot(p, x, y, r, col, k=1.0, base=ROAD_L):
    """A lit stud: soft halo + bright core. k: 0 = unlit, 1 = fully lit."""
    with p.flat():
        if k > 0:
            p.circle(x, y, r * (1.6 + 0.9 * k), fill=mix(base, col, 0.22 * k))
            p.circle(x, y, r * 1.3, fill=mix(base, col, 0.5 * k))
        p.circle(x, y, r, fill=mix((70, 74, 84), col, k))
        if k > 0.5 and r > 5:
            p.circle(x - r * 0.3, y - r * 0.3, r * 0.3, fill=mix(col, WHITE, 0.7))

SPECKS = [(-22, 14, 10), (18, -24, 8), (26, 22, 12), (-6, -34, 6), (-30, -10, 7)]

def lens(p, x, y, r, glow, dirt, col=GLASS):
    """One glass reflector seen face-on (or side-on), with dirt specks."""
    with p.flat():
        if glow > 0:
            p.circle(x, y, r + 14 * glow, fill=mix(RUB_D, GLOW, 0.55 * glow))
        p.circle(x, y, r, fill=mix(GLASS_DIM, col, glow), outline=RUB_D, width=max(2, r * 0.08))
        p.circle(x - r * 0.3, y - r * 0.32, r * 0.22, fill=WHITE)
        if dirt > 0:
            for dx, dy, rr in SPECKS:
                p.circle(x + dx * r / 62, y + dy * r / 62, rr * r / 62 * dirt, fill=DIRT)

# ---------------- scene 1: the hook (front view, the stud blinks) ----------------
def stud_front(p, cx, cy, sc, lid, dirt, glow):
    p.rr([cx - 360 * sc, cy + 80 * sc, cx + 360 * sc, cy + 200 * sc], 26 * sc, fill=IRON_D)
    for sx in (-1, 1):
        x0 = cx + sx * 300 * sc
        p.rr([x0 - 60 * sc, cy - 70 * sc, x0 + 60 * sc, cy + 190 * sc], 44 * sc, fill=IRON, outline=IRON_D, width=4 * sc)
    p.rr([cx - 215 * sc, cy - 160 * sc, cx + 215 * sc, cy + 150 * sc], 80 * sc, fill=RUB, outline=RUB_D, width=4 * sc)
    for dx in (-100, 100):
        lens(p, cx + dx * sc, cy - 10 * sc, 66 * sc, glow, dirt)
    if lid > 0.01:
        top = cy - 158 * sc
        bot = lerp(top + 20 * sc, cy + 84 * sc, lid)
        with p.flat():
            p.rr([cx - 206 * sc, top, cx + 206 * sc, bot], 70 * sc, fill=RUB)
            p.rect([cx - 196 * sc, top + 60 * sc, cx + 196 * sc, bot - 6 * sc], fill=RUB)
        p.line([(cx - 190 * sc, bot - 4 * sc), (cx + 190 * sc, bot - 4 * sc)], RUB_D, 9 * sc)

@V.scene(0)
def hook(p, t, L):
    a0, e0 = L(0)
    with p.flat():
        p.rr([70, 470, 1010, 1130], 48, fill=ROAD)
        for y in (520, 1000):
            pass
    # white road line running past the stud
    with p.flat():
        p.rect([505, 470, 575, 560], fill=(200, 204, 210))
        p.rect([505, 1040, 575, 1130], fill=(200, 204, 210))
    bob = math.sin(t * 2.4) * 6
    sc = lerp(0.8, 1.0, eback(prog(t, 0.0, 0.45)))
    lid = bump(t, 0.42, 0.72, 0.92, 1.2) + bump(t, 1.95, 2.2, 2.35, 2.6)
    dirt = 1 - prog(t, 0.78, 0.86)
    glow = 0.5 + 0.5 * prog(t, 1.05, 1.35)
    stud_front(p, 540, 790 + bob, sc, clamp(lid), dirt, glow)
    sp = prog(t, 1.2, 1.75)
    if 0 < sp < 1:
        for dx, dy, s in ((-170, -120, 1.0), (170, -130, 0.8), (210, 60, 0.7), (-200, 80, 0.9)):
            sparkle(p, 540 + dx, 790 + dy + bob, 30 * s * math.sin(math.pi * sp))
    pill(p, 540, 380, "CAT'S EYES HAVE EYELIDS", prog(t, -0.3, 0.0), size=46)

# ---------------- scene 2: side cutaway, the tyre squashes it ----------------
G = 800     # road surface

def tyre(p, x, y, r, ang):
    p.circle(x, y, r, fill=TYRE)
    with p.flat():
        for k in range(20):
            a = ang + k * math.pi * 2 / 20
            p.line([(x + math.cos(a) * r * 0.88, y + math.sin(a) * r * 0.88), (x + math.cos(a) * r * 0.99, y + math.sin(a) * r * 0.99)], TYRE_L, 10)
        p.circle(x, y, r * 0.7, fill=TYRE_L)
    p.circle(x, y, r * 0.44, fill=HUB, outline=(120, 126, 136), width=5)
    with p.flat():
        for k in range(5):
            a = ang + k * math.pi * 2 / 5
            p.circle(x + math.cos(a) * r * 0.26, y + math.sin(a) * r * 0.26, r * 0.045, fill=(110, 116, 126))
        p.circle(x, y, r * 0.09, fill=(130, 136, 146))

def stud_side(p, press, dirt, glow, water_hi=0.0, t=0.0, lid=None):
    """Cutaway of a cat's eye in the road. press 0..1 pushes the rubber and glass down."""
    with p.flat():
        p.rect([60, G, 1020, 1130], fill=ROAD_L)
        p.line([(60, G), (1020, G)], (86, 92, 106), 6)
    p.rr([300, G - 22, 780, G + 210], 26, fill=IRON, outline=IRON_D, width=5)
    with p.flat():
        p.rr([342, G - 22, 738, G + 168], 16, fill=(22, 26, 34))
        lvl = G + 118 - 14 * press
        p.rect([346, lvl, 734, G + 164], fill=mix(WATER, (150, 210, 255), water_hi))
        for k in range(8):
            x = 360 + k * 48
            p.circle(x + 12, lvl + 2 + math.sin(t * 5 + k) * 3, 14, fill=mix(WATER, (150, 210, 255), water_hi))
    # rubber pad (squashes down)
    top = G - 96 + 104 * press
    p.rr([356, top, 724, G + 112], 54, fill=RUB, outline=RUB_D, width=4)
    ly = top + 52
    for x in (404, 676):
        lens(p, x, ly, 36, glow, dirt)
        lk = clamp(press * 1.3) if lid is None else clamp(lid)
        if lk > 0.02:                       # the rubber closes over the glass like an eyelid
            bot = lerp(ly - 40, ly + 44, lk) + (math.sin(t * 22) * 5 if lk > 0.98 else 0)
            with p.flat():
                p.rr([x - 48, ly - 46, x + 48, bot], 14, fill=RUB)
            p.line([(x - 42, bot - 3), (x + 42, bot - 3)], RUB_D, 7)
    # metal kerbs with the fixed rubber wipers
    for x0, sgn in ((300, 1), (780, -1)):
        p.rr([min(x0, x0 + sgn * 56), G - 48, max(x0, x0 + sgn * 56), G + 36], 14, fill=IRON_L, outline=IRON_D, width=4)
        tip = x0 + sgn * 92
        p.poly([(x0 + sgn * 54, G - 26), (tip, G - 12), (x0 + sgn * 54, G + 4)], (60, 60, 58))
    # splash while it's squashed
    if 0.55 < press:
        for k in range(10):
            u = ((t * 1.7 + k / 10) % 1.0)
            side = -1 if k % 2 else 1
            bx = 540 + side * (60 + 120 * u)
            by = G + 110 - 160 * u + 220 * u * u
            p.circle(bx, by, 9 * (1 - u) + 3, fill=(150, 210, 255))
    return ly

@V.scene(1, 2)
def squash(p, t, L):
    a1, e1 = L(1); a2, e2 = L(2)
    t_in, t_hold, t_out = at(L, 1, 0.0), at(L, 1, 0.17), at(L, 1, 0.52)
    tx = lerp(-300, 540, eio(prog(t, t_in, t_hold)))
    tx = lerp(tx, 1400, eio(prog(t, t_out, at(L, 1, 0.72))))
    R = 230
    press = clamp(1 - abs(tx - 540) / 250) if -300 < tx < 1380 else 0.0
    press = eio(press)
    lid = eio(prog(t, at(L, 1, 0.2), at(L, 1, 0.33))) * (1 - eio(prog(t, at(L, 1, 0.55), at(L, 1, 0.64))))
    dirt = 1 - prog(t, at(L, 1, 0.24), at(L, 1, 0.33))
    glow = 0.35 + 0.65 * prog(t, at(L, 1, 0.6), at(L, 1, 0.68))
    if t > at(L, 1, 0.68): glow = 0.85 + 0.15 * pulse(t, 0.9)
    water_hi = (0.6 + 0.4 * pulse(t, 0.5)) * bump(t, at(L, 1, 0.70), at(L, 1, 0.75), at(L, 1, 1.0), e1 + 0.2)
    ly = stud_side(p, press, dirt, glow, water_hi, t, lid=lid)
    if -R < tx < 1080 + R:
        sq = 14 * clamp(1 - abs(tx - 540) / 250)
        tyre(p, tx, G - R + sq + 6, R, tx / R)
    if t > e1 + 0.6:                         # keep it twinkling during the follow ask
        u = ((t - e1 - 0.6) % 0.9) / 0.9
        x = (404, 676)[int((t - e1 - 0.6) / 0.9) % 2]
        sparkle(p, x + 40, ly - 50, 24 * math.sin(math.pi * u))
    # labels (one at a time, under the stud)
    pill(p, 540, 1075, "TYRE SQUASHES IT", bump(t, at(L, 1, 0.06), at(L, 1, 0.1), at(L, 1, 0.26), at(L, 1, 0.29)), bg=WHITE, size=42)
    pill(p, 540, 1075, "RUBBER CLOSES LIKE AN EYELID", bump(t, at(L, 1, 0.29), at(L, 1, 0.33), at(L, 1, 0.5), at(L, 1, 0.53)), size=40)
    pill(p, 540, 1075, "WIPED CLEAN", bump(t, at(L, 1, 0.53), at(L, 1, 0.57), at(L, 1, 0.68), at(L, 1, 0.71)), bg=GREEN, size=42)
    pill(p, 540, 1075, "RAINWATER IN THE BASE", bump(t, at(L, 1, 0.71), at(L, 1, 0.75), e1 + 0.1, e1 + 0.3), bg=BLUE, size=42)
    if 0.5 < glow:
        sp = prog(t, at(L, 1, 0.62), at(L, 1, 0.62) + 0.6)
        if 0 < sp < 1:
            for x in (404, 676):
                sparkle(p, x + 40, ly - 50, 26 * math.sin(math.pi * sp))
    # follow ask (by the 10 s mark)
    fk = prog(t, at(L, 1, 0.84), at(L, 1, 0.88))
    pill(p, 540, 430, "FOLLOW FOR 1 EVERYDAY GENIUS A DAY", fk, bg=WHITE, size=38)
    if fk > 0:
        r = 56 * eback(prog(t, a2 + 0.1, a2 + 0.45))
        cy = 560
        p.circle(540, cy, r, fill=RED)
        p.line([(540 - r * .45, cy), (540 + r * .45, cy)], fill=WHITE, width=12)
        p.line([(540, cy - r * .45), (540, cy + r * .45)], fill=WHITE, width=12)
        if t > a2 + 0.5:
            u = (t - a2 - 0.5) % 1.1 / 1.1
            p.circle(540, cy, lerp(60, 92, u), outline=YEL, width=8 * (1 - u) + 1)

# ---------------- scene 3: what's inside + the mirror ----------------
def part_glass(p, y, glow, hi):
    for x in (420, 660):
        if hi > 0: p.circle(x, y, 50, outline=YEL, width=7)
        lens(p, x, y, 40, glow, 0)

def part_dome(p, y, hi):
    p.rr([360, y - 70, 720, y + 62], 62, fill=RUB, outline=YEL if hi > 0 else RUB_D, width=8 if hi > 0 else 4)
    with p.flat():
        for x in (420, 660):
            p.circle(x, y - 6, 46, fill=(120, 122, 118))

def part_base(p, y, hi):
    p.rr([300, y - 50, 780, y + 100], 24, fill=IRON, outline=YEL if hi > 0 else IRON_D, width=8 if hi > 0 else 5)
    with p.flat():
        p.rr([346, y - 50, 734, y + 56], 14, fill=(28, 32, 40))
    for x0 in (300, 726):
        p.rr([x0, y - 92, x0 + 54, y + 20], 14, fill=IRON_L, outline=IRON_D, width=4)

PATH = [(300, 664), (523, 664), (838, 700), (523, 736), (300, 736)]

def car_side(p, x, y, glow):
    p.rr([x - 230, y - 50, x + 10, y + 60], 34, fill=BLUE, outline=(52, 110, 190), width=4)
    p.rr([x - 190, y - 120, x - 40, y - 30], 30, fill=BLUE)
    with p.flat():
        p.rr([x - 170, y - 104, x - 60, y - 44], 16, fill=(160, 205, 245))
    for wx in (x - 175, x - 40):
        p.circle(wx, y + 62, 38, fill=TYRE)
        p.circle(wx, y + 62, 16, fill=HUB)
    with p.flat():
        if glow > 0: p.circle(x + 4, y - 18, 26 + 10 * glow, fill=mix(BLUE, GLOW, 0.6 * glow))
        p.circle(x + 4, y - 18, 18, fill=mix((210, 210, 200), WHITE, glow))

def lit_path(p, path, u, col, width):
    """Draw the first fraction u of a polyline."""
    segs = list(zip(path, path[1:]))
    lens_ = [math.dist(a, b) for a, b in segs]
    d = u * sum(lens_)
    pts = [path[0]]
    for (a, b), l in zip(segs, lens_):
        if d >= l:
            pts.append(b); d -= l
        else:
            k = d / max(l, 1e-6)
            pts.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)); break
    if len(pts) > 1:
        p.line(pts, col, width)
    return pts[-1]

@V.scene(3, 4)
def inside(p, t, L):
    a3, e3 = L(3); a4, e4 = L(4)
    if t < e3 + 0.15:
        ex = eio(prog(t, a3 - 0.1, a3 + 0.6)) * (1 - eio(prog(t, at(L, 3, 0.78), at(L, 3, 0.95))))
        with p.flat():
            p.rect([60, 880, 1020, 1130], fill=ROAD_L)
            p.line([(60, 880), (1020, 880)], (86, 92, 106), 6)
        hd = bump(t, at(L, 3, 0.05), at(L, 3, 0.1), at(L, 3, 0.25), at(L, 3, 0.28))
        hg = bump(t, at(L, 3, 0.28), at(L, 3, 0.32), at(L, 3, 0.5), at(L, 3, 0.53))
        hb = bump(t, at(L, 3, 0.55), at(L, 3, 0.6), at(L, 3, 0.76), at(L, 3, 0.79))
        bob = math.sin(t * 2.2) * 6 * ex
        part_base(p, 930, hb)
        part_dome(p, lerp(880, 700, ex) + bob, hd)
        part_glass(p, lerp(874, 470, ex) - bob, 0.8, hg)
        pill(p, 540, 365, "RUBBER DOME", hd, bg=WHITE, size=46)
        pill(p, 540, 365, "GLASS REFLECTORS", hg, bg=GLOW, size=46)
        pill(p, 540, 365, "CAST IRON BASE", hb, bg=IRON_L, size=46)
        pill(p, 540, 365, "SET INTO THE ROAD", prog(t, at(L, 3, 0.82), at(L, 3, 0.88)), bg=YEL, size=46)
        tick(p, 540, 1040, 40, prog(t, at(L, 3, 0.95), e3))
        return
    # the mirror: light goes in, bounces off the back, comes straight back
    k = eo(prog(t, e3 + 0.15, e3 + 0.6))
    dx = lerp(900, 0, k)
    u = prog(t, at(L, 4, 0.12), at(L, 4, 0.42))
    glow = prog(t, at(L, 4, 0.40), at(L, 4, 0.46))
    car_side(p, 300 + dx * 0.4 - 0, 700, 0.6 + 0.4 * pulse(t, 0.8))
    sx, sy, sr = 680 + dx, 700, 160
    with p.flat():
        if glow > 0:
            p.circle(sx, sy, sr + 40 * glow, fill=mix(BG2, GLOW, 0.25 * glow))
    p.circle(sx, sy, sr, fill=mix((176, 214, 240), (255, 244, 200), glow), outline=(120, 170, 210), width=5)
    with p.flat():
        p.circle(sx - 60, sy - 70, 30, fill=(240, 250, 255))
    p.arc([sx - sr - 2, sy - sr - 2, sx + sr + 2, sy + sr + 2], -80, 80, MIRROR, 22)
    p.arc([sx - sr - 14, sy - sr - 14, sx + sr + 14, sy + sr + 14], -80, 80, (150, 158, 172), 6)
    path = [(x + (dx if i not in (0, 4) else dx * 0.4), y) for i, (x, y) in enumerate(PATH)]
    if u > 0 and dx < 5:
        end = lit_path(p, path, u, YEL, 10)
        p.circle(end[0], end[1], 14, fill=WHITE)
        if u >= 1:
            p.arrow(path[3], (path[4][0] + 6, path[4][1]), YEL, width=10, head=30)
            flow_dots(p, path, t, speed=0.7, n=6, r=10, fill=WHITE)
    pill(p, 680 + dx, 935, "MIRROR BEHIND THE GLASS", bump(t, at(L, 4, 0.02), at(L, 4, 0.07), at(L, 4, 0.36), at(L, 4, 0.4)), bg=MIRROR, size=40)
    pill(p, 540, 935, "STRAIGHT BACK TO YOU", bump(t, at(L, 4, 0.4), at(L, 4, 0.45), at(L, 4, 0.62), at(L, 4, 0.65)), bg=YEL, size=42)
    pill(p, 540, 935, "THAT'S WHY THEY GLOW", prog(t, at(L, 4, 0.66), at(L, 4, 0.71)), bg=GLOW, size=44)
    if t > at(L, 4, 0.7):
        for i in range(6):
            q = prog(t, at(L, 4, 0.72) + i * 0.16, at(L, 4, 0.72) + i * 0.16 + 0.3)
            x = 140 + i * 160
            glow_dot(p, x, 1070, 16, GLASS, q, base=BG2)

# ---------------- scene 4: Percy Shaw, 1934, and the cat ----------------
def patent_doc(p, cx, cy, stamp):
    p.rr([cx - 280, cy - 300, cx + 280, cy + 300], 18, fill=PAPER, outline=PAPER_D, width=4, shadow=True)
    p.text((cx, cy - 225), "PATENT", f2("anton", 76), INK)
    p.text((cx, cy - 160), "No. 436,290", f2("dm", 34), (110, 100, 80))
    # line drawing of the stud
    y0 = cy + 10
    p.rr([cx - 190, y0 - 20, cx + 190, y0 + 80], 16, outline=INK, width=4)
    p.rr([cx - 140, y0 - 80, cx + 140, y0 + 40], 50, outline=INK, width=4)
    for x in (-62, 62):
        p.circle(cx + x, y0 - 24, 30, outline=INK, width=4)
    for k in range(4):
        w = 400 if k < 3 else 250
        p.rr([cx - 200, cy + 150 + k * 32, cx - 200 + w, cy + 162 + k * 32], 6, fill=PAPER_D)
    if stamp > 0:
        s = lerp(2.2, 1.0, eo(clamp(stamp)))
        r = 92 * s
        sx, sy = cx + 160, cy + 200
        p.circle(sx, sy, r, outline=RED, width=10 * s)
        p.circle(sx, sy, r * 0.78, outline=RED, width=4 * s)
        p.text((sx, sy + 2), "1934", f2("anton", max(8, int(64 * s))), RED)

def cat(p, x, y, eyes, t):
    tail = [(x + 60, y + 120)]
    for k in range(1, 9):
        q = k / 8
        tail.append((x + 60 + 70 * q + math.sin(t * 2 + q * 3) * 18 * q, y + 120 + 150 * q))
    p.line(tail, CATC, 22)
    p.ell([x - 75, y - 10, x + 75, y + 150], fill=CATC)
    p.circle(x, y - 40, 58, fill=CATC)
    for sx in (-1, 1):
        p.poly([(x + sx * 18, y - 86), (x + sx * 52, y - 128), (x + sx * 56, y - 64)], CATC)
    for sx in (-1, 1):
        ex, ey = x + sx * 22, y - 44
        with p.flat():
            if eyes > 0:
                p.circle(ex, ey, 12 + 26 * eyes, fill=mix(BG2, CATEYE, 0.3 * eyes))
                p.circle(ex, ey, 12 + 12 * eyes, fill=mix(BG2, CATEYE, 0.6 * eyes))
            p.ell([ex - 11, ey - 7, ex + 11, ey + 7], fill=mix((40, 46, 40), CATEYE, eyes))

def fence(p, dx):
    with p.flat():
        for y in (900, 990):
            p.rr([60 + dx, y, 1020 + dx, y + 30], 6, fill=WOOD)
        for k in range(9):
            x = 80 + k * 115 + dx
            p.rr([x, 840, x + 46, 1120], 8, fill=WOOD_D)
            p.poly([(x, 842), (x + 23, 812), (x + 46, 842)], WOOD_D)

@V.scene(5, 6)
def history(p, t, L):
    a5, e5 = L(5); a6, e6 = L(6)
    sw = eio(prog(t, a6 - 0.3, a6 + 0.25))
    if sw < 1:
        dx = -1100 * sw
        k = eo(prog(t, a5 - 0.3, a5 + 0.3))
        bob = math.sin(t * 1.8) * 6
        patent_doc(p, 540 + dx, lerp(1500, 720, k) + bob, prog(t, at(L, 5, 0.78), at(L, 5, 0.86)))
        pill(p, 540 + dx, 365, "PERCY SHAW · HALIFAX, YORKSHIRE", prog(t, at(L, 5, 0.1), at(L, 5, 0.18)), bg=WHITE, size=40)
    if sw > 0:
        dx = 1100 * (1 - sw)
        beam = eo(prog(t, at(L, 6, 0.62), at(L, 6, 0.75)))
        if beam > 0:
            with p.flat():
                bx = lerp(60, 1020, beam)
                p.poly([(60 + dx, 1020), (bx + dx, lerp(1000, 560, beam)), (bx + dx, lerp(1040, 900, beam)), (60 + dx, 1050)], mix(BG2, YEL, 0.22))
                p.circle(60 + dx, 1035, 40, fill=mix(BG2, YEL, 0.6))
        with p.flat():
            p.circle(860 + dx, 470, 56, fill=(220, 226, 236))
            p.circle(838 + dx, 452, 50, fill=BG2)
        fence(p, dx)
        eyes = prog(t, at(L, 6, 0.74), at(L, 6, 0.8))
        cat(p, 560 + dx, 740, eyes, t)
        if 0 < eyes:
            sp = prog(t, at(L, 6, 0.8), at(L, 6, 0.8) + 0.6)
            if 0 < sp < 1:
                sparkle(p, 582 + dx + 30, 660, 26 * math.sin(math.pi * sp))
                sparkle(p, 538 + dx - 30, 680, 20 * math.sin(math.pi * sp))
        pill(p, 540 + dx, 365, "THE MOST FAMOUS STORY", prog(t, a6 + 0.1, a6 + 0.4), bg=WHITE, size=42)
        pill(p, 540 + dx, 1085, "EYES SHINING IN HIS HEADLIGHTS", prog(t, at(L, 6, 0.8), at(L, 6, 0.86)), bg=YEL, size=38)

# ---------------- scene 5: the wartime blackouts ----------------
HOUSES = (190, 420, 650, 880)

@V.scene(7)
def blackout(p, t, L):
    a7, e7 = L(7)
    pill(p, 540, 365, "WARTIME BLACKOUTS", prog(t, a7 + 0.05, a7 + 0.35), bg=WHITE, size=44)
    for i, cx in enumerate(HOUSES):
        p.rr([cx - 100, 880, cx + 100, 1060], 8, fill=(46, 54, 72))
        p.poly([(cx - 116, 884), (cx, 800), (cx + 116, 884)], (60, 68, 88))
        for j, wx in enumerate((cx - 50, cx + 50)):
            off = prog(t, a7 + 0.4 + (i * 2 + j) * 0.12, a7 + 0.5 + (i * 2 + j) * 0.12)
            with p.flat():
                p.rr([wx - 26, 920, wx + 26, 980], 6, fill=mix((255, 214, 120), (22, 28, 40), off))
        with p.flat():
            p.rr([cx - 24, 1000, cx + 24, 1060], 6, fill=(30, 36, 50))
    with p.flat():
        p.rect([60, 1072, 1020, 1140], fill=ROAD)
    for i in range(7):
        q = prog(t, a7 + 1.6 + i * 0.12, a7 + 1.9 + i * 0.12)
        x = 120 + i * 140 + ((t * 40) % 140)
        if 80 < x < 1000:
            glow_dot(p, x, 1106, 12, GLASS, q, base=ROAD)
    n0 = at(L, 7, 0.62)
    big_number(p, t, n0, 40000, cx=540, cy=600, size=210, start=0, dur=1.1, fmt="{:,}")
    if t > n0 + 0.3:
        p.text((540, 735), "ORDERS A WEEK", f2("dm", 54), WHITE)

# ---------------- scene 6: the colour code (driver's view of a motorway) ----------------
VPX, VPY, YB = 540, 400, 1120
LINES_BX = (170, 417, 663, 910)     # red edge, two white lane lines, amber edge

def persp(bx, z):
    return VPX + (bx - VPX) / z, VPY + (YB - VPY) / z

def stud_row(p, t, bx, col, k, speed=2.4, n=14, phase=0.0):
    pts = []
    for j in range(n):
        z = 1.0 + ((j * 1.0 + phase - t * speed) % 13.0)
        pts.append(z)
    for z in sorted(pts, reverse=True):
        x, y = persp(bx, z)
        if y > YB - 8 or y < VPY + 6: continue
        glow_dot(p, x, y, 3 + 15 / z, col, k)

@V.scene(8, 9)
def colours(p, t, L):
    a8, e8 = L(8); a9, e9 = L(9)
    with p.flat():
        p.poly([(VPX - 6, VPY), (VPX + 6, VPY), (1000, YB), (60, YB)], ROAD_L)
        p.line([(VPX + 8, VPY), (1000, 1050)], (120, 128, 140), 10)    # central reservation barrier
        for bx in LINES_BX:
            p.line([(VPX, VPY), (bx, YB)], (78, 84, 98), 4)
    dim = 1 - 0.75 * prog(t, a9 - 0.1, a9 + 0.3)
    kw = prog(t, at(L, 8, 0.33), at(L, 8, 0.38)) * dim
    kr = prog(t, at(L, 8, 0.5), at(L, 8, 0.55)) * dim
    ka = prog(t, at(L, 8, 0.7), at(L, 8, 0.75)) * dim
    stud_row(p, t, LINES_BX[0], SR_RED, kr, phase=0.3)
    stud_row(p, t, LINES_BX[1], GLASS, kw, phase=0.6)
    stud_row(p, t, LINES_BX[2], GLASS, kw, phase=0.1)
    stud_row(p, t, LINES_BX[3], AMBER, ka, phase=0.8)
    # slip road peeling off to the left, with green studs
    kg = prog(t, a9 + 0.2, a9 + 0.5)
    if kg > 0:
        x0, y0 = persp(LINES_BX[0], 2.6)
        with p.flat():
            p.poly([(x0, y0), (x0 - 10, y0), (60, 960), (60, YB), (130, YB)], ROAD_L)
        for j in range(7):
            u = ((j / 7) + t * 0.18) % 1.0
            x, y = lerp(x0, 70, u), lerp(y0, 1000, u)
            glow_dot(p, x, y, 5 + 12 * u, GRN, kg)
    pill(p, 540, 365, "IN THE UK: A COLOUR CODE", prog(t, a8 + 0.1, a8 + 0.4) * (1 - prog(t, a9 - 0.2, a9)), bg=WHITE, size=42)
    pill(p, 540, 1080, "WHITE = LANES", bump(t, at(L, 8, 0.33), at(L, 8, 0.38), at(L, 8, 0.5), at(L, 8, 0.53)), bg=WHITE, size=42)
    pill(p, 540, 1080, "RED = LEFT EDGE", bump(t, at(L, 8, 0.53), at(L, 8, 0.56), at(L, 8, 0.7), at(L, 8, 0.72)), bg=SR_RED, fg=WHITE, size=42)
    pill(p, 540, 1080, "AMBER = CENTRAL RESERVATION", bump(t, at(L, 8, 0.72), at(L, 8, 0.75), e8 + 0.1, e8 + 0.3), bg=AMBER, size=40)
    pill(p, 540, 365, "GREEN = ?", prog(t, a9 + 0.2, a9 + 0.5), bg=GRN, size=50)

# ---------------- scene 7: A, B or C ----------------
COLS = (210, 540, 870)
OPT = (("SLIP ROAD", "OR LAY-BY"), ("BUS LANE",), ("SPEED CAMERA", "AHEAD"))

def icon(p, i, cx, cy, t):
    if i == 0:
        p.rr([cx - 10, cy - 70, cx + 50, cy + 70], 10, fill=(92, 98, 110))
        p.arrow((cx + 20, cy + 62), (cx + 20, cy - 58), WHITE, width=12, head=26)
        p.arrow((cx + 10, cy + 30), (cx - 70, cy - 44), GRN, width=12, head=26)
        for k in range(4):
            glow_dot(p, cx + 4 - k * 22, cy + 20 - k * 20, 6, GRN, 1, base=(36, 52, 80))
    elif i == 1:
        p.rr([cx - 70, cy - 66, cx + 70, cy + 60], 18, fill=SR_RED)
        with p.flat():
            p.rr([cx - 56, cy - 52, cx + 56, cy + 4], 10, fill=(170, 214, 246))
            p.circle(cx - 44, cy + 32, 10, fill=YEL); p.circle(cx + 44, cy + 32, 10, fill=YEL)
            p.rr([cx - 60, cy + 58, cx - 30, cy + 78], 6, fill=TYRE); p.rr([cx + 30, cy + 58, cx + 60, cy + 78], 6, fill=TYRE)
    else:
        p.line([(cx + 10, cy - 10), (cx + 10, cy + 76)], (150, 156, 168), 12)
        p.rr([cx - 60, cy - 70, cx + 60, cy + 6], 12, fill=YEL)
        with p.flat():
            p.circle(cx - 26, cy - 32, 22, fill=DARK)
            p.circle(cx - 26, cy - 32, 10, fill=(90, 140, 220))
            fl = pulse(t, 1.4)
            if fl > 0.85: p.circle(cx + 28, cy - 44, 12, fill=WHITE)

@V.scene(10, 14)
def outro(p, t, L):
    a10, _ = L(10); a13, e13 = L(13); a14, e14 = L(14)
    pill(p, 540, 365, "WHAT DO GREEN STUDS MEAN?", prog(t, a10 - 0.3, a10 - 0.05), bg=GRN, size=42)
    starts = (a10 - 0.05, L(11)[0] - 0.05, L(12)[0] + 0.2)
    for i, cx in enumerate(COLS):
        k = eo(prog(t, starts[i], starts[i] + 0.4))
        if k <= 0: continue
        active = starts[i] <= t < (starts[i + 1] if i < 2 else a13 - 0.1)
        yo = lerp(700, 0, k) + math.sin(t * 2.6 + i) * 5
        p.rr([cx - 150, 450 + yo, cx + 150, 960 + yo], 36, fill=(36, 52, 80), outline=YEL if active else SLATE_L,
             width=8 if active else 4, shadow=True)
        p.circle(cx, 535 + yo, 50, fill=YEL)
        p.text((cx, 538 + yo), "ABC"[i], f2("anton", 64), INK)
        icon(p, i, cx, 690 + yo, t)
        for j, s in enumerate(OPT[i]):
            p.text((cx, 840 + j * 56 + yo), s, f2("anton", 46), WHITE)
    pill(p, 540, 1050, "COMMENT A, B OR C", bump(t, a13 - 0.05, a13 + 0.25, a14 - 0.05, a14 + 0.1), bg=YEL, size=46)
    if t > a14 + 0.1:
        r = 58 * eback(prog(t, a14 + 0.1, a14 + 0.5))
        p.circle(540, 1050, r, fill=RED)
        p.line([(540 - r * .45, 1050), (540 + r * .45, 1050)], fill=WHITE, width=12)
        p.line([(540, 1050 - r * .45), (540, 1050 + r * .45)], fill=WHITE, width=12)
        if t > a14 + 0.55:
            u = (t - a14 - 0.55) % 1.2 / 1.2
            p.circle(540, 1050, lerp(62, 90, u), outline=YEL, width=8 * (1 - u) + 1)

@V.sounds
def cues(L):
    a2, _ = L(2); a7, _ = L(7); a9, _ = L(9); a14, _ = L(14)
    out = [(0.45, "boing"), (1.15, "ding"), (1.95, "boing")]
    out += [(at(L, 1, 0.15), "thud"), (at(L, 1, 0.27), "boing"), (at(L, 1, 0.55), "whoosh"), (at(L, 1, 0.62), "ding")]
    out += [(at(L, 1, 0.86), "pop")]
    out += [(at(L, 3, f), "pop") for f in (0.06, 0.29, 0.56)] + [(at(L, 3, 0.9), "thud")]
    out += [(at(L, 4, 0.42), "ding"), (at(L, 4, 0.67), "pop")]
    out += [(at(L, 5, 0.8), "thud"), (at(L, 6, 0.75), "ding")]
    out += [(a7 + 0.45 + k * 0.24, "pop") for k in range(4)] + [(at(L, 7, 0.62) + 1.1, "cash")]
    out += [(at(L, 8, f), "pop") for f in (0.34, 0.51, 0.71)] + [(a9 + 0.25, "ding")]
    out += [(L(10)[0], "pop"), (L(11)[0], "pop"), (L(12)[0] + 0.25, "pop"), (a14 + 0.15, "pop")]
    return out

if __name__ == "__main__":
    V.main()
