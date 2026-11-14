"""0-6 s comparison: BG=blender|paint python3 comp5.py frames OUT a-b  |  stills OUT t1,t2
Same v3 toons, camera, look, captions for both; only the background plates differ."""
import os, sys, json, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(HERE, '..', 'v3zip', 'fableverse_engine', 'v2')
sys.path.insert(0, V2)
import numpy as np, cv2
from rig import *
from char3 import toon, hat3, WHO
from face import expr, timeline
import props as PR
import look as LK

MODE = os.environ.get('BG', 'blender')
W, H, FPS = 1080, 1920, 30
S = float(os.environ.get('S', '0.5'))
OW, OH = int(round(W * S)), int(round(H * S))
DUR = 6.0; NF = int(DUR * FPS)
PDIR = os.path.join(HERE, 'plates' if MODE == 'blender' else 'paint')
def _anc(n):
    p = os.path.join(HERE, 'plates', n + '.json')
    if os.path.exists(p): return json.load(open(p))['points']
    return dict(feet=(540, 2350, 1), head=(540, 1050, 1)) if n == 'cu' else dict(feet=(540, 1700, 1), head=(540, 1100, 1))
ANC = {n: _anc(n) for n in ('hero', 'map', 'cu', 'rab')}
TOON_H = 368.0     # toon design height (feet -> top of head) for a 1.7 m person
RAB_H = 230.0      # rabbit design height incl. ears for 0.38 m

_pl = {}
def plate(name):
    if name not in _pl:
        im = cv2.imread(os.path.join(PDIR, name + '.png'))
        if MODE == 'blender':
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); hsv[..., 1] = cv2.convertScaleAbs(hsv[..., 1], alpha=1.18); im = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        _pl[name] = im
    return _pl[name]

def camM(cx, cy, z, rot, shake=(0, 0)):
    return Aff(0, 0, S) @ Aff(W / 2 + shake[0], H / 2 + shake[1]) @ Aff(0, 0, z, rot) @ Aff(-cx, -cy)

def cam_keys(keys, t):
    if t <= keys[0][0]: return keys[0][1:5]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = (t - a[0]) / max(1e-6, b[0] - a[0]); e = b[5] if len(b) > 5 else 's'
            u = smooth(u) if e == 's' else eout(u) if e == 'o' else u
            return tuple(lerp(a[i], b[i], u) for i in range(1, 5))
    return keys[-1][1:5]

def shake_at(t, kicks, amp=16):
    sx = sy = 0
    for k in kicks:
        dt = t - k
        if 0 <= dt < 0.3: a = amp * (1 - dt / 0.3); sx += a * math.sin(dt * 90); sy += a * math.cos(dt * 70)
    return sx, sy

def anchor(name, k='feet'):
    p = ANC[name][k]; return p[0], p[1]
def toon_sc(name, ref=TOON_H):
    f = ANC[name]['feet']; h = ANC[name]['head']; return (f[1] - h[1]) / ref

def pop(t, t0, dur=0.25):
    return 0.0 if t < t0 else back((t - t0) / dur, 2.2)
def hud_text(img, txt, x, y, size, rgb=(255, 255, 255), scale=1.0, alpha=1.0, rot=0.0):
    blit(img, text_sprite(txt, int(size * S), rgb, 0.15), x * S, y * S, scale, alpha, rot)

# ---------------- shots ----------------
SH = []
def shot(t0, t1, plate_name, sun=None):
    def deco(fn): SH.append(dict(t0=t0, t1=t1, cam=fn, plate=plate_name, sun=sun)); return fn
    return deco
def reg(**kw): SH[-1].update(kw)

# S1 0-1.15 low hero angle
@shot(0.0, 1.15, 'hero', sun=(0.86, 0.55))
def c1(t, lt): return [(0, 540, 960, 1.0, -0.02), (1.15, 548, 935, 1.08, -0.035, 'l')], []
def d1(d, t, lt):
    fx, fy = anchor('hero'); sc = toon_sc('hero') * 2.1
    fy = fy + 360; fx = fx - 40
    PR.flag(d, fx + 170, fy - 140, sc * 0.75, t)
    P = timeline([(0, expr('neutral', smile=0.7, brow=(0.35, 0.6), bang=(0.2, -0.1))), (0.75, expr('smug', lid=(0.18, 0.15), low=(0.0, 0.0)))], lt)
    toon(d, fx, fy, sc, 'napoleon', P, dict(aL=(-40, 80), elL=-62, aR=(-18, 118), tilt=-0.04, bob=math.sin(t * 2.2) * 2), blink=0.55 < lt < 0.65)
reg(draw=d1)

# S2 1.15-2.9 map: Europe turns red, bicorne stamp lands at 2.42
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
    'russia': [(760, 720), (800, 560), (1000, 500), (1060, 520), (1060, 1000), (900, 960), (800, 900), (740, 860), (800, 800)],
    'scandi': [(560, 560), (620, 420), (720, 380), (760, 460), (700, 560), (660, 640), (620, 600)],
    'balkans': [(660, 930), (760, 920), (800, 900), (900, 960), (860, 1060), (780, 1100), (720, 1040)],
    'denmark': [(560, 640), (590, 610), (600, 690), (570, 690)],
}
CONQ = [('france', 0.2), ('low', 0.42), ('italy', 0.62), ('germany', 0.82), ('austria', 1.0), ('spain', 1.15), ('poland', 1.3)]
CW, CH = 600, 840
def chaikin(pts, n=3):
    p = np.array(pts, float)
    for _ in range(n):
        q = np.roll(p, -1, 0); p = np.stack([0.75 * p + 0.25 * q, 0.25 * p + 0.75 * q], 1).reshape(-1, 2)
    return [tuple(x) for x in p]
MAP_REG = {k: chaikin(v, 1) for k, v in MAP_REG.items()}
def mp(p): return ((p[0] - 120) / 960 * CW * 0.92 + CW * 0.04, (p[1] - 360) / 860 * CH * 0.78 + CH * 0.14)

def map_layer(lt):
    """RGBA map drawing in parchment space"""
    cv_ = np.zeros((CH, CW, 4), np.uint8); d = D(cv_, Aff())
    def poly(pts, col, a):
        q = (np.array([mp(p) for p in pts]) * 16).astype(np.int32)
        cv2.fillPoly(cv_, [q], (*col, a), cv2.LINE_AA, shift=4)
    for nm, pts in MAP_REG.items(): poly(pts, C('c9a77a'), 90)
    for nm, t0 in CONQ:
        if lt >= t0:
            u = min(1.0, pop(lt, t0, 0.22)); pts = np.array([mp(p) for p in MAP_REG[nm]]); c = pts.mean(0)
            q = (((pts - c) * u + c) * 16).astype(np.int32)
            cv2.fillPoly(cv_, [q], (*C('b52a22'), 205), cv2.LINE_AA, shift=4)
    for nm, pts in MAP_REG.items():
        q = (np.array([mp(p) for p in pts + [pts[0]]]) * 16).astype(np.int32)
        cv2.polylines(cv_, [q], True, (*C('4a2e1a'), 230), 3, cv2.LINE_AA, shift=4)
    spr = text_sprite('EUROPE', 64, (60, 40, 30), 0.0)
    h_, w_ = spr.shape[:2]; x0, y0 = CW // 2 - w_ // 2, 40
    cv_[y0:y0 + h_, x0:x0 + w_][spr[..., 3] > 0] = np.concatenate([spr[..., :3][..., ::-1], spr[..., 3:]], 2)[spr[..., 3] > 0]
    return cv_

def map_H(M):
    pts = np.float32([ANC['map'][k][:2] for k in ('tl', 'tr', 'br', 'bl')])
    scr = (np.c_[pts, np.ones(4)] @ M.T)[:, :2].astype(np.float32)
    return cv2.getPerspectiveTransform(np.float32([[0, 0], [CW, 0], [CW, CH], [0, CH]]), scr)

def par_to_design(p):
    """parchment-space point -> plate design coords (bilinear on the 4 corners)"""
    u, v = p[0] / CW, p[1] / CH
    tl, tr, br, bl = [np.array(ANC['map'][k][:2]) for k in ('tl', 'tr', 'br', 'bl')]
    return tuple((1 - v) * ((1 - u) * tl + u * tr) + v * ((1 - u) * bl + u * br))

@shot(1.15, 2.9, 'map')
def c2(t, lt): return [(0, 540, 960, 1.0, 0.0), (1.75, 540, 985, 1.12, 0.01, 'o')], [1.27]
def d2(d, t, lt):
    M = d.M
    lay = map_layer(lt)
    Hm = map_H(M)
    w = cv2.warpPerspective(lay, Hm, (OW, OH))
    a = w[..., 3:4].astype(np.float32) / 255
    d.img[:] = (d.img * (1 - a) + w[..., :3][..., ::-1].astype(np.float32) * a).astype(np.uint8) if False else (d.img * (1 - a) + w[..., :3].astype(np.float32) * a).astype(np.uint8)
    if lt > 1.15:
        fx, fy = par_to_design(mp((400, 890)))
        u = clamp((lt - 1.15) / 0.12)
        scale = lerp(2.2, 1.0, u * u)
        if u >= 1: PR_shadow = shadow(d.sub(Aff(fx, fy + 30, 1.0)), 0, 0, 120, 30, 0.45)
        Hh = d.sub(Aff(fx, fy + 90, 0.95 * scale, -0.08))
        hat3(Hh, 'bicorne', WHO['napoleon'])
reg(draw=d2)

# S3 2.9-4.75 close-up: smug -> worried on "lost"
@shot(2.9, 4.75, 'cu', sun=(0.82, 0.4))
def c3(t, lt): return [(0, 540, 960, 1.0, 0.0), (1.85, 540, 945, 1.1, 0.015, 'l')], []
def d3(d, t, lt):
    fx = 540; sc = 3.9; fy = 770 + 286 * sc
    P = timeline([(0, expr('smug', lid=(0.25, 0.2))), (0.62, expr('worried', look=(-0.6, 0.15))), (1.05, expr('worried', look=(0.6, 0.15))), (1.45, expr('worried', look=(0.0, 0.3)))], lt, 0.1)
    toon(d, fx, fy, sc, 'napoleon', P, dict(aL=(-40, 80), elL=-62, aR=(-18, 118), tilt=0.0 if lt < 0.62 else 0.06, bob=math.sin(t * 2) * 1.5), blink=1.25 < lt < 1.35)
reg(draw=d3)

# S4 4.75-6.0 bunny pops up, title
@shot(4.75, 6.0, 'rab', sun=(0.84, 0.35))
def c4(t, lt): return [(0, 540, 960, 1.0, 0.0), (1.25, 540, 955, 1.06, 0.0, 'l')], [0.12]
def d4(d, t, lt):
    fx, fy = anchor('rab'); sc = toon_sc('rab', RAB_H)
    p = back(clamp((lt - 0.04) / 0.3), 2.0)
    PR.rabbit(d, fx, fy + (1 - p) * 260 * sc, sc, 1, 0, 'front', face='wide' if lt > 0.5 else 'open', ear=1.0 if lt > 0.3 else 0.0,
              tilt=0.12 * math.sin(max(0, lt - 0.6) * 5) if lt > 0.6 else 0.0, blink=0.95 < lt < 1.05)
reg(draw=d4)
def h4(img, t, lt):
    if lt > 0.15:
        p = pop(lt, 0.15, 0.3)
        hud_text(img, 'NAPOLEON', 540, 250, 108, (255, 255, 255), p)
        hud_text(img, 'vs', 540, 360, 74, (255, 214, 64), pop(lt, 0.3, 0.3))
        hud_text(img, 'BUNNIES', 540, 470, 132, (255, 150, 170), pop(lt, 0.42, 0.3))
SH[-1]['hud'] = h4

def fg_grass(img, M, t, seed=8):
    """out-of-focus foreground grass blades (paint version only, Blender has real DOF grass)"""
    def draw():
        d = D(img, M); r = np.random.default_rng(seed)
        for i in range(34):
            x = r.uniform(-100, 1180); hh = r.uniform(180, 420); w = r.uniform(14, 26); sw = math.sin(t * 1.6 + i) * 18 + r.uniform(-40, 40)
            y = 2000; tip = (x + sw, y - hh)
            pts = list(bez((x - w, y), (x - w * 0.4 + sw * 0.3, y - hh * 0.6), tip, 8)) + list(bez(tip, (x + w * 0.4 + sw * 0.3, y - hh * 0.6), (x + w, y), 8))
            d.poly(pts, C('3e6a26') if i % 2 else C('4f7f30'), None)
    LK.dof_layer(img, draw, 40 * S)

# ---------------- captions ----------------
WORDS = json.load(open(os.path.join(HERE, '..', 'napoleon', 'work', 'words.json')))
TIM = json.load(open(os.path.join(HERE, '..', 'napoleon', 'work', 'timing.json')))
KEY = {'napoleon', 'europe', 'battle', 'bunnies'}
ENDS = [b for a, b, _ in TIM]
CAPS = []
for i, (a, b, w) in enumerate(WORDS):
    nxt = WORDS[i + 1][0] if i + 1 < len(WORDS) else 99
    t1 = nxt if any(abs(b - e) > 0.02 for e in [min(ENDS, key=lambda e: abs(e - b))]) else min(nxt, b + 0.2)
    t1 = min(t1, a + 1.1, nxt)
    CAPS.append((a, t1, w.lower().replace('…', '').replace('...', '').rstrip(',.')))

def cap_text(img, txt, x, y, size, rgb, sc):
    spr = text_sprite(txt, int(size * S), rgb, 0.17)
    sh = spr.copy(); sh[..., :3] = 0; k = max(3, int(14 * S) | 1)
    sh[..., 3] = cv2.GaussianBlur(sh[..., 3], (k, k), 0)
    blit(img, sh, x * S + 4 * S, y * S + 7 * S, sc, 0.7); blit(img, spr, x * S, y * S, sc)

def caption(img, t):
    for a, b, w in CAPS:
        if a - 0.02 <= t < b:
            u = (t - a) / 0.16; sc = 0.75 + 0.25 * back(u, 2.2) if u < 1 else 1.0
            cap_text(img, w, 540, 1190, 104, (255, 214, 64) if re.sub(r'[^a-z]', '', w) in KEY else (255, 255, 255), sc)
            return

CUTS = [s_['t0'] for s_ in SH if s_['t0'] > 0]
def whip(img, f):
    for b in CUTS:
        df = f - int(round(b * FPS))
        if -2 <= df <= 1:
            p = (2 - abs(df + 0.5)) / 2.5; sh = (1 if df < 0 else -1) * p * OW * 0.18
            out = cv2.warpAffine(img, np.float32([[1, 0, sh], [0, 1, 0]]), (OW, OH), borderMode=cv2.BORDER_REPLICATE)
            k = max(1, int(abs(sh) * 0.5)) | 1; img[:] = cv2.blur(out, (k, 1)); return

MOTES = LK.Motes(60, 5)
def render(f):
    t = f / FPS
    sh = next((s for s in SH if s['t0'] <= t < s['t1']), SH[-1]); lt = t - sh['t0']
    keys, kicks = sh['cam'](t, lt)
    cx, cy, z, rot = cam_keys(keys, lt)
    M = camM(cx, cy, z, rot, shake_at(lt, kicks))
    pl = plate(sh['plate']); ps = pl.shape[1] / 1296.0
    Mb = M @ np.array([[1 / ps, 0, -108], [0, 1 / ps, -192], [0, 0, 1]])
    img = cv2.warpAffine(pl, Mb[:2], (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    d = D(img, M)
    sh['draw'](d, t, lt)
    if MODE == 'paint' and sh['plate'] in ('rab', 'cu'): fg_grass(img, M, t, 8 if sh['plate'] == 'rab' else 11)
    # shared premium look
    if sh.get('sun'):
        sx, sy = sh['sun']; LK.god_rays(img, OW * sx, OH * sy, t, 0.13, (150, 210, 255), 9, 1.3, math.pi * 0.62, 1.5)
        MOTES.draw(img, t, cx / W * 0.3, cy / H * 0.3, (190, 230, 255), 0.7)
    LK.bloom(img, 225, 0.22)
    LK.grade(img, 'warm', 1.08)
    LK.contrast(img, 1.06)
    y_, x_ = np.mgrid[0:OH, 0:OW]
    vg = (1 - 0.3 * np.clip(np.sqrt(((x_ - OW / 2) / (OW / 2)) ** 2 + ((y_ - OH / 2) / (OH / 2)) ** 2) - 0.55, 0, 1) ** 1.5)[..., None]
    img[:] = (img * vg).astype(np.uint8)
    LK.grain(img, f, 4)
    if os.environ.get('NOTEXT'): return img
    if sh.get('hud'): sh['hud'](img, t, lt)
    whip(img, f)
    caption(img, t)
    return img

if __name__ == '__main__':
    mode = sys.argv[1]; out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    if mode == 'stills':
        for tt in sys.argv[3].split(','): cv2.imwrite(f'{out}/s_{float(tt):05.2f}.jpg', render(int(float(tt) * FPS)))
    else:
        a, b = map(int, sys.argv[3].split('-'))
        for fi in range(a, min(b, NF - 1) + 1): cv2.imwrite(f'{out}/f{fi:05d}.jpg', render(fi), [cv2.IMWRITE_JPEG_QUALITY, 93])
