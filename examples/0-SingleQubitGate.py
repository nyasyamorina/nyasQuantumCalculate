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
Builtin.I(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 1, ∣1❭: 0
# Reset


# Pauli Gates
# X gate can reverse states ∣0❭ and ∣1❭
print("after pauli-X gate:")
Builtin.X(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: 1
Builtin.X(qubit)    # Reset

# Y gate do similar thing as X gate, but on image number
print("after pauli-Y gate:")
Builtin.Y(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: i
Builtin.Y(qubit)    # Reset

# Z gate will flip the phase of ∣1❭, but do nothing on ∣0❭
print("after pauli-X gate and pauli-Z gate:")
Builtin.X(qubit)    # ∣0❭: 0, ∣1❭: 1
Builtin.Z(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: -1
Builtin.Z(qubit)
Builtin.X(qubit)  # Reset


# Hadamard Gate
# H gate will make qubit between ∣0❭ and ∣1❭
print("after Hadamard gate:")
Builtin.H(qubit)
DumpSystemText(qubit.system)        # ∣0❭: .707, ∣1❭: .707
Builtin.H(qubit)    # Reset


# Pahse Shift Gates
# T gate and S gate will shift phase of ∣1❭, but do nothing on ∣0❭
print("after pauli-X gate and T gate:")
Builtin.X(qubit)    # ∣0❭: 0, ∣1❭: 1
Builtin.T(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: .707+.707i
Builtin.TR(qubit)
Builtin.X(qubit)   # Reset

print("after pauli-X gate and S gate:")
Builtin.X(qubit)  # ∣0❭: 0, ∣1❭: 1
Builtin.S(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: i
Builtin.SR(qubit)
Builtin.X(qubit)   # Reset


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
Builtin.X(qubit)
R1(angle)(qubit)
DumpSystemText(qubit.system)        # ∣0❭: 0, ∣1❭: .5+.866i
R1(-angle)(qubit)
Builtin.X(qubit)     # Reset


# Phase Gate
# phase gate will shift global phase
print("after Phase gate:")
Phase(angle)(qubit)
DumpSystemText(qubit.system)        # ∣0❭: .5+.866i, ∣1❭: 0
Phase(-angle)(qubit)   # Reset


# Exit
Builtin.RA(sytm.getQubits())
