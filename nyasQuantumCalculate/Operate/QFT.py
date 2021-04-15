# -*- coding: utf-8 -*-

import numpy as np

from .QubitsOperation import *
from .Swap import *
from .SingleQubitGate import *
from .ControlMethod import *
from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.System import *


__all__ = ["QFT", "IQFT", "AQFT", "IAQFT"]


def R(n: int) -> SingleQubitGate:
    """QFT里的相位门"""
    gate = R1(np.pi / (1 << (n - 1)))
    gate.name = f"R_{n}"
    return gate


def QFT_gate(qbs: Qubits) -> None:
    Rs = [R(n) for n in range(2, len(qbs) + 1)]
    for idx0, qb in enumerate(qbs):
        H(qb)
        for idx1, ctlQb in enumerate(qbs[idx0 + 1:]):
            Controlled(Rs[idx1], ctlQb.asQubits(), qb)
    if Options.QFTswap:
        for idx in range(len(qbs) // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])


def QFT_numpy(qbs: Qubits) -> None:
    qbsys = qbs.system
    qbs_indexes = [qbsys.statesNdIndex(index) for index in qbs.indexes]
    indexesR = qbs_indexes + [index for index in range(qbsys.nQubits)
                              if index not in qbs_indexes]
    indexes = list(range(qbsys.nQubits))
    for index0, index1 in enumerate(indexesR):
        indexes[index1] = index0
    states = qbsys.statesNd. \
        transpose(indexesR). \
        reshape([-1] + [2] * (qbsys.nQubits - len(qbs)))
    states: np.ndarray = 2 ** (len(qbs) / 2) * \
        np.fft.ifft(states, axis=0)
    qbsys.statesNd = states.reshape([2] * qbsys.nQubits).transpose(indexes)
    if not Options.QFTswap:
        for idx in range(len(qbs) // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])


def iR(n: int) -> SingleQubitGate:
    """iQFT里的相位门"""
    gate = R1(-np.pi / (1 << (n - 1)))
    gate.name = f"iR_{n}"
    return gate


def iQFT_gate(qbs: Qubits) -> None:
    iRs = [iR(n) for n in range(2, len(qbs) + 1)]
    for idx0, qb in enumerate(qbs):
        H(qb)
        for idx1, ctlQb in enumerate(qbs[idx0 + 1:]):
            Controlled(iRs[idx1], ctlQb.asQubits(), qb)
    if Options.QFTswap:
        for idx in range(len(qbs) // 2):
            SWAP(qbs[idx], qbs[-(idx + 1)])


def iQFT_numpy(qbs: Qubits) -> None:
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
    states = qbsys.statesNd. \
        transpose(indexesR). \
        reshape([-1] + [2] * (qbsys.nQubits - len(qbs)))
    states: np.ndarray = 2 ** (-len(qbs) / 2) * \
        np.fft.fft(states, axis=0)
    qbsys.statesNd = states.reshape([2] * qbsys.nQubits).transpose(indexes)


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

    def call(self, qbs: Qubits) -> None:
        if Options.QFTwithNumpy:
            QFT_numpy(qbs)
        else:
            QFT_gate(qbs)

    def __call__(self, qbs: Qubits) -> None:
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

    def call(self, qbs: Qubits) -> None:
        if Options.QFTwithNumpy:
            iQFT_numpy(qbs)
        else:
            iQFT_gate(qbs)

    def __call__(self, qbs: Qubits) -> None:
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

    def call(self, qbs: Qubits, m: int) -> None:
        Rs = [R(i) for i in range(2, m + 1)]
        for idx0, qb in enumerate(qbs):
            H(qb)
            for idx1, ctl in enumerate(qbs[idx0 + 1: min(idx0 + m, len(qbs))]):
                Controlled(Rs[idx1], ctl.asQubits(), qb)
        if Options.QFTswap:
            for idx in range(len(qbs) // 2):
                SWAP(qbs[idx], qbs[-(idx + 1)])

    def __call__(self, qbs: Qubits, m: int) -> None:
        if m <= 0 or m > len(qbs):
            raise ValueError("'m' should be greater than 0 and "
                             "lower or equal to len(qbs)")
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

    def call(self, qbs: Qubits, m: int) -> None:
        iRs = [iR(i) for i in range(2, m + 1)]
        for idx0, qb in enumerate(qbs):
            H(qb)
            for idx1, ctl in enumerate(qbs[idx0 + 1: min(idx0 + m, len(qbs))]):
                Controlled(iRs[idx1], ctl.asQubits(), qb)
        if Options.QFTswap:
            for idx in range(len(qbs) // 2):
                SWAP(qbs[idx], qbs[-(idx + 1)])

    def __call__(self, qbs: Qubits, m: int) -> None:
        if m <= 0 or m > len(qbs):
            raise ValueError("'m' should be greater than 0 and "
                             "lower or equal to len(qbs)")
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
