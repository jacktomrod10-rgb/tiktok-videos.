"""The Pennys: an original cartoon family for the interactive vote series.

Use with studio.kit: every function draws with a kit Pen in 1080x1920 output coordinates.
Characters: dave (dad), sue (mum), ellie (15), alfie (8), crumbs (the dog).
Moods: "happy", "grin", "neutral", "sad", "shock", "worried", "tired".
"""
import math
from studio.kit import *

SKIN = (241, 196, 160)
SKIN_D = (222, 170, 135)
WALL, WALL_S = (88, 132, 140), (80, 122, 130)
FLOOR, FLOOR_L = (124, 86, 60), (140, 100, 70)
SOFA, SOFA_D = (214, 160, 70), (186, 134, 52)
OPT_COLS = {"A": (61, 200, 190), "B": (255, 120, 160), "C": (255, 200, 70)}
NARRATOR = "bm_fable"   # the owner picked this British male voice for The Pennys

# ---------------- helpers ----------------
OUT = (46, 32, 40)          # outline colour

def shade(c, k=0.82):
    return tuple(int(v * k) for v in c)

def tint(c, k=0.25):
    return tuple(int(v + (255 - v) * k) for v in c)

def orr(p, box, r, fill, ow=5, shade_side=None):
    """Outlined rounded rect with optional shading on one side ('r' or 'l')."""
    p.rr([box[0] - ow, box[1] - ow, box[2] + ow, box[3] + ow], r + ow, fill=OUT)
    p.rr(box, r, fill=shade(fill) if shade_side else fill)
    if shade_side == "r":
        p.rr([box[0], box[1], box[2] - (box[2] - box[0]) * 0.22, box[3]], r, fill=fill)
    elif shade_side == "l":
        p.rr([box[0] + (box[2] - box[0]) * 0.22, box[1], box[2], box[3]], r, fill=fill)

def ocircle(p, x, y, r, fill, ow=5, shaded=True):
    p.circle(x, y, r + ow, fill=OUT)
    if shaded:
        p.circle(x, y, r, fill=shade(fill, 0.86))
        p.circle(x - r * 0.12, y - r * 0.06, r * 0.9, fill=fill)
    else:
        p.circle(x, y, r, fill=fill)

def oline(p, a, b, colour, w, ow=5):
    p.line([a, b], OUT, w + ow * 2)
    p.line([a, b], colour, w)

def ground_shadow(p, x, yf, w):
    p.ell([x - w, yf - w * 0.12, x + w, yf + w * 0.12], fill=(70, 48, 36))

# ---------------- room ----------------
def living_room(p, t, jar_level=0.05):
    # wall with a warm light falloff and a soft diamond wallpaper
    p.rect([0, 300, 1080, 1010], fill=WALL)
    for i in range(6):
        p.circle(780, 560, 520 - i * 70, fill=tint(WALL, 0.04 + i * 0.025))
    p.rect([0, 0, 1080, 299], fill=(0, 0, 0, 0))   # keep the light inside the room
    for yy in range(330, 900, 80):
        for xx in range(20 + (40 if (yy // 80) % 2 else 0), 1080, 80):
            p.poly([(xx, yy - 10), (xx + 10, yy), (xx, yy + 10), (xx - 10, yy)], WALL_S)
    # skirting board + dado rail
    p.rect([0, 880, 1080, 1010], fill=shade(WALL, 0.88))
    p.rect([0, 872, 1080, 886], fill=(236, 230, 216))
    p.rect([0, 992, 1080, 1012], fill=(236, 230, 216))
    # window with curtains
    p.rr([84, 352, 406, 648], 16, fill=OUT)
    p.rr([90, 358, 400, 642], 12, fill=(236, 230, 216))
    p.rect([110, 378, 380, 622], fill=(150, 205, 245))
    p.rect([110, 540, 380, 622], fill=(175, 220, 250))
    p.ell([150 + (t * 12) % 200, 420, 250 + (t * 12) % 200, 460], fill=WHITE)
    p.rect([240, 378, 250, 622], fill=(236, 230, 216)); p.rect([110, 495, 380, 505], fill=(236, 230, 216))
    for x0 in (50, 380):
        p.rr([x0, 340, x0 + 70, 700], 26, fill=(196, 84, 84))
        p.rr([x0 + 12, 340, x0 + 30, 700], 10, fill=(176, 70, 70))
    p.rr([40, 330, 460, 346], 8, fill=(120, 86, 60))
    # framed beach picture (the dream)
    p.rr([520, 380, 660, 480], 8, fill=OUT)
    p.rect([528, 388, 652, 472], fill=(150, 210, 245))
    p.rect([528, 440, 652, 472], fill=(240, 214, 150))
    p.circle(630, 408, 12, fill=YEL)
    # shelf with savings jar
    p.rr([656, 516, 994, 540], 6, fill=OUT)
    p.rect([660, 520, 990, 536], fill=(150, 110, 80))
    jar(p, 760, 520, 0.8, jar_level)
    p.rr([856, 448, 954, 520], 8, fill=OUT)
    p.rr([860, 452, 900, 520], 6, fill=(200, 90, 80))
    p.rr([904, 440, 934, 520], 6, fill=(90, 140, 200))
    p.rr([936, 460, 950, 520], 4, fill=(240, 200, 80))
    # floor lamp with glow
    for i in range(5):
        p.circle(1010, 470, 150 - i * 25, fill=tint(WALL, 0.10 + i * 0.07))
    p.rect([1004, 480, 1016, 1000], fill=OUT)
    p.poly([(950, 480), (1070, 480), (1045, 400), (975, 400)], (250, 226, 170))
    # floor + rug
    p.rect([0, 1010, 1080, 1170], fill=FLOOR)
    for y in (1050, 1095, 1140):
        p.line([(0, y), (1080, y)], FLOOR_L, 4)
    p.ell([150, 1040, 930, 1160], fill=(150, 70, 80))
    p.ell([190, 1055, 890, 1145], fill=(170, 86, 96))
    # sofa with outline and cushions
    p.rr([132, 752, 948, 1004], 56, fill=OUT)
    p.rr([200, 760, 880, 880], 50, fill=SOFA_D)
    p.rr([170, 800, 910, 990], 50, fill=SOFA)
    p.rr([170, 930, 910, 990], 40, fill=shade(SOFA, 0.9))
    p.rr([140, 830, 230, 1000], 40, fill=SOFA_D); p.rr([850, 830, 940, 1000], 40, fill=SOFA_D)
    p.rr([250, 780, 400, 870], 34, fill=(110, 160, 190)); p.rr([680, 780, 830, 870], 34, fill=(200, 110, 140))
    # floor shadow under the sofa
    p.ell([150, 990, 930, 1030], fill=shade(FLOOR, 0.7))

def jar(p, cx, yb, sc=1.0, level=0.1, label=True):
    w, h = 110 * sc, 140 * sc
    p.rr([cx - w / 2 - 5 * sc, yb - h - 5 * sc, cx + w / 2 + 5 * sc, yb + 5 * sc], 26 * sc, fill=OUT)
    p.rr([cx - w / 2, yb - h, cx + w / 2, yb], 22 * sc, fill=(200, 230, 240))
    lv = max(0.0, min(1.0, level))
    if lv > 0:
        p.rr([cx - w / 2 + 6 * sc, yb - 6 * sc - (h - 20 * sc) * lv, cx + w / 2 - 6 * sc, yb - 6 * sc], 16 * sc, fill=BRASS)
    p.rr([cx - w / 2 + 10 * sc, yb - h + 12 * sc, cx - w / 2 + 24 * sc, yb - 20 * sc], 7 * sc, fill=(235, 248, 252))
    p.rr([cx - w / 2 - 10 * sc, yb - h - 24 * sc, cx + w / 2 + 10 * sc, yb - h + 8 * sc], 10 * sc, fill=OUT)
    p.rr([cx - w / 2 - 6 * sc, yb - h - 20 * sc, cx + w / 2 + 6 * sc, yb - h + 4 * sc], 8 * sc, fill=(170, 120, 80))
    if label:
        p.rr([cx - 38 * sc, yb - h * 0.62, cx + 38 * sc, yb - h * 0.35], 6 * sc, fill=WHITE)
        p.text((cx, yb - h * 0.485), "HOLS", f2("dm", max(8, int(20 * sc))), INK)

# ---------------- faces ----------------
def _face(p, x, y, r, mood, t, blink_seed=0.0, glasses=False, iris=(90, 70, 50)):
    blink = ((t + blink_seed) % 3.7) < 0.13
    ex, ey = r * 0.34, y - r * 0.06
    ew, eh = r * 0.17, r * 0.21
    look = math.sin(t * 0.7 + blink_seed) * r * 0.03
    for sx in (-1, 1):
        cx = x + sx * ex
        if blink:
            p.arc([cx - ew, ey - eh * .6, cx + ew, ey + eh * .6], 20, 160, OUT, max(2, r * .05))
        else:
            p.ell([cx - ew - 3, ey - eh - 3, cx + ew + 3, ey + eh + 3], fill=OUT)
            p.ell([cx - ew, ey - eh, cx + ew, ey + eh], fill=WHITE)
            ir = ew * 0.68
            p.circle(cx + look, ey + eh * .12, ir, fill=iris)
            p.circle(cx + look, ey + eh * .12, ir * .55, fill=INK)
            p.circle(cx + look + ir * .35, ey - eh * .15, ir * .3, fill=WHITE)
            if mood == "tired":
                p.rect([cx - ew - 3, ey - eh - 3, cx + ew + 3, ey - eh * .1], fill=SKIN_D)
    by = ey - eh - r * 0.12
    bw = max(3, r * .07)
    for sx in (-1, 1):
        cx = x + sx * ex
        if mood in ("sad", "worried"):
            p.line([(cx - sx * ew * 1.1, by - r * .07), (cx + sx * ew * 1.1, by + r * .03)], OUT, bw)
        elif mood == "shock":
            p.arc([cx - ew * 1.2, by - r * .12, cx + ew * 1.2, by + r * .06], 200, 340, OUT, bw)
        elif mood in ("angry",):
            p.line([(cx - sx * ew * 1.1, by + r * .04), (cx + sx * ew * 1.1, by - r * .06)], OUT, bw)
        else:
            p.arc([cx - ew * 1.2, by - r * .06, cx + ew * 1.2, by + r * .1], 200, 340, OUT, bw)
    if glasses:
        for sx in (-1, 1):
            p.circle(x + sx * ex, ey, r * .25, outline=(70, 50, 60), width=max(3, r * .05))
        p.line([(x - ex + r * .25, ey), (x + ex - r * .25, ey)], (70, 50, 60), max(3, r * .05))
    # nose
    p.ell([x - r * .1, y + r * .06, x + r * .1, y + r * .22], fill=SKIN_D)
    p.circle(x - r * .03, y + r * .1, r * .03, fill=tint(SKIN, .5))
    # cheeks
    if mood in ("happy", "grin", "shock"):
        p.ell([x - r * .7, y + r * .18, x - r * .42, y + r * .34], fill=(244, 160, 160))
        p.ell([x + r * .42, y + r * .18, x + r * .7, y + r * .34], fill=(244, 160, 160))
    # mouth
    my, mw = y + r * .44, r * .3
    lw = max(3, r * .055)
    if mood == "happy":
        p.arc([x - mw, my - mw * .8, x + mw, my + mw * .45], 20, 160, OUT, lw)
    elif mood == "grin":
        p.d.chord([(x - mw) * S, (my - mw * .55) * S, (x + mw) * S, (my + mw * .8) * S], 0, 180, fill=(110, 40, 50), outline=OUT, width=int(lw * S * .8))
        p.rect([x - mw * .72, my, x + mw * .72, my + mw * .2], fill=WHITE)
        p.ell([x - mw * .35, my + mw * .3, x + mw * .35, my + mw * .62], fill=(230, 110, 120))
    elif mood in ("sad", "worried"):
        p.arc([x - mw * .75, my, x + mw * .75, my + mw * .9], 200, 340, OUT, lw)
    elif mood == "shock":
        p.ell([x - mw * .38, my - mw * .25, x + mw * .38, my + mw * .6], fill=(110, 40, 50), outline=OUT, width=lw)
    elif mood == "tired":
        p.line([(x - mw * .5, my + mw * .2), (x + mw * .5, my + mw * .05)], OUT, lw)
    else:
        p.arc([x - mw * .6, my - mw * .2, x + mw * .6, my + mw * .3], 30, 150, OUT, lw)

def _head(p, x, y, r, mood, t, seed, glasses=False, ears=True, iris=(90, 70, 50)):
    if ears:
        for sx in (-1, 1):
            ocircle(p, x + sx * r * .96, y + r * .08, r * .2, SKIN, ow=4, shaded=False)
    ocircle(p, x, y, r, SKIN, ow=5)
    _face(p, x, y, r, mood, t, seed, glasses, iris)

def _body(p, x, yf, s, shirt, trousers, torso_w, torso_h, leg_h, legs_skin=False, wave=0.0, t=0.0, hold=None,
          shoe=(60, 52, 52), collar=None):
    breathe = 1 + 0.012 * math.sin(t * 2.4)
    ground_shadow(p, x, yf, torso_w * .62)
    lw = torso_w * 0.21
    for sx in (-1, 1):
        lx = x + sx * lw * 1.05
        orr(p, [lx - lw / 2, yf - leg_h, lx + lw / 2, yf - lw * .2], lw / 2, SKIN if legs_skin else trousers, ow=4, shade_side="r")
        p.ell([lx - lw * .85 - 4, yf - lw * .55 - 4, lx + lw * .95 + 4, yf + lw * .22 + 4], fill=OUT)
        p.ell([lx - lw * .85, yf - lw * .55, lx + lw * .95, yf + lw * .22], fill=shoe)
        p.ell([lx - lw * .5, yf - lw * .45, lx + lw * .1, yf - lw * .25], fill=tint(shoe, .35))
    if legs_skin:
        orr(p, [x - torso_w * .46, yf - leg_h - 10 * s, x + torso_w * .46, yf - leg_h * .5], 14 * s, trousers, ow=4)
    th = torso_h * breathe
    top = yf - leg_h - th
    aw = torso_w * .18
    # neck
    orr(p, [x - torso_w * .14, top - torso_w * .14, x + torso_w * .14, top + 20 * s], 10 * s, SKIN, ow=4)
    # left arm behind torso edge
    l0 = (x - torso_w / 2 + aw * .7, top + aw * .9)
    l1 = (x - torso_w / 2 - aw * .55, top + th * .8)
    oline(p, l0, l1, shade(shirt, .9), aw, ow=4)
    orr(p, [x - torso_w / 2, top, x + torso_w / 2, yf - leg_h + 14 * s], torso_w * .3, shirt, ow=5, shade_side="r")
    if collar:
        p.poly([(x - torso_w * .18, top + 2), (x, top + torso_w * .2), (x + torso_w * .18, top + 2)], collar)
    ocircle(p, l1[0], l1[1], aw * .6, SKIN, ow=4, shaded=False)
    r0 = (x + torso_w / 2 - aw * .7, top + aw * .9)
    if wave > 0:
        ang = -1.05 + 0.3 * math.sin(t * 9)
        r1 = (r0[0] + math.cos(ang) * th * .75, r0[1] + math.sin(ang) * th * .75)
    else:
        r1 = (x + torso_w / 2 + aw * .55, top + th * .8)
    oline(p, r0, r1, shirt, aw, ow=4)
    ocircle(p, r1[0], r1[1], aw * .6, SKIN, ow=4, shaded=False)
    if hold == "phone":
        p.rr([l1[0] - 22 * s, l1[1] - 58 * s, l1[0] + 22 * s, l1[1] + 14 * s], 8 * s, fill=OUT)
        p.rr([l1[0] - 16 * s, l1[1] - 52 * s, l1[0] + 16 * s, l1[1] + 8 * s], 5 * s, fill=(120, 190, 255))
        p.rect([l1[0] - 16 * s, l1[1] - 52 * s, l1[0] + 16 * s, l1[1] - 36 * s], fill=(160, 210, 255))
        ocircle(p, l1[0], l1[1], aw * .6, SKIN, ow=4, shaded=False)
    if hold == "wrench":
        oline(p, (r1[0], r1[1]), (r1[0] + 52 * s, r1[1] - 52 * s), (175, 182, 192), 12 * s, ow=4)
        p.circle(r1[0] + 58 * s, r1[1] - 58 * s, 22 * s, fill=OUT)
        p.circle(r1[0] + 58 * s, r1[1] - 58 * s, 17 * s, fill=(175, 182, 192))
        p.circle(r1[0] + 66 * s, r1[1] - 66 * s, 9 * s, fill=WALL)
        ocircle(p, r1[0], r1[1], aw * .6, SKIN, ow=4, shaded=False)
    return top

def dave(p, x, yf, s=1.0, mood="happy", t=0.0, wave=0.0, hold=None):
    bob = math.sin(t * 2.0) * 4 * s
    blue = (64, 96, 160)
    top = _body(p, x, yf, s, (225, 225, 215), blue, 250 * s, 240 * s, 150 * s, wave=wave, t=t, hold=hold, collar=(200, 200, 190))
    # overalls bib over the shirt
    p.rr([x - 95 * s - 5, top + 60 * s - 5, x + 95 * s + 5, yf - 150 * s + 19 * s], 30 * s, fill=OUT)
    p.rr([x - 95 * s, top + 60 * s, x + 95 * s, yf - 150 * s + 14 * s], 26 * s, fill=blue)
    p.rr([x - 95 * s, top + 60 * s, x + 30 * s, yf - 150 * s + 14 * s], 26 * s, fill=tint(blue, .08))
    for sx in (-1, 1):
        p.rr([x + sx * 70 * s - 13 * s, top - 2, x + sx * 70 * s + 13 * s, top + 70 * s], 8 * s, fill=blue)
        p.circle(x + sx * 70 * s, top + 70 * s, 9 * s, fill=YEL)
    p.rr([x - 48 * s, top + 110 * s, x + 48 * s, top + 170 * s], 10 * s, fill=shade(blue, .85))
    p.rect([x - 6 * s, top + 100 * s, x + 6 * s, top + 128 * s], fill=(175, 182, 192))   # pen in pocket
    hr = 92 * s
    hy = top - hr * .82 + bob
    for sx in (-1, 1):   # side tufts behind
        p.ell([x + sx * hr * .9 - hr * .2, hy - hr * .38, x + sx * hr * .9 + hr * .2, hy + hr * .32], fill=OUT)
        p.ell([x + sx * hr * .9 - hr * .16, hy - hr * .34, x + sx * hr * .9 + hr * .16, hy + hr * .28], fill=(110, 75, 50))
    _head(p, x, hy, hr, mood, t, 0.3, ears=False, iris=(80, 110, 150))
    p.arc([x - hr * .55, hy - hr * .85, x - hr * .05, hy - hr * .45], 200, 300, tint(SKIN, .5), max(3, hr * .06))   # bald shine
    p.rr([x - hr * .4 - 3, hy + hr * .22 - 3, x + hr * .4 + 3, hy + hr * .38 + 3], hr * .1, fill=OUT)
    p.rr([x - hr * .4, hy + hr * .22, x + hr * .4, hy + hr * .38], hr * .08, fill=(110, 75, 50))   # moustache
    if mood == "tired":
        for i in range(3):
            p.text((x + hr * 1.1 + i * 26 * s, hy - hr * .9 - i * 30 * s), "z", f2("anton", int(40 * s)), WHITE)

def sue(p, x, yf, s=1.0, mood="happy", t=0.0, wave=0.0, hold=None):
    bob = math.sin(t * 2.0 + 1) * 4 * s
    pink = (232, 116, 150)
    top = _body(p, x, yf, s, pink, (70, 70, 96), 200 * s, 220 * s, 150 * s, wave=wave, t=t, hold=hold)
    p.rr([x - 34 * s, top + 4, x + 34 * s, top + 200 * s], 16 * s, fill=(245, 236, 222))   # top under the cardigan
    for i in range(3):
        p.circle(x - 46 * s, top + 60 * s + i * 50 * s, 8 * s, fill=YEL)
    hr = 82 * s
    hy = top - hr * .82 + bob
    hair, hair_d = (196, 84, 52), (160, 64, 40)
    for k in range(12):
        a = math.radians(180 + k * 16 - 8)
        p.circle(x + math.cos(a) * hr * 1.02, hy + math.sin(a) * hr * .95 + hr * .2, hr * .4, fill=OUT)
    for sx in (-1, 1):
        p.circle(x + sx * hr * .95, hy + hr * .5, hr * .36, fill=OUT)
    for k in range(12):
        a = math.radians(180 + k * 16 - 8)
        p.circle(x + math.cos(a) * hr * 1.02, hy + math.sin(a) * hr * .95 + hr * .2, hr * .35, fill=hair_d if k % 2 else hair)
    for sx in (-1, 1):
        p.circle(x + sx * hr * .95, hy + hr * .5, hr * .31, fill=hair)
    _head(p, x, hy, hr, mood, t, 1.3, glasses=True, ears=False, iris=(70, 130, 90))
    for k in range(5):
        p.circle(x - hr * .55 + k * hr * .28, hy - hr * .8, hr * .27, fill=hair if k % 2 else hair_d)
    p.circle(x + hr * .35, hy - hr * .9, hr * .1, fill=tint(hair, .4))

def ellie(p, x, yf, s=1.0, mood="neutral", t=0.0, wave=0.0, hold="phone"):
    bob = math.sin(t * 2.0 + 2) * 3 * s
    hr = 72 * s
    torso_w, torso_h, leg_h = 170 * s, 200 * s, 160 * s
    top = yf - leg_h - torso_h
    hy = top - hr * .82 + bob
    hair = (48, 36, 44)
    p.rr([x - hr * 1.08 - 5, hy - hr * .6 - 5, x + hr * 1.08 + 5, top + 125 * s + 5], hr * .62, fill=OUT)
    p.rr([x - hr * 1.08, hy - hr * .6, x + hr * 1.08, top + 125 * s], hr * .6, fill=hair)
    purple = (128, 92, 200)
    _body(p, x, yf, s, purple, (50, 62, 92), torso_w, torso_h, leg_h, wave=wave, t=t, hold=hold, shoe=(235, 235, 240))
    p.rr([x - 50 * s, top + 120 * s, x + 50 * s, top + 175 * s], 18 * s, fill=shade(purple, .85))   # hoodie pocket
    for sx in (-1, 1):
        p.line([(x + sx * 16 * s, top + 4), (x + sx * 20 * s, top + 70 * s)], WHITE, 5 * s)
    _head(p, x, hy, hr, mood, t, 2.1, iris=(110, 80, 60))
    p.d.chord([(x - hr * 1.04) * S, (hy - hr * 1.08) * S, (x + hr * 1.04) * S, (hy + hr * .3) * S], 180, 360, fill=hair)
    p.arc([x - hr * .7, hy - hr * .95, x + hr * .1, hy - hr * .3], 200, 260, tint(hair, .3), max(3, hr * .06))

def alfie(p, x, yf, s=1.0, mood="grin", t=0.0, wave=0.0, hold=None):
    bob = abs(math.sin(t * 3.0)) * 8 * s
    hr = 70 * s
    green = (88, 178, 100)
    top = _body(p, x, yf - bob, s, green, (60, 90, 150), 150 * s, 150 * s, 110 * s, legs_skin=True, wave=wave, t=t, hold=hold, shoe=(220, 70, 60))
    hy = top - hr * .82
    blond = (242, 200, 80)
    for k in range(7):
        bx = x - hr * .85 + k * hr * .28
        p.poly([(bx - hr * .24, hy - hr * .5), (bx + hr * .05, hy - hr * 1.32), (bx + hr * .34, hy - hr * .5)], OUT)
    for k in range(7):
        bx = x - hr * .85 + k * hr * .28
        p.poly([(bx - hr * .2, hy - hr * .55), (bx + hr * .05, hy - hr * 1.25), (bx + hr * .3, hy - hr * .55)], blond if k % 2 else shade(blond, .9))
    _head(p, x, hy, hr, mood, t, 0.7, iris=(80, 120, 170))
    p.d.chord([(x - hr) * S, (hy - hr * 1.0) * S, (x + hr) * S, (hy + hr * .06) * S], 180, 360, fill=blond)
    # volcano on the t-shirt
    p.poly([(x - 34 * s, top + 104 * s), (x - 9 * s, top + 56 * s), (x + 9 * s, top + 56 * s), (x + 34 * s, top + 104 * s)], (120, 80, 60))
    p.circle(x, top + 52 * s, 9 * s, fill=ORANGE)
    p.circle(x - 8 * s, top + 42 * s, 6 * s, fill=YEL)

def crumbs(p, x, yf, s=1.0, mood="happy", t=0.0):
    wag = math.sin(t * 12) * 0.5
    body_c, ear_c = (176, 120, 70), (120, 80, 45)
    ground_shadow(p, x, yf, 140 * s)
    tx, ty = x + 120 * s, yf - 120 * s
    oline(p, (tx, ty), (tx + 70 * s * math.cos(-0.9 + wag), ty + 70 * s * math.sin(-0.9 + wag)), body_c, 18 * s, ow=4)
    for dx in (-90, -40, 50, 100):
        orr(p, [x + dx * s - 15 * s, yf - 70 * s, x + dx * s + 15 * s, yf], 10 * s, body_c if dx in (-90, 50) else shade(body_c, .9), ow=4)
    p.ell([x - 124 * s, yf - 164 * s, x + 134 * s, yf - 36 * s], fill=OUT)
    p.ell([x - 120 * s, yf - 160 * s, x + 130 * s, yf - 40 * s], fill=body_c)
    p.ell([x - 20 * s, yf - 150 * s, x + 60 * s, yf - 110 * s], fill=ear_c)    # patch
    p.rr([x - 125 * s, yf - 170 * s, x - 60 * s, yf - 140 * s], 10 * s, fill=(210, 60, 60))   # collar
    p.circle(x - 92 * s, yf - 132 * s, 10 * s, fill=YEL)
    hx, hy = x - 110 * s, yf - 190 * s
    flap = math.sin(t * 5) * 6 * s
    for sx in (-1, 1):
        p.ell([hx + sx * 75 * s - 34 * s, hy - 44 * s + flap, hx + sx * 75 * s + 34 * s, hy + 84 * s + flap], fill=OUT)
        p.ell([hx + sx * 75 * s - 30 * s, hy - 40 * s + flap, hx + sx * 75 * s + 30 * s, hy + 80 * s + flap], fill=ear_c)
    ocircle(p, hx, hy, 72 * s, body_c, ow=4)
    p.ell([hx - 42 * s, hy + 8 * s, hx + 42 * s, hy + 64 * s], fill=(226, 194, 154))
    p.ell([hx - 15 * s, hy + 8 * s, hx + 15 * s, hy + 30 * s], fill=INK)
    p.circle(hx - 5 * s, hy + 13 * s, 4 * s, fill=WHITE)
    for sx in (-1, 1):
        p.circle(hx + sx * 28 * s, hy - 18 * s, 11 * s, fill=INK)
        p.circle(hx + sx * 28 * s + 4 * s, hy - 22 * s, 4 * s, fill=WHITE)
    if mood in ("happy", "grin"):
        p.rr([hx - 11 * s, hy + 40 * s, hx + 11 * s, hy + 76 * s], 9 * s, fill=(240, 120, 140))
    else:
        p.arc([hx - 16 * s, hy + 36 * s, hx + 16 * s, hy + 52 * s], 20, 160, OUT, 4 * s)

CHARS = {"dave": dave, "sue": sue, "ellie": ellie, "alfie": alfie, "crumbs": crumbs}

def family(p, t, moods=None, yf=1080, sc=0.82, xs=(170, 390, 610, 800, 975)):
    m = {"dave": "happy", "sue": "happy", "ellie": "neutral", "alfie": "grin", "crumbs": "happy"}
    m.update(moods or {})
    sue(p, xs[1], yf, sc, m["sue"], t)
    dave(p, xs[0], yf, sc, m["dave"], t)
    ellie(p, xs[2], yf, sc * .95, m["ellie"], t)
    alfie(p, xs[3], yf, sc * .95, m["alfie"], t)
    crumbs(p, xs[4], yf, sc * .55, m["crumbs"], t)

# ---------------- overlays ----------------
def hud(p, day, fund, goal=1000, days=30, pop=1.0):
    if pop <= 0: return
    p.rr([60, 222, 300, 282], 30, fill=YEL)
    p.text((180, 253), f"DAY {day}/{days}", f2("dm", 32), INK)
    p.rr([330, 222, 1020, 282], 30, fill=(20, 30, 50))
    k = max(0.0, min(1.0, fund / goal))
    p.rr([336, 228, 336 + max(48, 678 * k), 276], 24, fill=GREEN)
    p.text((675, 253), f"HOLIDAY FUND  £{fund:,.2f} / £{goal:,}", f2("dm", 30), WHITE)

def stats_panel(p, t, t0, stats, cx=540, cy=700):
    """stats: list of (label, value 0..100, colour[, text shown on the right])."""
    k = eback(prog(t, t0, t0 + 0.5))
    if k <= 0: return
    w, h = 820 * k, 440 * k
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 40, fill=(20, 30, 50), outline=YEL, width=6)
    if k < 0.9: return
    p.text((cx, cy - 160), "THE PENNYS' STATS", f2("anton", 64), YEL)
    for i, st in enumerate(stats):
        lab, val, col = st[0], st[1], st[2]
        txt = st[3] if len(st) > 3 else f"{int(val)}/100"
        y = cy - 60 + i * 100
        g = eo(prog(t, t0 + 0.6 + i * 0.5, t0 + 1.4 + i * 0.5))
        p.text((cx - 370, y), lab, f2("dm", 38), WHITE, anchor="lm")
        p.rr([cx - 110, y - 22, cx + 200, y + 22], 22, fill=(50, 62, 86))
        p.rr([cx - 110, y - 22, cx - 110 + max(44, 310 * val / 100 * g), y + 22], 22, fill=col)
        if g > 0.5:
            p.text((cx + 370, y), txt, f2("anton", 44), col, anchor="rm")

def vote_card(p, t, t0, question, options, cx=540, top=330, gap=1.6):
    """options: [(letter, title, effects)], appear one by one from t0."""
    k = eback(prog(t, t0, t0 + 0.4))
    if k <= 0: return
    p.rr([cx - 470 * k, top, cx + 470 * k, top + 150], 36, fill=(20, 30, 50))
    if k > 0.9:
        p.text((cx, top + 75), question, f2("anton", 60), WHITE)
    for i, (letter, title, eff) in enumerate(options):
        t1 = t0 + 0.6 + i * gap
        q = eback(prog(t, t1, t1 + 0.4))
        if q <= 0: continue
        y = top + 190 + i * 210
        col = OPT_COLS[letter]
        p.rr([cx - 470 * q, y, cx + 470 * q, y + 180], 40, fill=col)
        if q > 0.9:
            p.circle(cx - 380, y + 90, 58, fill=WHITE)
            p.text((cx - 380, y + 92), letter, f2("anton", 80), INK)
            p.text((cx - 290, y + 62), title, f2("dm", 46), INK, anchor="lm")
            p.text((cx - 290, y + 128), eff, f2("dm", 32), (40, 40, 50), anchor="lm")

def result_bars(p, t, t0, votes, cx=540, top=420):
    """votes: {"A": n, "B": n, "C": n}; animated percentage bars."""
    total = max(1, sum(votes.values()))
    for i, L_ in enumerate("ABC"):
        g = eo(prog(t, t0 + i * 0.2, t0 + 1.2 + i * 0.2))
        pct = votes.get(L_, 0) / total
        y = top + i * 150
        p.rr([cx - 440, y, cx + 440, y + 110], 30, fill=(20, 30, 50))
        p.rr([cx - 440, y, cx - 440 + max(60, 880 * pct * g), y + 110], 30, fill=OPT_COLS[L_])
        p.text((cx - 400, y + 55), L_, f2("anton", 70), INK)
        p.text((cx + 400, y + 55), f"{round(pct * 100 * g)}%", f2("anton", 60), WHITE, anchor="rm")

def money_pop(p, t, t0, text, x=540, y=600, colour=GREEN):
    k = prog(t, t0, t0 + 1.2)
    if k <= 0 or k >= 1: return
    p.text((x, y - 120 * eo(k)), text, f2("anton", int(110 * (1 - 0.3 * k))), colour)

def phone_card(p, t, t0, lines, cx=540, cy=700):
    k = eback(prog(t, t0, t0 + 0.5))
    if k <= 0: return
    w, h = 460 * k, 780 * k
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 60 * k, fill=(30, 34, 44))
    p.rr([cx - w / 2 + 18, cy - h / 2 + 18, cx + w / 2 - 18, cy + h / 2 - 18], 46 * k, fill=(240, 244, 250))
    if k < 0.95: return
    p.rect([cx - 212, cy - 360, cx + 212, cy - 120], fill=(120, 190, 240))
    p.poly([(cx - 212, cy - 120), (cx - 90, cy - 250), (cx - 20, cy - 190), (cx + 60, cy - 290), (cx + 212, cy - 120)], (150, 100, 80))
    p.circle(cx + 120, cy - 300, 36, fill=YEL)
    for i, (txt, size, col) in enumerate(lines):
        p.text((cx, cy - 40 + i * 80), txt, f2("anton" if i == 0 else "dm", size), col)
