import sys, os, math, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from char4 import toon4, EMO
V2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v3zip', 'fableverse_engine', 'v2'); sys.path.insert(0, V2)
from rig import D, Aff, text_sprite, blit, C
from char3 import toon as toon3
from face import expr
def canvas(w, h, top=(214, 230, 242), bot=(178, 198, 214)):
    img = np.zeros((h, w, 3), np.uint8)
    for y in range(h): img[y] = [int(top[i] + (bot[i] - top[i]) * y / h) for i in range(3)]
    return img
def label(img, txt, x, y, size=34, col=(40, 30, 40)):
    blit(img, text_sprite(txt, size, (255, 255, 255), 0.18, None, col), x, y)
# ---- sheet 1: old vs new + 12 reactions
W1 = 2160; img = canvas(W1, 2960)
label(img, 'OLD (v3)', 300, 60, 52, (120, 40, 40)); label(img, 'NEW (v4)', 1500, 60, 52, (40, 110, 60))
d = D(img, Aff())
toon3(d, 200, 900, 1.55, 'napoleon', expr('neutral')); toon3(d, 470, 900, 1.55, 'napoleon', expr('worried'))
toon4(d, 1350, 900, 1.5, 'napoleon', 'happy', pose=dict(aL=(-40, 90), elL=-70)); toon4(d, 1680, 900, 1.5, 'napoleon', 'worried', pose=dict(aL=(150, 100), elL=-40, aR=(-150, 100), elR=40))
cv2.line(img, (1080, 120), (1080, 960), (150, 140, 130), 3)
label(img, 'NEW FACE REACTIONS', 1080, 1010, 50)
emos = ['neutral', 'happy', 'proud', 'smug', 'worried', 'scared', 'shocked', 'angry', 'sad', 'deadpan', 'excited', 'confused']
for i, e in enumerate(emos):
    cx = 180 + (i % 6) * 360; cy = 1330 + (i // 6) * 800
    sub = D(img, Aff(cx, cy + 640, 1.6))
    toon4(sub, 0, 0, 1.0, 'napoleon', e, shadow_on=False,
          pose=dict(aL=(150, 100), elL=-30, aR=(-150, 100), elR=30) if e in ('scared', 'excited', 'shocked') else dict(aL=(60, 100), elL=60, aR=(-60, 100), elR=-60) if e == 'angry' else None)
    label(img, e.upper(), cx, cy + 690, 36)
cv2.imwrite('sheet_reactions.png', img)
# ---- sheet 2: cast
img = canvas(2160, 1150); d = D(img, Aff())
cast = [('napoleon', 'proud'), ('berthier', 'smug'), ('tsar', 'happy'), ('hunter', 'determined' if 'determined' in EMO else 'angry'), ('farmer', 'happy')]
for i, (w, e) in enumerate(cast):
    x = 230 + i * 425
    toon4(d, x, 1000, 1.65, w, e, pose=dict(aL=(-40, 90), elL=-70) if w == 'napoleon' else None)
    label(img, w.upper(), x, 1090, 40)
cv2.imwrite('sheet_cast.png', img)
print('ok')
