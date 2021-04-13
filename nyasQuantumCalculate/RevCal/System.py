# -*- coding: utf-8 -*-

from typing import Any, List, Tuple, Union

from nyasQuantumCalculate.Options import *


__all__ = ["BitsSystem", "Bit", "Bits", "TemporaryBit", "TemporaryBits"]


class id_manager:
    _last_id = -1

    @classmethod
    def getID(cls) -> int:
        cls._last_id += 1
        return cls._last_id


class BitsSystem:
    def __init__(self, nBits: int) -> None:
        self.states = [False] * nBits
        self._id = id_manager.getID()
        self.ctlBits: List[int] = list()
        self._ctlBitPkgs: List[List[int]] = list()
        self._tracker: List[Tuple[Tuple[int, ...],
                                  Tuple[int, ...], str]] = list()
        self.stopTracking = False

    def __del__(self) -> None:
        if Options.checkCleaningSystem and any(self.states):
            raise RuntimeError("Before cleaning up bits system, "
                               "system should be reset.")

    @property
    def nBits(self) -> int: return len(self.states)

    @property
    def id(self) -> int: return self._id

    def getBit(self, idx: int) -> Any:
        raise NotImplementedError

    def getBits(self, *idxs: int) -> Any:
        raise NotImplementedError

    def __getitem__(self, idx: Union[int, slice]) -> Any:
        raise NotImplementedError

    def restart(self) -> None:
        for index in range(self.nBits):
            self.states[index] = False

    ##########################  Related to tracking  ##########################

    def canTrack(self) -> bool:
        return Options.allowTracking and not self.stopTracking

    def addTrack(self, name: str, *idxs: int) -> None:
        self._tracker.append((tuple(self.ctlBits), tuple(idxs), name))

    ####################  Related to controlling bits  ########################

    def addControllingBits(self, *idxs: int) -> None:
        if not idxs:
            return
        if any(idx in self.ctlBits for idx in idxs):
            raise ValueError("控制位被重复添加")
        self._ctlBitPkgs.append(list(idxs))
        self.updateControllingBits()

    def popControllingBits(self) -> None:
        if not self._ctlBitPkgs:
            return
        self._ctlBitPkgs.pop()
        self.updateControllingBits()

    def updateControllingBits(self) -> None:
        self.ctlBits.clear()
        if not self._ctlBitPkgs:
            return
        for pkg in self._ctlBitPkgs:
            self.ctlBits += pkg

    #####################  Related to temporary bit  ##########################

    def addBits(self, nBits: int) -> None:
        if nBits <= 0:
            raise ValueError(f"Cannot add {nBits} bits.")
        self.states += [False] * nBits

    def popBits(self, nBits: int) -> None:
        if nBits <= 0:
            raise ValueError(f"Cannot add {nBits} bits.")
        if any(idx >= self.nBits - nBits for idx in self.ctlBits):
            raise ValueError("被移除的位是控制位")
        self.states = self.states[:-nBits]


###############################################################################
###############################################################################


class Bit:
    def __init__(self, bsys: BitsSystem, idx: int) -> None:
        if not 0 <= idx < bsys.nBits:
            raise ValueError(f"索引为 {idx} 的位不存在")
        self.system = bsys
        self.index = idx

    def __add__(self, other: "Bit") -> Any:
        raise NotImplementedError

    def asBits(self) -> Any:
        raise NotImplementedError


class TemporaryBit:
    def __init__(self, bsys: BitsSystem):
        self.system = bsys

    def __enter__(self) -> Bit:
        self.system.addBits(1)
        return Bit(self.system, self.system.nBits - 1)

    def __exit__(self, *error: Any) -> None:
        self.system.popBits(1)


###############################################################################
###############################################################################


class Bits:
    def __init__(self, bsys: BitsSystem, *idxs: int) -> None:
        if not all(0 <= index < bsys.nBits for index in idxs):
            raise ValueError("输入参数内有超出范围的索引")
        self.system = bsys
        self.indexes = list(idxs)
        self._ptr = 0

    def __len__(self) -> int: return len(self.indexes)

    def __getitem__(self, idxx: Union[slice, int]) -> Any:
        if isinstance(idxx, slice):
            return Bits(self.system, *self.indexes[idxx])
        return Bit(self.system, self.indexes[idxx])

    def __iter__(self) -> "Bits":
        self._ptr = 0
        return self

    def __next__(self) -> Bit:
        if self._ptr < len(self.indexes):
            self._ptr += 1
            return Bit(self.system, self.indexes[self._ptr - 1])
        raise StopIteration

    def __iadd__(self, other: Union[Bit, "Bits"]) -> "Bits":
        assert self.system.id == other.system.id
        if isinstance(other, Bit):
            self.indexes.append(other.index)
        else:
            self.indexes += other.indexes
        return self

    def __add__(self, other: Union[Bit, "Bits"]) -> "Bits":
        result = Bits(self.system)
        result.indexes = self.indexes.copy()
        result += other
        return result


class TemporaryBits:
    def __init__(self, bsys: BitsSystem, nBits: int):
        self.system = bsys
        self.nBits = nBits

    def __enter__(self) -> Bits:
        self.system.addBits(self.nBits)
        return Bits(self.system, *range(self.system.nBits - self.nBits,
                                          self.system.nBits))

    def __exit__(self, *error: Any) -> None:
        self.system.popBits(self.nBits)


###############################################################################
###############################################################################


def BitsSystem_getBit(self: BitsSystem, idx: int) -> Bit:
    return Bit(self, idx)


def Bit___add__(self: Bit, other: Union[Bit, Bits]) -> Bits:
    if isinstance(other, Bits):
        return other + self
    return Bits(self.system, self.index, other.index)


def Bit_asBits(self: Bit) -> Bits:
    return Bits(self.system, self.index)


def BitsSystem_getBits(self: BitsSystem, *idxs: int) -> Bits:
    if len(idxs) == 0:
        return Bits(self, *range(self.nBits))
    return Bits(self, *idxs)


def BitsSystem___getitem__(self: BitsSystem,
                             idx: Union[int, slice]) -> Any:
    if isinstance(idx, slice):
        step: int = idx.step or 1
        if step > 0:
            start = idx.start or 0
            stop = idx.stop or self.nBits
        else:
            start = idx.start or self.nBits - 1
            stop = idx.stop or -1
        if start < 0:
            start += self.nBits
        if stop < 0:
            stop += self.nBits
        return Bits(self, *range(start, stop, step))
    else:
        if idx < 0:
            idx += self.nBits
        return Bit(self, idx)


Bit.__add__ = Bit___add__
Bit.asBits = Bit_asBits

BitsSystem.getBit = BitsSystem_getBit
BitsSystem.getBits = BitsSystem_getBits
BitsSystem.__getitem__ = BitsSystem___getitem__
