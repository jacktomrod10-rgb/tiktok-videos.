"""Episode 5 (short): Your fridge doesn't make cold, it moves heat.
    python3 -I videos/2026-11-24-fridge-cold/make.py tts | stills ... | render videos/2026-11-24-fridge-cold.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "fridge-cold", episode=5, title="Where does the *heat* in your fridge *go*?",
    lines=[
        "Your fridge doesn't make cold. It moves heat.",
        "It pulls the heat out of your food and dumps it into your kitchen. That's why the back of a fridge feels warm.",
        "Inside, a liquid called refrigerant evaporates in the pipes, and evaporating soaks up heat.",
        "A pump called the compressor squeezes that gas, which makes it even hotter.",
        "The pipes on the back let the heat out into the room, the gas turns back into liquid, and the loop starts again.",
        "Air conditioners work the same way.",
        "Did you know your fridge heats your kitchen? Comment yes or no.",
        "Follow for more everyday genius.",
    ],
    display=[
        "Your fridge doesn't make *cold*. It moves *heat*.",
        "It pulls the heat out of your *food* and dumps it into your *kitchen*. That's why the *back* of a fridge feels *warm*.",
        "Inside, a liquid called *refrigerant* evaporates in the pipes, and evaporating *soaks* *up* heat.",
        "A pump called the *compressor* squeezes that gas, which makes it even *hotter*.",
        "The pipes on the back let the heat out into the *room*, the gas turns back into liquid, and the *loop* starts again.",
        "*Air* *conditioners* work the same way.",
        "Did you know your fridge *heats* your kitchen? Comment *yes* or *no*.",
        "Follow for more everyday *genius*.",
    ],
)

COLD, HOT = (110, 190, 255), (255, 110, 80)

def fridge(p, cx, cy, sc=1.0, open_k=0.0):
    w, h = 300 * sc, 520 * sc
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 34 * sc, fill=(232, 236, 242))
    p.line([(cx - w / 2 + 10 * sc, cy - h / 2 + 170 * sc), (cx + w / 2 - 10 * sc, cy - h / 2 + 170 * sc)], fill=EDGE, width=5 * sc)
    for y0, y1 in ((cy - h / 2 + 40 * sc, cy - h / 2 + 130 * sc), (cy - h / 2 + 210 * sc, cy - h / 2 + 330 * sc)):
        p.rr([cx + w / 2 - 44 * sc, y0, cx + w / 2 - 30 * sc, y1], 6 * sc, fill=(170, 178, 190))

def heat_wave(p, x, y, t, k=1.0, col=HOT, h=70):
    for i in range(3):
        xx = x + i * 26
        pts = [(xx + 8 * math.sin((j / 6.0) * 2 * math.pi + t * 6 + i), y - j * h / 6 * k) for j in range(7)]
        p.line(pts, fill=col, width=7)

def snow(p, cx, cy, r, col=COLD):
    for a in range(3):
        ang = math.radians(a * 60)
        p.line([(cx - r * math.cos(ang), cy - r * math.sin(ang)), (cx + r * math.cos(ang), cy + r * math.sin(ang))], fill=col, width=max(2, r * 0.16))

@V.scene(0)
def hook(p, t, L):
    k = eback(prog(t, 0.0, 0.45))
    if k <= 0: return
    fridge(p, 540, 730, sc=k)
    sp = eback(prog(t, 0.5, 0.9)) * (1 - prog(t, 1.4, 1.6))
    if sp > 0:
        snow(p, 540, 560, 70 * sp)
        cross(p, 540, 560, 80, prog(t, 1.1, 1.3), shake_t=t - 1.1)
    pill(p, 540, 395, "DOESN'T MAKE COLD", prog(t, 1.0, 1.3) * (1 - prog(t, 1.8, 2.0)), bg=RED, fg=WHITE, size=42)
    if t > 1.8:
        u = eo(prog(t, 1.8, 2.4))
        p.arrow((540, 640), (540 + 360 * u, 640), HOT, width=16, head=44)
        heat_wave(p, 880, 600, t, k=u)
        pill(p, 540, 395, "IT MOVES HEAT", prog(t, 1.9, 2.2), bg=YEL, size=46)

@V.scene(1)
def kitchen(p, t, L):
    a, e = L(1)
    k = eback(prog(t, a, a + 0.4))
    # fridge in side view, food inside, coils on the back
    p.rr([300, 440, 700, 1060], 30, fill=(232, 236, 242))
    p.rr([330, 470, 640, 1030], 18, fill=(196, 222, 246))
    p.rect([330, 640, 640, 652], fill=WHITE)
    p.rect([330, 830, 640, 842], fill=WHITE)
    p.rr([370, 560, 470, 640], 12, fill=YEL)                     # cheese
    p.rr([520, 520, 560, 640], 14, fill=(90, 200, 140))          # bottle
    p.circle(430, 790, 40, fill=ORANGE)                          # orange
    p.rr([500, 740, 600, 830], 14, fill=(230, 120, 160))         # tub
    for i in range(9):                                           # coils on the back
        y = 480 + i * 64
        p.arc([700, y, 760, y + 64], 270, 90, fill=(60, 64, 72), width=8)
    path = [(450, 600), (560, 700), (680, 760), (740, 700), (820, 640), (900, 560)]
    if t > a + 0.6:
        flow_dots(p, path, t - a, speed=0.7, n=7, r=12, fill=HOT)
    if t > a + 3.0:
        heat_wave(p, 840, 560, t, k=eo(prog(t, a + 3.0, a + 3.6)))
    pill(p, 540, 395, "HEAT OUT OF YOUR FOOD", prog(t, a + 0.4, a + 0.8) * (1 - prog(t, a + 2.6, a + 2.8)), bg=WHITE, size=40)
    pill(p, 540, 395, "INTO YOUR KITCHEN", prog(t, a + 2.8, a + 3.1) * (1 - prog(t, a + 4.0, a + 4.2)), bg=YEL, size=42)
    if t > a + 4.2:
        pill(p, 540, 395, "THE BACK FEELS WARM", prog(t, a + 4.2, a + 4.5), bg=ORANGE, size=42)
        g = 0.5 + 0.5 * pulse(t, 0.8)
        p.rr([696, 470, 770, 1050], 20, outline=(255, int(140 + 60 * g), 80), width=6)

# the loop: inside (left, cold coil) -> compressor (bottom) -> back coils (right, hot) -> back inside
LOOP = [(250, 520), (250, 940), (540, 940), (830, 940), (830, 520), (540, 520), (250, 520)]

def loop_dot_colour(x, y):
    if y > 900 and x > 540: return HOT
    if x > 800: return HOT
    if y < 560 and x > 400: return (200, 160, 220)
    return COLD

@V.scene(2, 4)
def cycle(p, t, L):
    a2, _ = L(2); a3, _ = L(3); a4, e4 = L(4)
    k = eo(prog(t, a2, a2 + 0.6))
    # inside box and outside label
    p.rr([140, 450, 470, 1010], 26, fill=(36, 58, 88))
    p.text((305, 1050), "INSIDE THE FRIDGE", f2("dm", 32), MUTED)
    p.text((830, 1050), "BACK OF THE FRIDGE", f2("dm", 32), MUTED)
    p.line(LOOP, fill=(70, 84, 104), width=22)
    # evaporator coil (inside) and condenser coil (back)
    for i in range(5):
        y = 580 + i * 70
        p.arc([215, y, 285, y + 70], 90 if i % 2 else 270, 270 if i % 2 else 90, fill=COLD, width=12)
        p.arc([795, y, 865, y + 70], 90 if i % 2 else 270, 270 if i % 2 else 90, fill=HOT if t > a3 + 1.0 else (150, 120, 120), width=12)
    # refrigerant flowing round
    n = 12
    for j in range(n):
        x, y = path_point(LOOP, (t - a2) * 0.12 + j / n)
        p.circle(x, y, 14, fill=loop_dot_colour(x, y))
    # compressor (drawn over the pipe)
    sq = 1 + 0.08 * math.sin(t * 14) * (t > a3)
    p.rr([540 - 90 * sq, 880, 540 + 90 * sq, 1000], 24, fill=SLATE_L)
    p.text((540, 942), "PUMP", f2("dm", 34), WHITE)
    # stage labels
    pill(p, 540, 395, "EVAPORATES = SOAKS UP HEAT", prog(t, a2 + 2.6, a2 + 3.0) * (1 - prog(t, a3 - 0.3, a3)), bg=(170, 215, 255), size=34)
    if a2 + 3.0 < t < a3:
        snow(p, 305, 760, 40 + 6 * pulse(t, 1.0))
    pill(p, 540, 395, "SQUEEZED = HOTTER", prog(t, a3 + 1.0, a3 + 1.3) * (1 - prog(t, a4 - 0.3, a4)), bg=ORANGE, size=40)
    if t > a3 + 1.0:
        p.arrow((540, 870), (540, 790), HOT, width=10, head=30)
    if t > a4:
        heat_wave(p, 905, 640, t, k=eo(prog(t, a4, a4 + 0.6)))
        pill(p, 640, 395, "HEAT OUT TO THE ROOM", prog(t, a4 + 0.3, a4 + 0.6) * (1 - prog(t, a4 + 4.0, a4 + 4.3)), bg=YEL, size=38)
        pill(p, 540, 395, "AND REPEAT", prog(t, a4 + 4.3, a4 + 4.6), bg=GREEN, size=42)

@V.scene(5)
def aircon(p, t, L):
    a, e = L(5)
    k = eback(prog(t, a, a + 0.4))
    if k <= 0: return
    # indoor wall unit
    p.rr([140, 520 - 60 * k, 620, 520 + 60 * k], 30, fill=(236, 240, 246))
    for i in range(3):
        p.line([(170, 560 + i * 14), (590, 560 + i * 14)], fill=EDGE, width=4)
    for i in range(4):
        x = 200 + i * 110
        y = 610 + ((t * 120 + i * 30) % 120)
        p.line([(x, y), (x + 30, y + 30)], fill=COLD, width=6)
    # outdoor unit with a spinning fan
    p.rr([620, 760, 960, 1060], 24, fill=(200, 206, 216))
    p.circle(790, 910, 110, fill=SLATE)
    for b in range(3):
        ang = t * 9 + b * 2 * math.pi / 3
        p.line([(790, 910), (790 + 95 * math.cos(ang), 910 + 95 * math.sin(ang))], fill=EDGE, width=22)
    heat_wave(p, 760, 740, t, k=k)
    pill(p, 540, 395, "SAME TRICK", prog(t, a + 0.4, a + 0.7), bg=YEL, size=46)

@V.scene(6, 7)
def outro(p, t, L):
    a6, _ = L(6); a7, _ = L(7)
    k = eback(prog(t, a6, a6 + 0.4))
    if k > 0:
        fridge(p, 540, 640, sc=0.62 * k)
        heat_wave(p, 650, 560, t, k=k, h=60)
    for i, (lab, col, x) in enumerate((("YES", GREEN, 330), ("NO", RED, 750))):
        kk = eback(prog(t, a6 + 2.4 + i * 0.3, a6 + 2.8 + i * 0.3))
        if kk <= 0: continue
        hl = int((t - a6 - 3.2) / 0.5) % 2 == i if t > a6 + 3.2 else False
        p.rr([x - 150 * kk, 930 - 70 * kk, x + 150 * kk, 930 + 70 * kk], 30, fill=col if hl else (36, 54, 82), outline=col, width=6)
        p.text((x, 932), lab, f2("anton", max(8, int(90 * kk))), INK if hl else WHITE)
    pill(p, 540, 395, "COMMENT YES OR NO", prog(t, a6 + 2.2, a6 + 2.6), size=44)
    fp = prog(t, a7 + 0.1, a7 + 0.5)
    if fp > 0:
        r = 56 * eback(fp)
        p.circle(540, 1085, r, fill=RED)
        p.line([(540 - r * .45, 1085), (540 + r * .45, 1085)], fill=WHITE, width=12)
        p.line([(540, 1085 - r * .45), (540, 1085 + r * .45)], fill=WHITE, width=12)

@V.sounds
def cues(L):
    a6, _ = L(6)
    return [(1.1, "boing"), (1.9, "pop"), (a6 + 2.4, "pop"), (a6 + 2.7, "pop")]

if __name__ == "__main__":
    V.main()
