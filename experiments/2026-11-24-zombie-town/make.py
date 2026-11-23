"""Test format: interactive survival story, comments vote A/B/C. Cartoon, no gore."""
import os, sys, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

V = Video(
    "test-zombie-town", episode=None, series="ZOMBIE TOWN · PART 1", voice="bm_lewis", voice_lang="en-gb",
    music="pad", title="*10 seconds*. What do you *grab*?",
    lines=[
        "It's three in the morning. Your phone buzzes. Don't go outside.",
        "You look out of the window. The whole street is shuffling.",
        "Clive from number nine is trying to eat a garden gnome.",
        "Then you hear it. Something is scratching at your back door.",
        "You've got ten seconds. You can only grab one thing.",
        "A. The cricket bat by the stairs.",
        "B. Your car keys. Make a run for it.",
        "Or C. The dog. He's useless, but he's a very good boy.",
        "Comment A, B or C.",
        "The most votes decides what happens in part two.",
        "Follow, so you don't miss it.",
    ],
    display=[
        "It's *3* in the *morning*. Your phone buzzes. *Don't go outside.*",
        "You look out of the window. The whole street is *shuffling*.",
        "*Clive* from number nine is trying to eat a garden *gnome*.",
        "Then you hear it. Something is *scratching* at your *back door*.",
        "You've got *10 seconds*. You can only grab *one* thing.",
        "*A*. The cricket *bat* by the stairs.",
        "*B*. Your car *keys*. Make a *run* for it.",
        "Or *C*. The *dog*. He's useless, but he's a very *good boy*.",
        "Comment *A*, *B* or *C*.",
        "The most votes decides what happens in *part two*.",
        "*Follow*, so you don't miss it.",
    ],
)

NIGHT1, NIGHT2 = (18, 22, 48), (40, 44, 86)
ZSKIN, ZSKIN_D = (140, 196, 120), (110, 160, 96)
OUT = P.OUT

def night_sky(p, t):
    for i in range(12):
        c = tuple(int(NIGHT1[j] + (NIGHT2[j] - NIGHT1[j]) * i / 11) for j in range(3))
        p.rect([0, 300 + i * 60, 1080, 300 + (i + 1) * 60], fill=c)
    for i in range(40):
        x = (i * 173) % 1080; y = 320 + (i * 97) % 380
        p.circle(x, y, 1.5 + 1.2 * (0.5 + 0.5 * math.sin(t * 2 + i)), fill=(210, 220, 255))
    for i in range(4):
        p.circle(860, 430, 90 - i * 8 + 28 - i * 7, fill=(40 + i * 10, 46 + i * 10, 90 + i * 10))
    p.circle(860, 430, 62, fill=(240, 236, 210))
    p.circle(840, 418, 12, fill=(222, 216, 190)); p.circle(878, 448, 8, fill=(222, 216, 190))

def zombie(p, x, yf, s=1.0, t=0.0, seed=0, shirt=(90, 110, 140), gnome=False):
    sway = math.sin(t * 2.2 + seed) * 8 * s
    step = math.sin(t * 2.2 + seed)
    P.ground_shadow(p, x, yf, 70 * s)
    for sx, ph in ((-1, step), (1, -step)):                 # shuffling legs
        lx = x + sx * 24 * s + ph * 10 * s
        P.orr(p, [lx - 15 * s, yf - 150 * s, lx + 15 * s, yf - 8 * s], 12 * s, (70, 70, 90), ow=4)
        p.ell([lx - 26 * s, yf - 18 * s, lx + 22 * s, yf + 8 * s], fill=OUT)
    top = yf - 330 * s
    P.orr(p, [x - 62 * s + sway, top, x + 62 * s + sway, yf - 130 * s], 30 * s, shirt, ow=5, shade_side="r")
    p.poly([(x - 62 * s + sway, yf - 150 * s), (x - 40 * s + sway, yf - 120 * s), (x - 20 * s + sway, yf - 150 * s)], shirt)  # torn hem
    p.poly([(x + 10 * s + sway, yf - 150 * s), (x + 30 * s + sway, yf - 118 * s), (x + 50 * s + sway, yf - 150 * s)], shirt)
    p.circle(x - 20 * s + sway, top + 80 * s, 10 * s, fill=P.shade(shirt, 0.7))                                      # patch
    for sy in (0, 1):                                       # arms straight out
        ay = top + (40 + sy * 26) * s
        P.oline(p, (x + sway, ay), (x + 150 * s + sway, ay + 10 * s * math.sin(t * 3 + seed + sy)), ZSKIN_D if sy else ZSKIN, 22 * s, ow=4)
        P.ocircle(p, x + 158 * s + sway, ay + 10 * s * math.sin(t * 3 + seed + sy), 16 * s, ZSKIN, ow=4, shaded=False)
    if gnome:                                               # holding a garden gnome
        gx, gy = x + 175 * s + sway, top + 30 * s
        p.poly([(gx - 30 * s, gy - 10 * s), (gx, gy - 80 * s), (gx + 30 * s, gy - 10 * s)], RED)
        P.ocircle(p, gx, gy + 8 * s, 22 * s, P.SKIN, ow=3, shaded=False)
        p.poly([(gx - 22 * s, gy + 14 * s), (gx, gy + 60 * s), (gx + 22 * s, gy + 14 * s)], WHITE)
    hx, hy = x + sway * 1.3, top - 70 * s
    P.ocircle(p, hx, hy, 72 * s, ZSKIN, ow=5)
    p.ell([hx - 46 * s, hy - 70 * s, hx + 20 * s, hy - 40 * s], fill=(70, 80, 60))   # scruffy hair
    p.circle(hx - 26 * s, hy - 8 * s, 18 * s, fill=WHITE); p.circle(hx - 22 * s, hy - 6 * s, 6 * s, fill=INK)
    p.ell([hx + 12 * s, hy - 2 * s, hx + 46 * s, hy + 16 * s], fill=WHITE); p.circle(hx + 30 * s, hy + 8 * s, 5 * s, fill=INK)
    mo = 10 + 8 * (0.5 + 0.5 * math.sin(t * 4 + seed))
    p.rr([hx - 28 * s, hy + 26 * s, hx + 26 * s, hy + (26 + mo) * s], 8 * s, fill=(60, 30, 40))
    p.rect([hx - 18 * s, hy + 26 * s, hx - 8 * s, hy + 34 * s], fill=WHITE)
    p.rect([hx + 6 * s, hy + 26 * s, hx + 16 * s, hy + 34 * s], fill=WHITE)

def street(p, t):
    night_sky(p, t)
    for i, (x, w, h, c) in enumerate([(120, 220, 300, (70, 60, 80)), (380, 240, 340, (60, 70, 90)), (660, 220, 290, (80, 66, 70)), (930, 240, 330, (60, 64, 84))]):
        p.rect([x - w / 2, 980 - h, x + w / 2, 980], fill=c)
        p.poly([(x - w / 2 - 14, 980 - h + 2), (x, 980 - h - 90), (x + w / 2 + 14, 980 - h + 2)], P.shade(c, 0.7))
        for wx in (x - w * 0.25, x + w * 0.25):
            on = (i + int(t * 0.7)) % 3 != 0 or wx > x
            p.rect([wx - 28, 980 - h + 60, wx + 28, 980 - h + 130], fill=(255, 214, 120) if on else (34, 38, 60))
    p.rect([0, 980, 1080, 1170], fill=(44, 48, 62))
    p.rect([0, 980, 1080, 996], fill=(70, 74, 90))
    for i in range(0, 1080, 120):
        p.rect([i + 30, 1080, i + 90, 1088], fill=(90, 94, 110))
    p.rect([990, 640, 1004, 990], fill=(30, 32, 44))                # street lamp
    for i in range(5):
        p.circle(997, 640, 80 - i * 14, fill=(60 + i * 30, 60 + i * 28, 70 + i * 16))
    p.circle(997, 640, 18, fill=(255, 236, 170))

def window_frame(p):
    p.rect([0, 300, 1080, 360], fill=(52, 40, 46)); p.rect([0, 1110, 1080, 1170], fill=(52, 40, 46))
    p.rect([0, 300, 70, 1170], fill=(52, 40, 46)); p.rect([1010, 300, 1080, 1170], fill=(52, 40, 46))
    p.rect([530, 300, 550, 1170], fill=(52, 40, 46))
    for x0 in (40, 900):
        p.rr([x0, 300, x0 + 140, 1150], 30, fill=(110, 40, 60))
        p.rr([x0 + 20, 300, x0 + 50, 1150], 14, fill=(130, 54, 74))

def icon_bat(p, cx, cy, s=1.0):
    P.oline(p, (cx - 90 * s, cy + 60 * s), (cx + 80 * s, cy - 60 * s), (200, 150, 90), 26 * s, ow=4)
    P.oline(p, (cx - 90 * s, cy + 60 * s), (cx - 50 * s, cy + 32 * s), (40, 40, 50), 18 * s, ow=4)

def icon_keys(p, cx, cy, s=1.0):
    p.circle(cx - 40 * s, cy - 20 * s, 34 * s, outline=OUT, width=12 * s)
    p.circle(cx - 40 * s, cy - 20 * s, 34 * s, outline=(220, 220, 230), width=7 * s)
    for k, ang in enumerate((-0.3, 0.4)):
        x0, y0 = cx - 10 * s, cy
        x1, y1 = x0 + 110 * s * math.cos(ang), y0 + 110 * s * math.sin(ang)
        P.oline(p, (x0, y0), (x1, y1), BRASS if k == 0 else (200, 205, 215), 16 * s, ow=4)
    p.rr([cx + 40 * s, cy - 70 * s, cx + 100 * s, cy - 20 * s], 12 * s, fill=OUT)
    p.rr([cx + 44 * s, cy - 66 * s, cx + 96 * s, cy - 24 * s], 10 * s, fill=(40, 40, 50))
    p.circle(cx + 70 * s, cy - 45 * s, 9 * s, fill=RED)

def option_card(p, t, t0, y, letter, title, icon, h=170):
    q = eback(prog(t, t0, t0 + 0.35))
    if q <= 0: return
    col = P.OPT_COLS[letter]
    p.rr([540 - 460 * q, y, 540 + 460 * q, y + h], 40, fill=col)
    if q < 0.9: return
    cy = y + h / 2
    p.circle(150, cy, 56, fill=WHITE)
    p.text((150, cy + 2), letter, f2("anton", 80), INK)
    p.text((235, cy), title, f2("anton", 62), INK, anchor="lm")
    p.rr([780, y + 14, 970, y + h - 14], 30, fill=WHITE)
    if icon == "bat": icon_bat(p, 875, cy, 0.72)
    elif icon == "keys": icon_keys(p, 870, cy + 4, 0.68)
    else: P.crumbs(p, 895, y + h - 22, 0.5, "happy", t)

@V.sounds
def sounds(L):
    out = [(0.2, "ding"), (L(0)[1] - 1.0, "thud"), (L(2)[1] - 0.8, "boing"), (L(3)[0] + 1.4, "thud"), (L(3)[0] + 2.2, "thud")]
    out += [(L(i)[0] + 0.05, "pop") for i in (5, 6, 7)]
    out += [(L(4)[0] + 0.4 + k, "pop") for k in range(0, 10, 2)]
    return out

@V.scene(0)
def phone(p, t, L):
    a, e = L(0)
    p.rect([0, 300, 1080, 1170], fill=(10, 12, 24))
    glow = 0.5 + 0.5 * math.sin(t * 6) if t < 1.2 else 1.0
    for i in range(6):
        p.circle(540, 760, 420 - i * 55, fill=(int(14 + 10 * i * glow), int(16 + 12 * i * glow), int(30 + 18 * i * glow)))
    buzz = math.sin(t * 60) * 6 * (1 - prog(t, 0.0, 1.0))
    x = 540 + buzz
    p.rr([x - 230, 400, x + 230, 1120], 60, fill=(30, 32, 40))
    p.rr([x - 212, 418, x + 212, 1102], 46, fill=(20, 28, 48))
    p.text((x, 520), "03:00", f2("anton", 120), (220, 228, 255))
    k = eback(prog(t, 0.5, 0.9))
    if k > 0:
        p.rr([x - 190 * k, 640, x + 190 * k, 820], 30, fill=(236, 240, 248))
        if k > 0.9:
            p.text((x - 160, 680), "UNKNOWN NUMBER", f2("dm", 26), MUTED, anchor="lm")
            p.text((x - 160, 750), "DON'T GO OUTSIDE.", f2("anton", 46), RED, anchor="lm")

@V.scene(1, 2)
def outside(p, t, L):
    a1, _ = L(1); a2, e2 = L(2)
    street(p, t)
    for i, (zx, s, seed, shirt) in enumerate([(120, 0.62, 0.0, (90, 110, 140)), (330, 0.7, 1.3, (130, 90, 90)), (870, 0.66, 2.1, (90, 120, 100))]):
        zombie(p, zx + ((t * 18 + i * 40) % 60), 1050, s, t, seed, shirt)
    k = eback(prog(t, a2 - 0.2, a2 + 0.3))
    if k > 0:
        zombie(p, 560, 1150, 1.05 * k, t, 3.3, (200, 160, 80), gnome=True)
        pill(p, 560, 470, "CLIVE · NUMBER 9", prog(t, a2 + 0.2, a2 + 0.5), bg=WHITE, size=34)
    window_frame(p)

@V.scene(3)
def back_door(p, t, L):
    a, e = L(3)
    p.rect([0, 300, 1080, 1170], fill=(34, 30, 40))
    p.rect([0, 960, 1080, 1170], fill=(60, 52, 58))
    shake = math.sin(t * 40) * 6 * (prog(t, a + 1.3, a + 1.5) * (1 - prog(t, a + 2.0, a + 2.4)) + prog(t, a + 2.2, a + 2.3) * (1 - prog(t, a + 2.6, a + 3.0)))
    x = 540 + shake
    p.rr([x - 210, 400, x + 210, 1000], 10, fill=OUT)
    p.rr([x - 196, 414, x + 196, 1000], 6, fill=(120, 80, 60))
    for yy in (470, 700):
        p.rr([x - 160, yy, x + 160, yy + 180], 8, fill=(104, 70, 52))
    p.circle(x + 150, 720, 16, fill=BRASS)
    g = prog(t, a + 1.2, a + 3.2)
    for i in range(int(4 * g)):
        sx = x - 120 + i * 60
        p.line([(sx, 560), (sx + 40, 640), (sx + 20, 700)], (230, 220, 210), 5)
    p.rect([x - 196, 990, x + 196, 1000], fill=(255, 230, 160))
    for i in range(3):
        fx = x - 120 + i * 110 + 20 * math.sin(t * 3 + i)
        p.ell([fx - 30, 994, fx + 30, 1004], fill=(20, 18, 24))
    q = eback(prog(t, a + 1.4, a + 1.8))
    if q > 0:
        p.text((540, 1085), "SCRATCH", f2("anton", int(100 * q) + 1), RED)

@V.scene(4, 10)
def choose(p, t, L):
    a4, e4 = L(4); a5, _ = L(5); a6, _ = L(6); a7, _ = L(7); a8, e8 = L(8)
    p.rect([0, 300, 1080, 1170], fill=(20, 24, 44))
    for i in range(5):
        p.circle(540, 760, 560 - i * 70, fill=(22 + i * 3, 26 + i * 3, 50 + i * 5))
    remain = 10 - 10 * clamp((t - a4 - 0.3) / max(1.0, a8 - a4 - 0.3))
    cx, cy, r = 540, 400, 64
    p.circle(cx, cy, r + 8, fill=(40, 46, 80))
    if remain > 0:
        p.d.pieslice([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], -90, -90 + 360 * remain / 10,
                     fill=RED if remain < 4 else YEL)
    p.circle(cx, cy, r - 16, fill=(20, 24, 44))
    p.text((cx, cy + 3), str(int(math.ceil(remain))) if remain > 0 else "0", f2("anton", 64), WHITE)
    option_card(p, t, a5 - 0.1, 500, "A", "CRICKET BAT", "bat")
    option_card(p, t, a6 - 0.1, 690, "B", "CAR KEYS", "keys")
    option_card(p, t, a7 - 0.1, 880, "C", "THE DOG", "dog")
    if t > a8:
        pill(p, 540, 1105, "COMMENT A, B OR C", prog(t, a8 + 0.1, a8 + 0.4), bg=WHITE, size=44)
    elif t < a5 - 0.1:
        pill(p, 540, 760, "GRAB ONE THING", prog(t, a4 + 0.3, a4 + 0.6), bg=WHITE, size=56)

if __name__ == "__main__":
    V.main()
