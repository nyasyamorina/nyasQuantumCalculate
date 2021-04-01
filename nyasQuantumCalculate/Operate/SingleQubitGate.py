# -*- coding: utf-8 -*-

from typing import Any

import numpy as np

from .QubitsOperation import *
from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *


__all__ = ["SingleQubitGate", 'I', 'H', 'X', 'Y', 'Z', 'S', 'T', "SReverse",
           "TReverse", "Rx", "Ry", "Rz", "R1"]


class SingleQubitGate(QubitsOperation):
    """SingleQubitGate(complex, complex, complex, complex,
                       str, bool, **)

    单量子位门必须是酉矩阵, 初始化前可以使用`SingleQubitGate.checkUnitGate`
    检查4个数字是否组成单量子位门. 输入参数`name`可以定义门的名字以方便跟踪, 并且
    单量子位门的`controllable`应该为True (默认为False)

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
            raise ValueError("输入参数不能构造单量子位门")
        super().__init__()
        self.name = name
        self.controllable = True
        self.trackable = True
        self.matrix = np.array(((a, b), (c, d)), np.complex128)

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

    def __call__(self, q: Qubit) -> None:
        q.system.apply(self.matrix, q.index, self.name)

    def __imul__(self, s: complex) -> "SingleQubitGate":
        assert equal0(np.abs(s) - 1.)
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
        new.matrix[0, 0] = self.matrix[0, 0] * right.matrix[0, 0] + \
            self.matrix[0, 1] * right.matrix[1, 0]
        new.matrix[0, 1] = self.matrix[0, 0] * right.matrix[0, 1] + \
            self.matrix[0, 1] * right.matrix[1, 1]
        new.matrix[1, 0] = self.matrix[1, 0] * right.matrix[0, 0] + \
            self.matrix[1, 1] * right.matrix[1, 0]
        new.matrix[1, 1] = self.matrix[1, 0] * right.matrix[0, 1] + \
            self.matrix[1, 1] * right.matrix[1, 1]
        return new


rsqrt2 = 1. / np.sqrt(2.)


I = SingleQubitGate(1., 0., 0., 1., _notCheck=True,
                    name='I', controllable=True, canTracked=False)

H = SingleQubitGate(rsqrt2, rsqrt2, rsqrt2, -rsqrt2, _notCheck=True,
                    name='H', controllable=True, canTracked=True)

X = SingleQubitGate(0., 1., 1., 0., _notCheck=True,
                    name='X', controllable=True, canTracked=True)

Y = SingleQubitGate(0., -1.j, 1.j, 0., _notCheck=True,
                    name='Y', controllable=True, canTracked=True)

Z = SingleQubitGate(1., 0., 0., -1., _notCheck=True,
                    name='Z', controllable=True, canTracked=True)

S = SingleQubitGate(1., 0., 0., 1.j, _notCheck=True,
                    name='S', controllable=True, canTracked=True)

SReverse = SingleQubitGate(1., 0., 0., -1.j, _notCheck=True,
                           name='S^-1', controllable=True, canTracked=True)

T = SingleQubitGate(1., 0., 0., rsqrt2 + 1j*rsqrt2, _notCheck=True,
                    name='T', controllable=True, canTracked=True)

TReverse = SingleQubitGate(1., 0., 0., rsqrt2 - 1j*rsqrt2, _notCheck=True,
                           name='T^-1', controllable=True, canTracked=True)


def Rx(theta: float) -> SingleQubitGate:
    a = np.cos(theta / 2.)
    b = -1j * np.sin(theta / 2.)
    return SingleQubitGate(a, b, b, a, _notCheck=True,
                           name="Rx", controllable=True, canTracked=True)


def Ry(theta: float) -> SingleQubitGate:
    a = np.cos(theta / 2.)
    b = np.sin(theta / 2.)
    return SingleQubitGate(a, -b, b, a, _notCheck=True,
                           name="Ry", controllable=True, canTracked=True)


def Rz(theta: float) -> SingleQubitGate:
    a = np.cos(theta / 2.)
    b = 1j * np.sin(theta / 2.)
    return SingleQubitGate(a - b, 0., 0., a + b, _notCheck=True,
                           name="Rz", controllable=True, canTracked=True)


def R1(theta: float) -> SingleQubitGate:
    return SingleQubitGate(1., 0., 0., np.exp(1j * theta), _notCheck=True,
                           name="R1", controllable=True, canTracked=True)
