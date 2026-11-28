import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

DAY = 6
FUND_BEFORE = 133.00
FUND = 233.00         # nobody voted A/B/C, Crumbs chose B (the play); a viewer's "go after the play" won back 5 machines x £20 = +£100
VOTES = {"A": 0, "B": 0, "C": 0}

SCRIPT = [
    # (speaker, spoken text, caption text)
    ("narrator", "Nobody voted A, B or C. So Crumbs chose again. He sat on B: go to the play.", "*Nobody* voted A, B or C. So *Crumbs* chose *again*. He sat on *B*: go to the *play*."),
    ("narrator", "So Dave turned down the two hundred pounds, and went to see the kangaroo.", "So Dave *turned down* the *£200*, and went to see the *kangaroo*."),
    ("alfie", "Hop, hop, hop! I'm the best kangaroo in Year Four!", "*Hop, hop, hop!* I'm the *best kangaroo* in *Year 4!*"),
    ("dave", "That's my boy! I'm not crying. It's the washing powder.", "That's my *boy!* I'm not *crying*. It's the *washing powder*."),
    ("ellie", "I filmed it. Mum, do not put it in the group chat.", "I *filmed* it. Mum, do *not* put it in the *group chat*."),
    ("sue", "Too late. Ninety-four people have seen it.", "Too *late*. *94 people* have seen it."),
    ("narrator", "But one of you commented a new plan: go after the play. So Dave rang the launderette.", "But one of you commented a *new plan*: go *after* the play. So Dave rang the *launderette*."),
    ("narrator", "Another repairman had already fixed half. So Dave fixed the other five, until nine at night.", "Another repairman had already fixed *half*. So Dave fixed the other *5*, until *9 at night*."),
    ("narrator", "Five machines, at twenty pounds each: plus one hundred. The fund climbs to two hundred and thirty-three pounds.", "*5 machines*, at *£20* each: *+£100*. The fund climbs to *£233*."),
    ("narrator", "Happiness jumps to sixty out of a hundred. House: still sixty-five.", "Happiness jumps to *60/100*. House: still *65/100*."),
    ("narrator", "Then Ellie's phone pinged. Her best friend's birthday concert, next Saturday. Tickets: forty-five pounds.", "Then Ellie's phone *pinged*. Her best friend's *birthday concert*, next Saturday. Tickets: *£45*."),
    ("ellie", "Everyone's going. If I miss it, I literally don't exist.", "*Everyone's* going. If I miss it, I *literally* don't *exist*."),
    ("narrator", "A: pay from the holiday jar. B: say no, and Ellie sulks. Or C: a sponsored week with no phone. The street chat pays, but only if she lasts.", "*A*: pay from the *holiday jar*. *B*: say *no*, and Ellie *sulks*. Or *C*: a sponsored week with *no phone*. The street chat *pays*, but only if she *lasts*."),
    ("alfie", "Ellie, with no phone for a week? She'll explode!", "Ellie, with *no phone* for a *week?* She'll *explode!*"),
    ("narrator", "Comment A, B or C, or Crumbs chooses again. Day seven, tomorrow.", "Comment *A*, *B* or *C*, or *Crumbs* chooses again. *Day 7*, tomorrow."),
]

V = Video(
    "pennys-ep06", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS,
    lines=[(sp, txt) for sp, txt, _ in SCRIPT],
    display=[cap for _, _, cap in SCRIPT],
)


OPTIONS = [("A", "Pay from the jar", "-£45   ELLIE HAPPY"),
           ("B", "Say no", "£0   ELLIE SULKS"),
           ("C", "No-phone week", "STREET PAYS, IF SHE LASTS 7 DAYS")]

OUT = P.OUT

def at(i, sub):
    """Approximate time the substring `sub` starts in spoken line i (by character position)."""
    a, b = V.L(i)
    txt = V.lines[i][1]
    k = txt.find(sub)
    return a + (b - a) * max(0, k) / max(1, len(txt))

def mix(c1, c2, k):
    return tuple(int(c1[j] + (c2[j] - c1[j]) * k) for j in range(3))

def shade(c, k=0.82):
    return tuple(int(v * k) for v in c)

def tint(c, k=0.3):
    return tuple(int(v + (255 - v) * k) for v in c)

# ---------------- props (washer, clock, ears copied from Day 5 so they match) ----------------
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

def kangaroo_tail(p, x, yf, s):
    """A stuffed costume tail poking out behind Alfie (drawn before him)."""
    pts = [(x + 40 * s, yf - 130 * s), (x + 150 * s, yf - 40 * s), (x + 190 * s, yf - 6 * s), (x + 120 * s, yf - 20 * s), (x + 20 * s, yf - 90 * s)]
    p.poly([(px + 5, py + 5) for px, py in pts], OUT)
    p.poly(pts, (186, 124, 72))

def hop_y(t, amp=60, speed=6.0):
    return abs(math.sin(t * speed)) * amp

def note(p, x, y, s=1.0, ang=0.0, label="£20", col=(150, 110, 200)):
    w, h = 120 * s, 64 * s
    ca, sa = math.cos(ang), math.sin(ang)
    def rot(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
    p.poly([rot(-w / 2 - 4, -h / 2 - 4), rot(w / 2 + 4, -h / 2 - 4), rot(w / 2 + 4, h / 2 + 4), rot(-w / 2 - 4, h / 2 + 4)], OUT)
    p.poly([rot(-w / 2, -h / 2), rot(w / 2, -h / 2), rot(w / 2, h / 2), rot(-w / 2, h / 2)], col)
    p.circle(*rot(-w * .25, 0), h * .28, fill=tint(col))
    p.text(rot(w * .18, 0), label, f2("anton", max(8, int(30 * s))), WHITE)

def phone_frame(p, cx, cy, w, h, k, header, head_col=(70, 160, 100)):
    """A phone that pops in; returns True once it is fully open."""
    if k <= 0: return False
    ww, hh = w * k, h * k
    p.rr([cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2], 60 * k, fill=(30, 34, 44), shadow=True)
    p.rr([cx - ww / 2 + 18, cy - hh / 2 + 18, cx + ww / 2 - 18, cy + hh / 2 - 18], 46 * k, fill=(240, 244, 250))
    if k < 0.95: return False
    p.rr([cx - w / 2 + 28, cy - h / 2 + 28, cx + w / 2 - 28, cy - h / 2 + 118], 40, fill=head_col)
    p.text((cx, cy - h / 2 + 74), header, f2("dm", 34), WHITE)
    return True

def chat_bubble(p, x0, y, w, k, lines, col, size=38, right=False):
    if k <= 0: return
    q = eback(clamp(k))
    h = 30 + 58 * len(lines)
    if right:
        p.rr([x0 + w * (1 - q), y, x0 + w, y + h], 28, fill=col)
    else:
        p.rr([x0, y, x0 + w * q, y + h], 28, fill=col)
    if q < 0.9: return
    for j, ln in enumerate(lines):
        p.text((x0 + 26, y + 44 + j * 58), ln, f2("dm", size), INK, anchor="lm")

def heart(p, x, y, r, col=RED):
    """A drawn heart (the font has no heart glyph)."""
    for pad, c in ((4, OUT), (0, col)):
        p.circle(x - r * .5, y - r * .25, r * .55 + pad, fill=c)
        p.circle(x + r * .5, y - r * .25, r * .55 + pad, fill=c)
        p.poly([(x - r * 1.03 - pad, y - r * .05), (x + r * 1.03 + pad, y - r * .05), (x, y + r * 1.05 + pad)], c)

def tear_drops(p, x, yf, s, t, t0):
    """Happy tears running from Dave's eyes (matches pennys.dave's head position)."""
    if t < t0: return
    hr = 92 * s
    top = yf - 150 * s - 240 * s * (1 + 0.012 * math.sin(t * 2.4))
    hy = top - hr * .82 + math.sin(t * 2.0) * 4 * s
    for sx in (-1, 1):
        ex, ey = x + sx * hr * .34, hy + hr * .16
        for j in range(3):
            q = ((t - t0) * 1.4 + j / 3) % 1
            p.circle(ex + sx * 10 * q, ey + 120 * s * q, (9 - 4 * q) * s * 1.4, fill=(120, 190, 255))

# ---------------- backgrounds ----------------
CURTAIN, CURTAIN_D = (176, 40, 56), (140, 28, 44)

def stage(p, t, banner=True):
    """The school hall stage: red curtains, a painted outback backdrop and a wooden floor."""
    p.rect([0, 300, 1080, 1010], fill=(46, 36, 70))
    # painted cardboard outback backdrop
    p.rr([150, 410, 930, 906], 10, fill=OUT)
    p.rect([156, 416, 924, 900], fill=(140, 200, 240))
    p.rect([156, 740, 924, 900], fill=(214, 120, 60))
    p.poly([(210, 742), (260, 668), (400, 650), (470, 742)], (170, 80, 50))
    p.circle(820, 500, 48, fill=YEL)
    for k in range(8):
        a = t * 0.6 + k * math.pi / 4
        p.line([(820 + 60 * math.cos(a), 500 + 60 * math.sin(a)), (820 + 78 * math.cos(a), 500 + 78 * math.sin(a))], YEL, 6)
    p.rect([824, 600, 842, 742], fill=(120, 86, 60))
    for dx, dy, r in ((0, -10, 46), (-36, 12, 34), (36, 12, 34)):
        p.circle(833 + dx, 600 + dy, r, fill=(90, 160, 90))
    if banner:
        p.rr([186, 432, 470, 500], 14, fill=(250, 248, 238))
        p.text((328, 467), "YEAR 4 PLAY", f2("anton", 40), (176, 40, 56))
    # wooden stage floor and its front edge
    p.rect([0, 900, 1080, 1004], fill=(160, 110, 66))
    for y in (930, 962):
        p.line([(0, y), (1080, y)], (176, 124, 78), 4)
    with p.flat():
        p.ell([330, 920, 750, 1000], fill=(214, 170, 110))      # spotlight pool
    p.rect([0, 1000, 1080, 1030], fill=(110, 70, 44))
    p.rect([0, 1030, 1080, 1170], fill=(34, 28, 46))
    # curtains (gentle sway) and the scalloped pelmet
    sway = math.sin(t * 1.3) * 6
    for x0, x1 in ((0, 150), (930, 1080)):
        p.rect([x0, 300, x1, 1004], fill=CURTAIN)
        for k in range(4):
            fx = x0 + 18 + k * 36 + sway * (1 if x0 == 0 else -1)
            p.rect([fx, 300, fx + 12, 1004], fill=CURTAIN_D)
    p.rect([0, 300, 1080, 360], fill=CURTAIN)
    for k in range(9):
        p.circle(60 + k * 120, 360, 60, fill=CURTAIN)
        p.circle(60 + k * 120, 352, 50, fill=CURTAIN_D)
        p.circle(60 + k * 120, 344, 48, fill=CURTAIN)
    p.rect([0, 300, 1080, 330], fill=(200, 160, 70))

def launderette_bg(p, t):
    p.rect([0, 300, 1080, 1010], fill=(170, 214, 222))
    for yy in range(320, 1010, 70):
        p.line([(0, yy), (1080, yy)], (156, 200, 210), 3)
    p.rect([0, 1010, 1080, 1170], fill=(214, 214, 222))
    for xx in range(0, 1080, 90):
        for yy in (1010, 1090):
            if ((xx // 90) + (yy // 80)) % 2:
                p.rect([xx, yy, xx + 90, yy + 80], fill=(196, 196, 206))

WASH_X = (140, 340, 540, 740, 940)

# ---------------- fixed HUD ----------------
@V.fixed
def hud_band(p, t):
    k = eo(prog(t, V.L(8)[0] + 2.0, V.L(8)[0] + 3.4))
    P.hud(p, DAY, FUND_BEFORE + (FUND - FUND_BEFORE) * k)

def FIX_TIMES():
    """When each of the last five launderette machines starts spinning in line 7."""
    t0, e7 = at(7, "So Dave") + 0.2, V.L(7)[1] - 0.2
    return [t0 + (e7 - t0) * k / 5 for k in range(5)]

def NOTE_T0():
    return at(8, "plus") - 0.1

@V.sounds
def sounds(L):
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh")]
    ts = at(0, "He sat")
    out += [(ts - 0.5, "boing"), (ts + 0.3, "thud"), (ts + 0.45, "ding")]
    a1, e1 = L(1)
    out += [(a1 + 0.2, "pop"), (at(1, "turned down"), "pop"), (at(1, "two hundred") + 0.3, "thud"), (at(1, "kangaroo"), "ding")]
    out += [(at(2, "Hop") + k * 0.38, "boing") for k in range(3)] + [(at(2, "best"), "ding")]
    out += [(L(3)[0] + 0.1, "pop"), (at(3, "crying"), "boing")]
    out += [(L(4)[0] + 0.2, "ding"), (at(4, "do not"), "thud")]
    out += [(L(5)[0] + 0.1, "pop"), (at(5, "Ninety"), "ding")]
    out += [(L(6)[0] + 0.2, "ding"), (at(6, "new plan"), "pop"), (at(6, "rang"), "ding"), (at(6, "rang") + 0.5, "ding")]
    out += [(at(7, "half"), "pop")] + [(x, "pop") for x in FIX_TIMES()] + [(at(7, "nine"), "thud")]
    n0 = NOTE_T0()
    out += [(n0 + j * 0.2, "pop") for j in range(5)] + [(n0 + 0.4, "cash"), (at(8, "climbs"), "cash")]
    out += [(L(9)[0] + 0.2, "pop"), (at(9, "Happiness") + 0.6, "ding"), (at(9, "House"), "pop")]
    out += [(at(10, "pinged"), "ding"), (at(10, "Her best"), "pop"), (at(10, "Tickets"), "cash")]
    out += [(L(11)[0] + 0.1, "boing"), (at(11, "literally"), "thud")]
    out += [(at(12, "A:"), "pop"), (at(12, "B:") - 0.1, "pop"), (at(12, "Or C") - 0.1, "pop"), (at(12, "only if"), "thud")]
    out += [(L(13)[0] + 0.1, "boing"), (at(13, "explode"), "thud")]
    out += [(L(14)[0] + 0.1, "pop"), (at(14, "or Crumbs"), "boing"), (at(14, "Day seven"), "ding")]
    return out

# ---------------- scenes ----------------
@V.scene(0)
def hook(p, t, L):
    a0, e0 = L(0)
    p.text((540, 360), "YOUR VOTES", f2("anton", 72), YEL)
    P.result_bars(p, t, 0.2, VOTES, top=440)
    labels = ["TAKE THE JOB", "GO TO THE PLAY", "6AM START, RACE BACK"]
    for i, lab in enumerate(labels):
        k = prog(t, 0.3 + i * 0.2, 0.6 + i * 0.2)
        if k > 0:
            p.text((560, 440 + i * 150 + 55), lab, f2("dm", 36), WHITE)
    ts = at(0, "He sat")
    # Crumbs trots in and sits by the B bar; a paw print stamps it
    cx = lerp(1250, 820, eo(prog(t, ts - 0.7, ts + 0.2)))
    trot = abs(math.sin(t * 10)) * 10 * (1 - prog(t, ts + 0.1, ts + 0.3))
    P.crumbs(p, cx, 1150 - trot, 0.62, "happy", t)
    q = prog(t, ts + 0.3, ts + 0.6)
    if q > 0:
        paw(p, 250, 650, 40 * eback(q), WHITE)
        pill(p, 360, 1060, "CRUMBS PICKED B", prog(t, ts + 0.4, ts + 0.7), bg=P.OPT_COLS["B"], size=40)
        pill(p, 300, 940, "THE SCHOOL PLAY", prog(t, at(0, "go to the play"), at(0, "go to the play") + 0.3), bg=WHITE, size=34)
    # title card: the result is on screen from the first frame, then it slides away
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0, dx = 560, -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.3, 0.65)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "DAY 6", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "NOBODY VOTED. THE DOG CHOSE.", f2("anton", max(10, int(78 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "B: THE PLAY. SO GOODBYE, £200?", f2("dm", max(8, int(40 * k3))), (255, 160, 190))

@V.scene(1)
def turn_down(p, t, L):
    a1, e1 = L(1)
    P.living_room(p, t, FUND_BEFORE / 1000)
    k = eback(prog(t, a1 - 0.25, a1 + 0.15))
    s = 0.8 * max(0.01, k)
    P.dave(p, 200, 1150, s, "happy", t, hold="phone")
    ok = phone_frame(p, 660, 770, 520, 640, eback(prog(t, a1 - 0.1, a1 + 0.3)), "LAUNDERETTE, HIGH ST")
    if ok:
        chat_bubble(p, 430, 560, 380, prog(t, a1 + 0.2, a1 + 0.5), ["10 machines,", "£200, 2pm?"], (120, 210, 140))
        td = at(1, "turned down")
        chat_bubble(p, 470, 760, 380, prog(t, td, td + 0.35), ["Sorry!", "Kangaroo duty."], (150, 200, 255), right=True)
        t2 = at(1, "two hundred") + 0.3
        if t > t2:
            pill(p, 660, 980, "£200", 1.0, bg=GREEN, size=56)
            cross(p, 660, 980, 70, prog(t, t2, t2 + 0.25), shake_t=t - t2)
    # follow ask, on screen before the 10-second mark
    pill(p, 540, 395, "FOLLOW: A NEW EPISODE EVERY DAY", prog(t, a1 + 0.3, a1 + 0.7), bg=YEL, size=36)

@V.scene(2, 5)
def school_play(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3); a4, e4 = L(4); a5, e5 = L(5)
    stage(p, t, banner=t < a3 - 0.2)
    if t < a3 - 0.2:
        # Alfie, big, hopping in the spotlight
        k = eback(prog(t, a2 - 0.3, a2 + 0.1))
        s = 1.0 * max(0.01, k)
        hy = hop_y(t, 70, 6.5)
        kangaroo_tail(p, 600, 990 - hy, s)
        kangaroo_alfie(p, 600, 990 - hy, s, "grin", t, wave=1, talk=V.talk(t, "alfie"))
        for j, word in enumerate(("HOP!", "HOP!", "HOP!")):
            th = at(2, "Hop") + j * 0.38
            if t > th:
                pill(p, 260 + j * 150, 580 + j * 60, word, prog(t, th, th + 0.25), bg=YEL, size=44)
        tb = at(2, "best")
        if t > tb:
            pill(p, 540, 1080, "BEST KANGAROO IN YEAR 4", prog(t, tb, tb + 0.3), bg=GREEN, size=38)
        return
    # the front row: Dave, Sue and Ellie watching, with Alfie still hopping on stage behind them
    hy = hop_y(t, 36, 6.5)
    kangaroo_tail(p, 640, 960 - hy, 0.55)
    kangaroo_alfie(p, 640, 960 - hy, 0.55, "grin", t)
    sc = 0.72
    dmood = "grin" if t < at(3, "I'm not") else "happy"
    P.dave(p, 175, 1150, sc, dmood, t, talk=V.talk(t, "dave"))
    tear_drops(p, 175, 1150, sc, t, at(3, "I'm not"))
    P.sue(p, 370, 1150, sc * 0.98, "grin", t, hold="phone", talk=V.talk(t, "sue"))
    P.ellie(p, 905, 1150, sc * 0.95, "neutral" if t < a4 else ("shock" if t > a5 else "worried"), t, hold="phone", talk=V.talk(t, "ellie"))
    if a3 - 0.2 <= t < a4 - 0.2:
        tc = at(3, "crying")
        pill(p, 420, 475, "NOT CRYING", prog(t, tc, tc + 0.3), bg=(150, 200, 255), size=42)
        tw = at(3, "washing")
        pill(p, 450, 575, "(IT'S THE WASHING POWDER)", prog(t, tw, tw + 0.3), bg=WHITE, size=32)
        return
    if t < a5 - 0.2:
        # Ellie filming
        q = prog(t, a4, a4 + 0.3)
        if q > 0:
            p.rr([250, 440, 420, 500], 30, fill=(20, 30, 50))
            p.circle(290, 470, 16 * eback(q), fill=RED if (t % 1.0) < 0.6 else (150, 60, 60))
            p.text((315, 471), "REC", f2("anton", 40), WHITE, anchor="lm")
        tn = at(4, "do not")
        pill(p, 480, 575, "DO NOT POST IT", prog(t, tn, tn + 0.3), bg=RED, fg=WHITE, size=40)
        return
    # Sue already posted it
    tn = at(5, "Ninety")
    pill(p, 460, 470, "POSTED IN THE STREET CHAT", prog(t, a5, a5 + 0.3), bg=(120, 210, 140), size=32)
    if t > tn:
        q = eback(prog(t, tn, tn + 0.3))
        p.rr([450 - 230 * q, 590 - 70 * q, 450 + 230 * q, 590 + 70 * q], 30, fill=(20, 30, 50))
        big_number(p, t, tn, 94, cx=450, cy=592, size=100, start=0, dur=0.9, fill=YEL, fmt="{} VIEWS")
    pill(p, 790, 690, "MUM!", prog(t, tn + 0.6, tn + 0.9), bg=(200, 170, 255), size=44)

@V.scene(6, 7)
def plan_d(p, t, L):
    a6, e6 = L(6); a7, e7 = L(7)
    if t < a7 - 0.2:
        P.living_room(p, t, FUND_BEFORE / 1000)
        # the viewer's comment
        c = eback(prog(t, a6 - 0.1, a6 + 0.3))
        if c > 0:
            x0, y0, x1 = 120, 380, 960
            y1 = y0 + 230 * c
            p.rr([x0, y0, x1, y1], 30, fill=WHITE, shadow=True)
            if c > 0.9:
                p.text((x0 + 36, y0 + 44), "A COMMENT ON DAY 5", f2("dm", 30), (110, 120, 140), anchor="lm")
                P.ocircle(p, x0 + 80, y0 + 140, 44, (255, 180, 120), ow=4, shaded=False)
                p.text((x0 + 80, y0 + 142), "?", f2("anton", 48), INK)
                p.text((x0 + 150, y0 + 140), "“Or go after play”", f2("dm", 54), INK, anchor="lm")
                tn = at(6, "new plan")
                if t > tn:
                    pulse_k = 1 + 0.08 * math.sin(t * 8)
                    heart(p, x1 - 66, y0 + 140, 30 * pulse_k)
        tn = at(6, "new plan")
        pill(p, 540, 700, "A NEW PLAN!", prog(t, tn, tn + 0.3), bg=YEL, size=48)
        tr = at(6, "rang")
        k = eback(prog(t, tr - 0.5, tr - 0.1))
        if k > 0:
            P.dave(p, 300, 1150, 0.82 * max(0.01, k), "grin", t, hold="phone")
            for j in range(3):          # ringing arcs by his phone
                r = 30 + j * 26 + 10 * math.sin(t * 12)
                p.arc([190 - r, 880 - r, 190 + r, 880 + r], 200, 320, WHITE, 6)
            pill(p, 760, 900, "RING RING...", prog(t, tr, tr + 0.3), bg=WHITE, size=40)
        return
    # the launderette: half already fixed, Dave does the other five
    launderette_bg(p, t)
    th = at(7, "half")
    ft = FIX_TIMES()
    for row, yb in enumerate((690, 920)):
        for i, x in enumerate(WASH_X):
            if row == 0:
                spin = 1.0 if t > th else 0.0
            else:
                spin = prog(t, ft[i], ft[i] + 0.25)
            washer(p, x, yb, 0.42, t, spin=spin, shake=0.0)
            if row == 0 and t > th:
                tick(p, x + 52, yb - 150, 22, prog(t, th + i * 0.08, th + 0.25 + i * 0.08))
            if row == 1 and t > ft[i] + 0.2:
                tick(p, x + 52, yb - 150, 22, prog(t, ft[i] + 0.2, ft[i] + 0.45))
    pill(p, 540, 520, "ALREADY FIXED BY SOMEONE ELSE", prog(t, th, th + 0.3) * (1 - prog(t, ft[0] - 0.3, ft[0])), bg=WHITE, size=32)
    # Dave walks along the second row, machine to machine
    x = WASH_X[0]
    for i in range(1, 5):
        x = lerp(x, WASH_X[i], eio(prog(t, ft[i] - 0.45, ft[i] - 0.05)))
    k = eback(prog(t, a7 - 0.25, a7 + 0.15))
    moving = any(ft[i] - 0.45 < t < ft[i] - 0.05 for i in range(1, 5))
    bob = abs(math.sin(t * 9)) * 8 if moving else 0
    n = sum(1 for f in ft if t >= f)
    P.dave(p, x, 1150 - bob, 0.5 * max(0.01, k), "happy" if n < 4 else "tired", t, hold="wrench")
    mins = int(300 * prog(t, ft[0] - 0.2, e7 - 0.1))
    digital_clock(p, 860, 390, f"{16 + mins // 60:02d}:{mins % 60:02d}", t, colour=GREEN, w=260, h=110, blink=False)
    p.rr([90, 352, 590, 428], 20, fill=(20, 30, 50))
    p.text((340, 391), "LAUNDERETTE", f2("anton", 50), (150, 220, 255))
    if t > ft[0]:
        pill(p, 760, 1080, f"DAVE: {n}/5", 1.0, bg=YEL, size=36)

@V.scene(8, 9)
def money(p, t, L):
    a8, e8 = L(8); a9, e9 = L(9)
    if t < a9 - 0.2:
        n0 = NOTE_T0()
        lv = lerp(FUND_BEFORE, FUND, eo(prog(t, n0 + 0.2, n0 + 1.4))) / 1000
        P.jar(p, 300, 1090, 2.4, lv)
        p.text((300, 1135), "HOLIDAY JAR", f2("dm", 34), WHITE)
        # five fixed machines, each pays £20, and the notes fly into the jar
        tm = a8 + 0.1
        tw = at(8, "twenty")
        for j in range(5):
            mx = 540 + j * 100
            q = eback(prog(t, tm + j * 0.18, tm + 0.3 + j * 0.18))
            if q > 0:
                washer(p, mx, 560, 0.3 * q, t, spin=1.0)
                tick(p, mx + 34, 470, 16, prog(t, tm + 0.3 + j * 0.18, tm + 0.5 + j * 0.18))
            if t > tw + j * 0.12 and t < n0 + j * 0.2:
                pill(p, mx, 620, "£20", prog(t, tw + j * 0.12, tw + 0.25 + j * 0.12), bg=GREEN, size=30)
        for j in range(5):
            q = prog(t, n0 + j * 0.2, n0 + 0.8 + j * 0.2)
            if 0 < q < 1:
                x = lerp(540 + j * 100, 300, eo(q)); y = lerp(620, 820, eo(q)) - 160 * math.sin(math.pi * q)
                note(p, x, y, 1.1, ang=q * 3 + j)
        P.money_pop(p, t, n0, "+£100", x=740, y=760, colour=GREEN)
        tcl = at(8, "climbs")
        big_number(p, t, tcl, 233, cx=740, cy=820, size=210, start=133, dur=1.3, fill=GREEN, fmt="£{}")
        pill(p, 740, 980, "£767 STILL TO GO", prog(t, tcl + 1.0, tcl + 1.3), bg=WHITE, size=36)
        return
    P.stats_panel(p, t, a9 - 0.2, [("MONEY", 23.3, GREEN, "£233.00"), ("HAPPINESS", 60, YEL, "60/100"), ("HOUSE", 65, ORANGE, "65/100")])
    th = at(9, "Happiness") + 0.6
    pill(p, 540, 1010, "HAPPINESS +15: THE KANGAROO WAS WORTH IT", prog(t, th, th + 0.3), bg=YEL, size=30)
    tp = at(9, "House")
    pill(p, 540, 1100, "HOUSE: NO CHANGE", prog(t, tp, tp + 0.3), bg=WHITE, size=34)

@V.scene(10, 11)
def concert(p, t, L):
    a10, e10 = L(10); a11, e11 = L(11)
    if t < a11 - 0.2:
        P.living_room(p, t, FUND / 1000)
        tp = at(10, "pinged")
        k = eback(prog(t, a10 - 0.1, a10 + 0.3))
        P.ellie(p, 190, 1150, 0.78 * max(0.01, k), "shock" if t > at(10, "Her best") else "neutral", t, hold="phone")
        buzz = math.sin(t * 50) * 6 * (1 - prog(t, tp, tp + 0.6)) if t > tp else 0
        ok = phone_frame(p, 660 + buzz, 760, 520, 660, eback(prog(t, tp - 0.1, tp + 0.3)), "BEST FRIEND", head_col=(128, 92, 200))
        if ok:
            tb = at(10, "Her best")
            if t < tb:
                for j in range(3):   # typing dots
                    p.circle(530 + j * 40, 600, 12 + 4 * math.sin(t * 10 - j), fill=(150, 160, 176))
            else:
                chat_bubble(p, 430, 560, 400, prog(t, tb, tb + 0.3), ["My birthday", "concert!!"], (220, 200, 255))
                tn = at(10, "next Saturday")
                chat_bubble(p, 430, 720, 400, prog(t, tn, tn + 0.3), ["Next Saturday."], (220, 200, 255))
                tt = at(10, "Tickets")
                chat_bubble(p, 430, 820, 400, prog(t, tt, tt + 0.3), ["£45 a ticket!"], (220, 200, 255))
                if t > tt:
                    pill(p, 660, 1000, "£45", prog(t, tt + 0.2, tt + 0.5), bg=RED, fg=WHITE, size=60)
        return
    P.living_room(p, t, FUND / 1000)
    k = eback(prog(t, a11 - 0.25, a11 + 0.15))
    tl = at(11, "literally")
    P.ellie(p, 400, 1150, 1.05 * max(0.01, k), "worried" if t < tl else "shock", t, hold="phone", talk=V.talk(t, "ellie"))
    te = at(11, "Everyone")
    pill(p, 780, 470, "EVERYONE'S GOING", prog(t, te + 0.1, te + 0.4), bg=(200, 170, 255), size=38)
    pill(p, 780, 580, "LITERALLY", prog(t, tl, tl + 0.3), bg=YEL, size=44)
    tx = at(11, "don't exist")
    if t > tx:
        pill(p, 780, 680, "DOESN'T EXIST", prog(t, tx, tx + 0.3), bg=WHITE, size=44)
        for j in range(6):
            ang = t * 2 + j * 1.05
            sparkle(p, 400 + 200 * math.cos(ang), 760 + 230 * math.sin(ang), 14, fill=(220, 200, 255))

@V.scene(12, 14)
def vote(p, t, L):
    a12, e12 = L(12); a13, e13 = L(13); a14, _ = L(14)
    if t < a13 - 0.2:
        tA, tB, tC = at(12, "A:"), at(12, "B:"), at(12, "Or C")
        P.vote_card(p, t, tA - 0.6, "ELLIE'S CONCERT?", OPTIONS, gap=(tC - tA) / 2)
        to = at(12, "only if")
        if t > to:
            pill(p, 860, 975, "CAN SHE LAST?", prog(t, to, to + 0.3), bg=RED, fg=WHITE, size=32)
        return
    P.living_room(p, t, FUND / 1000)
    if t < a14 - 0.2:
        k = eback(prog(t, a13 - 0.25, a13 + 0.15))
        P.alfie(p, 260, 1150, 1.0 * max(0.01, k), "grin", t, talk=V.talk(t, "alfie"))
        tx = at(13, "explode")
        shake = math.sin(t * 45) * 8 if t > tx else 0
        P.ellie(p, 760 + shake, 1150, 0.9, "shock" if t > tx else "worried", t, hold="phone")
        tw = at(13, "no phone")
        pill(p, 560, 420, "7 DAYS. NO PHONE.", prog(t, tw, tw + 0.3), bg=WHITE, size=44)
        if t > tx:
            pill(p, 760, 540, "BOOM?!", prog(t, tx, tx + 0.3), bg=RED, fg=WHITE, size=56)
            for j in range(8):
                ang = j * math.pi / 4 + t
                r = 150 + 30 * math.sin(t * 10 + j)
                sparkle(p, 760 + r * math.cos(ang), 820 + r * math.sin(ang), 18, fill=YEL if j % 2 else ORANGE)
        return
    m = {"dave": "happy", "sue": "grin", "ellie": "worried", "alfie": "grin", "crumbs": "happy"}
    xs, yf, sc = (170, 390, 610, 800, 975), 1130, 0.82
    P.sue(p, xs[1], yf, sc, m["sue"], t, hold="phone")
    P.dave(p, xs[0], yf, sc, m["dave"], t, hold="wrench")
    P.ellie(p, xs[2], yf, sc * .95, m["ellie"], t, hold="phone")
    kangaroo_alfie(p, xs[3], yf, sc * .95, m["alfie"], t)
    P.crumbs(p, xs[4], yf, sc * .55, m["crumbs"], t)
    pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a14 + 0.1, a14 + 0.5), bg=WHITE, size=54)
    tcr = at(14, "or Crumbs")
    if t > tcr:
        pill(p, 540, 490, "OR CRUMBS CHOOSES AGAIN", prog(t, tcr, tcr + 0.3), bg=RED, fg=WHITE, size=36)
    td = at(14, "Day seven")
    pill(p, 540, 580, "DAY 7 TOMORROW", prog(t, td, td + 0.4), bg=YEL, size=40)

if __name__ == "__main__":
    V.main()
