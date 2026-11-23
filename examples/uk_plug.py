"""Example episode: 'The UK plug is secretly genius' (33 s test version).
Run from the repo root:
    python3 -I examples/uk_plug.py tts
    python3 -I examples/uk_plug.py stills 2.8 7.6 13.2 20.0 24.5 30.6
    python3 -I examples/uk_plug.py render
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from studio.kit import *

V = Video(
    "uk-plug", episode=1,
    lines=[
        "The British plug is big, bulky... and secretly genius.",
        "That top pin is longer for a reason. It's the earth pin, and it goes in first, pushing open the shutters that cover the other two holes.",
        "So poking something into one of those holes on its own gets you nowhere.",
        "Since nineteen eighty-four, the two power pins have been half covered in plastic, so you can't touch live metal while the plug is half out.",
        "And every plug has its own fuse. If too much current flows, the fuse blows, and the cable is protected.",
        "All of this was designed back in nineteen forty-seven. Follow for more everyday genius.",
    ],
    display=[
        "The British plug is big, bulky... and secretly *genius*.",
        "That top pin is *longer* for a reason. It's the *earth* pin, and it goes in *first*, pushing open the *shutters* that cover the other two holes.",
        "So poking something into one of those holes on its own gets you *nowhere*.",
        "Since *1984*, the two power pins have been half covered in *plastic*, so you can't touch *live* metal while the plug is half out.",
        "And every plug has its own *fuse*. If too much current flows, the fuse *blows*, and the cable is *protected*.",
        "All of this was designed back in *1947*. Follow for more everyday *genius*.",
    ],
)

# ---- drawings specific to this episode ----
def plug_face(p, cx, cy, sc=1.0):
    w, h = 400 * sc, 460 * sc
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 60 * sc, fill=WHITE, outline=EDGE, width=6 * sc)
    ew, eh, ey = 46 * sc, 120 * sc, cy - 95 * sc
    p.rr([cx - ew / 2, ey - eh / 2, cx + ew / 2, ey + eh / 2], 6 * sc, fill=BRASS, outline=BRASS_D, width=4 * sc)
    for dx in (-90, 90):
        x, y = cx + dx * sc, cy + 95 * sc
        p.rr([x - 60 * sc, y - 22 * sc, x + 60 * sc, y + 22 * sc], 6 * sc, fill=BRASS, outline=BRASS_D, width=4 * sc)
    p.rr([cx - 40 * sc, cy + h / 2 - 4 * sc, cx + 40 * sc, cy + h / 2 + 90 * sc], 16 * sc, fill=DARK)

def side_plug(p, px, glow=0.0):
    p.rr([px - 300, 470, px, 990], 40, fill=WHITE, outline=EDGE, width=6)
    p.rr([px - 380, 690, px - 290, 770], 20, fill=DARK)
    if glow > 0:
        g = int(10 * glow)
        p.rr([px - g, 548 - g, px + 210 + g, 612 + g], 12, fill=(255, 220, 120))
    p.rr([px, 550, px + 210, 610], 8, fill=BRASS, outline=BRASS_D, width=4)
    p.rr([px, 800, px + 150, 850], 8, fill=BRASS, outline=BRASS_D, width=4)
    p.rect([px, 800, px + 70, 850], fill=DARK)

def socket_block(p, drop):
    x0 = 640
    p.rr([x0, 430, 1010, 1050], 24, fill=SLATE)
    p.rect([x0, 430, x0 + 26, 1050], fill=SLATE_L)
    p.rect([x0, 540, 1010, 620], fill=(20, 27, 38))
    p.rect([x0 + 40, 790, 1010, 860], fill=(20, 27, 38))
    p.rr([x0 + 26, 770 + drop, x0 + 46, 880 + drop], 6, fill=ORANGE)

# ---- scenes ----
@V.scene(0)
def intro(p, t, L):
    k = eback(prog(t, 0.05, 0.6)); bob = math.sin(t * 2.2) * 8; sc = lerp(0.55, 1.0, k)
    p.circle(540, 720 + bob, 300 * sc, fill=(36, 62, 98))
    plug_face(p, 540, 700 + bob, sc)
    sp = prog(t, 2.0, 2.6)
    if sp > 0:
        for ang, rr in [(-40, 330), (210, 320), (20, 345), (160, 335)]:
            a = math.radians(ang)
            sparkle(p, 540 + math.cos(a) * rr, 700 + math.sin(a) * rr + bob, 26 * eback(sp))

@V.scene(1, 2)
def earth_and_shutters(p, t, L):
    a, _ = L(1); c, _ = L(2)
    px = 140
    px = lerp(px, 430, eio(prog(t, a + 0.1, a + 2.2)))
    px = lerp(px, 480, eio(prog(t, a + 2.6, a + 3.4)))
    px = lerp(px, 625, eio(prog(t, a + 4.2, a + 5.6)))
    px = lerp(px, -260, eio(prog(t, c - 0.2, c + 0.8)))
    drop = 150 * eio(prog(t, a + 2.9, a + 3.5)) * (1 - eio(prog(t, c + 0.6, c + 1.0)))
    socket_block(p, drop)
    side_plug(p, px, glow=prog(t, a + 1.6, a + 2.0) * (1 - prog(t, a + 4.0, a + 4.4)))
    pill(p, 300, 380, "EARTH PIN: LONGER", prog(t, a + 1.7, a + 2.1) * (1 - prog(t, c - 0.4, c - 0.1)))
    pill(p, 800, 1110, "SHUTTERS OPEN", prog(t, a + 3.3, a + 3.7) * (1 - prog(t, c - 0.4, c - 0.1)), bg=ORANGE)
    if t > c + 1.0:
        tip = lerp(120, 660, eio(prog(t, c + 1.1, c + 1.9)))
        p.line([(tip - 420, 825), (tip, 825)], fill=(200, 205, 215), width=10)
        cross(p, 520, 650, 70, prog(t, c + 1.9, c + 2.1), shake_t=t - (c + 1.9))
        pill(p, 520, 1110, "BLOCKED", prog(t, c + 1.95, c + 2.3), bg=RED, fg=WHITE)

@V.scene(3)
def sleeves(p, t, L):
    a, _ = L(3)
    sock_x = lerp(1200, 520, eio(prog(t, a + 4.0, a + 4.9)))
    p.rr([60, 470, 260, 1050], 36, fill=WHITE, outline=EDGE, width=6)
    p.rr([260, 690, 960, 830], 14, fill=BRASS, outline=BRASS_D, width=6)
    sl = eo(prog(t, a + 0.9, a + 1.8))
    if sl > 0: p.rect([260, 686, 260 + 260 * sl, 834], fill=DARK)
    if sock_x < 1090:
        p.rect([sock_x, 560, 1100, 960], fill=SLATE)
        p.rect([sock_x, 560, sock_x + 24, 960], fill=SLATE_L)
    pill(p, 470, 600, "INSULATED SLEEVE", prog(t, a + 1.6, a + 2.0))
    pill(p, 470, 905, "SINCE 1984", prog(t, a + 0.3, a + 0.7), bg=WHITE)
    tick(p, 400, 1035, 56, prog(t, a + 5.0, a + 5.4))

PATH = [(540, 1120), (540, 940), (760, 940), (760, 760), (700, 760), (430, 760), (380, 760), (320, 760), (320, 560), (420, 560)]

@V.scene(4)
def fuse(p, t, L):
    a, _ = L(4)
    over, blown = t > a + 2.0, t > a + 3.75
    p.rr([200, 400, 880, 1080], 70, fill=(232, 234, 236), outline=EDGE, width=8)
    p.rr([240, 440, 840, 1040], 50, fill=(208, 212, 218))
    p.rr([500, 1060, 580, 1130], 18, fill=DARK)
    p.line(PATH[:5], fill=(150, 90, 60), width=14)
    p.line(PATH[6:], fill=(150, 90, 60), width=14)
    p.rr([420, 520, 560, 600], 10, fill=BRASS, outline=BRASS_D, width=4)
    p.rr([380, 720, 700, 800], 36, fill=(250, 250, 248), outline=EDGE, width=4)
    p.rr([380, 720, 430, 800], 14, fill=(185, 190, 198))
    p.rr([650, 720, 700, 800], 14, fill=(185, 190, 198))
    if not blown:
        p.line([(430, 760), (650, 760)], fill=(120, 120, 128), width=6)
        flow_dots(p, PATH, t - a, speed=1.6 if over else 0.35, fill=RED if over else YEL)
    else:
        p.line([(430, 760), (520, 760), (530, 748)], fill=(90, 90, 98), width=6)
        p.line([(560, 772), (570, 760), (650, 760)], fill=(90, 90, 98), width=6)
    flash = prog(t, a + 3.7, a + 3.75) * (1 - prog(t, a + 3.8, a + 4.2))
    if flash > 0: p.circle(545, 760, 160 * flash, fill=(255, 245, 200))
    pill(p, 540, 670, "13A FUSE", prog(t, a + 0.4, a + 0.8) * (1 - prog(t, a + 3.6, a + 3.7)))
    pill(p, 540, 330, "TOO MUCH CURRENT", prog(t, a + 2.0, a + 2.3) * (1 - prog(t, a + 3.6, a + 3.7)), bg=RED, fg=WHITE)
    pill(p, 540, 330, "CABLE PROTECTED", prog(t, a + 4.3, a + 4.7), bg=GREEN)

@V.scene(5)
def outro(p, t, L):
    a, _ = L(5)
    big_number(p, t, a, 1947, start=1900, dur=1.2)
    if t > a: p.text((540, 840), "BS 1363  ·  STILL IN USE TODAY", f2("dm", 38), MUTED)
    fp = prog(t, a + 2.3, a + 2.7)
    if fp > 0:
        r = 64 * eback(fp)
        p.circle(540, 1030, r, fill=RED)
        p.line([(540 - r * .45, 1030), (540 + r * .45, 1030)], fill=WHITE, width=12)
        p.line([(540, 1030 - r * .45), (540, 1030 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
