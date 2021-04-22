# -*- coding: utf-8 -*-

from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *
from nyasQuantumCalculate.Operate import *


__all__ = ["Adder", "PhaseAdd", "IPhaseAdd","Add", "IAdd",
           "PhaseAddInt", "IPhaseAddInt", "AddInt", "IAddInt"]


def Adder(Cin: Qubit, A: Qubits, B: Qubits, Cout: Qubit) -> None:
    """基本加法器

    |Cin❭|A❭|B❭|Cout❭ -> |Cin❭|A❭|mod(A+B,N)❭|Cout⊕floor(A+B/N)❭; N = 2^n

    注意: 使用可逆计算逻辑运行的加法器, 中途会新增n-1个Qubits, 确保有足够的内存

    Args:
        Cin: 进位输入
        A: 第一个加数, A和B的长度必须都为n
        B: 第二个加数, 加法结果会储存在这里
        Cout: 进位输出"""
    if Options.inputCheck:
        if not inSameSystem(Cin, A, B, Cout):
            raise ValueError("Input qubits are not in same system.")
        if len(A) != len(B):
            raise ValueError("Length of A and B should be same.")
    n = len(A)
    A_ = A if Options.littleEndian else A[::-1]
    B_ = B if Options.littleEndian else B[::-1]
    with TemporaryQubits(Cin.system, n - 1) as tmp:
        carries = Cin + tmp + Cout
        for index in range(n):
            q0 = carries[index]
            q1 = A_[index]
            q2 = B_[index]
            q3 = carries[index + 1]
            CCNOT(q1, q2, q3)
            CNOT(q1, q2)
            CCNOT(q0, q2, q3)
        CNOT(A_[-1], B_[-1])
        CNOT(carries[-2], B_[-1])
        CNOT(A_[-1], B_[-1])
        for index in range(n-2, -1, -1):
            q0 = carries[index]
            q1 = A_[index]
            q2 = B_[index]
            q3 = carries[index + 1]
            CCNOT(q0, q2, q3)
            CNOT(q1, q2)
            CCNOT(q1, q2, q3)
            CNOT(q0, q2)
            CNOT(q1, q2)


def PhaseAdd(A: Qubits, B: Qubits) -> None:
    """把A作为相位加到B上

    Args:
        A: 加数, 长度为m
        B: 被加数, 长度为n, 并且n>=m"""
    if Options.inputCheck:
        if not inSameSystem(A, B):
            raise ValueError("Input qubits are not in same system.")
        if len(A) > len(B):
            raise ValueError("Length of A should not be greater than B's.")
    m = len(A)
    n = len(B)
    n_m = n - m
    RotationGates.updateRs(n)
    A_ = A[::-1] if Options.littleEndian else A
    B_ = B[::-1] if Options.littleEndian else B
    for index in range(n):
        A_start = max(0, index - n_m)
        B_start = max(0, n_m - index)
        B_end = n - index
        for ctlQb, target in zip(A_[A_start:], B_[B_start:B_end]):
            Controlled(RotationGates.Rs[index], ctlQb.asQubits(), target)


def Add(A: Qubits, B: Qubits) -> None:
    """计算A+B

    |A❭|B❭ -> |A❭|mod(A+B,N)❭; N = 2^n

    Args:
        A: 加数, 长度为m
        B: 被加数, 长度为n, 并且n>=m"""
    if Options.inputCheck:
        if not inSameSystem(A, B):
            raise ValueError("Input qubits are not in same system.")
        if len(A) > len(B):
            raise ValueError("Length of A should not be greater than B's.")
    A_ = A[::-1] if Options.littleEndian else A
    B_ = B[::-1] if Options.littleEndian else B
    with TemporaryOptions.QFTswap(False):
        QFT(B_)
        with (TemporaryOptions.inputCheck(False),
              TemporaryOptions.littleEndian(False)):
            PhaseAdd(A_, B_)
        IQFT(B_)


def IPhaseAdd(A: Qubits, B: Qubits) -> None:
    """计算PhaseAddd的逆

    Args:
        A: 加数, 长度为m
        B: 被加数, 长度为n, 并且n>=m"""
    if Options.inputCheck:
        if not inSameSystem(A, B):
            raise ValueError("Input qubits are not in same system.")
        if len(A) > len(B):
            raise ValueError("Length of A should not be greater than B's.")
    m = len(A)
    n = len(B)
    n_m = n - m
    RotationGates.updateiRs(n)
    A_ = A[::-1] if Options.littleEndian else A
    B_ = B[::-1] if Options.littleEndian else B
    for index in range(n):
        A_start = max(0, index - n_m)
        B_start = max(0, n_m - index)
        B_end = n - index
        for ctlQb, target in zip(A_[A_start:], B_[B_start:B_end]):
            Controlled(RotationGates.iRs[index], ctlQb.asQubits(), target)


def IAdd(A: Qubits, B: Qubits) -> None:
    """计算A+B的逆

    |A❭|A+B❭ -> |A❭|mod(B,N)❭; N = 2^n

    Args:
        A: 加数, 长度为m
        B: 被加数, 长度为n, 并且n>=m"""
    if Options.inputCheck:
        if not inSameSystem(A, B):
            raise ValueError("Input qubits are not in same system.")
        if len(A) > len(B):
            raise ValueError("Length of A should not be greater than B's.")
    A_ = A[::-1] if Options.littleEndian else A
    B_ = B[::-1] if Options.littleEndian else B
    with TemporaryOptions.QFTswap(False):
        QFT(B_)
        with (TemporaryOptions.inputCheck(False),
              TemporaryOptions.littleEndian(False)):
            IPhaseAdd(A_, B_)
        IQFT(B_)


def PhaseAddInt(A: int, B: Qubits) -> None:
    """把A作为相位加到B上

    Args:
        A: 加数, 长度小于等于n, 否则会被截断
        B: 被加数, 长度为n"""
    n = len(B)
    tag0 = 1 << n
    tag1 = tag0 - 1
    a_ = A & tag1
    B_ = B[::-1] if Options.littleEndian else B
    tag0 >>= 1
    for qb in B_:
        R1(a_ / tag0 * pi)(qb)
        tag1 >>= 1
        tag0 >>= 1
        a_ &= tag1


def AddInt(A: int, B: Qubits) -> None:
    """计算A+B

    |B❭ -> |mod(A+B,N)❭; N = 2^n

    因为加数不是量子位, 使用化简算法

    Args:
        A: 加数, 长度小于等于n, 否则会被截断
        B: 被加数, 长度为n"""
    B_ = B[::-1] if Options.littleEndian else B
    with TemporaryOptions.QFTswap(False):
        QFT(B_)
        with TemporaryOptions.littleEndian(False):
            PhaseAddInt(A, B_)
        IQFT(B_)


def IPhaseAddInt(A: int, B: Qubits) -> None:
    """计算PhaseAddInt的逆

    Args:
        A: 加数, 长度小于等于n, 否则会被截断
        B: 被加数, 长度为n"""
    n = len(B)
    tag0 = 1 << n
    tag1 = tag0 - 1
    a_ = A & tag1
    B_ = B[::-1] if Options.littleEndian else B
    tag0 >>= 1
    for qb in B_:
        R1(a_ / tag0 * -pi)(qb)
        tag1 >>= 1
        tag0 >>= 1
        a_ &= tag1


def IAddInt(A: int, B: Qubits) -> None:
    """计算A+B的逆

    |A+B❭ -> |mod(B,N)❭; N = 2^n

    因为加数不是量子位, 使用化简算法

    Args:
        A: 加数, 长度小于等于n, 否则会被截断
        B: 被加数, 长度为n"""
    B_ = B[::-1] if Options.littleEndian else B
    with TemporaryOptions.QFTswap(False):
        QFT(B_)
        with TemporaryOptions.littleEndian(False):
            PhaseAddInt(A, B_)
        IQFT(B_)
