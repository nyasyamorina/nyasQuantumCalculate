# -*- coding: utf-8 -*-

from typing import Any, List

import numpy as np

from .QubitsOperation import *
from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *


__all__ = ["SingleQubitGate", "Rx", "Ry", "Rz", "R1", "Phase", "RotationGates",
           "I", "H", "X", "Y", "Z", "S", "T", "SR", "TR"]


class SingleQubitGate(QubitsOperation):
    """SingleQubitGate(complex, complex, complex, complex, str, **)

    单量子位门必须是酉矩阵, 初始化前可以使用`SingleQubitGate.checkUnitGate`
    检查4个数字是否组成单量子位门. 输入参数`name`可以定义门的名字以方便跟踪. 并且
    被作用单量子位门的量子位不能是控制位.

    Attributes:
        matrix: 单量子位门里的矩阵
    """

    def __init__(self,
                 a: complex, b: complex,
                 c: complex, d: complex,
                 name: str = "",
                 **kwargs: Any) -> None:
        if not kwargs.get("_notCheck", False) and \
                not self.checkUnitGate(a, b, c, d):
            raise ValueError("Input parameters cannot build a qubit gate.")
        super().__init__()
        self.name = name
        self.controllable = True
        self.trackable = True
        self._isBuiltin = kwargs.get("_isBuiltin", False)
        self.matrix = np.array(((a, b), (c, d)), np.complex128)

    def copy(self) -> "SingleQubitGate":
        new = SingleQubitGate(0., 0., 0., 0., _notCheck=True)
        new.name = self.name
        new.controllable = self.controllable
        self.trackable = self.trackable
        new.matrix = self.matrix.copy()
        return new

    @staticmethod
    def checkUnitGate(a: complex, b: complex, c: complex, d: complex) -> bool:
        """检查参数是否可以组成单量子位门

        Args:
            a: 矩阵里左上元素
            b: 矩阵里右上元素
            c: 矩阵里左下元素
            d: 矩阵里右下元素

        Returns:
            True为可以组成单量子位门"""
        absA = np.square(np.abs(a))
        absB = np.square(np.abs(b))
        absC = np.square(np.abs(c))
        absD = np.square(np.abs(d))
        return equal0(np.abs(a * np.conj(c) + b * np.conj(d))) and \
            equal0(np.abs(a * np.conj(b) + c * np.conj(d))) and \
            equal0(absA + absB - 1.) and equal0(absA + absC - 1.) and \
            equal0(absD + absB - 1.) and equal0(absD + absC - 1.)

    def __str__(self) -> str:
        return f"{self.name} Gate"

    def __repr__(self) -> str:
        (a, b), (c, d) = self.matrix
        return f"{self.name}[{a:.2f} {b:.2f}; {c:.2f} {d:.2f}]"

    def call(self, qb: Qubit) -> None:
        qbsys = qb.system
        m = self.matrix
        controlling0 = (0, ..., *([1] * qbsys.nControllingQubits))
        controlling1 = (1, ..., *([1] * qbsys.nControllingQubits))
        states = qbsys.statesNd.swapaxes(0, qbsys.statesNdIndex(qb.index))
        new0 = states.__getitem__(controlling0).copy()
        if m[0, 1] == 0.:
            new0 *= m[0, 0]
        else:
            new0 *= m[0, 0] / m[0, 1]
            new0 += states.__getitem__(controlling1)
            new0 *= m[0, 1]
        new1 = states.__getitem__(controlling0).copy()
        if m[1, 1] == 0.:
            new1 *= m[1, 0]
        else:
            new1 *= m[1, 0] / m[1, 1]
            new1 += states.__getitem__(controlling1)
            new1 *= m[1, 1]
        states.__setitem__(controlling0, new0)
        states.__setitem__(controlling1, new1)
        if Options.autoNormalize:
            qbsys.normalize()

    def __call__(self, qb: Qubit) -> None:
        qbsys = qb.system
        if Options.inputCheck and qbsys.isControlling(qb.index):
            raise ValueError("受控过程作用在控制位上")
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, qb.index)
            qbsys.stopTracking = True
        self.call(qb)
        if not sysStopTrack:
            qbsys.stopTracking = False

    def __imul__(self, s: complex) -> "SingleQubitGate":
        if self._isBuiltin:
            raise NotImplementedError("The built-in gate cannot be modified.")
        if not equal0(np.abs(s) - 1.):
            raise ValueError("The norm of the scalar multiplication"
                             " must equal to 1.")
        self.matrix *= s
        return self

    def __mul__(self, s: complex) -> "SingleQubitGate":
        new = SingleQubitGate(0., 0., 0., 0., _notCheck=True)
        new.matrix = self.matrix.copy()
        return new.__imul__(s)

    def __rmul__(self, s: complex) -> "SingleQubitGate":
        return self.__mul__(s)

    def __matmul__(self, right: "SingleQubitGate") -> "SingleQubitGate":
        new = SingleQubitGate(0., 0., 0., 0., _notCheck=True)
        new.matrix = self.matrix @ right.matrix
        return new

    def __ipow__(self, n: complex) -> "SingleQubitGate":
        if self._isBuiltin:
            raise NotImplementedError("The built-in gate cannot be modified.")
        v, Q = np.linalg.eig(self.matrix)
        self.matrix *= 0
        self.matrix += Q @ np.diag(v ** n) @ np.linalg.inv(Q)
        return self

    def __pow__(self, n: complex) -> "SingleQubitGate":
        new = SingleQubitGate(0., 0., 0., 0., _notCheck=True)
        new.matrix = self.matrix.copy()
        return new.__ipow__(n)


###############################################################################
############################  Built-in Gates  #################################
###############################################################################
rsqrt2 = 1. / np.sqrt(2.)


I = SingleQubitGate(1., 0., 0., 1.,
                    _notCheck=True, _isBuiltin=True, name='I')
I.trackable = False

H = SingleQubitGate(rsqrt2, rsqrt2, rsqrt2, -rsqrt2,
                    _notCheck=True, _isBuiltin=True, name='H')

X = SingleQubitGate(0., 1., 1., 0.,
                    _notCheck=True, _isBuiltin=True, name='X')

Y = SingleQubitGate(0., -1.j, 1.j, 0.,
                    _notCheck=True, _isBuiltin=True, name='Y')

Z = SingleQubitGate(1., 0., 0., -1.,
                    _notCheck=True, _isBuiltin=True, name='Z')

S = SingleQubitGate(1., 0., 0., 1.j,
                    _notCheck=True, _isBuiltin=True, name='S')

SR = SingleQubitGate(1., 0., 0., -1.j,
                     _notCheck=True, _isBuiltin=True, name='S^-1')

T = SingleQubitGate(1., 0., 0., rsqrt2 + 1j*rsqrt2,
                    _notCheck=True, _isBuiltin=True, name='T')

TR = SingleQubitGate(1., 0., 0., rsqrt2 - 1j*rsqrt2,
                     _notCheck=True, _isBuiltin=True, name='T^-1')


def Rx(theta: float) -> SingleQubitGate:
    a = np.cos(theta / 2.)
    b = -1j * np.sin(theta / 2.)
    return SingleQubitGate(a, b, b, a,
                           _notCheck=True, name=f"Rx({theta:.4f})")


def Ry(theta: float) -> SingleQubitGate:
    a = np.cos(theta / 2.)
    b = np.sin(theta / 2.)
    return SingleQubitGate(a, -b, b, a,
                           _notCheck=True, name=f"Ry({theta:.4f})")


def Rz(theta: float) -> SingleQubitGate:
    a = np.cos(theta / 2.)
    b = 1j * np.sin(theta / 2.)
    return SingleQubitGate(a - b, 0., 0., a + b,
                           _notCheck=True, name=f"Rz({theta:.4f})")


def R1(theta: float) -> SingleQubitGate:
    """|1❭相位旋转门, 实际上 R1(theta) = Phase(theta/2) @ Rz(theta)"""
    return SingleQubitGate(1., 0., 0., np.exp(1j * theta),
                           _notCheck=True, name=f"R1({theta:.4f})")


def Phase(theta: float) -> SingleQubitGate:
    ph = np.exp(1j * theta)
    return SingleQubitGate(ph, 0., 0., ph,
                           _notCheck=True, name=f"Ph({theta:.4f})")


class RotationGates:
    """RotationGates(x)

    这个类不应该被初始化.

    用于管理QFT和Add等地方使用的旋转门, 通过`Rs`和`iRs`的索引可以获取相应的门. 比如
    `RotationGates.Rs[4]` 可以获取 `R1(2*pi/2**4)` 而`iRs`是`Rs`的逆门. 记得
    在索引前使用`RotationGates.updateRs(int)`来确保门已被初始化.
    """
    Rs: List[SingleQubitGate] = list()
    iRs: List[SingleQubitGate] = list()

    @ staticmethod
    def R(n: int) -> SingleQubitGate:
        gate = R1(pi / (1 << (n - 1)))
        gate.name = f"R_{n}"
        return gate

    @staticmethod
    def iR(n: int) -> SingleQubitGate:
        """iQFT里的相位门"""
        gate = R1(-pi / (1 << (n - 1)))
        gate.name = f"iR_{n}"
        return gate

    @classmethod
    def updateRs(cls, n: int) -> None:
        if n > len(cls.Rs):
            cls.Rs += [cls.R(i) for i in range(len(cls.Rs) + 1, n + 1)]

    @ classmethod
    def updateiRs(cls, n: int) -> None:
        if n > len(cls.iRs):
            cls.iRs += [cls.iR(i) for i in range(len(cls.iRs) + 1, n + 1)]
