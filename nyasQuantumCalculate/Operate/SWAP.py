from .QubitsOperation import *
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

    def call(self, q0: Qubit, q1: Qubit) -> None:
        q0.system.swap(q0.index, q1.index)

    def __call__(self, q0: Qubit, q1: Qubit) -> None:
        if q0.system.id != q1.system.id:
            raise ValueError("两个量子位处于不同的量子位系统")
        sysStopTrack = q0.system.stopTracking
        if q0.system.canTrack() and self.trackable:
            q0.system.addTrack((), (q0.index, q1.index), self.name)
            q0.system.stopTracking = True
        self.call(q0, q1)
        if not sysStopTrack:
            q0.system.stopTracking = False


SWAP = _SWAP()
