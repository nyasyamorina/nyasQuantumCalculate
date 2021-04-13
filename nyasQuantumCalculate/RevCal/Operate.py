# -*- coding: utf-8 -*-

from typing import Any, Iterable, List, TypeVar

from .System import *
from nyasQuantumCalculate.Utils import Int2Bools


__all__ = ["BitsOperation", "Controlled", "ControlledOnBools", "ControlledOnInt",
           "ApplyToEach", "ApplyFromBools", "ApplyFromInt", "Toffoli",
           "M", "MA", "R", "RA", "I", "X", "CNOT", "CCNOT", "SWAP"]


class BitsOperation:
    def __init__(self, name: str = "",
                 controllable: bool = False,
                 trackable: bool = False,
                 **kwargs: Any) -> None:
        self.name = name
        self.controllable = controllable
        self.trackable = trackable

    # def call(self, ...) -> ...: ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


###############################################################################
###############################################################################


class _I(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "I"
        self.controllable = True
        self.trackable = False

    def call(self, b: Bit) -> None:
        pass

    def __call__(self, b: Bit) -> None:
        bsys = b.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b.index)
            bsys.stopTracking = True
        self.call(b)
        if not sysStopTrack:
            bsys.stopTracking = False


class _X(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "X"
        self.controllable = True
        self.trackable = True

    def call(self, b: Bit) -> None:
        b.system.states[b.index] = not b.system.states[b.index]

    def __call__(self, b: Bit) -> None:
        bsys = b.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b.index)
            bsys.stopTracking = True
        self.call(b)
        if not sysStopTrack:
            bsys.stopTracking = False


I = _I()
X = _X()
SingleBitGate = TypeVar("SingleBitGate", _I, _X)


###############################################################################
###############################################################################


def Controlled(opr: BitsOperation, ctlBs: Bits,
               *args: Any, **kwargs: Any) -> Any:
    if not opr.controllable:
        raise ValueError("目标过程不是可控的")
    bsys = ctlBs.system
    bsys.addControllingBits(*ctlBs.indexes)
    if all(bsys.states[idx] for idx in bsys.ctlBits):
        opr(*args, **kwargs)
    bsys.popControllingBits()


def ControlledOnBools(opr: BitsOperation, bools: Iterable[bool], ctlBs: Bits,
                      *args: Any, **kwargs: Any) -> Any:
    for bit, b in zip(bools, ctlBs):
        if not bit:
            X(b)
    result = Controlled(opr, ctlBs, *args, **kwargs)
    for bit, b in zip(bools, ctlBs):
        if not bit:
            X(b)
    return result


def ControlledOnInt(opr: BitsOperation, integer: int, ctlBs: Bits,
                    *args: Any, **kwargs: Any) -> Any:
    bits = Int2Bools(integer, len(ctlBs))
    result = ControlledOnBools(opr, bits, ctlBs, *args, **kwargs)
    return result


class _CNOT(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "CNOT"
        self.controllable = True

    def call(self, b0: Bit, b1: Bit) -> None:
        Controlled(X, b0.asBits(), b1)

    def __call__(self, b0: Bit, b1: Bit) -> None:
        if b0.system.id != b1.system.id:
            raise ValueError("两个位处于不同的量子位系统")
        bsys = b0.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b0.index, b1.index)
            bsys.stopTracking = True
        self.call(b0, b1)
        if not sysStopTrack:
            bsys.stopTracking = False


class _CCNOT(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "CCNOT"
        self.controllable = True

    def call(self, b0: Bit, b1: Bit, b2: Bit) -> None:
        Controlled(X, b0 + b1, b2)

    def __call__(self, b0: Bit, b1: Bit, b2: Bit) -> None:
        if b0.system.id != b1.system.id or \
                b0.system.id != b2.system.id:
            raise ValueError("三个位处于不同的量子位系统")
        bsys = b0.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b0.index, b1.index, b2.index)
            bsys.stopTracking = True
        self.call(b0, b1, b2)
        if not sysStopTrack:
            bsys.stopTracking = False


###############################################################################
###############################################################################


def ApplyToEach(gate: SingleBitGate, bs: Bits) -> None:
    for b in bs:
        gate(b)


def ApplyFromBools(gate: SingleBitGate, bools: Iterable[bool],
                   bs: Bits) -> None:
    for bit, b in zip(bools, bs):
        if bit:
            gate(b)


def ApplyFromInt(gate: SingleBitGate, integer: int, bs: Bits) -> None:
    bits = Int2Bools(integer, len(bs))
    ApplyFromBools(gate, bits, bs)


###############################################################################
###############################################################################


class _SWAP(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "SWAP"
        self.trackable = True

    def call(self, b0: Bit, b1: Bit) -> None:
        bsys = b0.system
        tmp = bsys.states[b0.index]
        bsys.states[b0.index] = bsys.states[b1.index]
        bsys.states[b1.index] = tmp

    def __call__(self, b0: Bit, b1: Bit) -> None:
        if b0.system.id != b1.system.id:
            raise ValueError("两个位处于不同的量子位系统")
        bsys = b0.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b0.index, b1.index)
            bsys.stopTracking = True
        self.call(b0, b1)
        if not sysStopTrack:
            bsys.stopTracking = False


###############################################################################
###############################################################################


class _RESET(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "RESET"
        self.trackable = True

    def call(self, b: Bit) -> None:
        b.system.states[b.index] = False

    def __call__(self, b: Bit) -> None:
        bsys = b.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b.index)
            bsys.stopTracking = True
        self.call(b)
        if not sysStopTrack:
            bsys.stopTracking = False


class _RESETALL(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "RESETALL"
        self.trackable = True

    def call(self, bs: Bits) -> None:
        states = bs.system.states
        for index in bs.indexes:
            states[index] = False

    def __call__(self, bs: Bits) -> None:
        bsys = bs.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, *bs.indexes)
            bsys.stopTracking = True
        self.call(bs)
        if not sysStopTrack:
            bsys.stopTracking = False


###############################################################################
###############################################################################


class _MEASURE(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "MEASURE"
        self.trackable = True

    def call(self, b: Bit) -> bool:
        return b.system.states[b.index]

    def __call__(self, b: Bit) -> bool:
        bsys = b.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, b.index)
            bsys.stopTracking = True
        result = self.call(b)
        if not sysStopTrack:
            bsys.stopTracking = False
        return result


class _MEASUREALL(BitsOperation):
    def __init__(self) -> None:
        super().__init__()
        self.name = "MEASUREALL"
        self.trackable = True

    def call(self, bs: Bits) -> List[bool]:
        states = bs.system.states
        return [states[index] for index in bs.indexes]

    def __call__(self, bs: Bits) -> List[bool]:
        bsys = bs.system
        sysStopTrack = bsys.stopTracking
        if bsys.canTrack() and self.trackable:
            bsys.addTrack(self.name, *bs.indexes)
            bsys.stopTracking = True
        result = self.call(bs)
        if not sysStopTrack:
            bsys.stopTracking = False
        return result


###############################################################################
###############################################################################


M = _MEASURE()
MA = _MEASUREALL()

R = _RESET()
RA = _RESETALL()

CNOT = _CNOT()
CCNOT = _CCNOT()
Toffoli = CCNOT

SWAP = _SWAP()
