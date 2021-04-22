# -*- coding: utf-8 -*-

from .ControlMethod import *
from .SingleQubitGate import *
from .QubitsOperation import *
from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.System import *


__all__ = ["SWAP"]


class _SWAP(QubitsOperation):
    """交换量子位数据

    量子数据可以移动但不可复制, 这里是直接交换两个量子位的数据. 两个
    量子位必须处于相同的量子位系统.

    To use:
    >>> qbsys = QubitsSystem(2)
    >>> q0, q1 = qbsys.getQubits()
    >>> X(q0)
    >>> qbsys.states
    array([[0.+0.j],
           [1.+0.j],
           [0.+0.j],
           [0.+0.j]])
    >>> SWAP(q0, q1)
    array([[0.+0.j],
           [0.+0.j],
           [1.+0.j],
           [0.+0.j]])
    """
    def __init__(self) -> None:
        super().__init__()
        self.name = "SWAP"
        self.trackable = True
        self.controllable = True

    def call(self, q0: Qubit, q1: Qubit) -> None:
        qbsys = q0.system
        if qbsys.nControllingQubits == 0:
            qbsys.statesNd = qbsys.statesNd.swapaxes(
                qbsys.statesNdIndex(q0.index),
                qbsys.statesNdIndex(q1.index)
            )
        else:
            # 事实上, 受控SWAP应该为
            # CNOT(q1, q0); Controlled(CNOT, ctlQbs, q0, q1); CNOT(q1, q0)
            # 而这里是
            # Controlled(CNOT, ctlQbs, q1, q0)
            # Controlled(CNOT, ctlQbs, q0, q1)
            # Controlled(CNOT, ctlQbs, q1, q0)
            # 结果上相同就好
            CNOT(q1, q0)
            CNOT(q0, q1)
            CNOT(q1, q0)

    def __call__(self, q0: Qubit, q1: Qubit) -> None:
        if Options.inputCheck:
            if not inSameSystem(q0, q1):
                raise ValueError("Two qubits are in different qubit system.")
            if any(isControllingQubits(q0, q1)):
                raise ValueError("Controlled process operates controlling bit.")
            if haveSameQubit(q0, q1):
                raise ValueError("Cannot swap the same qubit.")
        qbsys = q0.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, q0.index, q1.index)
            qbsys.stopTracking = True
        self.call(q0, q1)
        if not sysStopTrack:
            qbsys.stopTracking = False


SWAP = _SWAP()
