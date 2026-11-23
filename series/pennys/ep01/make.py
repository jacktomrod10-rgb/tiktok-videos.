import os, sys, math, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)
from studio.kit import *
from studio import pennys as P

DAY = 1
FUND = 23.50

SCRIPT = [
    # (speaker, spoken text, caption text)
    ("narrator", "This family has never been on holiday. Not once.", "This family has never been on *holiday*. Not *once*."),
    ("narrator", "Meet the Pennys. Dave fixes washing machines.", "Meet the *Pennys*. *Dave* fixes washing machines."),
    ("dave", "I went to Skegness once. It rained the whole time.", "I went to *Skegness* once. It *rained* the whole time."),
    ("narrator", "Sue runs the house, the budget, and the family group chat.", "*Sue* runs the house, the *budget*, and the family *group chat*."),
    ("sue", "Nobody leaves the group chat. Nobody.", "Nobody *leaves* the group chat. *Nobody*."),
    ("narrator", "Ellie is fifteen, and hasn't looked up from her phone since twenty twenty-three.", "*Ellie* is 15, and hasn't looked up from her *phone* since *2023*."),
    ("ellie", "I'm literally listening.", "I'm *literally* listening."),
    ("narrator", "Alfie is eight, and he is obsessed with kangaroos.", "*Alfie* is 8, and he is obsessed with *kangaroos*."),
    ("alfie", "When I grow up, I'm going to be a kangaroo.", "When I grow up, I'm going to *be* a *kangaroo*."),
    ("narrator", "And this is Crumbs. He has eaten three TV remotes this year.", "And this is *Crumbs*. He has eaten *three* TV remotes this year."),
    ("narrator", "Last night, Sue found a deal. Three weeks in Australia, for the whole family.", "Last night, Sue found a deal. *Three weeks* in *Australia*, for the whole family."),
    ("sue", "We just need a one thousand pound deposit. In thirty days.", "We just need a *£1,000* deposit. In *30 days*."),
    ("alfie", "Kangaroos!", "*KANGAROOS!*"),
    ("narrator", "The holiday jar has... twenty-three pounds fifty in it.", "The holiday jar has... *£23.50* in it."),
    ("narrator", "Happiness: fifty out of a hundred. And the house: twenty-two. It's a mess.", "Happiness: *50/100*. And the house: *22/100*. It's a *mess*."),
    ("narrator", "So it's up to you. What should the Pennys do first?", "So it's up to *you*. What should the Pennys do *first*?"),
    ("narrator", "A: a car boot sale, to sell the junk in the garage. B: Dave takes weekend repair jobs. Or C: Ellie sells her old clothes online.", "*A*: a car boot sale, to sell the junk in the garage. *B*: Dave takes weekend repair jobs. Or *C*: Ellie sells her old clothes online."),
    ("ellie", "Not my clothes!", "Not *my* clothes!"),
    ("narrator", "Comment A, B or C. The most votes decides what happens tomorrow. Follow, to see if they make it.", "Comment *A*, *B* or *C*. The most votes decides what happens *tomorrow*. Follow, to see if they make it."),
]

V = Video(
    "pennys-ep01", episode=DAY, series="THE PENNYS", voice=P.NARRATOR, music="pluck",
    cast=P.CAST, speaker_colours=P.SPEAKER_COLOURS,
    lines=[(sp, txt) for sp, txt, _ in SCRIPT],
    display=[cap for _, _, cap in SCRIPT],
)

OPTIONS = [("A", "Car boot sale", "+£   HOUSE +   ALFIE'S TOYS?"),
           ("B", "Dave's weekend jobs", "+££   DAVE TIRED"),
           ("C", "Ellie sells clothes online", "+£   ELLIE NOT HAPPY")]

@V.fixed
def hud_band(p, t):
    P.hud(p, DAY, FUND)

@V.sounds
def sounds(L):
    out = [(0.02, "thud"), (0.36, "pop"), (0.8, "pop"), (2.2, "whoosh"), (2.5, "pop"),
           (L(9)[0] + 0.2, "boing"), (L(10)[0] + 0.8, "ding"), (L(12)[0], "boing"),
           (L(13)[0] + 0.4, "pop"), (L(13)[1] - 0.6, "cash"), (L(18)[0] + 0.1, "pop"), (L(18)[0] + 3.0, "ding")]
    out += [(L(16)[0] - 0.4 + 0.6 + i * 2.7, "pop") for i in range(3)]
    out += [(L(i)[0] + 0.3, "pop") for i in (3, 5, 7)]
    return out

@V.scene(0)
def hook(p, t, L):
    P.living_room(p, t, 0.03)
    P.family(p, t, {"dave": "sad", "sue": "sad", "ellie": "neutral", "alfie": "sad", "crumbs": "neutral"})
    out_k = eio(prog(t, 2.2, 2.7))
    if out_k < 1:
        y0, dx = 560, -1200 * out_k
        p.rect([0 + dx, y0, 1080 + dx, y0 + 430], fill=(11, 18, 32, 235))
        k1 = eback(prog(t, 0.0, 0.35)); k2 = eback(prog(t, 0.35, 0.7)); k3 = eback(prog(t, 0.8, 1.15))
        if k1 > 0: p.text((540 + dx, y0 + 110), "30 DAYS", f2("anton", max(10, int(180 * k1))), YEL)
        if k2 > 0: p.text((540 + dx, y0 + 250), "TO SAVE £1,000", f2("anton", max(10, int(96 * k2))), WHITE)
        if k3 > 0: p.text((540 + dx, y0 + 355), "ONE SKINT FAMILY. YOU DECIDE.", f2("dm", max(8, int(40 * k3))), (255, 160, 190))
    pill(p, 540, 380, "HOLIDAYS TAKEN: 0", prog(t, 2.5, 2.9), bg=RED, fg=WHITE)

@V.scene(1, 9)
def meet(p, t, L):
    P.living_room(p, t, 0.03)
    groups = [(1, 2, "dave"), (3, 4, "sue"), (5, 6, "ellie"), (7, 8, "alfie"), (9, 9, "crumbs")]
    cur = groups[0]
    for g in groups:
        if t >= L(g[0])[0] - 0.2: cur = g
    a, _ = L(cur[0])
    k = eback(prog(t, a - 0.2, a + 0.3))
    s = 1.25 * max(0.01, k)
    talk = V.talk(t, cur[2])
    if cur[2] == "dave":
        P.dave(p, 540, 1120, s, "tired" if t > L(2)[0] + 1.6 else "happy", t, hold="wrench", talk=talk)
        pill(p, 540, 380, "DAVE, 41", prog(t, a + 0.6, a + 0.9))
        pill(p, 540, 1110, "FURTHEST TRIP: SKEGNESS", prog(t, L(2)[0] + 0.4, L(2)[0] + 0.8), bg=WHITE)
    elif cur[2] == "sue":
        P.sue(p, 540, 1120, s, "happy", t, hold="phone", talk=talk)
        pill(p, 540, 380, "SUE, 40", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "BOSS OF THE GROUP CHAT", prog(t, a + 2.6, a + 3.0), bg=WHITE)
    elif cur[2] == "ellie":
        P.ellie(p, 540, 1120, s, "neutral", t, hold="phone", talk=talk)
        pill(p, 540, 380, "ELLIE, 15", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "SCREEN TIME: YES", prog(t, a + 2.4, a + 2.8), bg=WHITE)
    elif cur[2] == "alfie":
        P.alfie(p, 540, 1120, s * 1.1, "grin", t, wave=1, talk=talk)
        pill(p, 540, 380, "ALFIE, 8", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "FUTURE KANGAROO", prog(t, L(8)[0] + 1.6, L(8)[0] + 2.0), bg=ORANGE)
    else:
        P.crumbs(p, 600, 1120, 1.3 * max(0.01, k), "happy", t)
        p.rr([166, 1036, 334, 1094], 16, fill=P.OUT)
        p.rr([170, 1040, 330, 1090], 14, fill=(40, 44, 52))
        for i in range(3):
            p.circle(205 + i * 40, 1065, 9, fill=(200, 60, 60))
        pill(p, 540, 380, "CRUMBS, THE DOG", prog(t, a + 0.3, a + 0.6))
        pill(p, 540, 1110, "REMOTES EATEN: 3", prog(t, a + 2.0, a + 2.4), bg=WHITE)

@V.scene(10, 12)
def the_deal(p, t, L):
    a10, _ = L(10); a11, _ = L(11); a12, _ = L(12)
    P.living_room(p, t, 0.03)
    if t < a12:
        P.sue(p, 230, 1120, 1.0, "shock" if t > a10 + 2.5 else "happy", t, hold="phone", talk=V.talk(t, "sue"))
        P.phone_card(p, t, a10 + 0.8, [("AUSTRALIA", 70, INK), ("3 WEEKS · WHOLE FAMILY", 32, (60, 60, 70)), ("£1,000", 90, RED), ("DEPOSIT", 34, (60, 60, 70))], cx=700, cy=720)
    else:
        P.alfie(p, 540, 1120, 1.4, "grin", t, wave=1, talk=V.talk(t, "alfie"))
        for ang, rr in [(-30, 330), (200, 320), (20, 360), (160, 350)]:
            a = math.radians(ang)
            sparkle(p, 540 + math.cos(a) * rr, 700 + math.sin(a) * rr, 30 * eback(prog(t, a12 + 0.1, a12 + 0.5)))

@V.scene(13, 14)
def jar_and_stats(p, t, L):
    a13, e13 = L(13); a14, _ = L(14)
    P.living_room(p, t, 0.03)
    if t < a14:
        p.rect([0, 300, 1080, 1170], fill=(18, 28, 46))
        P.jar(p, 540, 980, 3.2, 0.03)
        pill(p, 540, 380, "DUE IN 30 DAYS", prog(t, a13 + 0.4, a13 + 0.8), bg=RED, fg=WHITE)
        k = eback(prog(t, e13 - 0.6, e13 - 0.2))
        if k > 0:
            p.text((540, 1080), "£23.50", f2("anton", int(110 * k)), YEL)
    else:
        P.stats_panel(p, t, a14 - 0.2, [("MONEY", 3, GREEN, "£23.50"), ("HAPPINESS", 50, YEL, "50/100"), ("HOUSE", 22, ORANGE, "22/100")])

@V.scene(15, 18)
def vote(p, t, L):
    a15, _ = L(15); a16, _ = L(16); a17, _ = L(17); a18, _ = L(18)
    if t < a16:
        P.living_room(p, t, 0.03)
        P.family(p, t, {"dave": "worried", "sue": "worried", "ellie": "neutral", "alfie": "grin"})
        pill(p, 540, 380, "YOU DECIDE", prog(t, a15 + 0.5, a15 + 0.9))
    elif t < a18:
        P.vote_card(p, t, a16 - 0.4, "WHAT SHOULD THEY DO?", OPTIONS, gap=2.7)
        if t > a17 - 0.1:
            k = eback(prog(t, a17 - 0.1, a17 + 0.3))
            P.ellie(p, 900, 1180, 0.55 * max(0.01, k), "shock", t, hold=None, talk=V.talk(t, "ellie"))
    else:
        P.living_room(p, t, 0.03)
        P.family(p, t, {"dave": "happy", "sue": "happy", "ellie": "happy", "alfie": "grin"})
        pill(p, 540, 400, "COMMENT A, B OR C!", prog(t, a18 + 0.1, a18 + 0.5), bg=WHITE, size=54)
        pill(p, 540, 490, "DAY 2 TOMORROW", prog(t, a18 + 3.0, a18 + 3.4), bg=YEL, size=40)

if __name__ == "__main__":
    V.main()
