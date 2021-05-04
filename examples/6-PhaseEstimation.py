# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from numpy import pi, sqrt
from nyasQuantumCalculate import *


Options.autoNormalize = False

"""细节可以参考 https://www.bilibili.com/read/cv10995770"""


###############################################################################

# 需要求特征值的位门
U = Rx(2*pi * sqrt(2))

###############################################################################
"""这个位门U有两个特征态和特征值
|u1❭ = |+❭; λ1 = exp(-pi*i*sqrt(2))
|u2❭ = |-❭; λ2 = exp( pi*i*sqrt(2))

相位估计是求特征值exp(2*pi*i*φ)里的φ, 其中φ取值[0,1).
也就是说U里的两个相位Φ为 φ1 = 1-sqrt(2)/2; φ2 = sqrt(2)/2
"""

###############################################################################

# 初始化量子位系统, n为求解精度
n = 8
qbsys = QubitsSystem(n + 1)
B = qbsys[0]
A = qbsys[1:]

# 制备叠加特征态, 因为这里的叠加特征态是|0❭, 所以什么也不做
# 需要注意的是叠加特征态在运行相位估计之后会与相位量子位纠缠在一起
# 这时候是无法抛弃储存特征态的量子位的

# 相位评估电路
ApplyToEach(Builtin.H, A)
for i, qb in enumerate(A):
    for _ in range(2 ** i):
        Controlled(U, qb.asQubits(), B)
# 因为上面的控制顺序已经反序, 则QFT并不需要再次反序
with TemporaryOptions.QFTswap(False):
    Builtin.IQFT(A)

# 加一个H门是为了可视化更明显, 不加H门之前系统总状态有4个峰值
# 加了H门后变为两个峰值, 看上去像是改变了相位估计的结果, 但实际上是没有的
Builtin.H(B)
# 查看目前系统的总状态
DumpSystemFig(qbsys)
# 测量量子位, 重置系统, 输出
result = Builtin.MA(A)
Builtin.RA(qbsys[:])
print("测得φ为", Utils.Bools2Int(result) / 2 ** n)
