from nyasQuantumCalculate.Options import *
from .System import *
from .Operate import *


__all__ = ["Adder"]


def Adder(Cin: Bit, A: Bits, B: Bits, Cout: Bit) -> None:
    if not inSameSystem(Cin, A, B, Cout):
        raise ValueError("Input qubits are not in same system.")
    if len(A) != len(B):
        raise ValueError("Length of A and B should be same.")
    n = len(A)
    A_ = A if Options.littleEndian else A[::-1]
    B_ = B if Options.littleEndian else B[::-1]
    with TemporaryBits(Cin.system, n - 1) as tmp:
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
