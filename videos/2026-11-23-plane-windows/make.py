import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "plane-windows", episode=3,
    lines=[
        "There's a reason aeroplane windows are never square.",
        "Up at cruising height, the air outside is too thin to breathe, so the cabin is pumped full of air, like a balloon.",
        "Every flight, the body of the plane stretches as it's pressurised, then relaxes again when you land.",
        "And all that stress has to flow through the metal skin, around every single opening.",
        "A smooth curve lets it flow around evenly. But a sharp corner squeezes it into one tiny spot.",
        "Thousands of flights later, tiny cracks can start right there. Engineers call it metal fatigue.",
        "The world learned this the hard way in nineteen fifty-four, when two de Havilland Comet jets broke apart in mid-air.",
        "Investigators sank a whole Comet in a giant water tank, and pressurised it over and over, like flight after flight.",
        "After about three thousand cycles, it split open, starting near the corner of an opening in the cabin.",
        "Later Comets got rounder, oval windows, and aircraft since have been designed with fatigue in mind.",
        "So that curve next to your seat isn't just style. Follow for more everyday genius.",
    ],
    display=[
        "There's a reason aeroplane windows are never *square*.",
        "Up at cruising height, the air outside is too *thin* to breathe, so the cabin is pumped full of air, like a *balloon*.",
        "Every flight, the body of the plane *stretches* as it's pressurised, then *relaxes* again when you land.",
        "And all that *stress* has to flow through the metal skin, around every single *opening*.",
        "A smooth *curve* lets it flow around evenly. But a sharp *corner* squeezes it into one tiny spot.",
        "Thousands of flights later, tiny *cracks* can start right there. Engineers call it *metal fatigue*.",
        "The world learned this the hard way in *1954*, when two de Havilland *Comet* jets broke apart in mid-air.",
        "Investigators sank a whole Comet in a giant *water tank*, and pressurised it over and over, like flight after flight.",
        "After about *3,000* cycles, it split open, starting near the *corner* of an opening in the cabin.",
        "Later Comets got rounder, *oval* windows, and aircraft since have been designed with *fatigue* in mind.",
        "So that curve next to your seat isn't just *style*. Follow for more everyday *genius*.",
    ],
)

SKY1, SKY2 = (120, 180, 240), (190, 225, 250)
HULL = (226, 230, 236)

def window(p, cx, cy, w, h, r, t, frame=HULL):
    p.rr([cx - w / 2 - 22, cy - h / 2 - 22, cx + w / 2 + 22, cy + h / 2 + 22], r + 22, fill=frame)
    p.rr([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], r, fill=SKY1)
    # drifting cloud
    x = cx - w / 2 + ((t * 60) % (w + 160)) - 80
    if cx - w / 2 < x < cx + w / 2 - 40:
        p.ell([x, cy + h * .05, min(cx + w / 2 - 4, x + 90), cy + h * .22], fill=WHITE)

def fuselage(p, cx, cy, length, radius, sc=1.0):
    r = radius * sc
    p.rr([cx - length / 2, cy - r, cx + length / 2, cy + r], r, fill=HULL)
    for i in range(7):
        x = cx - length / 2 + r + 30 + i * ((length - 2 * r - 60) / 6)
        p.rr([x - 14, cy - r * .35, x + 14, cy - r * .05], 12, fill=(80, 120, 170))

def flow(p, cx, cy, shape, t, hot):
    """Stress lines flowing around a hole (shape: 'square' or 'round')."""
    for k in range(-5, 6):
        y0 = cy + k * 34
        pts = []
        for i in range(41):
            x = cx - 220 + i * 11
            dx = (x - cx) / 120
            bend = 0
            if abs(k) <= 3:
                push = (100 - abs(k) * 26)
                bend = math.copysign(1, k if k != 0 else 1) * push * math.exp(-dx * dx * (6 if shape == "square" else 1.6))
            pts.append((x, y0 + bend))
        p.line(pts, (90, 140, 200), 4)
    if shape == "square":
        p.rect([cx - 70, cy - 70, cx + 70, cy + 70], fill=BG2)
        p.rect([cx - 70, cy - 70, cx + 70, cy + 70], outline=WHITE, width=5)
        if hot > 0:
            for sx in (-1, 1):
                for sy in (-1, 1):
                    rr = 26 + 10 * pulse(t, 0.7)
                    p.circle(cx + sx * 70, cy + sy * 70, rr * hot, fill=RED)
    else:
        p.ell([cx - 80, cy - 70, cx + 80, cy + 70], fill=BG2, outline=WHITE, width=5)
        if hot > 0:
            p.ell([cx - 92, cy - 82, cx + 92, cy + 82], outline=YEL, width=8 * hot)

@V.scene(0)
def intro(p, t, L):
    a = eback(prog(t, 0.05, 0.5)); b = eback(prog(t, 0.5, 0.95))
    if a > 0:
        window(p, 300, 700, 260 * a, 260 * a, 6, t)
        cross(p, 300, 960, 54, prog(t, 1.4, 1.6), shake_t=t - 1.4)
    if b > 0:
        window(p, 780, 700, 230 * b, 330 * b, 110 * b, t)
        tick(p, 780, 960, 54, prog(t, 1.9, 2.2))

@V.scene(1, 2)
def pressure(p, t, L):
    a1, _ = L(1); a2, _ = L(2)
    breathe = 0.0
    if t > a2:
        breathe = 0.5 + 0.5 * math.sin((t - a2) * 2.4)
    sc = 1.0 + 0.12 * breathe
    fuselage(p, 540, 740, 820, 150, sc)
    if t > a1 + 3.0:
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            r0 = 190 * sc
            p.arrow((540 + math.cos(a) * r0 * 2.2, 740 + math.sin(a) * r0 * 0.9),
                    (540 + math.cos(a) * (r0 * 2.2 + 50), 740 + math.sin(a) * (r0 * 0.9 + 30)), ORANGE, width=8, head=22)
    pill(p, 540, 430, "AIR TOO THIN OUTSIDE", prog(t, a1 + 1.0, a1 + 1.4) * (1 - prog(t, a1 + 3.6, a1 + 3.9)), bg=WHITE)
    pill(p, 540, 430, "CABIN PUMPED UP", prog(t, a1 + 4.0, a1 + 4.4) * (1 - prog(t, a2 - 0.3, a2)), bg=ORANGE)
    pill(p, 540, 430, "STRETCH, RELAX, REPEAT", prog(t, a2 + 0.8, a2 + 1.2))

@V.scene(3, 4)
def stress_flow(p, t, L):
    a3, _ = L(3); a4, _ = L(4)
    if t < a4:
        flow(p, 540, 740, "round", t, 0)
        pill(p, 540, 470, "STRESS FLOWS AROUND OPENINGS", prog(t, a3 + 0.8, a3 + 1.2), bg=WHITE)
    else:
        flow(p, 300, 740, "round", t, prog(t, a4 + 0.6, a4 + 1.0))
        flow(p, 780, 740, "square", t, prog(t, a4 + 2.6, a4 + 3.0))
        pill(p, 300, 470, "EVEN", prog(t, a4 + 0.6, a4 + 1.0), bg=YEL)
        pill(p, 780, 470, "HOT SPOTS", prog(t, a4 + 2.6, a4 + 3.0), bg=RED, fg=WHITE)

@V.scene(5)
def fatigue(p, t, L):
    a, _ = L(5)
    # big corner close-up
    p.rect([120, 380, 980, 1120], fill=HULL)
    p.rect([540, 380, 980, 800], fill=BG2)
    flights = int(lerp(0, 5000, eo(prog(t, a + 0.2, a + 3.6))))
    p.text((760, 590), f"{flights:,}", f2("anton", 110), YEL)
    p.text((760, 690), "FLIGHTS", f2("dm", 36), MUTED)
    g = prog(t, a + 1.0, a + 4.0)
    if g > 0:
        pts = [(540, 800)]
        for i in range(1, int(10 * g) + 1):
            pts.append((540 - i * 26, 800 + i * 22 + (12 if i % 2 else -12)))
        p.line(pts, RED, 7)
    pill(p, 330, 1060, "METAL FATIGUE", prog(t, a + 3.6, a + 4.0), bg=RED, fg=WHITE)

def jet(p, cx, cy, sc=1.0):
    L_ = 640 * sc
    p.rr([cx - L_ / 2, cy - 40 * sc, cx + L_ / 2, cy + 40 * sc], 40 * sc, fill=HULL)
    p.poly([(cx - L_ / 2 + 40 * sc, cy - 30 * sc), (cx - L_ / 2 - 10 * sc, cy - 150 * sc), (cx - L_ / 2 + 70 * sc, cy - 150 * sc), (cx - L_ / 2 + 140 * sc, cy - 30 * sc)], HULL)
    p.poly([(cx - 40 * sc, cy + 10 * sc), (cx - 150 * sc, cy + 170 * sc), (cx - 40 * sc, cy + 170 * sc), (cx + 90 * sc, cy + 10 * sc)], (200, 206, 214))
    for i in range(9):
        p.circle(cx - L_ / 2 + 150 * sc + i * 45 * sc, cy - 8 * sc, 9 * sc, fill=(80, 120, 170))

@V.scene(6)
def comet(p, t, L):
    a, _ = L(6)
    big_number(p, t, a, 1954, cy=560, size=260, start=1940, dur=1.0)
    k = eo(prog(t, a + 0.4, a + 1.4))
    if k > 0:
        jet(p, lerp(-200, 540, k), 900, 0.9)
    pill(p, 540, 1110, "DE HAVILLAND COMET", prog(t, a + 3.0, a + 3.4), bg=WHITE)

@V.scene(7, 8)
def tank(p, t, L):
    a7, _ = L(7); a8, _ = L(8)
    p.rr([90, 520, 990, 1100], 20, fill=(40, 90, 150))
    for i in range(6):
        y = 560 + i * 20 + 6 * math.sin(t * 2 + i)
        p.line([(110, y), (970, y)], (70, 130, 190), 3)
    fuselage(p, 540, 840, 760, 120, 1.0 + 0.05 * math.sin(t * 5))
    # opening (hatch) with crack later
    p.rr([600, 760, 680, 860], 12, fill=(70, 80, 96))
    cycles = int(lerp(0, 3057, eo(prog(t, a7 + 1.4, a8 + 1.2))))
    p.text((540, 390), f"{cycles:,}", f2("anton", 120), YEL)
    p.text((540, 470), "PRESSURE CYCLES", f2("dm", 32), MUTED)
    if t > a8 + 1.3:
        g = prog(t, a8 + 1.3, a8 + 2.3)
        pts = [(600, 760)]
        for i in range(1, int(9 * g) + 1):
            pts.append((600 - i * 28, 760 - i * 4 + (14 if i % 2 else -14)))
        p.line(pts, RED, 9)
        flash = prog(t, a8 + 1.3, a8 + 1.4) * (1 - prog(t, a8 + 1.5, a8 + 1.9))
        if flash > 0: p.circle(600, 760, 120 * flash, fill=(255, 240, 220))
        pill(p, 540, 1040, "CRACK AT AN OPENING'S CORNER", prog(t, a8 + 2.2, a8 + 2.6), bg=RED, fg=WHITE)

@V.scene(9, 10)
def outro(p, t, L):
    a9, _ = L(9); a10, _ = L(10)
    p.rect([60, 560, 1020, 900], fill=HULL)
    for i in range(3):
        k = eback(prog(t, a9 + i * 0.25, a9 + 0.5 + i * 0.25))
        if k > 0:
            window(p, 230 + i * 310, 730, 150 * k, 220 * k, 72 * k, t + i, frame=(200, 206, 214))
    tick(p, 540, 1000, 56, prog(t, a9 + 2.0, a9 + 2.4) * (1 - prog(t, a10, a10 + 0.3)))
    pill(p, 540, 470, "DESIGNED FOR FATIGUE", prog(t, a9 + 3.0, a9 + 3.4))
    fp = prog(t, a10 + 2.4, a10 + 2.8)
    if fp > 0:
        r = 60 * eback(fp)
        p.circle(540, 1000, r, fill=RED)
        p.line([(540 - r * .45, 1000), (540 + r * .45, 1000)], fill=WHITE, width=12)
        p.line([(540, 1000 - r * .45), (540, 1000 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
