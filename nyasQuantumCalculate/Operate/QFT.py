# -*- coding: utf-8 -*-

import numpy as np

from .QubitsOperation import *
from .SWAP import *
from .SingleQubitGate import *
from .ControlMethod import *
from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.System import *


__all__ = ["QFT", "IQFT"]


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


def iR(n: int) -> SingleQubitGate:
    """iQFT里的相位门"""
    gate = R1(-np.pi / (1 << (n - 1)))
    gate.name = f"iR_{n}"
    return gate


def iQFT_gate(qbs: Qubits) -> None:
    # 方法一: 逆着计算QFT电路
    for idx in range(len(qbs) // 2):
        SWAP(qbs[idx], qbs[-(idx + 1)])
    iRs = [iR(n) for n in range(len(qbs), 1, -1)]
    qbsR = qbs[::-1]
    for idx0, qb in enumerate(qbsR):
        for idx1, ctlQb in enumerate(qbsR[:idx0]):
            Controlled(iRs[idx1 - idx0 + len(iRs)], ctlQb.asQubits(), qb)
        H(qb)
    # 方法二: 顺着计算QFT电路, 但逆转门
    #iRs = [iR(n) for n in range(2, len(qbs) + 1)]
    #for idx0, qb in enumerate(qbs):
    #    H(qb)
    #    for idx1, ctlQb in enumerate(qbs[idx0 + 1:]):
    #        Controlled(iRs[idx1], ctlQb.asQubits(), qb)
    #for idx in range(len(qbs) // 2):
    #    SWAP(qbs[idx], qbs[-(idx + 1)])


def iQFT_numpy(qbs: Qubits) -> None:
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


QFT = _QFT()
IQFT = _iQFT()
