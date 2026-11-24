"""Short explainer: the first thing ever scanned at a till (barcodes).
    python3 -I videos/2026-11-24-barcode/make.py tts | stills ... | render videos/2026-11-24-barcode.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "barcode", episode=6, title="What was the *first* thing ever *scanned*?",
    lines=[
        "The first thing ever scanned at a till was chewing gum.",
        "A ten-pack of Juicy Fruit, in a supermarket in Ohio, on the twenty-sixth of June, nineteen seventy-four.",
        "Here's how the beep works. A light sweeps across the stripes. Black bars soak it up, and white gaps bounce it back.",
        "A sensor turns that flicker into the product's number.",
        "And the first few digits don't tell you where it was made. They show which country's barcode office gave out the number.",
        "Grab something from your cupboard. What are its first three digits? Comment them.",
        "Follow for more everyday genius.",
    ],
    display=[
        "The first thing ever *scanned* at a till was *chewing* *gum*.",
        "A ten-pack of *Juicy* *Fruit*, in a supermarket in *Ohio*, on the 26th of June, *1974*.",
        "Here's how the *beep* works. A light sweeps across the stripes. *Black* bars soak it up, and *white* gaps bounce it back.",
        "A *sensor* turns that flicker into the product's *number*.",
        "And the first few digits *don't* tell you where it was made. They show which country's barcode *office* gave out the number.",
        "Grab something from your *cupboard*. What are its first *three* digits? *Comment* them.",
        "Follow for more everyday *genius*.",
    ],
)

# ---- EAN-13 (GS1's example number 5012345678900) ----
_L = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
_G = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
_R = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]
_PAR = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]
NUM = "5012345678900"
def ean13(num):
    d = [int(c) for c in num]
    bits = "101"
    for i, c in enumerate(d[1:7]):
        bits += (_L if _PAR[d[0]][i] == "L" else _G)[c]
    bits += "01010"
    for c in d[7:]:
        bits += _R[c]
    return bits + "101"
BITS = ean13(NUM)
GUARD = set(list(range(0, 3)) + list(range(45, 50)) + list(range(92, 95)))

def barcode(p, cx, cy, mw, h, digits=True, hl3=0.0):
    w = 95 * mw
    x0 = cx - w / 2
    p.rr([x0 - 14 * mw, cy - h / 2 - 16, x0 + w + 10 * mw, cy + h / 2 + (70 if digits else 16)], 14, fill=WHITE)
    for i, b in enumerate(BITS):
        if b == "1":
            ext = 26 if i in GUARD else 0
            p.rect([x0 + i * mw, cy - h / 2, x0 + (i + 1) * mw - 0.5, cy + h / 2 + ext], fill=INK)
    if digits:
        f = f2("dm", int(mw * 7.4))
        ty = cy + h / 2 + 40
        p.text((x0 - 8 * mw, ty), NUM[0], f, INK)
        for i in range(6):
            p.text((x0 + (3 + 7 * i + 3.5) * mw, ty), NUM[1 + i], f, INK)
            p.text((x0 + (50 + 7 * i + 3.5) * mw, ty), NUM[7 + i], f, INK)
        if hl3 > 0:
            xa, xb = x0 - 14 * mw, x0 + 20.5 * mw
            p.rr([xa, ty - 30, xb, ty + 30], 10, outline=RED, width=int(6 * hl3) + 1)
    return x0, w

def gum(p, cx, cy, sc):
    p.rr([cx - 260 * sc, cy - 80 * sc, cx + 260 * sc, cy + 80 * sc], 26 * sc, fill=YEL)
    for i in range(1, 10):
        x = cx - 260 * sc + i * 52 * sc
        p.line([(x, cy - 80 * sc), (x, cy + 80 * sc)], fill=(230, 180, 40), width=max(1, 3 * sc))
    p.rr([cx - 150 * sc, cy - 30 * sc, cx + 150 * sc, cy + 30 * sc], 14 * sc, fill=(255, 245, 200))

@V.scene(0, 1)
def first_scan(p, t, L):
    a1, e1 = L(1)
    k = eback(prog(t, 0.05, 0.5))
    if k <= 0: return
    up = eio(prog(t, a1 - 0.2, a1 + 0.6))
    gy = lerp(680, 560, up)
    gum(p, 540, gy, k)
    # scanner beam sweeping over the pack
    if 0.6 < t < a1 + 0.5:
        u = (t * 1.4) % 1.0
        x = 300 + 480 * u
        p.line([(x, gy - 110), (x, gy + 110)], fill=RED, width=6)
    pill(p, 540, gy + 165, "BEEP!", prog(t, 2.3, 2.5) * (1 - prog(t, a1 - 0.3, a1)), bg=GREEN, size=50)
    if t > a1:
        big_number(p, t, a1 + 4.6, 1974, cy=850, size=150, start=1950, dur=0.9)
        pill(p, 540, 395, "10-PACK OF JUICY FRUIT", prog(t, a1 + 0.3, a1 + 0.6), bg=WHITE, size=40)
        pill(p, 310, 1010, "OHIO, USA", prog(t, a1 + 1.8, a1 + 2.1), bg=YEL, size=40)
        pill(p, 770, 1010, "26 JUNE", prog(t, a1 + 3.0, a1 + 3.3), bg=YEL, size=40)

@V.scene(2, 3)
def how(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3)
    mw, cx, cy, h = 7.6, 540, 640, 300
    x0, w = barcode(p, cx, cy, mw, h, digits=t > a3 + 0.6)
    # light sweep
    s = eio(prog(t, a2 + 1.6, a2 + 4.2)) if t < a3 else eio(prog(t, a3, a3 + 1.8))
    lx = x0 + w * s
    p.line([(lx, cy - h / 2 - 30), (lx, cy + h / 2 + 30)], fill=RED, width=7)
    # bounce-back rays where the light hits a white gap
    i = int((lx - x0) / mw)
    if 0 <= i < 95 and BITS[i] == "0" and a2 + 1.6 < t:
        for dy in (-60, 0, 60):
            p.line([(lx, cy + dy), (lx - 50, cy + dy - 50)], fill=YEL, width=6)
    # the signal it produces (drawn up to the beam)
    sy = 1020
    p.rect([x0, sy - 40, x0 + w, sy + 40], fill=(28, 42, 64))
    pts, prev = [], None
    for j in range(95):
        xx = x0 + j * mw
        if xx > lx: break
        yv = sy - 30 if BITS[j] == "0" else sy + 30
        if prev is not None and prev != yv: pts.append((xx, prev))
        pts.append((xx, yv)); prev = yv
    if len(pts) > 1:
        p.line(pts, fill=GREEN, width=5)
    p.text((x0 - 10, sy), "", f2("dm", 10), WHITE)
    pill(p, 300, 395, "BLACK: SOAKS IT UP", prog(t, a2 + 4.2, a2 + 4.5) * (1 - prog(t, a3 - 0.2, a3)), bg=WHITE, size=34)
    pill(p, 780, 395, "WHITE: BOUNCES BACK", prog(t, a2 + 5.4, a2 + 5.7) * (1 - prog(t, a3 - 0.2, a3)), bg=YEL, size=34)
    pill(p, 540, 395, "LIGHT PATTERN = NUMBER", prog(t, a3 + 0.4, a3 + 0.7), bg=GREEN, size=40)

@V.scene(4)
def prefix(p, t, L):
    a, e = L(4)
    barcode(p, 540, 600, 7.0, 260, hl3=0.5 + 0.5 * pulse(t, 0.7) if t > a + 0.6 else 0.0)
    if t > a + 1.6:
        cross(p, 540, 960, 60, prog(t, a + 1.6, a + 1.8), shake_t=t - (a + 1.6))
    pill(p, 540, 395, "NOT WHERE IT WAS MADE", prog(t, a + 1.4, a + 1.7) * (1 - prog(t, a + 3.6, a + 3.9)), bg=RED, fg=WHITE, size=42)
    if t > a + 3.9:
        k = eback(prog(t, a + 3.9, a + 4.3))
        # a little office building
        bx, by = 540, 980
        p.rr([bx - 120 * k, by - 90 * k, bx + 120 * k, by + 90 * k], 10, fill=(200, 206, 216))
        for r in range(2):
            for c in range(4):
                p.rect([bx - 95 * k + c * 52 * k, by - 65 * k + r * 60 * k, bx - 65 * k + c * 52 * k, by - 30 * k + r * 60 * k], fill=(120, 170, 230))
        pill(p, 540, 395, "WHO ISSUED THE NUMBER", prog(t, a + 4.2, a + 4.5), bg=GREEN, size=42)

@V.scene(5, 6)
def outro(p, t, L):
    a5, _ = L(5); a6, _ = L(6)
    k = eback(prog(t, a5, a5 + 0.4))
    if k > 0:
        # cupboard with a tin, a box and a jar
        p.rr([200, 480, 880, 900], 24, fill=(120, 84, 56))
        p.rr([230, 510, 850, 870], 16, fill=(70, 50, 36))
        p.rr([280, 640 - 140 * k, 400, 860], 14, fill=(200, 206, 216))
        p.rr([450, 600 - 100 * k, 620, 860], 10, fill=ORANGE)
        p.rr([670, 700 - 60 * k, 800, 860], 30, fill=(170, 215, 255))
        for x in (340, 535, 735):
            p.rr([x - 40, 790, x + 40, 840], 6, fill=WHITE)
            for j in range(9):
                p.rect([x - 34 + j * 8, 796, x - 31 + j * 8, 834], fill=INK)
    q = prog(t, a5 + 2.0, a5 + 2.4)
    if q > 0:
        for i in range(3):
            kk = eback(prog(t, a5 + 2.2 + i * 0.25, a5 + 2.6 + i * 0.25))
            x = 400 + i * 140
            p.rr([x - 55 * kk, 960 - 65 * kk, x + 55 * kk, 960 + 65 * kk], 18, fill=YEL if int(t * 2 + i) % 3 == 0 else WHITE)
            p.text((x, 962), "?", f2("anton", max(8, int(90 * kk))), INK)
    pill(p, 540, 395, "COMMENT YOUR FIRST 3 DIGITS", prog(t, a5 + 3.0, a5 + 3.4), size=40)
    fp = prog(t, a6 + 0.1, a6 + 0.5)
    if fp > 0:
        r = 52 * eback(fp)
        p.circle(860, 1090, r, fill=RED)
        p.line([(860 - r * .45, 1090), (860 + r * .45, 1090)], fill=WHITE, width=12)
        p.line([(860, 1090 - r * .45), (860, 1090 + r * .45)], fill=WHITE, width=12)

@V.sounds
def cues(L):
    a4, _ = L(4)
    return [(2.3, "ding"), (a4 + 1.6, "boing"), (a4 + 4.2, "pop")]

if __name__ == "__main__":
    V.main()
