"""Episode 4: How a torn QR code still scans (error correction).
Run from the repo root:
    python3 -I videos/2026-11-24-qr-torn/make.py tts
    python3 -I videos/2026-11-24-qr-torn/make.py stills ...
    python3 -I videos/2026-11-24-qr-torn/make.py render videos/2026-11-24-qr-torn.mp4
"""
import os, sys, math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from studio.kit import *

V = Video(
    "qr-torn", episode=4, title="How does a *torn* QR code still *scan*?",
    lines=[
        "Tear a chunk off a QR code. It still scans.",
        "Up to thirty percent of it can be damaged on the strongest setting, and your phone still rebuilds the message.",
        "The trick is hidden backup. Next to your message, the code stores extra data, built with maths called Reed-Solomon code.",
        "It's the same maths used on music CDs, and on space probes like Voyager.",
        "Whoever makes the code picks how much backup to add. Level L can recover about seven percent, M fifteen, Q twenty-five, and H thirty.",
        "More backup means more squares, so the stronger codes come out bigger.",
        "But the three big squares in the corners aren't data at all. They show your phone where the code is, and which way up, from any angle.",
        "Their stripes follow a one, one, three, one, one pattern. The inventors checked flyers, magazines and boxes to find the ratio that turns up least in print.",
        "Japan's Denso released it in nineteen ninety-four to track car parts in factories, where labels get covered in oil and dirt.",
        "And it chose not to enforce its patent, so anyone can make one, free.",
        "Which level would you pick: L, M, Q or H? Comment your letter.",
        "Follow for more everyday genius.",
    ],
    display=[
        "Tear a *chunk* off a QR code. It still *scans*.",
        "Up to *30%* of it can be *damaged* on the strongest setting, and your phone still *rebuilds* the message.",
        "The trick is hidden *backup*. Next to your message, the code stores *extra* data, built with maths called *Reed-Solomon* code.",
        "It's the same maths used on music *CDs*, and on space probes like *Voyager*.",
        "Whoever makes the code picks how much backup to add. Level *L* can recover about *7%*, *M* 15, *Q* 25, and *H* 30.",
        "More backup means more *squares*, so the stronger codes come out *bigger*.",
        "But the three big *squares* in the corners aren't data at all. They show your phone *where* the code is, and which way *up*, from any *angle*.",
        "Their stripes follow a *1,* *1,* *3,* *1,* *1* pattern. The inventors checked flyers, magazines and boxes to find the ratio that turns up *least* in print.",
        "Japan's *Denso* released it in *1994* to track *car* parts in factories, where labels get covered in *oil* and dirt.",
        "And it chose not to enforce its *patent*, so anyone can make one, *free*.",
        "Which level would you pick: *L,* *M,* *Q* or *H?* Comment your *letter*.",
        "Follow for more everyday *genius*.",
    ],
)

# ---------------------------------------------------------------- QR drawings
from PIL import ImageChops

# Real codes for "EVERYDAY GENIUS" (made with segno): level H = version 2 (25x25), level L = version 1 (21x21).
QR_H = ["1111111000111010001111111", "1000001010001001101000001", "1011101011011000101011101", "1011101011110010001011101",
        "1011101010010101001011101", "1000001010100110101000001", "1111111010101010101111111", "0000000000000011000000000",
        "0010011111000010110111110", "0100000010110101101000001", "0100011100001100011010011", "0101010111100001110110110",
        "1110101011001101100101101", "0000010000001110100010010", "1100101011110010111010101", "0011100101001101100001110",
        "1110001000111110111111110", "0000000010111011100011101", "1111111011000111101010010", "1000001010101100100010011",
        "1011101001000011111111001", "1011101000101101000101000", "1011101010000011111011011", "1000001001101000011001001",
        "1111111001110000010011011"]
QR_L = ["111111101111101111111", "100000101010101000001", "101110101000001011101", "101110101111001011101",
        "101110100000101011101", "100000101101001000001", "111111101010101111111", "000000000111100000000",
        "110011100101000101111", "001011010101111101101", "000001100001010010010", "001000001100001111010",
        "010001110010110100010", "000000001100100010110", "111111100100110010101", "100000101111100101111",
        "101110101001010100101", "101110100010111010111", "101110100011010110000", "100000101001011000101",
        "111111101010111110111"]
MARGIN = 3          # white border (modules) around the code
QINK = (16, 22, 34)

# the torn-off chunk (module coordinates, card spans -3..n+3); tested: the code still decodes without it
TEAR = [(28, 12.6), (26.2, 13.3), (24.6, 12.9), (22.8, 14.1), (21.0, 14.0), (19.6, 15.6), (18.2, 16.0), (17.3, 17.9),
        (16.0, 18.6), (15.6, 20.6), (14.5, 21.5), (14.6, 23.6), (13.6, 24.8), (13.9, 26.6), (13.2, 28)]
PIECE = TEAR + [(28, 28)]

def _in_poly(x, y, poly):
    inside, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside

MISSING = [(x, y) for y in range(25) for x in range(25) if QR_H[y][x] == "1" and _in_poly(x + .5, y + .5, PIECE)]

def is_finder(x, y, n):
    return (x < 7 and y < 7) or (x >= n - 7 and y < 7) or (x < 7 and y >= n - 7)

_SPR = {}
def qr_sprite(mat, mod, finder=None, part=None):
    """Card + modules at 2x. part: None (whole), 'main' (torn), 'piece' (the torn chunk)."""
    key = (id(mat), mod, finder, part)
    if key in _SPR: return _SPR[key]
    n = len(mat); m = mod * S; size = int((n + 2 * MARGIN) * m)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(m * 1.4), fill=(247, 247, 243, 255))
    for y, row in enumerate(mat):
        for x, c in enumerate(row):
            if c == "1":
                col = finder if (finder and is_finder(x, y, n)) else QINK
                x0, y0 = (x + MARGIN) * m, (y + MARGIN) * m
                d.rectangle([x0, y0, x0 + m - 1, y0 + m - 1], fill=col + (255,))
    if part:
        poly = [((x + MARGIN) * m, (y + MARGIN) * m) for x, y in PIECE]
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        if part == "main": mask = ImageChops.invert(mask)
        img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
        edge = [((x + MARGIN) * m, (y + MARGIN) * m) for x, y in TEAR]
        ImageDraw.Draw(img).line(edge, fill=(226, 224, 214, 255), width=max(2, int(m * 0.28)))
    _SPR[key] = img
    return img

def piece_sprite(mod):
    """The torn chunk cropped to its own box, plus its centre's offset from the card centre (output px)."""
    key = ("piece-crop", mod)
    if key not in _SPR:
        full = qr_sprite(QR_H, mod, part="piece")
        bb = full.getchannel("A").getbbox()
        im = full.crop(bb)
        _SPR[key] = (im, ((bb[0] + bb[2]) / 2 / S - full.width / 2 / S, (bb[1] + bb[3]) / 2 / S - full.height / 2 / S))
    return _SPR[key]

def _composite(dst, im, x, y):
    x, y = int(x), int(y)
    cx0, cy0 = max(0, -x), max(0, -y)
    cx1, cy1 = min(im.width, dst.width - x), min(im.height, dst.height - y)
    if cx1 <= cx0 or cy1 <= cy0: return
    dst.alpha_composite(im.crop((cx0, cy0, cx1, cy1)), (x + cx0, y + cy0))

def put(p, spr, cx, cy, angle=0.0, scale=1.0, alpha=1.0, shadow=True, offset=(0, 0)):
    """Paste a 2x sprite centred on (cx, cy) in output px. offset shifts it (output px) after rotating."""
    im = spr
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(angle) > 0.05:
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * clamp(alpha))))
    x = (cx + offset[0]) * S - im.width / 2; y = (cy + offset[1]) * S - im.height / 2
    if shadow and LOOK and alpha > 0.05:
        q = 4
        sm = im.getchannel("A").resize((max(1, im.width // q), max(1, im.height // q)), Image.BILINEAR)
        sm = sm.point(lambda v: int(v * 0.42 * clamp(alpha))).filter(ImageFilter.GaussianBlur(5))
        sh = Image.new("RGBA", sm.size, (4, 8, 18, 0)); sh.putalpha(sm)
        _composite(p.img, sh.resize(im.size, Image.BILINEAR), x, y + 20)
    _composite(p.img, im, x, y)

def card_px(n, mod, cx, cy, scale=1.0):
    """Top-left of module (0,0) and the module size, in output px, for a card centred on (cx, cy)."""
    m = mod * scale
    return cx - (n + 2 * MARGIN) * m / 2 + MARGIN * m, cy - (n + 2 * MARGIN) * m / 2 + MARGIN * m, m

def brackets(p, cx, cy, half, col=YEL, w=10, arm=60):
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * half, cy + sy * half
            p.line([(x, y - sy * arm), (x, y), (x - sx * arm, y)], fill=col, width=w)

def finder_big(p, cx, cy, m, col=QINK, light=(247, 247, 243)):
    h = 3.5 * m
    p.rect([cx - h, cy - h, cx + h, cy + h], fill=col)
    p.rect([cx - h + m, cy - h + m, cx + h - m, cy + h - m], fill=light)
    p.rect([cx - h + 2 * m, cy - h + 2 * m, cx + h - 2 * m, cy + h - 2 * m], fill=col)

def stripe_bar(p, cx, cy, u, k=1.0, pops=None, t=0.0):
    """1:1:3:1:1 bar (dark, light, dark x3, light, dark), unit u px. pops: start times of each segment."""
    widths, x = [1, 1, 3, 1, 1], cx - 3.5 * u
    for i, wd in enumerate(widths):
        kk = k if pops is None else eback(prog(t, pops[i], pops[i] + 0.3))
        if kk > 0:
            col = QINK if i % 2 == 0 else (247, 247, 243)
            hh = 50 * kk
            p.rect([x + 2, cy - hh, x + wd * u - 2, cy + hh], fill=col, outline=WHITE, width=3)
            p.text((x + wd * u / 2, cy + 100), str(wd), f2("anton", max(8, int(64 * kk))), YEL)
        x += wd * u

# ---------------------------------------------------------------- scenes
@V.scene(0, 1)
def torn(p, t, L):
    a1, e1 = L(1)
    mod = 17
    # card moves up a little for line 1
    mv = eio(prog(t, a1 - 0.2, a1 + 0.5))
    cx, cy, sc = 540, lerp(700, 625, mv), lerp(1.0, 0.86, mv)
    pop = eback(prog(t, 0.0, 0.45))
    if prog(t, 0.0, 0.45) < 1:
        put(p, qr_sprite(QR_H, mod), cx, cy, scale=max(0.05, pop * sc))
        return
    put(p, qr_sprite(QR_H, mod, part="main"), cx, cy, scale=sc)
    # the chunk tears off and drops away
    f = prog(t, 0.8, 1.9)
    if f < 1:
        dx, dy = 40 * eio(prog(t, 0.55, 0.8)) + 90 * f, -18 * eio(prog(t, 0.55, 0.8)) + 330 * f * f
        pc, (pdx, pdy) = piece_sprite(mod)
        put(p, pc, cx + pdx * sc, cy + pdy * sc, angle=-38 * f * f, scale=sc, alpha=1 - prog(t, 1.4, 1.9), offset=(dx, dy))
    ox, oy, m = card_px(25, mod, cx, cy, sc)
    half = (25 + 2 * MARGIN) * m / 2
    # scanner locks on and sweeps
    if 1.7 < t < a1 + 0.3:
        k = eo(prog(t, 1.7, 2.1))
        brackets(p, cx, cy, half + lerp(120, 18, k), w=10)
        sy = cy - half + 2 * half * eio(prog(t, 2.0, 2.7))
        if t < 2.75:
            p.line([(cx - half + 10, sy), (cx + half - 10, sy)], fill=RED, width=8)
    tick(p, cx + half - 30, cy - half + 30, 58, prog(t, 2.75, 3.0) * (1 - prog(t, a1 - 0.3, a1)))
    pill(p, 540, 1085, "STILL SCANS", prog(t, 2.8, 3.1) * (1 - prog(t, a1 - 0.3, a1)), bg=GREEN, size=46)
    # line 1: up to 30% ... rebuilt
    if t > a1:
        # marching dots round the missing chunk
        pts = [(ox + x * m, oy + y * m) for x, y in PIECE + [PIECE[0]]]
        n_d = 34
        for i in range(n_d):
            x, y = path_point(pts, i / n_d + (t - a1) * 0.05)
            p.circle(x, y, 4.5, fill=YEL)
        if t < a1 + 4.2:
            p.text((540, 935), "UP TO", f2("dm", 40), MUTED)
            big_number(p, t, a1 + 0.1, 30, cy=1050, size=170, start=0, dur=1.0, fmt="{}%")
        for i, (x, y) in enumerate(sorted(MISSING, key=lambda q: (q[1], q[0]))):
            k = eback(prog(t, a1 + 3.6 + i * 0.045, a1 + 3.9 + i * 0.045))
            if k > 0:
                c, h = ox + (x + .5) * m, m * 0.5 * k
                p.rect([c - h, oy + (y + .5) * m - h, c + h, oy + (y + .5) * m + h], fill=YEL)
        pill(p, 540, 1060, "MESSAGE REBUILT", prog(t, a1 + 4.6, a1 + 5.0), bg=YEL, size=46)

BR_MSG = ["H", "E", "L", "L", "O"]
BR_BAK = ["0110", "1011", "1100", "0101", "1001"]

@V.scene(2, 3)
def backup(p, t, L):
    a2, e2 = L(2); a3, e3 = L(3)
    if t < a3 - 0.1:
        fo = 1 - prog(t, a3 - 0.4, a3 - 0.1)
        p.text((540, 455), "YOUR MESSAGE", f2("dm", 40), WHITE if fo > 0.5 else MUTED)
        for i in range(5):
            x = 540 + (i - 2) * 175
            k = eback(prog(t, a2 + 0.15 + i * 0.12, a2 + 0.5 + i * 0.12)) * fo
            if k <= 0: continue
            hit = i in (1, 3) and a2 + 5.6 < t < a2 + 6.9
            col = RED if hit else YEL
            shake = math.sin(t * 60) * 8 * (1 - prog(t, a2 + 5.6, a2 + 6.0)) if hit else 0
            p.rr([x - 75 * k + shake, 560 - 60 * k, x + 75 * k + shake, 560 + 60 * k], 18, fill=col)
            if not hit:
                p.text((x, 562), BR_MSG[i], f2("anton", max(8, int(80 * k))), INK)
            else:
                cross(p, x, 560, 34, 1.0)
        if t > a2 + 2.6:
            p.text((540, 715), "BACKUP DATA", f2("dm", 40), BLUE)
        for i in range(5):
            x = 540 + (i - 2) * 175
            k = eback(prog(t, a2 + 3.0 + i * 0.12, a2 + 3.35 + i * 0.12)) * fo
            if k <= 0: continue
            p.rr([x - 75 * k, 820 - 60 * k, x + 75 * k, 820 + 60 * k], 18, fill=BLUE)
            p.text((x, 822), BR_BAK[i], f2("dm", max(8, int(36 * k))), INK)
        # backup rebuilds the damaged bricks
        if a2 + 6.2 < t < a3 - 0.3:
            for i in (1, 3):
                x = 540 + (i - 2) * 175
                k = eo(prog(t, a2 + 6.2, a2 + 6.8))
                p.arrow((x, 755), (x, lerp(755, 640, k)), GREEN, width=10, head=28)
        for i in (1, 3):
            tick(p, 540 + (i - 2) * 175 + 70, 505, 26, prog(t, a2 + 6.9, a2 + 7.2) * fo)
        pill(p, 540, 1040, "REED-SOLOMON CODE", prog(t, a2 + 5.0, a2 + 5.4) * fo, size=44)
    else:
        # music CD
        k = eback(prog(t, a3, a3 + 0.45))
        cx, cy, r = 300, 680, 185 * k
        if r > 1:
            p.circle(cx, cy, r, fill=(196, 202, 214))
            ang = (t - a3) * 120
            for off, col in ((0, (226, 236, 255)), (180, (255, 236, 222))):
                p.d.pieslice([(cx - r * .96) * S, (cy - r * .96) * S, (cx + r * .96) * S, (cy + r * .96) * S], ang + off, ang + off + 50, fill=col)
            p.circle(cx, cy, r * 0.36, fill=(160, 168, 182))
            p.circle(cx, cy, r * 0.12, fill=BG2)
        # space probe
        k2 = eback(prog(t, a3 + 1.6, a3 + 2.1))
        if k2 > 0:
            for i in range(14):
                sx, sy = 600 + (i * 83) % 390, 430 + (i * 151) % 500
                p.circle(sx, sy, 3 + 2 * pulse(t + i * 0.37, 1.4), fill=WHITE)
            bx, by = 780, 690 + math.sin(t * 1.6) * 12
            p.line([(bx, by), (bx + 170 * k2, by + 40 * k2)], fill=EDGE, width=6)
            p.circle(bx + 170 * k2, by + 40 * k2, 10 * k2, fill=BRASS)
            p.rr([bx - 60 * k2, by - 30 * k2, bx + 60 * k2, by + 50 * k2], 10, fill=BRASS)
            p.d.chord([(bx - 125 * k2) * S, (by - 190 * k2) * S, (bx + 125 * k2) * S, (by - 30 * k2) * S], 0, 180, fill=(200, 205, 215))
            p.ell([bx - 125 * k2, by - 128 * k2, bx + 125 * k2, by - 92 * k2], fill=WHITE, outline=EDGE, width=3)
            for sx in (-90, 0, 90):
                p.line([(bx + sx * k2, by - 108 * k2), (bx, by - 190 * k2)], fill=EDGE, width=5)
            p.circle(bx, by - 190 * k2, 9 * k2, fill=WHITE)
        pill(p, 300, 945, "MUSIC CDs", prog(t, a3 + 0.9, a3 + 1.2), bg=WHITE, size=40)
        pill(p, 780, 945, "SPACE PROBES", prog(t, a3 + 2.5, a3 + 2.8), bg=WHITE, size=40)
        pill(p, 540, 1080, "SAME MATHS", prog(t, a3 + 0.4, a3 + 0.7), size=46)

LEVELS = [("L", 7), ("M", 15), ("Q", 25), ("H", 30)]

@V.scene(4, 5)
def levels(p, t, L):
    a4, e4 = L(4); a5, e5 = L(5)
    if t < a5 - 0.1:
        fo = 1 - prog(t, a5 - 0.4, a5 - 0.1)
        pill(p, 540, 430, "YOU CHOOSE THE BACKUP", prog(t, a4 + 0.3, a4 + 0.7) * fo, bg=WHITE, size=42)
        starts = [a4 + 3.6, a4 + 6.1, a4 + 7.0, a4 + 8.1]
        for i, (lab, v) in enumerate(LEVELS):
            y = 560 + i * 140
            k = eback(prog(t, a4 + 0.8 + i * 0.25, a4 + 1.2 + i * 0.25)) * fo
            if k <= 0: continue
            p.text((150, y), lab, f2("anton", max(8, int(96 * k))), YEL)
            p.rr([230, y - 34, 230 + 700 * k, y + 34], 34, fill=(36, 54, 82))
            g = eo(prog(t, starts[i], starts[i] + 0.7)) * fo
            if g > 0:
                w = 700 * v / 30 * g
                p.rr([230, y - 34, 230 + max(68, w), y + 34], 34, fill=GREEN if lab == "H" else YEL)
                p.text((230 + max(68, w) + 20, y + 2), f"{round(v * g)}%", f2("anton", 60), WHITE, anchor="lm")
    else:
        mod = 14
        for mat, cx, lab, t0 in ((QR_L, 275, "LEVEL L: 21×21", a5 + 0.1), (QR_H, 775, "LEVEL H: 25×25", a5 + 0.9)):
            n = len(mat)
            k = eo(prog(t, t0, t0 + 0.9))
            if k <= 0: continue
            spr = qr_sprite(mat, mod)
            rows = int(spr.height * k)
            if rows < 2: continue
            put(p, spr.crop((0, 0, spr.width, rows)), cx, 700 - (spr.height - rows) / 2 / S, shadow=k > 0.99)
            pill(p, cx, 990, lab, prog(t, t0 + 0.6, t0 + 0.9), bg=WHITE if lab.startswith("LEVEL L") else GREEN, size=38)
        pill(p, 540, 1095, "MORE BACKUP = BIGGER CODE", prog(t, a5 + 2.2, a5 + 2.6), size=42)

@V.scene(6)
def finders(p, t, L):
    a, e = L(6)
    mod, cx, cy = 14, 540, 720
    g = pulse(t - a, 0.9) * prog(t, a + 0.9, a + 1.3)
    ang = 0.0
    seq = [(a + 5.3, a + 6.0, 0, 90), (a + 6.2, a + 6.9, 90, 200), (a + 7.0, a + 7.8, 200, 360)]
    for t0, t1, s0, s1 in seq:
        if t >= t0: ang = lerp(s0, s1, eio(prog(t, t0, t1)))
    spr = qr_sprite(QR_H, mod, finder=YEL) if g > 0.5 else qr_sprite(QR_H, mod)
    put(p, spr, cx, cy, angle=ang % 360)
    half = (25 + 2 * MARGIN) * mod / 2
    if ang == 0:
        ox, oy, m = card_px(25, mod, cx, cy)
        for fx, fy in ((0, 0), (18, 0), (0, 18)):
            k = eback(prog(t, a + 0.9, a + 1.3))
            if k > 0:
                x0, y0 = ox + fx * m - 10, oy + fy * m - 10
                p.rr([x0, y0, x0 + 7 * m + 20, y0 + 7 * m + 20], 16, outline=YEL, width=6)
    pill(p, 540, 415, "NOT DATA", prog(t, a + 2.0, a + 2.4) * (1 - prog(t, a + 3.4, a + 3.7)), bg=RED, fg=WHITE, size=44)
    if t > a + 3.6:
        k = eo(prog(t, a + 3.6, a + 4.1))
        brackets(p, cx, cy, half + lerp(130, 22, k) + (60 if ang else 0) * 0, w=10)
        pill(p, 540, 415, "WHERE IT IS + WHICH WAY UP", prog(t, a + 3.8, a + 4.2), size=40)
    pill(p, 540, 1100, "ANY ANGLE", prog(t, a + 6.4, a + 6.8), bg=GREEN, size=46)

@V.scene(7)
def ratio(p, t, L):
    a, e = L(7)
    if t < a + 4.6:
        fo = 1 - prog(t, a + 4.3, a + 4.6)
        k = eback(prog(t, a + 0.1, a + 0.5)) * fo
        if k > 0:
            m = 54 * k
            p.rr([540 - 4.6 * m, 640 - 4.6 * m, 540 + 4.6 * m, 640 + 4.6 * m], 20, fill=(247, 247, 243))
            finder_big(p, 540, 640, m)
            sx = lerp(540 - 3.8 * 54, 540 + 3.8 * 54, eio(prog(t, a + 1.0, a + 4.2)))
            p.line([(sx, 640 - 3.9 * m), (sx, 640 + 3.9 * m)], fill=RED, width=6)
            p.line([(540 - 3.8 * m, 640), (540 + 3.8 * m, 640)], fill=RED, width=4)
        stripe_bar(p, 540, 965, 80, pops=[a + 1.6, a + 2.0, a + 2.5, a + 3.0, a + 3.4], t=t) if fo > 0.5 else None
    else:
        # the survey: flyers, magazines, boxes
        icons_k = [eback(prog(t, a + 4.6 + i * 0.5, a + 5.0 + i * 0.5)) for i in range(3)]
        lift = eio(prog(t, a + 7.2, a + 7.8))
        y = 620 - 120 * lift
        sc = 1 - 0.35 * lift
        k = icons_k[0] * sc
        if k > 0:   # flyer
            x = 220
            p.rr([x - 95 * k, y - 130 * k, x + 95 * k, y + 130 * k], 8, fill=WHITE)
            p.rect([x - 95 * k, y - 130 * k, x + 95 * k, y - 80 * k], fill=ORANGE)
            for j in range(5):
                p.line([(x - 70 * k, y - 50 * k + j * 36 * k), (x + 70 * k - (j % 2) * 40 * k, y - 50 * k + j * 36 * k)], fill=EDGE, width=8 * k)
        k = icons_k[1] * sc
        if k > 0:   # magazine
            x = 540
            p.rr([x - 100 * k, y - 135 * k, x + 100 * k, y + 135 * k], 8, fill=BLUE)
            p.rect([x - 80 * k, y - 115 * k, x + 80 * k, y - 75 * k], fill=WHITE)
            p.circle(x, y + 30 * k, 60 * k, fill=YEL)
            p.rect([x - 80 * k, y + 105 * k, x + 20 * k, y + 118 * k], fill=WHITE)
        k = icons_k[2] * sc
        if k > 0:   # cardboard box
            x = 860
            p.poly([(x - 110 * k, y - 60 * k), (x - 60 * k, y - 110 * k), (x + 120 * k, y - 110 * k), (x + 70 * k, y - 60 * k)], (205, 160, 110))
            p.rect([x - 110 * k, y - 60 * k, x + 70 * k, y + 110 * k], fill=(176, 128, 80))
            p.poly([(x + 70 * k, y - 60 * k), (x + 120 * k, y - 110 * k), (x + 120 * k, y + 60 * k), (x + 70 * k, y + 110 * k)], (140, 100, 62))
            p.rect([x - 30 * k, y - 60 * k, x - 10 * k, y + 110 * k], fill=(222, 196, 150))
        # magnifier sweeps across them
        if a + 5.0 < t < a + 7.4:
            u = eio(prog(t, a + 5.0, a + 7.2))
            mx = lerp(150, 930, u); my = 600 + math.sin(u * 9) * 30
            p.circle(mx, my, 72, outline=WHITE, width=12)
            p.line([(mx + 52, my + 52), (mx + 110, my + 110)], fill=WHITE, width=18)
        pill(p, 540, 960, "FLYERS · MAGAZINES · BOXES", prog(t, a + 5.4, a + 5.8) * (1 - prog(t, a + 7.1, a + 7.4)), bg=WHITE, size=40)
        if t > a + 7.4:
            stripe_bar(p, 540, 860, 70, k=eback(prog(t, a + 7.4, a + 7.8)))
            tick(p, 870, 860, 46, prog(t, a + 7.9, a + 8.2))
            pill(p, 540, 1100, "LEAST USED IN PRINT", prog(t, a + 7.8, a + 8.2), bg=GREEN, size=44)

def oil(p, x, y, s):
    if s <= 0: return
    for dx, dy, r in ((0, 0, 22), (16, 8, 14), (-14, 10, 12), (6, -14, 10)):
        p.circle(x + dx * s, y + dy * s, r * s, fill=(70, 52, 30))

@V.scene(8, 9)
def history(p, t, L):
    a8, e8 = L(8); a9, e9 = L(9)
    if t < a9 - 0.1:
        fo = 1 - prog(t, a9 - 0.4, a9 - 0.1)
        big_number(p, t, a8 + 0.9, 1994, cy=470, size=170, start=1960, dur=1.0)
        # conveyor
        kb = eo(prog(t, a8 + 0.2, a8 + 0.8)) * fo
        if kb > 0:
            p.rr([80, 930, 80 + 920 * kb, 980], 25, fill=(52, 64, 84))
            for i in range(8):
                rx = 120 + i * 120
                if rx < 80 + 920 * kb:
                    p.circle(rx, 1010, 22, fill=SLATE_L)
                    ang = (t * 4 + i) % (2 * math.pi)
                    p.line([(rx, 1010), (rx + 18 * math.cos(ang), 1010 + 18 * math.sin(ang))], fill=EDGE, width=5)
        # scanner head with beam
        if t > a8 + 3.0:
            ks = eback(prog(t, a8 + 3.0, a8 + 3.4)) * fo
            p.rr([700 - 70 * ks, 600 - 40 * ks, 700 + 70 * ks, 650], 14, fill=SLATE_L)
        lab = qr_sprite(QR_L, 4)
        for i in range(4):
            u = ((t - a8 - 2.6) * 0.16 + i * 0.27) % 1.08
            bx = lerp(-120, 1180, u / 1.08)
            if t < a8 + 2.6 or bx < 40 or bx > 1040: continue
            bf = fo * clamp((bx - 40) / 60) * clamp((1040 - bx) / 60)
            p.rr([bx - 100, 760, bx + 100, 925], 10, fill=(176, 128, 80))
            p.rect([bx - 12, 760, bx + 12, 925], fill=(222, 196, 150))
            put(p, lab, bx, 842, shadow=False, alpha=bf)
            oil(p, bx + 28, 862, eback(prog(t, a8 + 5.8 + i * 0.2, a8 + 6.1 + i * 0.2)) * bf)
            if abs(bx - 700) < 45 and t > a8 + 3.4:
                p.line([(700, 650), (bx, 815)], fill=RED, width=5)
                p.line([(700, 650), (bx, 870)], fill=RED, width=5)
                tick(p, bx + 90, 730, 34, 1.0 * fo)
        pill(p, 540, 1100, "CAR PARTS", prog(t, a8 + 3.6, a8 + 4.0) * (1 - prog(t, a8 + 5.4, a8 + 5.7)) * fo, bg=WHITE, size=44)
        pill(p, 540, 1100, "OIL + DIRT? STILL READS", prog(t, a8 + 6.0, a8 + 6.4) * fo, bg=GREEN, size=42)
    else:
        k = eback(prog(t, a9, a9 + 0.45))
        if k > 0:
            p.rr([540 - 210 * k, 700 - 270 * k, 540 + 210 * k, 700 + 270 * k], 18, fill=WHITE)
            p.text((540, 700 - 200 * k), "PATENT", f2("anton", max(8, int(70 * k))), INK)
            for j in range(7):
                p.line([(540 - 150 * k, 700 - 110 * k + j * 46 * k), (540 + (150 - (j % 3) * 50) * k, 700 - 110 * k + j * 46 * k)], fill=EDGE, width=9 * k)
        # little codes popping up all around: anyone can make one
        spots = [(150, 470), (930, 520), (140, 880), (940, 900), (190, 1100), (890, 1110), (120, 680), (960, 710)]
        for i, (x, y) in enumerate(spots):
            kk = eback(prog(t, a9 + 2.2 + i * 0.12, a9 + 2.5 + i * 0.12))
            if kk > 0:
                put(p, qr_sprite(QR_L, 3), x, y + math.sin(t * 2 + i) * 6, scale=kk, shadow=False)
        sk = prog(t, a9 + 2.6, a9 + 2.85)
        if sk > 0:
            z = lerp(1.8, 1.0, eo(sk))
            p.rr([540 - 170 * z, 760 - 75 * z, 540 + 170 * z, 760 + 75 * z], 22, outline=GREEN, width=12)
            p.text((540, 762), "FREE", f2("anton", max(8, int(110 * z))), GREEN)
        pill(p, 540, 1010, "NOT ENFORCED", prog(t, a9 + 1.0, a9 + 1.4) * (1 - prog(t, a9 + 2.4, a9 + 2.6)), bg=RED, fg=WHITE, size=42)

@V.scene(10, 11)
def outro(p, t, L):
    a10, e10 = L(10); a11, e11 = L(11)
    pill(p, 540, 420, "COMMENT YOUR LETTER", prog(t, a10 + 3.0, a10 + 3.4), size=44)
    tiles = [(330, 605), (750, 605), (330, 875), (750, 875)]
    pops = [a10 + 1.6, a10 + 2.0, a10 + 2.4, a10 + 2.9]
    sel = int(((t - a10 - 3.4) / 0.45)) % 4 if t > a10 + 3.4 else -1
    for i, ((x, y), (lab, v)) in enumerate(zip(tiles, LEVELS)):
        k = eback(prog(t, pops[i] - 0.25 if i else a10 + 0.2, pops[i] + 0.1 if i else a10 + 0.6))
        if k <= 0: continue
        hl = i == sel
        p.rr([x - 170 * k, y - 120 * k, x + 170 * k, y + 120 * k], 30, fill=YEL if hl else (36, 54, 82), outline=YEL, width=6)
        p.text((x, y - 18 * k), lab, f2("anton", max(8, int(150 * k))), INK if hl else WHITE)
        p.text((x, y + 82 * k), f"{v}%", f2("dm", max(8, int(36 * k))), INK if hl else MUTED)
    if t > a10 + 3.3:
        bp = eback(prog(t, a10 + 3.3, a10 + 3.7))
        bx, by = 330, 1068
        p.rr([bx - 100 * bp, by - 48 * bp, bx + 100 * bp, by + 48 * bp], 26 * bp, fill=WHITE)
        p.poly([(bx - 40 * bp, by + 44 * bp), (bx - 66 * bp, by + 84 * bp), (bx - 6 * bp, by + 44 * bp)], fill=WHITE)
        for i in range(3):
            d = 9 * bp * (1 + 0.35 * pulse(t - i * 0.2, 0.9))
            p.circle(bx - 45 * bp + i * 45 * bp, by, d, fill=INK)
    fp = prog(t, a11 + 0.1, a11 + 0.5)
    if fp > 0:
        r = 56 * eback(fp)
        p.circle(750, 1068, r, fill=RED)
        p.line([(750 - r * .45, 1068), (750 + r * .45, 1068)], fill=WHITE, width=12)
        p.line([(750, 1068 - r * .45), (750, 1068 + r * .45)], fill=WHITE, width=12)

@V.sounds
def cues(L):
    a1, _ = L(1); a2, _ = L(2); a4, _ = L(4); a7, _ = L(7); a8, _ = L(8); a9, _ = L(9); a10, _ = L(10)
    out = [(0.85, "thud"), (2.75, "ding"), (a1 + 4.6, "pop"), (a2 + 5.6, "boing"), (a2 + 6.9, "ding"),
           (a4 + 3.6, "pop"), (a4 + 6.1, "pop"), (a4 + 7.0, "pop"), (a4 + 8.1, "pop"),
           (a7 + 7.9, "ding"), (a9 + 2.6, "thud")]
    out += [(a10 + 1.6 + 0.4 * i, "pop") for i in range(4)]
    return out

if __name__ == "__main__":
    V.main()
