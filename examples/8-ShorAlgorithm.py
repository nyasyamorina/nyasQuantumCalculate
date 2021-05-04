# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Union, List

from nyasQuantumCalculate import *
from nyasQuantumCalculate.Builtin import *


Options.autoNormalize = False
Options.QFTswap = False


###############################################################################
"""下面的方法可以参考 https://www.bilibili.com/read/cv11142193"""

def PhaseModularAddInt(a: int, N: int, register: Qubits) -> None:
    sign = register[0]
    PhaseAddInt(a, register)
    IPhaseAddInt(N, register)
    IQFT(register)
    with TemporaryQubit(register.system) as tmp:
        CNOT(sign, tmp)
        QFT(register)
        Controlled(PhaseAddInt, tmp.asQubits(), N, register)
        IPhaseAddInt(a, register)
        IQFT(register)
        X(sign)
        CNOT(sign, tmp)
    X(sign)
    QFT(register)
    PhaseAddInt(a, register)

def IPhaseModularAddInt(a: int, N: int, register: Qubits) -> None:
    sign = register[0]
    IPhaseAddInt(a, register)
    IQFT(register)
    X(sign)
    with TemporaryQubit(register.system) as tmp:
        CNOT(sign, tmp)
        X(sign)
        QFT(register)
        PhaseAddInt(a, register)
        Controlled(IPhaseAddInt, tmp.asQubits(), N, register)
        IQFT(register)
        CNOT(sign, tmp)
    QFT(register)
    PhaseAddInt(N, register)
    IPhaseAddInt(a, register)

def ModularMultiplyIntAdd(a: int, N: int, x: Qubits, b: Qubits) -> None:
    QFT(b)
    for x_ele in x[::-1]:
        Controlled(PhaseModularAddInt, x_ele.asQubits(), a % N, N, b)
        a <<= 1
    IQFT(b)

def IModularMultiplyIntAdd(a: int, N: int, x: Qubits, b: Qubits) -> None:
    QFT(b)
    for x_ele in x[::-1]:
        Controlled(IPhaseModularAddInt, x_ele.asQubits(), a % N, N, b)
        a <<= 1
    IQFT(b)

def ModularInverse(a: int, N: int) -> int:
    old_r, r = a, N
    old_s, s = 1, 0
    while r > 1:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
    return s

def U_aN(a: int, N: int, register: Qubits) -> None:
    if a == 1:
        return
    with TemporaryQubit(register.system) as sign:
        x = sign + register
        with TemporaryQubits(x.system, len(x)) as tmp:
            ModularMultiplyIntAdd(a, N, x, tmp)
            for _x, _tmp in zip(x, tmp):
                SWAP(_x, _tmp)
            ia = ModularInverse(a, N)
            IModularMultiplyIntAdd(ia, N, x, tmp)

def GuessingPeriodR(j: int, n: int, N: int) -> List[int]:
    if j < 2 ** n / N:
        return list()
    cFrac = Utils.Frac2ContinuedFrac(j, 2 ** n)
    result: set[int] = set()
    for i in range(1, len(cFrac)):
        _, k = Utils.ContinuedFrac2Frac(cFrac[:i])
        if k >= N:
            break
        result.add(k)
    return list(result)


###############################################################################


def RunQuantumPart(a: int, N: int, n: int,
                   PhaseQubit: Qubit, register: Qubits) -> int:
    # 输入的是随机选择的整数a, 被分解的整数N, 求解精度n,
    # 和相位估计的量子位, 储存叠加态的寄存器

    # 因为化简版的相位估计是从U^(2^(n-1))开始计算,
    # 并且 (a^2)%N = ((a%N)^2)%N, 所以可以使用迭代计算所有(a^(2^l))%N
    a_s = [a]
    for _ in range(n - 1):
        a_s.append((a_s[-1] ** 2) % N)

    # 制备叠加特征态
    ApplyFromInt(X, 1, register)
    # 相位估计算法, 把测量结果放在一个列表里
    result = [False] * n
    phi = 0.
    for i in range(n):
        H(PhaseQubit)
        Controlled(U_aN, PhaseQubit.asQubits(), a_s[n - i - 1], N, register)
        R1(-2 * Utils.pi * phi)(PhaseQubit)
        H(PhaseQubit)
        res = M(PhaseQubit)
        if res: X(PhaseQubit)
        phi = phi / 2 + int(res) / 4
        result[n - i - 1] = res
    # 把测量结果转为整数然后输出
    R(PhaseQubit)
    RA(register)
    return Utils.Bools2Int(result)

def FromPeriodRGetFactor(a: int, N: int, r: int) -> Union[int, None]:
    # 从r中得到N的因数
    if r % 2 == 1:
        return
    b = a ** (r // 2)
    if b % N == N - 1:
        return
    # 因为这里的r很有可能不是真正的阶
    # 所以 gcd(b-1,N)!=1 也可能不符合
    c = Utils.gcd(b - 1, N)
    if c == 1:
        return
    return c


###############################################################################


def RunShorAlgorithm(N: int) -> int:
    # 过滤N
    if N % 2 == 0:
        return 2
    # TODO: 这里应该加一步筛选 N=p^q 的传统算法
    # 但是实在找不到如何实现

    m = Utils.nBits(N)  # 表示N的最少比特数
    n = 2 * m + 1       # 相位估计的求解精度
    # 初始化量子系统
    qbsys = QubitsSystem(1 + m)
    PhaseQubit = qbsys[0]               # 用于相位估计的量子位
    register = qbsys[1:]                # 用于储存特征态的量子位
    randomQubits = QubitsSystem(m)[:]   # 使用量子计算机计算随机数

    # 开始算法
    factor = None       # 已求得的因数
    while factor is None:
        # 得到随机整数a, 量子随机数输出范围为[0,2^m)
        # 这将以最低0.5的概率得到a [2,N-1)
        ApplyToEach(H, randomQubits)
        a = Utils.Bools2Int(MA(randomQubits))
        if a < 2 or a > N - 2:
            continue
        # 计算gcd(a,N), 如果不为1则得到N的因数
        b = Utils.gcd(a, N)
        if b != 1:
            factor = b
            continue
        # 使用量子计算器求得r的候选集
        j = RunQuantumPart(a, N, n, PhaseQubit, register)
        r_s = GuessingPeriodR(j, n, N)
        # 对候选集里的数字计算是否可以得到N的因数
        for r in r_s:
            factor = FromPeriodRGetFactor(a, N, r)
            if factor is not None:
                break
    # 输出
    RA(randomQubits)
    return factor

print("Find factor:", RunShorAlgorithm(21))
