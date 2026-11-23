import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "uk-plug-full", episode=1,
    lines=[
        "The British plug is big, bulky... and secretly genius.",
        "That top pin is longer for a reason. It's the earth pin, so it connects first, and disconnects last.",
        "It also pushes open the shutters that cover the other two holes.",
        "So poking something into one of those holes on its own gets you nowhere.",
        "And because the three pins form a triangle, it only goes in one way round.",
        "Since nineteen eighty-four, the two power pins have been half covered in plastic, so you can't touch live metal while the plug is half out.",
        "Every plug also has its own fuse, because British wall circuits can deliver more current than a thin appliance cable can handle.",
        "So if something goes wrong, the fuse blows first, and the cable is protected.",
        "Small gadgets usually get a three amp fuse, and the big stuff, like kettles, gets thirteen.",
        "Even the cable is clever. It always leaves from the bottom, which discourages anyone from yanking the plug out by the wire. And inside, a grip clamps the cable, so a tug doesn't rip the wires loose.",
        "Most of this was designed back in nineteen forty-seven.",
        "So next time you step on one barefoot, at least you know why it's built like a tank. Follow for more everyday genius.",
    ],
    display=[
        "The British plug is big, bulky... and secretly *genius*.",
        "That top pin is *longer* for a reason. It's the *earth* pin, so it connects *first*, and disconnects *last*.",
        "It also pushes open the *shutters* that cover the other two holes.",
        "So poking something into one of those holes on its own gets you *nowhere*.",
        "And because the three pins form a *triangle*, it only goes in *one* way round.",
        "Since *1984*, the two power pins have been half covered in *plastic*, so you can't touch *live* metal while the plug is half out.",
        "Every plug also has its own *fuse*, because British wall circuits can deliver more current than a *thin* appliance cable can handle.",
        "So if something goes wrong, the fuse *blows* first, and the cable is *protected*.",
        "Small gadgets usually get a *3 amp* fuse, and the big stuff, like kettles, gets *13*.",
        "Even the *cable* is clever. It always leaves from the *bottom*, which discourages anyone from yanking the plug out by the wire. And inside, a grip clamps the cable, so a tug doesn't rip the wires loose.",
        "Most of this was designed back in *1947*.",
        "So next time you step on one *barefoot*, at least you know why it's built like a *tank*. Follow for more everyday *genius*.",
    ],
)

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

@V.scene(1, 3)
def earth_and_shutters(p, t, L):
    a1, e1 = L(1); a2, e2 = L(2); a3, _ = L(3)
    px = 140
    px = lerp(px, 430, eio(prog(t, a1 + 0.2, a1 + 2.4)))       # earth tip reaches the socket face
    px = lerp(px, 480, eio(prog(t, a1 + 2.8, a1 + 3.6)))        # earth goes in first
    px = lerp(px, 625, eio(prog(t, a2 + 0.9, a2 + 2.3)))        # all the way in after shutters open
    px = lerp(px, -260, eio(prog(t, a3 - 0.2, a3 + 0.8)))       # out of frame
    drop = 150 * eio(prog(t, a2 + 0.2, a2 + 0.8)) * (1 - eio(prog(t, a3 + 0.6, a3 + 1.0)))
    socket_block(p, drop)
    side_plug(p, px, glow=prog(t, a1 + 1.6, a1 + 2.0) * (1 - prog(t, a2 - 0.2, a2 + 0.2)))
    pill(p, 300, 380, "EARTH: FIRST IN, LAST OUT", prog(t, a1 + 2.2, a1 + 2.6) * (1 - prog(t, a2 - 0.3, a2)))
    pill(p, 800, 1110, "SHUTTERS OPEN", prog(t, a2 + 0.6, a2 + 1.0) * (1 - prog(t, a3 - 0.4, a3 - 0.1)), bg=ORANGE)
    if t > a3 + 1.0:
        tip = lerp(120, 660, eio(prog(t, a3 + 1.1, a3 + 1.9)))
        p.line([(tip - 420, 825), (tip, 825)], fill=(200, 205, 215), width=10)
        cross(p, 520, 650, 70, prog(t, a3 + 1.9, a3 + 2.1), shake_t=t - (a3 + 1.9))
        pill(p, 520, 1110, "BLOCKED", prog(t, a3 + 1.95, a3 + 2.3), bg=RED, fg=WHITE)

def plug_face_flipped(p, cx, cy, sc=1.0):
    w, h = 400 * sc, 460 * sc
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 60 * sc, fill=WHITE, outline=EDGE, width=6 * sc)
    ew, eh, ey = 46 * sc, 120 * sc, cy + 95 * sc
    p.rr([cx - ew / 2, ey - eh / 2, cx + ew / 2, ey + eh / 2], 6 * sc, fill=BRASS, outline=BRASS_D, width=4 * sc)
    for dx in (-90, 90):
        x, y = cx + dx * sc, cy - 95 * sc
        p.rr([x - 60 * sc, y - 22 * sc, x + 60 * sc, y + 22 * sc], 6 * sc, fill=BRASS, outline=BRASS_D, width=4 * sc)

def socket_face(p, cx, cy, sc=1.0):
    w = 440 * sc
    p.rr([cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2], 40 * sc, fill=(236, 238, 240), outline=EDGE, width=6 * sc)
    p.rr([cx - 26 * sc, cy - 160 * sc, cx + 26 * sc, cy - 40 * sc], 6 * sc, fill=INK)
    for dx in (-90, 90):
        p.rr([cx + dx * sc - 62 * sc, cy + 70 * sc, cx + dx * sc + 62 * sc, cy + 118 * sc], 6 * sc, fill=INK)

@V.scene(4)
def one_way(p, t, L):
    a, _ = L(4)
    k = eback(prog(t, a, a + 0.5))
    socket_face(p, 540, 560, 0.9 * k if k > 0 else 0.01)
    p1 = eback(prog(t, a + 0.8, a + 1.3))
    if p1 > 0:
        plug_face_flipped(p, 290, 940, 0.45 * p1)
        cross(p, 290, 940, 70, prog(t, a + 1.4, a + 1.6), shake_t=t - (a + 1.4))
    p2 = eback(prog(t, a + 1.8, a + 2.3))
    if p2 > 0:
        plug_face(p, 790, 940, 0.45 * p2)
        tick(p, 790, 1080, 46, prog(t, a + 2.4, a + 2.7))

@V.scene(8)
def ratings(p, t, L):
    a, _ = L(8)
    for i, (amp, label, x, t0) in enumerate([("3A", "LAMPS, CHARGERS", 300, a + 0.3), ("13A", "KETTLES, HEATERS", 780, a + 2.6)]):
        k = eback(prog(t, t0, t0 + 0.5))
        if k <= 0: continue
        h = 420 * k
        p.rr([x - 90, 700 - h / 2, x + 90, 700 + h / 2], 60, fill=(250, 250, 248), outline=EDGE, width=6)
        p.rr([x - 90, 700 - h / 2, x + 90, 700 - h / 2 + 70 * k], 30, fill=(185, 190, 198))
        p.rr([x - 90, 700 + h / 2 - 70 * k, x + 90, 700 + h / 2], 30, fill=(185, 190, 198))
        p.text((x, 700), amp, f2("anton", max(10, int(110 * k))), INK)
        pill(p, x, 1000, label, prog(t, t0 + 0.4, t0 + 0.8), bg=WHITE, size=34)

@V.scene(5)
def sleeves(p, t, L):
    a, _ = L(5)
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

@V.scene(6, 7)
def fuse(p, t, L):
    a5, _ = L(6); a6, _ = L(7)
    over, blown = t > a6 + 0.6, t > a6 + 1.9
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
        flow_dots(p, PATH, t - a5, speed=1.6 if over else 0.35, fill=RED if over else YEL)
    else:
        p.line([(430, 760), (520, 760), (530, 748)], fill=(90, 90, 98), width=6)
        p.line([(560, 772), (570, 760), (650, 760)], fill=(90, 90, 98), width=6)
    flash = prog(t, a6 + 1.85, a6 + 1.9) * (1 - prog(t, a6 + 1.95, a6 + 2.35))
    if flash > 0: p.circle(545, 760, 160 * flash, fill=(255, 245, 200))
    pill(p, 540, 670, "FUSE IN EVERY PLUG", prog(t, a5 + 0.6, a5 + 1.0) * (1 - prog(t, a6 + 1.7, a6 + 1.85)))
    pill(p, 540, 330, "THIN CABLE", prog(t, a5 + 3.2, a5 + 3.6) * (1 - prog(t, a6 + 0.4, a6 + 0.6)), bg=WHITE)
    pill(p, 540, 330, "TOO MUCH CURRENT", prog(t, a6 + 0.6, a6 + 0.9) * (1 - prog(t, a6 + 1.8, a6 + 1.9)), bg=RED, fg=WHITE)
    pill(p, 540, 330, "CABLE PROTECTED", prog(t, a6 + 2.4, a6 + 2.8), bg=GREEN)

@V.scene(9)
def cable(p, t, L):
    a, _ = L(9)
    # wall on the right, plug sticking out of it, cable leaving from the bottom
    p.rect([820, 330, 1080, 1150], fill=SLATE)
    p.rect([820, 330, 840, 1150], fill=SLATE_L)
    tug = 40 * eio(prog(t, a + 2.6, a + 3.4)) * (1 - eio(prog(t, a + 4.4, a + 5.0)))
    p.rr([520, 460, 820, 840], 40, fill=WHITE, outline=EDGE, width=6)
    p.line([(670, 830), (670, 900 + tug), (560, 975 + tug), (300, 1005 + tug)], fill=DARK, width=34)
    pill(p, 670, 400, "CABLE EXITS AT THE BOTTOM", prog(t, a + 1.6, a + 2.0))
    if t > a + 2.6:
        p.arrow((380, 920), (380, 1040), RED, width=14, head=40)
    tick(p, 670, 650, 70, prog(t, a + 4.0, a + 4.4))
    pill(p, 670, 1100, "PLUG STAYS PUT", prog(t, a + 4.2, a + 4.6) * (1 - prog(t, a + 6.2, a + 6.5)), bg=GREEN)
    g = eback(prog(t, a + 6.6, a + 7.1))
    if g > 0:
        p.rr([600, 790, 740, 820], 10, fill=ORANGE)
        p.circle(615, 805, 9 * g, fill=INK); p.circle(725, 805, 9 * g, fill=INK)
        pill(p, 670, 1100, "CABLE GRIP", prog(t, a + 6.7, a + 7.1), bg=ORANGE)

@V.scene(10, 11)
def outro(p, t, L):
    a8, _ = L(10); a9, _ = L(11)
    if t < a9:
        big_number(p, t, a8, 1947, start=1900, dur=1.2)
        if t > a8: p.text((540, 840), "BS 1363  ·  STILL IN USE TODAY", f2("dm", 38), MUTED)
    else:
        # plug lying on the floor, pins pointing up
        k = eback(prog(t, a9, a9 + 0.5))
        y = lerp(1300, 760, k)
        p.rect([100, 900, 980, 912], fill=SLATE_L)
        p.rr([340, y, 740, y + 140], 30, fill=WHITE, outline=EDGE, width=6)
        p.rr([516, y - 150, 564, y], 6, fill=BRASS, outline=BRASS_D, width=4)
        for x in (420, 660):
            p.rr([x - 22, y - 110, x + 22, y], 6, fill=BRASS, outline=BRASS_D, width=4)
            p.rect([x - 22, y - 50, x + 22, y], fill=DARK)
        pill(p, 540, 470, "OUCH", prog(t, a9 + 0.8, a9 + 1.2), bg=RED, fg=WHITE)
        fp = prog(t, a9 + 4.0, a9 + 4.4)
        if fp > 0:
            r = 64 * eback(fp)
            p.circle(540, 1060, r, fill=RED)
            p.line([(540 - r * .45, 1060), (540 + r * .45, 1060)], fill=WHITE, width=12)
            p.line([(540, 1060 - r * .45), (540, 1060 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
