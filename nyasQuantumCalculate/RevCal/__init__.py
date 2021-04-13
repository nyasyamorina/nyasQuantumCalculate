# -*- coding: utf-8 -*-

from .Operate import *
from .System import *
from . import Builtin


__all__ = ["BitsSystem", "Bit", "Bits", "TemporaryBit", "TemporaryBits",
           "BitsOperation", "Controlled", "ControlledOnBools", "ControlledOnInt",
           "ApplyToEach", "ApplyFromBools", "ApplyFromInt", "Toffoli",
           "Builtin"]


"""
强行模拟电子计算机的可逆逻辑计算. 没有相位, 叠加态, 纠缠等量子特性, 只有0和1.
这个库用于以少内存开销验证逻辑电路的正确性. 见 `examples/others/Adder.py`

这部分大部分方法是从 nyasQuantumCalculate 复制粘贴过来的, 并不能完全保证正常工作.
"""
