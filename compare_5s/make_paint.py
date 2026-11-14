"""Painted (no-Blender) plates in the same 1.2x-overscan plate convention as plates.py.
Uses the v3 engine's 2.5D painted sets (napoleon_rabbits bgimg) + v2 textures for the map table."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ['S'] = '0.6'
NR = os.path.join(HERE, '..', 'v3zip', 'fableverse_engine', 'napoleon_rabbits')
V2 = os.path.join(HERE, '..', 'v3zip', 'fableverse_engine', 'v2')
sys.path.insert(0, NR); os.chdir(NR)
import numpy as np, cv2
import render as NRR
sys.path.insert(0, V2)
import set25d as S25
from rig import D, Aff, C, INK, shade

PS = 0.6; PW, PH = int(1296 * PS), int(2304 * PS)
OUT = os.path.join(HERE, 'paint'); os.makedirs(OUT, exist_ok=True)

def nr_plate(kind, cx, cy, z):
    bg = NRR.bgimg(kind); ox, oy = NRR.BGOFF[kind]
    M = np.float32([[1 / z, 0, (cx - 648 / z + ox) * PS], [0, 1 / z, (cy - 1152 / z + oy) * PS]])
    return cv2.warpAffine(bg, M, (PW, PH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)

cv2.imwrite(f'{OUT}/hero.png', nr_plate('meadow', 540, NRR.HZ - 260, 1.0))
cv2.imwrite(f'{OUT}/cu.png', nr_plate('meadow_blur', 540, 1120, 1.5))
cv2.imwrite(f'{OUT}/rab.png', nr_plate('meadow_blur', 540, 1260, 1.9))

# map table: painted wood + parchment with bump shading, 2D brass compass + candle + coins + seal
img = np.zeros((PH, PW, 3), np.uint8)
wood = S25.tex_wood_floor(1024, 2048, 150, 11, (C('5a3a22'), C('8a5a34'), C('b07a48'), C('c99566')))
img[:] = cv2.resize(wood, (PW, PH))
parch = S25.tex_parchment(700, 960)
corners = json.load(open(os.path.join(HERE, 'plates', 'map.json')))['points'] if os.path.exists(os.path.join(HERE, 'plates', 'map.json')) else \
    json.load(open(os.path.join(HERE, 'test', 'map.json')))['points']
dst = np.float32([[(corners[k][0] + 108) * PS, (corners[k][1] + 192) * PS] for k in ('tl', 'tr', 'br', 'bl')])
src = np.float32([[0, 0], [parch.shape[1], 0], [parch.shape[1], parch.shape[0]], [0, parch.shape[0]]])
Hm = cv2.getPerspectiveTransform(src, dst)
sh = np.zeros((PH, PW), np.float32); cv2.fillPoly(sh, [(dst + [10, 14]).astype(np.int32)], 1.0); sh = cv2.GaussianBlur(sh, (41, 41), 0)
img[:] = (img * (1 - 0.45 * sh[..., None])).astype(np.uint8)
pw = cv2.warpPerspective(parch, Hm, (PW, PH)); m = cv2.warpPerspective(np.ones(parch.shape[:2], np.float32), Hm, (PW, PH))[..., None]
img[:] = (img * (1 - m) + pw * m).astype(np.uint8)
d = D(img, Aff(108 * PS, 192 * PS, PS))
def P(k): return corners[k][0], corners[k][1]
(tlx, tly), (brx, bry) = P('tl'), P('br')
cx, cy = brx - 40, bry + 40                        # compass near bottom-right corner
d.ell(cx, cy, 120, 120, C('b8862e'), INK, 6); d.ell(cx, cy, 100, 100, C('f1e6c8'), INK, 3)
for k in range(8):
    a = k * math.pi / 4; d.line([(cx + math.cos(a) * 70, cy + math.sin(a) * 70), (cx + math.cos(a) * 92, cy + math.sin(a) * 92)], C('6a5038'), 3)
d.poly([(cx - 8, cy), (cx + 60, cy - 50), (cx + 8, cy)], C('b8302a'), INK, 2); d.ell(cx - 40, cy - 40, 30, 16, C('ffffff'), None, 0, ang=-0.7)
kx, ky = tlx + 30, tly - 20                        # candle top-left
d.ell(kx, ky + 40, 100, 60, C('c99a3a'), INK, 5); d.ell(kx, ky, 46, 46, C('efe3c4'), INK, 4); d.ell(kx, ky - 4, 14, 22, C('ffd27a'), None, 0)
ov = img.copy(); D(ov, d.M).ell(kx, ky, 260, 260, C('ffcf80'), None, 0); img[:] = cv2.addWeighted(ov, 0.18, img, 0.82, 0)
for i in range(3): d.ell(tlx + 120 + i * 50, bry + 30 + i * 18, 34, 34, C('d9a640'), INK, 3)
d.ell(tlx + 40, bry + 10, 50, 50, C('9a1e22'), INK, 4)
S25_shade = S25.bump_shade if hasattr(S25, 'bump_shade') else None
cv2.imwrite(f'{OUT}/map.png', img)
print('paint plates ok', img.shape)
