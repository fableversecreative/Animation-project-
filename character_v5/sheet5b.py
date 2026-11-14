import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import char5
from char5 import toon5
from rig import D, Aff, text_sprite, blit
def canvas(w, h, top=(214, 230, 242), bot=(178, 198, 214)):
    img = np.zeros((h, w, 3), np.uint8)
    for y in range(h): img[y] = [int(top[i] + (bot[i] - top[i]) * y / h) for i in range(3)]
    return img
def label(img, txt, x, y, size=34, col=(40, 30, 40)): blit(img, text_sprite(txt, size, (255, 255, 255), 0.18, None, col), x, y)
cast = [('napoleon', 'proud', dict(aL=(-30, 100), elL=-70)), ('berthier', 'smug', None), ('tsar', 'happy', None), ('hunter', 'determined', None), ('farmer', 'neutral', None)]
for tag, arms in (('A', 'thin'), ('B', 'thick')):
    char5.STYLE.update(legs='thick', arms=arms)
    img = canvas(2160, 1250); d = D(img, Aff())
    label(img, 'OPTION %s: v5 head + v4 legs + %s arms' % (tag, 'thin stick' if arms == 'thin' else 'thick gloved'), 1080, 60, 46)
    for i, (w, e, p) in enumerate(cast):
        x = 230 + i * 425; toon5(d, x, 1100, 1.6, w, e, pose=p); label(img, w.upper(), x, 1190, 40)
    cv2.imwrite('/home/user/Animation-project-/character_v5/Characters_v5_option%s.jpg' % tag, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
print('ok')
