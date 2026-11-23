import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "ykk-zips", episode=5,
    lines=[
        "Check the zip on your jacket. It probably says Y K K.",
        "By one estimate, those three letters are on about half the zips on Earth.",
        "They stand for Yoshida Kohg yoh Kabooshiki guysha. Roughly, Yoshida Manufacturing Company.",
        "It was started in Tokyo in nineteen thirty-four, by a young man called Tadao Yoshida.",
        "Today it makes more than seven billion zips a year.",
        "And here's the genius. Most companies buy in their parts. Y K K makes almost everything itself.",
        "It melts its own brass, makes its own polyester, spins its own thread, and weaves and dyes its own tape.",
        "It even builds the machines that make the zips, and keeps them hidden from competitors.",
        "Controlling every step means every zip comes out the same, again and again.",
        "And for clothing brands, that matters. A zip is a tiny part of the cost, but if it breaks, the whole jacket is useless.",
        "So next time a zip just works, you know who to thank. Follow for more everyday genius.",
    ],
    display=[
        "Check the *zip* on your jacket. It probably says *YKK*.",
        "By one estimate, those three letters are on about *half* the zips on Earth.",
        "They stand for *Yoshida Kogyo Kabushikigaisha*. Roughly, Yoshida Manufacturing Company.",
        "It was started in *Tokyo* in *1934*, by a young man called Tadao Yoshida.",
        "Today it makes more than *7 billion* zips a year.",
        "And here's the *genius*. Most companies buy in their parts. YKK makes almost *everything* itself.",
        "It melts its own *brass*, makes its own *polyester*, spins its own *thread*, and weaves and dyes its own *tape*.",
        "It even builds the *machines* that make the zips, and keeps them *hidden* from competitors.",
        "Controlling every step means every zip comes out the *same*, again and again.",
        "And for clothing brands, that matters. A zip is a *tiny* part of the cost, but if it breaks, the whole jacket is *useless*.",
        "So next time a zip just works, you know who to *thank*. Follow for more everyday *genius*.",
    ],
)

TAPE = (60, 70, 86)
TOOTH = BRASS

def zip_v(p, cx, y_top, y_bot, closed_to, w=46, tooth=26, slider=True, tab_text=True, sc=1.0):
    """Vertical zip: closed from y_bot up to closed_to, open above."""
    for side in (-1, 1):
        pts_x = cx + side * (w * sc)
        p.rr([pts_x - 40 * sc if side < 0 else pts_x, y_top, pts_x if side < 0 else pts_x + 40 * sc, y_bot], 8, fill=TAPE)
    y = y_bot
    i = 0
    while y > y_top + tooth * sc:
        y -= tooth * sc
        gap = 0 if y > closed_to else min(60 * sc, (closed_to - y) * 0.25)
        side = -1 if i % 2 == 0 else 1
        x = cx + side * (gap + 6 * sc)
        p.rr([x - 22 * sc, y, x + 22 * sc, y + tooth * sc * 0.8], 6 * sc, fill=TOOTH)
        i += 1
    if slider:
        p.rr([cx - 44 * sc, closed_to - 40 * sc, cx + 44 * sc, closed_to + 40 * sc], 18 * sc, fill=(190, 196, 205))
        p.rr([cx - 34 * sc, closed_to + 30 * sc, cx + 34 * sc, closed_to + 160 * sc], 22 * sc, fill=(210, 214, 220))
        if tab_text:
            p.text((cx, closed_to + 100 * sc), "YKK", f2("dm", max(8, int(34 * sc))), INK)

@V.scene(0)
def intro(p, t, L):
    k = eio(prog(t, 0.2, 2.0))
    zip_v(p, 540, 330, 1150, lerp(1000, 560, k))
    if t > 2.2:
        p.circle(540, 660, 120 + 10 * pulse(t, 0.8), outline=YEL, width=8)

@V.scene(1)
def half_world(p, t, L):
    a, _ = L(1)
    k = eo(prog(t, a + 0.5, a + 2.0))
    p.circle(540, 700, 280, fill=(40, 60, 90))
    if k > 0:
        p.d.pieslice([(540 - 280) * S, (700 - 280) * S, (540 + 280) * S, (700 + 280) * S], -90, -90 + 180 * k, fill=YEL)
    p.circle(540, 700, 280, outline=WHITE, width=6)
    pill(p, 540, 1080, "ABOUT HALF THE WORLD'S ZIPS", prog(t, a + 1.8, a + 2.2))

@V.scene(2, 3)
def name_and_origin(p, t, L):
    a2, _ = L(2); a3, _ = L(3)
    if t < a3:
        words = [("Y", "YOSHIDA"), ("K", "KOGYO"), ("K", "KABUSHIKIGAISHA")]
        for i, (letter, word) in enumerate(words):
            y = 500 + i * 190
            k = eback(prog(t, a2 + 0.2 + i * 0.6, a2 + 0.6 + i * 0.6))
            if k > 0:
                p.text((200, y), letter, f2("anton", max(10, int(150 * k))), YEL)
                p.text((300, y + 8), word, f2("dm", 50), WHITE, anchor="lm")
        pill(p, 540, 1100, "YOSHIDA MANUFACTURING CO.", prog(t, a2 + 3.4, a2 + 3.8), bg=WHITE, size=36)
    else:
        big_number(p, t, a3 + 0.6, 1934, cy=640, start=1900, dur=1.0)
        pill(p, 540, 430, "TOKYO", prog(t, a3, a3 + 0.4))
        pill(p, 540, 860, "FOUNDER: TADAO YOSHIDA", prog(t, a3 + 2.6, a3 + 3.0), bg=WHITE)

@V.scene(4)
def billions(p, t, L):
    a, _ = L(4)
    # falling mini zips
    for i in range(18):
        x = 100 + (i * 137) % 880
        y = ((t - a) * 260 + i * 97) % 900 + 300
        p.rr([x - 8, y, x + 8, y + 70], 4, fill=(60, 70, 86))
        p.rr([x - 4, y + 4, x + 4, y + 66], 3, fill=BRASS)
    p.rr([200, 520, 880, 820], 40, fill=BG1)
    big_number(p, t, a + 0.3, 7, cx=540, cy=630, size=150, start=0, dur=1.2, fmt="{} BILLION+")
    pill(p, 540, 770, "ZIPS A YEAR", prog(t, a + 1.2, a + 1.6), bg=WHITE)

CHAIN = [("BRASS", 300, 470), ("POLYESTER", 780, 470), ("THREAD", 300, 680), ("TAPE", 780, 680), ("TEETH", 300, 890), ("MACHINES", 780, 890)]

@V.scene(5, 7)
def in_house(p, t, L):
    a5, _ = L(5); a6, e6 = L(6); a7, _ = L(7)
    if t < a6:
        # buy-in vs make-it
        p.rr([120, 480, 500, 900], 30, fill=(40, 60, 90))
        p.rr([580, 480, 960, 900], 30, fill=(40, 60, 90))
        p.text((310, 560), "OTHERS", f2("dm", 40), MUTED)
        p.text((770, 560), "YKK", f2("dm", 40), YEL)
        for i in range(3):
            k = prog(t, a5 + 1.0 + i * 0.3, a5 + 1.6 + i * 0.3)
            if k > 0:
                p.arrow((60 + 120 * k, 660 + i * 70), (220 + 60 * k, 660 + i * 70), MUTED, width=8, head=24)
        if t > a5 + 3.2:
            sparkle(p, 770, 720, 70 * eback(prog(t, a5 + 3.2, a5 + 3.6)))
            pill(p, 540, 1000, "MADE IN-HOUSE", prog(t, a5 + 3.4, a5 + 3.8))
    else:
        n = 4 + int(prog(t, a7, a7 + 0.4) * 2) if t > a7 else 0
        for i, (lab, x, y) in enumerate(CHAIN):
            t0 = a6 + i * 1.1 if i < 4 else a7 + 0.2 + (i - 4) * 0.8
            k = eback(prog(t, t0, t0 + 0.4))
            if k <= 0: continue
            p.rr([x - 200 * k, y - 70 * k, x + 200 * k, y + 70 * k], 26, fill=(40, 60, 90), outline=YEL, width=5)
            p.text((x, y), lab, f2("dm", max(8, int(44 * k))), WHITE)
        if t > a7 + 2.5:
            p.rr([620, 820, 940, 960], 26, fill=INK)
            p.text((780, 890), "HIDDEN", f2("anton", 60), RED)

@V.scene(8, 9)
def consistency(p, t, L):
    a8, _ = L(8); a9, _ = L(9)
    if t < a9:
        for i in range(5):
            x = 160 + i * 190
            k = eback(prog(t, a8 + i * 0.25, a8 + 0.4 + i * 0.25))
            if k > 0:
                zip_v(p, x, 430, 950, 600, w=26 * k, tooth=22, slider=True, tab_text=False, sc=0.55 * k)
                tick(p, x, 1030, 34, prog(t, a8 + 1.6 + i * 0.2, a8 + 1.9 + i * 0.2))
    else:
        # jacket outline with a zip
        k = eback(prog(t, a9, a9 + 0.5))
        if k > 0:
            p.poly([(540 - 220 * k, 420), (540 + 220 * k, 420), (540 + 330 * k, 560), (540 + 260 * k, 640),
                    (540 + 220 * k, 600), (540 + 220 * k, 1060), (540 - 220 * k, 1060), (540 - 220 * k, 600),
                    (540 - 260 * k, 640), (540 - 330 * k, 560)], (70, 110, 160))
            p.line([(540, 430), (540, 1060)], BRASS, 10)
        pill(p, 540, 360, "TINY PART OF THE COST", prog(t, a9 + 2.4, a9 + 2.8) * (1 - prog(t, a9 + 4.4, a9 + 4.6)), bg=WHITE)
        if t > a9 + 4.6:
            cross(p, 540, 760, 110, prog(t, a9 + 4.6, a9 + 4.8), shake_t=t - (a9 + 4.6))
            pill(p, 540, 360, "BROKEN ZIP = USELESS JACKET", prog(t, a9 + 4.7, a9 + 5.1), bg=RED, fg=WHITE)

@V.scene(10)
def outro(p, t, L):
    a, _ = L(10)
    k = eio(prog(t, a + 0.2, a + 2.2))
    zip_v(p, 540, 330, 1150, lerp(1050, 420, k))
    if t > a + 2.3:
        sparkle(p, 700, 420, 40 * eback(prog(t, a + 2.3, a + 2.7)))
    fp = prog(t, a + 3.6, a + 4.0)
    if fp > 0:
        r = 58 * eback(fp)
        p.circle(820, 1000, r, fill=RED)
        p.line([(820 - r * .45, 1000), (820 + r * .45, 1000)], fill=WHITE, width=12)
        p.line([(820, 1000 - r * .45), (820, 1000 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
