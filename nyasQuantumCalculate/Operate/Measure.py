# -*- coding: utf-8 -*-

from typing import List

import numpy as np

from .QubitsOperation import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *


__all__ = ["M", "MA"]


class _MEASURE(QubitsOperation):
    """重置一个量子位

    注意量子位只能重置振幅而不能重置相位, 如果可能的话
    请使用位门偏转相位再重置量子位.

    Args:
        qb: 需要重置的量子位
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "MEASURE"
        self.trackable = True

    def call(self, qb: Qubit) -> bool:
        qbsys = qb.system
        states = qbsys.statesNd.swapaxes(0, qbsys.statesNdIndex(qb.index))
        prob0 = sss(states[0, ...])
        prob1 = sss(states[1, ...])
        choice = 0 if np.random.random() * (prob0 + prob1) <= prob0 else 1
        states[choice, ...] /= np.sqrt(sss(states[choice, ...]))
        states[1 - choice, ...] *= 0.
        return choice == 1

    def __call__(self, qb: Qubit) -> bool:
        qbsys = qb.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, qb.index)
            qbsys.stopTracking = True
        result = self.call(qb)
        if not sysStopTrack:
            qbsys.stopTracking = False
        return result


class _MEASUREALL(QubitsOperation):
    """重置一个量子位

    注意量子位只能重置振幅而不能重置相位, 如果可能的话
    请使用位门偏转相位再重置量子位.

    Args:
        qbs: 需要重置的多个量子位
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "MEASUREALL"
        self.trackable = True

    def call(self, qbs: Qubits) -> List[bool]:
        qbsys = qbs.system
        result: List[bool] = list()
        for index in qbs.indexes:
            states = qbsys.statesNd.swapaxes(0, qbsys.statesNdIndex(index))
            prob0 = sss(states[0, ...])
            prob1 = sss(states[1, ...])
            choice = 0 if np.random.random() * (prob0 + prob1) <= prob0 else 1
            states[1 - choice, ...] *= 0.
            result.append(choice == 1)
        qbsys.normalize()
        return result

    def __call__(self, qbs: Qubits) -> List[bool]:
        qbsys = qbs.system
        sysStopTrack = qbsys.stopTracking
        if qbsys.canTrack() and self.trackable:
            qbsys.addTrack(self.name, *qbs.indexes)
            qbsys.stopTracking = True
        result = self.call(qbs)
        if not sysStopTrack:
            qbsys.stopTracking = False
        return result


M = _MEASURE()
MA = _MEASUREALL()
