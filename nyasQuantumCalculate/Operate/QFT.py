# -*- coding: utf-8 -*-

import numpy as np

from .QubitsOperation import *
from .Swap import *
from .SingleQubitGate import *
from .ControlMethod import *
from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.System import *


__all__ = ["QFT", "IQFT", "AQFT", "IAQFT"]


def QFT_gate(qbs: Qubits) -> None:
    n = len(qbs)
    if n == 0:
        return
    if n == 1:
        H(qbs[0])
        return
    RotationGates.updateRs(n)
    for idx0, qb in enumerate(qbs):
        H(qb)
        for idx1, ctlQb in enumerate(qbs[idx0 + 1:]):
            Controlled(RotationGates.Rs[idx1 + 1], ctlQb.asQubits(), qb)
    if Options.QFTswap:
        for idx in range(n // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])


def iQFT_gate(qbs: Qubits) -> None:
    n = len(qbs)
    if n == 0:
        return
    if n == 1:
        H(qbs[0])
        return
    RotationGates.updateiRs(n)
    if Options.QFTswap:
        for idx in range(n // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])
    for idx0, qb in enumerate(qbs[::-1]):
        for idx1, ctlQb in enumerate(qbs[n - idx0:]):
            Controlled(RotationGates.iRs[idx1 + 1], ctlQb.asQubits(), qb)
        H(qb)


def QFT_numpy(qbs: Qubits) -> None:
    if len(qbs) == 0:
        return
    qbsys = qbs.system
    qbs_indexes = [qbsys.statesNdIndex(index) for index in qbs.indexes]
    indexesR = qbs_indexes + [index for index in range(qbsys.nQubits)
                              if index not in qbs_indexes]
    indexes = list(range(qbsys.nQubits))
    for index0, index1 in enumerate(indexesR):
        indexes[index1] = index0
    controlling = (..., *([1] * qbsys.nControllingQubits))
    states = qbsys.statesNd. \
        transpose(indexesR). \
        reshape([-1] + [2] * (qbsys.nQubits - len(qbs))).copy()
    after: np.ndarray = 2 ** (len(qbs) / 2) * \
        np.fft.ifft(states.__getitem__(controlling), axis=0)
    states.__setitem__(controlling, after)
    qbsys.statesNd *= 0.
    qbsys.statesNd += states.reshape([2] * qbsys.nQubits).transpose(indexes)
    if not Options.QFTswap:
        for idx in range(len(qbs) // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])


def iQFT_numpy(qbs: Qubits) -> None:
    if len(qbs) == 0:
        return
    if not Options.QFTswap:
        for idx in range(len(qbs) // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])
    qbsys = qbs.system
    qbs_indexes = [qbsys.statesNdIndex(index) for index in qbs.indexes]
    indexesR = qbs_indexes + [index for index in range(qbsys.nQubits)
                              if index not in qbs_indexes]
    indexes = list(range(qbsys.nQubits))
    for index0, index1 in enumerate(indexesR):
        indexes[index1] = index0
    controlling = (..., *([1] * qbsys.nControllingQubits))
    states = qbsys.statesNd. \
        transpose(indexesR). \
        reshape([-1] + [2] * (qbsys.nQubits - len(qbs))).copy()
    after: np.ndarray = 2 ** (-len(qbs) / 2) * \
        np.fft.fft(states.__getitem__(controlling), axis=0)
    states.__setitem__(controlling, after)
    qbsys.statesNd *= 0.
    qbsys.statesNd += states.reshape([2] * qbsys.nQubits).transpose(indexes)


class _QFT(QubitsOperation):
    """量子傅里叶变换

    To use:
        >>> qbsys = QubitsSystem(2)
        >>> qbs = qbsys.getQubits()
        >>> ApplyToEach(X, qbs)
        >>> qbsys.states
        array([[0.+0.j],
               [0.+0.j],
               [0.+0.j],
               [1.+0.j]])
        >>> QFT(qbs)
        >>> qbsys.states
        array([[ 5.000000e-01+0.j ],
               [-5.000000e-01+0.j ],
               [-3.061617e-17-0.5j],
               [ 3.061617e-17+0.5j]])
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "QFT"
        self.trackable = True
        self.controllable = True

    def call(self, qbs: Qubits) -> None:
        if Options.QFTwithNumpy:
            QFT_numpy(qbs)
        else:
            QFT_gate(qbs)

    def __call__(self, qbs: Qubits) -> None:
        if Options.inputCheck:
            if any(isControllingQubits(qbs)):
                raise ValueError("Controlled process operates controlling bit.")
            if qbs.haveSameQubit():
                raise ValueError("QFT cannot operate multiple same qubits.")
        sysStopTrack = qbs.system.stopTracking
        if qbs.system.canTrack() and self.trackable:
            qbs.system.addTrack(self.name, *qbs.indexes)
            qbs.system.stopTracking = True
        self.call(qbs)
        if not sysStopTrack:
            qbs.system.stopTracking = False


class _iQFT(QubitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "iQFT"
        self.trackable = True
        self.controllable = True

    def call(self, qbs: Qubits) -> None:
        if Options.QFTwithNumpy:
            iQFT_numpy(qbs)
        else:
            iQFT_gate(qbs)

    def __call__(self, qbs: Qubits) -> None:
        if Options.inputCheck:
            if any(isControllingQubits(qbs)):
                raise ValueError("Controlled process operates controlling bit.")
            if qbs.haveSameQubit():
                raise ValueError("QFT cannot operate multiple same qubits.")
        sysStopTrack = qbs.system.stopTracking
        if qbs.system.canTrack() and self.trackable:
            qbs.system.addTrack(self.name, *qbs.indexes)
            qbs.system.stopTracking = True
        self.call(qbs)
        if not sysStopTrack:
            qbs.system.stopTracking = False


class _AQFT(QubitsOperation):
    """近似量子傅里叶变换

    比起QFT, AQFT在存在退相干时精度更高, 并且需要的位门更少. 输入m(int)
    是控制AQFT精度的参数, m只能大于0小于等于输入qbs的长度. 当
    m=1时, 即是Hadamard变换, m=输入qbs长度即为QFT.

    注意: AQFT是由位门实现的, 而在这里QFT提供numpy实现, 在很多量子位
    的情况下numpy实现的QFT比位门实现的AQFT要快很多倍.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "AQFT"
        self.trackable = True
        self.controllable = True

    def call(self, qbs: Qubits, m: int) -> None:
        n = len(qbs)
        if n == 0:
            return
        if n == 1:
            H(qbs[0])
            return
        RotationGates.updateRs(n)
        for idx0, qb in enumerate(qbs):
            H(qb)
            for idx1, ctl in enumerate(qbs[idx0 + 1: min(idx0 + m, len(qbs))]):
                Controlled(RotationGates.Rs[idx1 + 1], ctl.asQubits(), qb)
        if Options.QFTswap:
            for idx in range(len(qbs) // 2):
                SWAP(qbs[idx], qbs[-(idx + 1)])

    def __call__(self, qbs: Qubits, m: int) -> None:
        if Options.inputCheck:
            if m <= 0 or m > len(qbs):
                raise ValueError("'m' should be greater than 0 and "
                                "lower or equal to len(qbs)")
            if any(isControllingQubits(qbs)):
                raise ValueError("Controlled process operates controlling bit.")
            if qbs.haveSameQubit():
                raise ValueError("QFT cannot operate multiple same qubits.")
        sysStopTrack = qbs.system.stopTracking
        if qbs.system.canTrack() and self.trackable:
            qbs.system.addTrack(self.name + f"_{m}", *qbs.indexes)
            qbs.system.stopTracking = True
        self.call(qbs, m)
        if not sysStopTrack:
            qbs.system.stopTracking = False


class _iAQFT(QubitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "iAQFT"
        self.trackable = True
        self.controllable = True

    def call(self, qbs: Qubits, m: int) -> None:
        n = len(qbs)
        if n == 0:
            return
        if n == 1:
            H(qbs[0])
            return
        RotationGates.updateiRs(n)
        for idx0, qb in enumerate(qbs):
            H(qb)
            for idx1, ctl in enumerate(qbs[idx0 + 1: min(idx0 + m, len(qbs))]):
                Controlled(RotationGates.iRs[idx1 + 1], ctl.asQubits(), qb)
        if Options.QFTswap:
            for idx in range(len(qbs) // 2):
                SWAP(qbs[idx], qbs[-(idx + 1)])

    def __call__(self, qbs: Qubits, m: int) -> None:
        if Options.inputCheck:
            if m <= 0 or m > len(qbs):
                raise ValueError("'m' should be greater than 0 and "
                                "lower or equal to len(qbs)")
            if any(isControllingQubits(qbs)):
                raise ValueError("Controlled process operates controlling bit.")
            if qbs.haveSameQubit():
                raise ValueError("QFT cannot operate multiple same qubits.")
        sysStopTrack = qbs.system.stopTracking
        if qbs.system.canTrack() and self.trackable:
            qbs.system.addTrack(self.name + f"_{m}", *qbs.indexes)
            qbs.system.stopTracking = True
        self.call(qbs, m)
        if not sysStopTrack:
            qbs.system.stopTracking = False


QFT = _QFT()
IQFT = _iQFT()

AQFT = _AQFT()
IAQFT = _iAQFT()
