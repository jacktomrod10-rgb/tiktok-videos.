import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "noise-cancelling", episode=4,
    lines=[
        "Noise-cancelling headphones fight sound with more sound.",
        "Sound is a wave of air pressure, pushing and pulling, hundreds of times a second.",
        "Tiny microphones on the outside of the headphones listen to the noise around you.",
        "A chip then creates the exact opposite wave. Where the noise pushes, the anti-noise pulls.",
        "Play them together, and the peaks fill in the dips. The waves cancel out, and the noise fades away.",
        "And it has to happen almost instantly, because if the timing slips, the waves stop lining up.",
        "That's why it's brilliant on the deep, steady hum of a plane engine. A long, slow, predictable wave.",
        "But sudden high-pitched sounds, like voices or clattering plates, are much harder to catch. So the ear cushions block those instead.",
        "Many headphones also hide a microphone inside the ear cup, checking what's left and correcting it.",
        "The idea was patented in the nineteen thirties, but electronics took decades to catch up.",
        "Silence, made by adding sound. Follow for more everyday genius.",
    ],
    display=[
        "Noise-cancelling headphones fight *sound* with more *sound*.",
        "Sound is a wave of *air pressure*, pushing and pulling, *hundreds* of times a second.",
        "Tiny *microphones* on the outside of the headphones *listen* to the noise around you.",
        "A chip then creates the exact *opposite* wave. Where the noise *pushes*, the anti-noise *pulls*.",
        "Play them together, and the peaks fill in the dips. The waves *cancel* out, and the noise *fades* away.",
        "And it has to happen almost *instantly*, because if the timing slips, the waves stop lining up.",
        "That's why it's brilliant on the deep, steady *hum* of a plane engine. A long, slow, *predictable* wave.",
        "But sudden *high-pitched* sounds, like voices or clattering plates, are much harder to catch. So the ear *cushions* block those instead.",
        "Many headphones also hide a microphone *inside* the ear cup, checking what's *left* and correcting it.",
        "The idea was patented in the *1930s*, but electronics took *decades* to catch up.",
        "*Silence*, made by adding *sound*. Follow for more everyday *genius*.",
    ],
)

NOISE, ANTI = ORANGE, BLUE

def wave(p, x0, x1, y, amp, wl, phase, fill, width=8, jag=False):
    pts = []
    n = max(2, int((x1 - x0) / 5))
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        v = math.sin(2 * math.pi * (x - x0) / wl - phase)
        if jag:
            v = 0.6 * v + 0.4 * math.sin(2 * math.pi * (x - x0) / (wl * 0.37) - phase * 2.3)
        pts.append((x, y + amp * v))
    p.line(pts, fill, width)

def headphones(p, cx, cy, sc=1.0):
    p.arc([cx - 260 * sc, cy - 300 * sc, cx + 260 * sc, cy + 220 * sc], 180, 360, (70, 80, 96), 44 * sc)
    for sx in (-1, 1):
        x = cx + sx * 250 * sc
        p.rr([x - 70 * sc, cy - 40 * sc, x + 70 * sc, cy + 180 * sc], 60 * sc, fill=(52, 60, 74))
        p.rr([x - 50 * sc, cy - 20 * sc, x + 50 * sc, cy + 160 * sc], 44 * sc, fill=(88, 98, 116))

@V.scene(0)
def intro(p, t, L):
    k = eback(prog(t, 0.05, 0.55))
    headphones(p, 540, 700, lerp(0.6, 1.0, k))
    f = 1 - prog(t, 1.6, 2.6)
    if t > 0.5:
        wave(p, 70, 220, 760, 40 * f + 2, 60, t * 8, NOISE, 7)
        wave(p, 860, 1010, 760, 40 * f + 2, 60, t * 8, NOISE, 7)
    if t > 2.6:
        for sx, sy in [(-1, -1), (1, -1)]:
            sparkle(p, 540 + sx * 330, 520, 26 * eback(prog(t, 2.6, 3.0)))

@V.scene(1)
def pressure(p, t, L):
    a, _ = L(1)
    wave(p, 80, 1000, 600, 90, 300, (t - a) * 6, NOISE, 10)
    # air particles bunching and spreading
    for i in range(46):
        x0 = 80 + i * 20
        x = x0 + 14 * math.sin(2 * math.pi * x0 / 300 - (t - a) * 6)
        for j in range(4):
            p.circle(x, 830 + j * 44, 7, fill=(150, 180, 220))
    pill(p, 540, 420, "PUSH", prog(t, a + 1.4, a + 1.7) * (1 - prog(t, a + 2.6, a + 2.8)), bg=NOISE, fg=INK)
    pill(p, 540, 420, "PULL", prog(t, a + 2.8, a + 3.1), bg=WHITE)
    pill(p, 540, 1080, "AIR PRESSURE WAVE", prog(t, a + 0.6, a + 1.0))

@V.scene(2, 3)
def mic_and_chip(p, t, L):
    a2, _ = L(2); a3, _ = L(3)
    # one ear cup, big
    p.rr([560, 460, 820, 1000], 110, fill=(52, 60, 74))
    p.rr([600, 500, 780, 960], 90, fill=(88, 98, 116))
    mic = prog(t, a2 + 0.6, a2 + 1.0)
    if mic > 0:
        p.circle(560, 600, 22 * eback(mic), fill=YEL)
        pill(p, 400, 520, "MICROPHONE", prog(t, a2 + 0.9, a2 + 1.3), bg=YEL)
    wave(p, 80, 540, 600, 60, 200, (t - a2) * 6, NOISE, 8)
    if t > a3:
        p.rr([640, 680, 740, 780], 16, fill=INK)
        p.text((690, 730), "CHIP", f2("dm", 26), WHITE)
        k = prog(t, a3 + 0.8, a3 + 1.6)
        wave(p, 80, 80 + 460 * k, 860, 60, 200, (t - a2) * 6 + math.pi, ANTI, 8)
        pill(p, 300, 990, "ANTI-NOISE", prog(t, a3 + 1.4, a3 + 1.8), bg=ANTI, fg=INK)

@V.scene(4, 5)
def cancel(p, t, L):
    a4, _ = L(4); a5, _ = L(5)
    ph = (t - a4) * 6
    slip = 0.0
    if t > a5:
        slip = 1.2 * math.sin(prog(t, a5 + 1.5, a5 + 4.5) * math.pi)
    wave(p, 100, 980, 470, 60, 220, ph, NOISE, 7)
    wave(p, 100, 980, 640, 60, 220, ph + math.pi + slip, ANTI, 7)
    p.text((60, 470), "+", f2("anton", 60), WHITE)
    p.line([(100, 750), (980, 750)], (90, 100, 120), 4)
    # sum
    k = eo(prog(t, a4 + 1.0, a4 + 3.0))
    pts = []
    for i in range(177):
        x = 100 + i * 5
        v = math.sin(2 * math.pi * (x - 100) / 220 - ph) + math.sin(2 * math.pi * (x - 100) / 220 - ph - math.pi - slip)
        pts.append((x, 900 + 60 * v * (1 - k) + 60 * v * k * 0))
    if t > a4 + 1.0:
        sumamp = (1 - k) if t < a5 else 1.0
        pts = [(x, 900 + (y - 900) * (sumamp if t < a5 else 1.0)) for x, y in pts]
        p.line(pts, WHITE, 8)
    if t < a5:
        pill(p, 540, 1060, "CANCELLED", prog(t, a4 + 3.0, a4 + 3.4), bg=GREEN)
    else:
        pill(p, 540, 1060, "TIMING IS EVERYTHING", prog(t, a5 + 0.4, a5 + 0.8), bg=YEL)

@V.scene(6, 7)
def low_vs_high(p, t, L):
    a6, _ = L(6); a7, _ = L(7)
    ph = t * 4
    # low hum: long wave, cancelled
    wave(p, 100, 980, 520, 70 * (1 - 0.85 * prog(t, a6 + 2.0, a6 + 3.0)), 420, ph, NOISE, 9)
    pill(p, 300, 410, "ENGINE HUM", prog(t, a6 + 0.6, a6 + 1.0), bg=NOISE, fg=INK)
    tick(p, 860, 410, 40, prog(t, a6 + 3.0, a6 + 3.3))
    if t > a7:
        wave(p, 100, 980, 820, 60, 70, ph * 3, (255, 160, 200), 6, jag=True)
        pill(p, 300, 710, "VOICES, CLATTER", prog(t, a7 + 0.6, a7 + 1.0), bg=(255, 160, 200), fg=INK)
        cross(p, 860, 710, 40, prog(t, a7 + 2.4, a7 + 2.6), shake_t=t - (a7 + 2.4))
        cush = eback(prog(t, a7 + 4.6, a7 + 5.2))
        if cush > 0:
            p.rr([500 - 60 * cush, 940, 580 + 60 * cush, 1120], 40, fill=(70, 80, 96))
            pill(p, 540, 1030, "CUSHIONS BLOCK THESE", prog(t, a7 + 5.0, a7 + 5.4))

@V.scene(8)
def inner_mic(p, t, L):
    a, _ = L(8)
    p.rr([320, 440, 760, 1080], 160, fill=(52, 60, 74))
    p.rr([370, 490, 710, 1030], 130, fill=(88, 98, 116))
    p.circle(540, 760, 80, fill=(40, 46, 56))  # driver
    m = prog(t, a + 0.8, a + 1.2)
    if m > 0:
        p.circle(640, 880, 22 * eback(m), fill=YEL)
        pill(p, 540, 400, "INSIDE MIC", prog(t, a + 1.0, a + 1.4) * (1 - prog(t, a + 2.3, a + 2.5)), bg=YEL)
    if t > a + 2.0:
        ang = (t - a) * 3
        for i in range(3):
            aa = ang + i * 2.1
            p.circle(540 + 140 * math.cos(aa), 760 + 140 * math.sin(aa), 12, fill=GREEN)
        pill(p, 540, 400, "CHECK AND CORRECT", prog(t, a + 2.6, a + 3.0), bg=GREEN)

@V.scene(9, 10)
def outro(p, t, L):
    a9, _ = L(9); a10, _ = L(10)
    if t < a10:
        pop = eback(prog(t, a9, a9 + 0.4))
        if pop > 0:
            p.text((540, 620), "1930s", f2("anton", max(10, int(240 * pop))), YEL)
        pill(p, 540, 860, "FIRST PATENTED", prog(t, a9 + 0.4, a9 + 0.8), bg=WHITE)
        pill(p, 540, 960, "ELECTRONICS CAUGHT UP LATER", prog(t, a9 + 2.6, a9 + 3.0))
    else:
        k = eback(prog(t, a10, a10 + 0.5))
        headphones(p, 540, 660, 0.85 * k if k > 0 else 0.01)
        p.line([(120, 980), (960, 980)], WHITE, 6)
        fp = prog(t, a10 + 2.2, a10 + 2.6)
        if fp > 0:
            r = 58 * eback(fp)
            p.circle(540, 1090, r, fill=RED)
            p.line([(540 - r * .45, 1090), (540 + r * .45, 1090)], fill=WHITE, width=12)
            p.line([(540, 1090 - r * .45), (540, 1090 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
