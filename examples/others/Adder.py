# -*- coding: utf-8 -*-


USE_QUANTUM = False
n = 3


if USE_QUANTUM:
    from nyasQuantumCalculate import *
    Bit = Qubit
    Bits = Qubits
    BitsSystem = QubitsSystem
else:
    from nyasQuantumCalculate.RevCal import *

from nyasQuantumCalculate.Utils import Bools2Int
from typing import Any
X: Any = Builtin.X


bsys = BitsSystem(2 * (n + 1))
Cin = bsys[0]
A = bsys[1:n+1]
B = bsys[n+1:2*n+1]
Cout = bsys[2*n+1]


for a in range(2 ** n):
    for b in range(2 ** n):
        X(Cin)
        ApplyFromInt(X, a, A)
        ApplyFromInt(X, b, B)

        # nyasQuantumCalculate.HighLevel.Add.Adder
        Adder(Cin, A, B, Cout)

        result = [Builtin.M(Cout)] + Builtin.MA(B)
        Builtin.RA(bsys[:])

        print(f"{a} + {b} = {Bools2Int(result)}")
