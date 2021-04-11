# -*- coding: utf-8 -*-

import numpy as np

from .QubitsOperation import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *


__all__ = ["R", "RA"]


class _RESET(QubitsOperation):
    """重置一个量子位

    注意量子位只能重置振幅而不能重置相位, 如果可能的话
    请使用位门偏转相位再重置量子位.

    Args:
        qb: 需要重置的量子位
    """
    def __init__(self) -> None:
        super().__init__()
        self.name = "RESET"
        self.trackable = True

    def call(self, qb: Qubit) -> None:
        qbsys = qb.system
        states = qbsys.statesNd.swapaxes(0, qbsys.statesNdIndex(qb.index))
        prob0 = sss(states[0, ...])
        if equal0(prob0):
            states[0, ...] = states[1, ...]
        states[0, ...] /= np.sqrt(sss(states[0, ...]))
        states[1, ...] *= 0.

    def __call__(self, qb: Qubit) -> None:
        qbsys = qb.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, qb.index)
            qbsys.stopTracking = True
        self.call(qb)
        if not sysStopTrack:
            qbsys.stopTracking = False


class _RESETALL(QubitsOperation):
    """重置一个量子位

    注意量子位只能重置振幅而不能重置相位, 如果可能的话
    请使用位门偏转相位再重置量子位.

    Args:
        qbs: 需要重置的多个量子位
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "RESETALL"
        self.trackable = True

    def call(self, qbs: Qubits) -> None:
        qbsys = qbs.system
        for index in qbs.indexes:
            states = qbsys.statesNd.swapaxes(0, qbsys.statesNdIndex(index))
            prob0 = sss(states[0, ...])
            if equal0(prob0):
                states[0, ...] = states[1, ...]
            states[1, ...] *= 0.
        qbsys.normalize()

    def __call__(self, qbs: Qubits) -> None:
        qbsys = qbs.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, *qbs.indexes)
            qbsys.stopTracking = True
        self.call(qbs)
        if not sysStopTrack:
            qbsys.stopTracking = False


R = _RESET()
RA = _RESETALL()
