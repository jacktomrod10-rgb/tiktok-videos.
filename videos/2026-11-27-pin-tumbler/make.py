"""Episode 10 (long): How a key opens a lock (the pin tumbler).
    python3 -I videos/2026-11-27-pin-tumbler/make.py tts | stills ... | render videos/2026-11-27-pin-tumbler.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "pin-tumbler", episode=10, title="How does a *key* open a *lock*?",
    lines=[
        "Your house key is a password made of metal.",
        "Each bump lifts a tiny pin, split in two, to an exact height. Get every one right, and the lock turns.",
        "Inside, springs push five or six of these pin stacks down, so the top pins sit across the gap between the part that turns and the case around it.",
        "That's what stops it turning. Your key lifts each stack until its split lands exactly on that gap.",
        "The wrong key gets at least one height wrong, and that pin still blocks the gap.",
        "Locksmiths can even write your key down as a number, with one digit for how deep each cut is.",
        "Some locks hide a tiny spacer in their pin stacks, so they can split at two heights. That's how a master key opens lots of locks that each have their own key.",
        "And the idea is ancient. Egyptians used wooden pin locks about four thousand years ago.",
        "In the eighteen sixties, Lynus Yale Junior gave it the small, flat, jagged key we still use today.",
        "So which would you trust on your front door?",
        "A, a key.",
        "B, a keypad code.",
        "Or C, your fingerprint.",
        "Comment A, B or C.",
        "Follow for more everyday genius.",
    ],
    display=[
        "Your house key is a *password* made of metal.",
        "Each bump lifts a tiny pin, *split* in two, to an *exact* height. Get every one right, and the lock *turns*.",
        "Inside, *springs* push five or six of these pin stacks down, so the top pins sit *across* the gap between the part that *turns* and the case around it.",
        "That's what *stops* it turning. Your key lifts each stack until its split lands *exactly* on that gap.",
        "The *wrong* key gets at least one height wrong, and that pin still *blocks* the gap.",
        "Locksmiths can even write your key down as a *number*, with one digit for how *deep* each cut is.",
        "Some locks hide a tiny *spacer* in their pin stacks, so they can split at *two* heights. That's how a *master key* opens lots of locks that each have their own key.",
        "And the idea is *ancient*. *Egyptians* used wooden pin locks about *4,000* years ago.",
        "In the *1860s*, *Linus Yale Jr* gave it the small, flat, *jagged* key we still use today.",
        "So which would you *trust* on your front door?",
        "*A*, a key.",
        "*B*, a keypad code.",
        "Or *C*, your fingerprint.",
        "Comment *A*, *B* or *C*.",
        "Follow for more everyday *genius*.",
    ],
)


# ---------------- palette ----------------
CASE, CASE_D, CASE_L = (128, 140, 158), (92, 102, 120), (168, 180, 198)
HOLE = (20, 26, 36)
KEYPIN, KEYPIN_D = (255, 128, 92), (196, 86, 58)
DRIVER, DRIVER_D = (96, 170, 255), (56, 116, 196)
SPACER_D = (30, 160, 104)
SPRING = (205, 210, 220)
NICKEL, NICKEL_D = (214, 220, 228), (140, 150, 164)
GOLD = (255, 205, 100)
WOOD, WOOD_D, WOOD_L = (170, 116, 66), (120, 80, 44), (204, 152, 96)
SAND, SAND_D = (222, 190, 132), (192, 156, 100)
DOOR, DOOR_D = (156, 102, 64), (116, 74, 44)
BOWHOLE = (18, 32, 54)

DRV = 130     # top (driver) pin length, in lock units; the shear line (the gap) is y = 0
REST = 200    # bottom of a key pin when nothing lifts it
KTOP = 85     # uncut top edge of a key blade
KBOT = 238    # bottom edge of a key blade
PITCH = 110

def mix(c1, c2, k):
    k = clamp(k)
    return tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))

# ---------------- key geometry ----------------
def key_profile(xs, cuts, shoulder, peak=KTOP + 7):
    """Top edge of a key blade (key coords = lock coords when fully in): [(x, y)] from shoulder to tip."""
    pts = [(shoulder, KTOP)]
    for x, c in zip(xs, cuts):
        pts += [(x - 34, peak), (x - 11, c), (x + 11, c), (x + 34, peak)]
    tip = xs[-1] + 100
    pts += [(xs[-1] + 58, peak), (tip, 170), (tip, KBOT)]
    return pts

def prof_y(pts, x):
    if x < pts[0][0] or x > pts[-1][0]: return None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            if x1 - x0 < 1e-6: return max(y0, y1)
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None

def pin_bottoms(xs, pts, kx):
    out = []
    for x in xs:
        y = prof_y(pts, x - kx) if pts else None
        out.append(REST if y is None else min(REST, y))
    return out

def draw_blade(p, X, Y, pts, kx, xa, xb, fill=NICKEL, edge=NICKEL_D, s=1.0):
    """The part of a key blade between lock x xa..xb (sampled, so it can be cut off at the lock face)."""
    a, b = max(xa, pts[0][0] + kx), min(xb, pts[-1][0] + kx)
    if b <= a + 1: return
    xs = [a + (b - a) * k / 60 for k in range(61)] + [x + kx for x, _ in pts if a < x + kx < b]
    top = []
    for x in sorted(xs):
        y = prof_y(pts, x - kx)
        if y is not None: top.append((X(x), Y(y)))
    p.poly(top + [(X(b), Y(KBOT)), (X(a), Y(KBOT))], fill)
    p.line(top, edge, 3 * s)
    p.line([(X(a), Y(KBOT)), (X(b), Y(KBOT))], edge, 3 * s)
    if b - 40 > a: p.line([(X(a), Y(196)), (X(b - 40), Y(196))], edge, 4 * s)

def draw_handle(p, X, Y, shoulder_x, s=1.0, fill=NICKEL, edge=NICKEL_D):
    """Neck + round bow to the left of the key's shoulder (lock coords)."""
    p.rr([X(shoulder_x - 95), Y(KTOP - 22), X(shoulder_x), Y(KBOT + 22)], 10 * s, fill=fill, outline=edge, width=3 * s)
    bx = shoulder_x - 120
    p.circle(X(bx), Y(160), 72 * s, fill=fill, outline=edge, width=4 * s)
    p.circle(X(bx - 22), Y(160), 18 * s, fill=BOWHOLE)

def key_icon(p, cx, cy, sc, col=NICKEL, edge=NICKEL_D):
    """Small flat key, pointing right."""
    p.circle(cx - 70 * sc, cy, 42 * sc, fill=col, outline=edge, width=max(2, 4 * sc))
    p.circle(cx - 84 * sc, cy, 13 * sc, fill=BOWHOLE)
    pts = [(cx - 32 * sc, cy - 18 * sc), (cx + 98 * sc, cy - 18 * sc), (cx + 112 * sc, cy + 2 * sc), (cx + 96 * sc, cy + 18 * sc),
           (cx + 84 * sc, cy + 32 * sc), (cx + 70 * sc, cy + 18 * sc), (cx + 56 * sc, cy + 36 * sc), (cx + 40 * sc, cy + 18 * sc),
           (cx + 26 * sc, cy + 30 * sc), (cx + 12 * sc, cy + 18 * sc), (cx - 32 * sc, cy + 18 * sc)]
    p.poly(pts, col)
    p.line(pts + [pts[0]], edge, max(2, 3 * sc))

# ---------------- the lock ----------------
def spring(p, x, ya, yb, w, width):
    n = 6
    pts = [(x, ya)] + [(x + (w if k % 2 else -w), ya + (yb - ya) * k / (2 * n)) for k in range(1, 2 * n)] + [(x, yb)]
    p.line(pts, SPRING, width)

def dashed(p, x0, x1, y, col, width, dash=24, gap=14):
    x = x0
    while x < x1:
        p.line([(x, y), (min(x1, x + dash), y)], col, width)
        x += dash + gap

def stack_pieces(b, ln, sp):
    """(top, bottom, kind) of the key pin, spacer and top pin, bottom up."""
    out = [(b - ln, b, "key")]
    if sp > 0.5: out.append((b - ln - sp, b - ln, "spacer"))
    out.append((b - ln - sp - DRV, b - ln - sp, "driver"))
    return out

def lock_view(p, ox, oy, s, xs, lens, bottoms, x0=-150, x1=None, spacers=None, key=None, gap=0.0, gap_col=GREEN,
              bad=(), bad_k=1.0, hi_drv=0.0, tint_plug=0.0, tint_case=0.0, t=0.0):
    """Side cutaway of a pin tumbler lock. Lock units: x of each pin stack in xs, the gap (shear line) at y = 0."""
    X = lambda x: ox + x * s
    Y = lambda y: oy + y * s
    x1 = xs[-1] + 130 if x1 is None else x1
    p.rr([X(x0), Y(-230), X(x1), Y(290)], 22 * s, fill=mix(CASE, CASE_L, tint_case), outline=CASE_D, width=4 * s)
    p.rect([X(x0), Y(0), X(x1 - 18), Y(250)], fill=mix(BRASS, GOLD, tint_plug))
    p.line([(X(x0), Y(250)), (X(x1 - 18), Y(250))], BRASS_D, 3 * s)
    with p.flat():
        p.rect([X(x0), Y(80), X(x1 - 40), Y(245)], fill=HOLE)
        for x in xs:
            p.rect([X(x - 27), Y(-215), X(x + 27), Y(0)], fill=HOLE)
            p.rect([X(x - 27), Y(0), X(x + 27), Y(80)], fill=HOLE)
    if key: key(X, Y)
    for i, (x, ln, b) in enumerate(zip(xs, lens, bottoms)):
        sp = spacers[i] if spacers else 0
        pieces = stack_pieces(b, ln, sp)
        dtop = pieces[-1][0]
        spring(p, X(x), Y(-213), Y(dtop), 17 * s, 5 * s)
        for top, bot, kind in pieces:
            if kind == "key":
                pts = [(X(x - 22), Y(top)), (X(x + 22), Y(top)), (X(x + 22), Y(bot - 18)), (X(x), Y(bot)), (X(x - 22), Y(bot - 18))]
                p.poly(pts, KEYPIN)
                p.line(pts + [pts[0]], KEYPIN_D, 3 * s)
            elif kind == "spacer":
                p.rr([X(x - 22), Y(top), X(x + 22), Y(bot)], 5 * s, fill=GREEN, outline=SPACER_D, width=3 * s)
            else:
                ol = YEL if hi_drv > 0.5 else DRIVER_D
                p.rr([X(x - 22), Y(top), X(x + 22), Y(bot)], 8 * s, fill=DRIVER, outline=ol, width=(7 if hi_drv > 0.5 else 3) * s)
    # the gap between the part that turns (plug) and the fixed case
    if gap > 0:
        p.line([(X(x0) + 6, Y(0)), (X(x1) - 6, Y(0))], mix(CASE, gap_col, gap * 0.6), (10 + 10 * gap) * s)
    dashed(p, X(x0) + 8, X(x1) - 8, Y(0), mix(WHITE, gap_col, gap), (4 + 3 * gap) * s)
    for i in bad:
        r = 46 * s * (1 + 0.08 * math.sin(t * 9))
        if bad_k > 0: p.circle(X(xs[i]), Y(0), r * eback(clamp(bad_k)), outline=RED, width=7 * s)
    return X, Y

def lock_face(p, cx, cy, r, ang, glow=0.0):
    """Front view of the lock: the plug turns when ang goes 0 -> 90."""
    if glow > 0: p.circle(cx, cy, r + 14 * glow, fill=mix(BG2, GREEN, glow))
    p.circle(cx, cy, r, fill=CASE, outline=CASE_D, width=5)
    p.circle(cx, cy, r * 0.74, fill=BRASS, outline=BRASS_D, width=4)
    a = math.radians(ang - 90)
    d, n = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    L1, L2, w = r * 0.52, r * 0.30, r * 0.11
    p.poly([(cx + d[0] * L1 + n[0] * w, cy + d[1] * L1 + n[1] * w), (cx + d[0] * L1 - n[0] * w, cy + d[1] * L1 - n[1] * w),
            (cx - d[0] * L2 - n[0] * w, cy - d[1] * L2 - n[1] * w), (cx - d[0] * L2 + n[0] * w, cy - d[1] * L2 + n[1] * w)], HOLE)
    if ang > 3:
        p.arc([cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26], -90, -90 + ang, YEL, 8)

# ---------------- scene 1: the hook ----------------
XS5 = [i * PITCH for i in range(5)]
LENS = [100, 150, 120, 170, 110]               # bottom-pin lengths = the right key's cut depths
PTS5 = key_profile(XS5, LENS, shoulder=-165)
DIG = [(c - 80) // 10 for c in LENS]           # its code, one digit per cut: 2 7 4 9 3

@V.scene(0, 1)
def hook(p, t, L):
    a1, e1 = L(1)
    kx = lerp(-540, 0, eio(prog(t, -0.05, 1.05)))           # fast unlock straight away
    kx = lerp(kx, -540, eio(prog(t, a1 - 0.35, a1 + 0.25)))   # out again
    kx = lerp(kx, 0, eio(prog(t, a1 + 0.6, a1 + 3.6)))        # slow replay
    g = prog(t, 1.0, 1.2) * (1 - prog(t, a1 - 0.45, a1 - 0.25)) + prog(t, a1 + 3.6, a1 + 3.8)
    yel = prog(t, a1 + 2.85, a1 + 3.05) * (1 - prog(t, a1 + 3.5, a1 + 3.6))
    ox, oy = 400, 640
    X = lambda x: ox + x; Y = lambda y: oy + y
    bottoms = pin_bottoms(XS5, PTS5, kx)
    def key(X, Y): draw_blade(p, X, Y, PTS5, kx, -1000, XS5[-1] + 112)
    if yel > 0:
        lock_view(p, ox, oy, 1.0, XS5, LENS, bottoms, key=key, gap=yel, gap_col=YEL, t=t)
    else:
        lock_view(p, ox, oy, 1.0, XS5, LENS, bottoms, key=key, gap=g, t=t)
    draw_handle(p, X, Y, -165 + kx)
    # the split of one stack, ringed
    ks = prog(t, a1 + 1.8, a1 + 2.05) * (1 - prog(t, a1 + 2.7, a1 + 2.85))
    if ks > 0:
        p.circle(X(XS5[2]), Y(bottoms[2] - LENS[2]), 40 * eback(ks), outline=YEL, width=7)
    ang = 90 * (eio(prog(t, 1.25, 1.8)) * (1 - eio(prog(t, a1 - 0.45, a1 - 0.05))) + eio(prog(t, a1 + 5.45, a1 + 6.05)))
    glow = prog(t, 1.25, 1.5) * (1 - prog(t, a1 - 0.45, a1 - 0.2)) + prog(t, a1 + 5.45, a1 + 5.75)
    lock_face(p, 850, 1045, 78, ang, glow)
    pill(p, 540, 352, "YOUR KEY IS A PASSWORD", prog(t, -0.3, 0.0) * (1 - prog(t, a1 + 1.6, a1 + 1.75)), size=44)
    pill(p, 540, 352, "SPLIT IN TWO", prog(t, a1 + 1.8, a1 + 2.05) * (1 - prog(t, a1 + 2.65, a1 + 2.8)), bg=WHITE, size=44)
    pill(p, 540, 352, "EXACT HEIGHT", prog(t, a1 + 2.8, a1 + 3.05) * (1 - prog(t, a1 + 4.05, a1 + 4.2)), bg=YEL, size=44)
    for i, x in enumerate(XS5):
        tick(p, X(x), 372, 28, prog(t, a1 + 4.25 + i * 0.15, a1 + 4.55 + i * 0.15))
    pill(p, 380, 1045, "UNLOCKED", prog(t, 1.6, 1.85) * (1 - prog(t, a1 - 0.45, a1 - 0.3)) + prog(t, a1 + 5.85, a1 + 6.15), bg=GREEN, size=46)

# ---------------- scene 2: inside the lock ----------------
XS3 = [0, PITCH, 2 * PITCH]
LENS3 = [140, 100, 160]
PTS3 = key_profile(XS3, LENS3, shoulder=-165)
PTS3W = key_profile(XS3, [140, 135, 160], shoulder=-165)   # wrong key: the middle cut is too deep

def label(p, x, y, s, pop, bg=WHITE, fg=INK, to=None):
    if pop <= 0: return
    if to: p.arrow((x - 118, y), to, YEL, width=6, head=22)
    pill(p, x, y, s, pop, bg=bg, fg=fg, size=38)

@V.scene(2, 4)
def inside(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3); a4, e4 = L(4)
    s, oy = 1.25, 700
    kr = lerp(-760, 0, eio(prog(t, a3 + 1.9, a3 + 3.7)))
    kr = lerp(kr, -760, eio(prog(t, a4 - 0.25, a4 + 0.35)))
    kw = lerp(-760, 0, eio(prog(t, a4 + 0.45, a4 + 1.9)))
    wrong = t > a4 + 0.4
    pts, kx = (PTS3W, kw) if wrong else (PTS3, kr)
    stuck = prog(t, a3 + 0.05, a3 + 0.25) * (1 - prog(t, a3 + 1.5, a3 + 1.7))
    block = prog(t, a4 + 2.8, a4 + 3.0) * (1 - prog(t, a4 + 4.0, a4 + 4.2))
    ox = 275 + math.sin(t * 38) * 7 * max(stuck, block)
    bottoms = pin_bottoms(XS3, pts, kx)
    push = -70 * (1 - eback(prog(t, a2 + 0.85, a2 + 1.45)))           # springs push the stacks down
    bottoms = [b + push for b in bottoms]
    g = prog(t, a3 + 3.75, a3 + 4.0) * (1 - prog(t, a4 - 0.3, a4 - 0.1))
    gy = (0.6 + 0.4 * pulse(t, 0.5)) * prog(t, a2 + 5.3, a2 + 5.5) * (1 - prog(t, a2 + 6.6, a2 + 6.8))
    bad, bad_k = (), 0
    if stuck > 0: bad, bad_k = (0, 1, 2), prog(t, a3 + 0.05, a3 + 0.3) * (1 - prog(t, a3 + 1.5, a3 + 1.7))
    if t > a4 + 2.55: bad, bad_k = (1,), prog(t, a4 + 2.55, a4 + 2.8)
    def key(X, Y): draw_blade(p, X, Y, pts, kx, -150, XS3[-1] + 112, s=s)
    hd = prog(t, a2 + 4.2, a2 + 4.3) * (1 - prog(t, a2 + 5.9, a2 + 6.0))
    tp = (0.5 + 0.5 * pulse(t, 0.6)) * prog(t, a2 + 6.6, a2 + 6.8) * (1 - prog(t, e2 - 0.1, e2 + 0.1))
    tc = (0.5 + 0.5 * pulse(t, 0.6)) * prog(t, a2 + 7.7, a2 + 7.9) * (1 - prog(t, e2 - 0.1, e2 + 0.1))
    X, Y = lock_view(p, ox, oy, s, XS3, LENS3, bottoms, key=key, gap=g if g > 0 else gy, gap_col=GREEN if g > 0 else YEL,
                     bad=bad, bad_k=bad_k, hi_drv=hd, tint_plug=tp, tint_case=tc, t=t)
    # labels on the right
    label(p, 865, 470, "SPRINGS", prog(t, a2 + 0.7, a2 + 1.0) * (1 - prog(t, a2 + 3.6, a2 + 3.8)), to=(X(XS3[2]) + 34, 470))
    pill(p, 540, 352, "5 OR 6 PIN STACKS", prog(t, a2 + 1.4, a2 + 1.7) * (1 - prog(t, a2 + 3.7, a2 + 3.9)), bg=WHITE, size=42)
    label(p, 865, 610, "TOP PINS", prog(t, a2 + 4.2, a2 + 4.5) * (1 - prog(t, a2 + 5.9, a2 + 6.1)), bg=DRIVER, to=(X(XS3[2]) + 30, 610))
    label(p, 865, 700, "THE GAP", prog(t, a2 + 5.3, a2 + 5.6) * (1 - prog(t, e2 + 0.1, e2 + 0.3)), bg=YEL, to=(X(350) + 6, 700))
    label(p, 865, 880, "TURNS", prog(t, a2 + 6.6, a2 + 6.9) * (1 - prog(t, e2 + 0.1, e2 + 0.3)), bg=GOLD, to=(X(350) - 10, 880))
    label(p, 865, 455, "FIXED", prog(t, a2 + 7.7, a2 + 8.0) * (1 - prog(t, e2 + 0.1, e2 + 0.3)), bg=CASE_L, to=(X(350) + 4, 455))
    pill(p, 540, 352, "STUCK", stuck, bg=RED, fg=WHITE, size=46)
    pill(p, 540, 352, "LINED UP", g, bg=GREEN, size=46)
    tick(p, 865, 700, 58, g)
    pill(p, 540, 352, "WRONG KEY", prog(t, a4 + 0.4, a4 + 0.7), bg=RED, fg=WHITE, size=46)
    cross(p, 865, 700, 52, prog(t, a4 + 2.8, a4 + 3.0), shake_t=t - (a4 + 2.8))
    pill(p, 865, 820, "BLOCKED", prog(t, a4 + 2.9, a4 + 3.2), bg=RED, fg=WHITE, size=40)

# ---------------- scene 3: the key is a number ----------------
@V.scene(5)
def code(p, t, L):
    a, e = L(5)
    s, oy = 0.95, 545
    ox = lerp(1500, 412, eo(prog(t, a - 0.3, a + 0.4))) + math.sin(t * 1.6) * 4
    X = lambda x: ox + x * s; Y = lambda y: oy + y * s
    draw_blade(p, X, Y, PTS5, 0, -1000, 1000, s=s)
    draw_handle(p, X, Y, -165, s=s)
    u = prog(t, a + 0.9, a + 2.6)
    if 0 < u < 1:
        sx = X(lerp(-150, 560, u))
        p.line([(sx, Y(30)), (sx, Y(290))], (130, 225, 255), 8)
        p.circle(sx, Y(30), 10, fill=(130, 225, 255)); p.circle(sx, Y(290), 10, fill=(130, 225, 255))
    for i, (x, c) in enumerate(zip(XS5, LENS)):
        k = eback(prog(t, a + 3.05 + i * 0.3, a + 3.4 + i * 0.3))
        if k <= 0: continue
        p.line([(X(x), Y(KTOP - 45)), (X(x), Y(c))], YEL, 6)
        p.line([(X(x) - 16, Y(KTOP - 45)), (X(x) + 16, Y(KTOP - 45))], YEL, 6)
        p.circle(X(x), Y(c), 10 * k, fill=YEL)
        p.text((X(x), Y(345)), str(DIG[i]), f2("anton", max(8, int(120 * k))), YEL)
    pill(p, 540, 372, "WRITTEN AS A NUMBER", prog(t, a + 0.6, a + 0.9), bg=WHITE, size=44)
    pill(p, 540, 1070, "1 DIGIT = HOW DEEP 1 CUT IS", prog(t, a + 4.6, a + 4.9), bg=YEL, size=38)

# ---------------- scene 4: master keys ----------------
DOORX = (180, 400, 620, 840)
DOOR_KEYS = (BLUE, GREEN, (190, 140, 255), NICKEL)
MKEY, MKEY_D = ORANGE, (186, 92, 36)
MK_T0, MK_DUR = 6.1, 1.6          # master key flight, relative to line 6

def mk_x(t, a): return lerp(-160, 1240, (t - (a + MK_T0)) / MK_DUR)
def mk_pass(i, a): return a + MK_T0 + MK_DUR * (DOORX[i] + 160) / 1400

@V.scene(6)
def master(p, t, L):
    a, e = L(6)
    out = eio(prog(t, a + 4.85, a + 5.3))
    if out < 1:
        dx = -1100 * out
        sp = 40 * eback(prog(t, a + 0.95, a + 1.35))
        for side, (cx, cut, name) in enumerate(((290, 110, "YOUR KEY"), (790, 150, "MASTER KEY"))):
            pts = key_profile([0], [cut], shoulder=-300)
            kx = lerp(-430, 0, eio(prog(t, a + 3.1 + side * 0.5, a + 3.75 + side * 0.5)))
            bottoms = pin_bottoms([0], pts, kx)
            g = prog(t, a + 3.75 + side * 0.5, a + 3.95 + side * 0.5)
            col = (MKEY, MKEY_D) if side else (NICKEL, NICKEL_D)
            def key(X, Y, pts=pts, kx=kx, col=col): draw_blade(p, X, Y, pts, kx, -120, 112, fill=col[0], edge=col[1], s=1.2)
            lock_view(p, cx + dx, 680, 1.2, [0], [110], bottoms, x0=-120, x1=120, spacers=[sp], key=key, gap=g, t=t)
            tick(p, cx + dx + 120, 470, 36, g)
            pill(p, cx + dx, 1085, name, prog(t, a + 3.0 + side * 0.5, a + 3.3 + side * 0.5), bg=MKEY if side else WHITE, size=40)
        pill(p, 540 + dx, 352, "TINY SPACER", prog(t, a + 0.95, a + 1.25) * (1 - prog(t, a + 3.0, a + 3.15)), bg=GREEN, size=44)
        pill(p, 540 + dx, 352, "SPLITS AT 2 HEIGHTS", prog(t, a + 3.2, a + 3.5), bg=YEL, size=44)
    if t > a + 4.9:
        dx = 1100 * (1 - eo(prog(t, a + 4.9, a + 5.45)))
        mx = mk_x(t, a)
        for i, x in enumerate(DOORX):
            x += dx
            p.rr([x - 92, 470, x + 92, 900], 14, fill=DOOR, outline=DOOR_D, width=5)
            p.rr([x - 70, 494, x + 70, 670], 8, fill=DOOR_D)
            p.rr([x - 70, 700, x + 70, 876], 8, fill=DOOR_D)
            p.circle(x + 58, 690, 15, fill=BRASS)
            opened = t > mk_pass(i, a)
            if opened:
                tick(p, x, 430, 32, prog(t, mk_pass(i, a), mk_pass(i, a) + 0.3))
            kk = eback(prog(t, a + 7.9 + i * 0.18, a + 8.25 + i * 0.18))
            if kk > 0: key_icon(p, x - 4, 960, 0.5 * kk, DOOR_KEYS[i], mix(DOOR_KEYS[i], INK, 0.35))
        if -200 < mx < 1300:
            key_icon(p, mx, 1080, 0.95, MKEY, MKEY_D)
        pill(p, 540, 352, "1 MASTER KEY", prog(t, a + 5.5, a + 5.8) * (1 - prog(t, a + 7.7, a + 7.85)), bg=MKEY, size=44)
        pill(p, 540, 352, "EACH STILL HAS ITS OWN", prog(t, a + 7.85, a + 8.15), bg=WHITE, size=42)

# ---------------- scene 5: 4,000 years ----------------
EPIN = (430, 545, 660)

def egypt_lock(p, t, a, dx=0.0):
    """Ancient wooden pin lock: pins drop from a fixed block into a sliding bolt; a key with pegs lifts them."""
    p.rr([100 + dx, 445, 980 + dx, 885], 30, fill=SAND)
    for y in (580, 700, 830):
        p.line([(120 + dx, y), (960 + dx, y)], SAND_D, 4)
    p.poly([(810 + dx, 545), (885 + dx, 455), (960 + dx, 545)], SAND_D)
    kin = eio(prog(t, a + 2.35, a + 3.45))
    lift = 62 * eio(prog(t, a + 3.65, a + 4.15))
    slide = -170 * eio(prog(t, a + 4.55, a + 5.3))
    kxl = lerp(940, 290, kin) + slide + dx
    bx = 250 + slide + dx
    # fixed block with pin channels
    p.rr([330 + dx, 515, 760 + dx, 650], 12, fill=WOOD_D)
    for x in EPIN:
        p.rect([x - 22 + dx, 528, x + 22 + dx, 650], fill=(70, 46, 26))
    # bolt with holes and a hollow underneath for the key
    p.rr([bx, 650, bx + 620, 790], 14, fill=WOOD)
    for x in EPIN:
        hx = x - 250 + bx
        p.rect([hx - 22, 650, hx + 22, 712], fill=(96, 62, 34))
    with p.flat():
        p.rect([bx + 40, 712, bx + 620, 776], fill=(96, 62, 34))
    # key: a stick with pegs
    ky = 742 - lift
    p.rr([kxl, ky, kxl + 600, ky + 30], 10, fill=WOOD_L, outline=WOOD_D, width=3)
    p.rr([kxl + 590, ky - 30, kxl + 660, ky + 60], 16, fill=WOOD_L, outline=WOOD_D, width=3)
    pegs = []
    for k in (140, 255, 370):
        px = kxl + k
        p.rect([px - 12, ky - 30, px + 12, ky], fill=WOOD_L)
        pegs.append(px)
    # pins: rest in the bolt holes unless a peg under them pushes them up
    for x in EPIN:
        bot = 710
        for px in pegs:
            if abs(px - (x + dx)) < 14: bot = min(bot, ky - 30)
        p.rr([x - 17 + dx, bot - 112, x + 17 + dx, bot], 8, fill=(236, 196, 140), outline=WOOD_D, width=3)
    g = prog(t, a + 4.15, a + 4.35)
    if g > 0: p.line([(330 + dx, 650), (760 + dx, 650)], GREEN, 8)
    else: dashed(p, 335 + dx, 755 + dx, 650, WHITE, 4)
    return g

@V.scene(7, 8)
def history(p, t, L):
    a7, e7 = L(7); a8, e8 = L(8)
    if t < a7 + 1.55:
        big_number(p, t, a7 - 0.1, 4000, cx=540, cy=660, size=240, start=0, dur=1.0, fmt="{:,}")
        if t > a7 + 0.25: p.text((540, 840), "YEARS AGO", f2("dm", 56), WHITE)
        return
    if t < a8 - 0.15:
        dx = 1100 * (1 - eo(prog(t, a7 + 1.55, a7 + 2.05)))
        g = egypt_lock(p, t, a7, dx)
        pill(p, 540, 352, "4,000 YEARS AGO", prog(t, a7 + 1.6, a7 + 1.9), bg=WHITE, size=44)
        pill(p, 540, 975, "WOODEN PINS", prog(t, a7 + 2.9, a7 + 3.2) * (1 - prog(t, a7 + 4.1, a7 + 4.2)), bg=SAND, size=48)
        pill(p, 540, 975, "SAME IDEA", prog(t, a7 + 4.3, a7 + 4.6), bg=GREEN, size=48)
        return
    if t < a8 + 1.45:
        big_number(p, t, a8 - 0.15, 1860, cx=540, cy=680, size=240, start=1000, dur=0.9, fmt="{}s")
        return
    # the old wooden key shrinks into the small flat one
    ko = 1 - eio(prog(t, a8 + 1.45, a8 + 2.15))
    if ko > 0.02:
        w = 600 * ko
        p.rr([540 - w / 2, 690 - 16 * ko, 540 + w / 2, 690 + 16 * ko], 10 * ko, fill=WOOD_L, outline=WOOD_D, width=3)
        p.rr([540 + w / 2 - 10 * ko, 690 - 45 * ko, 540 + w / 2 + 60 * ko, 690 + 45 * ko], 16 * ko, fill=WOOD_L)
        for k in (0.23, 0.42, 0.62):
            px = 540 - w / 2 + w * k
            p.rect([px - 12 * ko, 690 - 46 * ko, px + 12 * ko, 690 - 16 * ko], fill=WOOD_L)
    kn = eback(prog(t, a8 + 1.75, a8 + 2.35))
    if kn > 0:
        s = 0.85 * kn
        bob = math.sin(t * 2.4) * 8
        ox, oy = 540 - 94 * s, 700 - 160 * s + bob
        X = lambda x: ox + x * s; Y = lambda y: oy + y * s
        draw_blade(p, X, Y, PTS5, 0, -1000, 1000, s=s)
        draw_handle(p, X, Y, -165, s=s)
        sh = prog(t, a8 + 4.2, a8 + 5.2)
        if 0 < sh < 1:
            for i, x in enumerate(XS5):
                q = prog(sh, i * 0.15, i * 0.15 + 0.35)
                if 0 < q < 1: sparkle(p, X(x), Y(LENS[i]) - 30, 26 * math.sin(math.pi * q))
    pill(p, 540, 352, "LINUS YALE JR", prog(t, a8 + 1.5, a8 + 1.8), bg=WHITE, size=44)
    pill(p, 540, 1000, "SMALL · FLAT · JAGGED", prog(t, a8 + 3.0, a8 + 3.3) * (1 - prog(t, a8 + 4.95, a8 + 5.1)), bg=YEL, size=42)
    pill(p, 540, 1000, "STILL USED TODAY", prog(t, a8 + 5.1, a8 + 5.4), bg=GREEN, size=44)
    tick(p, 540, 1100, 40, prog(t, a8 + 5.4, a8 + 5.7))

# ---------------- scene 6: A, B or C ----------------
ROWS_Y = (510, 690, 870)
ROW_LABELS = ("A KEY", "A KEYPAD CODE", "YOUR FINGERPRINT")

def keypad(p, cx, cy):
    p.rr([cx - 44, cy - 58, cx + 44, cy + 58], 12, fill=DARK, outline=EDGE, width=3)
    for r in range(4):
        for c in range(3):
            p.circle(cx - 24 + c * 24, cy - 36 + r * 24, 8, fill=WHITE if (r, c) != (3, 0) and (r, c) != (3, 2) else SLATE_L)

def fingerprint(p, cx, cy):
    for k, r in enumerate(range(10, 58, 9)):
        p.arc([cx - r * 0.8, cy - r, cx + r * 0.8, cy + r], 150 + k * 4, 390 - k * 3, (130, 225, 255), 5)

@V.scene(9, 14)
def outro(p, t, L):
    a9, e9 = L(9); a13, e13 = L(13); a14, e14 = L(14)
    pill(p, 540, 365, "WHICH WOULD YOU TRUST?", prog(t, a9 + 0.1, a9 + 0.4), bg=WHITE, size=42)
    at = (L(10)[0] - 0.05, L(11)[0] - 0.05, L(12)[0] + 0.2)
    for i, y in enumerate(ROWS_Y):
        k = eo(prog(t, at[i], at[i] + 0.4))
        if k <= 0: continue
        active = at[i] <= t < (at[i + 1] if i < 2 else a13 - 0.1)
        xo = lerp(900, 0, k)
        bob = math.sin((t - at[i]) * 3 + i) * 4
        p.rr([110 + xo, y - 78 + bob, 970 + xo, y + 78 + bob], 40, fill=(36, 52, 80), outline=YEL if active else SLATE_L,
             width=8 if active else 4, shadow=True)
        p.circle(200 + xo, y + bob, 48, fill=YEL)
        p.text((200 + xo, y + 2 + bob), "ABC"[i], f2("anton", 62), INK)
        ix = 340 + xo
        if i == 0: key_icon(p, ix + 10, y + bob, 0.48)
        elif i == 1: keypad(p, ix, y + bob)
        else: fingerprint(p, ix, y + bob)
        p.text((430 + xo, y + bob), ROW_LABELS[i], f2("anton", 58), WHITE, anchor="lm")
    pill(p, 540, 1045, "COMMENT A, B OR C", prog(t, a13 - 0.05, a13 + 0.25) * (1 - prog(t, a14 - 0.05, a14 + 0.1)), bg=YEL, size=46)
    if t > a14 + 0.1:
        r = 58 * eback(prog(t, a14 + 0.1, a14 + 0.5))
        p.circle(540, 1045, r, fill=RED)
        p.line([(540 - r * .45, 1045), (540 + r * .45, 1045)], fill=WHITE, width=12)
        p.line([(540, 1045 - r * .45), (540, 1045 + r * .45)], fill=WHITE, width=12)
        if t > a14 + 0.55:
            u = (t - a14 - 0.55) % 1.2 / 1.2
            p.circle(540, 1045, lerp(62, 90, u), outline=YEL, width=8 * (1 - u) + 1)

@V.sounds
def cues(L):
    a1, _ = L(1); a2, _ = L(2); a3, _ = L(3); a4, _ = L(4); a5, _ = L(5); a6, _ = L(6)
    a7, _ = L(7); a8, _ = L(8); a14, _ = L(14)
    out = [(1.25, "ding")]
    out += [(a1 + 4.25 + i * 0.15, "pop") for i in range(5)] + [(a1 + 5.5, "ding")]
    out += [(a2 + 0.9, "boing"), (a3 + 0.1, "thud"), (a3 + 3.8, "ding"), (a4 + 2.85, "thud")]
    out += [(a5 + 3.05 + i * 0.3, "pop") for i in range(5)]
    out += [(a6 + 1.0, "pop"), (a6 + 3.75, "ding"), (a6 + 4.25, "ding")]
    out += [(mk_pass(i, a6), "pop") for i in range(4)]
    out += [(a7 + 4.2, "ding"), (a8 + 5.4, "ding")]
    out += [(L(10)[0], "pop"), (L(11)[0], "pop"), (L(12)[0] + 0.25, "pop"), (a14 + 0.15, "pop")]
    return out

if __name__ == "__main__":
    V.main()
