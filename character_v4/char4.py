"""FableVerse toon v4: original designs.
Rounder big head, BIG expressive eyes (white eyeballs, black pupils, sliding/tilting lids),
thick tapered brows, filled mouth shapes, chubbier pear body, gloves, chunky boots.
toon4(d, x, y, sc, who, emo='neutral', look=(0,0), pose=dict(...), blink=False, flip=1)"""
import math, numpy as np, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v3zip', 'fableverse_engine', 'v2'))
from rig import C, INK, shade, bez, lerp, clamp, Aff, shadow, GOLD

OL = 7.0
SKIN = C('fdfbf6'); SKIN_S = C('e7e1d6'); PUPIL = C('16111a'); BLUSH = C('f6a7a7'); MOUTH = C('4a1a22'); TONGUE = C('e0727a'); TEETH = (252, 250, 246)

WHO = {
    'napoleon': dict(coat=C('2d4fa8'), pants=C('f2eee4'), boots=C('1d1a22'), hat='bicorne', lapel=C('f4f1ea'), collar=C('c8323a'), epaul=True, hair=C('2a1e1a'), sash=None),
    'berthier': dict(coat=C('25408a'), pants=C('f2eee4'), boots=C('1d1a22'), hat='bicorne_w', lapel=C('e3b84a'), collar=C('e3b84a'), epaul=True, tache=C('4a3424'), sash=C('c8323a')),
    'tsar':     dict(coat=C('f1f2f5'), pants=C('2f4a3a'), boots=C('1d1a22'), hat='plume', lapel=C('3f78c8'), collar=C('3f78c8'), epaul=True, sash=C('3f78c8'), side=C('c9a060')),
    'hunter':   dict(coat=C('3f7a3e'), pants=C('d8c9a2'), boots=C('4a3324'), hat='tricorne', lapel=C('c8a04a'), collar=C('2f5a2e'), tache=C('5a3a22')),
    'farmer':   dict(coat=C('d8573c'), pants=C('3e5f8f'), boots=C('4a3324'), hat='straw', lapel=C('f4eedf'), collar=C('b8432c'), beard=C('8a6a4a')),
}

# emotion presets. lid: 0 open..1 closed (per eye). ltilt: + = inner corner down (angry), - = inner up (sad)
# low: lower-lid push (happy squint). brow: raise (-1..1). bang: + = inner down (angry), - = inner up (worried)
EMO = {
    'neutral':  dict(eye=1.0, lid=(0.18, 0.18), ltilt=0.0, low=0.0, brow=(0.1, 0.1), bang=(0.0, 0.0), mouth='smile', pup=1.0, blush=0.3),
    'happy':    dict(eye=1.0, lid=(0.1, 0.1), ltilt=0.0, low=0.45, brow=(0.5, 0.5), bang=(-0.2, -0.2), mouth='grin', pup=1.0, blush=0.8),
    'proud':    dict(eye=0.95, lid=(0.42, 0.42), ltilt=-0.15, low=0.15, brow=(0.55, 0.55), bang=(-0.1, -0.1), mouth='smirk', pup=1.0, blush=0.4, chin=0.08),
    'smug':     dict(eye=0.95, lid=(0.5, 0.42), ltilt=0.1, low=0.2, brow=(-0.1, 0.55), bang=(0.4, -0.2), mouth='smirk', pup=0.95, blush=0.3, look=(0.5, 0.0)),
    'worried':  dict(eye=1.08, lid=(0.08, 0.08), ltilt=-0.45, low=0.0, brow=(0.55, 0.55), bang=(-0.9, -0.9), mouth='wavy', pup=0.85, sweat=1, blush=0.2),
    'scared':   dict(eye=1.25, lid=(0.0, 0.0), ltilt=-0.3, low=0.0, brow=(0.9, 0.9), bang=(-0.8, -0.8), mouth='scream', pup=0.6, sweat=1, blush=0.0),
    'shocked':  dict(eye=1.35, lid=(0.0, 0.0), ltilt=0.0, low=0.0, brow=(1.0, 1.0), bang=(-0.2, -0.2), mouth='o', pup=0.45, shock=1, blush=0.0),
    'angry':    dict(eye=0.95, lid=(0.32, 0.32), ltilt=0.55, low=0.15, brow=(-0.45, -0.45), bang=(1.0, 1.0), mouth='grit', pup=0.85, vein=1, blush=0.6),
    'sad':      dict(eye=1.0, lid=(0.35, 0.35), ltilt=-0.55, low=0.0, brow=(0.3, 0.3), bang=(-1.0, -1.0), mouth='frown', pup=1.0, tears=1, look=(0.0, 0.4)),
    'deadpan':  dict(eye=0.9, lid=(0.52, 0.52), ltilt=0.0, low=0.1, brow=(-0.05, -0.05), bang=(0.0, 0.0), mouth='flat', pup=0.9, blush=0.0),
    'excited':  dict(eye=1.2, lid=(0.0, 0.0), ltilt=0.0, low=0.3, brow=(0.9, 0.9), bang=(-0.3, -0.3), mouth='open', pup=1.15, sparkle=1, blush=0.9),
    'sly':      dict(eye=0.95, lid=(0.5, 0.25), ltilt=0.35, low=0.3, brow=(-0.3, 0.6), bang=(0.7, -0.2), mouth='smirk', pup=0.9, look=(0.6, 0.0), blush=0.3),
    'confused': dict(eye=1.05, lid=(0.12, 0.35), ltilt=0.0, low=0.0, brow=(0.85, -0.25), bang=(-0.4, 0.5), mouth='squiggle', pup=0.9, look=(0.0, -0.3), blush=0.1),
}

def tube(d, pts, w, col):
    d.line(pts, INK, w + OL * 1.5)
    for p in (pts[0], pts[-1]): d.dot(p[0], p[1], (w + OL * 1.5) / 2, INK)
    d.line(pts, col, w)
    for p in (pts[0], pts[-1]): d.dot(p[0], p[1], w / 2, col)

def arm(d, a, ang, ln, bend, col, cuff):
    r = math.radians(ang); r2 = math.radians(ang + bend)
    e = (a[0] + math.sin(r) * ln * 0.5, a[1] + math.cos(r) * ln * 0.5)
    h = (e[0] + math.sin(r2) * ln * 0.5, e[1] + math.cos(r2) * ln * 0.5)
    tube(d, [a, e, h], 19, col)
    cx = lerp(e[0], h[0], 0.82); cy = lerp(e[1], h[1], 0.82)
    d.ell(cx, cy, 13, 9, cuff, INK, 3, ang=math.atan2(h[1] - e[1], h[0] - e[0]) + math.pi / 2)
    # glove mitt + thumb
    ang_h = math.atan2(h[1] - e[1], h[0] - e[0])
    d.ell(h[0] + math.cos(ang_h - 1.2) * 12, h[1] + math.sin(ang_h - 1.2) * 12, 7, 6, (250, 250, 248), INK, 3)
    d.ell(h[0], h[1], 15, 14, (250, 250, 248), INK, 4)
    return h

def head_pts(rx=74, ry=70, n=56):
    out = []
    for a in np.linspace(0, 2 * math.pi, n, endpoint=False):
        s = math.sin(a)
        k = 1 - 0.06 * max(0, -s)                       # slightly narrower top
        jaw = 1 + 0.05 * max(0, s)                      # soft full cheeks / jaw
        out.append((math.cos(a) * rx * k * jaw, s * ry * (1.0 if s > 0 else 1.02)))
    return out

def eye(H, cx, side, E, look, blink):
    sz = E['eye']; rx, ry = 16 * sz, 19 * sz
    H.ell(cx, 0, rx, ry, (255, 255, 255), INK, 4)
    lx, ly = look
    pr = 9.5 * E['pup'] * (1 if sz <= 1.1 else 0.9)
    px, py = cx + lx * rx * 0.42, ly * ry * 0.42 + 1
    H.ell(px, py, pr, pr * 1.1, PUPIL, None, 0)
    H.dot(px + pr * 0.38, py - pr * 0.45, max(2.0, pr * 0.36), (255, 255, 255))
    H.dot(px - pr * 0.35, py + pr * 0.4, max(1.0, pr * 0.16), (255, 255, 255))
    if E.get('sparkle'):
        H.dot(px - pr * 0.1, py - pr * 0.05, pr * 0.22, (255, 255, 255))
    li = 1.0 if blink else E['lid'][0 if side < 0 else 1]
    tilt = E['ltilt'] * (-side)                         # inner corner is toward x=0
    if li > 0.02:
        yl = -ry + 2 * ry * li
        # lid cap in skin colour, edge tilted
        a_ = (cx - rx - 3, yl - tilt * 9); b_ = (cx + rx + 3, yl + tilt * 9)
        H.poly([(cx - rx - 4, -ry - 6), (cx + rx + 4, -ry - 6), b_, a_], SKIN, None)
        H.line([a_, b_], INK, 5.5)
    lo = 1.0 if blink else E['low']
    if lo > 0.02:
        yb = ry - 2 * ry * lo * 0.6
        H.poly([(cx - rx - 4, ry + 6), (cx + rx + 4, ry + 6), (cx + rx + 3, yb), (cx - rx - 3, yb)], SKIN, None)
        H.line(bez((cx - rx, yb + 2), (cx, yb - 5), (cx + rx, yb + 2), 8), INK, 3.5)
    if blink:
        H.line(bez((cx - rx, 2), (cx, 9), (cx + rx, 2), 8), INK, 5)
    # re-stroke the eyeball outline for crisp shape where lids don't cover it
    return rx, ry

def brow(H, cx, side, E, ry):
    raise_ = E['brow'][0 if side < 0 else 1]; bang = E['bang'][0 if side < 0 else 1]
    by = -ry - 16 - raise_ * 12
    inner = (cx - side * 18, by + bang * 9); outer = (cx + side * 18, by - bang * 6 + 2)
    # tapered thick brow (thicker at inner end)
    dx, dy = outer[0] - inner[0], outer[1] - inner[1]; L = math.hypot(dx, dy) + 1e-6; nx, ny = -dy / L, dx / L
    H.poly([(inner[0] + nx * 6, inner[1] + ny * 6), (outer[0] + nx * 3, outer[1] + ny * 3), (outer[0] - nx * 2, outer[1] - ny * 2), (inner[0] - nx * 6, inner[1] - ny * 6)], INK, INK, 2)

def mouth(H, kind, my=36):
    if kind == 'smile':
        H.line(bez((-18, my - 4), (0, my + 9), (18, my - 4), 12), INK, 5)
    elif kind == 'smirk':
        H.line(bez((-16, my + 3), (6, my + 6), (22, my - 8), 12), INK, 5)
        H.line([(20, my - 9), (25, my - 4)], INK, 4)
    elif kind == 'flat':
        H.line([(-15, my + 2), (15, my + 2)], INK, 5)
    elif kind == 'frown':
        H.line(bez((-17, my + 8), (0, my - 6), (17, my + 8), 12), INK, 5)
    elif kind == 'wavy':
        pts = [(x, my + 3 + math.sin(x * 0.42) * 4) for x in np.linspace(-18, 18, 14)]
        H.line(pts, INK, 4.5)
    elif kind == 'squiggle':
        pts = [(x, my + 2 + math.sin(x * 0.3 + 1) * 5 * (x / 18)) for x in np.linspace(-16, 16, 14)]
        H.line(pts, INK, 4.5)
    elif kind == 'o':
        H.ell(0, my + 6, 10, 13, MOUTH, INK, 4.5); H.ell(0, my + 13, 6, 4, TONGUE, None, 0)
    elif kind == 'grin':
        top = list(bez((-24, my - 4), (0, my + 2), (24, my - 4), 10)); bot = list(bez((24, my - 4), (0, my + 28), (-24, my - 4), 14))
        H.poly(top + bot, MOUTH, INK, 4.5)
        H.poly([(-19, my - 3), (19, my - 3), (16, my + 4), (-16, my + 4)], TEETH, None)
        H.ell(0, my + 15, 10, 5, TONGUE, None, 0)
    elif kind == 'open':
        H.poly(list(bez((-20, my - 2), (0, my - 6), (20, my - 2), 8)) + list(bez((20, my - 2), (0, my + 34), (-20, my - 2), 14)), MOUTH, INK, 4.5)
        H.ell(0, my + 18, 11, 6, TONGUE, None, 0)
    elif kind == 'scream':
        H.poly([(-18, my - 4), (18, my - 4), (14, my + 26), (-14, my + 26)], MOUTH, INK, 4.5)
        H.poly([(-16, my - 3), (16, my - 3), (15, my + 3), (-15, my + 3)], TEETH, None)
        H.ell(0, my + 20, 9, 5, TONGUE, None, 0)
    elif kind == 'grit':
        H.poly([(-21, my - 6), (21, my - 6), (19, my + 9), (-19, my + 9)], TEETH, INK, 4.5)
        H.line([(-20, my + 1), (20, my + 1)], INK, 2.5)
        for x in (-10, 0, 10): H.line([(x, my - 5), (x, my + 8)], INK, 2)

def hat(H, kind, o):
    if kind in ('bicorne', 'bicorne_w', 'plume'):
        hb = C('1c1a22')
        pts = list(bez((-132, -40), (-90, -150), (0, -132), 14)) + list(bez((0, -132), (90, -150), (132, -40), 14)) + list(bez((132, -40), (0, -78), (-132, -40), 16))
        H.poly(pts, hb, INK, OL)
        H.line(bez((-110, -52), (0, -84), (110, -52), 14), C('3e3a4a'), 5)
        H.line(bez((-60, -118), (0, -128), (50, -122), 8), C('3e3a4a'), 4)
        if kind == 'bicorne_w': H.line(bez((-122, -46), (0, -82), (122, -46), 16), o['lapel'], 8)
        if kind == 'plume':
            for k in range(-3, 4): H.ell(k * 22, -138 + abs(k) * 6, 17, 14, C('f4f1ea'), INK, 3)
        H.ell(72, -92, 15, 15, C('2b4aa8'), INK, 3); H.ell(72, -92, 10, 10, C('f4f1ea'), None, 0); H.ell(72, -92, 5, 5, C('d9323a'), None, 0)
    elif kind == 'tricorne':
        H.poly([(-104, -44), (-70, -112), (0, -98), (70, -112), (104, -44), (0, -64)], C('3a2a1e'), INK, OL)
        H.line([(-96, -48), (0, -68), (96, -48)], o['lapel'], 5)
    elif kind == 'straw':
        H.ell(0, -52, 112, 20, C('e8c35a'), INK, OL)
        H.poly([(-54, -54), (54, -54), (42, -110), (-42, -110)], C('e8c35a'), INK, OL * 0.85)
        H.poly([(-54, -58), (54, -58), (52, -72), (-52, -72)], C('d94b3c'), None)
        for k in range(-4, 5): H.line([(k * 10, -60), (k * 8, -106)], C('c9a040'), 2)

def toon4(d, x, y, sc, who='napoleon', emo='neutral', look=None, pose=None, blink=False, flip=1, shadow_on=True):
    o = WHO[who]; E = dict(EMO[emo]); pz = pose or {}
    lk = look if look is not None else E.get('look', (0.0, 0.0))
    aL = pz.get('aL', (22, 104)); aR = pz.get('aR', (-22, 104)); elL = pz.get('elL', 0); elR = pz.get('elR', 0)
    lean = pz.get('lean', 0.0); tilt = pz.get('tilt', 0.0) + E.get('chin', 0) * 0; bob = pz.get('bob', 0.0); step = pz.get('step', 0.0); sq = pz.get('squash', 0.0)
    if shadow_on: shadow(d.sub(Aff(x, y, sc)), 0, 2, 78, 16, 0.5)
    G = d.sub(Aff(x, y - bob * sc, sc, 0, flip)).sub(np.array([[1 + sq * 0.5, 0, 0], [0, 1 - sq, 0], [0, 0, 1]], float))
    st = math.sin(step) * 20 if step else 0
    for side, ph in ((-1, st), (1, -st)):                # legs + chunky boots
        hx = side * 19; fx = side * 20 + ph; fy = -abs(ph) * 0.3
        tube(G, [(hx, -122), (fx, -62 + fy * 0.5), (fx, -14 + fy)], 22, o['pants'])
        G.poly([(fx - 15, -58 + fy), (fx + 15, -58 + fy), (fx + 15, -12 + fy), (fx - 15, -12 + fy)], o['boots'], INK, OL * 0.7)
        G.ell(fx + 10, -8 + fy, 27, 13, o['boots'], INK, OL * 0.8)
        G.ell(fx + 4, -14 + fy, 10, 3, shade(o['boots'], 1.8), None, 0)
    B = G.sub(Aff(0, -118, 1, lean))
    hR = arm(B, (-38, -116), aR[0], aR[1], elR, shade(o['coat'], 0.82), o['lapel'])
    # pear torso with coat tails
    body = [(-50, 6), (-56, -30), (-52, -80), (-44, -112), (-30, -128), (30, -128), (44, -112), (52, -80), (56, -30), (50, 6), (0, 12)]
    B.poly(body, o['coat'], INK, OL)
    B.poly([(18, -122), (34, -122), (48, -86), (54, -30), (48, 4), (26, 8)], shade(o['coat'], 0.84), None)
    B.poly([(-50, 6), (-62, 24), (-36, 20)], shade(o['coat'], 0.9), INK, 4); B.poly([(50, 6), (62, 24), (36, 20)], shade(o['coat'], 0.8), INK, 4)
    B.poly(body, None, INK, OL)
    B.poly([(-26, -126), (0, -60), (26, -126), (14, -128), (0, -96), (-14, -128)], o['lapel'], INK, 3.5)
    B.poly([(-12, -124), (12, -124), (0, -98)], (250, 248, 242), None)
    for yy in (-80, -56, -32): B.dot(-14, yy, 4, GOLD); B.dot(14, yy, 4, GOLD)
    if o.get('sash'): B.poly([(-46, -112), (-30, -122), (52, -20), (46, -4)], o['sash'], INK, 3.5)
    B.poly([(-50, -16), (50, -16), (50, -2), (-50, -2)], o['pants'] if who in ('napoleon', 'berthier') else C('4a3a2a'), INK, 3.5)
    B.poly([(-9, -18), (9, -18), (9, 0), (-9, 0)], GOLD, INK, 2.5)
    if o.get('epaul'):
        for s_ in (-1, 1):
            B.ell(s_ * 40, -122, 20, 9, GOLD, INK, 3.5)
            for k in range(5): B.line([(s_ * 40 + (k - 2) * 8, -114), (s_ * 40 + (k - 2) * 9, -100)], GOLD, 3.5)
    B.poly([(-26, -128), (26, -128), (22, -142), (-22, -142)], o['collar'], INK, 3.5)
    hL = arm(B, (38, -116), aL[0], aL[1], elL, o['coat'], o['lapel'])
    if pz.get('prop'): pz['prop'](B, hL, hR)
    # head
    Hh = B.sub(Aff(0, -222, 1.2, tilt))
    hp = head_pts()
    Hh.poly(hp, SKIN_S, INK, OL)
    Hh.poly([(px * 0.9 - 7, py * 0.92 - 5) for px, py in hp], SKIN, None)
    Hh.poly(hp, None, INK, OL)
    if o.get('hair'):
        Hh.poly([(-50, -48), (-30, -64), (-6, -66), (16, -62), (8, -50), (-2, -58), (-12, -42), (-22, -54), (-36, -40)], o['hair'], INK, 3)
    if o.get('side'):
        for s_ in (-1, 1): Hh.poly([(s_ * 66, -20), (s_ * 74, 10), (s_ * 62, 26), (s_ * 58, -10)], o['side'], INK, 3)
    if E.get('blush', 0) > 0.05:
        for s_ in (-1, 1): Hh.ell(s_ * 40, 24, 13, 7, BLUSH, None, 0)
    for side in (-1, 1):
        rx, ry = eye(Hh, side * 27, side, E, lk, blink)
        brow(Hh, side * 27, side, E, ry)
    Hh.line(bez((-4, 12), (2, 18), (8, 13), 6), shade(SKIN, 0.7), 3)    # tiny nose
    if o.get('tache'):
        Hh.poly([(-28, 28), (-10, 20), (0, 25), (10, 20), (28, 28), (16, 34), (0, 30), (-16, 34)], o['tache'], INK, 3)
    if o.get('beard'):
        Hh.poly([(-56, 10), (-40, 48), (0, 70), (40, 48), (56, 10), (36, 34), (14, 44), (-14, 44), (-36, 34)], o['beard'], INK, 3)
    mouth(Hh, E['mouth'])
    if E.get('sweat'):
        Hh.poly([(70, -40), (80, -16), (70, -8), (60, -16)], C('9fd8ff'), INK, 3)
    if E.get('tears'):
        for s_ in (-1, 1): Hh.poly([(s_ * 26, 20), (s_ * 31, 38), (s_ * 26, 44), (s_ * 21, 38)], C('9fd8ff'), INK, 2.5)
    if E.get('vein'):
        for a_ in (0, 1.57, 3.14, 4.71):
            Hh.line(bez((50 + math.cos(a_) * 4, -50 + math.sin(a_) * 4), (50 + math.cos(a_ + 0.4) * 12, -50 + math.sin(a_ + 0.4) * 12), (50 + math.cos(a_) * 16, -50 + math.sin(a_) * 16), 5), C('d9323a'), 4)
    if E.get('shock'):
        for k in range(3):
            a_ = -2.3 + k * 0.45
            Hh.line([(math.cos(a_) * 96, math.sin(a_) * 92 - 12), (math.cos(a_) * 122, math.sin(a_) * 118 - 12)], INK, 5)
    hat(Hh, o['hat'], o)
    return hL, hR
