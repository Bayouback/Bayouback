# -*- coding: utf-8 -*-
# Снимаем робота с плитки. По цвету его не отделить — корпус такой же белый,
# как и сама плитка, поэтому идём по краям: у робота есть контур, а плитка
# и фон внутри гладкие. Заливаем от углов всё, где градиент ниже порога.
import sys, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)

EDGE = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0   # порог «это край»
GROW = int(sys.argv[4]) if len(sys.argv) > 4 else 3        # на сколько подъесть фон

img = Image.open(SRC).convert('RGB')
a = np.asarray(img).astype(np.float32)
h, w = a.shape[:2]
grey = a @ np.array([.299, .587, .114], dtype=np.float32)

# карта краёв
edges = ndimage.gaussian_gradient_magnitude(grey, sigma=1.4)
smooth = edges < EDGE

lab, n = ndimage.label(smooth)

# что считаем фоном: углы кадра (задник) и точки на плитке рядом с её углами
seeds = [(6, 6), (6, w - 7), (h - 7, 6), (h - 7, w - 7)]
inset = int(min(h, w) * 0.19)
seeds += [(inset, inset), (inset, w - inset), (h - inset, inset), (h - inset, w - inset)]

bg_ids = {lab[y, x] for y, x in seeds if lab[y, x] != 0}
bg = np.isin(lab, list(bg_ids))

# подъедаем мягкую кромку, чтобы по контуру не остался серый ореол плитки
bg = ndimage.binary_dilation(bg, iterations=GROW)
robot = ~bg
robot = ndimage.binary_fill_holes(robot)

# выбрасываем мелкий мусор — оставляем самую крупную область
lab2, n2 = ndimage.label(robot)
if n2 > 1:
    sizes = ndimage.sum(robot, lab2, range(1, n2 + 1))
    robot = lab2 == (int(np.argmax(sizes)) + 1)

alpha = ndimage.gaussian_filter(robot.astype(np.float32), 1.1)
alpha = np.clip((alpha - .35) / .35, 0, 1)   # чуть поджимаем, край остаётся мягким

rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(OUT / (SRC.stem + '-alpha.png'))

ys, xs = np.where(alpha > .04)
print(SRC.name, f'{w}×{h}', '| доля робота:', round(float(robot.mean()) * 100, 1), '%',
      '| рамка:', (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))

# контрольная картинка: маска рядом с оригиналом
Image.fromarray((alpha * 255).astype(np.uint8), 'L').save(OUT / (SRC.stem + '-mask.png'))
