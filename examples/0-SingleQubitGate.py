# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from nyasQuantumCalculate import *


sytm = QubitsSystem(1)
qubit: Qubit = sytm[0]


print("Original qubit:")
DumpSystemText(qubit.system)        # ∣0❭: 1, ∣1❭: 0


# Identity Gate
# I gate doing somthing looks like do nothing
print("after Identity gate:")
I(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 1, ∣1❭: 0
# Reset


# Pauli Gates
# X gate can reverse states ∣0❭ and ∣1❭
print("after pauli-X gate:")
X(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: 1
X(qubit)    # Reset

# Y gate do similar thing as X gate, but on image number
print("after pauli-Y gate:")
Y(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: i
Y(qubit)    # Reset

# Z gate will flip the phase of ∣1❭, but do nothing on ∣0❭
print("after pauli-X gate and pauli-Z gate:")
X(qubit)    # ∣0❭: 0, ∣1❭: 1
Z(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: -1
Z(qubit); X(qubit)  # Reset


# Hadamard Gate
# H gate will make qubit between ∣0❭ and ∣1❭
print("after Hadamard gate:")
H(qubit)
DumpSystemText(qubit.system)        # ∣0❭: .707, ∣1❭: .707
H(qubit)    # Reset


# Pahse Shift Gates
# T gate and S gate will shift phase of ∣1❭, but do nothing on ∣0❭
print("after pauli-X gate and T gate:")
X(qubit)    # ∣0❭: 0, ∣1❭: 1
T(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: .707+.707i
TR(qubit); X(qubit)   # Reset

print("after pauli-X gate and S gate:")
X(qubit)  # ∣0❭: 0, ∣1❭: 1
S(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: i
SR(qubit); X(qubit)   # Reset


# Rotation Gates
# rotation gates will "rotate" the qubit on "Bloch sphere"
# https://en.wikipedia.org/wiki/Bloch_sphere
angle = 1.0471975511966     # pi / 3

print("after Rotation-X gate:")
Rx(angle)(qubit)
DumpSystemText(qubit.system)        # ∣0❭: .866, ∣1❭: -.5i
Rx(-angle)(qubit)   # Reset

print("after Rotation-Y gate:")
Ry(angle)(qubit)
DumpSystemText(qubit.system)        # ∣0❭: .866, ∣1❭: .5
Ry(-angle)(qubit)   # Reset

print("after Rotation-Z gate:")
Rz(angle)(qubit)
DumpSystemText(qubit.system)        # ∣0❭: .866-.5i, ∣1❭: 0
Rz(-angle)(qubit)   # Reset

print("after pauli-X gate and Rotation-1 gate:")
X(qubit)
R1(angle)(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: .5+.866i
R1(-angle)(qubit); X(qubit)     # Reset


# Exit
ResetAll(sytm.getQubits())
