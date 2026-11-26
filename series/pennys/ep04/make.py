import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

DAY = 4
FUND_BEFORE = 88.00
FUND = 28.00          # nobody voted, Crumbs chose C: the gardener cost £60 (88 - 60)
VOTES = {"A": 0, "B": 0, "C": 0}

SCRIPT = [
    # (speaker, spoken text, caption text)
    ("narrator", "Yesterday, nobody voted. So Crumbs chose. And he chose the expensive one.", "Yesterday, *nobody* voted. So *Crumbs* chose. And he chose the *expensive* one."),
    ("narrator", "Zero votes. So Crumbs sat on C: pay a gardener sixty pounds.", "*Zero* votes. So Crumbs sat on *C*: pay a gardener *£60*."),
    ("narrator", "Nine in the morning. Bev the gardener arrived, with a wheelbarrow and a very big spade.", "*9am*. Bev the gardener arrived, with a *wheelbarrow* and a very *big spade*."),
    ("dave", "Sixty quid? I could have done that myself!", "*£60*? I could have done that *myself!*"),
    ("sue", "Dave, you fell asleep in your cornflakes.", "Dave, you fell *asleep* in your *cornflakes*."),
    ("narrator", "Two hours later: fourteen holes filled, and fresh grass seed down.", "*2 hours* later: *14 holes* filled, and fresh *grass seed* down."),
    ("ellie", "The neighbours stopped staring. I can literally go outside again.", "The neighbours stopped *staring*. I can *literally* go outside again."),
    ("alfie", "Goodbye, tunnel to Australia. I'll miss you.", "Goodbye, *tunnel* to *Australia*. I'll *miss* you."),
    ("narrator", "But the fund drops to twenty-eight pounds. Nearly back to day one.", "But the fund drops to *£28*. Nearly back to *day 1*."),
    ("narrator", "The house jumps to sixty-five out of a hundred. Happiness: fifty-five.", "The house jumps to *65/100*. Happiness: *55/100*."),
    ("narrator", "Then Bev spotted Dave's overalls. Her washing machine has been broken for a month.", "Then Bev spotted Dave's *overalls*. Her *washing machine* has been broken for a *month*."),
    ("dave", "Washing machines? That's my thing!", "Washing machines? That's *my thing!*"),
    ("narrator", "So what should the Pennys do?", "So what should the Pennys *do*?"),
    ("narrator", "A: fix it for free, as a thank you. B: charge her forty pounds. Or C: Sue posts Dave's repairs in the street group chat. Thirty pounds a job, but there go his evenings.", "*A*: fix it for *free*, as a thank you. *B*: charge her *£40*. Or *C*: Sue posts Dave's repairs in the street *group chat*. *£30 a job*, but there go his *evenings*."),
    ("sue", "The street chat has ninety-four people. Nobody leaves.", "The street chat has *94 people*. *Nobody* leaves."),
    ("narrator", "Comment A, B or C, or Crumbs chooses again. Day five, tomorrow. Follow, to see if they make it.", "Comment *A*, *B* or *C*, or *Crumbs* chooses again. *Day 5*, tomorrow. Follow, to see if they make it."),
]

V = Video(
    "pennys-ep04", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS,
    lines=[(sp, txt) for sp, txt, _ in SCRIPT],
    display=[cap for _, _, cap in SCRIPT],
)

OPTIONS = [("A", "Fix it for free", "FREE   HAPPINESS +   BEV OWES THEM"),
           ("B", "Charge Bev £40", "+£40   A BIT AWKWARD"),
           ("C", "Advertise in street chat", "£30 A JOB?   DAVE'S EVENINGS GONE")]

OUT = P.OUT

def at(i, sub):
    """Approximate time the substring `sub` starts in spoken line i (by character position)."""
    a, b = V.L(i)
    txt = V.lines[i][1]
    k = txt.find(sub)
    return a + (b - a) * max(0, k) / max(1, len(txt))

def mix(c1, c2, k):
    return tuple(int(c1[j] + (c2[j] - c1[j]) * k) for j in range(3))

# ---------------- the garden (same garden as Day 3, now in daylight) ----------------
C = dict(sky_t=(120, 190, 240), sky_b=(190, 228, 250), fence=(170, 120, 80), fence_l=(186, 134, 90), fence_d=(140, 96, 62),
         grass=(110, 180, 100), grass_d=(92, 160, 86), soil=(120, 82, 52), soil_d=(96, 64, 40), hole=(64, 42, 28))
HOLES = [(150, 880), (420, 872), (690, 886), (860, 902),
         (260, 975), (540, 985), (810, 992), (120, 1050),
         (380, 1062), (660, 1070), (880, 1090), (230, 1122), (500, 1128), (760, 1124)]
FILL = [7, 2, 11, 0, 9, 4, 13, 5, 1, 10, 3, 12, 6, 8]     # the order Bev fills them in

def sky(p, top, bot, y0=300, y1=700):
    n = 10
    for i in range(n):
        c = mix(top, bot, i / (n - 1))
        p.rect([0, y0 + (y1 - y0) * i / n, 1080, y0 + (y1 - y0) * (i + 1) / n + 1], fill=c)

def cloud(p, x, y, s=1.0, col=(250, 252, 255)):
    for dx, dy, r in [(-60, 10, 46), (0, -14, 60), (60, 10, 46), (0, 20, 46)]:
        p.circle(x + dx * s, y + dy * s, r * s, fill=col)

def neighbour_head(p, x, y, kind, t, i, smile=False):
    y = y + 6 * math.sin(t * 2.2 + i)
    skin = [(236, 190, 150), (198, 140, 100), (150, 104, 74)][i % 3]
    p.circle(x, y, 54, fill=OUT)
    p.circle(x, y, 49, fill=skin)
    if kind == "bun":
        p.circle(x, y - 54, 26, fill=(200, 200, 206))
        p.ell([x - 52, y - 50, x + 52, y - 8], fill=(200, 200, 206))
    elif kind == "cap":
        p.ell([x - 52, y - 54, x + 52, y - 4], fill=(70, 120, 200))
        p.rr([x - 4, y - 22, x + 76, y - 8], 7, fill=(56, 100, 170))
    else:
        p.arc([x - 50, y - 50, x + 50, y + 10], 200, 340, (90, 70, 60), 10)
    for sx in (-1, 1):
        p.circle(x + sx * 17, y + 4, 11, fill=WHITE)
        p.circle(x + sx * 17, y + 9, 6, fill=INK)

def hole(p, x, y, s=1.0):
    p.ell([x + 24 * s, y - 50 * s, x + 128 * s, y + 4 * s], fill=C["soil_d"])
    p.ell([x + 32 * s, y - 58 * s, x + 120 * s, y - 6 * s], fill=C["soil"])
    p.ell([x - 66 * s, y - 24 * s, x + 66 * s, y + 24 * s], fill=C["soil_d"])
    p.ell([x - 56 * s, y - 17 * s, x + 56 * s, y + 15 * s], fill=C["hole"])

def patch(p, x, y, sprout=0.0, pop=1.0):
    """A filled-in hole: flat fresh soil with grass seed, sprouting later."""
    s = 0.7 + 0.3 * eback(clamp(pop))
    p.ell([x - 70 * s, y - 24 * s, x + 70 * s, y + 24 * s], fill=C["soil_d"])
    p.ell([x - 60 * s, y - 18 * s, x + 60 * s, y + 16 * s], fill=C["soil"])
    for k in range(6):
        p.circle(x - 40 + k * 16, y - 6 + ((k * 7) % 3) * 6, 3.5, fill=(236, 220, 170))
    if sprout > 0:
        for k in range(5):
            gx = x - 40 + k * 20
            p.line([(gx, y + 6), (gx - 4, y + 6 - 18 * sprout)], C["grass_d"], 4)

def garden(p, t, holes=14, filled=0, neighbours=0, sink=0.0, sprout=0.0, fill_t=None):
    sky(p, C["sky_t"], C["sky_b"])
    p.circle(960, 380, 44, fill=YEL)
    cloud(p, (200 + t * 14) % 1300 - 110, 460, 0.7)
    for i, (nx, kind) in enumerate([(250, "bun"), (560, "cap"), (840, "bald")][:neighbours]):
        if sink < 1:
            neighbour_head(p, nx, 532 + 140 * eio(clamp(sink * 1.4 - i * 0.2)), kind, t, i)
    p.rect([0, 600, 1080, 820], fill=C["fence"])
    for i in range(0, 1080, 72):
        p.rect([i, 590, i + 64, 820], fill=C["fence_l"])
        p.poly([(i, 590), (i + 32, 566), (i + 64, 590)], C["fence_l"])
        p.line([(i + 66, 600), (i + 66, 820)], C["fence_d"], 6)
    p.rect([0, 680, 1080, 694], fill=C["fence_d"])
    p.rect([0, 800, 1080, 1170], fill=C["grass"])
    for i in range(16):
        gx = (i * 83) % 1080 + 20
        gy = 840 + (i * 57) % 300
        p.line([(gx, gy), (gx - 6, gy - 16)], C["grass_d"], 4)
        p.line([(gx + 8, gy), (gx + 10, gy - 18)], C["grass_d"], 4)
    done = set(FILL[:filled])
    for i in range(min(holes, len(HOLES))):
        x, y = HOLES[i]
        if i in done:
            pop = 1.0 if fill_t is None else prog(t, fill_t[i], fill_t[i] + 0.25)
            patch(p, x, y, sprout, pop)
        else:
            hole(p, x, y)

# ---------------- props ----------------
def spade(p, x, yb, s=1.0, lift=0.0):
    yb = yb - lift
    P.oline(p, (x, yb - 60 * s), (x, yb - 270 * s), (176, 124, 72), 12 * s, ow=4)
    p.rr([x - 30 * s - 4, yb - 290 * s - 4, x + 30 * s + 4, yb - 268 * s + 4], 8 * s, fill=OUT)
    p.rr([x - 30 * s, yb - 290 * s, x + 30 * s, yb - 268 * s], 6 * s, fill=(176, 124, 72))
    blade = [(x - 34 * s, yb - 74 * s), (x + 34 * s, yb - 74 * s), (x + 30 * s, yb - 10 * s), (x, yb + 8 * s), (x - 30 * s, yb - 10 * s)]
    big = [(x - 40 * s, yb - 80 * s), (x + 40 * s, yb - 80 * s), (x + 36 * s, yb - 7 * s), (x, yb + 15 * s), (x - 36 * s, yb - 7 * s)]
    p.poly(big, OUT)
    p.poly(blade, (184, 190, 200))
    p.line([(x - 18 * s, yb - 62 * s), (x - 16 * s, yb - 20 * s)], (220, 224, 230), 5 * s)

BEV_JUMPER, BEV_TROUSERS, BEV_BOOTS = (92, 140, 74), (112, 86, 62), (52, 96, 62)
BEV_HAT, BEV_HAIR = (240, 130, 50), (196, 196, 204)

def bev_hand(x, yf, s, t, side="l"):
    """Where Bev's resting left (or right) hand is (matches pennys._body)."""
    tw, th, lh = 210 * s, 220 * s * (1 + 0.012 * math.sin(t * 2.4)), 150 * s
    top = yf - lh - th
    aw = tw * .18
    if side == "l":
        return x - tw / 2 - aw * .55, top + th * .8
    return x + tw / 2 + aw * .55, top + th * .8

def bev(p, x, yf, s=1.0, mood="happy", t=0.0, wave=0.0):
    """Bev the gardener: green jumper, wellies, grey hair and an orange bobble hat."""
    bob = math.sin(t * 2.0 + 0.5) * 4 * s
    top = P._body(p, x, yf, s, BEV_JUMPER, BEV_TROUSERS, 210 * s, 220 * s, 150 * s, wave=wave, t=t, shoe=BEV_BOOTS)
    # body warmer zip and pockets
    p.line([(x, top + 10 * s), (x, yf - 150 * s)], P.shade(BEV_JUMPER, .75), 5 * s)
    for sx in (-1, 1):
        p.rr([x + sx * 55 * s - 26 * s, top + 120 * s, x + sx * 55 * s + 26 * s, top + 160 * s], 8 * s, fill=P.shade(BEV_JUMPER, .85))
    hr = 80 * s
    hy = top - hr * .82 + bob
    for sx in (-1, 1):   # grey curls under the hat
        P.ocircle(p, x + sx * hr * .92, hy + hr * .1, hr * .3, BEV_HAIR, ow=4, shaded=False)
    P._head(p, x, hy, hr, mood, t, 1.9, ears=False, iris=(90, 70, 50))
    # bobble hat
    p.d.chord([(x - hr * 1.06) * S, (hy - hr * 1.12) * S, (x + hr * 1.06) * S, (hy + hr * .3) * S], 180, 360, fill=OUT)
    p.d.chord([(x - hr) * S, (hy - hr * 1.06) * S, (x + hr) * S, (hy + hr * .24) * S], 180, 360, fill=BEV_HAT)
    P.orr(p, [x - hr * 1.04, hy - hr * .5, x + hr * 1.04, hy - hr * .26], hr * .1, P.shade(BEV_HAT, .85), ow=4)
    for k in range(4):
        p.line([(x - hr * .6 + k * hr * .4, hy - hr * .95), (x - hr * .6 + k * hr * .4, hy - hr * .55)], P.shade(BEV_HAT, .88), max(3, hr * .06))
    P.ocircle(p, x, hy - hr * 1.12, hr * .24, WHITE, ow=4)

def wheelbarrow(p, x, yb, s=1.0, hand=None, load=True, with_spade=True):
    red, red_d = (210, 70, 60), (170, 52, 44)
    if with_spade:
        spade(p, x - 30 * s, yb - 120 * s, 0.75 * s)
    if load:
        p.ell([x - 150 * s, yb - 215 * s, x + 110 * s, yb - 150 * s], fill=OUT)
        p.ell([x - 144 * s, yb - 210 * s, x + 104 * s, yb - 156 * s], fill=C["soil"])
    tray = [(x - 165 * s, yb - 180 * s), (x + 125 * s, yb - 180 * s), (x + 80 * s, yb - 80 * s), (x - 120 * s, yb - 80 * s)]
    big = [(x - 175 * s, yb - 188 * s), (x + 135 * s, yb - 188 * s), (x + 86 * s, yb - 74 * s), (x - 126 * s, yb - 74 * s)]
    p.poly(big, OUT)
    p.poly(tray, red)
    p.poly([(x + 40 * s, yb - 180 * s), (x + 125 * s, yb - 180 * s), (x + 80 * s, yb - 80 * s), (x + 20 * s, yb - 80 * s)], red_d)
    hx, hy = hand if hand else (x + 240 * s, yb - 130 * s)
    P.oline(p, (x + 100 * s, yb - 140 * s), (hx, hy), (150, 110, 70), 12 * s, ow=4)
    P.oline(p, (x + 50 * s, yb - 80 * s), (x + 60 * s, yb - 4 * s), (90, 90, 100), 10 * s, ow=4)
    P.ocircle(p, x - 120 * s, yb - 42 * s, 42 * s, (60, 60, 68), ow=4, shaded=False)
    p.circle(x - 120 * s, yb - 42 * s, 14 * s, fill=(190, 196, 206))

def washer(p, cx, yb, s=1.0, t=0.0, shake=0.0):
    """A broken washing machine: taped 'OUT OF ORDER' note and a puddle."""
    cx = cx + math.sin(t * 40) * 6 * shake
    p.ell([cx - 190 * s, yb - 16 * s, cx + 230 * s, yb + 30 * s], fill=(150, 200, 236))
    P.orr(p, [cx - 150 * s, yb - 340 * s, cx + 150 * s, yb], 26 * s, (236, 238, 242), shade_side="r")
    p.rr([cx - 140 * s, yb - 330 * s, cx + 140 * s, yb - 272 * s], 16 * s, fill=(204, 210, 218))
    p.rr([cx - 120 * s, yb - 318 * s, cx - 20 * s, yb - 286 * s], 8 * s, fill=(40, 46, 56))
    p.text((cx - 70 * s, yb - 302 * s), "ERR", f2("anton", max(8, int(24 * s))), RED)
    P.ocircle(p, cx + 90 * s, yb - 301 * s, 18 * s, (170, 176, 188), ow=3, shaded=False)
    P.ocircle(p, cx, yb - 140 * s, 102 * s, (160, 168, 182), ow=5, shaded=False)
    p.circle(cx, yb - 140 * s, 78 * s, fill=(110, 170, 220))
    p.rect([cx - 78 * s, yb - 140 * s, cx + 78 * s, yb - 62 * s], fill=(90, 150, 205))
    p.circle(cx, yb - 140 * s, 78 * s, outline=(110, 170, 220), width=0)
    p.arc([cx - 60 * s, yb - 200 * s, cx + 20 * s, yb - 120 * s], 200, 260, WHITE, max(3, 8 * s))
    # the taped note
    p.rr([cx - 96 * s, yb - 186 * s, cx + 96 * s, yb - 112 * s], 6 * s, fill=WHITE, shadow=True)
    p.rect([cx - 30 * s, yb - 196 * s, cx + 30 * s, yb - 178 * s], fill=(240, 220, 150))
    p.text((cx, yb - 162 * s), "OUT OF", f2("anton", max(8, int(26 * s))), RED)
    p.text((cx, yb - 134 * s), "ORDER", f2("anton", max(8, int(26 * s))), RED)
    # drips
    for k in range(3):
        ph = (t * 1.6 + k / 3) % 1
        p.circle(cx + 130 * s, yb - 40 * s + 50 * s * ph, 8 * s * (1 - ph * .5), fill=(150, 200, 236))

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

def note(p, x, y, s=1.0, ang=0.0):
    """A £20 note (flat rectangle), rotated by `ang` radians."""
    w, h = 120 * s, 64 * s
    ca, sa = math.cos(ang), math.sin(ang)
    def rot(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    p.poly([rot(-w / 2 - 4, -h / 2 - 4), rot(w / 2 + 4, -h / 2 - 4), rot(w / 2 + 4, h / 2 + 4), rot(-w / 2 - 4, h / 2 + 4)], OUT)
    p.poly([rot(-w / 2, -h / 2), rot(w / 2, -h / 2), rot(w / 2, h / 2), rot(-w / 2, h / 2)], (150, 110, 200))
    p.circle(*rot(-w * .25, 0), h * .28, fill=(190, 160, 230))
    p.text(rot(w * .18, 0), "£20", f2("anton", max(8, int(30 * s))), WHITE)

def sign(p, x, yb, text, tilt=0.0):
    """Alfie's little sign stuck in the soil."""
    ang = math.radians(tilt)
    top = (x + math.sin(ang) * 150, yb - math.cos(ang) * 150)
    P.oline(p, (x, yb), top, (176, 124, 72), 12, ow=4)
    bx, by = top
    p.rr([bx - 120 - 5, by - 70 - 5, bx + 120 + 5, by + 10 + 5], 14, fill=OUT)
    p.rr([bx - 120, by - 70, bx + 120, by + 10], 10, fill=(240, 226, 190))
    p.text((bx, by - 44), text, f2("anton", 34), INK)
    p.text((bx, by - 10), "THIS WAY ↓", f2("dm", 22), (90, 70, 60))

def chat_card(p, x, y, k, title, msg):
    if k <= 0: return
    w, h = 560 * k, 200 * k
    p.rr([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 30, fill=(240, 244, 250), shadow=True)
    if k < 0.9: return
    p.text((x - 250, y - 60), title, f2("dm", 28), (110, 120, 140), anchor="lm")
    p.rr([x - 250, y - 30, x + 250, y + 70], 24, fill=(120, 210, 140))
    p.text((x - 226, y + 20), msg, f2("dm", 34), INK, anchor="lm")

# ---------------- fixed HUD ----------------
@V.fixed
def hud_band(p, t):
    k = eo(prog(t, V.L(8)[0] + 0.3, V.L(8)[0] + 1.6))
    P.hud(p, DAY, FUND_BEFORE + (FUND - FUND_BEFORE) * k)

@V.sounds
def sounds(L):
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh"), (2.6, "pop")]
    out += [(at(0, "So Crumbs"), "boing"), (at(0, "expensive"), "cash")]
    out += [(L(1)[0] + 0.2, "pop"), (at(1, "So Crumbs") + 0.3, "thud"), (at(1, "pay"), "ding")]
    out += [(L(2)[0] + 0.1, "ding"), (at(2, "Bev"), "pop"), (at(2, "big spade"), "thud")]
    out += [(L(3)[0] + 0.1, "boing")]
    out += [(L(4)[0] + 0.2, "pop")]
    a5, e5 = L(5)
    out += [(t0, "pop") for t0 in FILL_TIMES()[::2]]
    out += [(e5 - 0.1, "ding")]
    out += [(L(6)[0] + 0.3, "whoosh"), (at(6, "go outside"), "ding")]
    out += [(L(7)[0] + 0.2, "boing")]
    out += [(L(8)[0] + 0.1, "cash"), (at(8, "Nearly"), "thud")]
    out += [(at(9, "The house") + 0.6, "pop"), (at(9, "Happiness"), "pop")]
    out += [(at(10, "overalls"), "ding"), (at(10, "Her washing"), "boing")]
    out += [(L(11)[0] + 0.1, "ding")]
    out += [(at(13, "A:"), "pop"), (at(13, "B:") - 0.1, "pop"), (at(13, "Or C") - 0.1, "pop")]
    out += [(L(14)[0] + 0.1, "pop"), (L(15)[0] + 0.1, "pop"), (at(15, "or Crumbs"), "boing"), (at(15, "Day five"), "ding")]
    return out

def FILL_TIMES():
    """When each hole gets filled during line 5 (in FILL order)."""
    a5, e5 = V.L(5)
    t0, t1 = a5 + 0.3, e5 - 0.4
    return [t0 + (t1 - t0) * k / 13 for k in range(14)]

def fill_t_map():
    ft = FILL_TIMES()
    return {FILL[k]: ft[k] for k in range(14)}

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    garden(p, t, holes=14, neighbours=3)
    P.family(p, t, {"dave": "worried", "sue": "worried", "ellie": "neutral", "alfie": "sad", "crumbs": "happy"}, yf=1130, sc=0.8,
             xs=(170, 380, 600, 790, 960))
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0, dx = 560, -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.35, 0.7)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "DAY 4", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "NOBODY VOTED", f2("anton", max(10, int(104 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "SO THE DOG CHOSE. IT COST £60.", f2("dm", max(8, int(42 * k3))), (255, 160, 190))
        if k3 > 0.5:
            paw(p, 960 + dx, y0 + 90, 40, (255, 160, 190))
    pill(p, 540, 390, "VOTES YESTERDAY: 0", prog(t, 2.6, 3.0), bg=RED, fg=WHITE)
    tc = at(0, "So Crumbs")
    if t > tc:
        pill(p, 820, 480, "CRUMBS CHOSE", prog(t, tc, tc + 0.3), bg=YEL, size=36)
    te = at(0, "expensive")
    if t > te:
        pill(p, 260, 480, "-£60", prog(t, te, te + 0.3), bg=RED, fg=WHITE, size=44)

@V.scene(1)
def result(p, t, L):
    a1, e1 = L(1)
    p.text((540, 360), "YOUR VOTES", f2("anton", 72), YEL)
    P.result_bars(p, t, a1 - 0.1, VOTES, top=440)
    labels = ["FILL IN THE HOLES", "CRAZY GOLF, £2 A ROUND", "PAY A GARDENER (£60)"]
    for i, lab in enumerate(labels):
        k = prog(t, a1 + 0.2 + i * 0.2, a1 + 0.5 + i * 0.2)
        if k > 0:
            p.text((540, 440 + i * 150 + 55), lab, f2("dm", 36), WHITE)
    ts = at(1, "So Crumbs")
    # Crumbs trots in and sits by the C bar; a paw print stamps it
    cx = lerp(1250, 800, eo(prog(t, ts - 0.6, ts + 0.3)))
    P.crumbs(p, cx, 1150, 0.62, "happy", t)
    q = prog(t, ts + 0.3, ts + 0.6)
    if q > 0:
        paw(p, 250, 800, 40 * eback(q), WHITE)
        pill(p, 360, 1060, "CRUMBS PICKED C", prog(t, ts + 0.4, ts + 0.7), bg=P.OPT_COLS["C"], size=40)

@V.scene(2, 4)
def bev_arrives(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3); a4, e4 = L(4)
    garden(p, t, holes=14, neighbours=3)
    if t < a3 - 0.2:
        bx = lerp(1260, 780, eo(prog(t, a2 - 0.2, a2 + 1.8)))
        walk = abs(math.sin(t * 7)) * 10 * (1 - prog(t, a2 + 1.6, a2 + 1.9))
        hand = bev_hand(bx, 1140 - walk, 0.9, t)
        wheelbarrow(p, bx - 300, 1140, 0.95, hand=hand)
        bev(p, bx, 1140 - walk, 0.9, "happy", t)
        digital_clock(p, 250, 400, "09:00", t, colour=GREEN, w=300, h=130)
        tb = at(2, "Bev")
        if t > tb:
            pill(p, 700, 400, "BEV THE GARDENER", prog(t, tb, tb + 0.3), bg=WHITE, size=38)
        ts = at(2, "big spade")
        if t > ts:
            for j in range(4):
                ang = t * 3 + j * 1.57
                sparkle(p, bx - 330 + 70 * math.cos(ang), 860 + 60 * math.sin(ang), 14)
        return
    # Bev parks the barrow and starts work; Dave and Sue come out
    wheelbarrow(p, 640, 1140, 0.85, hand=bev_hand(900, 1140, 0.85, t))
    bev(p, 900, 1140, 0.85, "happy", t)
    if t < a4 - 0.2:
        k = eback(prog(t, a3 - 0.2, a3 + 0.2))
        P.dave(p, 260, 1140, 0.9 * max(0.01, k), "shock", t, talk=V.talk(t, "dave"))
        pill(p, 300, 400, "£60?!", prog(t, a3 + 0.1, a3 + 0.4), bg=RED, fg=WHITE, size=60)
        return
    k = eback(prog(t, a4 - 0.2, a4 + 0.2))
    P.dave(p, 190, 1140, 0.85, "tired", t)
    P.sue(p, 420, 1140, 0.9 * max(0.01, k), "happy", t, talk=V.talk(t, "sue"))
    tc = at(4, "cornflakes")
    pill(p, 540, 400, "ASLEEP IN HIS CORNFLAKES", prog(t, tc, tc + 0.3), bg=YEL, size=38)

@V.scene(5, 7)
def timelapse(p, t, L):
    a5, e5 = L(5); a6, e6 = L(6); a7, e7 = L(7)
    if t < a6 - 0.2:
        ft = FILL_TIMES()
        n = sum(1 for x in ft if t >= x)
        garden(p, t, holes=14, filled=n, neighbours=3, fill_t=fill_t_map())
        # Bev zooms between holes (time-lapse)
        k = prog(t, a5 + 0.3, e5 - 0.4)
        bx = 540 + 330 * math.sin(k * math.pi * 5)
        spade(p, bx + 110, 1150, 0.8, lift=50 * abs(math.sin(t * 9)))
        bev(p, bx, 1150, 0.82, "happy", t)
        for j in range(3):   # speed lines
            y = 880 + j * 60
            d = -1 if math.cos(k * math.pi * 5) > 0 else 1
            p.line([(bx + d * 120, y), (bx + d * 220, y)], WHITE, 6)
        mins = int(120 * prog(t, a5, e5 - 0.4))
        digital_clock(p, 300, 400, f"{9 + mins // 60:02d}:{mins % 60:02d}", t, colour=GREEN, w=340, h=140, blink=False)
        pill(p, 760, 400, f"FILLED: {n}/14", prog(t, a5, a5 + 0.3), bg=GREEN if n >= 14 else WHITE, size=40)
        return
    sprout = prog(t, a6, e7)
    if t < a7 - 0.2:
        garden(p, t, holes=14, filled=14, neighbours=3, sink=prog(t, a6 + 0.1, a6 + 1.2), sprout=sprout)
        k = eback(prog(t, a6 - 0.2, a6 + 0.2))
        P.ellie(p, 540, 1150, 0.95 * max(0.01, k), "happy", t, talk=V.talk(t, "ellie"))
        P.crumbs(p, 880, 1150, 0.55, "happy", t)
        tn = at(6, "I can")
        pill(p, 540, 400, "STARING: STOPPED", prog(t, a6 + 0.6, a6 + 0.9), bg=GREEN, size=44)
        if t > tn:
            for j in range(5):
                ang = t * 2 + j * 1.26
                sparkle(p, 540 + 230 * math.cos(ang), 820 + 120 * math.sin(ang), 14, fill=WHITE)
        return
    garden(p, t, holes=14, filled=14, neighbours=0, sprout=sprout)
    tilt = lerp(0, 34, eback(prog(t, a7 + 0.2, a7 + 0.8)))
    sign(p, 760, 1120, "AUSTRALIA", tilt)
    k = eback(prog(t, a7 - 0.2, a7 + 0.2))
    P.alfie(p, 400, 1150, 1.0 * max(0.01, k), "sad", t, wave=1 if t > at(7, "I'll") else 0, talk=V.talk(t, "alfie"))
    pill(p, 540, 400, "TUNNEL: CLOSED", prog(t, a7 + 0.3, a7 + 0.6), bg=RED, fg=WHITE, size=44)

@V.scene(8, 9)
def money(p, t, L):
    a8, e8 = L(8); a9, e9 = L(9)
    if t < a9 - 0.2:
        lv = lerp(FUND_BEFORE, FUND, eo(prog(t, a8 + 0.3, a8 + 1.6))) / 1000
        P.jar(p, 300, 1090, 2.4, lv)
        p.text((300, 1135), "HOLIDAY JAR", f2("dm", 34), WHITE)
        for j in range(3):   # three £20 notes fly out of the jar
            q = prog(t, a8 + 0.1 + j * 0.25, a8 + 1.0 + j * 0.25)
            if 0 < q < 1:
                x = lerp(300, 1150, eo(q)); y = lerp(700, 560, q) - 160 * math.sin(math.pi * q)
                note(p, x, y, 1.1, ang=q * 3 + j)
        big_number(p, t, a8 + 0.3, 28, cx=740, cy=700, size=280, start=88, dur=1.3, fill=RED, fmt="£{}")
        P.money_pop(p, t, a8 + 0.2, "-£60", x=740, y=520, colour=RED)
        tn = at(8, "Nearly")
        if t > tn:
            pill(p, 540, 400, "NEARLY BACK TO DAY 1", prog(t, tn, tn + 0.3), bg=YEL, size=42)
            pill(p, 740, 920, "DAY 1: £23.50", prog(t, tn + 0.3, tn + 0.6), bg=WHITE, size=36)
        return
    P.stats_panel(p, t, a9 - 0.2, [("MONEY", 2.8, GREEN, "£28.00"), ("HAPPINESS", 55, YEL, "55/100"), ("HOUSE", 65, ORANGE, "65/100")])
    th = at(9, "The house") + 0.5
    pill(p, 540, 1010, "HOUSE +40: GARDEN FIXED", prog(t, th, th + 0.3), bg=WHITE, size=36)
    tp = at(9, "Happiness")
    pill(p, 540, 1100, "HAPPINESS +5: NO MORE STARING", prog(t, tp, tp + 0.3), bg=YEL, size=36)

@V.scene(10, 11)
def twist(p, t, L):
    a10, e10 = L(10); a11, e11 = L(11)
    tw = at(10, "Her washing")
    garden(p, t, holes=14, filled=14, sprout=1.0)
    if t < tw - 0.1:
        P.dave(p, 330, 1140, 0.9, "neutral", t)
        bev(p, 800, 1140, 0.85, "shock", t, wave=1)
        to = at(10, "overalls")
        if t > to:
            for j in range(5):
                ang = t * 3 + j * 1.26
                sparkle(p, 330 + 150 * math.cos(ang), 900 + 90 * math.sin(ang), 16)
            pill(p, 330, 560, "OVERALLS!", prog(t, to, to + 0.3), bg=YEL, size=44)
        return
    if t < a11 - 0.2:
        k = eback(prog(t, tw - 0.1, tw + 0.3))
        washer(p, 470, 1140, 1.35 * max(0.01, k), t, shake=1.0)
        bev(p, 880, 1150, 0.72, "worried", t)
        tm = at(10, "a month")
        pill(p, 540, 400, "BROKEN FOR 1 MONTH", prog(t, tm, tm + 0.3), bg=RED, fg=WHITE, size=44)
        return
    washer(p, 760, 1140, 0.95, t, shake=0.3)
    k = eback(prog(t, a11 - 0.2, a11 + 0.2))
    P.dave(p, 330, 1140, 0.95 * max(0.01, k), "grin", t, wave=1, hold="wrench", talk=V.talk(t, "dave"))
    pill(p, 540, 400, "EXPERT MODE: ON", prog(t, at(11, "That's"), at(11, "That's") + 0.3), bg=BLUE, fg=INK, size=48)
    for j in range(4):
        ang = t * 2.5 + j * 1.57
        sparkle(p, 760 + 200 * math.cos(ang), 940 + 130 * math.sin(ang), 14, fill=WHITE)

@V.scene(12, 15)
def vote(p, t, L):
    a12, _ = L(12); a13, e13 = L(13); a14, _ = L(14); a15, _ = L(15)
    if t < a13 - 0.3:
        garden(p, t, holes=14, filled=14, sprout=1.0)
        P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}, yf=1130)
        pill(p, 540, 390, "YOU DECIDE", prog(t, a12 + 0.3, a12 + 0.6), size=54)
    elif t < a15 - 0.2:
        tA, tB, tC = at(13, "A:"), at(13, "B:"), at(13, "Or C")
        P.vote_card(p, t, tA - 0.7, "BEV'S WASHING MACHINE?", OPTIONS, gap=(tC - tA) / 2)
        if t > a14 - 0.1:
            k = eback(prog(t, a14 - 0.1, a14 + 0.3))
            P.sue(p, 950, 1185, 0.46 * max(0.01, k), "happy", t, hold="phone", talk=V.talk(t, "sue"))
    else:
        garden(p, t, holes=14, filled=14, sprout=1.0)
        P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}, yf=1130,
                 talk=P.talkers(V, t))
        pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a15 + 0.1, a15 + 0.5), bg=WHITE, size=54)
        tcr = at(15, "or Crumbs")
        if t > tcr:
            pill(p, 540, 490, "OR CRUMBS CHOOSES AGAIN", prog(t, tcr, tcr + 0.3), bg=RED, fg=WHITE, size=36)
        td = at(15, "Day five")
        pill(p, 540, 580, "DAY 5 TOMORROW", prog(t, td, td + 0.4), bg=YEL, size=40)

if __name__ == "__main__":
    V.main()
