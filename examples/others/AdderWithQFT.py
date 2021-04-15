from nyasQuantumCalculate import *
from nyasQuantumCalculate.Utils import *


def AddUp(registerA: Qubits, registerB: Qubits) -> None:
    """|A❭|B❭ --> |A❭|mod(A+B,2^n)❭; n = len(registerA) = len(registerB)"""
    assert len(registerA) == len(registerB)
    n = len(registerA)
    with TemporaryOptions.QFTswap(False):
        Builtin.QFT(registerB)
        for i in range(n):
            Ri = R1(pi / (1 << i))
            Ri.name = f"R_{i}"
            for ctr, tar in zip(registerA[i:], registerB[:n - i]):
                Controlled(Ri, ctr.asQubits(), tar)
        Builtin.IQFT(registerB)


n = 3

qbsys = QubitsSystem(2 * n)
registerA = qbsys[:n]
registerB = qbsys[n:]


def add(a: int, b: int) -> int:
    ApplyFromInt(Builtin.X, a, registerA)
    ApplyFromInt(Builtin.X, b, registerB)

    AddUp(registerA, registerB)

    result = Builtin.MA(registerB)
    Builtin.RA(registerA + registerB)
    return Bools2Int(result)


N = 1 << n
for a in range(N):
    for b in range(N):
        print(f"mod({a} + {b}, {N}) = {add(a, b)}")
