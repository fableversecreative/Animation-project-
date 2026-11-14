import sys, os, math, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from char5 import toon5, EMO
from rig import D, Aff, text_sprite, blit, C
def canvas(w, h, top=(214, 230, 242), bot=(178, 198, 214)):
    img = np.zeros((h, w, 3), np.uint8)
    for y in range(h): img[y] = [int(top[i] + (bot[i] - top[i]) * y / h) for i in range(3)]
    return img
def label(img, txt, x, y, size=34, col=(40, 30, 40)): blit(img, text_sprite(txt, size, (255, 255, 255), 0.18, None, col), x, y)
emos = ['neutral', 'proud', 'smug', 'worried', 'scared', 'shocked', 'angry', 'sad', 'deadpan', 'happy', 'determined', 'confused']
img = canvas(2160, 2000)
label(img, 'NAPOLEON v5 - FACE REACTIONS', 1080, 60, 50)
for i, e in enumerate(emos):
    cx = 180 + (i % 6) * 360; cy = 120 + (i // 6) * 940
    sub = D(img, Aff(cx, cy + 780, 1.45))
    pose = dict(aL=(150, 120), elL=-30, aR=(-150, 120), elR=30) if e in ('scared', 'shocked') else dict(aL=(-30, 100), elL=-70) if e == 'proud' else dict(aL=(70, 110), elL=70, aR=(-70, 110), elR=-70) if e == 'angry' else None
    toon5(sub, 0, 0, 1.0, 'napoleon', e, shadow_on=False, pose=pose)
    label(img, e.upper(), cx, cy + 840, 36)
cv2.imwrite('sheet5_reactions.png', img)
# cast on a real Blender background (close-up field plate, blurred)
bg = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cmp5', 'plates', 'cu.png'))
bg = cv2.resize(bg, (2160, int(2160 * bg.shape[0] / bg.shape[1])))[600:1900]
img = cv2.GaussianBlur(bg, (0, 0), 6).copy(); d = D(img, Aff())
cast = [('napoleon', 'proud', dict(aL=(-30, 100), elL=-70)), ('berthier', 'smug', None), ('tsar', 'happy', None), ('hunter', 'determined', None), ('farmer', 'neutral', dict(step=0.9, knee=0.6))]
for i, (w, e, p) in enumerate(cast):
    x = 230 + i * 425
    toon5(d, x, 1150, 1.55, w, e, pose=p)
    label(img, w.upper(), x, 1240, 42)
cv2.imwrite('sheet5_cast.png', img)
print('ok')
