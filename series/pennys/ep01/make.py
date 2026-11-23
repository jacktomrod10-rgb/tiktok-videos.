import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

STATE = json.load(open(os.path.join(os.path.dirname(__file__), "..", "state.json")))
DAY = 1
FUND = 23.50

V = Video(
    "pennys-ep01", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    lines=[
        "This family has never been on holiday. Not once.",
        "Meet the Pennys. This is Dave. He fixes washing machines, and he's never been further than Skegness.",
        "This is Sue. She runs the house, the budget, and the family group chat.",
        "Ellie is fifteen, and hasn't looked up from her phone since twenty twenty-three.",
        "Alfie is eight, and his biggest dream is to see a real kangaroo.",
        "And this is Crumbs. He has eaten three TV remotes this year.",
        "Last night, Sue found a deal. Three weeks in Australia, for the whole family. But they need a one thousand pound deposit.",
        "Australia has kangaroos, koalas, and spiders the size of your hand. Alfie hasn't stopped screaming since.",
        "The money is due in thirty days. And the family holiday jar has... twenty-three pounds fifty in it.",
        "Their stats aren't great either. Money: twenty-three pounds fifty. Happiness: fifty out of a hundred. And the house: twenty-two. It's a mess.",
        "So it's up to you. What should the Pennys do first?",
        "A: a car boot sale, to sell all the junk in the garage. B: Dave takes weekend repair jobs. Or C: Ellie sells her old clothes online.",
        "Comment A, B or C. The most votes decides what happens tomorrow. Follow, to see if they make it.",
    ],
    display=[
        "This family has never been on *holiday*. Not *once*.",
        "Meet the *Pennys*. This is *Dave*. He fixes washing machines, and he's never been further than *Skegness*.",
        "This is *Sue*. She runs the house, the *budget*, and the family *group chat*.",
        "*Ellie* is 15, and hasn't looked up from her *phone* since *2023*.",
        "*Alfie* is 8, and his biggest dream is to see a real *kangaroo*.",
        "And this is *Crumbs*. He has eaten *three* TV remotes this year.",
        "Last night, Sue found a deal. Three weeks in *Australia*, for the whole family. But they need a *£1,000* deposit.",
        "Australia has *kangaroos*, koalas, and spiders the size of your *hand*. Alfie hasn't stopped *screaming* since.",
        "The money is due in *30 days*. And the family holiday jar has... *£23.50* in it.",
        "Their stats aren't great either. Money: *£23.50*. Happiness: *50/100*. And the house: *22/100*. It's a *mess*.",
        "So it's up to *you*. What should the Pennys do *first*?",
        "*A*: a car boot sale, to sell all the junk in the garage. *B*: Dave takes weekend repair jobs. Or *C*: Ellie sells her old clothes online.",
        "Comment *A*, *B* or *C*. The most votes decides what happens *tomorrow*. Follow, to see if they make it.",
    ],
)

OPTIONS = [("A", "Car boot sale", "+£   HOUSE +   ALFIE'S TOYS?"),
           ("B", "Dave's weekend jobs", "+££   DAVE TIRED"),
           ("C", "Ellie sells clothes online", "+£   ELLIE HAPPY")]

def top(p, t):
    pass   # the HUD is drawn by hud_band below, outside the camera move

@V.fixed
def hud_band(p, t):
    P.hud(p, DAY, FUND)

@V.sounds
def sounds(L):
    a5 = L(5)[0]; a6 = L(6)[0]; a8 = L(8)[0]; a11 = L(11)[0]; a12 = L(12)[0]
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh"), (2.5, "pop"), (a5 + 0.2, "boing"), (a6 + 0.8, "ding"), (L(7)[0] + 0.5, "boing"),
           (a8 + 0.4, "pop"), (a8 + 3.6, "cash"), (a12 + 0.1, "pop"), (a12 + 3.0, "ding")]
    out += [(a11 - 0.4 + 0.6 + i * 2.7, "pop") for i in range(3)]
    out += [(L(i)[0] + 0.3, "pop") for i in (2, 3, 4)]
    return out

@V.scene(0)
def hook(p, t, L):
    P.living_room(p, t, 0.03)
    P.family(p, t, {"dave": "sad", "sue": "sad", "ellie": "neutral", "alfie": "sad", "crumbs": "neutral"})
    top(p, t)
    # title card hook for the first ~2.4 s, then it slides away
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0 = 560
        dx = -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.35, 0.7)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "30 DAYS", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "TO SAVE \u00a31,000", f2("anton", max(10, int(96 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "ONE SKINT FAMILY. YOU DECIDE.", f2("dm", max(8, int(40 * k3))), (255, 160, 190))
    pill(p, 540, 380, "HOLIDAYS TAKEN: 0", prog(t, 2.5, 2.9), bg=RED, fg=WHITE)

@V.scene(1, 5)
def meet(p, t, L):
    P.living_room(p, t, 0.03)
    who = 1
    for i in range(1, 6):
        if t >= L(i)[0] - 0.2: who = i
    a, _ = L(who)
    k = eback(prog(t, a - 0.2, a + 0.3))
    s = 1.25 * max(0.01, k)
    if who == 1:
        P.dave(p, 540, 1120, s, "happy", t, hold="wrench")
        pill(p, 540, 380, "DAVE, 41", prog(t, a + 1.0, a + 1.3))
        pill(p, 540, 1110, "FURTHEST TRIP: SKEGNESS", prog(t, a + 4.0, a + 4.4), bg=WHITE)
    elif who == 2:
        P.sue(p, 540, 1120, s, "happy", t, hold="phone")
        pill(p, 540, 380, "SUE, 40", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "BOSS OF THE GROUP CHAT", prog(t, a + 2.6, a + 3.0), bg=WHITE)
    elif who == 3:
        P.ellie(p, 540, 1120, s, "neutral", t, hold="phone")
        pill(p, 540, 380, "ELLIE, 15", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "SCREEN TIME: YES", prog(t, a + 2.4, a + 2.8), bg=WHITE)
    elif who == 4:
        P.alfie(p, 540, 1120, s * 1.1, "grin", t, wave=1)
        pill(p, 540, 380, "ALFIE, 8", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "DREAM: A REAL KANGAROO", prog(t, a + 2.2, a + 2.6), bg=ORANGE)
    else:
        P.crumbs(p, 600, 1120, 1.3 * max(0.01, k), "happy", t)
        # half-eaten remote
        p.rr([170, 1040, 330, 1090], 14, fill=(40, 44, 52))
        for i in range(3):
            p.circle(205 + i * 40, 1065, 9, fill=(200, 60, 60))
        pill(p, 540, 380, "CRUMBS, THE DOG", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "REMOTES EATEN: 3", prog(t, a + 2.0, a + 2.4), bg=WHITE)
    top(p, t)

@V.scene(6, 7)
def the_deal(p, t, L):
    a6, _ = L(6); a7, _ = L(7)
    P.living_room(p, t, 0.03)
    if t < a7:
        P.sue(p, 230, 1120, 1.0, "shock" if t > a6 + 2.5 else "happy", t, hold="phone")
        P.phone_card(p, t, a6 + 0.8, [("AUSTRALIA", 70, INK), ("3 WEEKS · WHOLE FAMILY", 32, (60, 60, 70)), ("£1,000", 90, RED), ("DEPOSIT", 34, (60, 60, 70))], cx=700, cy=720)
    else:
        P.alfie(p, 540, 1120, 1.4, "grin", t, wave=1)
        for ang, rr in [(-30, 330), (200, 320), (20, 360), (160, 350)]:
            a = math.radians(ang)
            sparkle(p, 540 + math.cos(a) * rr, 700 + math.sin(a) * rr, 30 * eback(prog(t, a7 + 0.5, a7 + 0.9)))
        pill(p, 540, 380, "KANGAROOS!!!", prog(t, a7 + 0.4, a7 + 0.8), bg=ORANGE)
    top(p, t)

@V.scene(8, 9)
def jar_and_stats(p, t, L):
    a8, _ = L(8); a9, _ = L(9)
    P.living_room(p, t, 0.03)
    if t < a9:
        p.rect([0, 300, 1080, 1170], fill=(18, 28, 46))
        P.jar(p, 540, 980, 3.2, 0.03)
        pill(p, 540, 380, "DUE IN 30 DAYS", prog(t, a8 + 0.4, a8 + 0.8), bg=RED, fg=WHITE)
        k = eback(prog(t, a8 + 3.6, a8 + 4.0))
        if k > 0:
            p.text((540, 1080), "£23.50", f2("anton", int(110 * k)), YEL)
    else:
        P.stats_panel(p, t, a9 + 0.2, [("MONEY", 3, GREEN, "\u00a323.50"), ("HAPPINESS", 50, YEL, "50/100"), ("HOUSE", 22, ORANGE, "22/100")])
    top(p, t)

@V.scene(10, 12)
def vote(p, t, L):
    a10, _ = L(10); a11, _ = L(11); a12, _ = L(12)
    if t < a11:
        P.living_room(p, t, 0.03)
        P.family(p, t, {"dave": "worried", "sue": "worried", "ellie": "neutral", "alfie": "grin"})
        pill(p, 540, 380, "YOU DECIDE", prog(t, a10 + 0.5, a10 + 0.9))
    elif t < a12:
        # options appear as they're read out
        P.vote_card(p, t, a11 - 0.4, "WHAT SHOULD THEY DO?", OPTIONS, gap=2.7)
    else:
        P.living_room(p, t, 0.03)
        P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "happy", "alfie": "grin"})
        pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a12 + 0.1, a12 + 0.5), bg=WHITE, size=54)
        pill(p, 540, 490, "DAY 2 TOMORROW", prog(t, a12 + 3.0, a12 + 3.4), bg=YEL, size=40)
    top(p, t)

if __name__ == "__main__":
    V.main()
