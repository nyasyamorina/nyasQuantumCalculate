from nyasQuantumCalculate import *
from nyasQuantumCalculate.Utils import *

n = 3

qbsys = QubitsSystem(2 * n)
registerA = qbsys[:n]
registerB = qbsys[n:]

N = 1 << n
for a in range(N):
    for b in range(N):
        ApplyFromInt(Builtin.X, a, registerA)
        ApplyFromInt(Builtin.X, b, registerB)

        Add(registerA, registerB)

        print(f"mod({a} + {b}, {N}) = {Bools2Int(Builtin.MA(registerB))}")
        Builtin.RA(registerA + registerB)
