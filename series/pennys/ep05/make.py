import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

DAY = 5
FUND_BEFORE = 28.00
FUND = 133.00         # vote C: 4 paid repair jobs at £30 = £120, minus £15 parts = +£105 (the 5th was just unplugged: free)
VOTES = {"A": 1, "B": 0, "C": 2}

SCRIPT = [
    # (speaker, spoken text, caption text)
    ("narrator", "Yesterday, you voted C. So Sue told ninety-four neighbours: Dave fixes washing machines.", "Yesterday, you voted *C*. So Sue told *94 neighbours*: Dave fixes *washing machines*."),
    ("narrator", "C won, two votes to one. And the street group chat went wild.", "*C* won, *2 votes* to *1*. And the street group chat went *wild*."),
    ("sue", "Five bookings in ten minutes! I've made a spreadsheet.", "*5 bookings* in *10 minutes!* I've made a *spreadsheet*."),
    ("ellie", "Dad's more popular than me in the group chat. Literally embarrassing.", "Dad's more *popular* than me in the group chat. *Literally* embarrassing."),
    ("narrator", "First up: Bev. Then four more, all down the street, until eleven at night.", "First up: *Bev*. Then *4 more*, all down the street, until *11 at night*."),
    ("dave", "That one wasn't broken. It was unplugged.", "That one wasn't *broken*. It was *unplugged*."),
    ("narrator", "He didn't charge for that one. Four jobs at thirty pounds, minus fifteen for parts: plus one hundred and five.", "He didn't charge for that one. *4 jobs* at *£30*, minus *£15* for parts: *+£105*."),
    ("narrator", "The fund jumps to one hundred and thirty-three pounds.", "The fund jumps to *£133*."),
    ("alfie", "Dad missed my bedtime story. Crumbs red it. He ate page four.", "Dad missed my *bedtime story*. Crumbs read it. He *ate page 4*."),
    ("narrator", "Happiness drops to forty-five out of a hundred. House: still sixty-five.", "Happiness drops to *45/100*. House: still *65/100*."),
    ("narrator", "Then, a new message. The launderette: ten broken machines, two hundred pounds, tomorrow at two.", "Then, a *new message*. The launderette: *10 broken machines*, *£200*, tomorrow at *2pm*."),
    ("dave", "Two hundred quid? That's three trips to Skegness!", "*£200*? That's *3 trips* to *Skegness!*"),
    ("alfie", "But tomorrow at two is my school play! I'm the kangaroo!", "But tomorrow at *2* is my *school play!* I'm the *kangaroo!*"),
    ("narrator", "A: take the job, miss the play. B: go to the play, lose the two hundred. Or C: start at six in the morning, and race back for two. One delay, and he misses it.", "*A*: take the job, miss the *play*. *B*: go to the play, lose the *£200*. Or *C*: start at *6am*, and race back for *2*. *One delay*, and he misses it."),
    ("narrator", "Comment A, B or C, or Crumbs chooses again. Day six, tomorrow. Follow, to see if they make it.", "Comment *A*, *B* or *C*, or *Crumbs* chooses again. *Day 6*, tomorrow. Follow, to see if they make it."),
]

V = Video(
    "pennys-ep05", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS,
    lines=[(sp, txt) for sp, txt, _ in SCRIPT],
    display=[cap for _, _, cap in SCRIPT],
    holds={5: 0.5},     # a beat for the washing machine to spin after the plug goes in
)

OPTIONS = [("A", "Take the job", "+£200   MISSES ALFIE'S PLAY"),
           ("B", "Go to the play", "£0   HAPPINESS UP"),
           ("C", "6am start, race back", "+£200?   MIGHT BE LATE")]

OUT = P.OUT

def at(i, sub):
    """Approximate time the substring `sub` starts in spoken line i (by character position)."""
    a, b = V.L(i)
    txt = V.lines[i][1]
    k = txt.find(sub)
    return a + (b - a) * max(0, k) / max(1, len(txt))

def mix(c1, c2, k):
    return tuple(int(c1[j] + (c2[j] - c1[j]) * k) for j in range(3))

def hand(x, yf, s, t, dims, side="l"):
    """Where a character's resting hand is (matches pennys._body). dims = (torso_w, torso_h, leg_h) at scale 1."""
    tw, th, lh = dims[0] * s, dims[1] * s * (1 + 0.012 * math.sin(t * 2.4)), dims[2] * s
    top = yf - lh - th
    aw = tw * .18
    if side == "l":
        return x - tw / 2 - aw * .55, top + th * .8
    return x + tw / 2 + aw * .55, top + th * .8

DAVE_DIMS = (250, 240, 150)

# ---------------- backgrounds ----------------
NIGHT_T, NIGHT_B = (14, 22, 50), (46, 62, 112)
STARS = [(90, 340), (210, 420), (330, 360), (470, 450), (560, 330), (700, 400), (640, 470), (130, 470), (410, 330), (780, 340)]

def sky(p, top, bot, y0=300, y1=760):
    n = 10
    for i in range(n):
        c = mix(top, bot, i / (n - 1))
        p.rect([0, y0 + (y1 - y0) * i / n, 1080, y0 + (y1 - y0) * (i + 1) / n + 1], fill=c)

def moon(p, x, y, r):
    p.circle(x, y, r, fill=(240, 236, 212))
    for dx, dy, rr in [(-0.3, -0.25, 0.22), (0.25, 0.1, 0.16), (-0.1, 0.38, 0.12), (0.35, -0.35, 0.09)]:
        p.circle(x + dx * r, y + dy * r, rr * r, fill=(214, 208, 184))

def stars(p, t, pts=STARS, r=4):
    for i, (sx, sy) in enumerate(pts):
        k = 0.6 + 0.4 * math.sin(t * 3 + i * 1.7)
        p.circle(sx, sy, r * k, fill=(250, 240, 200))

HOUSES = [(150, "9", (196, 120, 96)), (345, "14", (210, 180, 120)), (540, "22", (150, 170, 196)),
          (735, "31", (200, 140, 160)), (930, "40", (170, 190, 140))]

def street(p, t, lit=0, ticks=None):
    """A row of five terraced houses at night. lit = how many have lights on; ticks = {house: pop}."""
    sky(p, NIGHT_T, NIGHT_B, 300, 900)
    stars(p, t)
    moon(p, 960, 372, 40)
    for i, (cx, num, col) in enumerate(HOUSES):
        w = 170
        x0, x1 = cx - w / 2, cx + w / 2
        night = mix(col, (40, 50, 90), 0.35)
        p.poly([(x0 - 14, 606), (cx, 494), (x1 + 14, 606)], OUT)
        p.poly([(x0 - 6, 600), (cx, 504), (x1 + 6, 600)], (92, 62, 72))
        p.rect([x0, 600, x1, 900], fill=night)
        p.rect([x1 - 6, 600, x1, 900], fill=shade(night, .8))
        on = i < lit
        win = (255, 222, 120) if on else (52, 62, 96)
        for wx in (x0 + 20, x1 - 70):
            p.rr([wx - 4, 626, wx + 54, 694], 6, fill=OUT)
            p.rect([wx, 630, wx + 50, 690], fill=win)
            p.rect([wx + 23, 630, wx + 27, 690], fill=OUT)
        p.rr([x0 + 14, 786, cx - 42, 852], 6, fill=OUT)
        p.rect([x0 + 18, 790, cx - 46, 848], fill=win)
        p.rr([cx - 34, 776, cx + 34, 900], 8, fill=OUT)
        p.rr([cx - 30, 780, cx + 30, 900], 6, fill=shade(col, .6))
        p.circle(cx + 18, 842, 5, fill=YEL)
        p.rr([cx - 26, 732, cx + 26, 766], 8, fill=(236, 230, 216))
        p.text((cx, 750), num, f2("anton", 28), INK)
        if ticks and ticks.get(i, 0) > 0:
            tick(p, cx, 452, 34, ticks[i])
    p.rect([0, 900, 1080, 1170], fill=(70, 76, 98))
    p.rect([0, 900, 1080, 916], fill=(96, 102, 124))
    for i in range(0, 1080, 180):
        p.line([(i + 40, 1040), (i + 140, 1040)], (86, 92, 114), 6)

def shade(c, k=0.82):
    return tuple(int(v * k) for v in c)

def kitchen(p, t):
    p.rect([0, 300, 1080, 1010], fill=(232, 212, 172))
    for yy in range(700, 1010, 60):
        for xx in range(0, 1080, 60):
            p.rect([xx + 2, yy + 2, xx + 58, yy + 58], fill=(214, 226, 236) if (xx // 60 + yy // 60) % 2 else (236, 242, 246))
    p.rr([96, 356, 344, 584], 14, fill=OUT)
    p.rect([104, 364, 336, 576], fill=(30, 40, 80))
    moon(p, 270, 420, 30)
    stars(p, t, [(140, 400), (200, 520), (310, 520), (160, 470)], 3)
    p.rect([216, 364, 224, 576], fill=OUT); p.rect([104, 466, 336, 474], fill=OUT)
    p.rect([0, 1010, 1080, 1170], fill=(150, 110, 80))
    for y in (1060, 1110):
        p.line([(0, y), (1080, y)], (166, 124, 92), 4)

def bedroom(p, t):
    p.rect([0, 300, 1080, 1010], fill=(54, 68, 122))
    for yy in range(340, 1000, 110):
        for xx in range(40 + (55 if (yy // 110) % 2 else 0), 1080, 110):
            k = 0.5 + 0.5 * math.sin(t * 2 + xx * 0.03 + yy)
            p.circle(xx, yy, 5 + 2 * k, fill=(90, 106, 168))
    p.rr([700, 350, 980, 610], 14, fill=OUT)
    p.rect([710, 360, 970, 600], fill=(20, 28, 62))
    moon(p, 900, 430, 36)
    stars(p, t, [(750, 400), (790, 520), (860, 560), (940, 540)], 3)
    p.rect([836, 360, 844, 600], fill=OUT); p.rect([710, 476, 970, 484], fill=OUT)
    p.rect([0, 1010, 1080, 1170], fill=(112, 82, 66))
    # bed: headboard, pillow, duvet
    p.rr([84, 744, 636, 1010], 30, fill=OUT)
    p.rr([90, 750, 630, 1004], 26, fill=(176, 124, 84))
    p.rr([130, 830, 380, 910], 30, fill=(240, 240, 236))
    p.rr([70, 900, 660, 1066], 30, fill=OUT)
    p.rr([76, 906, 654, 1060], 26, fill=(88, 178, 100))
    for k in range(5):
        p.circle(150 + k * 110, 980, 18, fill=(150, 210, 150))

# ---------------- props ----------------
def bubble(p, x, y, k, who, msg, w=470, col=(240, 244, 250)):
    """A chat notification that pops in."""
    if k <= 0: return
    s = eback(clamp(k))
    ww, hh = w * s, 118 * s
    p.rr([x - ww / 2, y - hh / 2, x + ww / 2, y + hh / 2], 26 * s, fill=col, shadow=True)
    if k < 0.9: return
    p.circle(x - w / 2 + 44, y, 26, fill=(120, 210, 140))
    p.text((x - w / 2 + 44, y + 1), who[0], f2("anton", 30), INK)
    p.text((x - w / 2 + 84, y - 24), who, f2("dm", 26), (110, 120, 140), anchor="lm")
    p.text((x - w / 2 + 84, y + 18), msg, f2("dm", 34), INK, anchor="lm")

MSGS = [("BEV, No. 9", "Me first please!"), ("No. 14", "Mine smells of fish"), ("No. 22", "Mine walks about!"),
        ("No. 31", "Leaking. Help!!"), ("No. 40", "Mine won't turn on")]

def toolbox(p, hx, hy, s=1.0):
    """A red toolbox hanging from a hand at (hx, hy)."""
    w, h = 120 * s, 66 * s
    top = hy + 26 * s
    p.line([(hx - 26 * s, top), (hx - 20 * s, hy), (hx + 20 * s, hy), (hx + 26 * s, top)], OUT, 9 * s)
    P.orr(p, [hx - w / 2, top, hx + w / 2, top + h], 10 * s, (214, 64, 56), ow=4, shade_side="r")
    p.rect([hx - w / 2, top + h * .34, hx + w / 2, top + h * .44], fill=(160, 44, 40))
    p.rr([hx - 14 * s, top + 4 * s, hx + 14 * s, top + 16 * s], 4 * s, fill=(200, 200, 210))

def washer(p, cx, yb, s=1.0, t=0.0, shake=0.0, spin=0.0, broken=True):
    """A washing machine. spin 0..1 makes the drum whirl and the light go green."""
    cx = cx + math.sin(t * 40) * 6 * shake
    P.orr(p, [cx - 150 * s, yb - 340 * s, cx + 150 * s, yb], 26 * s, (236, 238, 242), shade_side="r")
    p.rr([cx - 140 * s, yb - 330 * s, cx + 140 * s, yb - 272 * s], 16 * s, fill=(204, 210, 218))
    p.rr([cx - 120 * s, yb - 318 * s, cx - 20 * s, yb - 286 * s], 8 * s, fill=(40, 46, 56))
    if spin > 0:
        p.text((cx - 70 * s, yb - 302 * s), "ON", f2("anton", max(8, int(24 * s))), GREEN)
    elif broken:
        p.text((cx - 70 * s, yb - 302 * s), "OFF", f2("anton", max(8, int(24 * s))), (120, 126, 140))
    P.ocircle(p, cx + 90 * s, yb - 301 * s, 18 * s, GREEN if spin > 0 else (170, 176, 188), ow=3, shaded=False)
    P.ocircle(p, cx, yb - 140 * s, 102 * s, (160, 168, 182), ow=5, shaded=False)
    p.circle(cx, yb - 140 * s, 78 * s, fill=(110, 170, 220))
    p.rect([cx - 78 * s, yb - 140 * s, cx + 78 * s, yb - 62 * s], fill=(90, 150, 205))
    if spin > 0:
        a0 = (t * 720 * spin) % 360
        for k in range(3):
            p.arc([cx - 60 * s, yb - 200 * s, cx + 60 * s, yb - 80 * s], a0 + k * 120, a0 + k * 120 + 60, WHITE, max(3, 9 * s))
        for k in range(4):
            ang = math.radians(a0 * 1.3 + k * 90)
            p.circle(cx + 40 * s * math.cos(ang), yb - 140 * s + 40 * s * math.sin(ang), 9 * s, fill=(255, 140, 160) if k % 2 else YEL)
    else:
        p.arc([cx - 60 * s, yb - 200 * s, cx + 20 * s, yb - 120 * s], 200, 260, WHITE, max(3, 8 * s))

def socket(p, x, y, s=1.0, on=False):
    P.orr(p, [x - 48 * s, y - 48 * s, x + 48 * s, y + 48 * s], 10 * s, (244, 244, 240), ow=4)
    for dx, dy, w, h in ((0, -16, 8, 18), (-18, 14, 18, 8), (18, 14, 18, 8)):
        p.rect([x + (dx - w / 2) * s, y + (dy - h / 2) * s, x + (dx + w / 2) * s, y + (dy + h / 2) * s], fill=OUT)
    p.rr([x + 24 * s, y - 40 * s, x + 40 * s, y - 26 * s], 3 * s, fill=RED if on else (196, 196, 196))

def plug(p, x, y, s=1.0):
    p.rect([x - 6 * s, y - 50 * s, x + 6 * s, y - 30 * s], fill=(190, 160, 80))
    P.orr(p, [x - 30 * s, y - 32 * s, x + 30 * s, y + 30 * s], 10 * s, (250, 250, 248), ow=4)
    p.rect([x - 4 * s, y + 30 * s, x + 4 * s, y + 46 * s], fill=(250, 250, 248))

def cable(p, a, b, sag=80):
    pts = []
    for k in range(13):
        u = k / 12
        pts.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u) + sag * math.sin(math.pi * u)))
    p.line(pts, OUT, 12)
    p.line(pts, (250, 250, 248), 6)

def note(p, x, y, s=1.0, ang=0.0, label="£20", col=(150, 110, 200)):
    w, h = 120 * s, 64 * s
    ca, sa = math.cos(ang), math.sin(ang)
    def rot(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    p.poly([rot(-w / 2 - 4, -h / 2 - 4), rot(w / 2 + 4, -h / 2 - 4), rot(w / 2 + 4, h / 2 + 4), rot(-w / 2 - 4, h / 2 + 4)], OUT)
    p.poly([rot(-w / 2, -h / 2), rot(w / 2, -h / 2), rot(w / 2, h / 2), rot(-w / 2, h / 2)], col)
    p.circle(*rot(-w * .25, 0), h * .28, fill=tint(col))
    p.text(rot(w * .18, 0), label, f2("anton", max(8, int(30 * s))), WHITE)

def tint(c, k=0.3):
    return tuple(int(v + (255 - v) * k) for v in c)

def digital_clock(p, cx, cy, text, t, colour=RED, w=560, h=230, blink=True):
    p.rr([cx - w / 2 - 6, cy - h / 2 - 6, cx + w / 2 + 6, cy + h / 2 + 6], 36, fill=OUT)
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 30, fill=(24, 22, 28))
    if not blink or (t % 1.0) < 0.5 or ":" not in text:
        p.text((cx, cy + 4), text, f2("anton", int(h * 0.8)), colour)
    else:
        a, b = text.split(":")
        p.text((cx, cy + 4), a + " " + b, f2("anton", int(h * 0.8)), colour)

def paw(p, x, y, r, col=INK):
    p.ell([x - r * .62, y - r * .2, x + r * .62, y + r * .55], fill=col)
    for dx, dy in ((-.62, -.52), (-.22, -.86), (.22, -.86), (.62, -.52)):
        p.ell([x + dx * r - r * .2, y + dy * r - r * .26, x + dx * r + r * .2, y + dy * r + r * .2], fill=col)

def kangaroo_ears(p, x, yf, s, t):
    """Alfie's kangaroo costume ears, drawn just before P.alfie so they sit behind his hair."""
    bob = abs(math.sin(t * 3.0)) * 8 * s
    th = 150 * s * (1 + 0.012 * math.sin(t * 2.4))
    top = yf - bob - 110 * s - th
    hr = 70 * s
    hy = top - hr * .82
    brown, inner = (186, 124, 72), (236, 176, 150)
    for sx in (-1, 1):
        wig = math.sin(t * 6 + sx) * 4 * s
        ex = x + sx * hr * .62
        p.ell([ex - 30 * s - 5, hy - hr * 2.25 + wig - 5, ex + 30 * s + 5, hy - hr * .55 + 5], fill=OUT)
        p.ell([ex - 30 * s, hy - hr * 2.25 + wig, ex + 30 * s, hy - hr * .55], fill=brown)
        p.ell([ex - 15 * s, hy - hr * 2.0 + wig, ex + 15 * s, hy - hr * .8], fill=inner)

def kangaroo_alfie(p, x, yf, s, mood, t, wave=0.0, talk=0.0):
    kangaroo_ears(p, x, yf, s, t)
    P.alfie(p, x, yf, s, mood, t, wave=wave, talk=talk)

def book(p, x, y, s=1.0, torn=False):
    p.poly([(x - 110 * s, y - 50 * s), (x, y - 36 * s), (x + 110 * s, y - 50 * s), (x + 116 * s, y + 30 * s), (x, y + 42 * s), (x - 116 * s, y + 30 * s)], OUT)
    p.poly([(x - 102 * s, y - 42 * s), (x - 4 * s, y - 30 * s), (x - 4 * s, y + 32 * s), (x - 106 * s, y + 22 * s)], (250, 248, 238))
    right = [(x + 4 * s, y - 30 * s), (x + 102 * s, y - 42 * s), (x + 106 * s, y + 22 * s), (x + 4 * s, y + 32 * s)]
    if torn:
        right = [(x + 4 * s, y - 30 * s), (x + 50 * s, y - 36 * s), (x + 62 * s, y - 6 * s), (x + 46 * s, y + 8 * s), (x + 70 * s, y + 28 * s), (x + 4 * s, y + 32 * s)]
    p.poly(right, (250, 248, 238))
    for k in range(3):
        p.line([(x - 88 * s, y - 20 * s + k * 16 * s), (x - 20 * s, y - 14 * s + k * 16 * s)], (170, 170, 180), 4 * s)

def scrap(p, x, y, s=1.0, ang=0.2):
    ca, sa = math.cos(ang), math.sin(ang)
    def rot(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    pts = [(-34, -26), (30, -30), (36, 4), (22, 28), (-30, 24)]
    p.poly([rot(px * s * 1.15, py * s * 1.15) for px, py in pts], OUT)
    p.poly([rot(px * s, py * s) for px, py in pts], (250, 248, 238))
    p.text(rot(0, 0), "4", f2("anton", max(8, int(30 * s))), INK)

def rain_cloud(p, x, y, t, s=1.0):
    for dx, dy, r in [(-40, 8, 30), (0, -10, 40), (40, 8, 30), (0, 14, 30)]:
        p.circle(x + dx * s, y + dy * s, r * s + 4, fill=OUT)
    for dx, dy, r in [(-40, 8, 30), (0, -10, 40), (40, 8, 30), (0, 14, 30)]:
        p.circle(x + dx * s, y + dy * s, r * s, fill=(176, 186, 204))
    for k in range(4):
        ph = (t * 1.8 + k * 0.27) % 1
        dx = (-36 + k * 24) * s
        p.line([(x + dx, y + 40 * s + ph * 70 * s), (x + dx - 6 * s, y + 58 * s + ph * 70 * s)], BLUE, max(3, 6 * s))

# ---------------- fixed HUD ----------------
@V.fixed
def hud_band(p, t):
    k = eo(prog(t, V.L(7)[0] + 0.3, V.L(7)[0] + 1.6))
    P.hud(p, DAY, FUND_BEFORE + (FUND - FUND_BEFORE) * k)

def JOB_TIMES():
    """When Dave arrives at each of the 5 houses during line 4."""
    a4, e4 = V.L(4)
    t0, t1 = a4 + 0.1, e4 - 0.1
    return [t0 + (t1 - t0) * k / 4.6 for k in range(5)]

def BUBBLE_TIMES():
    """Five chat notifications pop out of Sue's phone after the title card."""
    a0, e0 = V.L(0)
    t0 = max(2.6, at(0, "Dave fixes") - 0.2)
    return [t0 + k * 0.42 for k in range(5)]

@V.sounds
def sounds(L):
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh")]
    out += [(at(0, "ninety-four"), "pop")]
    out += [(tb, "ding") for tb in BUBBLE_TIMES()]
    a1, e1 = L(1)
    out += [(a1 + 0.2, "pop"), (at(1, "C won") + 1.3, "ding"), (at(1, "went wild"), "boing")]
    a2, e2 = L(2)
    out += [(a2 + 0.3 + k * (e2 - a2 - 0.8) / 5, "pop") for k in range(5)]
    out += [(at(2, "spreadsheet"), "ding")]
    out += [(L(3)[0] + 0.3, "whoosh"), (at(3, "Literally"), "boing")]
    jt = JOB_TIMES()
    out += [(at(4, "Bev"), "pop")] + [(x + 0.55, "ding") for x in jt[:4]]
    out += [(at(4, "eleven"), "thud")]
    out += [(L(5)[0] + 0.1, "boing"), (at(5, "It was") + 0.5, "thud"), (at(5, "unplugged"), "ding")]
    out += [(L(6)[0] + 0.3, "pop"), (at(6, "Four jobs"), "pop"), (at(6, "minus"), "pop"), (at(6, "plus"), "cash")]
    a7, e7 = L(7)
    out += [(a7 + 0.1 + j * 0.2, "pop") for j in range(5)] + [(a7 + 1.4, "cash")]
    out += [(L(8)[0] + 0.2, "pop"), (at(8, "Crumbs"), "boing"), (at(8, "He ate"), "thud")]
    out += [(at(9, "Happiness") + 0.6, "pop"), (at(9, "House"), "pop")]
    out += [(L(10)[0] + 0.1, "ding"), (at(10, "two hundred"), "cash"), (at(10, "tomorrow"), "pop")]
    out += [(L(11)[0] + 0.1, "boing")]
    out += [(L(12)[0] + 0.1, "thud"), (at(12, "school play"), "ding"), (at(12, "kangaroo"), "boing")]
    out += [(at(13, "A:"), "pop"), (at(13, "B:") - 0.1, "pop"), (at(13, "Or C") - 0.1, "pop"), (at(13, "One delay"), "thud")]
    out += [(L(14)[0] + 0.1, "pop"), (at(14, "or Crumbs"), "boing"), (at(14, "Day six"), "ding")]
    return out

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    P.living_room(p, t, 0.03)
    ph = BUBBLE_TIMES()
    buzz = math.sin(t * 50) * 5 if any(0 < t - x < 0.25 for x in ph) else 0
    P.dave(p, 170, 1130, 0.8, "shock" if t > at(0, "Dave fixes") else "neutral", t)
    P.sue(p, 390 + buzz, 1130, 0.82, "grin", t, hold="phone")
    P.ellie(p, 610, 1130, 0.78, "neutral", t)
    P.alfie(p, 800, 1130, 0.78, "grin", t)
    P.crumbs(p, 975, 1130, 0.45, "happy", t)
    # chat notifications burst out of Sue's phone like a feed: newest at the bottom, old ones scroll off the top
    n = sum(eo(prog(t, x, x + 0.3)) for x in ph)
    for k, (who, msg) in enumerate(MSGS):
        q = prog(t, ph[k], ph[k] + 0.3)
        if q <= 0: continue
        y = 650 - 120 * (n - 1 - k)
        if y < 400: continue              # scrolled off the top
        bubble(p, 700, y, q, who, msg)
    tn = at(0, "ninety-four")
    if t > tn:
        pill(p, 250, 600, "94 NEIGHBOURS", prog(t, tn, tn + 0.3), bg=YEL, size=38)
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0, dx = 560, -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.35, 0.7)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "DAY 5", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "£200 OR THE KANGAROO?", f2("anton", max(10, int(86 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "YOU VOTED C. NOW THE WHOLE STREET WANTS DAD.", f2("dm", max(8, int(36 * k3))), (255, 160, 190))

@V.scene(1)
def result(p, t, L):
    a1, e1 = L(1)
    p.text((540, 360), "YOUR VOTES", f2("anton", 72), YEL)
    P.result_bars(p, t, a1 - 0.1, VOTES, top=440)
    labels = ["FIX IT FOR FREE", "CHARGE BEV £40", "POST IN THE STREET CHAT"]
    total = sum(VOTES.values())
    for i, lab in enumerate(labels):
        k = prog(t, a1 + 0.2 + i * 0.2, a1 + 0.5 + i * 0.2)
        if k > 0:
            w = len(lab) * 34 * 0.6 + 40
            p.rr([540 - w / 2, 440 + i * 150 + 30, 540 + w / 2, 440 + i * 150 + 80], 25, fill=(20, 30, 50))
            p.text((540, 440 + i * 150 + 55), lab, f2("dm", 34), WHITE)
    pill(p, 540, 940, "C WINS: 2 VOTES TO 1", prog(t, a1 + 1.3, a1 + 1.6), bg=P.OPT_COLS["C"], size=44)
    tw = at(1, "went wild")
    if t > tw:
        # little chat bubbles fizz up around the pill
        for j in range(8):
            q = ((t - tw) * 0.9 + j / 8) % 1
            x = 140 + j * 115
            y = 1130 - 120 * q
            r = 22 * (1 - q * 0.4)
            p.rr([x - r * 1.4, y - r, x + r * 1.4, y + r], r * .8, fill=(120, 210, 140) if j % 2 else WHITE)
            p.poly([(x - r * .6, y + r - 2), (x - r * .9, y + r * 1.6), (x, y + r - 2)], (120, 210, 140) if j % 2 else WHITE)

@V.scene(2, 3)
def bookings(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3)
    P.living_room(p, t, 0.03)
    if t < a3 - 0.2:
        k = eback(prog(t, a2 - 0.25, a2 + 0.15))
        P.sue(p, 290, 1140, 1.05 * max(0.01, k), "grin", t, hold="phone", talk=V.talk(t, "sue"))
        # Sue's colour-coded spreadsheet fills up
        c = eback(prog(t, a2 - 0.1, a2 + 0.3))
        if c > 0:
            x0, y0, x1, y1 = 540, 350, 1000, 350 + 560 * c
            p.rr([x0, y0, x1, y1], 24, fill=WHITE, shadow=True)
            if c > 0.9:
                p.rr([x0, y0, x1, y0 + 80], 24, fill=(70, 160, 100))
                p.text(((x0 + x1) / 2, y0 + 42), "DAVE'S JOBS TONIGHT", f2("anton", 40), WHITE)
                rows = [("6PM", "BEV, No. 9"), ("7PM", "No. 14"), ("8PM", "No. 22"), ("9PM", "No. 31"), ("10PM", "No. 40")]
                cols = [(255, 214, 120), (180, 220, 255), (255, 190, 210), (200, 240, 190), (230, 210, 255)]
                for i, (tm, who) in enumerate(rows):
                    q = eback(prog(t, a2 + 0.3 + i * (e2 - a2 - 0.8) / 5, a2 + 0.6 + i * (e2 - a2 - 0.8) / 5))
                    if q <= 0: continue
                    y = y0 + 100 + i * 88
                    p.rr([x0 + 20, y, x0 + 20 + (x1 - x0 - 40) * q, y + 72], 14, fill=cols[i])
                    if q > 0.9:
                        p.text((x0 + 44, y + 37), tm, f2("anton", 38), INK, anchor="lm")
                        p.text((x0 + 170, y + 37), who, f2("dm", 36), INK, anchor="lm")
                        tick(p, x1 - 56, y + 36, 24, prog(t, at(2, "spreadsheet"), at(2, "spreadsheet") + 0.3))
        tb = at(2, "in ten")
        pill(p, 770, 980, "5 BOOKINGS IN 10 MIN", prog(t, tb, tb + 0.3), bg=YEL, size=36)
        return
    # Ellie: Dad is out-mentioning her in the chat
    k = eback(prog(t, a3 - 0.2, a3 + 0.2))
    P.ellie(p, 300, 1140, 1.05 * max(0.01, k), "worried", t, talk=V.talk(t, "ellie"))
    c = eback(prog(t, a3, a3 + 0.4))
    if c > 0:
        x0, y0, x1, y1 = 540, 380, 1000, 380 + 400 * c
        p.rr([x0, y0, x1, y1], 30, fill=(20, 30, 50), shadow=True)
        if c > 0.9:
            p.text(((x0 + x1) / 2, y0 + 56), "MENTIONS IN THE CHAT", f2("anton", 40), YEL)
            g = eo(prog(t, a3 + 0.5, a3 + 1.8))
            n = int(round(37 * g))
            p.text((x0 + 30, y0 + 150), "DAD", f2("anton", 44), WHITE, anchor="lm")
            p.rr([x0 + 150, y0 + 124, x0 + 150 + max(30, 220 * g), y0 + 176], 26, fill=BLUE)
            p.text((x1 - 30, y0 + 150), str(n), f2("anton", 50), BLUE, anchor="rm")
            p.text((x0 + 30, y0 + 270), "ELLIE", f2("anton", 44), WHITE, anchor="lm")
            p.rr([x0 + 170, y0 + 244, x0 + 200, y0 + 296], 26, fill=(200, 170, 255))
            p.text((x1 - 30, y0 + 270), "0", f2("anton", 50), (200, 170, 255), anchor="rm")
    tl = at(3, "Literally")
    pill(p, 770, 900, "LITERALLY EMBARRASSING", prog(t, tl, tl + 0.3), bg=(200, 170, 255), size=34)

@V.scene(4, 6)
def rounds(p, t, L):
    a4, e4 = L(4); a5, e5 = L(5); a6, e6 = L(6)
    jt = JOB_TIMES()
    if t < a5 - 0.2:
        n = sum(1 for x in jt if t >= x)
        street(p, t, lit=n, ticks={i: prog(t, jt[i] + 0.55, jt[i] + 0.8) for i in range(4)})
        # Bev waves from her doorstep
        tb = at(4, "Bev")
        bev(p, 112, 1150, 0.5, "happy", t, wave=1 if t > tb else 0)
        # Dave goes door to door with his toolbox
        stops = [HOUSES[i][0] + (70 if i < 4 else -70) for i in range(5)]
        x = stops[0]
        for i in range(1, 5):
            x = lerp(x, stops[i], eio(prog(t, jt[i] - 0.45, jt[i] - 0.05)))
        moving = any(jt[i] - 0.45 < t < jt[i] - 0.05 for i in range(1, 5))
        bob = abs(math.sin(t * 9)) * 8 if moving else 0
        mood = "happy" if n <= 2 else "tired"
        k = eback(prog(t, a4 - 0.3, a4 + 0.1))
        s = 0.62 * max(0.01, k)
        toolbox(p, *hand(x, 1150 - bob, s, t, DAVE_DIMS, "l"), s=s)
        P.dave(p, x, 1150 - bob, s, mood, t, hold="wrench")
        mins = int(300 * prog(t, a4 + 0.1, e4 - 0.1))
        digital_clock(p, 210, 380, f"{18 + mins // 60:02d}:{mins % 60:02d}", t, colour=GREEN, w=280, h=120, blink=False)
        if t > tb:
            pill(p, 600, 380, "FIRST UP: BEV", prog(t, tb, tb + 0.3), bg=YEL, size=36)
        return
    if t < a6 - 0.2:
        # No. 40: the machine that "won't turn on"
        kitchen(p, t)
        tw = at(5, "It was")
        q = eio(prog(t, tw, tw + 0.45))
        on = q >= 1
        hx, hy = hand(250, 1140, 0.95 * max(0.01, eback(prog(t, a5 - 0.25, a5 + 0.15))), t, DAVE_DIMS, "r")
        px, py = lerp(hx + 10, 950, q), lerp(hy - 20, 860 - 40 * math.sin(math.pi * q), q)
        cable(p, (700, 960), (px, py + 40), sag=30)       # runs from behind the machine
        washer(p, 700, 1130, 1.1, t, spin=prog(t, tw + 0.45, tw + 0.75))
        socket(p, 950, 880, 1.0, on=on)
        k = eback(prog(t, a5 - 0.25, a5 + 0.15))
        s = 0.95 * max(0.01, k)
        P.dave(p, 250, 1140, s, "shock" if t < tw else "grin", t, talk=V.talk(t, "dave"))
        plug(p, px, py, 1.0)
        tu = at(5, "unplugged")
        if t > tu:
            pill(p, 540, 400, "IT WAS UNPLUGGED", prog(t, tu, tu + 0.3), bg=RED, fg=WHITE, size=48)
            for j in range(5):
                ang = t * 3 + j * 1.26
                sparkle(p, 700 + 190 * math.cos(ang), 990 + 120 * math.sin(ang), 14, fill=WHITE)
        return
    # tonight's takings
    street(p, t, lit=5, ticks={i: 1.0 for i in range(5)})
    toolbox(p, *hand(900, 1150, 0.62, t, DAVE_DIMS, "l"), s=0.62)
    P.dave(p, 900, 1150, 0.62, "tired", t)
    c = eback(prog(t, a6 - 0.1, a6 + 0.3))
    if c > 0:
        x0, y0, x1 = 70, 380, 730
        y1 = y0 + 480 * c
        p.rr([x0, y0, x1, y1], 26, fill=(250, 248, 238), shadow=True)
        if c > 0.9:
            p.text(((x0 + x1) / 2, y0 + 50), "TONIGHT'S TAKINGS", f2("anton", 46), INK)
            p.line([(x0 + 30, y0 + 92), (x1 - 30, y0 + 92)], (190, 186, 176), 4)
            rows = [(a6 + 0.3, "No. 40: UNPLUGGED", "£0", (130, 130, 140)),
                    (at(6, "Four jobs"), "4 JOBS × £30", "£120", INK),
                    (at(6, "minus"), "PARTS", "-£15", RED)]
            for i, (tr, lab, val, col) in enumerate(rows):
                q = eback(prog(t, tr, tr + 0.3))
                if q <= 0: continue
                y = y0 + 145 + i * 80
                p.text((x0 + 40, y), lab, f2("dm", int(38 * q) + 1), col, anchor="lm")
                p.text((x1 - 40, y), val, f2("anton", int(46 * q) + 1), col, anchor="rm")
            if t > at(6, "minus"):
                p.line([(x0 + 30, y0 + 372), (x1 - 30, y0 + 372)], INK, 5)
            tp = at(6, "plus")
            q = eback(prog(t, tp, tp + 0.35))
            if q > 0:
                p.text((x0 + 40, y0 + 425), "TOTAL", f2("anton", int(50 * q) + 1), INK, anchor="lm")
                p.text((x1 - 40, y0 + 425), "+£105", f2("anton", int(64 * q) + 1), (30, 160, 90), anchor="rm")

BEV_JUMPER, BEV_TROUSERS, BEV_BOOTS = (92, 140, 74), (112, 86, 62), (52, 96, 62)
BEV_HAT, BEV_HAIR = (240, 130, 50), (196, 196, 204)

def bev(p, x, yf, s=1.0, mood="happy", t=0.0, wave=0.0):
    """Bev the gardener (same design as Day 4): green jumper, wellies, grey curls, orange bobble hat."""
    bob = math.sin(t * 2.0 + 0.5) * 4 * s
    top = P._body(p, x, yf, s, BEV_JUMPER, BEV_TROUSERS, 210 * s, 220 * s, 150 * s, wave=wave, t=t, shoe=BEV_BOOTS)
    p.line([(x, top + 10 * s), (x, yf - 150 * s)], P.shade(BEV_JUMPER, .75), 5 * s)
    for sx in (-1, 1):
        p.rr([x + sx * 55 * s - 26 * s, top + 120 * s, x + sx * 55 * s + 26 * s, top + 160 * s], 8 * s, fill=P.shade(BEV_JUMPER, .85))
    hr = 80 * s
    hy = top - hr * .82 + bob
    for sx in (-1, 1):
        P.ocircle(p, x + sx * hr * .92, hy + hr * .1, hr * .3, BEV_HAIR, ow=4, shaded=False)
    P._head(p, x, hy, hr, mood, t, 1.9, ears=False, iris=(90, 70, 50))
    p.d.chord([(x - hr * 1.06) * S, (hy - hr * 1.12) * S, (x + hr * 1.06) * S, (hy + hr * .3) * S], 180, 360, fill=OUT)
    p.d.chord([(x - hr) * S, (hy - hr * 1.06) * S, (x + hr) * S, (hy + hr * .24) * S], 180, 360, fill=BEV_HAT)
    P.orr(p, [x - hr * 1.04, hy - hr * .5, x + hr * 1.04, hy - hr * .26], hr * .1, P.shade(BEV_HAT, .85), ow=4)
    for k in range(4):
        p.line([(x - hr * .6 + k * hr * .4, hy - hr * .95), (x - hr * .6 + k * hr * .4, hy - hr * .55)], P.shade(BEV_HAT, .88), max(3, hr * .06))
    P.ocircle(p, x, hy - hr * 1.12, hr * .24, WHITE, ow=4)

@V.scene(7, 9)
def money(p, t, L):
    a7, e7 = L(7); a8, e8 = L(8); a9, e9 = L(9)
    if t < a8 - 0.2:
        lv = lerp(FUND_BEFORE, FUND, eo(prog(t, a7 + 0.3, a7 + 1.6))) / 1000
        P.jar(p, 300, 1090, 2.4, lv)
        p.text((300, 1135), "HOLIDAY JAR", f2("dm", 34), WHITE)
        for j in range(5):   # five £20 notes and a fiver fly into the jar
            q = prog(t, a7 + 0.05 + j * 0.2, a7 + 0.85 + j * 0.2)
            if 0 < q < 1:
                x = lerp(1150, 300, eo(q)); y = lerp(480, 800, eo(q)) - 140 * math.sin(math.pi * q)
                if j < 4:
                    note(p, x, y, 1.1, ang=q * 3 + j)
                else:
                    note(p, x, y, 1.0, ang=q * 3 + j, label="£5", col=(60, 170, 150))
        big_number(p, t, a7 + 0.3, 133, cx=740, cy=700, size=250, start=28, dur=1.3, fill=GREEN, fmt="£{}")
        P.money_pop(p, t, a7 + 0.2, "+£105", x=740, y=520, colour=GREEN)
        tb = a7 + 1.4
        pill(p, 540, 400, "BEST NIGHT YET", prog(t, tb, tb + 0.3), bg=YEL, size=44)
        pill(p, 740, 900, "£867 STILL TO GO", prog(t, tb + 0.3, tb + 0.6), bg=WHITE, size=36)
        return
    if t < a9 - 0.2:
        bedroom(p, t)
        tc, te = at(8, "Crumbs"), at(8, "He ate")
        k = eback(prog(t, a8 - 0.25, a8 + 0.15))
        P.alfie(p, 300, 1150, 1.05 * max(0.01, k), "sad" if t < te else "grin", t, talk=V.talk(t, "alfie"))
        if t > tc - 0.2:
            cx = lerp(1200, 840, eo(prog(t, tc - 0.2, tc + 0.4)))
            book(p, cx - 230, 1110, 1.0, torn=t > te)
            P.crumbs(p, cx, 1150, 0.7, "happy", t)
            if t > te:
                # page 4 in Crumbs' mouth
                hx, hy = cx - 110 * 0.7, 1150 - 190 * 0.7
                scrap(p, hx + 8, hy + 52 + 3 * math.sin(t * 10), 1.1, ang=0.25 + 0.15 * math.sin(t * 10))
                pill(p, 600, 400, "PAGE 4: EATEN", prog(t, te, te + 0.3), bg=RED, fg=WHITE, size=44)
        td = at(8, "Dad missed")
        if t < tc:
            pill(p, 600, 400, "DAD: STILL AT No. 31", prog(t, td + 0.3, td + 0.6), bg=YEL, size=38)
        return
    P.stats_panel(p, t, a9 - 0.2, [("MONEY", 13.3, GREEN, "£133.00"), ("HAPPINESS", 45, YEL, "45/100"), ("HOUSE", 65, ORANGE, "65/100")])
    th = at(9, "Happiness") + 0.6
    pill(p, 540, 1010, "HAPPINESS -10: DAD WORKED TILL 11", prog(t, th, th + 0.3), bg=YEL, size=34)
    tp = at(9, "House")
    pill(p, 540, 1100, "HOUSE: NO CHANGE", prog(t, tp, tp + 0.3), bg=WHITE, size=34)

@V.scene(10, 12)
def twist(p, t, L):
    a10, e10 = L(10); a11, e11 = L(11); a12, e12 = L(12)
    if t < a11 - 0.2:
        p.text((540, 360), "NEW MESSAGE", f2("anton", 60), YEL)
        k = eback(prog(t, a10 - 0.2, a10 + 0.3))
        if k <= 0: return
        buzz = math.sin(t * 50) * 6 * (1 - prog(t, a10, a10 + 0.6))
        cx, cy = 540 + buzz, 760
        w, h = 520 * k, 700 * k
        p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 60 * k, fill=(30, 34, 44), shadow=True)
        p.rr([cx - w / 2 + 18, cy - h / 2 + 18, cx + w / 2 - 18, cy + h / 2 - 18], 46 * k, fill=(240, 244, 250))
        if k < 0.95: return
        p.rr([cx - 242, cy - 332, cx + 242, cy - 240], 40, fill=(70, 160, 100))
        p.text((cx, cy - 286), "STREET CHAT (94)", f2("dm", 34), WHITE)
        tm = at(10, "The launderette")
        if t < tm:
            for j in range(3):   # typing dots
                p.circle(cx - 150 + j * 40, cy - 150, 12 + 4 * math.sin(t * 10 - j), fill=(150, 160, 176))
            return
        p.text((cx - 200, cy - 190), "LAUNDERETTE, HIGH ST", f2("dm", 26), (110, 120, 140), anchor="lm")
        rows = [("10 machines broken.", at(10, "ten")), ("£200 to fix them,", at(10, "two hundred")), ("tomorrow at 2pm?", at(10, "tomorrow"))]
        q0 = eback(prog(t, tm, tm + 0.3))
        p.rr([cx - 210, cy - 160, cx - 210 + 420 * q0, cy + 100], 30, fill=(120, 210, 140))
        for j, (txt, tr) in enumerate(rows):
            if t > tr:
                p.text((cx - 186, cy - 110 + j * 80), txt, f2("dm", 38), INK, anchor="lm")
        t2 = at(10, "two hundred")
        if t > t2:
            pill(p, 540, 940, "£200", prog(t, t2, t2 + 0.3), bg=GREEN, size=56)
        t3 = at(10, "tomorrow")
        if t > t3:
            pill(p, 540, 1035, "TOMORROW 2PM", prog(t, t3, t3 + 0.3), bg=YEL, size=40)
        return
    P.living_room(p, t, 0.133)
    if t < a12 - 0.2:
        k = eback(prog(t, a11 - 0.25, a11 + 0.15))
        P.dave(p, 300, 1140, 1.0 * max(0.01, k), "grin", t, wave=1, hold="wrench", talk=V.talk(t, "dave"))
        pill(p, 720, 400, "£200 = 3 x SKEGNESS", prog(t, at(11, "That's"), at(11, "That's") + 0.3), bg=YEL, size=40)
        ts = at(11, "three trips")
        for j in range(3):
            q = eback(prog(t, ts + j * 0.2, ts + 0.3 + j * 0.2))
            if q > 0:
                rain_cloud(p, 640 + j * 140, 720 + 12 * math.sin(t * 2 + j), t, 0.85 * q)
        if t > ts:
            pill(p, 780, 880, "(IT RAINED)", prog(t, ts + 0.8, ts + 1.1), bg=WHITE, size=30)
        return
    # the clash: Alfie's school play, same time
    k = eback(prog(t, a12 - 0.25, a12 + 0.15))
    s = 1.12 * max(0.01, k)
    kangaroo_alfie(p, 540, 1150, s, "shock" if t < at(12, "I'm the") else "grin", t,
                   wave=1 if t > at(12, "I'm the") else 0, talk=V.talk(t, "alfie"))
    c1 = eback(prog(t, a12, a12 + 0.3))
    c2 = eback(prog(t, at(12, "school play"), at(12, "school play") + 0.3))
    if c1 > 0:
        digital_clock(p, 270, 420, "14:00", t, colour=BLUE, w=260 * c1, h=110 * c1, blink=False)
        pill(p, 270, 515, "LAUNDERETTE", prog(t, a12 + 0.2, a12 + 0.5), bg=(20, 30, 50), fg=BLUE, size=28)
    if c2 > 0:
        digital_clock(p, 810, 420, "14:00", t, colour=YEL, w=260 * c2, h=110 * c2, blink=False)
        pill(p, 810, 515, "SCHOOL PLAY", prog(t, at(12, "school play") + 0.2, at(12, "school play") + 0.5), bg=(20, 30, 50), fg=YEL, size=28)
        sh = math.sin(t * 30) * 5 * (1 - prog(t, at(12, "school play") + 0.3, at(12, "school play") + 0.9))
        pill(p, 540 + sh, 420, "CLASH!", prog(t, at(12, "school play") + 0.2, at(12, "school play") + 0.5), bg=RED, fg=WHITE, size=40)
    tk = at(12, "kangaroo")
    if t > tk:
        pill(p, 540, 590, "STARRING ALFIE AS THE KANGAROO", prog(t, tk, tk + 0.3), bg=GREEN, size=32)

@V.scene(13, 14)
def vote(p, t, L):
    a13, e13 = L(13); a14, _ = L(14)
    if t < a14 - 0.2:
        tA, tB, tC = at(13, "A:"), at(13, "B:"), at(13, "Or C")
        P.vote_card(p, t, tA - 0.6, "DAVE'S BIG CHOICE?", OPTIONS, gap=(tC - tA) / 2)
        td = at(13, "One delay")
        if t > td:
            pill(p, 870, 975, "RISKY!", prog(t, td, td + 0.3), bg=RED, fg=WHITE, size=34)
        return
    P.living_room(p, t, 0.133)
    m = {"dave": "worried", "sue": "happy", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}
    xs, yf, sc = (170, 390, 610, 800, 975), 1130, 0.82
    P.sue(p, xs[1], yf, sc, m["sue"], t, hold="phone")
    P.dave(p, xs[0], yf, sc, m["dave"], t, hold="wrench")
    P.ellie(p, xs[2], yf, sc * .95, m["ellie"], t)
    kangaroo_alfie(p, xs[3], yf, sc * .95, m["alfie"], t)
    P.crumbs(p, xs[4], yf, sc * .55, m["crumbs"], t)
    pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a14 + 0.1, a14 + 0.5), bg=WHITE, size=54)
    tcr = at(14, "or Crumbs")
    if t > tcr:
        pill(p, 540, 490, "OR CRUMBS CHOOSES AGAIN", prog(t, tcr, tcr + 0.3), bg=RED, fg=WHITE, size=36)
    td = at(14, "Day six")
    pill(p, 540, 580, "DAY 6 TOMORROW", prog(t, td, td + 0.4), bg=YEL, size=40)

if __name__ == "__main__":
    V.main()
