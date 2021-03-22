from cmath import sqrt, exp, pi, sin, cos
from typing import Tuple

from numpy import arccos

from nyasQuantumCalculate import M, Reset
from nyasQuantumCalculate import Utils
from nyasQuantumCalculate.cy.nyasQC import *


############################  Options  #########################################
assert Options.autoNormalize == True
assert Options.checkUnitGate == True
assert Options.ignoreWarning == False
assert Options.checkQubitIdx == True

Options.autoNormalize = False
Options.checkUnitGate = False
Options.ignoreWarning = True
Options.checkQubitIdx = False
assert Options.autoNormalize == False
assert Options.checkUnitGate == False
assert Options.ignoreWarning == True
assert Options.checkQubitIdx == False

#######################  TemporaryOptions  #####################################
with TemporaryOptions.autoNormalize(True):
    assert Options.autoNormalize == True
    with TemporaryOptions.autoNormalize(False):
        assert Options.autoNormalize == False
    assert Options.autoNormalize == True
assert Options.autoNormalize == False

with TemporaryOptions.checkUnitGate(True):
    assert Options.checkUnitGate == True
    with TemporaryOptions.checkUnitGate(False):
        assert Options.checkUnitGate == False
    assert Options.checkUnitGate == True
assert Options.checkUnitGate == False

with TemporaryOptions.ignoreWarning(False):
    assert Options.ignoreWarning == False
    with TemporaryOptions.ignoreWarning(True):
        assert Options.ignoreWarning == True
    assert Options.ignoreWarning == False
assert Options.ignoreWarning == True

with TemporaryOptions.checkQubitIdx(True):
    assert Options.checkQubitIdx == True
    with TemporaryOptions.checkQubitIdx(False):
        assert Options.checkQubitIdx == False
    assert Options.checkQubitIdx == True
assert Options.checkQubitIdx == False

################################################################################
################################################################################

def checkAllValue(v0: Tuple[Tuple[complex, ...], ...],
                  v1: Tuple[Tuple[complex, ...], ...],
                  delta: float = 1e-8):
    for t0, t1 in zip(v0, v1):
        for value0, value1 in zip(t0, t1):
            assert abs(value0 - value1) < delta

rsqrt2 = 1. / sqrt(2.)

##########################  SingleQubitGate  ###################################

checkAllValue(I.matrix, ((1., 0.), (0., 1.)))
assert I.isUnitary == True

checkAllValue(H.matrix, ((rsqrt2, rsqrt2), (rsqrt2, -rsqrt2)))
assert H.isUnitary == True

checkAllValue(X.matrix, ((0., 1.), (1., 0.)))
assert X.isUnitary == True

checkAllValue(Y.matrix, ((0., -1j), (1j, 0.)))
assert Y.isUnitary == True

checkAllValue(Z.matrix, ((1., 0.), (0., -1.)))
assert Z.isUnitary == True

checkAllValue(S.matrix, ((1., 0.), (0., 1j)))
assert S.isUnitary == True

checkAllValue(T.matrix, ((1., 0.), (0., exp(1j*pi/4))))
assert T.isUnitary == True

TTS = Z @ T @ T @ S
assert TTS.isUnitary == True
checkAllValue(TTS.matrix, I.matrix)

for i in range(8):
    angle = 2*pi * i/8
    sa = sin(angle / 2)
    ca = cos(angle / 2)

    rotX = Rx(angle)
    assert rotX.isUnitary == True
    checkAllValue(rotX.matrix, ((ca, -1j*sa), (-1j*sa, ca)))

    rotY = Ry(angle)
    assert rotY.isUnitary == True
    checkAllValue(rotY.matrix, ((ca, -sa), (sa, ca)))

    rotZ = Rz(angle)
    assert rotZ.isUnitary == True
    checkAllValue(rotZ.matrix, ((exp(-1j*angle/2), 0.), (0., exp(1j*angle/2))))

    rot1 = R1(angle)
    assert rot1.isUnitary == True
    checkAllValue(rot1.matrix, ((1., 0.), (0., exp(1j*angle))))

checkAllValue((Z @ X @ Z).matrix, (X * -1).matrix)

myGate = SingleQubitGate(1., 1., 1., 1.)
assert myGate.isUnitary == False
myGate *= -1
checkAllValue(myGate.matrix, ((-1., -1.), (-1., -1.)))

######  A bug from python
try:
    -1 * X
except TypeError:
    print("Unsupported SingleQubitGate.__rmul__()")
# if supported, it will raise RuntimeError, instead of TypeError
# see SingleQubitGate.__rmul__ in ~/nyasQuantumCalculate/cy/nyasQC.pyi (or pyx)

############################  SingleQubit  #####################################

q = SingleQubit()
checkAllValue(q.states, ((1.,), (0.,)))
H(q)
checkAllValue(q.states, ((rsqrt2,), (rsqrt2,)))
Z(q)
checkAllValue(q.states, ((rsqrt2,), (-rsqrt2,)))
H(q)
checkAllValue(q.states, ((0.,), (1.,)))
assert M(q) == True
Reset(q)
checkAllValue(q.states, ((1.,), (0.,)))
q = None

#############################  MultiQubits  ####################################

q = MultiQubits(2)
checkAllValue(q.states, ((1.,), (0.,), (0.,), (0.,)))
H(q[0])
checkAllValue(q.states, ((rsqrt2,), (rsqrt2,), (0.,), (0.,)))
CNOT(q[0], q[1])
checkAllValue(q.states, ((rsqrt2,), (0.,), (0.,), (rsqrt2,)))
Utils.DumpMachineText(q)
q.resetAll()
ApplyToEach(H, q)
checkAllValue(q.states, ((.5,), (.5,), (.5,), (.5,)))
Z(q.getQubit(1))
ApplyToEach(H, q)
assert q.measure(0) == False and M(q[1]) == True
assert MeasureAll(q) == (False, True)

Options.checkQubitIdx = True
try:
    q.getQubit(2)
except IndexError:
    pass
else:
    raise RuntimeError

try:
    q.applyTo(H, 2)
except IndexError:
    pass
else:
    raise RuntimeError

try:
    q.control(X, [1], 1)
except ValueError:
    pass
else:
    raise RuntimeError

try:
    MultiQubits(64)
except ValueError:
    pass
else:
    raise RuntimeError

try:
    MultiQubits(63)
    # 2^67 bytes memory
except MemoryError:
    pass
else:
    raise RuntimeError

################################################################################
################################################################################

try:
    import numpy as np
except ModuleNotFoundError:
    exit()

have_cv2 = True
have_pillow = True
try:
    import cv2
except ModuleNotFoundError:
    have_cv2 = False
    try:
        from PIL import Image
    except ModuleNotFoundError:
        have_pillow = False
        try:
            from matplotlib import pyplot as plt
        except ModuleNotFoundError:
            exit()
import os

saveFile = "ColorWheel.png"
if os.path.exists(saveFile):
    exit()

figSize = 500
backgroundColor = np.array((60, 60, 60), dtype=np.uint8)
coord1D = np.linspace(-1, 1, figSize)
xCoord, yCoord = np.meshgrid(coord1D, coord1D)

im = np.ones((figSize, figSize, 3), np.uint8) * backgroundColor

def _renderProcess(x: float, y: float) -> None:
    rr = x * x + y * y
    if 0.4 <= rr <= 0.9:
        theta = convert_number(x + 1j * y)[1]
        color = np.array(ColorWheel2RGB(theta, False), dtype=np.uint8)
        alpha = 1. - np.clip(30.0 * abs(rr - 0.65) - 6.5, 0., 1.)
        color = color * alpha + backgroundColor * (1. - alpha)
        color = np.clip(color, 0., 255.)
        im[int((y+1) * figSize / 2), int((x+1) * figSize / 2)] = color

np.vectorize(_renderProcess)(xCoord, yCoord)

if have_cv2:
    cv2.imwrite(saveFile, im[..., ::-1])
elif have_pillow:
    Image.fromarray(im).save(saveFile)
else:
    plt.imsave(saveFile, im)
