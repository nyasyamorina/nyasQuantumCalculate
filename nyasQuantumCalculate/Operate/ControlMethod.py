# -*- coding: utf-8 -*-

from typing import Any, Iterable

from .QubitsOperation import *
from .SingleQubitGate import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *


__all__ = ["Controlled", "ControlledOnInt", "Toffoli", "CNOT", "CCNOT"]


def Controlled(opr: OperationLike, ctlQbs: Qubits,
               *args: Any, **kwargs: Any) -> Any:
    """控制过程

    把普通可控的量子位过程转为控制过程, 暂时只有单量子位门属于可控过程.

    Args:
        opr: 可控的量子位过程
        ctlQbs: 控制位
        *args, **kwargs: 输入到过程的参数

    Returns:
        opr返回的值"""
    operation = QubitsOperation.getOperation(opr)
    if not operation.controllable:
        raise ValueError("目标过程不是可控的")
    ctlQbs.system.addControllingQubits(*ctlQbs.indexes)
    result = operation(*args, **kwargs)
    ctlQbs.system.popControllingQubits()
    return result


def ControlledOnBools(opr: OperationLike, bools: Iterable[bool], ctlQbs: Qubits,
                    *args: Any, **kwargs: Any) -> Any:
    """整数控制过程

    类似`Controlled`, 但只有控制位符合bools(而不是全部为1)时, 触发
    过程opr. 当bools比ctlQbs长时会截断bools, 而bools比ctlQbs短时
    会使用True填充bools.

    Args:
        opr: 可控的量子位过程
        bools: bool列表
        ctlQbs: 控制位
        *args, **kwargs: 输入到过程的参数

    Returns:
        opr返回的值
    """
    for bit, qubit in zip(bools, ctlQbs):
        if not bit:
            X(qubit)
    result = Controlled(opr, ctlQbs, *args, **kwargs)
    for bit, qubit in zip(bools, ctlQbs):
        if not bit:
            X(qubit)
    return result


def ControlledOnInt(opr: OperationLike, integer: int, ctlQbs: Qubits,
                    *args: Any, **kwargs: Any) -> Any:
    """整数控制过程

    类似`Controlled`, 但只有控制位符合integer(而不是全部为1)时, 触发
    过程opr. 当integer位数比ctlQbs长时会截断高位

    Args:
        opr: 可控的量子位过程
        integer: 目标整数
        ctlQbs: 控制位
        *args, **kwargs: 输入到过程的参数

    Returns:
        opr返回的值
    """
    bits = Int2Bools(integer, len(ctlQbs))
    result = ControlledOnBools(opr, bits, ctlQbs, *args, **kwargs)
    return result


class _CNOT(QubitsOperation):
    """CNOT门 (可逆XOR门)

    两个量子位必须处于相同的量子位系统.

    Args:
        q0: 控制位
        q1: 被控制位
    """
    def __init__(self) -> None:
        super().__init__()
        self.name = "CNOT"
        self.controllable = True

    def call(self, q0: Qubit, q1: Qubit) -> None:
        Controlled(X, q0.asQubits(), q1)

    def __call__(self, q0: Qubit, q1: Qubit) -> None:
        if q0.system.id != q1.system.id:
            raise ValueError("两个量子位处于不同的量子位系统")
        qbsys = q0.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, q0.index, q1.index)
            qbsys.stopTracking = True
        self.call(q0, q1)
        if not sysStopTrack:
            qbsys.stopTracking = False


class _CCNOT(QubitsOperation):
    """Toffoli门 (CCNOT门, 可逆AND门)

    三个量子位必须处于相同的量子位系统.

    Args:
        q0: 控制位
        q1: 控制位
        q2: 被控制位
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "CCNOT"
        self.controllable = True

    def call(self, q0: Qubit, q1: Qubit, q2: Qubit) -> None:
        Controlled(X, q0 + q1, q2)

    def __call__(self, q0: Qubit, q1: Qubit, q2: Qubit) -> None:
        if q0.system.id != q1.system.id or \
                q0.system.id != q2.system.id:
            raise ValueError("三个量子位处于不同的量子位系统")
        qbsys = q0.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, q0.index, q1.index, q2.index)
            qbsys.stopTracking = True
        self.call(q0, q1, q2)
        if not sysStopTrack:
            qbsys.stopTracking = False


CNOT = _CNOT()
CCNOT = _CCNOT()
Toffoli = CCNOT
