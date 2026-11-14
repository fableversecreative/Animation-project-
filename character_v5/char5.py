"""FableVerse toon v5 (original designs, premium 'dry comedy' technique):
big round shaded ball head, small dark oval eyes with heavy lid lines, thick brows, one signature feature,
soft bean torso with clothes drawn on it, very thin ink stick limbs, soft cel shading.
toon5(d, x, y, sc, who, emo, look, pose, blink, flip)"""
import math, numpy as np, cv2, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v3zip', 'fableverse_engine', 'v2'))
from rig import C, INK, shade, bez, lerp, clamp, Aff, shadow, GOLD

INK5 = C('231a2e'); OL = 7.5
STYLE = dict(legs='thick', arms='thin')
PANTS = {'napoleon': C('f2eee4'), 'berthier': C('f2eee4'), 'tsar': C('2f4a3a'), 'hunter': C('d8c9a2'), 'farmer': C('3e5f8f')}
BOOT = {'napoleon': C('1d1a22'), 'berthier': C('1d1a22'), 'tsar': C('1d1a22'), 'hunter': C('4a3324'), 'farmer': C('4a3324')}
HEAD_T = C('fbfaf7'); HEAD_B = C('c9cfdc')        # light top -> cool bluish shadow bottom

WHO = {
    'napoleon': dict(coat=C('2b4a9a'), front=C('f1ede3'), trim=C('c8323a'), hat='bicorne', epaul=True, forelock=True, boots=True, breeches=C('efe9dc')),
    'berthier': dict(coat=C('22397a'), front=C('e8c25a'), trim=C('e3b84a'), hat='bicorne_w', epaul=True, tache=C('3a2a20'), sash=C('c8323a'), boots=True, breeches=C('efe9dc')),
    'tsar':     dict(coat=C('eef0f4'), front=C('3f6fb8'), trim=C('3f6fb8'), hat='plume', epaul=True, sash=C('3f78c8'), sideburns=C('c9a060'), boots=True, breeches=C('2f4a3a')),
    'hunter':   dict(coat=C('5a7a3a'), front=C('c9b48a'), trim=C('3e5a28'), hat='tricorne', beard=C('6a4a30'), boots=True, breeches=C('b8a478'), strap=C('6a4a2e')),
    'farmer':   dict(coat=C('3e6aa8'), front=C('e9e2d0'), trim=C('2e5088'), hat='straw', stubble=True, straw=True, boots=False, breeches=C('6a4a30'), overall=True),
}

# eye: open 0..1 (lid coverage = 1-open), tilt + inner-down (angry) / - inner-up (sad); brow raise/angle; mouth kind
EMO = {
    'neutral':  dict(lid=(0.45, 0.45), tilt=0.0, brow=(0.0, 0.0), bang=(0.1, 0.1), mouth='line', eye=1.0),
    'proud':    dict(lid=(0.6, 0.6), tilt=-0.2, brow=(0.35, 0.35), bang=(-0.2, -0.2), mouth='smirk', eye=1.0, chin=-0.08),
    'smug':     dict(lid=(0.62, 0.5), tilt=0.15, brow=(-0.05, 0.45), bang=(0.35, -0.3), mouth='smirk', eye=1.0, look=(0.5, 0)),
    'worried':  dict(lid=(0.12, 0.12), tilt=-0.5, brow=(0.5, 0.5), bang=(-0.9, -0.9), mouth='wavy', eye=1.1, sweat=1),
    'scared':   dict(lid=(0.0, 0.0), tilt=-0.3, brow=(0.9, 0.9), bang=(-0.7, -0.7), mouth='open', eye=1.3, sweat=1, ring=1),
    'shocked':  dict(lid=(0.0, 0.0), tilt=0.0, brow=(1.0, 1.0), bang=(-0.1, -0.1), mouth='o', eye=1.35, ring=1, lines=1),
    'angry':    dict(lid=(0.4, 0.4), tilt=0.6, brow=(-0.45, -0.45), bang=(1.0, 1.0), mouth='grit', eye=0.95),
    'sad':      dict(lid=(0.45, 0.45), tilt=-0.6, brow=(0.2, 0.2), bang=(-1.0, -1.0), mouth='frown', eye=1.0, look=(0, 0.4)),
    'deadpan':  dict(lid=(0.6, 0.6), tilt=0.0, brow=(-0.1, -0.1), bang=(0.0, 0.0), mouth='line', eye=1.0),
    'happy':    dict(lid=(0.3, 0.3), tilt=-0.1, brow=(0.45, 0.45), bang=(-0.2, -0.2), mouth='grin', eye=1.0, happy=1),
    'determined': dict(lid=(0.5, 0.5), tilt=0.4, brow=(-0.3, -0.3), bang=(0.8, 0.8), mouth='line', eye=1.0),
    'confused': dict(lid=(0.2, 0.45), tilt=0.0, brow=(0.8, -0.25), bang=(-0.4, 0.5), mouth='squiggle', eye=1.05, look=(0, -0.3)),
}

def grad_poly(d, pts, c_top, c_bot, ang=1.35, ol=None, w=OL, soft=0.0):
    """fill polygon with a linear gradient (screen space), optional outline"""
    p = d.tp(pts); H_, W_ = d.img.shape[:2]
    x0, y0 = np.floor(p.min(0)).astype(int) - 2; x1, y1 = np.ceil(p.max(0)).astype(int) + 2
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W_, x1), min(H_, y1)
    if xa < xb and ya < yb:
        m = np.zeros((yb - ya, xb - xa), np.uint8)
        cv2.fillPoly(m, [((p - [xa, ya]) * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
        yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
        cx, cy = p.mean(0); L = max(1.0, float(np.abs(p - [cx, cy]).max()))
        t = np.clip(0.5 + ((xx - cx) * math.cos(ang) + (yy - cy) * math.sin(ang)) / (2 * L), 0, 1)[..., None]
        col = np.array(c_top, np.float32) * (1 - t) + np.array(c_bot, np.float32) * t
        a = (m.astype(np.float32) / 255)[..., None]
        roi = d.img[ya:yb, xa:xb].astype(np.float32)
        d.img[ya:yb, xa:xb] = (roi * (1 - a) + col * a).astype(np.uint8)
    if ol is not None: d.poly(pts, None, ol, w)

def circ(cx, cy, rx, ry, n=60, squash=0.0):
    return [(cx + math.cos(a) * rx, cy + math.sin(a) * ry * (1 - squash * max(0, -math.sin(a)))) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]

def limb(d, pts, w=8.5):
    d.line(pts, INK5, w)
    for q in (pts[0], pts[-1]): d.dot(q[0], q[1], w / 2, INK5)

def tube(d, pts, w, col):
    d.line(pts, INK5, w + OL * 1.5)
    for q in (pts[0], pts[-1]): d.dot(q[0], q[1], (w + OL * 1.5) / 2, INK5)
    d.line(pts, col, w)
    for q in (pts[0], pts[-1]): d.dot(q[0], q[1], w / 2, col)

def arm(d, s, ang, ln, bend, col=None):
    r = math.radians(ang); r2 = math.radians(ang + bend)
    e = (s[0] + math.sin(r) * ln * 0.5, s[1] + math.cos(r) * ln * 0.5)
    h = (e[0] + math.sin(r2) * ln * 0.5, e[1] + math.cos(r2) * ln * 0.5)
    if STYLE['arms'] == 'thick' and col is not None:
        tube(d, [s, e, h], 19, col)
        a_ = math.atan2(h[1] - e[1], h[0] - e[0])
        d.ell(h[0] + math.cos(a_ - 1.2) * 12, h[1] + math.sin(a_ - 1.2) * 12, 7, 6, (250, 250, 248), INK5, 3)
        d.ell(h[0], h[1], 15, 14, (250, 250, 248), INK5, 4)
    else:
        limb(d, [s, e, h], 8.5)
        d.ell(h[0], h[1], 11, 10, INK5, None, 0)
    return h

def eye5(H, cx, side, E, look, blink):
    sz = E['eye']; rx, ry = 10 * sz, 13 * sz
    lx, ly = look
    ex, ey = cx + lx * 6, -4 + ly * 6
    if E.get('ring'):
        H.ell(ex, ey, rx + 7, ry + 7, (255, 255, 255), INK5, 3.5)
        H.ell(ex, ey, rx * 0.55, ry * 0.55, INK5, None, 0)
    else:
        H.ell(ex, ey, rx, ry, INK5, None, 0)
        H.dot(ex + rx * 0.35, ey - ry * 0.4, rx * 0.28, (255, 255, 255))
    if E.get('happy') and not blink:
        H.poly([(ex - rx - 3, ey + 3), (ex + rx + 3, ey + 3), (ex + rx + 3, ey + ry + 4), (ex - rx - 3, ey + ry + 4)], HEAD_T, None)
        H.line(bez((ex - rx - 2, ey + 6), (ex, ey - 1), (ex + rx + 2, ey + 6), 8), INK5, 4)
    li = 1.0 if blink else E['lid'][0 if side < 0 else 1]
    if li > 0.02:
        top = ey - ry - (9 if E.get('ring') else 2)
        yl = top + (2 * ry + 4) * li
        t = E['tilt'] * (-side) * 8
        a_ = (ex - rx - 6, yl - t); b_ = (ex + rx + 6, yl + t)
        H.poly([(ex - rx - 7, top - 4), (ex + rx + 7, top - 4), b_, a_], HEAD_T, None)
        H.line([a_, b_], INK5, 6)

def brow5(H, cx, side, E):
    r = E['brow'][0 if side < 0 else 1]; a = E['bang'][0 if side < 0 else 1]
    by = -32 - r * 12
    inner = (cx - side * 17, by + a * 8); outer = (cx + side * 17, by - a * 5)
    dx, dy = outer[0] - inner[0], outer[1] - inner[1]; L = math.hypot(dx, dy) + 1e-6; nx, ny = -dy / L * 6.5, dx / L * 6.5
    H.poly([(inner[0] + nx, inner[1] + ny), (outer[0] + nx * 0.8, outer[1] + ny * 0.8), (outer[0] - nx * 0.8, outer[1] - ny * 0.8), (inner[0] - nx, inner[1] - ny)], INK5, INK5, 3)

def mouth5(H, kind, my=34):
    if kind == 'line': H.line(bez((-11, my), (0, my + 2), (11, my), 6), INK5, 4.5)
    elif kind == 'smirk': H.line(bez((-10, my + 3), (4, my + 4), (15, my - 4), 8), INK5, 4.5)
    elif kind == 'frown': H.line(bez((-12, my + 5), (0, my - 3), (12, my + 5), 8), INK5, 4.5)
    elif kind == 'wavy': H.line([(x, my + 2 + math.sin(x * 0.55) * 3) for x in np.linspace(-13, 13, 12)], INK5, 4)
    elif kind == 'squiggle': H.line([(x, my + math.sin(x * 0.35 + 1) * 4 * x / 13) for x in np.linspace(-12, 12, 12)], INK5, 4)
    elif kind == 'o': H.ell(0, my + 4, 8, 11, C('3a1520'), INK5, 4)
    elif kind == 'open':
        H.poly(list(bez((-14, my - 2), (0, my - 4), (14, my - 2), 6)) + list(bez((14, my - 2), (0, my + 24), (-14, my - 2), 10)), C('3a1520'), INK5, 4)
    elif kind == 'grin':
        H.poly(list(bez((-17, my - 3), (0, my + 1), (17, my - 3), 8)) + list(bez((17, my - 3), (0, my + 18), (-17, my - 3), 10)), C('3a1520'), INK5, 4)
        H.poly([(-13, my - 2), (13, my - 2), (11, my + 3), (-11, my + 3)], (250, 248, 244), None)
    elif kind == 'grit':
        H.poly([(-16, my - 5), (16, my - 5), (14, my + 7), (-14, my + 7)], (250, 248, 244), INK5, 4)
        H.line([(-15, my + 1), (15, my + 1)], INK5, 2)

def hat5(H, kind, o):
    if kind in ('bicorne', 'bicorne_w', 'plume'):
        pts = list(bez((-140, -40), (-96, -168), (0, -150), 16)) + list(bez((0, -150), (96, -168), (140, -40), 16)) + list(bez((140, -40), (0, -86), (-140, -40), 18))
        grad_poly(H, pts, C('3a3646'), C('121018'), 1.2, INK5, OL)
        H.line(bez((-118, -52), (0, -92), (118, -52), 16), C('4a4658'), 5)
        H.line(bez((-70, -132), (-10, -146), (40, -140), 8), C('5a5668'), 4)
        if kind == 'bicorne_w': H.line(bez((-128, -46), (0, -90), (128, -46), 18), C('e3b84a'), 8)
        if kind == 'plume':
            for k in range(-3, 4): H.ell(k * 24, -150 + abs(k) * 6, 19, 15, C('f4f1ea'), INK5, 3)
        H.ell(80, -100, 16, 16, C('2b4aa8'), INK5, 3); H.ell(80, -100, 10.5, 10.5, C('f4f1ea'), None, 0); H.ell(80, -100, 5, 5, C('d9323a'), None, 0)
    elif kind == 'tricorne':
        pts = [(-112, -40), (-76, -116), (0, -100), (76, -116), (112, -40), (0, -62)]
        grad_poly(H, pts, C('5a4632'), C('2e2218'), 1.2, INK5, OL)
        H.line([(-102, -44), (0, -66), (102, -44)], C('c8a04a'), 5)
    elif kind == 'straw':
        grad_poly(H, circ(0, -52, 128, 22), C('f2d68a'), C('c99a3a'), 1.4, INK5, OL)
        crown = [(-58, -56), (58, -56), (46, -118), (-46, -118)]
        grad_poly(H, crown, C('f2d68a'), C('caa04a'), 0.3, INK5, OL * 0.85)
        H.poly([(-58, -60), (58, -60), (55, -76), (-55, -76)], C('c8433a'), INK5, 2.5)
        for k in range(-5, 6): H.line([(k * 10, -78), (k * 8, -114)], C('b8903a'), 2)

def toon5(d, x, y, sc, who='napoleon', emo='neutral', look=None, pose=None, blink=False, flip=1, shadow_on=True):
    o = WHO[who]; E = EMO[emo]; pz = pose or {}
    lk = look if look is not None else E.get('look', (0, 0))
    aL = pz.get('aL', (20, 120)); aR = pz.get('aR', (-20, 120)); elL = pz.get('elL', 10); elR = pz.get('elR', -10)
    lean = pz.get('lean', 0.0); tilt = pz.get('tilt', 0.0) + E.get('chin', 0.0); bob = pz.get('bob', 0.0); step = pz.get('step', 0.0); knee = pz.get('knee', 0.15)
    if shadow_on: shadow(d.sub(Aff(x, y, sc)), 0, 2, 70, 14, 0.5)
    G = d.sub(Aff(x, y - bob * sc, sc, 0, flip))
    st = math.sin(step) * 30 if step else 0
    # thin stick legs with a slight knee bend, small dark shoes / tall boots
    if STYLE['legs'] == 'thick':
        pc = PANTS[who]; bc = BOOT[who]
        for side, ph in ((-1, st), (1, -st)):
            hx = side * 19; fx = side * 20 + ph; fy = -abs(ph) * 0.3
            tube(G, [(hx, -150), (fx, -70 + fy * 0.5), (fx, -14 + fy)], 22, pc)
            G.poly([(fx - 15, -60 + fy), (fx + 15, -60 + fy), (fx + 15, -12 + fy), (fx - 15, -12 + fy)], bc, INK5, OL * 0.7)
            G.ell(fx + 10, -8 + fy, 27, 13, bc, INK5, OL * 0.8)
            G.ell(fx + 4, -14 + fy, 10, 3, shade(bc, 1.8), None, 0)
    for side, ph in (((-1, st), (1, -st)) if STYLE['legs'] != 'thick' else ()):
        hx = side * 16; fx = side * 22 + ph; lift = max(0, -math.cos(step + (0 if side < 0 else math.pi))) * 18 if step else 0
        kx = (hx + fx) / 2 + 10 * knee * (1 + abs(ph) / 30); ky = -82
        limb(G, [(hx, -158), (kx, ky - lift * 0.5), (fx, -8 - lift)], 8.5)
        if o.get('boots'):
            G.line([(lerp(kx, fx, 0.15), lerp(ky, -8 - lift, 0.15) - 6), (fx, -10 - lift)], INK5, 17)
        G.ell(fx + 12, -6 - lift, 20, 9, INK5, None, 0); G.ell(fx + 8, -10 - lift, 7, 2.5, C('5a5468'), None, 0)
    B = G.sub(Aff(0, -150, 1, lean))
    hR = arm(B, (-34, -118), aR[0], aR[1], elR, shade(o['coat'], 0.8))
    # bean torso
    bean = [(math.cos(a) * 58 * (1 + 0.08 * math.sin(a)), -78 + math.sin(a) * 86 * (1 if math.sin(a) > 0 else 0.92)) for a in np.linspace(0, 2 * math.pi, 56, endpoint=False)]
    grad_poly(B, bean, shade(o['coat'], 1.12), shade(o['coat'], 0.72), 0.35, None)
    if o.get('overall'):
        grad_poly(B, [(-34, -110), (34, -110), (40, 8), (-40, 8)], o['front'], shade(o['front'], 0.8), 0.4, INK5, 3)
        B.poly([(-38, -70), (38, -70), (44, 8), (-44, 8)], C('6a8ac0'), INK5, 3)
    else:
        grad_poly(B, [(-16, -158), (16, -158), (22, -40), (0, -24), (-22, -40)], o['front'], shade(o['front'], 0.82), 0.4, INK5, 3)
        for yy in (-130, -104, -78, -52): B.dot(-26, yy, 3.6, GOLD); B.dot(26, yy, 3.6, GOLD)
    if o.get('sash'): B.poly([(-50, -132), (-36, -144), (56, -22), (44, -6)], o['sash'], INK5, 3)
    if o.get('strap'): B.poly([(30, -150), (44, -144), (-40, -10), (-52, -18)], o['strap'], INK5, 3)
    B.poly([(-52, -14), (52, -14), (48, 0), (-48, 0)], shade(o['breeches'], 0.95), INK5, 3)
    B.poly([(-8, -16), (8, -16), (8, 0), (-8, 0)], GOLD, INK5, 2)
    B.poly(bean, None, INK5, OL)
    if o.get('epaul'):
        for s_ in (-1, 1):
            B.ell(s_ * 40, -152, 22, 10, GOLD, INK5, 3)
            for k in range(5): B.line([(s_ * 40 + (k - 2) * 8, -144), (s_ * 40 + (k - 2) * 9, -128)], C('d9a640'), 3)
    hL = arm(B, (34, -118), aL[0], aL[1], elL, o['coat'])
    if pz.get('prop'): pz['prop'](B, hL, hR)
    # big round shaded head
    Hh = B.sub(Aff(0, -232, 1, tilt))
    hp = circ(0, 0, 80, 76)
    grad_poly(Hh, hp, HEAD_T, HEAD_B, 1.25, None)
    hl = circ(-20, -26, 42, 30); grad_poly(Hh, hl, (255, 255, 255), HEAD_T, 1.2, None)
    Hh.poly(hp, None, INK5, OL)
    if o.get('stubble'):
        rr = np.random.default_rng(3)
        for i in range(70):
            a_ = rr.uniform(0.25, math.pi - 0.25); rad = rr.uniform(34, 70)
            Hh.dot(math.cos(a_) * rad, math.sin(a_) * rad * 0.9 + 6, 1.6, C('8a8a96'))
    if o.get('sideburns'):
        for s_ in (-1, 1): Hh.poly([(s_ * 70, -26), (s_ * 80, 6), (s_ * 68, 30), (s_ * 60, -8)], o['sideburns'], INK5, 3)
    if o.get('forelock'):
        Hh.poly([(-46, -58), (-24, -74), (2, -76), (14, -64), (2, -60), (-6, -46), (-12, -60), (-26, -48), (-36, -58)], C('2a1e1a'), INK5, 3)
    for side in (-1, 1):
        eye5(Hh, side * 26, side, E, lk, blink); brow5(Hh, side * 26, side, E)
    Hh.line(bez((-3, 12), (4, 20), (10, 13), 6), C('9aa0b4'), 3.5)            # nose hint
    if o.get('tache'):
        Hh.poly([(-34, 30), (-18, 16), (0, 22), (18, 16), (34, 30), (26, 38), (12, 30), (0, 34), (-12, 30), (-26, 38)], o['tache'], INK5, 3)
    if o.get('beard'):
        grad_poly(Hh, [(-66, 8), (-50, 52), (-14, 76), (14, 76), (50, 52), (66, 8), (40, 26), (16, 40), (-16, 40), (-40, 26)], o['beard'], shade(o['beard'], 0.7), 1.4, INK5, 3)
    if not o.get('tache'): mouth5(Hh, E['mouth'])
    elif E['mouth'] in ('o', 'open', 'grit', 'grin'): mouth5(Hh, E['mouth'], 44)
    if o.get('straw'):
        Hh.line([(10, 36), (60, 26), (74, 16)], C('e8c35a'), 4); Hh.line([(64, 24), (78, 30)], C('e8c35a'), 3)
    if E.get('sweat'): Hh.poly([(76, -44), (86, -20), (76, -12), (66, -20)], C('9fd8ff'), INK5, 3)
    if E.get('lines'):
        for k in range(3):
            a_ = -2.3 + k * 0.45; Hh.line([(math.cos(a_) * 104, math.sin(a_) * 98 - 10), (math.cos(a_) * 130, math.sin(a_) * 122 - 10)], INK5, 5)
    hat5(Hh, o['hat'], o)
    return hL, hR
