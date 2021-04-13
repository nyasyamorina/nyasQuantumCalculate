# -*- coding: utf-8 -*-


USE_QUANTUM = False


if USE_QUANTUM:
    from nyasQuantumCalculate import *
    Bit = Qubit
    Bits = Qubits
    BitsSystem = QubitsSystem
else:
    from nyasQuantumCalculate.RevCal import *

from nyasQuantumCalculate.Utils import Bools2Int, Int2Bools
from typing import Any
X: Any = Builtin.X


def CARRY(q0: Any, q1: Any, q2: Any, q3: Any):
    Builtin.CCNOT(q1, q2, q3)
    Builtin.CNOT(q1, q2)
    Builtin.CCNOT(q0, q2, q3)

def CARRYR(q0: Any, q1: Any, q2: Any, q3: Any):
    Builtin.CCNOT(q0, q2, q3)
    Builtin.CNOT(q1, q2)
    Builtin.CCNOT(q1, q2, q3)

def SUM(q0: Any, q1: Any, q2: Any):
    Builtin.CNOT(q0, q2)
    Builtin.CNOT(q1, q2)


bsys = BitsSystem(10)

a = bsys[1:8:3]
b = bsys[2:9:3]
out = b + bsys[9]


def add(a_number: int, b_number: int) -> int:
    ApplyFromBools(X, Int2Bools(a_number)[::-1], a)
    ApplyFromBools(X, Int2Bools(b_number)[::-1], b)

    CARRY(*bsys[0:4])
    CARRY(*bsys[3:7])
    CARRY(*bsys[6:10])
    Builtin.CNOT(bsys[7], bsys[8])
    SUM(*bsys[6:9])
    CARRYR(*bsys[3:7])
    SUM(*bsys[3:6])
    CARRYR(*bsys[0:4])
    SUM(*bsys[0:3])

    result = Builtin.MA(out)
    Builtin.RA(bsys[:])

    return Bools2Int(result[::-1])


for x in range(8):
    for y in range(8):
        print(f"{x} + {y} = {add(x, y)}")
