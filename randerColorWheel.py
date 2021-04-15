# -*- coding: utf-8 -*-

import numpy as np

from nyasQuantumCalculate.Utils import ColorWheel2RGB


figSize = 500
bgColor = "#262626"

wheelRange = (0.4, 0.9)
fadeWidth = 0.05

##############################################################################

bgc = np.array((int(bgColor[1:3], 16),
                int(bgColor[3:5], 16),
                int(bgColor[5:], 16)), np.uint8)

fig = np.ones((figSize, figSize, 3), np.uint8) * bgc

rsize_2 = 2 / figSize
RRin = wheelRange[0] * wheelRange[0]
RRout = wheelRange[1] * wheelRange[1]
k = 1 / fadeWidth
b0 = wheelRange[0] * k
b1 = wheelRange[1] * k

totalRun = figSize * figSize
countRun = 0

for yf in range(figSize):
    y = yf * rsize_2 - 1
    for xf in range(figSize):
        x = xf * rsize_2 - 1
        rr = x * x + y * y
        if RRin <= rr <= RRout:
            r = np.sqrt(rr)
            color = np.array(ColorWheel2RGB(np.angle(x - 1j * y)), np.uint8)
            alpha = np.clip(min(k * r - b0, -k * r + b1), 0., 1.)
            color = color * alpha + bgc * (1. - alpha)
            color = np.clip(color, 0., 255.)
            fig[yf, xf] = color
        countRun += 1
        prop = countRun / totalRun
        barL = int(50 * prop - 1)
        print(f"[{100 * prop:.1f}%%] "
            f"[{'=' * max(barL, 0)}>{' ' * max(49 - barL, 0)}]", end='\r')
print()

###############################################################################

file_name = "ColorWheel.png"

try:
    import cv2
except ModuleNotFoundError:
    try:
        from PIL import Image
    except ModuleNotFoundError:
        from matplotlib import pyplot as plt
        plt.imsave(file_name, fig)
    else:
        Image.fromarray(fig).save(file_name)
else:
    cv2.imwrite(file_name, fig[..., ::-1])
