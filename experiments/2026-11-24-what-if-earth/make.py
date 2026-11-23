"""Test format: 'What if' scenario. What if you jumped into a hole through the Earth? Sources in sources.md."""
import os, sys, math
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *

V = Video(
    "test-what-if-earth", episode=None, title="What if you fell *through* the Earth?", music="pad",
    lines=[
        "What if you jumped into a hole through the Earth?",
        "You'd pop out the other side in just thirty-eight minutes.",
        "And it gets weird. As you fall, gravity actually gets stronger at first, because Earth's core is so dense.",
        "By the middle, you're doing over eight kilometres a second.",
        "Right at the centre, gravity is zero. You'd be completely weightless.",
        "Then gravity flips, and starts pulling you back, slowing you down the whole way up.",
        "You'd reach the other side at a dead stop. So grab the edge!",
        "Miss it, and you fall all the way back. Back and forth, like a pendulum.",
        "Oh, and the core is about six thousand degrees Celsius.",
        "As hot as the surface of the Sun.",
        "Would you jump? Tell me in the comments. Follow for more everyday genius.",
    ],
    display=[
        "What if you *jumped* into a hole through the *Earth*?",
        "You'd pop out the other side in just *38 minutes*.",
        "And it gets *weird*. As you fall, gravity actually gets *stronger* at first, because Earth's core is so *dense*.",
        "By the middle, you're doing over *8 km* a *second*.",
        "Right at the centre, gravity is *zero*. You'd be completely *weightless*.",
        "Then gravity *flips*, and starts pulling you *back*, slowing you down the whole way up.",
        "You'd reach the other side at a *dead stop*. So *grab* the edge!",
        "Miss it, and you fall all the way *back*. Back and forth, like a *pendulum*.",
        "Oh, and the core is about *6,000 degrees* Celsius.",
        "As hot as the surface of the *Sun*.",
        "Would *you* jump? Tell me in the *comments*. Follow for more everyday *genius*.",
    ],
)

EX, EY, ER = 420, 800, 325          # Earth centre and radius
CRUST, MANTLE, OUTER, INNER = (90, 150, 90), (200, 80, 50), (240, 150, 50), (255, 226, 120)
SPACE = (10, 14, 30)

def lerpc(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

def space(p, t):
    p.rect([0, 300, 1080, 1170], fill=SPACE)
    for i in range(70):
        x = (i * 157) % 1080
        y = 310 + (i * 211) % 850
        tw = 0.5 + 0.5 * math.sin(t * 2 + i)
        r = 1.6 + 1.4 * tw * (i % 3 == 0)
        p.circle(x, y, r, fill=(200, 210, 255))

def earth(p, t, glow=0.0, cutaway=True, cx=EX, cy=EY, r=ER):
    for i in range(6):                                      # atmosphere halo
        p.circle(cx, cy, r + 34 - i * 5, fill=lerpc(SPACE, (70, 140, 230), 0.12 + i * 0.07))
    p.circle(cx, cy, r + 6, fill=(40, 110, 200))           # ocean rim
    p.circle(cx, cy, r, fill=CRUST)
    for i in range(10):                                     # mantle: hotter towards the core
        rr = r * (0.94 - i * 0.045)
        p.circle(cx, cy, rr, fill=lerpc((170, 70, 45), MANTLE, i / 9))
    for i in range(6):
        rr = r * (0.53 - i * 0.03)
        p.circle(cx, cy, rr, fill=lerpc((230, 120, 40), OUTER, i / 5))
    pul = 0.5 + 0.5 * math.sin(t * 3)
    for i in range(5):
        rr = r * (0.33 - i * 0.05) + glow * 6 * pul
        p.circle(cx, cy, rr, fill=lerpc((255, 200, 90), (255, 248, 210), i / 4))
    # the tunnel
    p.rect([cx - 15, cy - r - 8, cx + 15, cy + r + 8], fill=(22, 26, 40))
    p.rect([cx - 15, cy - r - 8, cx - 9, cy + r + 8], fill=(46, 52, 72))
    # tiny houses on the surface at both ends
    for sy in (-1, 1):
        y = cy + sy * (r + 6)
        p.rr([cx - 70, y - (24 if sy < 0 else -2), cx - 30, y + (2 if sy < 0 else 24)], 4, fill=(230, 220, 200))
        p.rr([cx + 30, y - (24 if sy < 0 else -2), cx + 70, y + (2 if sy < 0 else 24)], 4, fill=(200, 220, 240))

def faller(p, x, y, s=1.0, ang=0.0, arms=1.0, t=0.0):
    """Cartoon jumper: orange suit, helmet, arms up. ang rotates the whole figure."""
    ca, sa = math.cos(ang), math.sin(ang)
    def r(dx, dy): return (x + (dx * ca - dy * sa) * s, y + (dx * sa + dy * ca) * s)
    for sx in (-1, 1):                                      # legs
        p.line([r(sx * 10, 18), r(sx * 16, 52)], (40, 50, 70), 12 * s)
        p.line([r(sx * 10, 18), r(sx * 16, 52)], (255, 140, 40), 8 * s)
    for sx in (-1, 1):                                      # arms (up when falling)
        p.line([r(sx * 14, -14), r(sx * (26 + 8 * arms), -14 - 30 * arms)], (40, 50, 70), 11 * s)
        p.line([r(sx * 14, -14), r(sx * (26 + 8 * arms), -14 - 30 * arms)], (255, 140, 40), 7 * s)
    c = r(0, 2)
    p.ell([c[0] - 19 * s, c[1] - 26 * s, c[0] + 19 * s, c[1] + 22 * s], fill=(40, 50, 70))
    p.ell([c[0] - 16 * s, c[1] - 23 * s, c[0] + 16 * s, c[1] + 19 * s], fill=(255, 140, 40))
    h = r(0, -40)
    p.circle(h[0], h[1], 20 * s, fill=(40, 50, 70))
    p.circle(h[0], h[1], 17 * s, fill=WHITE)
    p.circle(h[0] + 4 * s * ca, h[1] + 4 * s * sa, 10 * s, fill=(90, 170, 240))
    p.circle(h[0] + 1 * s, h[1] - 3 * s, 3.5 * s, fill=WHITE)

def pos(phase):
    """phase 0 = top surface, pi = bottom surface (simple harmonic motion)."""
    return EX, EY - (ER + 4) * math.cos(phase)

def meter(p, x, y, label, frac, txt, col, k=1.0):
    if k <= 0: return
    p.rr([x - 90, y - 230, x + 90, y + 130], 30, fill=(20, 30, 50))
    p.text((x, y - 195), label, f2("dm", 28), MUTED)
    p.rr([x - 26, y - 160, x + 26, y + 60], 26, fill=(44, 56, 80))
    h = 220 * clamp(frac) * k
    if h > 4:
        p.rr([x - 26, y + 60 - h, x + 26, y + 60], 26, fill=col)
    p.text((x, y + 100), txt, f2("anton", 46), col)

def gravity_arrows(p, x, y, k, direction, t):
    if k <= 0: return
    for i in range(3):
        yy = y + direction * (20 + i * 46 + 10 * pulse(t + i * 0.2, 0.8))
        p.arrow((x - 70, yy - direction * 30), (x - 70, yy), (120, 200, 255), width=6 + 4 * k, head=18 + 8 * k)

@V.sounds
def sounds(L):
    return [(0.9, "whoosh"), (L(1)[0] + 0.2, "whoosh"), (L(1)[1] - 0.4, "pop"), (L(3)[0] + 0.3, "whoosh"),
            (L(4)[0] + 0.2, "ding"), (L(5)[0] + 0.3, "boing"), (L(6)[1] - 0.8, "thud"), (L(7)[0] + 0.4, "whoosh"),
            (L(8)[0] + 0.6, "thud"), (L(9)[0] + 0.1, "ding"), (L(10)[0] + 0.2, "pop")]

@V.scene(0)
def hook(p, t, L):
    a, e = L(0)
    space(p, t)
    z = 1.0
    earth(p, t)
    jump = prog(t, e - 0.6, e + 0.2)
    if jump <= 0:
        faller(p, EX, EY - ER - 60, 1.3, arms=0.2 + 0.2 * math.sin(t * 6), t=t)
    else:
        faller(p, EX, EY - ER - 60 + 90 * eio(jump), 1.3 * (1 - 0.3 * jump), arms=1, t=t)
    pill(p, 850, 470, "12,742 KM", prog(t, 0.6, 0.9), bg=WHITE, size=36)
    p.arrow((850, 520), (850, 1040), (200, 210, 230), width=5, head=20) if t > 0.8 else None
    pill(p, 850, 1110, "NO AIR · NO HEAT", prog(t, 1.4, 1.7), bg=(44, 56, 80), fg=WHITE, size=26)

@V.scene(1)
def whole_trip(p, t, L):
    a, e = L(1)
    space(p, t)
    earth(p, t)
    k = eio(prog(t, a, e - 0.3))
    x, y = pos(math.pi * k)
    for j in range(6):                                       # speed streaks
        if 0.05 < k < 0.95:
            p.line([(x - 22 + j * 9, y - 40 - j * 10), (x - 22 + j * 9, y - 90 - j * 14)], (255, 220, 150), 3)
    faller(p, x, y, 1.0, ang=math.pi * min(1, k * 1.0) if k > 0.5 else 0, arms=1, t=t)
    total = 38 * 60 + 11
    secs = int(total * clamp(prog(t, a, e - 0.3)))
    p.rr([780, 440, 1010, 600], 30, fill=(20, 30, 50))
    p.text((895, 500), f"{secs // 60:02d}:{secs % 60:02d}", f2("anton", 84), YEL)
    p.text((895, 568), "MINUTES", f2("dm", 26), MUTED)
    if k >= 0.99:
        sparkle(p, x + 70, y + 30, 34 * eback(prog(t, e - 0.35, e)))

@V.scene(2)
def stronger(p, t, L):
    a, e = L(2)
    space(p, t)
    earth(p, t)
    k = eio(prog(t, a + 0.4, e))
    x, y = pos(0.38 * math.pi * k)
    faller(p, x, y, 1.0, arms=1, t=t)
    g = 1.0 + 0.10 * clamp(k * 1.6)
    gravity_arrows(p, x, y, k, 1, t)
    meter(p, 905, 790, "GRAVITY", g / 1.15, f"{int(round(g * 100))}%", (120, 200, 255), eback(prog(t, a + 0.6, a + 1.0)))
    pill(p, 905, 440, "DENSE CORE", prog(t, e - 1.6, e - 1.2), bg=ORANGE, size=30)

@V.scene(3)
def fastest(p, t, L):
    a, e = L(3)
    space(p, t)
    earth(p, t)
    k = eio(prog(t, a, e - 0.2))
    x, y = pos((0.38 + 0.12 * k) * math.pi)
    for j in range(8):
        p.line([(x - 30 + j * 9, y - 46 - j * 6), (x - 30 + j * 9, y - 150 - j * 12)], (255, 220, 150), 3)
    faller(p, x, y, 1.0, arms=1, t=t)
    v = 8.0 * eo(prog(t, a + 0.2, e - 0.2))
    meter(p, 905, 790, "SPEED", v / 8.6, f"{v:.1f}", RED, eback(prog(t, a, a + 0.4)))
    pill(p, 905, 985, "KM / SECOND", prog(t, a + 0.3, a + 0.6), bg=WHITE, size=26)
    pill(p, 905, 440, "28,800 KM/H", prog(t, e - 1.0, e - 0.7), bg=YEL, size=30)

@V.scene(4)
def weightless(p, t, L):
    a, e = L(4)
    space(p, t)
    earth(p, t, glow=1.0)
    x, y = pos(0.5 * math.pi)
    faller(p, x + 6 * math.sin(t * 2), y - 6 * math.cos(t * 2.3), 1.25, ang=(t - a) * 2.2, arms=1, t=t)
    for i in range(4):
        q = t * 1.5 + i * 1.57
        sparkle(p, x + 80 * math.cos(q), y + 80 * math.sin(q), 14, fill=WHITE)
    meter(p, 905, 790, "GRAVITY", 0.0, "0%", (120, 200, 255), 1.0)
    pill(p, 905, 440, "WEIGHTLESS", prog(t, e - 1.6, e - 1.3), bg=WHITE, size=30)

@V.scene(5, 6)
def slowing(p, t, L):
    a5, e5 = L(5); a6, e6 = L(6)
    space(p, t)
    earth(p, t)
    k = eio(prog(t, a5, e6 - 1.0))
    x, y = pos((0.5 + 0.5 * k) * math.pi)
    faller(p, x, y, 1.0, ang=math.pi, arms=1, t=t)
    if k < 0.98:
        gravity_arrows(p, x, y, 1 - k * 0.5, -1, t)
    v = 8.0 * (1 - eo(k))
    meter(p, 905, 790, "SPEED", v / 8.6, f"{v:.1f}", RED, 1.0)
    pill(p, 905, 440, "GRAVITY FLIPS", prog(t, a5 + 0.2, a5 + 0.5) * (1 - prog(t, a6, a6 + 0.3)), bg=(120, 200, 255), size=30)
    if t > a6:
        pill(p, 905, 440, "DEAD STOP", prog(t, a6 + 0.3, a6 + 0.6), bg=WHITE, size=30)
        q = eback(prog(t, e6 - 0.9, e6 - 0.5))
        if q > 0:
            p.text((x, y + 110), "GRAB IT!", f2("anton", int(64 * q) + 1), YEL)

@V.scene(7)
def pendulum(p, t, L):
    a, e = L(7)
    space(p, t)
    earth(p, t)
    ph = (t - a) * 2.4
    x, y = pos(math.pi * (0.5 - 0.5 * math.cos(ph)))
    for j in range(1, 7):                                   # ghost trail
        gx, gy = pos(math.pi * (0.5 - 0.5 * math.cos(ph - j * 0.12)))
        p.circle(gx, gy, 9 - j, fill=(255, 140, 40))
    faller(p, x, y, 1.0, ang=math.pi * (0.5 - 0.5 * math.cos(ph)), arms=1, t=t)
    trips = int((t - a) * 2.4 / math.pi)
    p.rr([800, 440, 1010, 590], 30, fill=(20, 30, 50))
    p.text((905, 500), f"×{trips}", f2("anton", 80), YEL)
    p.text((905, 562), "TRIPS", f2("dm", 26), MUTED)

@V.scene(8, 9)
def hot(p, t, L):
    a, _ = L(8); a9, e = L(9)
    space(p, t)
    z = eio(prog(t, a - 0.3, a + 0.5))
    earth(p, t, glow=1.0, cx=lerp(EX, 540, z), cy=lerp(EY, 775, z), r=lerp(ER, 380, z))
    k = eback(prog(t, a + 0.6, a + 1.0))
    if k > 0:
        p.rr([540 - 300 * k, 560, 540 + 300 * k, 720], 40, fill=(20, 30, 50))
        if k > 0.9:
            p.text((540, 640), "6,000°C", f2("anton", 120), YEL)
    q = eback(prog(t, a9, a9 + 0.4))
    if q > 0:
        p.circle(400, 900, 90 * q, fill=(255, 200, 60))
        for i in range(12):
            ang = i * math.pi / 6 + t
            p.line([(400 + 105 * q * math.cos(ang), 900 + 105 * q * math.sin(ang)),
                    (400 + 135 * q * math.cos(ang), 900 + 135 * q * math.sin(ang))], (255, 200, 60), 8)
        p.text((540, 900), "=", f2("anton", int(110 * q) + 1), WHITE)
        p.text((700, 900), "SUN'S SURFACE", f2("dm", max(8, int(34 * q))), WHITE)

@V.scene(10)
def outro(p, t, L):
    a, e = L(10)
    space(p, t)
    earth(p, t)
    faller(p, EX, EY - ER - 60, 1.3, arms=0.3 + 0.2 * math.sin(t * 6), t=t)
    pill(p, 850, 520, "YES", prog(t, a + 0.3, a + 0.6), bg=GREEN, size=60)
    pill(p, 850, 660, "NO WAY", prog(t, a + 0.6, a + 0.9), bg=RED, fg=WHITE, size=50)
    fp = prog(t, e - 1.8, e - 1.4)
    if fp > 0:
        r = 60 * eback(fp)
        p.circle(850, 860, r, fill=RED)
        p.line([(850 - r * .45, 860), (850 + r * .45, 860)], fill=WHITE, width=12)
        p.line([(850, 860 - r * .45), (850, 860 + r * .45)], fill=WHITE, width=12)

if __name__ == "__main__":
    V.main()
