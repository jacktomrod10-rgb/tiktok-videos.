"""Episode 8 (long): How a touchscreen knows where your finger is.
    python3 -I videos/2026-11-25-touchscreen/make.py tts | stills ... | render videos/2026-11-25-touchscreen.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "touchscreen", episode=8, title="How does your *screen* find your *finger*?",
    lines=[
        "Your phone screen doesn't need you to press it.",
        "It's sensing electricity. Your skin is a conductor, so your finger pulls a tiny bit of charge from the screen, right where you touch.",
        "That's why it works with bare skin, but not with a plastic pen, or a woolly glove.",
        "Under the glass is an invisible grid: rows and columns of see-through wires, made of indium tin oxide.",
        "A chip measures the charge at every crossing point, over and over, without stopping.",
        "Where the charge drops, that's you. And from the pattern of drops, it works out the exact spot.",
        "Every crossing is measured on its own, so it can follow several fingers at once. That's how pinch to zoom works.",
        "It's also why rain makes your phone tap things by itself. Water's a conductor too, so the screen thinks it's a finger.",
        "In twenty ten, cold commuters in South Korea were even reported using sausages as a stylus, because electrically, they're close enough to a finger.",
        "Be honest. Have you ever tapped your phone with your nose? Comment yes or no.",
        "Follow for more everyday genius.",
    ],
    display=[
        "Your phone screen doesn't need you to *press* it.",
        "It's sensing *electricity*. Your skin is a *conductor*, so your finger pulls a tiny bit of *charge* from the screen, right where you touch.",
        "That's why it works with *bare* skin, but not with a *plastic* pen, or a woolly *glove*.",
        "Under the glass is an *invisible* grid: rows and columns of see-through wires, made of *indium tin oxide*.",
        "A chip measures the charge at *every* crossing point, over and over, without *stopping*.",
        "Where the charge *drops*, that's you. And from the pattern of drops, it works out the *exact* spot.",
        "Every crossing is measured on its own, so it can follow *several* fingers at once. That's how *pinch* to zoom works.",
        "It's also why *rain* makes your phone tap things by itself. Water's a *conductor* too, so the screen thinks it's a *finger*.",
        "In *2010*, cold commuters in *South Korea* were even reported using *sausages* as a stylus, because electrically, they're close enough to a *finger*.",
        "Be honest. Have you ever tapped your phone with your *nose*? Comment *yes* or *no*.",
        "Follow for more everyday *genius*.",
    ],
)

SKIN, SKIN_D, NAIL = (238, 190, 152), (206, 152, 116), (252, 226, 210)
SCREEN, SCREEN_L = (16, 27, 46), (28, 44, 70)
ROWC, COLC = (90, 170, 255), (255, 140, 66)
WOOL, WOOL_D = (196, 64, 78), (150, 40, 56)
MEAT, MEAT_L, MEAT_D = (192, 100, 62), (232, 150, 110), (140, 68, 40)
DROP = (120, 190, 255)

# ---------------- drawings ----------------
def capsule_pts(tip, ang, length, width, n=10):
    """Stadium shape: rounded tip at `tip`, body running towards angle `ang` (degrees, screen coords)."""
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

def plastic_pen(p, tip, ang=55, length=400, width=58):
    p.poly([tip, along(tip, ang, 70, -width / 2), along(tip, ang, 70, width / 2)], EDGE)
    p.poly(capsule_pts(along(tip, ang, 66), ang, length - 66, width), BLUE)
    p.line([along(tip, ang, 160, -width * 0.18), along(tip, ang, length - 40, -width * 0.18)], (200, 228, 255), 6)

def glove(p, tip, ang=55, length=360, width=170):
    p.poly(capsule_pts(tip, ang, length, width), WOOL)
    for k in range(3):
        dd = 90 + k * 70
        p.line([along(tip, ang, dd, -width * 0.45), along(tip, ang, dd, width * 0.45)], WOOL_D, 8)
    p.poly(capsule_pts(along(tip, ang, 150, -width * 0.42), ang - 50, 150, 74), WOOL)
    p.poly(capsule_pts(along(tip, ang, length - 70), ang, 90, width + 14), WHITE)

def sausage(p, tip, ang, length=300, width=86):
    p.poly(capsule_pts(tip, ang, length, width), MEAT)
    p.line([along(tip, ang, 40, -width * 0.22), along(tip, ang, length - 40, -width * 0.22)], MEAT_L, 9)
    for dd in (0, length):
        x, y = along(tip, ang, dd)
        p.circle(x, y, 9, fill=MEAT_D)

def phone(p, box, screen=SCREEN):
    x0, y0, x1, y1 = box
    p.rr([x0, y0, x1, y1], 56, fill=(52, 62, 80), outline=EDGE, width=5)
    p.rr([x0 + 22, y0 + 22, x1 - 22, y1 - 22], 38, fill=screen)
    cx = (x0 + x1) / 2
    p.rr([cx - 60, y0 + 34, cx + 60, y0 + 52], 9, fill=(52, 62, 80))
    return [x0 + 22, y0 + 22, x1 - 22, y1 - 22]

def icons(p, scr, cols=3, rows=4, hot=None, k=1.0):
    x0, y0, x1, y1 = scr
    pal = [BLUE, GREEN, ORANGE, YEL, RED, (170, 130, 255)]
    gw, gh = (x1 - x0) / cols, (y1 - y0 - 60) / rows
    out = []
    for r in range(rows):
        for c in range(cols):
            cx, cy = x0 + gw * (c + 0.5), y0 + 70 + gh * (r + 0.5)
            s = min(gw, gh) * 0.30 * k
            if s <= 1: continue
            i = r * cols + c
            col = pal[i % len(pal)]
            if hot is not None and i in hot:
                g = hot[i]
                p.rr([cx - s - 14 * g, cy - s - 14 * g, cx + s + 14 * g, cy + s + 14 * g], 26, fill=WHITE)
            p.rr([cx - s, cy - s, cx + s, cy + s], 22, fill=col)
            out.append((cx, cy))
    return out

def ripple(p, x, y, u, col=YEL, r0=20, r1=120, width=8):
    if 0 < u < 1:
        p.circle(x, y, lerp(r0, r1, u), outline=col, width=width * (1 - u) + 1)

def plus_button(p, x, y, r):
    p.circle(x, y, r, fill=RED)
    p.line([(x - r * .45, y), (x + r * .45, y)], fill=WHITE, width=12)
    p.line([(x, y - r * .45), (x, y + r * .45)], fill=WHITE, width=12)

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    k = eback(prog(t, 0.0, 0.45))
    if k <= 0: return
    w, h = 470 * k, 760 * k
    scr = phone(p, [540 - w / 2, 765 - h / 2, 540 + w / 2, 765 + h / 2])
    hot = {4: pulse(t, 0.5)} if t > 1.25 else None
    pts = icons(p, scr, k=k, hot=hot)
    if t > 0.35:
        tx, ty = pts[4] if len(pts) > 4 else (540, 760)
        u = eio(prog(t, 0.35, 1.2))
        tip = (lerp(tx + 260, tx, u), lerp(ty + 330, ty, u))
        for i in range(2):
            ripple(p, tx, ty, prog(t, 1.2 + i * 0.35, 2.0 + i * 0.35))
        finger(p, tip)
    pill(p, 540, 1095, "NO PRESSURE NEEDED", prog(t, 1.4, 1.75), size=40)

@V.scene(1, 2)
def charge(p, t, L):
    a1, e1 = L(1); a2, e2 = L(2)
    if t < a2 - 0.15:
        # side view: finger above the glass, charge flowing up into it
        k = eo(prog(t, a1 - 0.3, a1 + 0.3))
        p.rr([110, 800, 970, 850], 12, fill=(150, 200, 235))           # glass
        for i in range(9):                                            # electrodes under the glass
            x = 150 + i * 98
            glow = 1 - prog(t, a1 + 4.2, a1 + 5.0) * clamp(1 - abs(x - 540) / 160) * 0.8
            col = tuple(int(c * glow + 40 * (1 - glow)) for c in YEL)
            p.rr([x, 875, x + 74, 905], 8, fill=col)
        down = eio(prog(t, a1 + 0.2, a1 + 1.4))
        tip = (540, lerp(560, 800, down))
        finger(p, tip, ang=-90, length=420, width=130)
        if t > a1 + 4.0:
            for j, off in enumerate((-60, 0, 60)):
                path = [(540 + off, 890), (540 + off * 0.5, 820), (540 + off * 0.3, 700), (540, 560)]
                flow_dots(p, path, t - a1, speed=0.9, n=5, r=10, fill=YEL)
        pill(p, 270, 965, "GLASS", prog(t, a1 + 0.3, a1 + 0.6) * (1 - prog(t, a1 + 3.9, a1 + 4.1)), bg=WHITE, size=36)
        pill(p, 790, 965, "ELECTRODES", prog(t, a1 + 0.6, a1 + 0.9) * (1 - prog(t, a1 + 3.9, a1 + 4.1)), bg=YEL, size=36)
        pill(p, 540, 1065, "SKIN CONDUCTS", prog(t, a1 + 1.5, a1 + 1.8), bg=GREEN, size=40)
        pill(p, 540, 965, "CHARGE PULLED AWAY", prog(t, a1 + 4.3, a1 + 4.7), bg=YEL, size=40)
        return
    # three things try the screen: finger works, pen and glove don't
    d = e2 - a2
    spots = [(230, prog(t, a2 + d * 0.30, a2 + d * 0.38)), (540, prog(t, a2 + d * 0.62, a2 + d * 0.70)),
             (850, prog(t, a2 + d * 0.88, a2 + d * 0.96))]
    for i, (x, u) in enumerate(spots):
        kk = eback(prog(t, a2 - 0.1 + i * 0.12, a2 + 0.3 + i * 0.12))
        if kk <= 0: continue
        scr = [x - 120 * kk, 900, x + 120 * kk, 1040]
        lit = i == 0 and u > 0.6
        p.rr(scr, 26, fill=SLATE_L if not lit else (40, 120, 90), outline=EDGE, width=4)
        tip = (x, lerp(650, 900, eio(u)))
        if i == 0: finger(p, tip, ang=-90, length=270, width=110)
        elif i == 1: plastic_pen(p, tip, ang=-90, length=280)
        else: glove(p, tip, ang=-90, length=260, width=150)
        if i == 0:
            ripple(p, x, 970, prog(t, a2 + d * 0.38, a2 + d * 0.38 + 0.8), GREEN)
            tick(p, x, 1110, 40, prog(t, a2 + d * 0.40, a2 + d * 0.46))
        else:
            cross(p, x, 1110, 34, prog(t, a2 + d * (0.72 if i == 1 else 0.97), a2 + d * (0.78 if i == 1 else 1.0)),
                  shake_t=t - (a2 + d * (0.72 if i == 1 else 0.97)))
    pill(p, 230, 1000, "SKIN", prog(t, a2 + d * 0.30, a2 + d * 0.36), bg=GREEN, size=36)
    pill(p, 540, 1000, "PLASTIC", prog(t, a2 + d * 0.62, a2 + d * 0.68), bg=WHITE, size=36)
    pill(p, 850, 1000, "WOOL", prog(t, a2 + d * 0.88, a2 + d * 0.94), bg=WHITE, size=36)

GX0, GY0, GX1, GY1 = 250, 430, 830, 990     # grid area inside the big phone
NC, NR = 6, 7
def gx(c): return GX0 + (GX1 - GX0) * c / (NC - 1)
def gy(r): return GY0 + (GY1 - GY0) * r / (NR - 1)

@V.scene(3, 5)
def grid(p, t, L):
    a3, e3 = L(3); a4, e4 = L(4); a5, e5 = L(5)
    scr = phone(p, [195, 335, 885, 1145])
    # faint app icons first, the grid "x-rays" in over them
    fade = 1 - prog(t, a3 + 0.4, a3 + 1.2)
    if fade > 0:
        icons(p, scr, k=fade)
    for r in range(NR):
        u = eo(prog(t, a3 + 1.0 + r * 0.12, a3 + 1.6 + r * 0.12))
        if u > 0: p.line([(GX0 - 30, gy(r)), (GX0 - 30 + (GX1 - GX0 + 60) * u, gy(r))], ROWC, 7)
    for c in range(NC):
        u = eo(prog(t, a3 + 2.2 + c * 0.12, a3 + 2.8 + c * 0.12))
        if u > 0: p.line([(gx(c), GY0 - 30), (gx(c), GY0 - 30 + (GY1 - GY0 + 60) * u)], COLC, 7)
    pill(p, 390, 1075, "ROWS", prog(t, a3 + 1.2, a3 + 1.5) * (1 - prog(t, e3 - 2.1, e3 - 1.9)), bg=BLUE, size=34)
    pill(p, 680, 1075, "COLUMNS", prog(t, a3 + 2.4, a3 + 2.7) * (1 - prog(t, e3 - 2.1, e3 - 1.9)), bg=ORANGE, size=34)
    pill(p, 540, 1075, "INDIUM TIN OXIDE", prog(t, e3 - 1.8, e3 - 1.4) * (1 - prog(t, a4 - 0.4, a4 - 0.2)), bg=WHITE, size=38)
    # touch position sits between crossings
    fx, fy = gx(2.45), gy(3.6)
    # line 4: a scan runs over every crossing, over and over
    if t >= a4 - 0.2:
        n = NC * NR
        scan = (t - a4) * 26
        for r in range(NR):
            for c in range(NC):
                i = r * NC + c
                age = (scan - i) % n
                base = 10
                if t >= a5:
                    dist = math.hypot(gx(c) - fx, gy(r) - fy)
                    dropk = clamp(1 - dist / 190) * prog(t, a5 + 0.6, a5 + 1.1)
                    col = tuple(int(lerp(cv, rv, dropk)) for cv, rv in zip(WHITE, RED))
                    p.circle(gx(c), gy(r), base + 12 * dropk, fill=col)
                else:
                    hot = clamp(1 - age / 5)
                    p.circle(gx(c), gy(r), base + 10 * hot, fill=YEL if hot > 0 else WHITE)
        pill(p, 540, 1075, "CHECKS EVERY CROSSING", prog(t, a4 + 0.3, a4 + 0.7) * (1 - prog(t, a5 - 0.3, a5 - 0.1)), bg=YEL, size=36)
    # line 5: finger touches, crossings near it drop, then the exact spot is pinned
    if t >= a5 - 0.3:
        u_in = eio(prog(t, a5 - 0.3, a5 + 0.5)); u_out = eio(prog(t, a5 + 1.8, a5 + 2.6))
        if u_out < 1:
            tip = (lerp(fx + 300, fx, u_in) + 300 * u_out, lerp(fy + 360, fy, u_in) + 360 * u_out)
            finger(p, tip)
        pill(p, 540, 1075, "CHARGE DROPS HERE", prog(t, a5 + 0.8, a5 + 1.1) * (1 - prog(t, e5 - 2.2, e5 - 2.0)), bg=RED, fg=WHITE, size=36)
        tk = eback(prog(t, e5 - 2.0, e5 - 1.5))
        if tk > 0:
            R = 70 * tk
            p.circle(fx, fy, R, outline=GREEN, width=8)
            p.line([(fx - R - 24, fy), (fx - R + 20, fy)], GREEN, 8); p.line([(fx + R - 20, fy), (fx + R + 24, fy)], GREEN, 8)
            p.line([(fx, fy - R - 24), (fx, fy - R + 20)], GREEN, 8); p.line([(fx, fy + R - 20), (fx, fy + R + 24)], GREEN, 8)
            p.circle(fx, fy, 9, fill=GREEN)
        pill(p, 540, 1075, "EXACT SPOT", prog(t, e5 - 1.8, e5 - 1.4), bg=GREEN, size=40)

@V.scene(6)
def pinch(p, t, L):
    a, e = L(6)
    scr = phone(p, [215, 345, 865, 1135])
    cx, cy = 540, 730
    z = eio(prog(t, a + 3.4, a + 5.2))
    s = lerp(150, 285, z)
    # a little picture: sky, sun and hills, growing as the fingers spread
    p.rr([cx - s, cy - s * 0.8, cx + s, cy + s * 0.8], 18, fill=(70, 130, 200))
    p.circle(cx + s * 0.45, cy - s * 0.35, s * 0.18, fill=YEL)
    p.poly([(cx - s, cy + s * 0.8), (cx - s * 0.35, cy - s * 0.1), (cx + s * 0.25, cy + s * 0.8)], GREEN)
    p.poly([(cx - s * 0.1, cy + s * 0.8), (cx + s * 0.5, cy + s * 0.15), (cx + s, cy + s * 0.8)], (40, 170, 120))
    # two touches, tracked separately
    spread = lerp(90, 200, z)
    t1 = (cx - spread * 0.75, cy + spread * 0.75)
    t2 = (cx + spread * 0.75, cy - spread * 0.75)
    come = eio(prog(t, a + 0.2, a + 1.2))
    if come > 0:
        for (tx, ty), ang in ((t1, 140), (t2, -40)):
            if t > a + 1.2:
                for i in range(2):
                    ph = ((t - a - 1.2) * 0.9 + i * 0.5) % 1.0
                    ripple(p, tx, ty, ph, YEL, 24, 100, 6)
        finger(p, (t1[0] - 260 * (1 - come), t1[1] + 220 * (1 - come)), ang=140, length=260, width=108)
        finger(p, (t2[0] + 260 * (1 - come), t2[1] - 220 * (1 - come)), ang=-40, length=260, width=108)
    pill(p, 540, 395, "2 FINGERS, 2 SPOTS", prog(t, a + 1.4, a + 1.8) * (1 - prog(t, a + 3.4, a + 3.6)), bg=YEL, size=38)
    pill(p, 540, 395, "PINCH TO ZOOM", prog(t, a + 3.7, a + 4.1), bg=GREEN, size=40)

@V.scene(7)
def rain(p, t, L):
    a, e = L(7)
    scr = phone(p, [255, 400, 825, 1140])
    hot = {}
    hits = [(0.6, 4), (1.3, 1), (1.9, 7), (2.6, 3), (3.4, 9), (4.1, 5), (4.8, 10), (5.4, 0)]
    pts_guess = None
    for th, idx in hits:
        g = prog(t, a + th, a + th + 0.15) * (1 - prog(t, a + th + 0.6, a + th + 0.9))
        if g > 0: hot[idx] = g
    pts = icons(p, scr, hot=hot)
    # falling drops: each lands on an icon, splashes, and triggers a phantom tap
    for th, idx in hits:
        if idx >= len(pts): continue
        tx, ty = pts[idx]
        u = prog(t, a + th - 0.6, a + th)
        if 0 < u < 1:
            y = lerp(320, ty, u * u)
            p.poly([(tx, y - 46), (tx - 20, y - 6), (tx + 20, y - 6)], DROP)
            p.circle(tx, y - 4, 20, fill=DROP)
        sp = prog(t, a + th, a + th + 0.7)
        if 0 < sp < 1:
            ripple(p, tx, ty, sp, DROP, 20, 90, 6)
            for s in (-1, 1):
                p.circle(tx + s * 50 * sp, ty - 30 * math.sin(sp * math.pi), 7, fill=DROP)
    pill(p, 540, 365, "PHANTOM TAPS", prog(t, a + 1.2, a + 1.6) * (1 - prog(t, a + 3.4, a + 3.6)), bg=WHITE, size=40)
    pill(p, 540, 365, "WATER CONDUCTS TOO", prog(t, a + 3.6, a + 4.0), bg=BLUE, size=40)

@V.scene(8)
def sausages(p, t, L):
    a, e = L(8)
    big_number(p, t, a, 2010, cx=540, cy=470, size=190, start=1990, dur=1.0)
    for i in range(12):   # snow
        x = 90 + (i * 83) % 880
        y = 330 + ((t * 70 + i * 97) % 820)
        sparkle(p, x, y, 8 + (i % 3) * 3, fill=WHITE)
    k = eback(prog(t, a + 0.6, a + 1.0))
    if k > 0:
        scr = phone(p, [700 - 170 * k, 860 - 270 * k, 700 + 170 * k, 860 + 270 * k])
        icons(p, scr, k=k)
    if t > a + 1.6:
        tap = 0.5 + 0.5 * math.sin((t - a - 1.6) * 5)
        tip = (640 - 40 * tap, 860 - 30 * tap)
        if tap < 0.12:
            ripple(p, 640, 860, 0.5, YEL, 20, 90, 6)
        sausage(p, tip, 215, length=330, width=88)
    pill(p, 290, 1080, "SOUTH KOREA", prog(t, a + 1.0, a + 1.4), bg=WHITE, size=36)
    pill(p, 290, 990, "SAUSAGE STYLUS", prog(t, e - 2.0, e - 1.6), bg=YEL, size=36)

@V.scene(9, 10)
def outro(p, t, L):
    a9, e9 = L(9); a10, e10 = L(10)
    ky = eback(prog(t, a9 + 0.2, a9 + 0.6))
    kn = eback(prog(t, a9 + 0.35, a9 + 0.75))
    yes_c, no_c = (330, 640), (750, 640)
    if ky > 0:
        p.rr([yes_c[0] - 150 * ky, yes_c[1] - 90 * ky, yes_c[0] + 150 * ky, yes_c[1] + 90 * ky], 44, fill=GREEN, shadow=True)
        p.text(yes_c, "YES", f2("anton", max(8, int(110 * ky))), INK)
    if kn > 0:
        p.rr([no_c[0] - 150 * kn, no_c[1] - 90 * kn, no_c[0] + 150 * kn, no_c[1] + 90 * kn], 44, fill=RED, shadow=True)
        p.text(no_c, "NO", f2("anton", max(8, int(110 * kn))), WHITE)
    # a finger hovers between the two, undecided, then goes to the follow button
    if t > a9 + 0.6:
        sw = 0.5 + 0.5 * math.sin((t - a9 - 0.6) * 2.4)
        hx = lerp(yes_c[0] + 40, no_c[0] - 40, sw); hy = 760
        go = eio(prog(t, a10 - 0.1, a10 + 0.7))
        bx, by = 540, 980
        tip = (lerp(hx, bx + 20, go), lerp(hy, by + 20, go))
        if t > a10 + 0.2:
            r = 62 * eback(prog(t, a10 + 0.2, a10 + 0.6))
            plus_button(p, bx, by, r)
            ripple(p, bx, by, prog(t, a10 + 0.7, a10 + 1.4), YEL, 60, 150, 8)
        finger(p, tip, ang=60, length=340, width=112)
    pill(p, 540, 420, "COMMENT", prog(t, e9 - 1.6, e9 - 1.2), bg=YEL, size=44)

@V.sounds
def cues(L):
    a2, e2 = L(2); a7, _ = L(7); a10, _ = L(10)
    d = e2 - a2
    out = [(1.2, "pop"), (a2 + d * 0.40, "ding"), (a2 + d * 0.72, "thud"), (a2 + d * 0.97, "thud")]
    out += [(a7 + th, "pop") for th in (0.6, 1.9, 3.4, 4.8)]
    out += [(a10 + 0.7, "pop")]
    return out

if __name__ == "__main__":
    V.main()
