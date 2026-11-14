import numpy as np, cv2, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

def C(h):
    h = h.lstrip('#'); return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))  # BGR

INK = C('3a2236')

def smooth(x):
    x = min(1, max(0, x)); return x * x * x * (x * (x * 6 - 15) + 10)
def eout(x):
    x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def back(x, s=1.7):
    x = min(1, max(0, x)); x -= 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0, b=1): return max(a, min(b, x))

def Aff(tx=0, ty=0, s=1, rot=0, fx=1, sy=None):
    sy = s if sy is None else sy
    c, sn = math.cos(rot), math.sin(rot)
    return np.array([[c * s * fx, -sn * sy, tx], [sn * s * fx, c * sy, ty], [0, 0, 1]], float)

def ellpts(cx, cy, rx, ry, ang=0, n=28):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    x = rx * np.cos(t); y = ry * np.sin(t)
    c, s = math.cos(ang), math.sin(ang)
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], 1)

class D:
    """Drawer: design coords -> screen via 3x3 M. k = pixel scale of 1 design unit."""
    def __init__(s, img, M):
        s.img = img; s.M = M
        s.k = math.sqrt(abs(np.linalg.det(M[:2, :2])))
    def sub(s, L): return D(s.img, s.M @ L)
    def tp(s, pts):
        p = np.asarray(pts, float).reshape(-1, 2)
        return p @ s.M[:2, :2].T + s.M[:2, 2]
    def _i(s, pts): return (s.tp(pts) * 16).astype(np.int32)
    def poly(s, pts, fill=None, ol=INK, w=5):
        p = s._i(pts)
        if fill is not None: cv2.fillPoly(s.img, [p], fill, cv2.LINE_AA, shift=4)
        if ol is not None and w > 0:
            cv2.polylines(s.img, [p], True, ol, max(1, int(round(w * s.k))), cv2.LINE_AA, shift=4)
    def ell(s, cx, cy, rx, ry, fill=None, ol=INK, w=5, ang=0, n=30):
        s.poly(ellpts(cx, cy, rx, ry, ang, n), fill, ol, w)
    def line(s, pts, col=INK, w=5, closed=False):
        cv2.polylines(s.img, [s._i(pts)], closed, col, max(1, int(round(w * s.k))), cv2.LINE_AA, shift=4)
    def tube(s, pts, w, col, ol=INK, ow=5):
        p = s._i(pts)
        if ol is not None:
            cv2.polylines(s.img, [p], False, ol, max(1, int(round((w + 2 * ow) * s.k))), cv2.LINE_AA, shift=4)
            for q in (p[0], p[-1]):
                cv2.circle(s.img, tuple(q), int(round((w / 2 + ow) * s.k * 16)), ol, -1, cv2.LINE_AA, shift=4)
        cv2.polylines(s.img, [p], False, col, max(1, int(round(w * s.k))), cv2.LINE_AA, shift=4)
        for q in (p[0], p[-1]):
            cv2.circle(s.img, tuple(q), int(round(w / 2 * s.k * 16)), col, -1, cv2.LINE_AA, shift=4)
    def dot(s, x, y, r, col):
        q = s._i([(x, y)])[0]
        cv2.circle(s.img, tuple(q), max(1, int(round(r * s.k * 16))), col, -1, cv2.LINE_AA, shift=4)

def shade(c, f):
    return tuple(int(clamp(v * f, 0, 255)) for v in c)

def celpoly(d, pts, col, w=5, light=(-6, -8)):
    """dark base + lighter inset copy (cel look)"""
    pts = np.asarray(pts, float)
    d.poly(pts, shade(col, 0.78), INK, w)
    c = pts.mean(0)
    p2 = (pts - c) * 0.86 + c + np.array(light)
    d.poly(p2, col, None)

def bez(p0, p1, p2, n=12):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(np.array, (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2

# ---------------- HUMAN ----------------
SKIN = C('f6d9bd'); KHAKI = C('a8915e'); KHAKI2 = C('8c7748'); BOOT = C('4a3324')
HATC = C('9c8253'); BLUE = C('4f7cc4'); STRAW = C('e8c35a'); RED = C('d94b3c'); GOLD = C('e3b84a')

OUT = {
 'soldier': dict(body=C('a38c58'), pants=C('8f7a4a'), hat='slouch', belt=C('6b4a2a'), puttee=C('9a8656')),
 'farmer': dict(body=C('4f7cc4'), pants=C('3e5f8f'), hat='straw', belt=C('3c2a1c'), puttee=None, skin=C('f0c39c'), stubble=True),
 'officer': dict(body=C('a8915e'), pants=C('8c7748'), hat='peak', belt=C('5b3d22'), tache=True, puttee=C('6b4a2a')),
 'troffea': dict(body=C('3f6fb8'), pants=C('3f6fb8'), hat='coif', belt=C('f2ead8'), puttee=None, robe=C('3f6fb8'), apron=C('f4eedf'), fem=True, skin=C('f6d6ba')),
 'peasant_w': dict(body=C('b8543c'), pants=C('b8543c'), hat='coif', belt=C('e9dfc8'), puttee=None, robe=C('b8543c'), apron=C('e9dfc8'), fem=True, skin=C('f3cfb0')),
 'peasant_w2': dict(body=C('5f8a4a'), pants=C('5f8a4a'), hat='kerchief', belt=C('e9dfc8'), puttee=None, robe=C('5f8a4a'), apron=None, fem=True, skin=C('e9c19c')),
 'peasant_m': dict(body=C('8a5a34'), pants=C('6b6b4a'), hat='hood', belt=C('3c2a1c'), puttee=None, tunic=True, skin=C('f0c8a6')),
 'peasant_m2': dict(body=C('4e6e8a'), pants=C('7a5a3a'), hat='beret', belt=C('3c2a1c'), puttee=None, tunic=True, skin=C('dcae88')),
 'doctor': dict(body=C('2b2a33'), pants=C('2b2a33'), hat='doccap', belt=C('7a6a50'), puttee=None, robe=C('2b2a33'), beard=True, specs=True, skin=C('f2d2b6')),
 'musician': dict(body=C('d0453a'), pants=C('e6b64a'), hat='feather', belt=C('5a3a20'), puttee=None, tunic=True, stripes=C('e6b64a'), skin=C('f2cdaa')),
 'council': dict(body=C('a3202a'), pants=C('a3202a'), hat='furcap', belt=C('e0b84a'), puttee=None, robe=C('a3202a'), chain=True, tache=True, skin=C('f0cfb2')),
 'priest': dict(body=C('6b4a32'), pants=C('6b4a32'), hat='tonsure', belt=C('e0d0a0'), puttee=None, robe=C('6b4a32'), skin=C('f2d0b0')),
 'napoleon': dict(body=C('2a3d78'), pants=C('f1ece0'), hat='bicorne', belt=C('f1ece0'), puttee=None, mil=True, hair=C('3a2a20'), boot=C('1e1a22'), skin=C('f3d6bb')),
 'berthier': dict(body=C('2f4a8a'), pants=C('f1ece0'), hat='plume', belt=C('e3b84a'), puttee=None, mil=True, tache=True, boot=C('1e1a22'), skin=C('f0cfb2')),
 'tsar': dict(body=C('2f5a3e'), pants=C('f1ece0'), hat='plume', belt=C('e3b84a'), puttee=None, mil=True, lapel=C('c23a3a'), hair=C('c9a060'), boot=C('1e1a22'), skin=C('f4dcc4')),
 'hunter': dict(body=C('3f6a3a'), pants=C('cdbb8a'), hat='tricorne', belt=C('5a3a20'), puttee=None, boot=C('3a2a20'), skin=C('efc9a6')),
 'hunter2': dict(body=C('8a3a2e'), pants=C('cdbb8a'), hat='tricorne', belt=C('5a3a20'), puttee=None, boot=C('3a2a20'), skin=C('dcae88'), tache=True),
}

def shadow(d, x, y, rx, ry, k=0.55):
    """soft contact shadow: darken ellipse region in place"""
    p = d.tp(ellpts(x, y, rx, ry, 0, 24))
    x0, y0 = np.floor(p.min(0)).astype(int) - 2; x1, y1 = np.ceil(p.max(0)).astype(int) + 2
    H_, W_ = d.img.shape[:2]
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W_, x1), min(H_, y1)
    if xa >= xb or ya >= yb: return
    m = np.zeros((yb - ya, xb - xa), np.uint8)
    cv2.fillPoly(m, [((p - [xa, ya]) * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4)
    kk = max(3, int((x1 - x0) * 0.12) | 1)
    m = cv2.GaussianBlur(m, (kk, kk), 0).astype(np.float32)[..., None] / 255.0
    roi = d.img[ya:yb, xa:xb].astype(np.float32)
    d.img[ya:yb, xa:xb] = (roi * (1 - m * (1 - k))).astype(np.uint8)

def limb(d, pts, w, col, ow=4.5):
    d.tube(pts, w, col, INK, ow)
    p = np.asarray(pts, float)
    d.line(p + [-w * 0.18, -w * 0.12], shade(col, 1.12), w * 0.3)

def hand(d, x, y, r=15, ang=0.0, col=None):
    col = col or SKIN
    d.ell(x + math.cos(ang) * r * 0.8, y + math.sin(ang) * r * 0.8 - 3, r * 0.45, r * 0.35, col, INK, 3.5, ang=ang)
    d.ell(x, y, r, r * 0.92, col, INK, 4)
    d.ell(x - r * 0.3, y - r * 0.3, r * 0.3, r * 0.2, shade(col, 1.08), None, 0)

def human(d, x, y, sc=1.0, out='soldier', face='open', mouth='smile', flip=1,
          armL=(20, 70), armR=(-20, 70), step=0.0, lean=0.0, tilt=0.0, bob=0.0,
          brow=0.0, prop=None, sweat=False, soot=False, look=(0, 0), shadow_on=True, var=0, shoes=None, kick=0.0, flare=0.0):
    o = OUT[out]
    HSK = o.get('skin', SKIN) if var not in (1, 2) else (C('f1cfae') if var == 1 else C('e2b48c'))
    if shadow_on: shadow(d.sub(Aff(x, y, sc)), 0, 2, 70, 16)
    L = d.sub(Aff(x, y - bob, sc, 0, flip))
    st = math.sin(step) * 22 if step else 0
    # legs
    for side, ph in ((-1, st), (1, -st)):
        hx = side * 17; fx = side * 19 + ph; fy = -abs(ph) * 0.25 if step else 0
        if kick > 0 and side == 1:
            fx = side * 19 + 70 * kick; fy = -80 * kick
        limb(L, [(hx, -112), ((hx + fx) / 2, -60), (fx, -14 + fy)], 27, o['pants'])
        if o['puttee'] is not None:
            for k in range(4):
                yy = -18 - k * 11 + fy
                L.line([(fx - 13, yy), (fx + 13, yy - 6)], shade(o['puttee'], 0.8), 3)
            L.poly([(fx - 14, -14 + fy), (fx + 14, -14 + fy), (fx + 14, -58 + fy), (fx - 14, -58 + fy)], None, INK, 0)
        sc_ = shoes if shoes is not None else o.get('boot', BOOT)
        L.poly([(fx - 16, -16 + fy), (fx + 30, -10 + fy), (fx + 32, 2 + fy), (fx - 18, 2 + fy)], sc_, INK, 4)
        L.line([(fx - 14, -3 + fy), (fx + 30, -3 + fy)], shade(sc_, 1.4), 3)
        if shoes is not None:
            L.ell(fx + 6, -10 + fy, 8, 3, shade(sc_, 1.5), None, 0)
    if o.get('robe') is not None:
        sw_ = st * 0.6; fl_ = flare * 40
        L.poly([(-42, -112), (42, -112), (66 + sw_ + fl_, -16 - fl_ * 0.5), (40 + sw_ + fl_ * 0.6, -10 - fl_ * 0.2), (0 + sw_, -14), (-40 + sw_ - fl_ * 0.6, -10 - fl_ * 0.2), (-66 + sw_ - fl_, -16 - fl_ * 0.5)], o['robe'], INK, 5)
        L.line([(-30, -100), (-44 + sw_, -22)], shade(o['robe'], 0.82), 4); L.line([(24, -100), (40 + sw_, -22)], shade(o['robe'], 0.82), 4)
        if o.get('apron'):
            L.poly([(-26, -110), (26, -110), (34 + sw_, -30), (-34 + sw_, -30)], o['apron'], INK, 4)
    if o.get('tunic'):
        L.poly([(-48, -112), (48, -112), (56, -64), (0, -58), (-56, -64)], o['body'], INK, 5)
    B = L.sub(Aff(0, -110, 1, lean))
    def arm(side, a):
        ang, ln = a
        r = math.radians(ang)
        sx = side * 40; sy = -84
        ex = sx + math.sin(r) * ln * 0.55; ey = sy + math.cos(r) * ln * 0.55
        hx = sx + math.sin(r) * ln; hy = sy + math.cos(r) * ln
        limb(B, [(sx, sy), (ex, ey), (hx, hy)], 23, o['body'])
        cx_, cy_ = hx - (hx - ex) * 0.18, hy - (hy - ey) * 0.18
        B.ell(cx_, cy_, 13, 8, shade(o['body'], 0.85), INK, 3, ang=math.atan2(hy - ey, hx - ex) + math.pi / 2)
        hand(B, hx, hy, 15, math.atan2(hy - ey, hx - ex) - 0.6 * side, HSK)
        return hx, hy
    hR = arm(-1, armR)
    body = [(-44, 0), (-50, -40), (-44, -80), (-30, -100), (30, -100), (44, -80), (50, -40), (44, 0)]
    celpoly(B, body, o['body'])
    if out in ('soldier', 'officer'):
        # pockets
        for sx in (-22, 22):
            B.poly([(sx - 14, -76), (sx + 14, -76), (sx + 14, -50), (sx - 14, -50)], shade(o['body'], 0.92), INK, 3)
            B.poly([(sx - 16, -80), (sx + 16, -80), (sx + 14, -70), (sx - 14, -70)], shade(o['body'], 0.8), INK, 3)
            B.dot(sx, -73, 2.6, GOLD)
        B.poly([(-26, -100), (0, -86), (26, -100), (14, -104), (0, -95), (-14, -104)], shade(o['body'], 0.75), INK, 3)  # collar
        for yy in (-62, -42, -24): B.dot(0, yy, 3.4, GOLD)
        if out == 'officer':
            B.line([(-34, -96), (34, -10)], C('5a3a20'), 7)
            B.dot(-20, -96, 5, RED); B.dot(20, -96, 5, RED)
    if o.get('stripes') is not None:
        for i in range(-3, 4): B.line([(i * 14, -98), (i * 14, -2)], o['stripes'], 6)
    if o.get('mil'):
        lap = o.get('lapel', C('f1ece0'))
        B.poly([(-30, -100), (0, -54), (30, -100), (18, -102), (0, -72), (-18, -102)], lap, INK, 3)
        B.poly([(-14, -98), (14, -98), (0, -74)], C('f8f4ea'), None)
        for yy in (-46, -30): B.dot(0, yy, 3.6, GOLD)
        for sd in (-1, 1):
            B.ell(sd * 40, -97, 22, 9, GOLD, INK, 3)
            for k in range(5): B.line([(sd * 40 + (k - 2) * 8, -90), (sd * 40 + (k - 2) * 9, -76)], GOLD, 3)
        B.poly([(-22, -100), (22, -100), (18, -112), (-18, -112)], o.get('collar', RED), INK, 3)
    if o.get('fem'):
        B.poly([(-26, -100), (0, -78), (26, -100)], C('f4eedf'), INK, 3)
    if o.get('robe') is not None and not o.get('fem'):
        B.poly([(-20, -100), (0, -84), (20, -100)], shade(o['body'], 0.7), INK, 3)
    if o.get('chain'):
        B.line(bez((-36, -96), (0, -40), (36, -96), 12), C('e3b84a'), 7)
        B.ell(0, -48, 12, 12, C('e3b84a'), INK, 3)
        B.poly([(-50, -100), (50, -100), (46, -84), (-46, -84)], C('f2ead8'), INK, 3)
    if out == 'priest':
        B.line(bez((-44, -14), (0, -4), (44, -14), 8), C('e0d0a0'), 6); B.line([(10, -8), (14, 40)], C('e0d0a0'), 5)
    if out == 'farmer':
        for i in range(-3, 4): B.line([(i * 13, -98), (i * 13 + 2, -2)], C('3d63a8'), 3)
        for j in range(1, 6): B.line([(-46, -j * 17), (46, -j * 17)], C('3d63a8'), 3)
        B.line([(-26, -98), (-24, 0)], C('7a5530'), 7); B.line([(26, -98), (24, 0)], C('7a5530'), 7)
    B.poly([(-47, -16), (47, -16), (47, -2), (-47, -2)], o['belt'], INK, 3)
    B.poly([(-8, -18), (8, -18), (8, 0), (-8, 0)], GOLD, INK, 2)
    hL = arm(1, armL)
    if prop: prop(B, hL, hR)
    # neck
    sk = o.get('skin', SKIN)
    if var == 1: sk = C('f1cfae')
    if var == 2: sk = C('e2b48c')
    B.poly([(-15, -100), (15, -100), (13, -114), (-13, -114)], shade(sk, 0.8), INK, 3)
    Hh = B.sub(Aff(0, -150, 1, tilt))
    # ears
    for sd in (-1, 1):
        Hh.ell(sd * 57, 8, 11, 16, shade(sk, 0.92), INK, 4)
        Hh.line(bez((sd * 55, 0), (sd * 61, 8), (sd * 55, 16), 6), shade(sk, 0.7), 2.5)
    # head: slightly longer jaw
    head = [(math.cos(a_) * 58 * (1 - 0.06 * max(0, math.sin(a_))), math.sin(a_) * (54 if math.sin(a_) < 0 else 62)) for a_ in np.linspace(0, 2 * math.pi, 44, endpoint=False)]
    Hh.poly(head, shade(sk, 0.84), INK, 5)
    Hh.poly([(x_ * 0.9 - 4, y_ * 0.9 - 5) for x_, y_ in head], sk, None)
    # soft forehead shade under the hat (subtle)
    if o['hat'] in ('slouch', 'peak', 'straw'):
        Hh.poly([(math.cos(a_) * 52, math.sin(a_) * 48) for a_ in np.linspace(math.pi * 1.1, math.pi * 1.9, 14)] + [(36, -32), (0, -28), (-36, -32)], shade(sk, 0.92), None)
    Hh.ell(-31, 20, 11, 6.5, C('f0aa98'), None, 0); Hh.ell(31, 20, 11, 6.5, C('f0aa98'), None, 0)
    if o.get('stubble') or var == 3:
        Hh.poly([(math.cos(a_) * 50, math.sin(a_) * 56) for a_ in np.linspace(0.15, math.pi - 0.15, 16)] + [(-30, 26), (30, 26)], shade(sk, 0.88), None)
        rr = np.random.default_rng(3)
        for i in range(40):
            a_ = rr.uniform(0.3, math.pi - 0.3); rad = rr.uniform(30, 52)
            Hh.dot(math.cos(a_) * rad, math.sin(a_) * rad + 6, 1.4, shade(sk, 0.6))
    if out == 'farmer':
        for k in (-1, 1):
            Hh.line(bez((k * 36, -4), (k * 41, 2), (k * 37, 8), 5), shade(sk, 0.72), 2)
        Hh.line([(-14, -30), (14, -30)], shade(sk, 0.78), 2)
    if var == 1:
        for (fx_, fy_) in ((-31, 12), (-25, 17), (-37, 17), (29, 12), (35, 17), (25, 17)):
            Hh.dot(fx_, fy_, 1.7, C('c9875c'))
    if soot:
        for (a2, b2, r2) in ((-30, 10, 14), (24, -14, 10), (6, 22, 12), (-10, -24, 8), (38, 20, 9)):
            Hh.dot(a2, b2, r2, C('55504a'))
    ex, ey = look
    eyec = C('3a2a22')
    bcol = C('6a4a30') if var != 2 else C('3a2a20')
    for side in (-1, 1):
        cx = side * 20 + ex * 0.5; cy = -2 + ey * 0.5
        if face in ('open', 'wide', 'half'):
            if face == 'wide':
                Hh.ell(cx, cy, 11, 13, (255, 255, 255), INK, 3)
                Hh.ell(cx + ex * 0.4, cy + 1 + ey * 0.3, 5.5, 6.5, eyec, None, 0)
                Hh.dot(cx + ex * 0.4 + 2, cy - 2, 2, (255, 255, 255))
            else:
                Hh.ell(cx, cy, 6.5, 8.5, eyec, None, 0)
                Hh.dot(cx + 2, cy - 3, 2.4, (255, 255, 255))
                Hh.dot(cx - 2, cy + 3, 1.1, (255, 255, 255))
                if face == 'half':
                    Hh.poly([(cx - 9, cy - 11), (cx + 9, cy - 11), (cx + 9, cy - 1), (cx - 9, cy - 1)], sk, None)
                    Hh.line([(cx - 9, cy - 1), (cx + 9, cy - 1)], INK, 3.5)
        elif face == 'happy':
            Hh.line(bez((cx - 9, cy + 3), (cx, cy - 7), (cx + 9, cy + 3), 8), INK, 4)
        elif face == 'closed':
            Hh.line(bez((cx - 9, cy), (cx, cy + 5), (cx + 9, cy), 8), INK, 4)
        elif face == 'squint':
            Hh.line([(cx - 9, cy - 4), (cx + 7, cy), (cx - 9, cy + 4)] if side < 0 else [(cx + 9, cy - 4), (cx - 7, cy), (cx + 9, cy + 4)], INK, 4)
        by = cy - 18 - brow * 4
        if brow < 0:
            Hh.line([(cx + 11 * side, by - 5), (cx - 9 * side, by + 4)], bcol, 5)
        elif brow > 0.5:
            Hh.line(bez((cx - 10 * side, by - 7), (cx, by - 4), (cx + 10 * side, by + 1), 6), bcol, 5)
        else:
            Hh.line(bez((cx - 10, by + 2), (cx, by - 3), (cx + 10, by + 1), 6), bcol, 5)
    # nose: small soft curve
    nx = ex * 0.6
    Hh.ell(nx + 1, 13, 6, 4.5, shade(sk, 0.86), None, 0)
    Hh.line(bez((nx - 4, 13), (nx + 1, 17), (nx + 6, 13), 6), C('b97c62'), 2.6)
    my = 30 + ey * 0.5; mx = ex * 0.6
    lip = C('b5524a')
    if mouth == 'smile':
        Hh.line(bez((mx - 14, my - 3), (mx, my + 7), (mx + 14, my - 3), 10), INK, 4)
    elif mouth == 'grin':
        Hh.poly(list(bez((mx - 19, my - 4), (mx, my + 18), (mx + 19, my - 4), 12)), C('6e2626'), INK, 4)
        Hh.poly([(mx - 15, my - 3), (mx + 15, my - 3), (mx + 12, my + 3), (mx - 12, my + 3)], (255, 255, 255), None)
        Hh.ell(mx, my + 9, 7, 3.5, C('d86a6a'), None, 0)
    elif mouth == 'o':
        Hh.ell(mx, my + 3, 7, 9, C('6e2626'), INK, 4)
    elif mouth == 'flat':
        Hh.line([(mx - 11, my + 2), (mx + 11, my + 2)], INK, 4)
    elif mouth == 'frown':
        Hh.line(bez((mx - 13, my + 6), (mx, my - 3), (mx + 13, my + 6), 10), INK, 4)
    elif mouth == 'smirk':
        Hh.line(bez((mx - 11, my + 2), (mx + 4, my + 5), (mx + 15, my - 5), 10), INK, 4)
    elif mouth == 'grit':
        Hh.poly([(mx - 15, my - 4), (mx + 15, my - 4), (mx + 15, my + 7), (mx - 15, my + 7)], (255, 255, 255), INK, 4)
        Hh.line([(mx - 15, my + 1.5), (mx + 15, my + 1.5)], INK, 2)
        for q in (-8, 0, 8): Hh.line([(mx + q, my - 4), (mx + q, my + 7)], INK, 2)
    if o.get('fem'):
        for side in (-1, 1):
            cx = side * 20 + ex * 0.5; cy = -2 + ey * 0.5
            if face in ('open', 'wide', 'half'):
                Hh.line([(cx + side * 6, cy - 6), (cx + side * 11, cy - 9)], INK, 2.5)
        if mouth in ('smile', 'smirk', 'flat'):
            Hh.ell(mx, my + 2, 7, 3, C('d7746a'), None, 0)
    if o.get('beard'):
        Hh.poly([(-46, 6), (-30, 40), (0, 64), (30, 40), (46, 6), (34, 30), (16, my + 10), (-16, my + 10), (-34, 30)], C('8a8a8a'), INK, 3)
    if o.get('specs'):
        for side in (-1, 1):
            Hh.ell(side * 20, -2, 15, 15, None, INK, 3)
        Hh.line([(-5, -4), (5, -4)], INK, 3)
    if o.get('tache') or var == 2:
        Hh.poly([(-24, my - 5), (-7, my - 11), (0, my - 8), (7, my - 11), (24, my - 5), (14, my), (0, my - 4), (-14, my)], C('5a3a22'), INK, 3)
    if o.get('hair') is not None:
        hc_ = o['hair']
        Hh.poly([(math.cos(a_) * 60, math.sin(a_) * 56 + 2) for a_ in np.linspace(math.pi * 0.98, math.pi * 2.02, 22)] + [(56, -18), (30, -30), (10, -24), (-6, -34), (-30, -26), (-56, -18)], hc_, INK, 4)
        Hh.poly([(-6, -34), (4, -14), (12, -30)], hc_, INK, 3)
    if o['hat'] in ('bicorne', 'plume'):
        hb = C('1f1b22')
        top = list(bez((118, -24), (10, -190), (-118, -24), 16)); bot = list(bez((-118, -24), (0, -60), (118, -24), 12))
        Hh.poly(top + bot, hb, INK, 5)
        Hh.line(list(bez((100, -34), (8, -160), (-100, -34), 14)), C('3a3442'), 4)
        if o['hat'] == 'plume':
            Hh.line(bot, GOLD, 5)
            for k, (px, py) in enumerate(((-10, -112), (8, -122), (24, -112), (2, -138))):
                Hh.ell(px, py, 26, 20, C('f6f1e6') if k % 2 else C('e9e2d2'), INK, 3)
        Hh.ell(70, -58, 17, 17, C('2a4fa8'), INK, 3); Hh.ell(70, -58, 11, 11, C('f6f1e6'), None, 0); Hh.ell(70, -58, 5.5, 5.5, C('d23a34'), None, 0)
    elif o['hat'] == 'tricorne':
        ht = C('2e2420')
        Hh.poly([(-86, -28), (0, -48), (86, -28), (66, -74), (0, -112), (-66, -74)], ht, INK, 5)
        Hh.line([(-80, -32), (0, -50), (80, -32)], GOLD, 4)
        Hh.line([(-56, -70), (0, -100), (56, -70)], C('4a3c36'), 3)
    if o['hat'] == 'slouch':
        Hh.poly([(-96, -38), (64, -38), (84, -46), (66, -56), (-70, -56)], HATC, INK, 4)
        Hh.line([(-88, -42), (72, -42)], shade(HATC, 1.15), 3)
        Hh.poly([(-74, -54), (-96, -38), (-90, -104), (-70, -102)], shade(HATC, 0.86), INK, 4)
        for k in range(6):
            a_ = k * math.pi / 3; Hh.line([(-82, -76), (-82 + 11 * math.cos(a_), -76 + 11 * math.sin(a_))], GOLD, 3)
        Hh.dot(-82, -76, 6, GOLD)
        Hh.poly([(-46, -52), (46, -52), (42, -94), (18, -106), (0, -100), (-18, -106), (-42, -94)], HATC, INK, 4)
        Hh.line([(-10, -100), (0, -76)], shade(HATC, 0.75), 3)
        Hh.poly([(-47, -50), (47, -50), (46, -66), (-46, -66)], C('b8a070'), INK, 3)
        for k in range(-3, 4): Hh.line([(k * 13 - 4, -50), (k * 13 + 4, -66)], C('9c8560'), 2)
    elif o['hat'] == 'straw':
        Hh.ell(0, -44, 98, 17, STRAW, INK, 4)
        for k in range(1, 4): Hh.ell(0, -44, 98 - k * 18, 17 - k * 3, None, shade(STRAW, 0.82), 2)
        Hh.poly([(-46, -46), (46, -46), (36, -98), (0, -92), (-36, -98)], STRAW, INK, 4)
        for k in range(-3, 4): Hh.line([(k * 11, -50), (k * 9, -94)], shade(STRAW, 0.85), 2)
        Hh.poly([(-46, -50), (46, -50), (44, -63), (-44, -63)], RED, INK, 2)
    elif o['hat'] == 'coif':
        cw = C('f6f1e6')
        outer = [(math.cos(a_) * 68, math.sin(a_) * 64 - 4) for a_ in np.linspace(math.pi * 0.78, math.pi * 2.22, 30)]
        inner = [(math.cos(a_) * 52, math.sin(a_) * 46 + 2) for a_ in np.linspace(math.pi * 2.18, math.pi * 0.82, 30)]
        Hh.poly(outer + [(48, 52), (36, 58)] + inner + [(-36, 58), (-48, 52)], cw, INK, 4)
        Hh.line(bez((-46, -8), (0, -60), (46, -8), 12), shade(cw, 0.86), 3)
    elif o['hat'] == 'kerchief':
        Hh.poly([(math.cos(a_) * 62, math.sin(a_) * 58) for a_ in np.linspace(math.pi * 1.0, math.pi * 2.0, 20)] + [(58, -6), (-58, -6)], C('d8b84a'), INK, 4)
        for k in range(4): Hh.dot(-36 + k * 24, -30 + (k % 2) * 10, 5, C('f6f1e6'))
        Hh.poly([(52, -10), (78, 8), (70, 18), (50, 2)], C('d8b84a'), INK, 3)
    elif o['hat'] == 'hood':
        hc = C('4f7a3a')
        Hh.poly([(20, -60), (74, -104), (92, -82), (44, -48)], hc, INK, 4)
        outer = [(math.cos(a_) * 74, math.sin(a_) * 70) for a_ in np.linspace(math.pi * 0.7, math.pi * 2.3, 34)]
        inner = [(math.cos(a_) * 54, math.sin(a_) * 50 + 4) for a_ in np.linspace(math.pi * 2.25, math.pi * 0.75, 34)]
        Hh.poly(outer + [(56, 66), (-56, 66)][::-1][:0] + inner, hc, INK, 4)
        Hh.poly([(-66, 56), (66, 56), (58, 92), (-58, 92)], hc, INK, 4)
    elif o['hat'] == 'beret':
        Hh.ell(6, -50, 70, 26, C('6a2e3e'), INK, 4); Hh.dot(6, -76, 7, C('6a2e3e'))
    elif o['hat'] == 'doccap':
        Hh.ell(0, -56, 82, 30, C('22212a'), INK, 4)
        Hh.ell(0, -72, 58, 26, C('2b2a33'), INK, 4)
        Hh.ell(-10, -80, 30, 10, C('3a3944'), None, 0)
    elif o['hat'] == 'feather':
        Hh.poly([(-58, -36), (58, -36), (48, -76), (-40, -80)], C('2f6a3a'), INK, 4)
        fp = list(bez((30, -72), (70, -150), (130, -160), 10)) + list(bez((132, -150), (86, -130), (46, -64), 10))
        Hh.poly(fp, C('f2e6c8'), INK, 3)
        Hh.line(bez((34, -70), (72, -140), (128, -156), 10), C('c8b890'), 2)
    elif o['hat'] == 'furcap':
        Hh.poly([(-60, -40), (60, -40), (54, -100), (-54, -100)], C('2a2028'), INK, 4)
        Hh.poly([(-64, -36), (64, -36), (64, -58), (-64, -58)], C('8a6a4a'), INK, 4)
        for k in range(-5, 6): Hh.line([(k * 11, -38), (k * 11 + 3, -56)], C('6a4e34'), 2)
    elif o['hat'] == 'tonsure':
        Hh.poly([(math.cos(a_) * 62, math.sin(a_) * 56) for a_ in np.linspace(math.pi * 0.95, math.pi * 2.05, 24)] + [(58, -14), (-58, -14)], C('6b4a2e'), INK, 4)
        Hh.ell(0, -42, 30, 12, sk, INK, 3)
    elif o['hat'] == 'peak':
        Hh.poly([(-56, -40), (56, -40), (62, -84), (-62, -84)], KHAKI2, INK, 4)
        Hh.poly([(-66, -84), (66, -84), (58, -102), (-58, -102)], shade(KHAKI2, 0.92), INK, 4)
        Hh.poly([(-50, -40), (40, -40), (72, -26), (-30, -28)], C('3a2a1a'), INK, 4)
        Hh.line([(-40, -36), (60, -30)], C('6a5a4a'), 2)
        Hh.poly([(-56, -46), (56, -46), (56, -58), (-56, -58)], RED, None)
        Hh.ell(0, -72, 11, 11, GOLD, INK, 3); Hh.dot(0, -72, 4, RED)
    if sweat:
        Hh.poly([(70, -20), (78, -2), (70, 4), (62, -2)], C('9fd8ff'), INK, 3)

# ---------------- EMU ----------------
EMUB = C('6f5747'); EMUB2 = C('4f3d31'); EMUB3 = C('8c7360'); NECK = C('7d97b0'); NECKD = C('5f7891')
BEAK = C('3b302a'); IRIS = C('e07a2a'); LEG = C('8a8174'); CROWN = C('2f2724')

def _shag(cx, cy, rx, ry, n, amp, seed, droop=0.0):
    r = np.random.default_rng(seed)
    pts = []
    for i in range(n):
        t = i / n * 2 * math.pi
        k = 1 + (amp if i % 2 else -amp * 0.3) * (0.7 + 0.6 * r.random())
        px = math.cos(t) * rx * k; py = math.sin(t) * ry * k
        if math.sin(t) > 0.2 and i % 2: py += amp * 90
        px -= droop * max(0, -math.cos(t)) * (py + ry) * 0.0
        pts.append((cx + px, cy + py))
    return pts

def emu(d, x, y, sc=1.0, flip=1, run=0.0, phase=0.0, neck=0.0, face='open', mouth=None, tilt=0.0,
        bob=0.0, peck=0.0, blink=False, look=(0, 0), wink=False, shadow_on=True, star=False):
    if shadow_on: shadow(d.sub(Aff(x, y, sc)), 10, 2, 80, 15)
    L = d.sub(Aff(x, y, sc, 0, flip))
    b = abs(math.sin(phase)) * 14 * run + bob
    # legs
    for k, ph in ((0, phase), (1, phase + math.pi)):
        sw = math.sin(ph) * run
        lift = max(0, math.cos(ph)) * run * 46
        hip = (6 + k * 12, -168 + b)
        foot = (sw * 74 + (k * 2 - 1) * 16 * (1 - run), -lift)
        knee = (hip[0] + 4 + sw * 10, hip[1] + 46)
        ankle = ((knee[0] + foot[0]) / 2 - 22, (knee[1] + foot[1]) / 2 - 10 + lift * 0.2)
        col = LEG if k == 0 else shade(LEG, 1.12)
        L.tube([hip, knee], 22, EMUB2 if k == 0 else EMUB, INK, 4)
        L.tube([knee, ankle, foot], 12, col, INK, 4)
        for j in range(1, 6):
            p = np.array(knee) + (np.array(ankle) - np.array(knee)) * j / 6
            L.line([(p[0] - 5, p[1]), (p[0] + 5, p[1] + 1)], shade(col, 0.75), 2)
        fx, fy = foot
        for a in (-0.45, 0.05, 0.5):
            tx, ty = fx + 26 * math.cos(a), fy - 2 + 7 * math.sin(a)
            L.tube([(fx, fy), (tx, ty)], 8, col, INK, 3)
            L.line([(tx, ty), (tx + 6, ty + 2)], INK, 3)
    # body
    B = L.sub(Aff(0, -205 + b, 1, -0.1 - neck * 0.14))
    B.poly(_shag(-6, 4, 100, 64, 30, 0.10, 3), EMUB2, INK, 5)
    B.poly(_shag(-2, -2, 90, 54, 26, 0.08, 4), EMUB, None)
    B.poly(_shag(10, -14, 62, 30, 18, 0.07, 5), EMUB3, None)
    rr = np.random.default_rng(9)
    for i in range(22):
        fx_ = rr.uniform(-85, 70); fy_ = rr.uniform(-40, 50)
        if (fx_ / 90) ** 2 + (fy_ / 58) ** 2 > 0.85: continue
        c_ = EMUB2 if i % 3 else EMUB3
        B.line([(fx_ + 8, fy_ - 8), (fx_, fy_), (fx_ - 4, fy_ + 14)], c_, 3)
    # drooping fringe
    for i in range(9):
        fx_ = -80 + i * 19; L0 = 26 + (i % 3) * 10
        B.line([(fx_, 44), (fx_ - 8, 44 + L0)], EMUB2, 5)
    # neck
    nl = neck
    base = (64, -34)
    hx = 92 + nl * 70 + peck * 80; hy = -178 + nl * 60 + peck * 250
    t = np.linspace(0, 1, 18)[:, None]
    p0 = np.array(base); p3 = np.array((hx, hy + 14))
    p1 = np.array((112 + nl * 40, -72 + nl * 20)); p2 = np.array((40 + nl * 80 + peck * 30, -122 + nl * 50 + peck * 60))
    pts = (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
    B.tube(pts, 28, NECK, INK, 4)
    B.line(pts[2:] + [-6, 2], NECKD, 8)
    B.line(pts[2:] + [6, -3], shade(NECK, 1.15), 4)
    # fluffy lower neck collar
    c0 = pts[3]
    B.poly(_shag(c0[0] - 4, c0[1] + 6, 30, 30, 14, 0.25, 11), EMUB2, INK, 4)
    B.poly(_shag(c0[0] - 2, c0[1] + 2, 22, 22, 12, 0.2, 12), EMUB, None)
    H = B.sub(Aff(hx, hy, 1, tilt + peck * 0.9))
    if star:
        for k, (a_, l_) in enumerate(((-2.2, 42), (-1.85, 50), (-1.5, 40))):
            tx_, ty_ = -14 + math.cos(a_) * l_, -18 + math.sin(a_) * l_
            H.poly([(-18 + k * 6, -18), (tx_ - 6, ty_), (tx_ + 4, ty_ + 2), (-8 + k * 6, -16)], CROWN, INK, 3)
    H.ell(0, 0, 36, 28, C('8ca4ba'), INK, 4)
    H.poly(_shag(-10, -14, 30, 16, 16, 0.18, 7), CROWN, None)
    H.ell(-24, 6, 10, 12, C('6f88a0'), None, 0)
    if mouth == 'open':
        H.poly([(24, -4), (66, 0), (24, 6)], BEAK, INK, 3); H.poly([(24, 10), (58, 18), (22, 16)], BEAK, INK, 3)
    elif mouth == 'chew':
        H.poly([(24, -4), (60, 4), (24, 12)], BEAK, INK, 3)
        H.ell(12, 18, 16, 11, C('8ca4ba'), INK, 3)
    else:
        H.poly([(24, -6), (58, -2), (66, 4), (24, 12)], BEAK, INK, 3)
        H.line([(26, 4), (56, 4)], C('5a4a40'), 2)
    H.dot(46, -1, 2, C('1a1a1a'))
    ex, ey = look
    if blink or face == 'closed':
        H.line([(-4, -2), (18, -2)], INK, 4)
    elif face == 'half' or wink:
        H.ell(7 + ex, -2 + ey, 13, 13, (255, 255, 255), INK, 3)
        H.dot(10 + ex, ey, 6.5, IRIS); H.dot(11 + ex, ey, 3.2, INK)
        H.poly([(-8, -17), (22, -17), (22, -2), (-8, -2)], C('8ca4ba'), None)
        H.line([(-8, -2), (22, -2)], INK, 4)
    else:
        rr_ = 15 if face == 'wide' else 12.5
        H.ell(7, -2, rr_, rr_, (255, 255, 255), INK, 3)
        H.dot(9 + ex, ey, 7, IRIS); H.dot(10 + ex, ey, 3.6, INK); H.dot(12 + ex, -4 + ey, 2.2, (255, 255, 255))
        if face == 'angry':
            H.line([(-10, -20), (22, -10)], INK, 5)
    q = H.tp([(8, -2)])[0]
    return q

# ---------------- PROPS ----------------
def lewis(d, x, y, sc=1.0, ang=0.0, flip=1, smoke=0.0, fire=0.0):
    L = d.sub(Aff(x, y, sc, ang, flip))
    if fire > 0:
        rr = 40 + 30 * fire
        st = [(150 + (rr if i % 2 == 0 else rr * 0.4) * math.cos(i * math.pi / 5), (rr if i % 2 == 0 else rr * 0.4) * 0.7 * math.sin(i * math.pi / 5)) for i in range(10)]
        st = [(150 + abs(px - 150) * 1.4 + 10, py) for px, py in st]
        L.poly(st, C('ffb02e'), INK, 3)
        L.ell(175, 0, 22, 12, C('fff3b0'), None, 0)
    L.poly([(-120, -8), (-60, -14), (-60, 14), (-110, 22)], C('7a5230'), INK, 4)  # stock
    L.poly([(-62, -16), (90, -16), (90, 16), (-62, 16)], C('4b5258'), INK, 4)  # shroud
    for i in range(8): L.line([(-50 + i * 18, -16), (-50 + i * 18, 16)], C('3a4046'), 3)
    L.poly([(90, -6), (150, -6), (150, 6), (90, 6)], C('2f3438'), INK, 4)
    L.ell(-10, -30, 44, 12, C('3a4046'), INK, 4)
    L.ell(-10, -36, 44, 10, C('5a6268'), INK, 3)
    L.line([(60, 16), (40, 70)], INK, 6); L.line([(60, 16), (84, 70)], INK, 6)
    if smoke > 0:
        for i, (a, b, r) in enumerate(((160, -10, 22), (190, -30, 28), (215, -12, 20), (175, -46, 18))):
            rr = r * smoke * (1 + i * 0.1)
            L.ell(a + smoke * 20 * i, b - smoke * 30, rr, rr * 0.85, C('cfcfcf'), INK, 3)

def draw_wheel(d, x, y, r, rot):
    W_ = d.sub(Aff(x, y, 1, rot))
    W_.ell(0, 0, r, r, C('262422'), INK, 5)
    for i in range(16):
        a = i * 2 * math.pi / 16
        W_.line([(math.cos(a) * (r - 7), math.sin(a) * (r - 7)), (math.cos(a) * (r - 1), math.sin(a) * (r - 1))], C('3c3a37'), 4)
    W_.ell(0, 0, r * 0.62, r * 0.62, C('a8342a'), INK, 4)
    W_.ell(-3, -3, r * 0.5, r * 0.5, C('bf4436'), None, 0)
    for i in range(5):
        a = i * 2 * math.pi / 5; W_.dot(math.cos(a) * r * 0.36, math.sin(a) * r * 0.36, 3.2, C('e8e2d0'))
    W_.ell(0, 0, r * 0.2, r * 0.2, C('d0d4d8'), INK, 3)
    W_.line([(0, 0), (r * 0.55, 0)], shade(C('a8342a'), 0.7), 3)

def truck(d, x, y, sc=1.0, flip=1, wheel_rot=0.0, bounce=0.0, tilt=0.0, wheel=None, shadow_on=True):
    if wheel is not None: wheel_rot = wheel
    if shadow_on: shadow(d.sub(Aff(x, y, sc)), 20, 4, 300, 26, 0.5)
    L = d.sub(Aff(x, y, sc, 0, flip))
    R = L.sub(Aff(0, -bounce, 1, tilt))
    B = R.sub(Aff(0, 0, 0.8))
    GR = C('3d6a49'); GRL = C('4f8460'); GRD = C('2b4c34'); CH = C('cfd3d6'); WOOD = C('9a6b3c')
    # chassis
    B.poly([(-300, -96), (360, -96), (360, -80), (-300, -80)], C('2a2a2a'), INK, 4)
    # flatbed + stake sides
    B.poly([(-300, -96), (40, -96), (40, -126), (-300, -126)], WOOD, INK, 5)
    B.line([(-296, -111), (36, -111)], shade(WOOD, 0.8), 3)
    for i in range(8):
        px = -290 + i * 46
        B.poly([(px, -126), (px + 10, -126), (px + 10, -200), (px, -200)], shade(WOOD, 0.9), INK, 3)
    for yy in (-150, -196):
        B.poly([(-300, yy), (40, yy), (40, yy - 12), (-300, yy - 12)], shade(WOOD, 1.08), INK, 3)
    # rear fender
    B.poly(list(bez((-250, -92), (-160, -200), (-70, -92), 14)) + [(-70, -84), (-250, -84)], GRD, INK, 4)
    # cab
    cab = [(40, -96), (215, -96), (215, -205), (200, -262), (60, -268), (40, -250)]
    B.poly(cab, GR, INK, 5)
    B.poly([(52, -110), (205, -110), (205, -200), (190, -250), (66, -255), (52, -240)], GRL, None)
    B.poly([(70, -246), (176, -246), (188, -196), (70, -196)], C('b9dcec'), INK, 4)
    B.line([(84, -238), (110, -206)], C('e8f6fb'), 5)
    B.line([(140, -196), (140, -104)], GRD, 3); B.line([(70, -104), (70, -196)], GRD, 3)
    B.poly([(120, -170), (134, -170), (134, -164), (120, -164)], CH, INK, 2)
    B.poly([(54, -268), (205, -262), (208, -272), (60, -280)], GRD, INK, 3)
    # hood
    hood = [(215, -100), (345, -100), (348, -190), (330, -205), (215, -210)]
    B.poly(hood, GR, INK, 5)
    B.poly([(222, -108), (338, -108), (338, -186), (222, -198)], GRL, None)
    for i in range(5): B.line([(250 + i * 14, -170), (250 + i * 14, -130)], GRD, 4)
    # grille
    B.poly([(345, -96), (372, -96), (372, -200), (348, -206)], CH, INK, 4)
    for i in range(4): B.line([(351 + i * 6, -104), (351 + i * 6, -194)], C('6a6e72'), 2)
    # front fender + running board
    B.poly(list(bez((235, -92), (320, -205), (400, -92), 14)) + [(400, -84), (380, -80), (230, -84)], GRD, INK, 4)
    B.poly([(70, -84), (240, -84), (240, -74), (70, -74)], C('2f2f2f'), INK, 3)
    # headlamp + bumper
    B.line([(352, -150), (360, -176)], CH, 5)
    B.ell(366, -184, 17, 17, CH, INK, 4); B.ell(372, -184, 10, 12, C('fff1b0'), None, 0)
    B.poly([(360, -70), (410, -70), (410, -58), (360, -58)], CH, INK, 3)
    # wheels
    draw_wheel(L.sub(Aff(0, 0, 0.8)), -160, -60, 62, wheel_rot)
    draw_wheel(L.sub(Aff(0, 0, 0.8)), 318, -60, 62, wheel_rot)
    return R

WHEAT = C('e0a63c'); WHEATD = C('b9822c'); WHEATL = C('f6d77e'); STALK = C('c99a3e')

def wheat_ear(d, x, y, h, sway=0.0, sc=1.0, col=None, ink=True, awn=True):
    """one wheat stalk with a grain ear. (x,y) base, h height (design units), sway radians-ish."""
    col = col or WHEAT
    top = (x + sway * h * 0.45, y - h)
    mid = (x + sway * h * 0.12, y - h * 0.55)
    stalk = bez((x, y), mid, top, 8)
    d.line(stalk, STALK, 3.2 * sc)
    # leaf
    lp_ = stalk[3]
    d.poly([(lp_[0], lp_[1]), (lp_[0] + 30 * sc, lp_[1] + 10 * sc + sway * 20), (lp_[0] + 6 * sc, lp_[1] + 4 * sc)], shade(STALK, 0.9), None)
    # ear along direction of top
    dx, dy = stalk[-1] - stalk[-2]; ln = math.hypot(dx, dy) + 1e-6; ux, uy = dx / ln, dy / ln
    px, py = -uy, ux
    n = 7; gl = 11 * sc
    for i in range(n):
        cx_ = top[0] + ux * (i * gl * 0.75); cy_ = top[1] + uy * (i * gl * 0.75)
        for s_ in (-1, 1):
            gx = cx_ + px * s_ * 5 * sc; gy = cy_ + py * s_ * 5 * sc
            ang = math.atan2(uy, ux) + s_ * 0.45
            d.ell(gx, gy, 8 * sc, 4.6 * sc, shade(col, 1.0 if s_ > 0 else 0.86), INK if ink else None, 1.6 * sc, ang=ang, n=12)
            if awn and i % 2 == 0:
                d.line([(gx, gy), (gx + (ux * 1.0 + px * s_ * 0.5) * 34 * sc, gy + (uy * 1.0 + py * s_ * 0.5) * 34 * sc)], shade(col, 1.18), 1.4 * sc)
    d.ell(top[0] + ux * (n * gl * 0.75), top[1] + uy * (n * gl * 0.75), 6 * sc, 4 * sc, WHEATL, INK if ink else None, 1.5 * sc, ang=math.atan2(uy, ux))

def fg_wheat(d, t, y0, x0=-400, x1=4400, n=None, seed=1, sc=2.0, h=300, wind=1.0, xoff=0.0, density=1.6):
    """foreground wheat fixed in the world; only on-screen stalks are drawn"""
    r = np.random.default_rng(seed)
    n = int((x1 - x0) / 100 * density * 10)
    items = sorted([(r.uniform(0, 1), r.uniform(x0, x1), r.uniform(0, 6.28)) for _ in range(n // 10)])
    W_ = d.img.shape[1]
    for dep, x, ph in items:
        sx = d.tp([(x, y0)])[0][0]
        if sx < -0.25 * W_ or sx > 1.25 * W_: continue
        yy = y0 + dep * 140; k = 0.75 + dep * 0.5
        sw = (math.sin(t * 1.6 + x * 0.004 + ph * 0.3) * 0.12 + 0.05) * wind
        wheat_ear(d, x, yy, h * k, sw, sc * k)

def trail(d, x, y, t, flip=1, sc=1.0, seed=0, amt=1.0):
    """dust puffs kicked up behind a runner (x,y = feet)"""
    for k in range(4):
        ph = (t * 2.6 + k * 0.25 + seed * 0.13) % 1.0
        px = x - flip * (40 + ph * 220) * sc; py = y - (10 + ph * 50) * sc
        r_ = (14 + ph * 46) * sc * (1 - ph * 0.55) * amt
        if r_ < 1: continue
        col = shade(C('e9d6ad'), 1.0 - ph * 0.12)
        d.ell(px, py, r_, r_ * 0.8, col, None, 0)
        d.ell(px - 4 * sc, py - 4 * sc, r_ * 0.6, r_ * 0.5, shade(col, 1.06), None, 0)

def wheat_tuft(d, x, y, h, col, sway=0.0, w=4):
    for i in range(-2, 3):
        wheat_ear(d, x + i * 14, y, h * (0.85 + 0.1 * (i % 2)), sway + i * 0.04, 1.3)

# ---------------- TEXT ----------------
FB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
FX = '/usr/share/fonts/truetype/google-fonts/Poppins-ExtraBold.ttf'
FDJ = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
import os
if not os.path.exists(FX): FX = FB

@lru_cache(maxsize=4000)
def text_sprite(txt, size, rgb=(255, 255, 255), stroke=0.14, font=None, stroke_rgb=(40, 22, 40)):
    f = ImageFont.truetype(font or FX, max(6, int(size)))
    sw = max(1, int(size * stroke))
    bb = f.getbbox(txt, stroke_width=sw)
    w = bb[2] - bb[0] + 4; h = bb[3] - bb[1] + 4
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-bb[0] + 2, -bb[1] + 2), txt, font=f, fill=rgb + (255,), stroke_width=sw, stroke_fill=stroke_rgb + (255,))
    a = np.array(im)
    return a

def blit(img, spr, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01: return
    s = spr
    if abs(scale - 1) > 1e-3 or abs(rot) > 1e-3:
        h, w = s.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), math.degrees(rot), scale)
        c_, s_ = abs(math.cos(rot)), abs(math.sin(rot))
        nw = int((w * c_ + h * s_) * scale + 8); nh = int((w * s_ + h * c_) * scale + 8)
        M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        s = cv2.warpAffine(s, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    h, w = s.shape[:2]
    x0 = int(cx - w / 2); y0 = int(cy - h / 2)
    H, W = img.shape[:2]
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb: return
    sub = s[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = sub[..., 3:4] / 255.0 * alpha
    rgb = sub[..., :3][..., ::-1]
    img[ya:yb, xa:xb] = (img[ya:yb, xa:xb] * (1 - a) + rgb * a).astype(np.uint8)


def dancer(d, x, y, sc, out, t, ph=0.0, var=0, energy=1.0, tired=0.0, face=None, mouth=None, flip=1, shoes=None, style='bounce', arms=None):
    """townsfolk dancing. styles: bounce, spin, kick, hold (arms out to the sides for couples/rings)"""
    w = t * 7.5 + ph
    e = energy
    armL = (150 + 25 * math.sin(w) * e, 80) if e > 0.3 else (20, 70)
    armR = (-140 - 30 * math.sin(w + 1.3) * e, 80) if e > 0.3 else (-20, 70)
    kick = 0.0; lean = math.sin(w * 0.5 + 0.5) * 0.06 * e
    if style == 'kick' and e > 0.3:
        kick = max(0, math.sin(w * 0.5)) * e
        armL = (120, 80); armR = (-120, 80); lean = -0.1 * kick
    if style == 'hold':
        armL = (95 + 10 * math.sin(w), 82); armR = (-95 - 10 * math.sin(w), 82)
    flare = 0.0; extra_bob = 0.0
    if style == 'star' and e > 0.3:
        mv = int(t * 112 / 60 / 2) % 4
        beat = (t * 112 / 60) % 1.0; hit = math.exp(-beat * 6)
        if mv == 0:   # twirl, skirt flares
            style_spin = True; armL = (148, 118); armR = (-148, 118); flare = 0.8
        elif mv == 1:  # clap overhead on the beat
            armL = (152 - 10 * hit, 132); armR = (-152 + 10 * hit, 132); extra_bob = 12 * hit
        elif mv == 2:  # happy hops, arms wide
            armL = (115, 85); armR = (-115, 85); extra_bob = 34 * hit; flare = 0.35 * hit
        else:          # side sway, waving
            armL = (150 + 30 * math.sin(w), 85); armR = (-60 - 30 * math.sin(w), 75); lean = 0.16 * math.sin(t * 3.7)
        face = face or 'happy'; mouth = mouth or 'grin'
    if arms: armL, armR = arms
    if tired > 0.5:
        armL = (40 + 20 * math.sin(w), 75); armR = (-40 - 20 * math.sin(w + 1), 75)
    f = face or ('closed' if tired > 0.5 else ('happy' if math.sin(w * 0.3 + ph) > 0 else 'open'))
    m = mouth or ('frown' if tired > 0.5 else ('grin' if math.sin(w * 0.3 + ph) > -0.3 else 'o'))
    D_ = d
    xx = x + math.sin(w * 0.5) * 10 * e
    spin_now = (style == 'spin' and e > 0.3) or (style == 'star' and e > 0.3 and int(t * 112 / 60 / 2) % 4 == 0)
    if spin_now:
        c = math.cos(w * 0.35) if style == 'spin' else math.cos(((t * 112 / 60 / 2) % 1.0) * 2 * math.pi)
        D_ = d.sub(Aff(xx, y)).sub(np.array([[max(0.2, abs(c)), 0, 0], [0, 1, 0], [0, 0, 1]], float))
        flip = 1 if c > 0 else -1
        xx, y = 0, 0
        D_ = D_.sub(Aff(0, 0, sc)); sc_ = 1.0
        shadow(d.sub(Aff(x, d_y if False else 0)), 0, 0, 0.01, 0.01) if False else None
    else:
        sc_ = sc
        D_ = d.sub(Aff(xx, y, sc)); xx, y = 0, 0; sc_ = 1.0
    human(D_, 0, 0, sc_, out, face=f, mouth=m, flip=flip,
          armL=armL, armR=armR, step=(w * 0.5 if (e > 0.2 and style != 'kick') else 0) or 0.0001, tilt=math.sin(w * 0.5) * 0.12 * e,
          bob=abs(math.sin(w)) * 14 * e + extra_bob, lean=lean, var=var, sweat=tired > 0.3, shoes=shoes, kick=kick, flare=flare)
    if style == 'star' and e > 0.3 and tired < 0.5:
        mv = int(t * 112 / 60 / 2) % 4; u = (t * 112 / 60 / 2) % 1.0
        G = d.sub(Aff(x, y, sc))
        if mv == 0:
            for k in range(2):
                a0 = u * 6.28 + k * math.pi
                arc = [(math.cos(a0 + j * 0.12) * 120, -150 + math.sin(a0 + j * 0.12) * 40) for j in range(10)]
                G.line(arc, C('fff6dc'), 7); G.line(arc, C('ffd34a'), 3)
        elif mv == 1 and u < 0.5:
            for k in range(5):
                a0 = k * 1.26 + 0.3
                G.line([(math.cos(a0) * 30, -430 + math.sin(a0) * 30), (math.cos(a0) * 60, -430 + math.sin(a0) * 60)], C('ffd34a'), 6)


# ================= NAPOLEON vs BUNNIES additions =================
RAB = {'white': C('f4f1ea'), 'brown': C('a8794e'), 'grey': C('9a9590'), 'cream': C('e8d2a8'), 'black': C('4a4246'), 'spot': C('f4f1ea')}
PINK = C('f2a0a8')

def rabbit(d, x, y, sc=1.0, flip=1, hop=0.0, col='white', face='open', ear=0.0, look=(0, 0), tilt=0.0,
           mouth='w', shadow_on=True, napkin=False, brow=0.0, stretch=0.0, ear_flop=0.0, sweat=False):
    """FableVerse farm bunny. (x,y)=feet. hop 0..1 = height of jump. stretch>0 = mid-leap pose."""
    c = RAB.get(col, col) if isinstance(col, str) else col
    if shadow_on: shadow(d.sub(Aff(x, y, sc)), 0, 2, 62 * (1 - hop * 0.4), 13 * (1 - hop * 0.4))
    L = d.sub(Aff(x, y - hop * 90 * sc, sc, 0, flip))
    sq = 1 + stretch * 0.25
    # back foot
    L.ell(-36 - stretch * 20, -8 + stretch * 6, 40, 12, shade(c, 0.86), INK, 4, ang=stretch * 0.3)
    # tail
    L.ell(-72 - stretch * 10, -52, 17, 17, C('fbfaf6'), INK, 4)
    # body
    L.ell(-10, -50, 64 * sq, 50 / sq, c, INK, 5)
    L.ell(4, -40, 34, 32, shade(c, 1.08) if col != 'brown' else C('e8d2a8'), None, 0)
    if col == 'spot':
        L.ell(-30, -66, 24, 16, C('a8794e'), None, 0); L.ell(-50, -36, 14, 12, C('a8794e'), None, 0)
    # front paws
    L.ell(30 + stretch * 30, -8 - stretch * 10, 15, 9, shade(c, 0.95), INK, 3.5)
    L.ell(14 + stretch * 26, -6 - stretch * 6, 14, 8, shade(c, 0.9), INK, 3.5)
    H = L.sub(Aff(34 + stretch * 16, -104 + stretch * 18, 1, tilt))
    # ears (behind head)
    fl = ear_flop
    for k, (ex_, ang) in enumerate(((-12, -0.22 + ear - fl), (12, 0.18 - ear + fl * 1.3))):
        ax = ex_ + math.sin(ang) * 46; ay = -40 - math.cos(ang) * 46
        H.ell(ax, ay, 15, 48, shade(c, 0.95 if k == 0 else 1.0), INK, 4, ang=ang)
        H.ell(ax, ay + 4, 7, 34, PINK, None, 0, ang=ang)
    H.ell(0, 0, 48, 42, c, INK, 5)
    if col == 'spot': H.ell(-22, -16, 16, 12, C('a8794e'), None, 0)
    H.ell(-18, 16, 10, 6, C('f6b8b8'), None, 0); H.ell(30, 16, 9, 6, C('f6b8b8'), None, 0)
    ex, ey = look
    for sd, cx in ((-1, -8), (1, 20)):
        cy = -6
        if face == 'wide':
            H.ell(cx, cy, 11, 13, (255, 255, 255), INK, 3); H.ell(cx + ex * 0.4, cy + 1 + ey * 0.3, 6, 7, C('2a1e22'), None, 0)
            H.dot(cx + ex * 0.4 + 2, cy - 2, 2.2, (255, 255, 255))
        elif face == 'happy':
            H.line(bez((cx - 8, cy + 3), (cx, cy - 7), (cx + 8, cy + 3), 8), INK, 4)
        elif face == 'closed':
            H.line(bez((cx - 8, cy), (cx, cy + 5), (cx + 8, cy), 8), INK, 4)
        else:
            H.ell(cx + ex * 0.4, cy + ey * 0.4, 7, 9, C('2a1e22'), None, 0)
            H.dot(cx + ex * 0.4 + 2.5, cy + ey * 0.4 - 3.5, 2.8, (255, 255, 255))
            if face == 'half':
                H.poly([(cx - 10, cy - 12), (cx + 10, cy - 12), (cx + 10, cy - 1), (cx - 10, cy - 1)], c, None)
                H.line([(cx - 10, cy - 1), (cx + 10, cy - 1)], INK, 3.5)
        if brow:
            by = cy - 18
            if brow < 0: H.line([(cx - 9 * -1, by - 4), (cx + 9 * -1, by + 4)] if sd < 0 else [(cx + 9, by - 4), (cx - 9, by + 4)], INK, 4.5)
            else: H.line(bez((cx - 9, by + 2), (cx, by - 4), (cx + 9, by + 2), 6), INK, 4)
    H.poly([(28, 8), (40, 8), (34, 16)], C('e07a8a'), INK, 2.5)
    if mouth == 'w':
        H.line(bez((24, 20), (29, 26), (34, 20), 5), INK, 3); H.line(bez((34, 20), (39, 26), (44, 20), 5), INK, 3)
    elif mouth == 'o':
        H.ell(34, 26, 6, 7, C('6e2626'), INK, 3)
    elif mouth == 'grin':
        H.poly(list(bez((22, 20), (34, 38), (46, 20), 8)), C('6e2626'), INK, 3)
        H.poly([(30, 20), (38, 20), (38, 27), (30, 27)], (255, 255, 255), INK, 1.5)
    elif mouth == 'flat':
        H.line([(26, 24), (42, 24)], INK, 3)
    for k in (-1, 1):
        H.line([(44, 14 + k * 3), (66, 10 + k * 9)], shade(c, 0.6), 1.8)
    if napkin:
        H.poly([(-14, 34), (46, 30), (16, 74)], C('fbfaf6'), INK, 3)
        H.line([(-4, 40), (36, 37)], C('d23a34'), 3)
    if sweat:
        H.poly([(-40, -30), (-34, -14), (-40, -8), (-46, -14)], C('9fd8ff'), INK, 2.5)

def cage(d, x, y, sc=1.0, door=0.0, inside=None, t=0.0):
    """wooden rabbit crate. door 0 closed .. 1 swung open. inside(d_local) draws peeking rabbits."""
    L = d.sub(Aff(x, y, sc))
    W_ = C('a87444'); Wd = C('7a4e2a')
    L.poly([(-150, 0), (150, 0), (150, -190), (-150, -190)], C('8a6440'), INK, 5)
    L.poly([(-150, 0), (150, 0), (150, -40), (-150, -30)], C('e0c060'), None)
    if inside: inside(L)
    for k in range(-3, 4):
        if door > 0.02 and abs(k) <= 1: continue
        L.tube([(k * 40, -12), (k * 40, -178)], 6, C('9a9a96'), INK, 2)
    L.poly([(-160, 0), (160, 0), (160, -18), (-160, -18)], W_, INK, 4)
    L.poly([(-160, -176), (160, -176), (160, -196), (-160, -196)], W_, INK, 4)
    L.poly([(-160, 0), (-136, 0), (-136, -196), (-160, -196)], Wd, INK, 4)
    L.poly([(136, 0), (160, 0), (160, -196), (136, -196)], Wd, INK, 4)
    if door > 0.02:
        cw = math.cos(door * 1.7)
        Dd = L.sub(Aff(-66, 0)).sub(np.array([[cw, 0, 0], [-0.25 * math.sin(door * 1.7), 1, 0], [0, 0, 1]], float))
        Dd.poly([(0, -14), (132, -14), (132, -178), (0, -178)], None, Wd, 6)
        for k in range(1, 5): Dd.line([(k * 26, -16), (k * 26, -176)], C('8a8a86'), 5)
        Dd.ell(124, -96, 7, 7, GOLD, INK, 2)
    else:
        L.poly([(-68, -14), (68, -14), (68, -178), (-68, -178)], None, Wd, 6)
        L.ell(60, -96, 7, 7, GOLD, INK, 2)

def carriage(d, x, y, sc=1.0, wheel=0.0, bounce=0.0, part='all'):
    L = d.sub(Aff(x, y, sc))
    R = L.sub(Aff(0, -bounce))
    G_ = C('233a30'); Gl = C('2f4e40'); GD = GOLD
    if part in ('all', 'back'):
        shadow(L, 0, 4, 280, 24, 0.5)
        R.line([(220, -120), (520, -110)], C('5a3a20'), 12)
        draw_wheel(L, -170, -78, 82, wheel); draw_wheel(L, 190, -66, 68, wheel)
        R.poly([(-240, -140), (240, -140), (240, -170), (-240, -170)], C('2a2a2a'), INK, 4)
        body = [(-230, -150), (230, -150), (250, -300), (220, -420), (-220, -420), (-250, -300)]
        R.poly(body, G_, INK, 6); R.poly([(x_ * 0.92, y_ * 0.96 - 6) for x_, y_ in body], Gl, None)
        R.poly([(-250, -420), (250, -420), (236, -446), (-236, -446)], C('1a2a22'), INK, 5)
        for k in (-200, -60, 60, 200): R.ell(k, -452, 10, 10, GD, INK, 3)
        R.poly([(-170, -400), (-30, -400), (-30, -290), (-170, -290)], C('2c2a30'), INK, 5)  # window (interior)
        R.poly([(40, -400), (170, -400), (170, -290), (40, -290)], C('b9dcec'), INK, 5)
        R.line([(60, -390), (100, -300)], C('e8f6fb'), 6)
    if part in ('all', 'front'):
        R.poly([(-190, -290), (0, -290), (0, -160), (-190, -160)], G_, INK, 5)
        R.poly([(-180, -282), (-10, -282), (-10, -168), (-180, -168)], None, GD, 4)
        R.ell(-95, -226, 32, 32, GD, INK, 3); R.ell(-95, -226, 22, 22, G_, None, 0)
        world_N = text_sprite('N', max(6, int(40 * R.k)), (227, 184, 74), 0.0)
        q = R.tp([(-95, -226)])[0]; blit(R.img, world_N, q[0], q[1])
        R.line([(-200, -295), (0, -295)], GD, 5)

def gun_prop(B, hL, hR):
    p0 = np.array(hR, float); p1 = np.array(hL, float); v = p1 - p0; n = float(np.linalg.norm(v))
    if n < 8: v = np.array([1.0, -0.3]); n = float(np.linalg.norm(v))
    u = v / n
    B.tube([p0 - u * 46, p0 + u * 46], 22, C('7a4a28'), INK, 4)
    B.tube([p0 + u * 40, p1 + u * 170], 10, C('4a4f55'), INK, 3)
    B.ell(*(p0 + u * 30), 8, 8, C('8a8a86'), INK, 2)

def stick_prop(ang=-0.6, ln=170, col=None):
    col = col or C('8a5a32')
    def f(B, hL, hR):
        x0, y0 = hL; B.tube([(x0, y0), (x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln)], 11, col, INK, 3.5)
    return f

def clip_prop(B, hL, hR):
    x0, y0 = hL
    B.poly([(x0 - 40, y0 - 70), (x0 + 30, y0 - 70), (x0 + 30, y0 + 20), (x0 - 40, y0 + 20)], C('a87444'), INK, 4)
    B.poly([(x0 - 32, y0 - 60), (x0 + 22, y0 - 60), (x0 + 22, y0 + 12), (x0 - 32, y0 + 12)], C('f6f1e6'), None)
    for k in range(4): B.line([(x0 - 26, y0 - 46 + k * 15), (x0 + 16, y0 - 46 + k * 15)], C('8a7a6a'), 2.5)
    B.poly([(x0 - 14, y0 - 76), (x0 + 6, y0 - 76), (x0 + 6, y0 - 64), (x0 - 14, y0 - 64)], C('8a8a86'), INK, 2)

def flag(d, x, y, t, sc=1.0, h=520):
    L = d.sub(Aff(x, y, sc))
    L.tube([(0, 0), (0, -h)], 12, C('6a4a30'), INK, 4); L.ell(0, -h - 10, 14, 14, GOLD, INK, 3)
    cols = (C('2a4fa8'), C('f6f1e6'), C('d23a34'))
    for k in range(3):
        pts = []
        for j in range(7):
            u = (k + j / 6) / 3; px = 8 + u * 300; wv = math.sin(t * 5 - u * 5) * 18 * u
            pts.append((px, -h + 10 + wv))
        for j in range(6, -1, -1):
            u = (k + j / 6) / 3; px = 8 + u * 300; wv = math.sin(t * 5 - u * 5) * 18 * u
            pts.append((px, -h + 200 + wv))
        L.poly(pts, cols[k], INK, 4)

def bubble(d, x, y, r, tx, ty, sc=1.0, inner=None):
    L = d.sub(Aff(x, y, sc))
    for k, rr in enumerate((12, 20)):
        u = (k + 1) / 3; L.ell(lerp(tx, 0, u), lerp(ty, 0, u) + r * 0.6 * u, rr, rr, C('ffffff'), INK, 4)
    pts = []
    for i in range(40):
        a = i / 40 * 2 * math.pi; k = 1 + 0.07 * math.sin(a * 9)
        pts.append((math.cos(a) * r * 1.25 * k, math.sin(a) * r * k))
    L.poly(pts, C('ffffff'), INK, 5)
    if inner: inner(L)

def carrot(d, x, y, sc=1.0, ang=0.0):
    L = d.sub(Aff(x, y, sc, ang))
    for k in (-0.4, 0, 0.4): L.ell(math.sin(k) * 30, -70 - math.cos(k) * 20, 9, 28, C('4f9a3a'), INK, 3, ang=k)
    L.poly([(-26, -60), (26, -60), (0, 80)], C('f08a2a'), INK, 4)
    for k in range(3): L.line([(-14 + k * 4, -30 + k * 30), (2 + k * 2, -26 + k * 30)], C('c86a1a'), 3)

def quill(d, x, y, sc=1.0, ang=0.5):
    L = d.sub(Aff(x, y, sc, ang))
    L.line([(0, 0), (0, -40)], C('2a2a2a'), 5)
    L.poly([(0, -30), (26, -120), (14, -230), (-4, -160), (-14, -60)], C('fbfaf6'), INK, 4)
    L.line([(0, -30), (12, -220)], C('c9c2b2'), 3)
