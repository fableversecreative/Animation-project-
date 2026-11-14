import numpy as np, cv2, math, json, sys, os, random, re
from rig import *

W, H, FPS = 1080, 1920, 30
DUR = 44.6
NF = int(round(DUR * FPS))
S = float(os.environ.get('S', '0.3333333'))
OW, OH = int(round(W * S)), int(round(H * S))
MARG = 420
HERE = os.path.dirname(os.path.abspath(__file__))
HZ = 980

def rng(seed): return random.Random(seed)

# ---------------- backgrounds ----------------
_bg = {}; BGOFF = {}
def gradient(img, y0, y1, c0, c1):
    for y in range(max(0, y0), min(img.shape[0], y1)):
        t = (y - y0) / max(1, y1 - y0)
        img[y, :] = [int(lerp(c0[i], c1[i], t)) for i in range(3)]

MAP_REG = {
    'britain': [(300, 560), (350, 520), (380, 600), (370, 700), (330, 760), (290, 740), (310, 660)],
    'ireland': [(230, 620), (270, 600), (280, 660), (240, 690)],
    'spain': [(150, 1000), (330, 960), (380, 1000), (360, 1120), (280, 1200), (170, 1190), (120, 1100)],
    'france': [(330, 960), (300, 880), (330, 800), (420, 780), (480, 800), (500, 880), (470, 960), (400, 990), (380, 1000)],
    'low': [(420, 780), (440, 730), (500, 720), (510, 790), (480, 800)],
    'germany': [(500, 720), (600, 690), (640, 740), (640, 850), (560, 880), (500, 880), (510, 790)],
    'italy': [(500, 880), (560, 880), (600, 920), (640, 1010), (700, 1090), (680, 1120), (630, 1060), (570, 990), (520, 960)],
    'austria': [(560, 880), (640, 850), (740, 860), (760, 920), (660, 930), (600, 920)],
    'poland': [(640, 740), (760, 720), (800, 800), (740, 860), (640, 850)],
    'russia': [(760, 720), (800, 560), (1000, 500), (1180, 520), (1180, 1000), (900, 960), (800, 900), (740, 860), (800, 800)],
    'scandi': [(560, 560), (620, 420), (720, 380), (760, 460), (700, 560), (660, 640), (620, 600)],
    'balkans': [(660, 930), (760, 920), (800, 900), (900, 960), (860, 1060), (780, 1100), (720, 1040)],
    'denmark': [(560, 640), (590, 610), (600, 690), (570, 690)],
}
CONQ = [('france', 0.25), ('low', 0.55), ('italy', 0.8), ('germany', 1.05), ('austria', 1.3), ('spain', 1.55), ('poland', 1.8)]

def draw_meadow(d, img, r, XL, XR, bh, farm=False):
    gradient(img, 0, int((MARG + HZ) * S), C('86c3ec'), C('f7e6c2'))
    for rr_, a in ((300, 0.12), (190, 0.2)):
        ov = img.copy(); D(ov, d.M).ell(860, 360, rr_, rr_, C('fff4c8'), None, 0)
        img[:] = cv2.addWeighted(ov, a, img, 1 - a, 0)
    d.ell(860, 360, 80, 80, C('fff6d0'), None, 0)
    for i in range(12):
        cx = r.uniform(XL, XR); cy = r.uniform(120, 560)
        for j in range(4): d.ell(cx + j * 64 - 96, cy + (0 if j % 3 else -26), 84, 46, C('ffffff'), None, 0)
    xs = np.linspace(XL, XR, 160)
    for layer, (col, base, amp) in enumerate(((C('a9c4a6'), HZ - 90, 70), (C('8eb08a'), HZ - 30, 40))):
        ys = base - amp * (0.5 + 0.5 * np.sin(xs / 230 + layer * 2.1)) - 16 * np.sin(xs / 71 + layer)
        d.poly(np.concatenate([np.stack([xs, ys], 1), [[XR, HZ + 40], [XL, HZ + 40]]]), col, None)
    # forest edge
    for i in range(int((XR - XL) / 38)):
        tx = XL + i * 38 + r.uniform(-10, 10); s_ = r.uniform(0.7, 1.15)
        col = C(r.choice(('4f7a44', '5a8a4a', '46703e', '628f50')))
        d.poly([(tx - 46 * s_, HZ + 10), (tx + 46 * s_, HZ + 10), (tx, HZ - 190 * s_)], col, INK, 2)
        d.poly([(tx - 34 * s_, HZ - 60 * s_), (tx + 34 * s_, HZ - 60 * s_), (tx, HZ - 230 * s_)], shade(col, 1.1), INK, 2)
    # far camp tents with flags
    if not farm:
        for tx in (-420, -250, -90, 1500, 1680):
            d.poly([(tx - 60, HZ + 30), (tx + 60, HZ + 30), (tx, HZ - 70)], C('f2ead8'), INK, 3)
            d.line([(tx, HZ - 70), (tx, HZ - 110)], C('6a4a30'), 3)
            d.poly([(tx, HZ - 110), (tx + 30, HZ - 110), (tx + 30, HZ - 92), (tx, HZ - 92)], C('d23a34'), None)
            d.poly([(tx, HZ - 110), (tx + 10, HZ - 110), (tx + 10, HZ - 92), (tx, HZ - 92)], C('2a4fa8'), None)
            d.poly([(tx + 10, HZ - 110), (tx + 20, HZ - 110), (tx + 20, HZ - 92), (tx + 10, HZ - 92)], C('f6f1e6'), None)
    else:
        bx = 820
        d.poly([(bx, HZ + 60), (bx + 330, HZ + 60), (bx + 330, HZ - 170), (bx, HZ - 170)], C('b8463a'), INK, 5)
        d.poly([(bx - 30, HZ - 170), (bx + 360, HZ - 170), (bx + 165, HZ - 330)], C('7a3a30'), INK, 5)
        d.poly([(bx + 110, HZ + 60), (bx + 220, HZ + 60), (bx + 220, HZ - 90), (bx + 110, HZ - 90)], C('f2ead8'), INK, 4)
        d.line([(bx + 110, HZ + 60), (bx + 220, HZ - 90)], C('f2ead8'), 6); d.line([(bx + 220, HZ + 60), (bx + 110, HZ - 90)], C('f2ead8'), 6)
        d.poly([(bx + 140, HZ - 240), (bx + 190, HZ - 240), (bx + 190, HZ - 200), (bx + 140, HZ - 200)], C('2c3440'), INK, 3)
    # grass
    gradient(img, int((MARG + HZ) * S), bh, C('8fb85c'), C('6e9a44'))
    for i in range(16):
        d.ell(r.uniform(XL, XR), HZ + r.uniform(120, 1100), r.uniform(240, 500), r.uniform(40, 110), C('82ab52'), None, 0)
    for i in range(1700):
        y = HZ + 12 + (r.random() ** 1.3) * (H + MARG - HZ); x = r.uniform(XL, XR); sz = 0.25 + (y - HZ) / 700
        d.line([(x, y), (x + r.uniform(-5, 5) * sz, y - 26 * sz)], shade(C('8fb85c'), r.choice((0.78, 0.9, 1.14))), 3 * sz)
    for i in range(220):
        y = HZ + 30 + (r.random() ** 1.2) * (H + MARG - HZ); x = r.uniform(XL, XR); sz = 0.3 + (y - HZ) / 800
        d.dot(x, y, 4 * sz, C(r.choice(('fff8f0', 'f2d14a', 'e87a9a', 'ffffff', 'b9a6e8'))))
    for i in range(10):
        x_ = r.uniform(XL, XR); y_ = HZ + r.uniform(30, 220); s_ = 0.5 + (y_ - HZ) / 400
        for j in range(3): d.ell(x_ + (j - 1) * 26 * s_, y_ - (j % 2) * 16 * s_, 30 * s_, 22 * s_, C('5f8a40') if j % 2 else C('6c9a48'), INK, 2)
    if farm:
        for i in range(-12, 40):
            fx = i * 70; d.tube([(fx, HZ + 150), (fx, HZ + 70)], 9, C('a87444'), INK, 2)
        d.line([(XL, HZ + 95), (XR, HZ + 95)], C('a87444'), 7); d.line([(XL, HZ + 125), (XR, HZ + 125)], C('a87444'), 7)

def bgimg(kind):
    if kind in _bg: return _bg[kind]
    if kind.endswith('_blur'):
        b = bgimg(kind[:-5]); k = int(30 * S) | 1
        BGOFF[kind] = BGOFF[kind[:-5]]
        _bg[kind] = cv2.GaussianBlur(b, (k, k), 0); return _bg[kind]
    mxl, mxr = 900, 1500
    BGOFF[kind] = (mxl, MARG)
    bw, bh = int((W + mxl + mxr) * S), int((H + 2 * MARG) * S)
    img = np.zeros((bh, bw, 3), np.uint8)
    d = D(img, Aff(mxl * S, MARG * S, S))
    XL, XR = -mxl, W + mxr
    r = rng(sum(map(ord, kind)))
    if kind in ('meadow', 'farm'):
        draw_meadow(d, img, r, XL, XR, bh, farm=(kind == 'farm'))
    elif kind == 'map':
        img[:] = C('9fbcc0')
        for i in range(60):
            d.ell(r.uniform(XL, XR), r.uniform(-MARG, H + MARG), r.uniform(60, 200), r.uniform(40, 120), shade(C('9fbcc0'), r.choice((0.95, 1.04))), None, 0)
        for k in range(-2, 18): d.line([(XL, k * 120), (XR, k * 120)], C('8eaab0'), 2)
        for k in range(-8, 24): d.line([(k * 120, -MARG), (k * 120, H + MARG)], C('8eaab0'), 2)
        for nm, pts in MAP_REG.items():
            d.poly(pts, C('ecdcb4'), C('6a5038'), 3)
        for i in range(160):
            x_ = r.uniform(150, 1100); y_ = r.uniform(420, 1200)
            d.dot(x_, y_, r.uniform(2, 5), C('d9c49a'))
        # compass rose + frame
        cx_, cy_ = 900, 1300
        for k in range(8):
            a_ = k * math.pi / 4; L_ = 90 if k % 2 == 0 else 50
            d.poly([(cx_, cy_), (cx_ + math.cos(a_ - 0.25) * 22, cy_ + math.sin(a_ - 0.25) * 22), (cx_ + math.cos(a_) * L_, cy_ + math.sin(a_) * L_), (cx_ + math.cos(a_ + 0.25) * 22, cy_ + math.sin(a_ + 0.25) * 22)], C('8a3a2e') if k % 2 == 0 else C('e3b84a'), INK, 3)
        d.ell(cx_, cy_, 12, 12, C('f6f1e6'), INK, 3)
        ov = img.copy(); d2 = D(ov, d.M)
        for i in range(40): d2.ell(r.uniform(XL, XR), r.uniform(-MARG, H + MARG), r.uniform(100, 300), r.uniform(80, 200), C('c9b48a'), None, 0)
        img[:] = cv2.addWeighted(ov, 0.12, img, 0.88, 0)
    elif kind == 'tent':
        gradient(img, 0, bh, C('ecdcb8'), C('cdb68a'))
        for i in range(-10, 30):
            x = i * 120; d.poly([(x, -MARG), (x + 60, -MARG), (x + 60, 1500), (x, 1500)], C('3a5a9a'), None)
        d.poly([(XL, 1250), (XR, 1250), (XR, 1500), (XL, 1500)], None, None, 0)
        for i in range(-10, 30):
            x = i * 120; d.poly(list(bez((x, 300), (x + 60, 360), (x + 120, 300), 8)) + [(x + 120, 220), (x, 220)], C('d23a34') if i % 2 else C('f2ead8'), INK, 3)
        d.line([(XL, 300), (XR, 300)], C('e3b84a'), 10)
        d.poly([(XL, 1500), (XR, 1500), (XR, H + MARG), (XL, H + MARG)], C('7a3a30'), INK, 5)
        for i in range(-10, 40): d.line([(i * 90, 1500), (i * 90 - 60, H + MARG)], C('6a3028'), 4)
        d.poly([(-200, 1560), (1300, 1560), (1360, 1900), (-260, 1900)], C('b8463a'), INK, 4)
        d.poly([(-160, 1590), (1260, 1590), (1300, 1860), (-200, 1860)], None, C('e3b84a'), 6)
    elif kind == 'blue':
        img[:] = C('2a5a9a')
        for i in range(-20, 40):
            d.line([(i * 80, -MARG), (i * 80 + 600, H + MARG)], C('336aaa'), 30)
    elif kind == 'red':
        img[:] = C('b8382e')
        for i in range(-20, 40):
            d.line([(i * 80, -MARG), (i * 80 + 600, H + MARG)], C('c8463a'), 30)
    _bg[kind] = img
    return img

# ---------------- look ----------------
VIG = None
def vignette():
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:OH, 0:OW]
        r = np.sqrt(((x - OW / 2) / (OW / 2)) ** 2 + ((y - OH / 2) / (OH / 2)) ** 2)
        VIG = (1 - 0.32 * np.clip(r - 0.5, 0, 1) ** 1.5)[..., None].astype(np.float32)
    return VIG
LUT = None
def grade(img, f):
    global LUT
    if LUT is None:
        x = np.arange(256, dtype=np.float32)
        y = np.clip((x - 128) * 1.1 + 128, 0, 255)
        LUT = [np.clip(y * k, 0, 255).astype(np.uint8) for k in (0.95, 1.0, 1.05)]
    for c in range(3): img[..., c] = LUT[c][img[..., c]]
    g = np.random.default_rng(f).integers(-5, 6, (OH, OW, 1), dtype=np.int16)
    img[:] = np.clip(img.astype(np.float32) * vignette() + g, 0, 255).astype(np.uint8)

# ---------------- camera ----------------
def cam_keys(keys, t):
    if t <= keys[0][0]: return keys[0][1:5]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = (t - a[0]) / max(1e-6, b[0] - a[0])
            e = b[5] if len(b) > 5 else 's'
            u = smooth(u) if e == 's' else eout(u) if e == 'o' else back(u, 1.4) if e == 'b' else u
            return tuple(lerp(a[i], b[i], u) for i in range(1, 5))
    return keys[-1][1:5]

def camM(cx, cy, z, rot, shake=(0, 0)):
    return Aff(0, 0, S) @ Aff(W / 2 + shake[0], H / 2 + shake[1]) @ Aff(0, 0, z, rot) @ Aff(-cx, -cy)

def shake_at(t, kicks, amp=16):
    sx = sy = 0
    for k in kicks:
        dt = t - k
        if 0 <= dt < 0.3:
            a = amp * (1 - dt / 0.3); sx += a * math.sin(dt * 90); sy += a * math.cos(dt * 70)
    return sx, sy

def fr(x, feet, sc, z, face_y=None, dx=0):
    """camera centre so a human of scale sc standing at feet has its face at screen y=face_y (auto: chin clears captions)"""
    if face_y is None: face_y = min(1000, 1190 - 80 * sc * z - 80)
    return (x - dx / z, feet - 262 * sc - (face_y - 960) / z, z)

def K(t, x, feet, sc, z, rot=0.0, e='s', face_y=None, dx=0):
    cx, cy, zz = fr(x, feet, sc, z, face_y, dx); return (t, cx, cy, zz, rot, e)

# ---------------- HUD ----------------
def hud_text(img, txt, x, y, size, rgb=(255, 255, 255), scale=1.0, alpha=1.0, rot=0.0, font=None):
    blit(img, text_sprite(txt, int(size * S), rgb, 0.14, font), x * S, y * S, scale, alpha, rot)

def pop(t, t0, dur=0.25):
    if t < t0: return 0.0
    return back((t - t0) / dur, 2.2)

def tag(img, txt, t, t0, t1, y=230):
    if t < t0 or t > t1: return
    a = clamp((t - t0) / 0.15) * clamp((t1 - t) / 0.2)
    sc = 0.6 + 0.4 * pop(t, t0, 0.3)
    w = len(txt) * 30 + 80
    ov = img.copy(); D(ov, Aff(0, 0, S)).poly([(540 - w / 2 * sc, y - 44 * sc), (540 + w / 2 * sc, y - 44 * sc), (540 + w / 2 * sc, y + 44 * sc), (540 - w / 2 * sc, y + 44 * sc)], C('2a1a2a'), None)
    img[:] = cv2.addWeighted(ov, 0.62 * a, img, 1 - 0.62 * a, 0)
    hud_text(img, txt, 540, y, 54, (255, 214, 64), sc, a)

def blinkat(t, times): return any(0 <= t - k < 0.11 for k in times)

EXP = {'proud': ('half', 'smirk', 0.8), 'smug': ('half', 'smirk', 0.0), 'worried': ('open', 'frown', 1.0), 'scared': ('wide', 'o', 1.0),
       'shocked': ('wide', 'o', 1.0), 'sad': ('half', 'frown', 1.0), 'deadpan': ('half', 'flat', 0.0), 'excited': ('happy', 'grin', 1.0),
       'confused': ('open', 'smirk', 0.7), 'angry': ('open', 'grit', -1.0), 'happy': ('happy', 'smile', 0.6), 'sly': ('half', 'smirk', -1.0),
       'determined': ('open', 'grit', -1.0)}

def person(d, out, x, y, sc, expr='happy', t=0.0, blink=(), **kw):
    f, m, b = EXP[expr]
    if blinkat(t, blink) and f in ('open', 'half'): f = 'closed'
    kw.setdefault('brow', b)
    kw.setdefault('sweat', expr in ('scared', 'shocked', 'worried'))
    human(d, x, y, sc, out, face=f, mouth=m, **kw)

def nap(d, x, y, sc, expr='smug', t=0.0, **kw): person(d, 'napoleon', x, y, sc, expr, t, **kw)

def track(t, keys):
    """keys [(t, value)], hold + quick overshoot move"""
    if t <= keys[0][0]: return keys[0][1]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = clamp((t - a[0]) / 0.22) if b[0] - a[0] > 0.22 else (t - a[0]) / (b[0] - a[0])
            return lerp(a[1], b[1], back(u, 1.6))
    return keys[-1][1]

def at(t, keys):
    v = keys[0][1]
    for k, val in keys:
        if t >= k: v = val
    return v

# ---------------- shots ----------------
SH = []
def shot(t0, t1, bg=None, blur=False):
    def deco(fn):
        SH.append(dict(t0=t0, t1=t1, cam=fn, bg=bg, blur=blur)); return fn
    return deco
def draws(fn): SH[-1]['draw'] = fn; return fn
def huds(fn): SH[-1]['hud'] = fn; return fn

COLS = ['white', 'brown', 'grey', 'cream', 'spot', 'black', 'white', 'brown']

# A1 0-1.15: low-angle proud Napoleon with flag
@shot(0.0, 1.15, 'meadow')
def a1(t, lt): return [K(0, 560, 1600, 1.5, 1.55, -0.04), K(1.15, 560, 1600, 1.5, 1.7, -0.06, 'l')], []
@draws
def a1d(d, t, lt):
    flag(d, 360, 1560, t, 1.6)
    nap(d, 560, 1600, 1.5, 'proud', t, armR=(60, 52), armL=(25, 70), bob=math.sin(t * 2) * 2, look=(4, -2))

# A2 1.15-2.9: map, red spreads, hat stamp
@shot(1.15, 2.9, 'map')
def a2(t, lt): return [(0, 560, 860, 1.65, 0.03), (1.6, 560, 880, 1.0, 0.0, 'o')], [2.42 - 1.15]
@draws
def a2d(d, t, lt):
    for nm, t0 in CONQ:
        if lt >= t0:
            u = pop(lt, t0, 0.25); pts = np.array(MAP_REG[nm], float); c = pts.mean(0)
            d.poly((pts - c) * min(1, u) + c, C('c8382e'), C('6a2018'), 3)
    if lt > 1.27:
        u = clamp((lt - 1.27) / 0.12)
        hy = lerp(-200, 0, u * u)
        L = d.sub(Aff(410, 880 + hy, 0.75 + 0.5 * (1 - u)))
        top = list(bez((118, -24), (10, -190), (-118, -24), 16)); bot = list(bez((-118, -24), (0, -60), (118, -24), 12))
        L.poly(top + bot, C('1f1b22'), INK, 6)
        L.ell(70, -58, 17, 17, C('2a4fa8'), INK, 3); L.ell(70, -58, 11, 11, C('f6f1e6'), None, 0); L.ell(70, -58, 5.5, 5.5, C('d23a34'), None, 0)
@huds
def a2h(img, t, lt):
    hud_text(img, 'EUROPE', 540, 300, 110, (255, 255, 255), 0.6 + 0.4 * pop(lt, 0.1, 0.3))

# B 2.9-4.75: Napoleon CU smug -> worried on "lost"
@shot(2.9, 4.75, 'meadow', blur=True)
def b_(t, lt): return [K(0, 540, 1700, 1.8, 2.05, 0.0), K(1.85, 540, 1700, 1.8, 2.3, 0.02, 'l')], []
@draws
def b_d(d, t, lt):
    e = 'smug' if lt < 0.75 else 'worried'
    lk = (0, 0) if lt < 0.75 else ((-6, 2) if lt < 1.2 else (6, 2))
    nap(d, 540, 1700, 1.8, e, t, armR=(60, 52), armL=(25, 70), look=lk, tilt=track(lt, [(0, 0.0), (0.75, 0.08)]), blink=(0.4,))

# C 4.75-6.6: rabbit CU pops up
@shot(4.75, 6.6, 'meadow', blur=True)
def c_(t, lt): return [(0, 540, 1420, 2.6, 0.0), (1.85, 540, 1430, 2.8, 0.03, 'l')], []
@draws
def c_d(d, t, lt):
    u = clamp((lt - 0.08) / 0.25)
    hop = math.sin(u * math.pi) * 0.7 if u < 1 else 0
    tl = track(lt, [(0, 0.0), (0.9, 0.22), (1.5, -0.1)])
    rabbit(d, 520, 1560, 2.4, 1, hop, 'white', face='open', ear=0.15 * math.sin(lt * 9) if lt > 1.0 else 0, tilt=tl, look=(4, 0), mouth='w')
    for i in range(14):
        x_ = 300 + i * 40; d.line([(x_, 1580), (x_ + 10, 1500 - (i % 3) * 20)], C('6e9a44'), 9)
@huds
def c_h(img, t, lt):
    if lt > 0.35:
        p = pop(lt, 0.35, 0.3); hud_text(img, 'NAPOLEON', 540, 250, 96, (255, 255, 255), p)
        hud_text(img, 'vs', 540, 345, 70, (255, 214, 64), p)
        hud_text(img, 'BUNNIES', 540, 440, 120, (255, 140, 160), p)

# D 6.6-8.2: macro treaty + quill
@shot(6.6, 8.2, 'tent', blur=True)
def d_(t, lt): return [(0, 560, 1500, 2.2, -0.08), (1.6, 520, 1470, 2.4, -0.04, 'l')], []
@draws
def d_d(d, t, lt):
    d.poly([(100, 1380), (1000, 1380), (1040, 1800), (60, 1800)], C('7a4a28'), INK, 6)
    d.poly([(300, 1330), (800, 1310), (830, 1700), (280, 1720)], C('f4ead2'), INK, 5)
    for k in range(7): d.line([(340, 1380 + k * 36), (770, 1365 + k * 36)], C('b8a888'), 4)
    hud_like = text_sprite('TREATY', max(6, int(54 * d.k)), (90, 60, 40), 0.0)
    q = d.tp([(550, 1345)])[0]; blit(d.img, hud_like, q[0], q[1])
    u = clamp((lt - 0.2) / 1.1); n = int(u * 30)
    pts = [(420 + i * 9, 1640 + math.sin(i * 1.7) * 14 - i * 0.6) for i in range(n + 1)]
    if n > 1: d.line(pts, C('2a2030'), 5)
    qx, qy = pts[-1]
    quill(d, qx, qy, 1.3, 0.45 + 0.1 * math.sin(lt * 20))
@huds
def d_h(img, t, lt): tag(img, 'JULY 1807', t, 6.75, 8.15)

# E 8.2-10.0: handshake with the Tsar
@shot(8.2, 10.0, 'tent')
def e_(t, lt): return [K(0, 540, 1650, 1.3, 1.35, 0.0), K(1.8, 540, 1650, 1.3, 1.5, 0.0, 'l')], [0.35]
@draws
def e_d(d, t, lt):
    sh = math.sin(lt * 22) * 6 if 0.3 < lt < 1.2 else 0
    nap(d, 410, 1650, 1.25, 'excited' if lt > 0.3 else 'smug', t, armL=(84 + sh, 104), armR=(-20, 70), lean=0.08)
    person(d, 'tsar', 670, 1660, 1.3, 'happy', t, flip=-1, armL=(84 - sh, 100), armR=(-20, 70), lean=0.08)
    d.poly([(140, 1660), (960, 1660), (960, 1720), (140, 1720)], C('7a4a28'), INK, 5)
    d.poly([(300, 1620), (520, 1610), (530, 1665), (290, 1670)], C('f4ead2'), INK, 4)
@huds
def e_h(img, t, lt): tag(img, 'BIG PEACE TREATY', t, 8.35, 9.95)

# F 10.0-12.6: Napoleon wants a rabbit hunt
@shot(10.0, 12.6, 'meadow')
def f_(t, lt): return [K(0, 470, 1640, 1.4, 1.45, 0.0), K(2.6, 500, 1640, 1.4, 1.6, -0.02, 'l')], []
@draws
def f_d(d, t, lt):
    raise_ = track(lt, [(0, 0.0), (0.55, 1.0)])
    nap(d, 420, 1640, 1.4, 'excited' if lt > 0.5 else 'happy', t, armL=(lerp(40, 150, raise_), 85), armR=(lerp(-20, 120, raise_), 60),
        prop=gun_prop, bob=abs(math.sin(lt * 9)) * 10 * raise_)
    if lt > 1.9:
        p = pop(lt, 1.9, 0.3)
        bubble(d, 800, 760, 150, -180, 250, p, inner=lambda L: rabbit(L, 10, 90, 0.9, -1, 0, 'white', face='happy', shadow_on=False))
@huds
def f_h(img, t, lt): tag(img, 'TIME TO CELEBRATE!', t, 10.1, 11.9)

# G 12.6-14.3: Berthier, chief of staff
@shot(12.6, 14.3, 'meadow', blur=True)
def g_(t, lt): return [K(0, 540, 1650, 1.55, 1.7, 0.03), K(1.7, 540, 1650, 1.55, 1.85, 0.0, 'l')], []
@draws
def g_d(d, t, lt):
    sal = track(lt, [(0, 0.0), (0.25, 1.0), (1.2, 0.0)])
    person(d, 'berthier', 540, 1650, 1.55, 'proud', t, armR=(lerp(-20, -158, sal), lerp(70, 62, sal)), armL=(40, 62), prop=clip_prop, blink=(1.0,))
@huds
def g_h(img, t, lt): tag(img, 'CHIEF OF STAFF', t, 12.75, 14.25)

# H 14.3-16.3: rows of cages full of rabbits
def peekers(seed, n=3, t=0.0, hop=False):
    def f(L):
        r = rng(seed)
        for i in range(n):
            x_ = -90 + i * 90 + r.uniform(-15, 15); ph = r.uniform(0, 6)
            rabbit(L, x_, -20, 0.72, r.choice((1, -1)), abs(math.sin(t * 6 + ph)) * 0.25 if hop else 0, r.choice(COLS), face='open',
                   ear=0.1 * math.sin(t * 7 + ph), look=(r.uniform(-4, 4), 0), shadow_on=False)
    return f
@shot(14.3, 16.3, 'meadow')
def h_(t, lt): return [(0, 260, 1300, 1.45, 0.0), (2.0, 760, 1310, 1.5, 0.02, 'l')], []
@draws
def h_d(d, t, lt):
    for row, (yy, sc_) in enumerate(((1250, 0.75), (1420, 0.95), (1640, 1.2))):
        for i in range(-3, 9):
            x_ = i * 340 * sc_ + row * 110
            cage(d, x_, yy, sc_, 0, peekers(i * 7 + row, 3, t, hop=True), t)
@huds
def h_h(img, t, lt):
    if lt > 0.95:
        p = pop(lt, 0.95, 0.3); hud_text(img, 'HUNDREDS', 540, 300, 140, (255, 214, 64), p, 1, -0.05)

# I 16.3-17.75: macro cage door opens
@shot(16.3, 17.75, 'meadow', blur=True)
def i_(t, lt): return [(0, 560, 1380, 2.6, -0.05), (1.45, 560, 1390, 2.75, -0.03, 'l')], [0.32]
@draws
def i_d(d, t, lt):
    dr = clamp((lt - 0.28) / 0.25)
    def inside(L):
        u = clamp((lt - 0.7) / 0.3)
        rabbit(L, lerp(-10, 40, u), -20, 0.75, 1, 0, 'brown', face='open', look=(5, 0), ear=0.12 * math.sin(lt * 10), shadow_on=False)
    cage(d, 540, 1520, 1.6, back(dr, 1.4), inside, t)

# J 17.75-19.75: hunters raise their guns
@shot(17.75, 19.75, 'meadow')
def j_(t, lt): return [K(0, 560, 1600, 1.3, 1.25, 0.03), K(2.0, 560, 1600, 1.3, 1.4, 0.05, 'l')], []
@draws
def j_d(d, t, lt):
    for k, (x_, out, t0) in enumerate(((180, 'hunter', 0.35), (900, 'hunter2', 0.45))):
        r_ = track(lt, [(0, 0.0), (t0, 1.0)])
        person(d, out, x_, 1500, 1.05, 'determined', t, flip=1 if x_ < 540 else -1,
               armL=(lerp(20, 100, r_), 85), armR=(lerp(-20, 72, r_), 55), prop=gun_prop)
    r_ = track(lt, [(0, 0.0), (0.25, 1.0)])
    nap(d, 560, 1600, 1.3, 'sly', t, armL=(lerp(20, 100, r_), 85), armR=(lerp(-20, 72, r_), 55), prop=gun_prop, look=(6, 0))

# K 19.75-21.8: rabbits don't run
@shot(19.75, 21.8, 'meadow')
def k_(t, lt): return [(0, 560, 1250, 1.15, 0.0), (2.05, 560, 1250, 1.25, 0.0, 'l')], []
@draws
def k_d(d, t, lt):
    nap(d, 560, 1300, 0.85, 'confused', t, armL=(100, 85), armR=(72, 55), prop=gun_prop, tilt=track(lt, [(0, 0), (0.9, 0.15)]))
    r = rng(4)
    for i in range(14):
        x_ = r.uniform(80, 1000); y_ = 1460 + (i % 4) * 90 + r.uniform(-20, 20)
        sc_ = 0.7 + (y_ - 1460) / 600
        lk = (-6, -4) if lt < 0.9 else (6, -4)
        rabbit(d, x_, y_, sc_, r.choice((1, -1)), 0, r.choice(COLS), face='open', look=lk, ear=0.08 * math.sin(t * 5 + i), tilt=0.1 * math.sin(i))
@huds
def k_h(img, t, lt): pass

# L 21.8-23.85: rabbits charge at Napoleon
@shot(21.8, 23.85, 'meadow')
def l_(t, lt): return [(0, 600, 1280, 1.05, 0.0), (2.05, 700, 1300, 1.2, 0.03, 'l')], [0.25]
@draws
def l_d(d, t, lt):
    items = []
    r = rng(9)
    for i in range(34):
        x0 = r.uniform(-650, 250); y_ = r.uniform(1380, 1820); sp = r.uniform(420, 620); ph = r.uniform(0, 1)
        x_ = min(x0 + sp * lt, 700 - (1820 - y_) * 0.3 + r.uniform(-80, 40))
        items.append((y_, x_, ph, i))
    nap(d, 880, 1360, 1.0, 'shocked', t, armL=(150, 80), armR=(-150, 80), flip=-1, look=(-6, 2), bob=abs(math.sin(lt * 25)) * 6)
    for y_, x_, ph, i in sorted(items):
        sc_ = 0.55 + (y_ - 1380) / 700
        hp = abs(math.sin((lt * 3.2 + ph) * math.pi))
        rabbit(d, x_, y_, sc_, 1, hp * 0.55, COLS[i % len(COLS)], face='happy' if i % 3 == 0 else 'open', mouth='grin' if i % 2 else 'w',
               stretch=hp * 0.6, ear=-0.15, look=(6, 0))
@huds
def l_h(img, t, lt):
    if lt > 0.2: hud_text(img, '!', 900, 560, 220, (255, 214, 64), pop(lt, 0.2, 0.25), 1, 0.1)

# M 23.85-25.4: swarm climbing his legs
@shot(23.85, 25.4, 'meadow')
def m_(t, lt): return [K(0, 540, 1700, 1.4, 1.35, 0.0), K(1.55, 540, 1700, 1.4, 1.5, -0.04, 'l')], [0.1, 0.8]
@draws
def m_d(d, t, lt):
    fl = math.sin(lt * 16)
    r = rng(12)
    for i in range(10):
        a = r.uniform(0, 6.28); x_ = 540 + math.cos(a) * r.uniform(140, 420); y_ = 1640 + math.sin(a) * 50
        if y_ < 1700: rabbit(d, x_, y_, 0.7, 1 if x_ < 540 else -1, abs(math.sin(lt * 8 + i)) * 0.4, COLS[i % 8], face='open', look=(0, -4))
    nap(d, 540, 1700, 1.4, 'scared', t, armL=(130 + 30 * fl, 85), armR=(-130 - 30 * fl, 85), bob=abs(fl) * 10, lean=0.06 * fl)
    climb = clamp(lt / 1.2)
    for i, (sx, base) in enumerate(((-30, 0.0), (30, 0.25), (-20, 0.5), (34, 0.75))):
        u = clamp(climb * 1.5 - base * 0.5)
        y_ = 1700 - u * 120 - i * 8
        rabbit(d, 540 + sx * 2.2, y_, 0.6, 1 if sx < 0 else -1, 0, COLS[(i + 2) % 8], face='happy', mouth='grin', stretch=0.6, tilt=-0.5 if sx < 0 else 0.5, shadow_on=False)
    for i in range(8):
        a = r.uniform(0, 6.28); x_ = 540 + math.cos(a) * r.uniform(90, 380); y_ = 1720 + abs(math.sin(a)) * 120
        rabbit(d, x_, y_, 0.85, 1 if x_ < 540 else -1, abs(math.sin(lt * 9 + i)) * 0.35, COLS[(i + 3) % 8], face='open', look=(0, -4))

# N 25.4-27.0: CU, rabbit on his hat
@shot(25.4, 27.0, 'meadow', blur=True)
def n_(t, lt): return [K(0, 540, 1800, 2.0, 2.0, 0.04), K(1.6, 540, 1800, 2.0, 2.15, 0.02, 'l')], []
@draws
def n_d(d, t, lt):
    nap(d, 540, 1800, 2.0, 'worried', t, look=(0, -8), armL=(20, 70), armR=(-20, 70), blink=(1.1,))
    u = clamp(lt / 0.25)
    rabbit(d, 560, lerp(1060, 1135, back(u)), 1.0, -1, 0, 'cream', face='happy', mouth='w', shadow_on=False, tilt=0.1 * math.sin(lt * 4))
    rabbit(d, 720, 1440, 0.85, -1, 0, 'grey', face='open', look=(-6, 0), shadow_on=False, ear=0.1 * math.sin(lt * 8))

# O 27.0-29.2: whips and sticks, rabbits bounce on
@shot(27.0, 29.2, 'meadow')
def o_(t, lt): return [(0, 560, 1260, 1.1, 0.0), (2.2, 560, 1270, 1.2, -0.02, 'l')], [0.3, 0.9, 1.5]
@draws
def o_d(d, t, lt):
    sw = math.sin(lt * 14)
    person(d, 'berthier', 260, 1560, 1.0, 'angry', t, armL=(110 + 60 * sw, 85), armR=(-30, 70), prop=stick_prop(-0.4 + sw * 0.9, 190))
    person(d, 'hunter2', 820, 1560, 1.0, 'angry', t, flip=-1, armL=(110 - 60 * sw, 85), armR=(-30, 70), prop=stick_prop(-0.6 - sw * 0.9, 190, C('5a3a20')))
    r = rng(21)
    for i in range(16):
        x_ = r.uniform(100, 980); y_ = r.uniform(1580, 1820); ph = r.uniform(0, 3)
        hp = abs(math.sin(lt * 5 + ph))
        rabbit(d, x_, y_, 0.75, r.choice((1, -1)), hp * 0.8, r.choice(COLS), face='happy' if hp > 0.5 else 'open', mouth='grin', look=(0, -3))
@huds
def o_h(img, t, lt):
    for k, t0 in enumerate((0.3, 0.9, 1.5)):
        if t0 <= lt < t0 + 0.35:
            hud_text(img, 'WHACK!' if k % 2 == 0 else 'SWISH!', 300 + k * 230, 520 + (k % 2) * 90, 80, (255, 255, 255), pop(lt, t0, 0.2), 1, -0.15 + k * 0.1)

# P 29.2-30.5: nothing worked (deadpan, buried)
@shot(29.2, 30.5, 'meadow', blur=True)
def p_(t, lt): return [K(0, 540, 1700, 1.6, 1.75, 0.0), K(1.3, 540, 1700, 1.6, 1.85, 0.0, 'l')], []
@draws
def p_d(d, t, lt):
    nap(d, 540, 1700, 1.6, 'deadpan', t, armL=(20, 70), armR=(-20, 70), blink=(0.7,))
    r = rng(30)
    for i in range(18):
        x_ = 540 + r.uniform(-330, 330); y_ = 1700 + r.uniform(-60, 130) - max(0, 160 - abs(x_ - 540)) * 0.9
        rabbit(d, x_, y_, 0.9, r.choice((1, -1)), 0, r.choice(COLS), face='closed' if i % 4 == 0 else 'open', look=(0, -4), ear=0.06 * math.sin(t * 4 + i), shadow_on=False)

# Q 30.5-33.2: retreat to the carriage
@shot(30.5, 33.2, 'meadow')
def q_(t, lt): return [(0, 380, 1250, 0.95, 0.0), (2.7, 1150, 1250, 1.0, 0.0, 'l')], []
@draws
def q_d(d, t, lt):
    carriage(d, 1420, 1520, 1.1, 0, 0, 'all')
    nx = lerp(150, 1120, smooth(clamp(lt / 2.6)))
    nap(d, nx, 1560, 1.0, 'scared', t, step=lt * 18, armL=(140, 80), armR=(-140, 80), bob=abs(math.sin(lt * 18)) * 12, lean=0.12)
    r = rng(40)
    for i in range(18):
        off = r.uniform(120, 900); y_ = r.uniform(1480, 1800)
        x_ = nx - off; hp = abs(math.sin(lt * 7 + i))
        rabbit(d, x_, y_, 0.6 + (y_ - 1480) / 800, 1, hp * 0.5, r.choice(COLS), face='happy', mouth='grin', stretch=hp * 0.6)
@huds
def q_h(img, t, lt): pass

# R 33.2-35.6: carriage flees, rabbits chase, one in the window
@shot(33.2, 35.6, 'meadow')
def r_(t, lt): return [(0, 480, 1250, 1.2, 0.0), (2.4, 1560, 1250, 1.2, 0.0, 'l')], []
@draws
def r_d(d, t, lt):
    cx = 600 + lt * 450
    b = abs(math.sin(lt * 12)) * 8
    carriage(d, cx, 1560, 1.1, -lt * 9, b, 'back')
    Q = d.sub(Aff(cx, 1560 - b, 1.1))
    nap(Q, -100, -150, 0.62, 'scared', t, armL=(150, 80), armR=(-20, 70), shadow_on=False)
    rabbit(Q, -86, -420, 0.42, -1, 0, 'spot', face='happy', mouth='grin', shadow_on=False)
    carriage(d, cx, 1560, 1.1, -lt * 9, b, 'front')
    r = rng(50)
    for i in range(20):
        off = r.uniform(300, 1300); y_ = r.uniform(1520, 1820); x_ = cx - off + math.sin(lt * 3 + i) * 30
        hp = abs(math.sin(lt * 8 + i))
        rabbit(d, x_, y_, 0.55 + (y_ - 1520) / 800, 1, hp * 0.6, r.choice(COLS), face='happy', mouth='grin', stretch=hp * 0.7)
@huds
def r_h(img, t, lt):
    if lt > 1.0: hud_text(img, 'TOO!', 540, 360, 130, (255, 214, 64), pop(lt, 1.0, 0.25), 1, 0.06)

# S 35.6-36.55: Why?
@shot(35.6, 36.55, 'blue')
def s_(t, lt): return [(0, 540, 1240, 1.0, 0.0), (0.95, 540, 1240, 1.08, 0.0, 'l')], []
@draws
def s_d(d, t, lt):
    rabbit(d, 540, 1420, 2.1, 1, 0, 'white', face='open', tilt=track(lt, [(0, 0.0), (0.15, 0.3)]), look=(-4, -4), ear=0.15)
@huds
def s_h(img, t, lt):
    hud_text(img, '?', 540, 380, 280, (255, 214, 64), pop(lt, 0.15, 0.3), 1, 0.12 * math.sin(lt * 6))

# T 36.55-38.25: not wild rabbits
@shot(36.55, 38.25, 'meadow', blur=True)
def t_(t, lt): return [(0, 540, 1240, 1.6, 0.0), (1.7, 540, 1240, 1.7, 0.0, 'l')], [0.75]
@draws
def t_d(d, t, lt):
    rabbit(d, 540, 1450, 1.9, 1, 0, 'grey', face='open', mouth='flat', brow=-1, look=(4, 0), ear=0.25)
    sx = 540; sy = 900
    L = d.sub(Aff(sx, sy, 1.0, -0.05))
    L.poly([(-200, -70), (200, -70), (200, 70), (-200, 70)], C('a87444'), INK, 6)
    spr = text_sprite('WILD', max(6, int(90 * L.k)), (250, 240, 220), 0.12)
    q = L.tp([(0, 0)])[0]; blit(L.img, spr, q[0], q[1])
    if lt > 0.75:
        u = clamp((lt - 0.75) / 0.15)
        L.line([(-190, -90), (lerp(-190, 190, u), lerp(-90, 90, u))], C('e23b3b'), 26)
        if lt > 0.9: L.line([(190, -90), (-190, 90)], C('e23b3b'), 26)

# U 38.25-40.1: tame farm rabbits
@shot(38.25, 40.1, 'farm')
def u_(t, lt): return [K(0, 560, 1640, 1.25, 1.35, 0.0), K(1.85, 560, 1640, 1.25, 1.45, 0.02, 'l')], []
@draws
def u_d(d, t, lt):
    person(d, 'farmer', 760, 1600, 1.15, 'happy', t, flip=-1, armL=(70 + 10 * math.sin(lt * 6), 70), armR=(-20, 70), blink=(0.9,))
    r = rng(60)
    for i in range(7):
        x_ = 240 + i * 75 + r.uniform(-20, 20); y_ = 1640 + (i % 2) * 80
        rabbit(d, x_, y_, 0.95, 1, abs(math.sin(lt * 6 + i)) * 0.15, COLS[i], face='happy', mouth='w', look=(5, -3))
@huds
def u_h(img, t, lt): tag(img, 'TAME FARM BUNNIES', t, 38.35, 40.05)

# V 40.1-42.5: rabbit POV, a man walks toward them
@shot(40.1, 42.5, 'meadow')
def v_(t, lt): return [(0, 540, 1330, 1.15, -0.03), (2.4, 540, 1300, 1.25, -0.03, 'l')], []
@draws
def v_d(d, t, lt):
    u = lt / 2.4
    sc_ = lerp(0.8, 1.15, u); y_ = lerp(1320, 1440, u)
    nap(d, 560, y_, sc_, 'smug', t, step=lt * 7, armL=(20, 70), armR=(-20, 70), bob=abs(math.sin(lt * 7)) * 5)
    for i, (x_, col) in enumerate(((170, 'brown'), (480, 'white'), (860, 'grey'))):
        perk = clamp((lt - 0.4 - i * 0.15) / 0.2)
        rabbit(d, x_, 1880, 1.6, -1 if x_ > 540 else 1, 0, col, face='wide' if perk > 0.5 else 'open', look=(0, -6), ear=0.25 * perk, mouth='o' if perk > 0.5 else 'w')
@huds
def v_h(img, t, lt): pass

# W 42.5-44.6: dinner time!
@shot(42.5, 44.6, 'farm')
def w_(t, lt): return [(0, 540, 1300, 1.25, 0.0), (2.1, 540, 1310, 1.38, 0.02, 'l')], [0.3]
@draws
def w_d(d, t, lt):
    r = rng(70)
    for i in range(5):
        x_ = 140 + i * 200; y_ = 1660 + (i % 2) * 70
        hp = abs(math.sin(lt * 7 + i)) * 0.35
        rabbit(d, x_, y_, 1.15, 1 if x_ < 540 else -1, hp, COLS[i], face='happy', mouth='grin', napkin=True, look=(0, -4), ear=0.15)
    if lt > 0.15:
        p = pop(lt, 0.15, 0.3)
        def inner(L):
            carrot(L, -60, 30, 1.0, -0.4); carrot(L, 50, 20, 0.9, 0.35)
            L.ell(0, 70, 90, 26, C('f6f1e6'), INK, 4)
        bubble(d, 540, 1030, 170, -60, 280, p, inner)
@huds
def w_h(img, t, lt):
    if lt > 0.5: hud_text(img, 'DINNER TIME!', 540, 300, 120, (255, 214, 64), pop(lt, 0.5, 0.3), 1, -0.04)

# ---------------- captions (one word, lowercase) ----------------
WORDS = json.load(open(os.path.join(HERE, 'work/words.json')))
TIM = json.load(open(os.path.join(HERE, 'work/timing.json')))
KEY = {'napoleon', 'europe', 'battle', 'bunnies', '1807', 'treaty', 'hunt', 'hundreds', 'opened', 'guns', "didn't", 'straight', 'swarmed', 'legs',
       'whips', 'nothing', 'carriage', 'too', 'why?', 'wild', 'tame', 'man', 'dinner'}
CAPS = []
ends = [b for a, b, _ in TIM]
for i, (a, b, w) in enumerate(WORDS):
    nxt = WORDS[i + 1][0] if i + 1 < len(WORDS) else 99
    pe = min([e for e in ends if e >= b - 0.01] or [b])
    t1 = min(nxt, max(b, pe + 0.15) if abs(b - pe) < 0.02 else nxt)
    t1 = min(t1, a + 1.2)
    disp = w.lower().replace('…', '').rstrip(',.').replace('...', '')
    CAPS.append((a, t1, disp))

def cap_text(img, txt, x, y, size, rgb, sc):
    spr = text_sprite(txt, int(size * S), rgb, 0.17)
    sh = spr.copy(); sh[..., :3] = 0
    k = max(3, int(14 * S) | 1)
    sh[..., 3] = cv2.GaussianBlur(sh[..., 3], (k, k), 0)
    blit(img, sh, x * S + 4 * S, y * S + 7 * S, sc, 0.7)
    blit(img, spr, x * S, y * S, sc)

def caption(img, t):
    for a, b, w in CAPS:
        if a - 0.02 <= t < b:
            key = re.sub(r"[!.,]", '', w) in KEY or w in KEY
            u = (t - a) / 0.16
            sc = 0.75 + 0.25 * back(u, 2.2) if u < 1 else 1.0
            cap_text(img, w, 540, 1190, 104, (255, 214, 64) if key else (255, 255, 255), sc)
            return

# ---------------- render ----------------
CUTS = [s_['t0'] for s_ in SH if s_['t0'] > 0]
def whip(img, f):
    for b in CUTS:
        df = f - int(round(b * FPS))
        if -2 <= df <= 1:
            p = (2 - abs(df + 0.5)) / 2.5; sh = (1 if df < 0 else -1) * p * OW * 0.18
            M2 = np.float32([[1, 0, sh], [0, 1, 0]])
            out = cv2.warpAffine(img, M2, (OW, OH), borderMode=cv2.BORDER_REPLICATE)
            k = max(1, int(abs(sh) * 0.5)) | 1
            img[:] = cv2.blur(out, (k, 1)); return

def render(f):
    t = f / FPS
    sh = next((s for s in SH if s['t0'] <= t < s['t1']), SH[-1])
    lt = t - sh['t0']
    keys, kicks = sh['cam'](t, lt)
    cx, cy, z, rot = cam_keys(keys, lt)
    cx += math.sin(t * 0.9) * 5; cy += math.cos(t * 0.7) * 4
    M = camM(cx, cy, z, rot, shake_at(lt, kicks))
    img = np.zeros((OH, OW, 3), np.uint8)
    kind = sh['bg'] + ('_blur' if sh['blur'] else '')
    bg = bgimg(kind); ox, oy = BGOFF[kind]
    Mb = M @ np.array([[1 / S, 0, -ox], [0, 1 / S, -oy], [0, 0, 1]])
    cv2.warpAffine(bg, Mb[:2], (OW, OH), dst=img, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    d = D(img, M)
    sh['draw'](d, t, lt)
    grade(img, f)
    if os.environ.get('NOTEXT'): return img
    if sh.get('hud'): sh['hud'](img, t, lt)
    whip(img, f)
    caption(img, t)
    return img

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stills':
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        for tt in sys.argv[3].split(','):
            fi = int(float(tt) * FPS); cv2.imwrite(f'{out}/s_{float(tt):05.2f}.jpg', render(fi))
    else:
        out = sys.argv[2]; a, b = map(int, sys.argv[3].split('-')); os.makedirs(out, exist_ok=True)
        for fi in range(a, min(b, NF - 1) + 1):
            cv2.imwrite(f'{out}/f{fi:05d}.jpg', render(fi), [cv2.IMWRITE_JPEG_QUALITY, 92])
