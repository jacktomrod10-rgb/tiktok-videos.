"""Episode 7 (short): Why food tins have ridges.
    python3 -I videos/2026-11-25-tin-ridges/make.py tts | stills ... | render videos/2026-11-25-tin-ridges.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "tin-ridges", episode=7, title="Why do food *tins* have *ridges*?",
    lines=[
        "There's a reason food tins have ridges.",
        "They stop the tin crumpling. The ridges stiffen the thin metal, so a stack of tins doesn't collapse under its own weight.",
        "Food tins are also heated after they're sealed, to sterilise the food, and the ridges help the walls cope with the heat and pressure.",
        "So why are drinks cans smooth? The fizz inside pushes outwards and keeps the can stiff.",
        "Be honest. Did you think the ridges were just for grip? Tell me in the comments.",
        "Follow for more everyday genius.",
    ],
    display=[
        "There's a *reason* food tins have *ridges*.",
        "They stop the tin *crumpling*. The ridges *stiffen* the thin metal, so a *stack* of tins doesn't collapse under its own weight.",
        "Food tins are also *heated* after they're sealed, to *sterilise* the food, and the ridges help the walls cope with the heat and *pressure*.",
        "So why are *drinks* cans *smooth*? The *fizz* inside pushes outwards and keeps the can *stiff*.",
        "Be honest. Did you think the ridges were just for *grip*? Tell me in the *comments*.",
        "Follow for more everyday *genius*.",
    ],
)

STEEL, STEEL_D, STEEL_L = (186, 192, 202), (140, 147, 158), (222, 226, 232)

def tin(p, cx, cy, w, h, ridges=True, label=(214, 76, 70), crush=0.0, t=0.0):
    """Side view of a tin. crush 0..1 squashes a smooth tin into a crumpled shape."""
    hh = h * (1 - 0.35 * crush)
    top, bot = cy + h / 2 - hh, cy + h / 2
    if crush > 0.01:
        pts_l, pts_r = [], []
        n = 9
        for i in range(n + 1):
            y = top + (bot - top) * i / n
            z = (12 + 28 * crush) * (1 if i % 2 else -1) * crush
            pts_l.append((cx - w / 2 + z, y)); pts_r.append((cx + w / 2 - z, y))
        p.poly(pts_l + pts_r[::-1], STEEL)
        p.poly([(cx - w / 2 + 14, top + 40), (cx + w / 2 - 14, top + 40), (cx + w / 2 - 20, bot - 40), (cx - w / 2 + 20, bot - 40)], label)
    else:
        p.rr([cx - w / 2, top, cx + w / 2, bot], 14, fill=STEEL)
        p.rect([cx - w / 2, top + hh * 0.22, cx + w / 2, bot - hh * 0.22], fill=label)
        if ridges:
            n = 7
            for i in range(n):
                y = top + hh * (0.12 + 0.76 * i / (n - 1))
                p.line([(cx - w / 2 + 4, y - 4), (cx + w / 2 - 4, y - 4)], fill=STEEL_L, width=5)
                p.line([(cx - w / 2 + 4, y + 4), (cx + w / 2 - 4, y + 4)], fill=STEEL_D, width=5)
    p.ell([cx - w / 2, top - 22, cx + w / 2, top + 22], fill=STEEL_L, outline=STEEL_D, width=4)

def drink_can(p, cx, cy, w, h, t):
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 30, fill=(90, 170, 255))
    p.rect([cx - w / 2, cy - h / 2 + 40, cx + w / 2, cy - h / 2 + 70], fill=(200, 225, 255))
    p.ell([cx - w / 2 + 10, cy - h / 2 - 18, cx + w / 2 - 10, cy - h / 2 + 18], fill=STEEL_L, outline=STEEL_D, width=4)
    for i in range(10):
        bx = cx - w / 2 + 30 + (i * 37) % (w - 60)
        by = cy + h / 2 - 30 - ((t * 140 + i * 53) % (h - 120))
        p.circle(bx, by, 7 + (i % 3) * 3, fill=(220, 240, 255))

@V.scene(0)
def hook(p, t, L):
    k = eback(prog(t, 0.0, 0.45))
    if k <= 0: return
    tin(p, 540, 720, 300 * k, 400 * k, t=t)
    for i, (dx, dy) in enumerate(((-210, -150), (220, -120), (-190, 170), (200, 190))):
        sp = eback(prog(t, 0.9 + i * 0.12, 1.2 + i * 0.12))
        if sp > 0:
            sparkle(p, 540 + dx, 720 + dy, 26 * sp)
    if t > 1.2:
        for i in range(3):
            y = 600 + i * 95
            p.arrow((790, y), (705, y), YEL, width=8, head=24)
        pill(p, 540, 395, "THE RIDGES", prog(t, 1.2, 1.5), size=46)

@V.scene(1)
def stacking(p, t, L):
    a, e = L(1)
    # left: smooth tin under a weight crumples; right: a stack of ridged tins holds
    drop = eio(prog(t, a + 1.0, a + 1.8))
    crush = eo(prog(t, a + 1.7, a + 2.3))
    tin(p, 270, 870, 210, 300, ridges=False, crush=crush)
    tin_top = 1020 - 300 * (1 - 0.35 * crush)
    wy = lerp(420, tin_top - 64, drop)
    p.rr([170, wy - 60, 370, wy + 40], 18, fill=SLATE_L)
    p.text((270, wy - 8), "WEIGHT", f2("dm", 34), WHITE)
    cross(p, 270, 1090, 40, prog(t, a + 2.3, a + 2.5), shake_t=t - (a + 2.3))
    # stack of ridged tins (pyramid of 3 rows) builds up
    spots = [(650, 1000), (790, 1000), (930, 1000), (720, 790), (860, 790), (790, 580)]
    for i, (x, y) in enumerate(spots):
        kk = eback(prog(t, a + 3.0 + i * 0.25, a + 3.3 + i * 0.25))
        if kk > 0:
            tin(p, x, y + (1 - kk) * -80, 130, 190, ridges=True)
    tick(p, 930, 560, 46, prog(t, a + 4.8, a + 5.1))
    pill(p, 270, 395, "SMOOTH", prog(t, a + 0.3, a + 0.6), bg=WHITE, size=40)
    pill(p, 790, 395, "RIDGED", prog(t, a + 3.0, a + 3.3), bg=GREEN, size=40)

@V.scene(2)
def cooking(p, t, L):
    a, e = L(2)
    # tin sitting in a steaming pot, walls flexing
    p.rr([220, 760, 860, 1100], 40, fill=(70, 84, 104))
    p.rect([200, 740, 880, 790], fill=(96, 112, 136))
    flex = math.sin((t - a) * 5) * 10 * prog(t, a + 1.5, a + 2.0)
    tin(p, 540, 720, 260 + flex, 380, ridges=True, label=(70, 160, 90))
    for i, x in enumerate((260, 340, 740, 820, 300)):
        u = ((t - a) * 0.8 + i * 0.23) % 1.0
        y = 720 - u * 300
        p.circle(x, y, 22 * (1 - u) + 6, fill=(220, 228, 238))
    for i in range(4):   # flames
        fx = 300 + i * 160
        fh = 50 + 15 * math.sin(t * 9 + i)
        p.poly([(fx - 30, 1140), (fx, 1140 - fh), (fx + 30, 1140)], ORANGE)
    pill(p, 540, 395, "HEATED AFTER SEALING", prog(t, a + 0.4, a + 0.8) * (1 - prog(t, a + 4.0, a + 4.3)), bg=ORANGE, size=40)
    pill(p, 540, 395, "RIDGES COPE WITH THE PRESSURE", prog(t, a + 4.3, a + 4.7), bg=YEL, size=38)

@V.scene(3)
def drinks(p, t, L):
    a, e = L(3)
    k = eback(prog(t, a, a + 0.4))
    if k <= 0: return
    drink_can(p, 540, 740, 280 * k, 470 * k, t)
    if t > a + 2.4:
        u = eo(prog(t, a + 2.4, a + 3.0))
        for ang in range(0, 360, 45):
            r0, r1 = 170, 170 + 90 * u
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            p.arrow((540 + r0 * c, 740 + r0 * s * 1.4), (540 + r1 * c, 740 + r1 * s * 1.4), YEL, width=9, head=26)
    pill(p, 540, 395, "NO RIDGES", prog(t, a + 0.5, a + 0.8) * (1 - prog(t, a + 2.2, a + 2.4)), bg=WHITE, size=44)
    pill(p, 540, 395, "FIZZ PUSHES OUT", prog(t, a + 2.5, a + 2.8), bg=YEL, size=44)

@V.scene(4, 5)
def outro(p, t, L):
    a4, _ = L(4); a5, _ = L(5)
    k = eback(prog(t, a4, a4 + 0.4))
    if k > 0:
        tin(p, 360, 720, 220 * k, 320 * k)
        # a hand-ish grip outline that gets a question mark
        p.text((720, 700), "?", f2("anton", max(8, int(260 * k))), YEL)
    pill(p, 540, 395, "JUST FOR GRIP?", prog(t, a4 + 1.2, a4 + 1.5), bg=WHITE, size=44)
    if t > a4 + 3.0:
        bp = eback(prog(t, a4 + 3.0, a4 + 3.4))
        bx, by = 400, 1020
        p.rr([bx - 110 * bp, by - 52 * bp, bx + 110 * bp, by + 52 * bp], 28 * bp, fill=WHITE)
        p.poly([(bx - 40 * bp, by + 48 * bp), (bx - 70 * bp, by + 90 * bp), (bx - 6 * bp, by + 48 * bp)], fill=WHITE)
        for i in range(3):
            d = 10 * bp * (1 + 0.35 * pulse(t - i * 0.2, 0.9))
            p.circle(bx - 50 * bp + i * 50 * bp, by, d, fill=INK)
    fp = prog(t, a5 + 0.1, a5 + 0.5)
    if fp > 0:
        r = 56 * eback(fp)
        p.circle(720, 1030, r, fill=RED)
        p.line([(720 - r * .45, 1030), (720 + r * .45, 1030)], fill=WHITE, width=12)
        p.line([(720, 1030 - r * .45), (720, 1030 + r * .45)], fill=WHITE, width=12)

@V.sounds
def cues(L):
    a1, _ = L(1)
    return [(1.0, "ding"), (a1 + 1.8, "thud"), (a1 + 4.8, "ding")]

if __name__ == "__main__":
    V.main()
