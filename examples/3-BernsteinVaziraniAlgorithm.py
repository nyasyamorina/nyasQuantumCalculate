# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np

from nyasQuantumCalculate import *
from nyasQuantumCalculate.Utils import Int2Bools


################################  问题  ########################################
"""
有一个带参黑盒 f_s(x) = s·x; s,x是n比特整数, s·x为s与x在{0,1}^n里的内积, 也就是
s·x = s1*x1⊕s2*x2⊕...⊕sn*sn, ⊕是异或

通过调用黑盒求s
"""

n = 4       # 比特串的长度


###############################  初始化黑盒  ###################################
# 目标比特串
s = Int2Bools(int(2 ** n * np.random.random()), n)  # 随机生成一个比特串
print(f"bit string: [{''.join(map(lambda b: '1' if b else '0', s))}]")

def UnknownClassical(x: int) -> bool:
    """提供给传统算法的接口"""
    res = False
    for ele in s:
        # x & 1 == 1 可以提取x最右端的bit并转为bool
        res ^= ele and (x & 1 == 1)
        x >>= 1
    return res

def UnknownQuantum(qbs: Qubits):
    """提供给量子算法的接口"""
    ApplyFromBools(Z, s, qbs)


#################################  传统算法  ###################################
"""传统算法需要调用n次黑盒才可以得到s
每次提取s的1个bit"""

def mainClassical():
    x = 1
    result: List[bool] = list()
    for _ in range(n):
        result.append(UnknownClassical(x))
        x <<= 1
    # 输出
    print(f"bit string (Classical): [{''.join(map(lambda b: '1' if b else '0', result))}]")

mainClassical()


#################################  量子算法  ###################################
"""量子算法只需要调用1次黑盒就可以得到s
原理与频谱分析有关, 见阿达马变换 https://en.wikipedia.org/wiki/Hadamard_transform"""

def mainQuantum():
    # 初始化量子位系统
    qbsys = QubitsSystem(n)
    qbs = qbsys.getQubits()

    # BernsteinVazirani算法
    ApplyToEach(H, qbs)
    UnknownQuantum(qbs)
    ApplyToEach(H, qbs)

    # 测量并重设所有量子位
    result = MeasureAll(qbs)
    ResetAll(qbs)

    # 输出
    print(f"bit string (Quantum): [{''.join(map(lambda i: str(i), result))}]")

mainQuantum()
