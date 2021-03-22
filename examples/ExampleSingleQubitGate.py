import upper_path

from nyasQuantumCalculate import *
from nyasQuantumCalculate import Gates
from nyasQuantumCalculate import Utils

print(dir())


qubit = SingleQubit()
print("Original qubit:")
Utils.DumpMachineText(qubit)        # ∣0❭: 1, ∣1❭: 0


# Identity Gate
# I gate doing somthing looks like do nothing
print("after Identity gate:")
Gates.I(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 1, ∣1❭: 0
Reset(qubit)


# Pauli Gates
# X gate can reverse states ∣0❭ and ∣1❭
print("after pauli-X gate:")
Gates.X(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 0, ∣1❭: 1
Reset(qubit)

# Y gate do similar thing as X gate, but on image number
print("after pauli-Y gate:")
Gates.Y(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 0, ∣1❭: i
Reset(qubit)

# Z gate will flip the phase of ∣1❭, but do nothing on ∣0❭
print("after pauli-X gate and pauli-Z gate:")
Gates.X(qubit)  # ∣0❭: 0, ∣1❭: 1
Gates.Z(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 0, ∣1❭: -1
Reset(qubit)


# Hadamard Gate
# H gate will make qubit between ∣0❭ and ∣1❭
print("after Hadamard gate:")
Gates.H(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: .707, ∣1❭: .707
Reset(qubit)


# Pahse Shift Gates
# T gate and S gate will shift phase of ∣1❭, but do nothing on ∣0❭
print("after pauli-X gate and T gate:")
Gates.X(qubit)  # ∣0❭: 0, ∣1❭: 1
Gates.T(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 0, ∣1❭: .707+.707i
Reset(qubit)

print("after pauli-X gate and S gate:")
Gates.X(qubit)  # ∣0❭: 0, ∣1❭: 1
Gates.S(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 0, ∣1❭: i
Reset(qubit)


# Rotation Gates
# rotation gates will "rotate" the qubit on "Bloch sphere"
# https://en.wikipedia.org/wiki/Bloch_sphere
angle = 1.0471975511966     # pi / 3

print("after Rotation-X gate:")
Gates.Rx(angle)(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: .866, ∣1❭: -.5i
Reset(qubit)

print("after Rotation-Y gate:")
Gates.Ry(angle)(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: .866, ∣1❭: .5
Reset(qubit)

print("after Rotation-Z gate:")
Gates.Rz(angle)(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: .866-.5i, ∣1❭: 0
Gates.X(qubit); Reset(qubit)

print("after pauli-X gate and Rotation-1 gate:")
Gates.X(qubit)
Gates.R1(angle)(qubit)
Utils.DumpMachineText(qubit)        # ∣0❭: 0, ∣1❭: .5+.866i
Reset(qubit)
