# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from nyasQuantumCalculate import *
from numpy import pi, sin


Options.autoNormalize = False

"""细节可以参考 https://www.bilibili.com/read/cv11088535"""


###############################################################################
""" 图形着色部分代码 """
edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
nColorBits = 2
nVertex = max(max(edge) for edge in edges) + 1
def Equality(registerA: Qubits, registerB: Qubits, target: Qubit) -> None:
    # 把registerA和registerB按位做XOR, 结果储存在registerB
    for q0, q1 in zip(registerA, registerB):
        Builtin.CNOT(q0, q1)
    # registerB按位取反
    ApplyToEach(Builtin.X, registerB)
    # 如果registerB全部为1, 说明registerA=registerB, 则翻转target的状态
    Controlled(Builtin.X, registerB, target)
    # 反向计算所有改变registerB的逻辑以还原registerB
    ApplyToEach(Builtin.X, registerB)
    for q0, q1 in zip(registerA, registerB):
        Builtin.CNOT(q0, q1)
def GraphColoring(register: Qubits, target: Qubit) -> None:
    colors = [register[2*i:2*i+2] for i in range(5)]
    with TemporaryQubits(register.system, len(edges)) as tmpQubits:
        for (i0, i1), tmpQ in zip(edges, tmpQubits):
            Equality(colors[i0], colors[i1], tmpQ)
        ApplyToEach(Builtin.X, tmpQubits)
        Controlled(Builtin.X, tmpQubits, target)
        # 退出前还原tmpQubits
        ApplyToEach(Builtin.X, tmpQubits)
        for (i0, i1), tmpQ in zip(edges, tmpQubits):
            Equality(colors[i0], colors[i1], tmpQ)


###############################################################################


def GroverOperator(register: Qubits) -> None:
    ApplyToEach(Builtin.H, register)
    ApplyToEach(Builtin.X, register)
    Controlled(Builtin.Z, register[:-1], register[-1])
    ApplyToEach(Builtin.X, register)
    ApplyToEach(Builtin.H, register)
    #Phase(pi)(register[-1])

    # 如果增加 `Phase(pi)(register[-1])` 的代码, Grover算子定义为
    # G = W(2|0❭❬0|-I)W, 这时从测量结果得到M的式子为 2**n*sin(pi*2*phi)**2.
    # 当如果没有这行代码, Grover算子定义为 G = W(I-2|0❭❬0|)W, 这时
    # 计算M为 2**n*sin(pi*(2*phi-0.5))**2


n = nVertex * nColorBits    # 运行Grover算法的量子位数量
m = n + 2                   # 运行相位估计的精度

qbsys = QubitsSystem(1 + n)
A = qbsys[0]                # 使用化简的相位估计, 只需要1个量子位而不是m个
B = qbsys[1:]               # Grover算法的量子位

# 制备特征叠加态
ApplyToEach(Builtin.H, B)
# 把Grover算法里单次迭代做成一个函数
def RunGroverStep():
    with TemporaryQubit(qbsys) as tmp:
        # 使用相位反冲技巧把标记黑盒转为相位黑盒
        Builtin.X(tmp)
        Builtin.H(tmp)
        GraphColoring(B, tmp)
        Builtin.H(tmp)
        Builtin.X(tmp)
    GroverOperator(B)


# 相位估计算法
phi = 0.
for i in range(m):
    Builtin.H(A)
    for _ in range(2 ** (m - i - 1)):
        Controlled(RunGroverStep, A.asQubits())
    R1(-2 * pi * phi)(A)
    Builtin.H(A)
    res = Builtin.M(A)
    if res:
        Builtin.X(A)
    phi = phi / 2 + int(res) / 4

# 输出, 重置系统
print("测得共有", round(2**n * sin(pi*(2*phi-0.5))**2), "个正确答案")
Builtin.RA(qbsys[:])
