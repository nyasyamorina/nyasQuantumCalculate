# -*- coding: utf-8 -*-

from typing import Iterable

from .SingleQubitGate import *
from nyasQuantumCalculate.Utils import *
from nyasQuantumCalculate.System import *


__all__ = ["ApplyToEach", "ApplyFromBools", "ApplyFromInt"]


def ApplyToEach(gate: SingleQubitGate, qbs: Qubits) -> None:
    """把单量子位门作用到qbs的每个量子位上"""
    for qb in qbs:
        gate(qb)


def ApplyFromBools(gate: SingleQubitGate, bools: Iterable[bool],
                   qbs: Qubits, flip: bool = False) -> None:
    """使用bool控制单量子位门

    当flip为False, 把位门作用到bools里为True的相应索引的量子位上, 如果
    flip为True, 则对应False. bools和qbs长度不同时取最短.

    Args:
        gate: 需要作用的单量子位门
        bools: bool列表
        qbs: 多个量子位
        flip: 是否翻转bools"""
    for b, qb in zip(bools, qbs):
        if b ^ flip:
            gate(qb)


def ApplyFromInt(gate: SingleQubitGate, integer: int,
                 qbs: Qubits, reverse: bool = False) -> None:
    """使用int控制单量子位门

    如同`ApplyFromBools`差不多, 但bool列表从integer里推导, 且flip为False.
    默认在qbs第1个量子位对应integer高位, 最后1个量子位对应低位.
    设置reverse为True可以翻转顺序.

    Args:
        gate: 需要作用的单量子位门
        integer: 控制用的整数
        qbs: 多个量子位
        reverse: 是否翻转integer序列"""
    bits = Int2Bools(integer, len(qbs))
    ApplyFromBools(gate, bits[::-1] if reverse else bits, qbs, False)
