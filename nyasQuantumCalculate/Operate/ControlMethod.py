# -*- coding: utf-8 -*-

from typing import Any

from .QubitsOperation import *
from .SingleQubitGate import *
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
    ctlQbs.system.setControllingQubits(*ctlQbs.indexes)
    result = operation(*args, **kwargs)
    ctlQbs.system.removeControllingQubits()
    return result


def ControlledOnInt(opr: OperationLike, integer: int, ctlQbs: Qubits,
                    *args: Any, **kwargs: Any) -> Any:
    """整数控制过程

    类似`Controlled`, 但只有控制位符合integer(而不是全部为1)时, 触发
    过程opr. 当integer位数比ctlQbs位数长时会截断高位

    Args:
        opr: 可控的量子位过程
        integer: 目标整数
        ctlQbs: 控制位
        *args, **kwargs: 输入到过程的参数

    Returns:
        opr返回的值
    """
    bits = [False] * len(ctlQbs)
    for index in range(len(ctlQbs)):
        if integer == 0:
            break
        bits[index] = integer & 1 == 1      # integer % 2 == 1
        integer >>= 1
    for bit, qubit in zip(bits, ctlQbs):
        if not bit:
            X(qubit)
    result = Controlled(opr, ctlQbs, *args, **kwargs)
    for bit, qubit in zip(bits, ctlQbs):
        if not bit:
            X(qubit)
    return result


def _cnot(q0: Qubit, q1: Qubit) -> None:
    """CNOT门 (可逆XOR门)

    两个量子位必须处于相同的量子位系统.

    Args:
        q0: 控制位
        q1: 被控制位"""
    if q0.system.id != q1.system.id:
        raise ValueError("两个量子位处于不同的量子位系统")
    Controlled(X, q0.asQubits(), q1)


def Toffoli(q0: Qubit, q1: Qubit, q2: Qubit) -> None:
    """Toffoli门 (CCNOT门, 可逆AND门)

    三个量子位必须处于相同的量子位系统.

    Args:
        q0: 控制位
        q1: 控制位
        q2: 被控制位"""
    if q0.system.id != q1.system.id or \
            q0.system.id != q2.system.id:
        raise ValueError("三个量子位处于不同的量子位系统")
    Controlled(X, q0 + q1, q2)


CNOT = _cnot
CCNOT = Toffoli
