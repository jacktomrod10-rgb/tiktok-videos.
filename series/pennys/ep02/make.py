import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

DAY = 2
FUND_BEFORE = 23.50
FUND = 88.00          # 23.50 + 78 sales - 10 pitch - 3.50 bacon roll
VOTES = {"A": 1, "B": 0, "C": 0}

SCRIPT = [
    # (speaker, spoken text, caption text)
    ("narrator", "Yesterday, you voted for the car boot sale. And then Crumbs struck again.", "Yesterday, you voted for the *car boot sale*. And then *Crumbs* struck again."),
    ("narrator", "The winner: A. Every single vote.", "The winner: *A*. *Every single* vote."),
    ("narrator", "Six in the morning. Dave packed the car with twenty years of garage junk.", "*6am*. Dave packed the car with *20 years* of garage junk."),
    ("dave", "Best day out since Skegness. And it's not even raining!", "Best day out since *Skegness*. And it's not even *raining!*"),
    ("sue", "Everything has a price sticker. Nobody haggles with me.", "Everything has a *price sticker*. Nobody *haggles* with me."),
    ("ellie", "If anyone from school sees me, I'm literally moving to Australia. On my own.", "If anyone from *school* sees me, I'm *literally* moving to Australia. On my *own*."),
    ("alfie", "I sold all my dinosaurs. I'm a kangaroo person now.", "I sold all my *dinosaurs*. I'm a *kangaroo* person now."),
    ("narrator", "They sold seventy-eight pounds of stuff. Then Crumbs ate a customer's bacon roll.", "They sold *£78* of stuff. Then Crumbs ate a customer's *bacon roll*."),
    ("narrator", "Minus ten pounds for the pitch. Minus three pounds fifty for a new roll.", "Minus *£10* for the pitch. Minus *£3.50* for a new roll."),
    ("narrator", "The holiday fund is now eighty-eight pounds. Happiness: fifty-five out of a hundred. And the house, with an empty garage: forty.", "The holiday fund is now *£88*. Happiness: *55/100*. And the house, with an empty garage: *40/100*."),
    ("narrator", "But back home, Dave put the car keys down for one second.", "But back home, Dave put the *car keys* down for *one second*."),
    ("narrator", "Crumbs buried them. Somewhere in the garden.", "Crumbs *buried* them. Somewhere in the *garden*."),
    ("dave", "I need that car for work tomorrow!", "I need that car for *work* tomorrow!"),
    ("narrator", "So what should the Pennys do?", "So what should the Pennys *do*?"),
    ("narrator", "A: dig up the whole garden. It's free, but they might not find them. B: buy a new key, for eighty pounds. Or C: Dave rides to work on Alfie's tiny bike.", "*A*: dig up the whole garden. It's free, but they might not find them. *B*: buy a new key, for *£80*. Or *C*: Dave rides to work on Alfie's *tiny bike*."),
    ("alfie", "Don't break it, Dad!", "Don't *break* it, Dad!"),
    ("narrator", "Comment A, B or C. Day three, tomorrow. Follow, to see if they make it.", "Comment *A*, *B* or *C*. *Day 3*, tomorrow. Follow, to see if they make it."),
]

V = Video(
    "pennys-ep02", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS,
    lines=[(sp, txt) for sp, txt, _ in SCRIPT],
    display=[cap for _, _, cap in SCRIPT],
)

OPTIONS = [("A", "Dig up the garden", "FREE   HOUSE -   MAY NOT FIND THEM"),
           ("B", "Buy a new key", "-£80   SORTED"),
           ("C", "Dave rides Alfie's bike", "FREE   DAVE TIRED   HAPPINESS -")]

OUT = P.OUT
SKY_T, SKY_B = (120, 190, 240), (190, 228, 250)
GRASS, GRASS_D = (110, 180, 100), (92, 160, 86)
SOIL, SOIL_D = (120, 82, 52), (96, 64, 40)

def at(i, sub):
    """Approximate time the substring `sub` starts in spoken line i (by character position)."""
    a, b = V.L(i)
    txt = V.lines[i][1]
    k = txt.find(sub)
    return a + (b - a) * max(0, k) / max(1, len(txt))

# ---------------- props ----------------
def sky(p, top=SKY_T, bot=SKY_B, y0=300, y1=780):
    n = 10
    for i in range(n):
        c = tuple(int(top[j] + (bot[j] - top[j]) * i / (n - 1)) for j in range(3))
        p.rect([0, y0 + (y1 - y0) * i / n, 1080, y0 + (y1 - y0) * (i + 1) / n + 1], fill=c)

def cloud(p, x, y, s=1.0, col=(250, 252, 255)):
    for dx, dy, r in [(-60, 10, 46), (0, -14, 60), (60, 10, 46), (0, 20, 46)]:
        p.circle(x + dx * s, y + dy * s, r * s, fill=col)

def gazebo(p, cx, base, w, col):
    p.rect([cx - w / 2 + 6, base - 90, cx - w / 2 + 12, base], fill=(230, 230, 230))
    p.rect([cx + w / 2 - 12, base - 90, cx + w / 2 - 6, base], fill=(230, 230, 230))
    p.poly([(cx - w / 2, base - 90), (cx, base - 140), (cx + w / 2, base - 90)], col)
    p.rect([cx - w / 2, base - 96, cx + w / 2, base - 84], fill=shade(col, .8))

def shade(c, k=0.8):
    return tuple(int(v * k) for v in c)

def field(p, t, sun_y=430):
    sky(p)
    p.circle(880, sun_y, 62 + 3 * pulse(t, 1.6), fill=YEL)
    for i, (x0, y, s) in enumerate([(160, 420, 0.9), (620, 380, 0.7), (1000, 470, 0.8)]):
        x = (x0 + t * (12 + i * 5)) % 1300 - 110
        cloud(p, x, y, s)
    p.rect([0, 700, 1080, 1170], fill=GRASS)
    for i in range(0, 1080, 60):       # far hedge
        p.circle(i + 30, 705, 42, fill=(70, 130, 70))
    for i, (cx, col) in enumerate([(120, (230, 90, 90)), (330, (90, 150, 230)), (560, (240, 200, 70)), (790, (120, 200, 160)), (990, (230, 130, 190))]):
        gazebo(p, cx, 760, 150, col)
    # bunting
    pts = [(60 + i * 80, 320 + 28 * math.sin(i * 0.9) ** 2) for i in range(13)]
    p.line(pts, (240, 240, 240), 3)
    for i, (x, y) in enumerate(pts[:-1]):
        col = [RED, YEL, BLUE, GREEN][i % 4]
        sw = 3 * math.sin(t * 3 + i)
        p.poly([(x + 8, y + 4), (x + 44, y + 6), (x + 26 + sw, y + 50)], col)
    for i in range(14):                # grass tufts
        gx = (i * 83) % 1080 + 20
        gy = 860 + (i * 57) % 270
        p.line([(gx, gy), (gx - 6, gy - 18)], GRASS_D, 4)
        p.line([(gx + 8, gy), (gx + 10, gy - 20)], GRASS_D, 4)

def car(p, x, base, s=1.0, boot=1.0, boxes=0):
    red, red_d = (200, 72, 62), (160, 52, 46)
    P.ground_shadow(p, x, base, 250 * s)
    # cabin
    p.rr([x - 150 * s - 5, base - 215 * s - 5, x + 160 * s + 5, base - 100 * s], 40 * s, fill=OUT)
    p.rr([x - 150 * s, base - 215 * s, x + 160 * s, base - 100 * s], 36 * s, fill=red)
    p.rr([x - 128 * s, base - 196 * s, x - 10 * s, base - 120 * s], 14 * s, fill=(170, 215, 240))
    p.rr([x + 5 * s, base - 196 * s, x + 110 * s, base - 120 * s], 14 * s, fill=(170, 215, 240))
    # body
    P.orr(p, [x - 240 * s, base - 130 * s, x + 240 * s, base - 40 * s], 30 * s, red, shade_side="r")
    p.circle(x - 200 * s, base - 100 * s, 12 * s, fill=YEL)          # headlight
    p.ell([x + 60 * s, base - 80 * s, x + 96 * s, base - 62 * s], fill=(150, 90, 60))   # rust spot
    if boot > 0:
        # open boot: dark opening and a lid swung up
        p.rr([x + 120 * s, base - 200 * s, x + 236 * s, base - 70 * s], 18 * s, fill=(50, 40, 44))
        for i in range(boxes):
            bx, by = x + 140 * s + (i % 2) * 46 * s, base - 110 * s - (i // 2) * 40 * s
            p.rect([bx - 3, by - 3, bx + 44 * s + 3, by + 38 * s + 3], fill=OUT)
            p.rect([bx, by, bx + 44 * s, by + 38 * s], fill=(205, 160, 105))
        k = boot
        hx, hy = x + 150 * s, base - 212 * s
        ex, ey = hx + 120 * s, hy - 110 * s * k
        P.oline(p, (hx, hy), (ex, ey), red_d, 22 * s, ow=4)
    for wx in (-145, 145):
        P.ocircle(p, x + wx * s, base - 36 * s, 44 * s, (50, 50, 58), ow=4, shaded=False)
        p.circle(x + wx * s, base - 36 * s, 20 * s, fill=(180, 186, 196))

def box(p, x, y, s=1.0):
    p.rect([x - 30 * s - 4, y - 26 * s - 4, x + 30 * s + 4, y + 26 * s + 4], fill=OUT)
    p.rect([x - 30 * s, y - 26 * s, x + 30 * s, y + 26 * s], fill=(205, 160, 105))
    p.rect([x - 30 * s, y - 6 * s, x + 30 * s, y + 4 * s], fill=(180, 135, 85))

def table(p, x0, x1, top, legs_to):
    for lx in (x0 + 30, x1 - 30):
        p.line([(lx - 20, top + 40), (lx + 20, legs_to)], OUT, 10)
        p.line([(lx + 20, top + 40), (lx - 20, legs_to)], OUT, 10)
    p.rr([x0 - 5, top - 5, x1 + 5, top + 75], 12, fill=OUT)
    p.rr([x0, top, x1, top + 70], 10, fill=(240, 240, 236))
    for i in range(int((x1 - x0) / 40)):
        if i % 2 == 0:
            p.rect([x0 + i * 40, top + 30, x0 + i * 40 + 40, top + 70], fill=(220, 90, 100))

def lamp(p, x, y):
    p.rr([x - 30, y - 12, x + 30, y], 6, fill=OUT)
    p.line([(x, y - 10), (x, y - 90)], OUT, 8)
    p.poly([(x - 52, y - 80), (x + 52, y - 80), (x + 30, y - 150), (x - 30, y - 150)], OUT)
    p.poly([(x - 45, y - 84), (x + 45, y - 84), (x + 26, y - 145), (x - 26, y - 145)], (250, 220, 150))

def records(p, x, y):
    for i in range(3):
        p.rr([x - 50 + i * 8, y - 100 + i * 6, x + 50 + i * 8, y], 6, fill=OUT)
        p.rr([x - 46 + i * 8, y - 96 + i * 6, x + 46 + i * 8, y - 4], 4, fill=[(90, 120, 200), (230, 140, 60), (150, 90, 170)][i])
    p.circle(x + 16, y - 40, 26, fill=(30, 30, 34))
    p.circle(x + 16, y - 40, 8, fill=YEL)

def dino(p, x, y, s=1.0, col=(110, 200, 110)):
    p.ell([x - 40 * s - 4, y - 44 * s - 4, x + 30 * s + 4, y + 4], fill=OUT)
    p.ell([x - 40 * s, y - 44 * s, x + 30 * s, y], fill=col)
    p.line([(x + 15 * s, y - 30 * s), (x + 40 * s, y - 75 * s)], OUT, 22 * s)
    p.line([(x + 15 * s, y - 30 * s), (x + 40 * s, y - 75 * s)], col, 14 * s)
    p.circle(x + 44 * s, y - 80 * s, 20 * s, fill=OUT)
    p.circle(x + 44 * s, y - 80 * s, 15 * s, fill=col)
    p.circle(x + 50 * s, y - 84 * s, 4 * s, fill=INK)
    p.poly([(x - 38 * s, y - 20 * s), (x - 72 * s, y - 6 * s), (x - 36 * s, y - 4 * s)], col)
    for i in range(3):
        p.poly([(x - 24 * s + i * 16 * s, y - 40 * s), (x - 16 * s + i * 16 * s, y - 58 * s), (x - 8 * s + i * 16 * s, y - 40 * s)], (240, 140, 80))

def kettle(p, x, y):
    p.rr([x - 44, y - 80, x + 44, y], 30, fill=OUT)
    p.rr([x - 40, y - 76, x + 40, y - 4], 26, fill=(190, 196, 206))
    p.arc([x - 30, y - 110, x + 30, y - 60], 180, 360, OUT, 8)
    p.line([(x + 38, y - 50), (x + 66, y - 72)], OUT, 10)

def price_tag(p, x, y, text, k):
    if k <= 0: return
    w = (34 + 18 * len(text)) * k
    p.line([(x, y - 40 * k), (x, y - 18 * k)], OUT, 3)
    p.rr([x - w / 2 - 3, y - 22 * k, x + w / 2 + 3, y + 26 * k], 10, fill=OUT)
    p.rr([x - w / 2, y - 19 * k, x + w / 2, y + 23 * k], 8, fill=YEL)
    if k > 0.9:
        p.text((x, y + 2), text, f2("anton", 34), INK)

def keys(p, x, y, s=1.0):
    p.circle(x, y, 22 * s, outline=OUT, width=int(7 * s) + 1)
    p.circle(x, y, 22 * s, outline=(200, 200, 210), width=int(4 * s) + 1)
    for ang, col in ((0.5, YEL), (1.3, (190, 196, 206))):
        x1, y1 = x + math.cos(ang) * 26 * s, y + math.sin(ang) * 26 * s
        x2, y2 = x + math.cos(ang) * 84 * s, y + math.sin(ang) * 84 * s
        P.oline(p, (x1, y1), (x2, y2), col, 12 * s, ow=3)
        for j in (0.55, 0.75):
            tx, ty = x + math.cos(ang) * 84 * s * j, y + math.sin(ang) * 84 * s * j
            p.rect([tx - 4 * s, ty, tx + 4 * s, ty + 12 * s], fill=col)
        p.circle(x1, y1, 14 * s, fill=OUT)
        p.circle(x1, y1, 10 * s, fill=col)

def bacon_roll(p, x, y, s=1.0):
    p.ell([x - 60 * s - 4, y - 30 * s - 4, x + 60 * s + 4, y + 30 * s + 4], fill=OUT)
    p.ell([x - 60 * s, y - 2 * s, x + 60 * s, y + 30 * s], fill=(225, 170, 100))
    p.rr([x - 66 * s, y - 10 * s, x + 66 * s, y + 6 * s], 8 * s, fill=(200, 80, 70))
    p.ell([x - 60 * s, y - 30 * s, x + 60 * s, y], fill=(235, 180, 110))
    for i in range(4):
        p.circle(x - 30 * s + i * 20 * s, y - 20 * s, 3 * s, fill=(250, 235, 200))

def ellie_shades(p, x, yf, s, t):
    hr = 72 * s
    top = yf - 360 * s
    hy = top - hr * .82 + math.sin(t * 2.0 + 2) * 3 * s
    ey, ex = hy - hr * .06, hr * .34
    for sx in (-1, 1):
        p.rr([x + sx * ex - hr * .28, ey - hr * .2, x + sx * ex + hr * .28, ey + hr * .2], hr * .1, fill=(26, 26, 34))
        p.rr([x + sx * ex - hr * .2, ey - hr * .14, x + sx * ex - hr * .02, ey - hr * .06], hr * .04, fill=(110, 110, 140))
    p.line([(x - ex + hr * .26, ey - hr * .05), (x + ex - hr * .26, ey - hr * .05)], (26, 26, 34), max(3, hr * .07))

def garden(p, t, mounds=0):
    sky(p, y1=700)
    p.circle(940, 480, 48, fill=YEL)
    cloud(p, (200 + t * 14) % 1300 - 110, 470, 0.7)
    # fence
    p.rect([0, 600, 1080, 820], fill=(170, 120, 80))
    for i in range(0, 1080, 72):
        p.rect([i, 590, i + 64, 820], fill=(186, 134, 90))
        p.poly([(i, 590), (i + 32, 566), (i + 64, 590)], (186, 134, 90))
        p.line([(i + 66, 600), (i + 66, 820)], (140, 96, 62), 6)
    p.rect([0, 680, 1080, 694], fill=(150, 104, 70))
    p.rect([0, 800, 1080, 1170], fill=GRASS)
    p.rr([780, 740, 1000, 830], 20, fill=(230, 110, 150))           # flower bed
    for i in range(6):
        p.circle(800 + i * 36, 742, 16, fill=[RED, YEL, WHITE][i % 3])
    spots = [(180, 900), (420, 960), (760, 930), (290, 1080), (880, 1060), (600, 1110)]
    for i, (mx, my) in enumerate(spots[:mounds]):
        p.ell([mx - 70, my - 34, mx + 70, my + 20], fill=SOIL_D)
        p.ell([mx - 60, my - 44, mx + 60, my + 10], fill=SOIL)
        p.ell([mx - 40, my - 30, mx + 40, my - 6], fill=(70, 46, 30))

def dirt_spray(p, x, y, t, d=1):
    for i in range(14):
        ph = (t * 1.8 + i / 14) % 1
        px = x + d * (30 + 260 * ph)
        py = y - 340 * ph + 380 * ph * ph
        p.circle(px, py, 10 + 6 * ((i * 7) % 3), fill=SOIL if i % 2 else SOIL_D)

# ---------------- fixed HUD ----------------
@V.fixed
def hud_band(p, t):
    k = eo(prog(t, V.L(9)[0], V.L(9)[0] + 1.4))
    P.hud(p, DAY, FUND_BEFORE + (FUND - FUND_BEFORE) * k)

@V.sounds
def sounds(L):
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh"), (2.6, "pop")]
    out += [(L(1)[0] + 0.2, "pop"), (L(1)[0] + 1.3, "ding")]
    a2, e2 = L(2)
    out += [(a2 + 0.9 + i * 1.1 + 0.7, "thud") for i in range(3)]
    out += [(L(3)[0] + 0.3, "ding")]
    a4, e4 = L(4)
    out += [(a4 + 0.4 + i * 0.45, "pop") for i in range(4)]
    out += [(L(5)[0] + 0.4, "pop"), (L(6)[1] - 0.8, "pop")]
    a7, e7 = L(7)
    out += [(at(7, "Then") - 0.5, "cash"), (at(7, "Then") + 0.2, "boing")]
    a8, e8 = L(8)
    out += [(a8 + 0.05, "pop"), (at(8, "Minus three") , "pop"), (e8 + 0.05, "cash")]
    out += [(L(9)[0] + 1.4, "ding")]
    out += [(L(10)[1] - 0.6, "boing"), (L(11)[0] + 0.3, "thud"), (L(12)[0], "thud")]
    out += [(at(14, "B:") - 0.1, "pop"), (at(14, "Or C") - 0.1, "pop"), (L(14)[0], "pop")]
    out += [(L(15)[0], "boing"), (L(16)[0] + 0.1, "pop"), (at(16, "Day three"), "ding")]
    return out

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    field(p, t)
    car(p, 290, 1000, 0.9, boot=1.0, boxes=4)
    P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}, yf=1120, sc=0.78,
             xs=(170, 380, 600, 790, 960))
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0, dx = 560, -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.35, 0.7)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "DAY 2", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "£976.50 TO GO", f2("anton", max(10, int(96 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "CAR BOOT SALE. WHAT COULD GO WRONG?", f2("dm", max(8, int(40 * k3))), (255, 160, 190))
    pill(p, 540, 390, "YOU VOTED: CAR BOOT SALE", prog(t, 2.6, 3.0), bg=YEL)
    if t > L(0)[1] - 1.8:
        pill(p, 960, 880, "?!", prog(t, L(0)[1] - 1.8, L(0)[1] - 1.5), bg=RED, fg=WHITE, size=40)

@V.scene(1)
def result(p, t, L):
    a1, _ = L(1)
    p.text((540, 360), "YOUR VOTES", f2("anton", 72), YEL)
    P.result_bars(p, t, a1 - 0.1, VOTES, top=440)
    labels = ["CAR BOOT SALE", "DAVE'S WEEKEND JOBS", "ELLIE SELLS CLOTHES"]
    for i, lab in enumerate(labels):
        k = prog(t, a1 + 0.2 + i * 0.2, a1 + 0.5 + i * 0.2)
        if k > 0:
            p.text((540, 440 + i * 150 + 55), lab, f2("dm", 36), INK if i == 0 else WHITE)
    if t > a1 + 1.0:
        tick(p, 540, 1000, 70, prog(t, a1 + 1.0, a1 + 1.4))
        pill(p, 540, 1110, "A WINS", prog(t, a1 + 1.1, a1 + 1.4), bg=P.OPT_COLS["A"], size=48)

@V.scene(2, 6)
def car_boot(p, t, L):
    a2, e2 = L(2)
    if t < L(3)[0] - 0.2:
        # dawn: Dave loads the car
        k = prog(t, a2 - 0.3, e2)
        field(p, t, sun_y=lerp(700, 470, eo(k)))
        n_in = 0
        for i in range(3):
            t0 = a2 + 0.9 + i * 1.1
            q = prog(t, t0, t0 + 0.7)
            if q >= 1: n_in += 1
            elif q > 0:
                bx = lerp(700, 470, q); by = lerp(840, 860, q) - 220 * math.sin(math.pi * q)
                box(p, bx, by, 0.9)
        car(p, 290, 1000, 0.9, boot=1.0, boxes=min(4, n_in + 1))
        P.dave(p, 760, 1130, 0.85, "happy", t, talk=0.0)
        if t < a2 + 0.9 + 2 * 1.1 + 0.4:
            box(p, 760, 860, 0.9)
        pill(p, 540, 390, "6:00 AM", prog(t, a2 + 0.1, a2 + 0.4), bg=WHITE, size=48)
        pill(p, 540, 470, "20 YEARS OF JUNK", prog(t, at(2, "twenty"), at(2, "twenty") + 0.3), bg=ORANGE, size=36)
        return
    field(p, t)
    car(p, 200, 1000, 0.75, boot=1.0, boxes=4)
    table(p, 470, 1000, 900, 1040)
    # items on the table
    lamp(p, 540, 905)
    records(p, 680, 905)
    kettle(p, 960, 905)
    a6, e6 = L(6)
    if t < a6 - 0.2 or t > a6 + 1.6:
        dino(p, 820, 902, 0.8)
    a4, e4 = L(4)
    for i, (x, txt) in enumerate([(540, "£2"), (690, "£5"), (830, "50p"), (960, "£1")]):
        price_tag(p, x, 960, txt, eback(prog(t, a4 + 0.4 + i * 0.45, a4 + 0.7 + i * 0.45)))
    who = "dave"
    for i, w in ((3, "dave"), (4, "sue"), (5, "ellie"), (6, "alfie")):
        if t >= L(i)[0] - 0.25: who = w
    a, _ = L({"dave": 3, "sue": 4, "ellie": 5, "alfie": 6}[who])
    k = eback(prog(t, a - 0.25, a + 0.2))
    s = 0.95 * max(0.01, k)
    talk = V.talk(t, who)
    if who == "dave":
        P.dave(p, 300, 1140, s, "grin", t, wave=1, talk=talk)
        tick(p, 670, 390, 36, prog(t, at(3, "And") + 0.3, at(3, "And") + 0.6))
        pill(p, 480, 390, "RAIN: NONE", prog(t, at(3, "And") + 0.2, at(3, "And") + 0.5), bg=WHITE, size=40)
        for ang in range(0, 360, 45):
            r0, r1 = 80, 110 + 8 * pulse(t, 0.8)
            ar = math.radians(ang + t * 20)
            p.line([(880 + r0 * math.cos(ar), 430 + r0 * math.sin(ar)), (880 + r1 * math.cos(ar), 430 + r1 * math.sin(ar))], YEL, 8)
    elif who == "sue":
        P.sue(p, 300, 1140, s, "happy", t, talk=talk)
        pill(p, 500, 390, "PRICES: FINAL", prog(t, at(4, "Nobody"), at(4, "Nobody") + 0.3), bg=RED, fg=WHITE, size=40)
    elif who == "ellie":
        P.ellie(p, 300, 1140, s, "worried", t, hold="phone", talk=talk)
        if k > 0.9:
            ellie_shades(p, 300, 1140, s, t)
        pill(p, 500, 390, "UNDERCOVER MODE", prog(t, a + 0.3, a + 0.6), bg=(128, 92, 200), fg=WHITE, size=40)
    else:
        P.alfie(p, 300, 1140, s * 1.05, "grin", t, talk=talk)
        if t > a6 + 1.6:
            pill(p, 820, 840, "SOLD!", prog(t, a6 + 1.6, a6 + 1.9), bg=RED, fg=WHITE, size=40)
        pill(p, 500, 390, "TEAM KANGAROO", prog(t, at(6, "I'm a"), at(6, "I'm a") + 0.3), bg=ORANGE, size=40)

@V.scene(7, 9)
def takings(p, t, L):
    a7, e7 = L(7); a8, e8 = L(8); a9, e9 = L(9)
    tc = at(7, "Then")
    if t < tc - 0.15:
        p.text((540, 400), "SOLD AT THE CAR BOOT", f2("anton", 60), WHITE)
        big_number(p, t, a7 + 0.2, 78, cx=540, cy=680, size=300, start=0, dur=1.4, fill=GREEN, fmt="£{}")
        for i in range(6):
            ang = t * 2 + i * 1.05
            sparkle(p, 540 + 330 * math.cos(ang), 680 + 200 * math.sin(ang), 22)
        P.jar(p, 540, 1120, 1.4, 0.06)
    elif t < a8 - 0.2:
        k = eback(prog(t, tc - 0.15, tc + 0.3))
        P.crumbs(p, 640, 1080, 1.5 * max(0.01, k), "happy", t)
        if k > 0.9:
            bacon_roll(p, 640 - 165, 1080 - 285 + 75, 0.9)
        pill(p, 540, 400, "CHOMP!", prog(t, tc + 0.6, tc + 0.9), bg=RED, fg=WHITE, size=60)
        pill(p, 540, 500, "STOLEN: 1 BACON ROLL", prog(t, tc + 1.0, tc + 1.3), bg=WHITE, size=36)
    elif t < a9 - 0.2:
        p.rr([110, 360, 970, 1120], 40, fill=(20, 30, 50), outline=YEL, width=6)
        p.text((540, 440), "TODAY'S TAKINGS", f2("anton", 64), YEL)
        rows = [(a8 - 0.2, "Car boot sales", "+£78.00", GREEN),
                (a8 + 0.2, "Pitch fee", "-£10.00", RED),
                (at(8, "Minus three"), "Crumbs' bacon roll", "-£3.50", RED)]
        for i, (t0, lab, val, col) in enumerate(rows):
            k = eback(prog(t, t0, t0 + 0.35))
            if k <= 0: continue
            y = 570 + i * 110
            p.text((170, y), lab, f2("dm", max(8, int(44 * k))), WHITE, anchor="lm")
            p.text((910, y), val, f2("anton", max(8, int(56 * k))), col, anchor="rm")
        q = prog(t, e8 - 0.4, e8)
        if q > 0:
            p.line([(170, 880), (170 + 740 * eo(q), 880)], MUTED, 4)
            k = eback(prog(t, e8 - 0.2, e8 + 0.2))
            p.text((170, 970), "Today", f2("dm", max(8, int(48 * k))), WHITE, anchor="lm")
            p.text((910, 970), "+£64.50", f2("anton", max(8, int(80 * k))), YEL, anchor="rm")
    else:
        P.stats_panel(p, t, a9 - 0.2, [("MONEY", 9, GREEN, "£88.00"), ("HAPPINESS", 55, YEL, "55/100"), ("HOUSE", 40, ORANGE, "40/100")])
        pill(p, 540, 1020, "+£64.50 TODAY", prog(t, a9 + 1.4, a9 + 1.7), bg=GREEN, size=44)
        pill(p, 540, 1110, "HOUSE +18: GARAGE EMPTY", prog(t, at(9, "And the house"), at(9, "And the house") + 0.3), bg=WHITE, size=36)

@V.scene(10, 12)
def the_keys(p, t, L):
    a10, e10 = L(10); a11, e11 = L(11); a12, e12 = L(12)
    if t < a11 - 0.2:
        P.living_room(p, t, 0.09)
        grab = prog(t, e10 - 0.7, e10 - 0.2)
        P.dave(p, 250, 1120, 0.9, "happy", t)
        cx = lerp(1180, 820, eo(prog(t, a10 + 1.0, e10 - 0.8)))
        P.crumbs(p, cx, 1100, 0.75, "happy", t)
        if grab < 1:
            keys(p, 720, 810, 1.0)
            sparkle(p, 790, 770, 18 * pulse(t, 0.6))
        else:
            keys(p, cx - 82, 1100 - 128, 0.6)
        pill(p, 540, 390, "1 SECOND...", prog(t, at(10, "for one"), at(10, "for one") + 0.3), bg=WHITE, size=44)
    elif t < a12 - 0.2:
        n = 1 + int(5 * prog(t, a11, e11 + 0.1))
        garden(p, t, mounds=n)
        P.crumbs(p, 560, 1090, 0.95, "happy", t)
        dirt_spray(p, 640, 1020, t, d=1)
        pill(p, 540, 390, "WHERE ARE THE KEYS?", prog(t, a11 + 0.4, a11 + 0.7), bg=RED, fg=WHITE, size=44)
        for i, (qx, qy) in enumerate([(180, 820), (420, 880), (760, 850), (290, 1000), (880, 980)][:n - 1]):
            p.text((qx, qy - 6 * pulse(t + i * 0.3, 0.9)), "?", f2("anton", 64), WHITE)
    else:
        garden(p, t, mounds=6)
        P.dave(p, 330, 1130, 0.95, "shock", t, talk=V.talk(t, "dave"))
        P.crumbs(p, 820, 1110, 0.7, "happy", t)
        p.circle(820 - 0.7 * 110 + 10, 1110 - 0.7 * 190 + 18, 14, fill=SOIL_D)   # muddy nose
        pill(p, 540, 390, "WORK AT 8AM!", prog(t, a12 + 0.3, a12 + 0.6), bg=RED, fg=WHITE, size=48)

@V.scene(13, 16)
def vote(p, t, L):
    a13, _ = L(13); a14, e14 = L(14); a15, _ = L(15); a16, _ = L(16)
    if t < a14 - 0.3:
        garden(p, t, mounds=6)
        P.family(p, t, {"dave": "worried", "sue": "worried", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}, yf=1120)
        pill(p, 540, 390, "YOU DECIDE", prog(t, a13 + 0.3, a13 + 0.6), size=54)
    elif t < a16 - 0.2:
        tA, tB, tC = at(14, "A:"), at(14, "B:"), at(14, "Or C")
        P.vote_card(p, t, tA - 0.7, "HOW DO THEY GET TO WORK?", OPTIONS, gap=(tC - tA) / 2)
        if t > a15 - 0.1:
            k = eback(prog(t, a15 - 0.1, a15 + 0.3))
            P.alfie(p, 920, 1180, 0.55 * max(0.01, k), "worried", t, talk=V.talk(t, "alfie"))
    else:
        P.living_room(p, t, 0.09)
        P.family(p, t, {"dave": "worried", "sue": "happy", "ellie": "happy", "alfie": "grin", "crumbs": "happy"})
        pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a16 + 0.1, a16 + 0.5), bg=WHITE, size=54)
        pill(p, 540, 490, "DAY 3 TOMORROW", prog(t, at(16, "Day three"), at(16, "Day three") + 0.4), bg=YEL, size=40)

if __name__ == "__main__":
    V.main()
