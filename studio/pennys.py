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

# ---------------- room ----------------
def living_room(p, t, jar_level=0.05):
    p.rect([0, 300, 1080, 1010], fill=WALL)
    for x in range(0, 1080, 90):
        p.rect([x, 300, x + 40, 1010], fill=WALL_S)
    # window
    p.rr([90, 360, 400, 640], 14, fill=(230, 226, 214))
    p.rect([110, 380, 380, 620], fill=(150, 200, 240))
    p.ell([150 + (t * 12) % 200, 420, 250 + (t * 12) % 200, 460], fill=WHITE)
    p.rect([240, 380, 250, 620], fill=(230, 226, 214)); p.rect([110, 495, 380, 505], fill=(230, 226, 214))
    # shelf with savings jar
    p.rect([660, 520, 990, 536], fill=(150, 110, 80))
    jar(p, 760, 520, 0.8, jar_level)
    p.rr([860, 452, 950, 520], 8, fill=(200, 90, 80))   # book
    p.rr([900, 440, 930, 520], 6, fill=(90, 140, 200))
    # floor
    p.rect([0, 1010, 1080, 1170], fill=FLOOR)
    for y in (1050, 1095, 1140):
        p.line([(0, y), (1080, y)], FLOOR_L, 4)
    # sofa
    p.rr([170, 800, 910, 990], 50, fill=SOFA)
    p.rr([200, 760, 880, 880], 50, fill=SOFA_D)
    p.rr([140, 830, 230, 1000], 40, fill=SOFA_D); p.rr([850, 830, 940, 1000], 40, fill=SOFA_D)

def jar(p, cx, yb, sc=1.0, level=0.1, label=True):
    w, h = 110 * sc, 140 * sc
    p.rr([cx - w / 2, yb - h, cx + w / 2, yb], 22 * sc, fill=(200, 230, 240), outline=WHITE, width=4 * sc)
    lv = max(0.0, min(1.0, level))
    if lv > 0:
        p.rr([cx - w / 2 + 6 * sc, yb - 6 * sc - (h - 20 * sc) * lv, cx + w / 2 - 6 * sc, yb - 6 * sc], 16 * sc, fill=BRASS)
    p.rr([cx - w / 2 - 6 * sc, yb - h - 20 * sc, cx + w / 2 + 6 * sc, yb - h + 4 * sc], 8 * sc, fill=(170, 120, 80))
    if label:
        p.rr([cx - 38 * sc, yb - h * 0.62, cx + 38 * sc, yb - h * 0.35], 6 * sc, fill=WHITE)
        p.text((cx, yb - h * 0.485), "HOLS", f2("dm", max(8, int(20 * sc))), INK)

# ---------------- faces ----------------
def _face(p, x, y, r, mood, t, blink_seed=0.0, glasses=False):
    blink = ((t + blink_seed) % 3.7) < 0.13
    ex, ey, er = r * 0.36, y - r * 0.08, r * 0.11
    for sx in (-1, 1):
        if blink:
            p.line([(x + sx * ex - er, ey), (x + sx * ex + er, ey)], INK, max(2, er * .5))
        else:
            p.ell([x + sx * ex - er, ey - er * 1.2, x + sx * ex + er, ey + er * 1.2], fill=INK)
            p.circle(x + sx * ex + er * .3, ey - er * .4, er * .35, fill=WHITE)
    # brows
    by = ey - r * 0.26
    for sx in (-1, 1):
        if mood in ("sad", "worried"):
            p.line([(x + sx * (ex - r * .16), by - r * .06), (x + sx * (ex + r * .16), by + r * .04)], INK, max(2, r * .05))
        elif mood == "shock":
            p.line([(x + sx * (ex - r * .16), by - r * .1), (x + sx * (ex + r * .16), by - r * .1)], INK, max(2, r * .05))
        elif mood == "tired":
            p.line([(x + sx * (ex - r * .16), by + r * .04), (x + sx * (ex + r * .16), by + r * .04)], INK, max(2, r * .05))
        else:
            p.line([(x + sx * (ex - r * .16), by), (x + sx * (ex + r * .16), by - r * .04)], INK, max(2, r * .05))
    if glasses:
        for sx in (-1, 1):
            p.circle(x + sx * ex, ey, r * .22, outline=(60, 60, 70), width=max(2, r * .04))
        p.line([(x - ex + r * .22, ey), (x + ex - r * .22, ey)], (60, 60, 70), max(2, r * .04))
    # nose
    p.circle(x, y + r * .12, r * .09, fill=SKIN_D)
    # mouth
    my = y + r * .42
    mw = r * .34
    if mood in ("happy", "neutral") and mood == "happy":
        p.arc([x - mw, my - mw * .7, x + mw, my + mw * .5], 15, 165, INK, max(2, r * .06))
        p.circle(x - r * .55, y + r * .25, r * .12, fill=(240, 150, 150)); p.circle(x + r * .55, y + r * .25, r * .12, fill=(240, 150, 150))
    elif mood == "grin":
        p.d.chord([(x - mw) * S, (my - mw * .55) * S, (x + mw) * S, (my + mw * .75) * S], 0, 180, fill=INK)
        p.rect([x - mw * .7, my + 1, x + mw * .7, my + mw * .18], fill=WHITE)
        p.circle(x - r * .55, y + r * .25, r * .12, fill=(240, 150, 150)); p.circle(x + r * .55, y + r * .25, r * .12, fill=(240, 150, 150))
    elif mood in ("sad", "worried"):
        p.arc([x - mw * .8, my, x + mw * .8, my + mw * .9], 200, 340, INK, max(2, r * .06))
    elif mood == "shock":
        p.ell([x - mw * .35, my - mw * .2, x + mw * .35, my + mw * .55], fill=INK)
    elif mood == "tired":
        p.line([(x - mw * .6, my + mw * .2), (x + mw * .6, my + mw * .1)], INK, max(2, r * .06))
    else:
        p.line([(x - mw * .55, my + mw * .15), (x + mw * .55, my + mw * .15)], INK, max(2, r * .06))

def _body(p, x, yf, s, shirt, trousers, torso_w, torso_h, leg_h, legs_skin=False, wave=0.0, t=0.0, hold=None):
    lw = torso_w * 0.2
    for sx in (-1, 1):
        p.rr([x + sx * lw * 1.1 - lw / 2, yf - leg_h, x + sx * lw * 1.1 + lw / 2, yf], lw / 2, fill=SKIN if legs_skin else trousers)
        p.ell([x + sx * lw * 1.1 - lw * .8, yf - lw * .45, x + sx * lw * 1.1 + lw * .8, yf + lw * .25], fill=(50, 45, 45))
    if legs_skin:
        p.rr([x - torso_w * .45, yf - leg_h - 10 * s, x + torso_w * .45, yf - leg_h * .55], 12 * s, fill=trousers)
    top = yf - leg_h - torso_h
    p.rr([x - torso_w / 2, top, x + torso_w / 2, yf - leg_h + 14 * s], torso_w * .3, fill=shirt)
    aw = torso_w * .17
    # left arm (down)
    l0 = (x - torso_w / 2 + aw * .6, top + aw)
    l1 = (x - torso_w / 2 - aw * .5, top + torso_h * .78)
    p.line([l0, l1], shirt, aw); p.circle(l1[0], l1[1], aw * .55, fill=SKIN)
    # right arm (down or waving)
    r0 = (x + torso_w / 2 - aw * .6, top + aw)
    if wave > 0:
        ang = -1.05 + 0.3 * math.sin(t * 9)
        r1 = (r0[0] + math.cos(ang) * torso_h * .75, r0[1] + math.sin(ang) * torso_h * .75)
    else:
        r1 = (x + torso_w / 2 + aw * .5, top + torso_h * .78)
    p.line([r0, r1], shirt, aw); p.circle(r1[0], r1[1], aw * .55, fill=SKIN)
    if hold == "phone":
        p.rr([l1[0] - 18 * s, l1[1] - 50 * s, l1[0] + 18 * s, l1[1] + 10 * s], 6 * s, fill=(30, 34, 44))
        p.rr([l1[0] - 13 * s, l1[1] - 44 * s, l1[0] + 13 * s, l1[1] + 4 * s], 4 * s, fill=(120, 190, 255))
    if hold == "wrench":
        p.line([(r1[0], r1[1]), (r1[0] + 50 * s, r1[1] - 50 * s)], (170, 176, 186), 12 * s)
        p.circle(r1[0] + 55 * s, r1[1] - 55 * s, 16 * s, outline=(170, 176, 186), width=8 * s)
    return top

def dave(p, x, yf, s=1.0, mood="happy", t=0.0, wave=0.0, hold=None):
    bob = math.sin(t * 2.0) * 4 * s
    yf = yf + 0
    top = _body(p, x, yf, s, (60, 90, 150), (60, 90, 150), 250 * s, 240 * s, 150 * s, wave=wave, t=t, hold=hold)
    p.rr([x - 70 * s, top + 10 * s, x - 40 * s, top + 200 * s], 10 * s, fill=(90, 120, 180))   # overall straps
    p.rr([x + 40 * s, top + 10 * s, x + 70 * s, top + 200 * s], 10 * s, fill=(90, 120, 180))
    p.rr([x - 60 * s, top + 120 * s, x + 60 * s, top + 190 * s], 12 * s, fill=(90, 120, 180))  # pocket
    hr = 92 * s
    hy = top - hr * .8 + bob
    for sx in (-1, 1):   # side tufts (drawn behind the head), bald top
        p.ell([x + sx * hr * .9 - hr * .16, hy - hr * .35, x + sx * hr * .9 + hr * .16, hy + hr * .3], fill=(110, 75, 50))
    p.circle(x, hy, hr, fill=SKIN)
    _face(p, x, hy, hr, mood, t, 0.3)
    p.rr([x - hr * .38, hy + hr * .2, x + hr * .38, hy + hr * .36], hr * .08, fill=(110, 75, 50))   # moustache

def sue(p, x, yf, s=1.0, mood="happy", t=0.0, wave=0.0, hold=None):
    bob = math.sin(t * 2.0 + 1) * 4 * s
    top = _body(p, x, yf, s, (235, 120, 150), (70, 70, 90), 200 * s, 220 * s, 150 * s, wave=wave, t=t, hold=hold)
    hr = 82 * s
    hy = top - hr * .8 + bob
    for k in range(12):   # curly hair behind
        a = math.radians(180 + k * 16 - 8)
        p.circle(x + math.cos(a) * hr * 1.02, hy + math.sin(a) * hr * .95 + hr * .2, hr * .36, fill=(190, 80, 50))
    p.circle(x - hr * .95, hy + hr * .45, hr * .32, fill=(190, 80, 50)); p.circle(x + hr * .95, hy + hr * .45, hr * .32, fill=(190, 80, 50))
    p.circle(x, hy, hr, fill=SKIN)
    for k in range(5):
        p.circle(x - hr * .55 + k * hr * .28, hy - hr * .78, hr * .26, fill=(190, 80, 50))
    _face(p, x, hy, hr, mood, t, 1.3, glasses=True)

def ellie(p, x, yf, s=1.0, mood="neutral", t=0.0, wave=0.0, hold="phone"):
    bob = math.sin(t * 2.0 + 2) * 3 * s
    hr = 72 * s
    torso_w, torso_h, leg_h = 170 * s, 200 * s, 160 * s
    top = yf - leg_h - torso_h
    hy = top - hr * .8 + bob
    p.rr([x - hr * 1.05, hy - hr * .6, x + hr * 1.05, top + 120 * s], hr * .6, fill=(45, 35, 40))   # long hair behind
    _body(p, x, yf, s, (130, 90, 200), (50, 60, 90), torso_w, torso_h, leg_h, wave=wave, t=t, hold=hold)
    p.rr([x - 22 * s, top - 6 * s, x + 22 * s, top + 60 * s], 8 * s, fill=(110, 75, 180))   # hood strings area
    p.circle(x, hy, hr, fill=SKIN)
    p.d.chord([(x - hr * 1.02) * S, (hy - hr * 1.05) * S, (x + hr * 1.02) * S, (hy + hr * .35) * S], 180, 360, fill=(45, 35, 40))
    _face(p, x, hy + hr * .08, hr * .95, mood, t, 2.1)

def alfie(p, x, yf, s=1.0, mood="grin", t=0.0, wave=0.0, hold=None):
    bob = abs(math.sin(t * 3.0)) * 8 * s
    hr = 70 * s
    top = _body(p, x, yf - bob, s, (90, 180, 100), (60, 90, 150), 150 * s, 150 * s, 110 * s, legs_skin=True, wave=wave, t=t, hold=hold)
    hy = top - hr * .8
    for k in range(7):   # spiky hair
        bx = x - hr * .85 + k * hr * .28
        p.poly([(bx - hr * .2, hy - hr * .55), (bx + hr * .05, hy - hr * 1.25), (bx + hr * .3, hy - hr * .55)], (240, 200, 80))
    p.circle(x, hy, hr, fill=SKIN)
    p.d.chord([(x - hr) * S, (hy - hr * 1.0) * S, (x + hr) * S, (hy + hr * .1) * S], 180, 360, fill=(240, 200, 80))
    _face(p, x, hy + hr * .05, hr * .95, mood, t, 0.7)
    # little volcano on the t-shirt
    p.poly([(x - 30 * s, top + 100 * s), (x - 8 * s, top + 55 * s), (x + 8 * s, top + 55 * s), (x + 30 * s, top + 100 * s)], (120, 80, 60))
    p.circle(x, top + 52 * s, 8 * s, fill=ORANGE)

def crumbs(p, x, yf, s=1.0, mood="happy", t=0.0):
    wag = math.sin(t * 12) * 0.5
    body_c, ear_c = (176, 120, 70), (120, 80, 45)
    tx, ty = x + 120 * s, yf - 120 * s
    p.line([(tx, ty), (tx + 70 * s * math.cos(-0.9 + wag), ty + 70 * s * math.sin(-0.9 + wag))], body_c, 18 * s)
    p.ell([x - 120 * s, yf - 160 * s, x + 130 * s, yf - 40 * s], fill=body_c)
    for dx in (-90, -40, 50, 100):
        p.rr([x + dx * s - 14 * s, yf - 70 * s, x + dx * s + 14 * s, yf], 10 * s, fill=body_c)
    hx, hy = x - 110 * s, yf - 190 * s
    p.ell([hx - 105 * s, hy - 40 * s, hx - 45 * s, hy + 80 * s], fill=ear_c)
    p.ell([hx + 45 * s, hy - 40 * s, hx + 105 * s, hy + 80 * s], fill=ear_c)
    p.circle(hx, hy, 72 * s, fill=body_c)
    p.ell([hx - 40 * s, hy + 10 * s, hx + 40 * s, hy + 62 * s], fill=(222, 190, 150))
    p.circle(hx, hy + 18 * s, 13 * s, fill=INK)
    for sx in (-1, 1):
        p.circle(hx + sx * 26 * s, hy - 16 * s, 9 * s, fill=INK)
    if mood in ("happy", "grin"):
        p.rr([hx - 10 * s, hy + 40 * s, hx + 10 * s, hy + 72 * s], 8 * s, fill=(240, 120, 140))

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
