"""Test format: 'In this town, everyone goes on holiday... except us' (The Pennys). ~45 s."""
import os, sys, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

SCRIPT = [
    ("dave", "In this town, everyone goes on holiday.", "In this town, *everyone* goes on *holiday*."),
    ("dave", "Except us.", "*Except* us."),
    ("dave", "Next door went to Spain. Twice.", "Next door went to *Spain*. *Twice*."),
    ("dave", "Gary from work went to Florida, and came back orange.", "*Gary* from work went to *Florida*, and came back *orange*."),
    ("dave", "The Hendersons went skiing. Even their dog went skiing.", "The Hendersons went *skiing*. Even their *dog* went skiing."),
    ("dave", "My mum went on a cruise. She's eighty-four.", "My *mum* went on a *cruise*. She's *84*."),
    ("dave", "But not us.", "But *not* us."),
    ("sue", "We've got thirty days to save a thousand pounds.", "We've got *30 days* to save *£1,000*."),
    ("dave", "So. Day by day.", "So. *Day* by *day*."),
    ("alfie", "Kangaroos, here we come!", "*Kangaroos*, here we *come!*"),
    ("dave", "Where did you go on holiday this year? Go on. Rub it in, in the comments.", "Where did *you* go on holiday this year? Go on. *Rub it in*, in the *comments*."),
    ("narrator", "This is the Pennys. Thirty days, one thousand pounds, and you decide what they do. Follow, to watch them try.", "This is *The Pennys*. 30 days, *£1,000*, and *you* decide what they do. *Follow*, to watch them try."),
]
MONTAGE = 6.4     # seconds of music-only "day by day" montage after line 8

V = Video(
    "test-in-this-town", episode=None, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS, title="Everyone goes on *holiday*… except *us*",
    lines=[(sp, txt) for sp, txt, _ in SCRIPT], display=[cap for _, _, cap in SCRIPT], holds={8: MONTAGE},
)

SKY, SKY2 = (120, 190, 240), (175, 220, 250)
GRASS, PAVE = (110, 180, 100), (170, 170, 176)
OUT = P.OUT

def plane(p, x, y, s=1.0, ang=-0.35):
    ca, sa = math.cos(ang), math.sin(ang)
    def r(dx, dy): return (x + (dx * ca - dy * sa) * s, y + (dx * sa + dy * ca) * s)
    p.poly([r(-60, -10), r(55, -10), r(70, 0), r(55, 10), r(-60, 10)], WHITE)
    p.poly([r(-10, 0), r(20, 0), r(-20, 45), r(-35, 45)], (220, 226, 236))
    p.poly([r(-10, 0), r(20, 0), r(-20, -45), r(-35, -45)], (200, 206, 216))
    p.poly([r(-60, -8), r(-45, -8), r(-58, -32), r(-66, -32)], RED)

def house(p, cx, base, w, h, wall, roof, t, shabby=False):
    P.orr(p, [cx - w / 2, base - h, cx + w / 2, base], 6, wall)
    p.poly([(cx - w / 2 - 22, base - h + 4), (cx, base - h - w * 0.45), (cx + w / 2 + 22, base - h + 4)], OUT)
    p.poly([(cx - w / 2 - 12, base - h), (cx, base - h - w * 0.45 + 10), (cx + w / 2 + 12, base - h)], roof)
    p.rr([cx - 26, base - 96, cx + 26, base], 6, fill=OUT)
    p.rr([cx - 20, base - 90, cx + 20, base], 4, fill=shade_(roof))
    for sx in (-1, 1):
        wx = cx + sx * w * 0.28
        p.rr([wx - 30, base - h + 40, wx + 30, base - h + 100], 6, fill=OUT)
        p.rect([wx - 24, base - h + 46, wx + 24, base - h + 94], fill=(255, 236, 170) if not shabby else (150, 170, 190))
    if shabby:
        p.line([(cx - w / 2 + 20, base - h + 130), (cx - w / 2 + 70, base - h + 160)], OUT, 5)   # crack

def shade_(c, k=0.75):
    return tuple(int(v * k) for v in c)

def cloud(p, x, y, s=1.0, col=(150, 156, 170)):
    for dx, dy, r in [(-60, 10, 50), (0, -15, 65), (60, 10, 50), (0, 20, 50)]:
        p.circle(x + dx * s, y + dy * s, r * s, fill=col)

def sky_bg(p, top=(120, 190, 240), bot=(190, 228, 250)):
    for i in range(12):
        c = tuple(int(top[j] + (bot[j] - top[j]) * i / 11) for j in range(3))
        p.rect([0, 300 + i * 72, 1080, 300 + (i + 1) * 72], fill=c)

def postcard(p, t, t0, kind, title, cx=540, cy=640):
    k = eback(prog(t, t0, t0 + 0.45))
    if k <= 0: return
    w, h = 780 * k, 620 * k
    tilt = 0
    p.rr([cx - w / 2 + 10, cy - h / 2 + 16 + tilt, cx + w / 2 + 10, cy + h / 2 + 16 - tilt], 24, fill=(16, 24, 40))
    p.rr([cx - w / 2, cy - h / 2 + tilt, cx + w / 2, cy + h / 2 - tilt], 24, fill=WHITE)
    if k < 0.95: return
    x0, y0, x1, y1 = cx - 350, cy - 270, cx + 350, cy + 170
    if kind == "spain":
        p.rect([x0, y0, x1, y1], fill=(110, 190, 245))
        p.rect([x0, y0 + 250, x1, y1], fill=(60, 150, 220))
        for i in range(6):
            yy = y0 + 270 + i * 14
            p.line([(x0 + ((t * 60 + i * 50) % 120) + j * 120, yy) for j in range(0, 6)], (140, 200, 245), 3)
        p.rect([x0, y0 + 340, x1, y1], fill=(240, 214, 150))
        p.circle(x1 - 110, y0 + 90, 56 + 4 * pulse(t, 1.4), fill=YEL)
        p.line([(x0 + 200, y1 - 10), (x0 + 240, y0 + 230)], OUT, 8)
        p.poly([(x0 + 120, y0 + 250), (x0 + 240, y0 + 180), (x0 + 340, y0 + 270)], RED)
        p.poly([(x0 + 180, y0 + 230), (x0 + 240, y0 + 180), (x0 + 290, y0 + 240)], WHITE)
    elif kind == "florida":
        p.rect([x0, y0, x1, y1], fill=(255, 170, 120))
        p.rect([x0, y0 + 280, x1, y1], fill=(240, 214, 150))
        p.circle(x0 + 520, y0 + 150, 90, fill=(255, 220, 120))
        tx, ty = x0 + 160, y1
        for i in range(10):
            p.circle(tx + i * 6, ty - i * 32, 16, fill=(150, 100, 60))
        for ang in (-150, -110, -70, -30, 10):
            a = math.radians(ang + 6 * math.sin(t * 2))
            p.line([(tx + 54, ty - 300), (tx + 54 + 150 * math.cos(a), ty - 300 + 90 * math.sin(a) + 60)], (60, 150, 80), 22)
    elif kind == "ski":
        p.rect([x0, y0, x1, y1], fill=(150, 200, 245))
        p.poly([(x0, y1 - 80), (x0 + 220, y0 + 80), (x0 + 430, y1 - 80)], (235, 240, 250))
        p.poly([(x0 + 260, y1 - 80), (x0 + 520, y0 + 40), (x1, y1 - 80)], (220, 230, 245))
        p.poly([(x0 + 175, y0 + 140), (x0 + 220, y0 + 80), (x0 + 265, y0 + 140)], WHITE)
        p.rect([x0, y1 - 90, x1, y1], fill=WHITE)
        for i in range(30):
            sx_ = x0 + (i * 97 + t * 40) % 700
            sy_ = y0 + (i * 53 + t * 120) % 440
            p.circle(sx_, sy_, 5, fill=WHITE)
    elif kind == "cruise":
        p.rect([x0, y0, x1, y1], fill=(130, 200, 250))
        p.rect([x0, y0 + 300, x1, y1], fill=(40, 110, 190))
        bob = 6 * math.sin(t * 2.2)
        bx, by = cx - 20, y0 + 300 + bob
        p.poly([(bx - 260, by - 40), (bx + 260, by - 40), (bx + 210, by + 40), (bx - 220, by + 40)], (30, 40, 70))
        p.rect([bx - 220, by - 52, bx + 240, by - 40], fill=RED)
        for i, (dw, c) in enumerate([(220, WHITE), (180, (235, 238, 245)), (130, WHITE)]):
            p.rr([bx - dw, by - 100 - i * 50, bx + dw - 20, by - 50 - i * 50], 10, fill=c)
            for j in range(-dw + 30, dw - 30, 44):
                p.circle(bx + j, by - 75 - i * 50, 8, fill=(90, 150, 210))
        for fx in (bx - 40, bx + 50):
            p.rr([fx - 22, by - 260, fx + 22, by - 190], 8, fill=RED)
            p.rect([fx - 22, by - 260, fx + 22, by - 245], fill=OUT)
        for i in range(8):
            wx = x0 + ((i * 110 - t * 50) % 760) - 30
            p.arc([wx, y0 + 330, wx + 70, y0 + 370], 200, 340, WHITE, 4)
    p.text((cx, cy + 228 - tilt * 0.3), title, f2("anton", 92), INK)

def gary(p, x, yf, s, orange):
    skin = tuple(int(P.SKIN[i] + ((255, 140, 40)[i] - P.SKIN[i]) * orange) for i in range(3))
    P.ground_shadow(p, x, yf, 120 * s)
    for sx in (-1, 1):
        P.orr(p, [x + sx * 40 * s - 22 * s, yf - 170 * s, x + sx * 40 * s + 22 * s, yf - 10 * s], 18 * s, skin, ow=4)
        p.ell([x + sx * 40 * s - 34 * s, yf - 24 * s, x + sx * 40 * s + 34 * s, yf + 8 * s], fill=OUT)
    P.orr(p, [x - 95 * s, yf - 230 * s, x + 95 * s, yf - 140 * s], 30 * s, (250, 200, 80), ow=4)          # shorts
    P.orr(p, [x - 110 * s, yf - 440 * s, x + 110 * s, yf - 210 * s], 50 * s, (60, 190, 200), ow=5)       # shirt
    for fx, fy in [(-60, -400), (30, -360), (-20, -290), (70, -270), (-80, -250), (60, -420)]:
        for a in range(5):
            ang = a * 1.256
            p.circle(x + fx * s + 13 * s * math.cos(ang), yf + fy * s + 13 * s * math.sin(ang), 9 * s, fill=(255, 120, 170))
        p.circle(x + fx * s, yf + fy * s, 6 * s, fill=YEL)
    for sx in (-1, 1):
        P.oline(p, (x + sx * 100 * s, yf - 410 * s), (x + sx * 150 * s, yf - 260 * s), (60, 190, 200), 38 * s, ow=4)
        P.ocircle(p, x + sx * 150 * s, yf - 255 * s, 24 * s, skin, ow=4, shaded=False)
    hx, hy = x, yf - 520 * s
    P.ocircle(p, hx, hy, 95 * s, skin, ow=5)
    p.rr([hx - 80 * s, hy - 30 * s, hx + 80 * s, hy + 8 * s], 14 * s, fill=OUT)        # sunglasses
    p.rr([hx - 72 * s, hy - 24 * s, hx - 8 * s, hy + 2 * s], 10 * s, fill=(40, 60, 90))
    p.rr([hx + 8 * s, hy - 24 * s, hx + 72 * s, hy + 2 * s], 10 * s, fill=(40, 60, 90))
    p.arc([hx - 40 * s, hy + 20 * s, hx + 40 * s, hy + 60 * s], 20, 160, OUT, 6 * s)
    p.poly([(hx - 100 * s, hy - 60 * s), (hx, hy - 150 * s), (hx + 100 * s, hy - 60 * s)], (240, 220, 150))  # straw hat
    p.rr([hx - 140 * s, hy - 70 * s, hx + 140 * s, hy - 50 * s], 10 * s, fill=(220, 196, 120))

def washing_machine(p, cx, cy, t):
    P.orr(p, [cx - 120, cy - 150, cx + 120, cy + 150], 18, (238, 240, 244))
    p.rect([cx - 110, cy - 140, cx + 110, cy - 100], fill=(210, 214, 222))
    p.circle(cx, cy + 20, 92, fill=OUT); p.circle(cx, cy + 20, 82, fill=(120, 170, 220))
    for i in range(3):
        a = t * 6 + i * 2.1
        p.circle(cx + 40 * math.cos(a), cy + 20 + 40 * math.sin(a), 22, fill=[(220, 80, 80), (250, 220, 90), (90, 200, 120)][i])

@V.sounds
def sounds(L):
    a8, e8 = L(8)
    out = [(L(1)[0], "thud"), (L(2)[1] - 0.5, "ding"), (L(3)[1] - 0.6, "boing"), (L(4)[1] - 1.2, "boing"),
           (L(5)[1] - 0.8, "pop"), (L(6)[0], "thud"), (L(7)[1] - 0.4, "cash")]
    out += [(e8 + 0.15 + i * MONTAGE / 5, "cash") for i in range(5)]
    out += [(L(9)[0], "ding"), (L(11)[1] - 1.0, "pop")]
    return out

@V.scene(0, 1)
def town(p, t, L):
    a1, _ = L(1)
    sky_bg(p)
    p.circle(880, 420, 60, fill=YEL)
    p.rect([0, 960, 1080, 1170], fill=GRASS)
    p.rect([0, 1030, 1080, 1100], fill=PAVE)
    for i in range(0, 1080, 90):
        p.rect([i, 1062, i + 50, 1068], fill=WHITE)
    houses = [(150, (240, 200, 160), (190, 80, 70)), (400, (200, 220, 240), (80, 100, 150)), (650, (250, 230, 180), (150, 90, 60))]
    for i, (cx, wall, roof) in enumerate(houses):
        house(p, cx, 960, 210, 230, wall, roof, t)
        t0 = 0.5 + i * 0.6
        k = prog(t, t0, t0 + 2.2)
        if 0 < k < 1:
            px = cx + 40 + 700 * eio(k)
            if px < 1000:
                plane(p, px, 700 - 330 * eio(k), 0.9 + 0.3 * k)
        if t > t0 - 0.2:
            P.orr(p, [cx + 40, 900, cx + 90, 958], 8, (200, 90, 120), ow=3)
            pill(p, cx, 560, "AWAY", prog(t, t0, t0 + 0.3), bg=WHITE, size=30)
    house(p, 900, 960, 190, 220, (190, 190, 186), (110, 110, 110), t, shabby=True)
    if t > a1 - 0.2:
        k = eback(prog(t, a1 - 0.2, a1 + 0.3))
        cloud(p, 900, 560, 0.9 * k)
        for i in range(10):
            ry = 620 + ((t * 420 + i * 47) % 160)
            p.line([(830 + i * 15, ry), (826 + i * 15, ry + 22)], (90, 140, 220), 4)
        pill(p, 900, 420, "THE PENNYS", prog(t, a1, a1 + 0.3), bg=RED, fg=WHITE, size=34)

@V.scene(2)
def spain(p, t, L):
    a, e = L(2)
    sky_bg(p, (40, 60, 100), (70, 100, 150))
    postcard(p, t, a - 0.34, "spain", "SPAIN")
    k = eback(prog(t, e - 0.7, e - 0.4))
    if k > 0:
        p.circle(820, 900, 110 * k, fill=RED)
        p.circle(820, 900, 96 * k, outline=WHITE, width=5)
        p.text((820, 900), "×2", f2("anton", int(90 * k) + 1), WHITE)
    pill(p, 540, 1080, "NEXT DOOR", prog(t, a + 0.1, a + 0.4), bg=WHITE)

@V.scene(3)
def florida(p, t, L):
    a, e = L(3)
    sky_bg(p, (40, 60, 100), (70, 100, 150))
    postcard(p, t, a - 0.34, "florida", "FLORIDA", cx=470, cy=640)
    orange = eio(prog(t, e - 1.3, e - 0.5))
    gary(p, 860 + 6 * math.sin(t * 3), 1165, 0.5, orange)
    pill(p, 300, 1080, "GARY FROM WORK", prog(t, a + 0.3, a + 0.6), bg=WHITE, size=34)
    if orange > 0.5:
        for ang, rr in [(-40, 230), (200, 220), (-140, 240)]:
            q = math.radians(ang)
            sparkle(p, 860 + math.cos(q) * rr, 900 + math.sin(q) * rr, 26 * eback(prog(t, e - 0.6, e - 0.3)), fill=ORANGE)

@V.scene(4)
def skiing(p, t, L):
    a, e = L(4)
    sky_bg(p, (40, 60, 100), (70, 100, 150))
    postcard(p, t, a - 0.34, "ski", "SKIING", cy=640)
    dk = eback(prog(t, a + 2.2, a + 2.6))
    if dk > 0:
        x = 600 + 80 * math.sin(t * 1.6)
        yf = 795
        s = 0.72 * dk
        p.rr([x - 240 * s, yf - 6 * s, x + 200 * s, yf + 14 * s], 10 * s, fill=RED)
        p.rr([x - 230 * s, yf + 20 * s, x + 210 * s, yf + 40 * s], 10 * s, fill=(240, 200, 60))
        P.crumbs(p, x, yf, s, "happy", t)
        hx, hy = x - 110 * s, yf - 190 * s
        p.rr([hx - 70 * s, hy - 40 * s, hx + 70 * s, hy - 2 * s], 18 * s, fill=OUT)
        p.rr([hx - 62 * s, hy - 34 * s, hx + 62 * s, hy - 8 * s], 14 * s, fill=(255, 170, 60))
        pill(p, 540, 1080, "THEIR DOG. ON SKIS.", prog(t, a + 2.5, a + 2.8), bg=WHITE)

@V.scene(5)
def cruise(p, t, L):
    a, e = L(5)
    sky_bg(p, (40, 60, 100), (70, 100, 150))
    postcard(p, t, a - 0.34, "cruise", "CRUISE")
    pill(p, 540, 1080, "DAVE'S MUM · AGE 84", prog(t, e - 1.2, e - 0.9), bg=WHITE)

@V.scene(6, 7)
def not_us(p, t, L):
    a6, e6 = L(6); a7, e7 = L(7)
    P.living_room(p, t, 0.02)
    P.family(p, t, {"dave": "sad", "sue": "worried" if t > a7 else "sad", "ellie": "neutral", "alfie": "sad", "crumbs": "neutral"},
             talk=P.talkers(V, t))
    if t < a7:
        k = eback(prog(t, a6, a6 + 0.35))
        if k > 0:
            p.rr([140, 360, 940, 520], 30, fill=(20, 30, 50))
            p.text((540, 440), "BUT NOT US.", f2("anton", int(120 * k) + 1), YEL)
    else:
        pill(p, 330, 420, "30 DAYS", prog(t, a7 + 0.6, a7 + 0.9), bg=RED, fg=WHITE, size=56)
        pill(p, 750, 420, "£1,000", prog(t, e7 - 0.8, e7 - 0.5), bg=GREEN, fg=INK, size=56)

SHOTS = ["dave", "sue", "ellie", "alfie", "crumbs"]

@V.scene(8)
def day_by_day(p, t, L):
    a8, e8 = L(8)
    i = int((t - e8 - 0.15) / (MONTAGE / 5)) if t > e8 + 0.15 else -1
    p.rect([0, 300, 1080, 1170], fill=(24, 30, 46))
    with p.flat():
        for k in range(7):
            p.circle(540, 760, 520 - k * 60, fill=(28 + k * 3, 36 + k * 3, 56 + k * 4))
    if i < 0:
        P.living_room(p, t, 0.02)
        P.dave(p, 540, 1150, 1.15, "tired", t, talk=V.talk(t, "dave"))
        return
    i = min(i, 4)
    t0 = e8 + 0.15 + i * MONTAGE / 5
    who = SHOTS[i]
    level = 0.05 + 0.17 * (i + prog(t, t0, t0 + MONTAGE / 5))
    if who == "dave":
        washing_machine(p, 330, 860, t)
        P.dave(p, 760, 1150, 1.0, "happy", t, hold="wrench")
        money_txt, mx = "+£40", 330
    elif who == "sue":
        P.sue(p, 330, 1150, 1.0, "happy", t, hold="phone")
        p.rr([560, 900, 1000, 940], 10, fill=(150, 110, 80))
        for j in range(5):
            hgt = int(6 + 6 * min(8, (t - t0) * 12 - j))
            for c in range(max(0, hgt // 6)):
                p.ell([600 + j * 80, 890 - c * 12, 660 + j * 80, 906 - c * 12], fill=BRASS, outline=BRASS_D, width=2)
        money_txt, mx = "+£12", 780
    elif who == "ellie":
        P.ellie(p, 380, 1150, 1.05, "happy", t, hold="phone")
        p.rr([600, 560, 960, 900], 30, fill=WHITE)
        p.rr([640, 600, 920, 760], 16, fill=(200, 170, 255))
        p.text((780, 820), "SOLD!", f2("anton", 70), GREEN)
        money_txt, mx = "+£15", 780
    elif who == "alfie":
        p.rr([520, 820, 980, 1000], 14, fill=(240, 200, 120))
        p.rr([560, 600, 940, 720], 14, fill=WHITE)
        p.text((750, 640), "LEMONADE", f2("anton", 50), INK)
        p.text((750, 695), "50p", f2("dm", 40), RED)
        for j in range(3):
            p.rr([600 + j * 110, 760, 660 + j * 110, 820], 10, fill=(255, 240, 120))
        P.alfie(p, 300, 1150, 1.1, "grin", t, wave=1)
        money_txt, mx = "+£3", 750
    else:
        P.jar(p, 380, 1050, 2.4, level)
        P.crumbs(p, 760, 1150, 1.0, "happy", t)
        money_txt, mx = "+£0 (HE TRIED)", 540
    P.money_pop(p, t, t0 + 0.25, money_txt, x=mx, y=620)
    pill(p, 540, 380, "DAY BY DAY", 1.0, bg=YEL, size=50)
    P.jar(p, 960, 560, 0.9, level, label=False)

@V.scene(9, 11)
def finale(p, t, L):
    a9, _ = L(9); a10, _ = L(10); a11, e11 = L(11)
    P.living_room(p, t, 0.3)
    if t < a10:
        P.alfie(p, 540, 1150, 1.4, "grin", t, wave=1, talk=V.talk(t, "alfie"))
        for ang, rr in [(-30, 330), (200, 320), (20, 360), (160, 350)]:
            q = math.radians(ang)
            sparkle(p, 540 + math.cos(q) * rr, 720 + math.sin(q) * rr, 30 * eback(prog(t, a9 + 0.1, a9 + 0.5)))
    elif t < a11:
        P.dave(p, 540, 1150, 1.0, "happy", t, talk=V.talk(t, "dave"))
        pill(p, 540, 380, "WHERE DID YOU GO?", prog(t, a10 + 0.3, a10 + 0.6), bg=WHITE, size=52)
        pill(p, 540, 470, "RUB IT IN, IN THE COMMENTS", prog(t, a10 + 2.6, a10 + 2.9), bg=YEL, size=40)
    else:
        P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "happy", "alfie": "grin"})
        pill(p, 540, 400, "THE PENNYS", prog(t, a11 + 0.1, a11 + 0.4), bg=RED, fg=WHITE, size=60)
        pill(p, 540, 500, "YOU DECIDE WHAT THEY DO", prog(t, a11 + 3.0, a11 + 3.3), bg=WHITE, size=40)
        fp = prog(t, e11 - 1.8, e11 - 1.4)
        if fp > 0:
            r = 58 * eback(fp)
            p.circle(880, 620, r, fill=RED)
            p.line([(880 - r * .45, 620), (880 + r * .45, 620)], fill=WHITE, width=12)
            p.line([(880, 620 - r * .45), (880, 620 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
