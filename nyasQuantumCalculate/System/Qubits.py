# -*- coding: utf-8 -*-

from typing import Union, Any

from .QubitsSystem import *
from .Qubit import *


__all__ = ["Qubits", "TemporaryQubits"]


class Qubits:
    """Qubits(QubitsSystem, *int)

    多个量子位对象, 可以通过 `qbsys.getQubits(*idx)` 或 `qbsys[from:to]` 得到.

    因为在Qubits里面会对QubitsSystem引用一次, 所以在释放QubitsSystems前
    请确保所有相应的Qubits也被释放.

    Attributes:
        system: 量子位所在的系统
        indexes: 量子位索引
    """

    def __init__(self, qbsys: QubitsSystem, *idxs: int) -> None:
        if not all(0 <= index < qbsys.nQubits for index in idxs):
            raise ValueError("输入参数内有超出范围的索引")
        self.system = qbsys
        self.indexes = list(idxs)
        self._ptr = 0

    def __str__(self) -> str:
        return f"Qubits({len(self)} qubits)"

    def __repr__(self) -> str:
        return "Qubits([{}] in system with id:{})".format(
            # 虽然可以写为 `','.join(self.indexes)`
            # 但是类型提示会出现, 所以就写多一步了
            ','.join(str(i) for i in self.indexes),
            self.system.id
        )

    def __len__(self) -> int: return len(self.indexes)

    def __getitem__(self, idxx: Union[slice, int]) -> Any:
        if isinstance(idxx, slice):
            return Qubits(self.system, *self.indexes[idxx])
        return Qubit(self.system, self.indexes[idxx])

    def __iter__(self) -> "Qubits":
        self._ptr = 0
        return self

    def __next__(self) -> Qubit:
        if self._ptr < len(self.indexes):
            self._ptr += 1
            return Qubit(self.system, self.indexes[self._ptr - 1])
        raise StopIteration

    def __iadd__(self, other: Union[Qubit, "Qubits"]) -> "Qubits":
        assert self.system.id == other.system.id
        if isinstance(other, Qubit):
            self.indexes.append(other.index)
        else:
            self.indexes += other.indexes
        return self

    def __add__(self, other: Union[Qubit, "Qubits"]) -> "Qubits":
        result = Qubits(self.system)
        result.indexes = self.indexes.copy()
        result += other
        return result


class TemporaryQubits:
    """TemporaryQubits(QubitsSystem, int)

    配合with语句产生临时的Qubits对象, 临时Qubits的内存块在with退出时会被销毁. 在
    使用完临时Qubits后记得释放临时Qubits对象, 否则可能会引起不必要的错误.

    To use:
    >>> qbsys = QubitsSystem(4)
    >>> qbsys.nQubits
    4
    >>> with TemporaryQubits(qbsys, 3) as tmpQbs:
    ...     print(qbsys.nQubits, tmpQbs)
    ...
    7 Qubits(3 qubits)
    >>> qbsys.nQubits
    4
    >>> del tmpQbs          # 释放临时Qubits对象
    """
    def __init__(self, qbsys: QubitsSystem, nQubits: int):
        self.system = qbsys
        self.nQubits = nQubits

    def __enter__(self) -> Qubits:
        self.system.addQubits(self.nQubits)
        return Qubits(self.system, *range(self.system.nQubits - self.nQubits,
                                          self.system.nQubits))

    def __exit__(self, *error: Any) -> None:
        self.system.popQubits(self.nQubits)


###############################################################################
########################## * 你不应该调用以下方法  ##############################
###############################################################################


def Qubit___add__(self: Qubit, other: Union[Qubit, Qubits]) -> Qubits:
    if isinstance(other, Qubits):
        return other + self
    return Qubits(self.system, self.index, other.index)


def Qubit_asQubits(self: Qubit) -> Qubits:
    return Qubits(self.system, self.index)


def QubitsSystem_getQubits(self: QubitsSystem, *idxs: int) -> Qubits:
    if len(idxs) == 0:
        return Qubits(self, *range(self.nQubits))
    return Qubits(self, *idxs)


def QubitsSystem___getitem__(self: QubitsSystem,
                             idx: Union[int, slice]) -> Any:
    if isinstance(idx, slice):
        step: int = idx.step or 1
        if step > 0:
            start = idx.start or 0
            stop = idx.stop or self.nQubits
        else:
            start = idx.start or self.nQubits - 1
            stop = idx.stop or -1
        if start < 0:
            start += self.nQubits
        if stop < 0:
            stop += self.nQubits
        return Qubits(self, *range(start, stop, step))
    else:
        if idx < 0:
            idx += self.nQubits
        return Qubit(self, idx)


Qubit.__add__ = Qubit___add__
Qubit.asQubits = Qubit_asQubits

QubitsSystem.getQubits = QubitsSystem_getQubits
QubitsSystem.__getitem__ = QubitsSystem___getitem__
