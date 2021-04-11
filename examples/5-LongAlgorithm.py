# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Callable

from numpy import pi, arcsin, sin, sqrt

from nyasQuantumCalculate import *
from nyasQuantumCalculate.Utils import Bools2Int


Options.autoNormalize = False


##########################  改进 Grover 算法  ##################################
"""
值得注意的是, Grover搜索算法并不是迭代次数越多越精确的.
记M为正确答案的数量, N为全部答案的数量, j = round(π / (4*arcsin(sqrt(M / N))) -.5),
当迭代次数为j时, 测量出正确答案的机率比较大.
当迭代次数为2*j时, 测量出错误答案机率比较大.
3*j时为正确答案的机率大, 4*j时为错误答案, 以此类推

记|Good❭为所有正确答案的叠加态, |Bad❭为所有错误状态的叠加态.
则叠加态|ψ❭在相空间{O;|Bad❭,|Good❭}里是一个长度为1的矢态. 记均匀叠加态(H|0❭)^(⊗n)与
|Bad❭之间的夹角为θ, 则每次运算Grover过程都会使|ψ❭在相空间里旋转2θ. 当|ψ❭与|Bad❭夹角
为π/2时, 则|ψ❭与|Good❭夹角为0, 此时以概率1测出正确答案.
但每次迭代一定会旋转2θ, 当迭代次数过多时会使|ψ❭向-|Bad❭转动, 以此类推.

实际上θ = arcsin(sqrt(M / N))), 则迭代次数j = round(π / 4θ - .5)
"""
"""
Grover算法一个致命缺点是旋转角度θ与迭代次数j无关, θ只与数据相关.
龙桂鲁团队提出了一个改进版Grover算法, 被称作Long算法.
这个算法从迭代次数j中得出旋转角度θ
"""
"""
Grover过程, 也就是单次迭代记作G,
G = -W(I-(exp(iφ)+1)|0❭❬0|)W(I-(exp(iφ)+1)|Good❭❬Good|).
在Grover算法里, φ = π, 并且 -W(I-(exp(iφ)+1)|0❭❬0|)W 即为Grover扩散算子,
I-(exp(iφ)+1)|Good❭❬Good|为需要搜索的黑盒.

在Long算法里, φ = 2*arcsin(sin(π / (4*J+6)) / sinθ),
其中J >= j_op = floor(π / 4θ - .5). 则迭代次数j为J+1
当J<j_op时, φ为复数, 这时Grover过程失去定义(非酉).
也就是说Long算法并不会比Grover算法快.
"""


#############################  图形着色问题  ###################################
"""此处的例子与4-GroverAlgorithm.py相同, 就不过多叙述了
需要注意的是, 旋转门的角度需要在一开始就确定, 所以这里的计算顺序有所调整"""


edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)]
nColorBits = 2
nVertex = max(max(edge) for edge in edges) + 1


# 计算迭代Grover过程的数量
m = 72                              # 正确答案的数量
n = 2 ** (nColorBits * nVertex)     # 所有答案的数量
theta = arcsin(sqrt(m / n))         # 均匀叠加态在相空间里的辐角
j_op = int(pi / (4 * theta) - .5)   # Grover算法最少迭代次数
J = j_op                            # Long算法里的可调参数, 这里选择运行最快的
j = J + 1                           # Long算法迭代的次数
# Long算法里对相位旋转的角度
phi = 2 * arcsin(sin(pi / (4 * J + 6)) / sin(theta))
RO = R1(phi)                        # 相位旋转矩阵


def ColorEquality(c0: Qubits, c1: Qubits, target: Qubit):
    for q0, q1 in zip(c0, c1):
        Builtin.CNOT(q0, q1)
    ApplyToEach(Builtin.X, c1)
    Controlled(Builtin.X, c1, target)
    ApplyToEach(Builtin.X, c1)
    for q0, q1 in zip(c0, c1):
        Builtin.CNOT(q0, q1)


def ValidVertexColoring(register: Qubits, target: Qubit):
    assert len(register) == nColorBits * nVertex
    colors = [register[nColorBits*v: nColorBits*(v+1)] for v in range(nVertex)]
    with TemporaryQubits(register.system, len(edges)) as edgesResult:
        for (idx0, idx1), edgeResult in zip(edges, edgesResult):
            ColorEquality(colors[idx0], colors[idx1], edgeResult)
        ApplyToEach(Builtin.X, edgesResult)
        # target输入不再是|0❭-|1❭的相位反冲, 而是输入|1❭"相位偏移"(乱起的名字)
        Controlled(RO, edgesResult, target)
        ApplyToEach(Builtin.X, edgesResult)
        for (idx0, idx1), edgeResult in zip(edges, edgesResult):
            ColorEquality(colors[idx0], colors[idx1], edgeResult)


def LongSearch(f: Callable[[Qubits, Qubit], None],
                 register: Qubits, nIter: int):
    ApplyToEach(Builtin.H, register)
    with TemporaryQubit(register.system) as target:
        # "相位偏移"使用|1❭, 而不是|0❭-|1❭
        Builtin.X(target)
        for _ in range(nIter):
            f(register, target)
            ApplyToEach(Builtin.H, register)
            ApplyToEach(Builtin.X, register)
            # 偏移均值相位, 而不是翻转
            Controlled(RO, register[0:-1], register[-1])
            ApplyToEach(Builtin.X, register)
            ApplyToEach(Builtin.H, register)
        Builtin.X(target)


qbsys = QubitsSystem(nColorBits * nVertex)
register = qbsys.getQubits()

LongSearch(ValidVertexColoring, register, j)
result = Builtin.MA(register)
Builtin.RA(register)

for v in range(nVertex):
    print(f"Vertex {v} has color "
          f"{Bools2Int(result[nColorBits*v : nColorBits*(v+1)])}")


# edges=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3),(3,4)] 的解
answer = [108, 109, 110, 120, 121, 123, 156, 157, 158, 180, 182, 183, 216, 217,
          219, 228, 230, 231, 300, 301, 302, 312, 313, 315, 396, 397, 398, 433,
          434, 435, 456, 457, 459, 481, 482, 483, 540, 541, 542, 564, 566, 567,
          588, 589, 590, 625, 626, 627, 708, 710, 711, 721, 722, 723, 792, 793,
          795, 804, 806, 807, 840, 841, 843, 865, 866, 867, 900, 902, 903, 913,
          914, 915]
print(f"Is result correct: {Bools2Int(result) in answer}")
