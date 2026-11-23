import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "microwave-door", episode=2, title="Why doesn't your *microwave* cook *you*?",
    lines=[
        "Why doesn't your microwave cook you too?",
        "The answer is hiding in plain sight, right on the door.",
        "Inside, a device called a magnetron fires invisible waves, about two point four five billion times a second.",
        "They make the water molecules in your food twist and jostle, and that turns into heat.",
        "They only reach a centimetre or so into the food, which is one reason the middle can stay cold.",
        "The metal walls bounce those waves around inside the box.",
        "But you can see through the door. So why don't they escape there?",
        "Look closely. The window is covered by a metal screen, full of holes about one millimetre wide.",
        "A single microwave is about twelve centimetres long. That's over a hundred times bigger than the holes.",
        "So to a microwave, that screen behaves like a solid metal wall, and the waves bounce straight back in.",
        "But light waves are less than a thousandth of a millimetre long. Thousands of times smaller than the holes, so they slip right through.",
        "That's how you can watch your food, while the microwaves stay locked inside.",
        "One sheet of metal with holes in it. A window for light, and a wall for microwaves. Follow for more everyday genius.",
    ],
    display=[
        "Why doesn't your microwave cook *you* too?",
        "The answer is hiding in plain sight, right on the *door*.",
        "Inside, a device called a *magnetron* fires invisible waves, about *2.45 billion* times a second.",
        "They make the *water* molecules in your food twist and jostle, and that turns into *heat*.",
        "They only reach a *centimetre* or so into the food, which is one reason the middle can stay *cold*.",
        "The metal walls *bounce* those waves around inside the box.",
        "But you can see through the *door*. So why don't they *escape* there?",
        "Look closely. The window is covered by a *metal screen*, full of holes about *1 mm* wide.",
        "A single microwave is about *12 cm* long. That's over a *hundred* times bigger than the holes.",
        "So to a microwave, that screen behaves like a *solid* metal wall, and the waves bounce straight *back* in.",
        "But *light* waves are less than a *thousandth* of a millimetre long. Thousands of times *smaller* than the holes, so they slip right *through*.",
        "That's how you can *watch* your food, while the microwaves stay *locked* inside.",
        "One sheet of metal with holes in it. A *window* for light, and a *wall* for microwaves. Follow for more everyday *genius*.",
    ],
)

MW = (255, 120, 90)      # microwave colour
LIGHT = YEL

def wave(p, x0, x1, y, amp, wl, phase, fill, width=8):
    pts = []
    n = max(2, int((x1 - x0) / 6))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, y + amp * math.sin(2 * math.pi * (x - x0) / wl - phase)))
    p.line(pts, fill, width)

def oven(p, cx, cy, sc=1.0, glow=0.0, door_hl=0.0):
    w, h = 780 * sc, 500 * sc
    x0, y0 = cx - w / 2, cy - h / 2
    p.rr([x0, y0, x0 + w, y0 + h], 40 * sc, fill=(214, 218, 224), outline=EDGE, width=6 * sc)
    # door window with mesh
    wx0, wy0, wx1, wy1 = x0 + 50 * sc, y0 + 60 * sc, x0 + w - 220 * sc, y0 + h - 60 * sc
    p.rr([wx0, wy0, wx1, wy1], 24 * sc, fill=(40, 46, 56))
    if glow > 0:
        p.rr([wx0 + 20 * sc, wy0 + 20 * sc, wx1 - 20 * sc, wy1 - 20 * sc], 18 * sc, fill=(int(40 + 140 * glow), int(46 + 110 * glow), 56))
    # plate and bowl
    p.ell([(wx0 + wx1) / 2 - 150 * sc, wy1 - 70 * sc, (wx0 + wx1) / 2 + 150 * sc, wy1 - 30 * sc], fill=(120, 126, 136))
    p.rr([(wx0 + wx1) / 2 - 90 * sc, wy1 - 150 * sc, (wx0 + wx1) / 2 + 90 * sc, wy1 - 50 * sc], 30 * sc, fill=WHITE)
    for i in range(int((wx1 - wx0) / (26 * sc))):
        for j in range(int((wy1 - wy0) / (26 * sc))):
            p.circle(wx0 + 16 * sc + i * 26 * sc, wy0 + 16 * sc + j * 26 * sc, 3.2 * sc, fill=(20, 22, 28))
    if door_hl > 0:
        p.rr([wx0 - 8, wy0 - 8, wx1 + 8, wy1 + 8], 28 * sc, outline=YEL, width=8 * door_hl)
    # control panel
    px0 = x0 + w - 180 * sc
    p.rr([px0, y0 + 60 * sc, px0 + 130 * sc, y0 + 150 * sc], 14 * sc, fill=(30, 36, 46))
    p.text((px0 + 65 * sc, y0 + 105 * sc), "0:30", f2("dm", max(8, int(36 * sc))), GREEN)
    for k in range(3):
        p.circle(px0 + 65 * sc, y0 + 220 * sc + k * 80 * sc, 26 * sc, fill=(170, 176, 186))

def molecule(p, cx, cy, ang, r=30):
    p.circle(cx, cy, r, fill=(110, 170, 255))
    for da in (-52, 52):
        a = math.radians(ang + da)
        p.circle(cx + math.cos(a) * r * 1.05, cy + math.sin(a) * r * 1.05, r * 0.55, fill=WHITE)

@V.scene(0, 1)
def intro(p, t, L):
    k = eback(prog(t, 0.05, 0.55))
    oven(p, 540, 720, lerp(0.6, 1.0, k), glow=0.5 + 0.5 * pulse(t, 1.4), door_hl=prog(t, L(1)[0] + 1.4, L(1)[0] + 1.8))
    for i in range(3):
        a = prog(t, 0.8 + i * 0.3, 1.6 + i * 0.3)
        if a > 0:
            wave(p, 160, 920, 380 + i * 18, 14, 90, t * 6 + i, (255, 120, 90), width=5)
    a1, _ = L(1)
    pill(p, 540, 1080, "WHY ARE YOU SAFE?", prog(t, 1.0, 1.4) * (1 - prog(t, a1, a1 + 0.2)), bg=WHITE)
    pill(p, 540, 1080, "THE CLUE: THE DOOR", prog(t, a1 + 1.4, a1 + 1.8), bg=YEL)

@V.scene(2, 4)
def magnetron(p, t, L):
    a1, _ = L(2); a2, _ = L(3); a4, _ = L(4)
    # cavity
    p.rr([260, 430, 980, 1060], 30, fill=(40, 46, 56), outline=SLATE_L, width=8)
    # magnetron box
    p.rr([80, 600, 260, 880], 20, fill=SLATE_L)
    p.text((170, 740), "M", f2("anton", 90), WHITE)
    pill(p, 170, 560, "MAGNETRON", prog(t, a1 + 1.0, a1 + 1.4), bg=WHITE, size=32)
    if t > a1 + 1.6:
        for i, y in enumerate((660, 740, 820)):
            wave(p, 270, 970, y, 22, 120, t * 9 + i * 1.3, MW, width=7)
        pill(p, 640, 470, "2.45 GHz", prog(t, a1 + 3.5, a1 + 3.9), bg=MW, fg=INK)
    if t > a2 - 0.2:
        for i in range(5):
            cx = 380 + i * 130
            jig = math.sin(t * 22 + i) * 40 * prog(t, a2 + 0.3, a2 + 0.8)
            molecule(p, cx, 960, -90 + jig, r=30)
        h = prog(t, a2 + 2.4, a2 + 2.9)
        pill(p, 620, 1110, "HEAT", h * (1 - prog(t, a4 - 0.2, a4)), bg=ORANGE)
        pill(p, 620, 1110, "ONLY ~1-2 CM DEEP", prog(t, a4 + 0.6, a4 + 1.0), bg=WHITE)

BOUNCE = [(300, 520), (940, 700), (300, 880), (940, 1000), (500, 520), (940, 620), (300, 760), (700, 1010), (300, 520)]

@V.scene(5, 6)
def bouncing(p, t, L):
    a3, _ = L(5); a4, _ = L(6)
    p.rr([260, 470, 980, 1050], 30, fill=(40, 46, 56), outline=(150, 156, 166), width=14)
    p.line(BOUNCE, (90, 60, 60), 4)
    flow_dots(p, BOUNCE, t - a3, speed=0.25, n=14, r=11, fill=MW)
    pill(p, 620, 410, "METAL WALLS REFLECT", prog(t, a3 + 0.6, a3 + 1.0) * (1 - prog(t, a4 - 0.3, a4)))
    if t > a4:
        hl = pulse(t, 0.8)
        p.rect([248, 470, 272, 1050], fill=(255, int(180 + 60 * hl), 60))
        pill(p, 330, 410, "THE DOOR?", prog(t, a4 + 1.6, a4 + 2.0), bg=YEL)
        p.arrow((150, 760), (235, 760), YEL, width=12, head=36)

@V.scene(7)
def mesh(p, t, L):
    a, _ = L(7)
    k = eback(prog(t, a, a + 0.5))
    oven(p, 330, 640, 0.55, door_hl=prog(t, a + 0.4, a + 0.8))
    # magnifier
    mx, my, mr = 700, 760, 250 * k
    if mr > 1:
        p.line([(330, 640), (mx - mr * .7, my - mr * .7)], fill=(200, 205, 215), width=6)
        p.circle(mx, my, mr, fill=(150, 156, 166), outline=WHITE, width=10)
        step = 62 * k
        for i in range(-4, 5):
            for j in range(-4, 5):
                x, y = mx + i * step, my + j * step
                if (x - mx) ** 2 + (y - my) ** 2 < (mr - 30) ** 2:
                    p.circle(x, y, 20 * k, fill=(20, 22, 28))
    pill(p, 700, 1080, "HOLES ABOUT 1 MM", prog(t, a + 3.2, a + 3.6))

@V.scene(8, 9)
def too_big(p, t, L):
    a6, _ = L(8); a7, _ = L(9)
    # metal screen on the right (side view): bars with tiny gaps
    sx = 760
    for j in range(16):
        y = 430 + j * 40
        p.rect([sx, y, sx + 30, y + 30], fill=(170, 176, 186))
    # one long wave approaching from the left
    head = lerp(80, sx - 10, eio(prog(t, a6 + 0.2, a6 + 1.6)))
    back = prog(t, a7 + 1.6, a7 + 2.6)
    if back > 0:
        head = lerp(sx - 10, 300, eio(back))
    wave(p, 60, head, 760, 130, 240, 0, MW, width=12)
    # 12 cm ruler for one wavelength
    rp = prog(t, a6 + 1.6, a6 + 2.0)
    if rp > 0 and t < a7:
        p.line([(120, 960), (120 + 240 * eo(rp), 960)], WHITE, 6)
        p.line([(120, 940), (120, 980)], WHITE, 6); p.line([(120 + 240 * eo(rp), 940), (120 + 240 * eo(rp), 980)], WHITE, 6)
        pill(p, 240, 1040, "ONE WAVE = 12 CM", rp, bg=MW, fg=INK)
        pill(p, sx + 15, 380, "GAPS: 1 MM", prog(t, a6 + 3.0, a6 + 3.4), bg=WHITE)
    if t > a7:
        pill(p, 560, 1080, "LOOKS LIKE A SOLID WALL", prog(t, a7 + 0.6, a7 + 1.0) * (1 - prog(t, a7 + 2.4, a7 + 2.6)))
        if back > 0:
            p.arrow((620, 600), (380, 600), MW, width=14, head=44)
            pill(p, 560, 1080, "BOUNCES BACK IN", prog(t, a7 + 2.6, a7 + 3.0), bg=MW, fg=INK)

@V.scene(10, 11)
def light_through(p, t, L):
    a8, _ = L(10); a9, _ = L(11)
    sx = 520
    for j in range(16):
        y = 430 + j * 40
        p.rect([sx, y, sx + 30, y + 30], fill=(170, 176, 186))
    # tiny light waves passing through the gaps
    offs = [0, 420, 160, 680, 300, 860, 540]
    for i, y in enumerate((465, 545, 625, 705, 785, 865, 945)):
        x = (((t - a8) * 420 + offs[i]) % 1300) - 260
        if x + 220 > 80 and x < 980:
            wave(p, max(60, x), min(1000, x + 220), y, 5, 18, t * 20, LIGHT, width=5)
    pill(p, 270, 380, "LIGHT: TINY WAVES", prog(t, a8 + 0.4, a8 + 0.8) * (1 - prog(t, a9 - 0.3, a9)))
    if t > a9:
        # eye on the right
        k = eback(prog(t, a9, a9 + 0.5))
        p.ell([820 - 120 * k, 690 - 70 * k, 820 + 120 * k, 690 + 70 * k], fill=WHITE)
        p.circle(820, 690, 50 * k, fill=(60, 120, 200)); p.circle(820, 690, 22 * k, fill=INK)
        tick(p, 820, 900, 56, prog(t, a9 + 1.0, a9 + 1.4))
        pill(p, 270, 380, "MICROWAVES STAY IN", prog(t, a9 + 2.0, a9 + 2.4), bg=MW, fg=INK)

@V.scene(12)
def outro(p, t, L):
    a, _ = L(12)
    sx = 525
    for j in range(16):
        y = 430 + j * 40
        p.rect([sx, y, sx + 30, y + 30], fill=(170, 176, 186))
    if t > a + 1.2:
        wave(p, 600, 990, 560, 8, 22, t * 20, LIGHT, width=6)
        wave(p, 80, 500, 560, 8, 22, t * 20, LIGHT, width=6)
        pill(p, 300, 470, "WINDOW FOR LIGHT", prog(t, a + 1.4, a + 1.8))
    if t > a + 3.0:
        wave(p, 80, 505, 860, 60, 200, t * 5, MW, width=10)
        cross(p, 760, 860, 60, prog(t, a + 3.4, a + 3.6), shake_t=t - (a + 3.4))
        pill(p, 300, 1000, "WALL FOR MICROWAVES", prog(t, a + 3.2, a + 3.6), bg=MW, fg=INK)
    fp = prog(t, a + 5.6, a + 6.0)
    if fp > 0:
        r = 60 * eback(fp)
        p.circle(780, 1060, r, fill=RED)
        p.line([(780 - r * .45, 1060), (780 + r * .45, 1060)], fill=WHITE, width=12)
        p.line([(780, 1060 - r * .45), (780, 1060 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
