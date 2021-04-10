# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Callable

from numpy import pi, sqrt, arcsin

from nyasQuantumCalculate import *
from nyasQuantumCalculate.Utils import Bools2Int


# 把自动normalize设为False以加快运行速度
Options.autoNormalize = False


#############################  搜索问题  #######################################
"""
有一个黑盒 f: Z -> {0,1}, 寻找一个输入x使得f输出为1

这个问题被称为搜索问题. 图形着色问题, 数据库搜索也属于搜索问题.
"""


############################  图形着色问题  ####################################
r"""下面以一个实际的问题作为 Grover 算法的例子
https://en.wikipedia.org/wiki/Graph_coloring

构建一个无向图:
    0------1
    |\    /|
    | \  / |
    |  \/  |
    |  /\  |
    | /  \ |
    |/    \|
    2------3------4
寻找一种着色方案使得每条边上不存在相同的颜色.

在这个例子中, 需要的最少颜色为4种, 使用2bits对一个顶点的颜色进行编码.
总共5个顶点, 则需要10bits储存结果.
"""

# 使用索引表示线段与点的关系
edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)]
# 表示颜色需要的bit数
nColorBits = 2
# 总共顶点数
nVertex = max(max(edge) for edge in edges) + 1


def ColorEquality(c0: Qubits, c1: Qubits, target: Qubit):
    """计算输入的两种颜色是否相同, 如果相同则翻转target的状态, 否则什么也不做"""
    # 把c0和c1按位做异或, 并把结果储存在c1
    for q0, q1 in zip(c0, c1):
        CNOT(q0, q1)
    # 如果c1全部为0, 则c0与c1相同, 此时翻转target的状态
    ApplyToEach(X, c1)
    Controlled(X, c1, target)

    # 因为作为数据位的c1被修改了, 在退出前需要还原c1的数据
    ApplyToEach(X, c1)
    for q0, q1 in zip(c0, c1):
        CNOT(q0, q1)


def ValidVertexColoring(register: Qubits, target: Qubit):
    """计算按照edges的图形, colors的着色是否为解, 如果是则翻转target, 否则什么也不做"""
    # 输入的colors的量子位数量应该为 颜色的bit数*总定点数, 在这里为10
    assert len(register) == nColorBits * nVertex

    # 把寄存器分离为顶点
    colors = [register[nColorBits*v: nColorBits*(v+1)] for v in range(nVertex)]

    # 使用寄存器记录每条边的顶点颜色是否一样
    with TemporaryQubits(register.system, len(edges)) as edgesResult:
        # 对每一条边计算两顶点的颜色是否一样, 并把结果储存在edgesResult里
        for (idx0, idx1), edgeResult in zip(edges, edgesResult):
            ColorEquality(colors[idx0], colors[idx1], edgeResult)
        # 如果edgesResult的结果全部为|0❭, 则证明全部边上不存在相同的颜色,
        # 这时候colors的着色为解, 则翻转target
        ApplyToEach(X, edgesResult)
        Controlled(X, edgesResult, target)

        # 尽管在退出with时会自动重置edgesResult,
        # 但是手动还原为原本的状态是良好的习惯
        ApplyToEach(X, edgesResult)
        for (idx0, idx1), edgeResult in zip(edges, edgesResult):
            ColorEquality(colors[idx0], colors[idx1], edgeResult)


"""Grover算法是一个渐进算法, 也就是需要不断迭代Grover过程才可以得到需要的答案,

Grover过程包含以下两步:
    1) 把标记状态的相位反转
    2) 作用Grover扩散算子(Grover diffusion operator)

Grover扩散算子可以减少大于平均值的状态而增加少于平均值的状态,
当需要的结果数量小于不需要的结果数量时, Grover扩散算子可以有效地增加需要的结果的机率.

记M为全部需要结果的数量, N为全部结果的数量 (在这里M=72, N=2^10=1024)
则迭代次数 j = round(π / (4 * arcsin(sqrt(M / N))) - .5); (在这里为2)
"""


def GroverSearch(f: Callable[[Qubits, Qubit], None],
                 register: Qubits, nIter: int):
    """Grover算法是通用算法, 给出黑盒f和|0❭状态register, 并执行nIter次Grover过程"""
    # 使寄存器处于全部结果的叠加态里
    ApplyToEach(H, register)
    # 使用"相位反冲"技巧翻转目标状态
    with TemporaryQubit(register.system) as target:
        X(target)
        H(target)

        # 执行Grover过程
        for _ in range(nIter):
            # 把标记状态的相位反转
            f(register, target)
            # 作用Grover扩散算子
            ApplyToEach(H, register)
            ApplyToEach(X, register)
            Controlled(X, register[0:-1], register[-1])
            ApplyToEach(X, register)
            ApplyToEach(H, register)
            # Grover扩散算子应该在执行完上述步骤后, 把全部状态的相位翻转
            # 但由于全局相位对计算和测量都没有影响, 所以最后一步并不是必须的
            Phase(pi)(register[-1])         # Grover扩散算子最后一步

        # 退出前还原临时量子位
        H(target)
        X(target)


"""运行例子
需要注意的是, Grover算法是以很大概率给出正确答案, 所以检查答案是否正确也是必须的"""


# 计算迭代Grover过程的数量
M = 72                              # 正确答案的数量
N = 2 ** (nColorBits * nVertex)     # 所有答案的数量
j = round(pi / (4 * arcsin(sqrt(M / N))) - .5)

# 初始化量子位系统
qbsys = QubitsSystem(nColorBits * nVertex)
register = qbsys.getQubits()

# 这个result是不让编辑器提示result(165)不存在的, 并没有实际用途
result = MeasureAll(register)

# 使用一个额外的量子位判断答案是否正确, 如果不正确则继续运行Grover算法
with TemporaryQubit(qbsys) as Correctness:
    while Measure(Correctness) == 0:
        # 运行Grover算法
        GroverSearch(ValidVertexColoring, register, j)

        # 测量寄存器, 并使量子位全部坍缩到测量结果里
        result = MeasureAll(register)
        # 判断结果是否正确, 如果正确则把Correctness从|0❭变为|1❭
        ValidVertexColoring(register, Correctness)
        # 无论结果是否正确都需要重置寄存器
        ResetAll(register)


# 使用比较好的方式输出结果
for v in range(nVertex):
    print(f"Vertex {v} has color "
          f"{Bools2Int(result[nColorBits*v : nColorBits*(v+1)])}")
