import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

DAY = 3
FUND = 88.00          # A was free: the fund stays at £88.00
VOTES = {"A": 2, "B": 0, "C": 0}

SCRIPT = [
    # (speaker, spoken text, caption text)
    ("narrator", "Yesterday, you voted to dig up the garden. Eight hours to find the keys.", "Yesterday, you voted to *dig up* the garden. *8 hours* to find the keys."),
    ("narrator", "The winner: A. Every vote, again.", "The winner: *A*. *Every vote*, again."),
    ("narrator", "Midnight. Torches on. Sue split the garden into squares.", "*Midnight*. Torches on. Sue split the garden into *squares*."),
    ("sue", "Square one: no keys. I'm posting it in the group chat.", "Square *one*: no keys. I'm posting it in the *group chat*."),
    ("ellie", "I'm literally helping. My phone is the torch.", "I'm *literally* helping. My phone is the *torch*."),
    ("alfie", "If I dig deep enough, I'll come out in Australia!", "If I dig deep enough, I'll come out in *Australia!*"),
    ("narrator", "By one in the morning, they'd found a sock, a tennis ball, and three TV remotes.", "By *1am*, they'd found a sock, a tennis ball, and *3 TV remotes*."),
    ("dave", "So that's where they went!", "So *that's* where they went!"),
    ("narrator", "Ten to eight in the morning. Fourteen holes. Still no keys.", "*7:50am*. *14 holes*. Still *no keys*."),
    ("narrator", "Then Crumbs sniffed one spot, and dug them up in ten seconds.", "Then Crumbs sniffed *one spot*, and dug them up in *10 seconds*."),
    ("dave", "Good boy. I think.", "*Good boy*. I think."),
    ("narrator", "Dave made it with two minutes to spare. It cost nothing, so the fund stays at eighty-eight pounds.", "Dave made it with *2 minutes* to spare. It cost *nothing*, so the fund stays at *£88*."),
    ("narrator", "But everyone's exhausted. Happiness: fifty out of a hundred. And the house: twenty-five.", "But everyone's *exhausted*. Happiness: *50/100*. And the house: *25/100*."),
    ("narrator", "Now the garden looks like the moon. And the neighbours are staring.", "Now the garden looks like the *moon*. And the *neighbours* are staring."),
    ("alfie", "I've got an idea. Crazy golf!", "I've got an *idea*. *Crazy golf!*"),
    ("narrator", "So what should the Pennys do?", "So what should the Pennys *do*?"),
    ("narrator", "A: fill every hole back in. Free, but it takes Dave's day off. B: crazy golf for the street, at two pounds a round. Or C: pay a gardener sixty pounds to fix it.", "*A*: fill every hole back in. Free, but it takes Dave's *day off*. *B*: crazy golf for the street, at *£2 a round*. Or *C*: pay a gardener *£60* to fix it."),
    ("ellie", "Not B! If anyone from school sees this, I'm moving to the moon.", "Not *B!* If anyone from *school* sees this, I'm moving to the *moon*."),
    ("narrator", "Comment A, B or C. Day four, tomorrow. Follow, to see if they make it.", "Comment *A*, *B* or *C*. *Day 4*, tomorrow. Follow, to see if they make it."),
]

V = Video(
    "pennys-ep03", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS,
    lines=[(sp, txt) for sp, txt, _ in SCRIPT],
    display=[cap for _, _, cap in SCRIPT],
)

OPTIONS = [("A", "Fill in the holes", "FREE   HOUSE +   DAVE'S DAY OFF GONE"),
           ("B", "Crazy golf, £2 a round", "+£   GARDEN STAYS A MESS"),
           ("C", "Pay a gardener", "-£60   HOUSE ++")]

OUT = P.OUT
SKY_T, SKY_B = (120, 190, 240), (190, 228, 250)

def at(i, sub):
    """Approximate time the substring `sub` starts in spoken line i (by character position)."""
    a, b = V.L(i)
    txt = V.lines[i][1]
    k = txt.find(sub)
    return a + (b - a) * max(0, k) / max(1, len(txt))

def shade(c, k=0.8):
    return tuple(int(v * k) for v in c)

def mix(c1, c2, k):
    return tuple(int(c1[j] + (c2[j] - c1[j]) * k) for j in range(3))

# ---------------- the garden: night, dawn, day ----------------
PAL = {
    "night": dict(sky_t=(12, 20, 46), sky_b=(38, 56, 100), fence=(78, 60, 56), fence_l=(92, 72, 64), fence_d=(60, 46, 42),
                  grass=(44, 88, 60), grass_d=(36, 74, 52), soil=(78, 56, 40), soil_d=(58, 42, 30), hole=(24, 18, 16)),
    "dawn": dict(sky_t=(96, 116, 180), sky_b=(252, 186, 146), fence=(150, 104, 72), fence_l=(166, 118, 82), fence_d=(124, 86, 58),
                 grass=(92, 150, 90), grass_d=(78, 134, 78), soil=(112, 78, 50), soil_d=(90, 62, 40), hole=(46, 32, 24)),
    "day": dict(sky_t=SKY_T, sky_b=SKY_B, fence=(170, 120, 80), fence_l=(186, 134, 90), fence_d=(140, 96, 62),
                grass=(110, 180, 100), grass_d=(92, 160, 86), soil=(120, 82, 52), soil_d=(96, 64, 40), hole=(64, 42, 28)),
}
HOLES = [(150, 880), (420, 872), (690, 886), (860, 902),
         (260, 975), (540, 985), (810, 992), (120, 1050),
         (380, 1062), (660, 1070), (880, 1090), (230, 1122), (500, 1128), (760, 1124)]
STARS = [(90, 340), (210, 420), (330, 360), (470, 450), (560, 330), (700, 400), (760, 520), (1010, 350), (130, 520), (620, 540), (980, 560)]

def sky(p, top, bot, y0=300, y1=700):
    n = 10
    for i in range(n):
        c = mix(top, bot, i / (n - 1))
        p.rect([0, y0 + (y1 - y0) * i / n, 1080, y0 + (y1 - y0) * (i + 1) / n + 1], fill=c)

def cloud(p, x, y, s=1.0, col=(250, 252, 255)):
    for dx, dy, r in [(-60, 10, 46), (0, -14, 60), (60, 10, 46), (0, 20, 46)]:
        p.circle(x + dx * s, y + dy * s, r * s, fill=col)

def moon(p, x, y, r, sky_c=None):
    p.circle(x, y, r, fill=(240, 236, 212))
    for dx, dy, rr in [(-0.3, -0.25, 0.22), (0.25, 0.1, 0.16), (-0.1, 0.38, 0.12), (0.35, -0.35, 0.09)]:
        p.circle(x + dx * r, y + dy * r, rr * r, fill=(214, 208, 184))

def neighbour_head(p, x, y, kind, t, i):
    peek = 6 * math.sin(t * 2.2 + i)
    y = y + peek
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

def garden(p, t, tod="night", holes=0, grid=0.0, beam=None, neighbours=0, sun_k=1.0):
    c = PAL[tod]
    sky(p, c["sky_t"], c["sky_b"])
    if tod == "night":
        for i, (sx, sy) in enumerate(STARS):
            sparkle(p, sx, sy, 5 + 5 * pulse(t + i * 0.37, 1.4), fill=(250, 240, 200))
        moon(p, 955, 480, 44)
    elif tod == "dawn":
        p.circle(860, lerp(720, 600, sun_k), 78, fill=(255, 196, 96))
        cloud(p, (300 + t * 14) % 1300 - 110, 450, 0.6, col=(255, 214, 196))
    else:
        p.circle(960, 380, 44, fill=YEL)
        cloud(p, (200 + t * 14) % 1300 - 110, 460, 0.7)
    # neighbours peeking over the fence (drawn before it, so the fence hides their chins)
    for i, (nx, kind) in enumerate([(250, "bun"), (560, "cap"), (840, "bald")][:neighbours]):
        neighbour_head(p, nx, 532, kind, t, i)
    # fence
    p.rect([0, 600, 1080, 820], fill=c["fence"])
    for i in range(0, 1080, 72):
        p.rect([i, 590, i + 64, 820], fill=c["fence_l"])
        p.poly([(i, 590), (i + 32, 566), (i + 64, 590)], c["fence_l"])
        p.line([(i + 66, 600), (i + 66, 820)], c["fence_d"], 6)
    p.rect([0, 680, 1080, 694], fill=c["fence_d"])
    p.rect([0, 800, 1080, 1170], fill=c["grass"])
    for i in range(16):                # grass tufts
        gx = (i * 83) % 1080 + 20
        gy = 840 + (i * 57) % 300
        p.line([(gx, gy), (gx - 6, gy - 16)], c["grass_d"], 4)
        p.line([(gx + 8, gy), (gx + 10, gy - 18)], c["grass_d"], 4)
    if beam:
        glow_poly(p, beam, (255, 244, 190), 95)
    if grid > 0:                        # Sue's string grid
        for gy in (930, 1035):
            p.line([(60, gy), (60 + 940 * eo(prog(grid, 0, 0.6)), gy)], (236, 232, 220), 3)
        for gx in (280, 540, 800):
            p.line([(gx, 815), (gx, 815 + 340 * eo(prog(grid, 0.3, 1.0)))], (236, 232, 220), 3)
        if grid >= 1:
            for gx in (280, 540, 800):
                for gy in (930, 1035):
                    p.circle(gx, gy, 6, fill=(236, 232, 220))
    for i in range(min(holes, len(HOLES))):
        hole(p, *HOLES[i], c)

def hole(p, x, y, c, s=1.0):
    p.ell([x + 24 * s, y - 50 * s, x + 128 * s, y + 4 * s], fill=c["soil_d"])
    p.ell([x + 32 * s, y - 58 * s, x + 120 * s, y - 6 * s], fill=c["soil"])
    p.ell([x - 66 * s, y - 24 * s, x + 66 * s, y + 24 * s], fill=c["soil_d"])
    p.ell([x - 56 * s, y - 17 * s, x + 56 * s, y + 15 * s], fill=c["hole"])

def glow_poly(p, pts, colour, alpha):
    """A see-through polygon (torch beam) blended onto what is already drawn."""
    xs = [x * S for x, _ in pts]; ys = [y * S for _, y in pts]
    x0, y0 = max(0, int(min(xs))), max(0, int(min(ys)))
    x1, y1 = min(p.img.width, int(max(xs)) + 1), min(p.img.height, int(max(ys)) + 1)
    if x1 <= x0 or y1 <= y0: return
    ov = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(x - x0, y - y0) for x, y in zip(xs, ys)], fill=colour + (alpha,))
    p.img.alpha_composite(ov, (x0, y0))

def dirt_spray(p, x, y, t, d=1, c=PAL["night"]):
    for i in range(14):
        ph = (t * 1.8 + i / 14) % 1
        px = x + d * (30 + 240 * ph)
        py = y - 320 * ph + 360 * ph * ph
        p.circle(px, py, 10 + 6 * ((i * 7) % 3), fill=c["soil"] if i % 2 else c["soil_d"])

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

def remote(p, x, y, s=1.0):
    p.rr([x - 24 * s - 4, y - 72 * s - 4, x + 24 * s + 4, y + 72 * s + 4], 16 * s, fill=OUT)
    p.rr([x - 24 * s, y - 72 * s, x + 24 * s, y + 72 * s], 14 * s, fill=(44, 46, 56))
    p.circle(x, y - 48 * s, 9 * s, fill=RED)
    for r in range(3):
        for cc in (-1, 0, 1):
            p.circle(x + cc * 13 * s, y - 16 * s + r * 20 * s, 5 * s, fill=(170, 176, 190))
    for k in range(3):                  # tooth marks
        p.circle(x + 24 * s, y + 30 * s + k * 14 * s, 5 * s, fill=OUT)

def sock(p, x, y, s=1.0):
    red = (230, 86, 96)
    P.oline(p, (x, y - 64 * s), (x, y + 10 * s), red, 40 * s, ow=4)
    P.oline(p, (x - 6 * s, y + 18 * s), (x + 46 * s, y + 22 * s), red, 40 * s, ow=4)
    p.rect([x - 20 * s, y - 64 * s, x + 20 * s, y + 10 * s], fill=red)
    for yy in (-50, -30):
        p.rect([x - 20 * s, y + yy * s, x + 20 * s, y + (yy + 8) * s], fill=WHITE)
    p.circle(x + 50 * s, y + 22 * s, 10 * s, fill=(170, 60, 70))   # hole in the toe

def tennis_ball(p, x, y, s=1.0):
    P.ocircle(p, x, y, 38 * s, (210, 230, 70), ow=4)
    p.arc([x - 64 * s, y - 34 * s, x - 4 * s, y + 34 * s], 300, 60, WHITE, 5 * s)
    p.arc([x + 4 * s, y - 34 * s, x + 64 * s, y + 34 * s], 120, 240, WHITE, 5 * s)

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

def golf_flag(p, x, yb, s=1.0, t=0.0, num="1"):
    p.line([(x, yb), (x, yb - 200 * s)], OUT, 9 * s)
    p.line([(x, yb), (x, yb - 200 * s)], WHITE, 5 * s)
    w = 8 * math.sin(t * 5)
    p.poly([(x, yb - 200 * s), (x + 96 * s, yb - 172 * s + w), (x, yb - 144 * s)], OUT)
    p.poly([(x + 3, yb - 194 * s), (x + 88 * s, yb - 172 * s + w), (x + 3, yb - 150 * s)], RED)
    p.text((x + 32 * s, yb - 172 * s), num, f2("anton", int(30 * s)), WHITE)

def golf_club(p, hx, hy, s=1.0, swing=0.0):
    ang = math.radians(70 + 30 * swing)
    ex, ey = hx + math.cos(ang) * 190 * s, hy + math.sin(ang) * 190 * s
    P.oline(p, (hx, hy), (ex, ey), (190, 196, 206), 8 * s, ow=3)
    p.rr([ex - 6 * s, ey - 8 * s, ex + 44 * s, ey + 12 * s], 6 * s, fill=OUT)
    p.rr([ex - 2 * s, ey - 4 * s, ex + 40 * s, ey + 8 * s], 4 * s, fill=(150, 156, 170))

def car(p, x, base, s=1.0):
    red, red_d = (200, 72, 62), (160, 52, 46)
    P.ground_shadow(p, x, base, 250 * s)
    p.rr([x - 150 * s - 5, base - 215 * s - 5, x + 160 * s + 5, base - 100 * s], 40 * s, fill=OUT)
    p.rr([x - 150 * s, base - 215 * s, x + 160 * s, base - 100 * s], 36 * s, fill=red)
    p.rr([x - 128 * s, base - 196 * s, x - 10 * s, base - 120 * s], 14 * s, fill=(170, 215, 240))
    p.rr([x + 5 * s, base - 196 * s, x + 110 * s, base - 120 * s], 14 * s, fill=(170, 215, 240))
    # Dave at the wheel
    p.circle(x + 58 * s, base - 150 * s, 30 * s, fill=OUT)
    p.circle(x + 58 * s, base - 150 * s, 26 * s, fill=P.SKIN)
    p.rr([x + 40 * s, base - 146 * s, x + 76 * s, base - 138 * s], 4 * s, fill=(110, 75, 50))
    P.orr(p, [x - 240 * s, base - 130 * s, x + 240 * s, base - 40 * s], 30 * s, red, shade_side="r")
    p.circle(x + 222 * s, base - 100 * s, 12 * s, fill=YEL)          # headlight (driving right)
    p.ell([x - 96 * s, base - 80 * s, x - 60 * s, base - 62 * s], fill=(150, 90, 60))   # rust spot
    for wx in (-145, 145):
        P.ocircle(p, x + wx * s, base - 36 * s, 44 * s, (50, 50, 58), ow=4, shaded=False)
        p.circle(x + wx * s, base - 36 * s, 20 * s, fill=(180, 186, 196))

def digital_clock(p, cx, cy, text, t, colour=RED, w=560, h=230):
    p.rr([cx - w / 2 - 6, cy - h / 2 - 6, cx + w / 2 + 6, cy + h / 2 + 6], 36, fill=OUT)
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 30, fill=(24, 22, 28))
    if (t % 1.0) < 0.5 or ":" not in text:
        p.text((cx, cy + 4), text, f2("anton", int(h * 0.8)), colour)
    else:
        a, b = text.split(":")
        p.text((cx, cy + 4), a + " " + b, f2("anton", int(h * 0.8)), colour)

def chat_card(p, x, y, k, msg):
    if k <= 0: return
    w, h = 540 * k, 190 * k
    p.rr([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 30, fill=(240, 244, 250), shadow=True)
    if k < 0.9: return
    p.text((x - 240, y - 56), "PENNY FAMILY CHAT", f2("dm", 28), (110, 120, 140), anchor="lm")
    p.rr([x - 240, y - 26, x + 240, y + 66], 24, fill=(120, 210, 140))
    p.text((x - 216, y + 20), msg, f2("dm", 36), INK, anchor="lm")

def dave_hand(x, yf, s, t):
    """Where Dave's raised right hand is when he waves (matches pennys._body)."""
    th = 240 * s * (1 + 0.012 * math.sin(t * 2.4))
    tw = 250 * s; aw = tw * .18
    top = yf - 150 * s - th
    r0 = (x + tw / 2 - aw * .7, top + aw * .9)
    ang = -1.05 + 0.3 * math.sin(t * 9)
    return r0[0] + math.cos(ang) * th * .75, r0[1] + math.sin(ang) * th * .75

def sniff(p, x, y, t):
    for i in range(3):
        k = (t * 2.5 + i / 3) % 1
        r = 14 + 26 * k
        p.arc([x - r - 30 * k, y - r, x + r - 30 * k, y + r], 120, 240, (240, 240, 240), 4)

# ---------------- fixed HUD ----------------
@V.fixed
def hud_band(p, t):
    P.hud(p, DAY, FUND)

@V.sounds
def sounds(L):
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh"), (2.6, "pop")]
    out += [(L(1)[0] + 0.2, "pop"), (L(1)[0] + 1.3, "ding")]
    out += [(L(2)[0] + 0.1, "ding"), (at(2, "squares"), "pop")]
    out += [(L(3)[0] + 0.2, "pop"), (at(3, "I'm posting"), "ding")]
    out += [(L(4)[0] + 0.3, "whoosh")]
    out += [(L(5)[0] + 0.2 + i * 0.6, "thud") for i in range(4)]
    out += [(at(6, "a sock"), "pop"), (at(6, "a tennis"), "boing"), (at(6, "three"), "pop"), (at(6, "three") + 0.3, "pop"), (at(6, "three") + 0.6, "pop")]
    out += [(L(7)[0] + 0.1, "ding")]
    out += [(L(8)[0] + 0.1, "thud"), (at(8, "Still"), "boing")]
    out += [(at(9, "sniffed"), "pop"), (at(9, "dug"), "thud"), (at(9, "dug") + 0.6, "ding")]
    out += [(L(10)[0] + 0.1, "pop")]
    out += [(at(11, "two minutes"), "ding"), (at(11, "It cost"), "pop")]
    out += [(L(12)[0] + 0.3, "thud"), (at(12, "Happiness"), "pop"), (at(12, "And the house"), "pop")]
    out += [(L(13)[0] + 0.3, "boing"), (at(13, "And the"), "pop")]
    out += [(L(14)[0] + 0.2, "ding")]
    out += [(at(16, "A:") , "pop"), (at(16, "B:") - 0.1, "pop"), (at(16, "Or C") - 0.1, "pop")]
    out += [(L(17)[0], "boing"), (L(18)[0] + 0.1, "pop"), (at(18, "Day four"), "ding")]
    return out

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    garden(p, t, "night", holes=3)
    spade(p, 500, 1000, 0.8)
    P.family(p, t, {"dave": "worried", "sue": "worried", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}, yf=1130, sc=0.8,
             xs=(170, 380, 650, 840, 975))
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0, dx = 560, -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.35, 0.7)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "DAY 3", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "£912 TO GO", f2("anton", max(10, int(96 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "THE GREAT KEY DIG. 8 HOURS. GO!", f2("dm", max(8, int(42 * k3))), (255, 160, 190))
    pill(p, 540, 390, "YOU VOTED: DIG UP THE GARDEN", prog(t, 2.6, 3.0), bg=YEL)
    if t > at(0, "Eight"):
        pill(p, 540, 480, "8 HOURS TO FIND THE KEYS", prog(t, at(0, "Eight"), at(0, "Eight") + 0.3), bg=RED, fg=WHITE, size=36)

@V.scene(1)
def result(p, t, L):
    a1, _ = L(1)
    p.text((540, 360), "YOUR VOTES", f2("anton", 72), YEL)
    P.result_bars(p, t, a1 - 0.1, VOTES, top=440)
    labels = ["DIG UP THE GARDEN", "BUY A NEW KEY (£80)", "DAVE RIDES ALFIE'S BIKE"]
    for i, lab in enumerate(labels):
        k = prog(t, a1 + 0.2 + i * 0.2, a1 + 0.5 + i * 0.2)
        if k > 0:
            p.text((540, 440 + i * 150 + 55), lab, f2("dm", 36), INK if i == 0 else WHITE)
    if t > a1 + 1.0:
        tick(p, 540, 1000, 70, prog(t, a1 + 1.0, a1 + 1.4))
        pill(p, 540, 1110, "A WINS", prog(t, a1 + 1.1, a1 + 1.4), bg=P.OPT_COLS["A"], size=48)

@V.scene(2, 5)
def night_dig(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3); a4, e4 = L(4); a5, e5 = L(5)
    if t < a3 - 0.2:
        g = prog(t, at(2, "squares") - 0.2, e2)
        garden(p, t, "night", holes=0, grid=g)
        P.sue(p, 300, 1140, 0.9, "happy", t)
        spade(p, 760, 1110, 0.85, lift=40 * abs(math.sin(t * 4)))
        P.crumbs(p, 860, 1150, 0.6, "happy", t)
        digital_clock(p, 540, 430, "00:00", t, colour=RED, w=420, h=170)
        if t > at(2, "Torches"):
            pill(p, 540, 580, "TORCHES ON", prog(t, at(2, "Torches"), at(2, "Torches") + 0.3), bg=YEL, size=36)
        return
    who = "sue"
    for i, w in ((3, "sue"), (4, "ellie"), (5, "alfie")):
        if t >= L(i)[0] - 0.25: who = w
    a, _ = L({"sue": 3, "ellie": 4, "alfie": 5}[who])
    k = eback(prog(t, a - 0.25, a + 0.2))
    s = 0.95 * max(0.01, k)
    talk = V.talk(t, who)
    if who == "sue":
        garden(p, t, "night", holes=0, grid=1.0)
        hole(p, 680, 985, PAL["night"])
        cross(p, 680, 900, 34, prog(t, a3 + 0.4, a3 + 0.7))
        P.sue(p, 300, 1140, s, "happy", t, hold="phone", talk=talk)
        chat_card(p, 600, 470, eback(prog(t, at(3, "I'm posting"), at(3, "I'm posting") + 0.35)), "Square 1: no keys")
        pill(p, 540, 620, "SQUARES LEFT: 11", prog(t, at(3, "I'm posting") + 0.5, at(3, "I'm posting") + 0.8), bg=WHITE, size=34)
    elif who == "ellie":
        x, yf = 760, 1140
        # phone in her left hand (matches pennys._body)
        tw, th = 170 * s, 200 * s
        ph = (x - tw / 2 - tw * .18 * .55, yf - 160 * s - th + th * .8 - 30 * s)
        garden(p, t, "night", holes=3, grid=1.0)
        if k > 0.9:
            glow_poly(p, [(ph[0], ph[1] - 20), (60, 830), (60, 1160), (360, 1160)], (255, 244, 190), 90)
            sparkle(p, 200, 1060, 16 + 6 * pulse(t, 0.7), fill=(255, 250, 220))
        P.ellie(p, x, yf, s, "neutral", t, hold="phone", talk=talk)
        pill(p, 420, 400, "TORCH MODE: ON", prog(t, at(4, "My phone"), at(4, "My phone") + 0.3), bg=(128, 92, 200), fg=WHITE, size=40)
        pill(p, 420, 490, "BATTERY: 9%", prog(t, at(4, "torch"), at(4, "torch") + 0.3), bg=RED, fg=WHITE, size=34)
    else:
        garden(p, t, "night", holes=5, grid=1.0)
        hole(p, 520, 1100, PAL["night"], 1.6)
        P.alfie(p, 520, 1150, s * 1.05, "grin", t, talk=talk)
        # soil in front of his legs: he's standing in the hole
        p.ell([400, 1060, 650, 1170], fill=PAL["night"]["soil_d"])
        p.ell([420, 1070, 630, 1160], fill=PAL["night"]["soil"])
        spade(p, 700, 1130, 0.75, lift=60 * abs(math.sin(t * 5)))
        dirt_spray(p, 720, 1060, t, d=1)
        kx = at(5, "Australia")
        pill(p, 540, 400, "NEXT STOP: AUSTRALIA", prog(t, kx, kx + 0.3), bg=ORANGE, size=40)
        if t > kx:
            q = prog(t, kx, kx + 0.4)
            p.arrow((540, 470), (540, 470 + 110 * eo(q)), WHITE, 14, 40)

@V.scene(6, 7)
def finds(p, t, L):
    a6, e6 = L(6); a7, e7 = L(7)
    n_holes = 6 + int(3 * prog(t, a6, e6))
    garden(p, t, "night", holes=n_holes, grid=1.0)
    if t < a7 - 0.25:
        digital_clock(p, 540, 400, "01:00", t, colour=RED, w=320, h=130)
    else:
        pill(p, 540, 400, "MYSTERY SOLVED", prog(t, a7 - 0.1, a7 + 0.2), bg=GREEN, size=48)
    items = [(at(6, "a sock"), "sock", 200, 560), (at(6, "a tennis"), "ball", 400, 560),
             (at(6, "three"), "remote", 620, 560), (at(6, "three") + 0.3, "remote", 740, 560), (at(6, "three") + 0.6, "remote", 860, 560)]
    src = [HOLES[1], HOLES[2], HOLES[5], HOLES[6], HOLES[3]]
    for i, (t0, kind, tx, ty) in enumerate(items):
        q = prog(t, t0, t0 + 0.6)
        if q <= 0: continue
        sx, sy = src[i]
        x = lerp(sx, tx, eo(q)); y = lerp(sy - 30, ty, eo(q)) - 160 * math.sin(math.pi * q)
        if kind == "sock": sock(p, x, y, 1.0)
        elif kind == "ball": tennis_ball(p, x, y, 1.0)
        else: remote(p, x, y, 0.9)
        if q >= 1 and kind == "remote" and i == 4:
            pill(p, 740, 690, "3 TV REMOTES", prog(t, t0 + 0.6, t0 + 0.9), bg=YEL, size=36)
    if t < a7 - 0.25:
        P.crumbs(p, 860, 1150, 0.6, "happy", t)
        return
    k = eback(prog(t, a7 - 0.25, a7 + 0.2))
    P.dave(p, 250, 1140, 0.85 * max(0.01, k), "shock", t, talk=V.talk(t, "dave"))
    P.crumbs(p, 820, 1150, 0.62, "neutral", t)
    pill(p, 820, 960, "WHO, ME?", prog(t, a7 + 0.5, a7 + 0.8), bg=WHITE, size=32)

@V.scene(8, 10)
def dawn(p, t, L):
    a8, e8 = L(8); a9, e9 = L(9); a10, e10 = L(10)
    sk = prog(t, a8 - 0.3, e10)
    if t < a9 - 0.2:
        garden(p, t, "dawn", holes=14, sun_k=sk)
        P.family(p, t, {"dave": "tired", "sue": "tired", "ellie": "tired", "alfie": "grin", "crumbs": "happy"}, yf=1130, sc=0.72,
                 xs=(170, 370, 590, 780, 960))
        digital_clock(p, 540, 440, "07:50", t, colour=RED, w=440, h=180)
        pill(p, 360, 600, "14 HOLES", prog(t, at(8, "Fourteen"), at(8, "Fourteen") + 0.3), bg=WHITE, size=40)
        if t > at(8, "Still"):
            pill(p, 700, 600, "NO KEYS", prog(t, at(8, "Still"), at(8, "Still") + 0.3), bg=RED, fg=WHITE, size=40)
            cross(p, 860, 600, 30, prog(t, at(8, "Still") + 0.1, at(8, "Still") + 0.4), shake_t=t - at(8, "Still"))
        return
    if t < a10 - 0.2:
        garden(p, t, "dawn", holes=14, sun_k=sk)
        td = at(9, "dug")
        cx = lerp(1180, 600, eo(prog(t, a9 - 0.2, a9 + 0.8)))
        P.crumbs(p, cx, 1110, 0.95, "happy", t)
        hx, hy = cx - 110 * 0.95, 1110 - 190 * 0.95
        if t < td:
            sniff(p, hx - 40, hy + 20, t)
            pill(p, 540, 400, "SNIFF... SNIFF...", prog(t, at(9, "sniffed"), at(9, "sniffed") + 0.3), bg=WHITE, size=40)
        else:
            dirt_spray(p, cx + 80, 1060, t, d=1, c=PAL["dawn"])
            q = prog(t, td + 0.4, td + 1.1)
            if q > 0:
                ky = lerp(1080, 640, eo(q))
                keys(p, 460, ky, 1.3)
                for j in range(5):
                    ang = t * 2.5 + j * 1.26
                    sparkle(p, 470 + 130 * math.cos(ang), ky + 30 + 110 * math.sin(ang), 18)
            pill(p, 540, 400, "10 SECONDS", prog(t, at(9, "ten seconds"), at(9, "ten seconds") + 0.3), bg=YEL, size=48)
        return
    garden(p, t, "dawn", holes=14, sun_k=sk)
    k = eback(prog(t, a10 - 0.2, a10 + 0.2))
    s = 0.95 * max(0.01, k)
    P.dave(p, 330, 1140, s, "happy", t, wave=1, talk=V.talk(t, "dave"))
    if k > 0.9:
        hxp, hyp = dave_hand(330, 1140, s, t)
        keys(p, hxp + 6, hyp - 8, 1.0)
    P.crumbs(p, 800, 1130, 0.75, "happy", t)
    pill(p, 800, 820, "GOOD BOY?", prog(t, a10 + 0.3, a10 + 0.6), bg=WHITE, size=40)

@V.scene(11, 12)
def made_it(p, t, L):
    a11, e11 = L(11); a12, e12 = L(12)
    if t < a12 - 0.2:
        c = PAL["dawn"]
        sky(p, (150, 190, 236), (250, 214, 180))
        # houses scrolling past
        for i in range(8):
            x = (i * 200 - t * 260) % 1600 - 260
            col = [(200, 120, 100), (150, 160, 190), (210, 180, 120), (140, 170, 140)][i % 4]
            p.rect([x, 560, x + 170, 860], fill=col)
            p.poly([(x - 10, 560), (x + 85, 480), (x + 180, 560)], (110, 70, 60))
            p.rect([x + 30, 620, x + 75, 680], fill=(240, 230, 170)); p.rect([x + 100, 620, x + 145, 680], fill=(240, 230, 170))
            p.rect([x + 65, 760, x + 105, 860], fill=(90, 60, 50))
        p.rect([0, 860, 1080, 900], fill=(170, 170, 176))
        p.rect([0, 900, 1080, 1170], fill=(70, 74, 82))
        for i in range(8):
            x = (i * 180 - t * 900) % 1440 - 180
            p.rect([x, 1030, x + 100, 1044], fill=(240, 240, 236))
        bob = 3 * math.sin(t * 14)
        car(p, 520, 1010 + bob, 0.95)
        for i in range(4):
            y = 860 + i * 34
            x0 = 200 - (t * 600 + i * 60) % 120
            p.line([(x0 - 120, y), (x0, y)], WHITE, 6)
        digital_clock(p, 540, 400, "07:58", t, colour=GREEN, w=380, h=150)
        if t > at(11, "two minutes"):
            pill(p, 820, 520, "2 MINS TO SPARE", prog(t, at(11, "two minutes"), at(11, "two minutes") + 0.3), bg=GREEN, size=32)
        tc = at(11, "It cost")
        if t > tc:
            pill(p, 300, 520, "COST: £0", prog(t, tc, tc + 0.3), bg=YEL, size=40)
            P.money_pop(p, t, tc + 0.1, "£0", x=300, y=720, colour=WHITE)
        return
    P.stats_panel(p, t, a12 - 0.2, [("MONEY", 9, GREEN, "£88.00"), ("HAPPINESS", 50, YEL, "50/100"), ("HOUSE", 25, ORANGE, "25/100")])
    pill(p, 540, 1020, "HAPPINESS -5: NO SLEEP", prog(t, at(12, "Happiness"), at(12, "Happiness") + 0.3), bg=YEL, size=36)
    pill(p, 540, 1110, "HOUSE -15: 14 HOLES", prog(t, at(12, "And the house"), at(12, "And the house") + 0.3), bg=WHITE, size=36)
    for i in range(3):
        p.text((180 + i * 30, 400 - i * 34 - 10 * pulse(t + i * 0.3, 1.2)), "z", f2("anton", 50), WHITE)

@V.scene(13, 14)
def moon_garden(p, t, L):
    a13, e13 = L(13); a14, e14 = L(14)
    nb = 0 if t < at(13, "And the") else min(3, 1 + int((t - at(13, "And the")) / 0.35))
    garden(p, t, "day", holes=14, neighbours=nb)
    if t < a14 - 0.2:
        km = eback(prog(t, a13 + 0.2, a13 + 0.6))
        if km > 0:
            moon(p, 160, 420, 70 * km)
            pill(p, 420, 420, "LOOKS LIKE: THE MOON", prog(t, a13 + 0.4, a13 + 0.7), bg=WHITE, size=34)
        for i, nx in enumerate([250, 560, 840][:nb]):
            pill(p, nx + 70, 480, "?!", prog(t, at(13, "And the") + i * 0.35, at(13, "And the") + i * 0.35 + 0.3), bg=RED, fg=WHITE, size=36)
        P.crumbs(p, 860, 1150, 0.6, "happy", t)
        return
    k = eback(prog(t, a14 - 0.2, a14 + 0.2))
    s = 0.95 * max(0.01, k)
    golf_flag(p, 760, 1124, 1.0, t, "1")
    golf_flag(p, 540, 985, 0.8, t + 1, "2")
    P.alfie(p, 330, 1140, s, "grin", t, talk=V.talk(t, "alfie"))
    if k > 0.9:
        bob = abs(math.sin(t * 3.0)) * 8 * s
        top = 1140 - bob - 110 * s - 150 * s
        golf_club(p, 330 + 150 * s / 2 + 150 * s * .18 * .55, top + 150 * s * .8, s, swing=math.sin(t * 3))
    p.circle(520, 1120, 13, fill=OUT); p.circle(520, 1120, 10, fill=WHITE)
    pill(p, 640, 400, "CRAZY GOLF!", prog(t, at(14, "Crazy"), at(14, "Crazy") + 0.3), bg=GREEN, size=56)

@V.scene(15, 18)
def vote(p, t, L):
    a15, _ = L(15); a16, e16 = L(16); a17, _ = L(17); a18, _ = L(18)
    if t < a16 - 0.3:
        garden(p, t, "day", holes=14)
        P.family(p, t, {"dave": "worried", "sue": "worried", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}, yf=1130)
        pill(p, 540, 390, "YOU DECIDE", prog(t, a15 + 0.3, a15 + 0.6), size=54)
    elif t < a18 - 0.2:
        tA, tB, tC = at(16, "A:"), at(16, "B:"), at(16, "Or C")
        P.vote_card(p, t, tA - 0.7, "WHAT ABOUT THE GARDEN?", OPTIONS, gap=(tC - tA) / 2)
        if t > a17 - 0.1:
            k = eback(prog(t, a17 - 0.1, a17 + 0.3))
            P.ellie(p, 920, 1180, 0.55 * max(0.01, k), "worried", t, talk=V.talk(t, "ellie"))
    else:
        garden(p, t, "day", holes=14)
        golf_flag(p, 760, 1124, 1.0, t, "1")
        P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "worried", "alfie": "grin", "crumbs": "happy"}, yf=1130)
        pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a18 + 0.1, a18 + 0.5), bg=WHITE, size=54)
        pill(p, 540, 490, "DAY 4 TOMORROW", prog(t, at(18, "Day four"), at(18, "Day four") + 0.4), bg=YEL, size=40)

if __name__ == "__main__":
    V.main()
