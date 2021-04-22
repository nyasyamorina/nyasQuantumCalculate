# -*- coding: utf-8 -*-

from typing import Any

from .QubitsSystem import *


__all__ = ["Qubit", "TemporaryQubit"]


class Qubit:
    """Qubit(QubitsSystem, int)

    单个量子位对象, 可以通过 `qbsys.getQubit(idx)` 或 `qbsys[idx]` 得到.

    因为在Qubit里面会对QubitsSystem引用一次, 所以在释放QubitsSystems前
    请确保所有相应的Qubit也被释放.

    Attributes:
        system: 量子位所在的系统
        index: 量子位索引
    """

    def __init__(self, qbsys: QubitsSystem, idx: int) -> None:
        """初始化

        Args:
            sys: 量子位所处的量子位系统
            idx: 量子位的索引, 应该从0开始到sys.nQubits-1"""
        if not 0 <= idx < qbsys.nQubits:
            raise ValueError(f"The qubit indexed {idx} does not exist.")
        self.system = qbsys
        self.index = idx

    def __str__(self) -> str:
        return f"Qubit({self.index})"

    def __repr__(self) -> str:
        return f"Qubit({self.index} in system with id:{self.system.id})"

    def __add__(self, other: Any) -> Any:
        raise NotImplementedError

    def asQubits(self) -> Any:
        """返回与自身相应的Qubits对象(system相同, index相同)

        Returns:
            (Qubits)"""
        raise NotImplementedError


class TemporaryQubit:
    """TemporaryQubit(QubitsSystem)

    配合with语句产生临时的Qubit对象, 临时Qubit的内存块在with退出时会被销毁. 在
    使用完临时Qubit后记得释放临时Qubit对象, 否则可能会引起不必要的错误.

    To use:
    >>> qbsys = QubitsSystem(4)
    >>> qbsys.nQubits
    4
    >>> with TemporaryQubit(qbsys) as tmpQb:
    ...     print(qbsys.nQubits, tmpQb)
    ...
    5 Qubit(4)
    >>> qbsys.nQubits
    4
    >>> del tmpQb           # 释放临时Qubit对象
    """

    def __init__(self, qbsys: QubitsSystem):
        self.system = qbsys

    def __enter__(self) -> Qubit:
        self.system.addQubits(1)
        return Qubit(self.system, self.system.nQubits - 1)

    def __exit__(self, *error: Any) -> None:
        self.system.popQubits(1)


###############################################################################
########################## * 你不应该调用以下方法  ##############################
###############################################################################


def QubitsSystem_getQubit(self: QubitsSystem, idx: int) -> Qubit:
    return Qubit(self, idx)


QubitsSystem.getQubit = QubitsSystem_getQubit
