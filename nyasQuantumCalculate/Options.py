# -*- coding: utf-8 -*-

"""用于控制库的一些默认行为

这个包不会被显式引用

see more: `help(Options)` or `help(TemporaryOptions)`
"""

from typing import Any


__all__ = ["Options", "TemporaryOptions", "TempOption"]


class _options:
    """不应该由用户实例化这个对象

    Attributes:
        autoNormalize: 自动在作用位门后归一化系统 [default: True]
        allowTracking: 跟踪量子位系统的每一个操作 [default: False]
        reverseBitIndex: 翻转位索引, True时为从右到左 [default: True]
        QFTwithNumpy: 使用numpy而不是位门实现QFT [default: True]
        checkCleaningSystem: 清除系统时检查系统是否已被重置 [default: True]

    To use: (reverseBitIndex)
    >>> qbsys = QubitsSystem(2)
    >>> H(qbsys[0])
    >>> qbsys.states
    array([[0.70710678+0.j],
       [0.70710678+0.j],
       [0.        +0.j],
       [0.        +0.j]])
    >>> Options.reverseBitIndex = False
    array([[0.70710678+0.j],
       [0.        +0.j],
       [0.70710678+0.j],
       [0.        +0.j]])
    """
    def __init__(self) -> None:
        self.autoNormalize = True
        self.allowTracking = False
        self.reverseBitIndex = True
        self.QFTwithNumpy = True
        self.checkCleaningSystem = True


Options = _options()


class TempOption:
    """see more: help(TemporaryOptions)"""
    def __init__(self, option: str, after: bool) -> None:
        Options.__getattribute__(option)
        self.option = option
        self._after = after
        self._before = False

    def __enter__(self) -> None:
        self._before = Options.__getattribute__(self.option)
        Options.__setattr__(self.option, self._after)

    def __exit__(self, *error: Any) -> None:
        Options.__setattr__(self.option, self._before)


class TemporaryOptions:
    """不应该由用户实例化这个对象

    配合with语句在代码块中临时把设置改为特定值

    To use:
    >>> Options.autoNormalize
    True
    >>> with TemporaryOptions.autoNormalize(False):
    ...     print(Options.autoNormalize)
    ...
    False
    >>> Options.autoNormalize
    True
    """
    @staticmethod
    def autoNormalize(after: bool) -> TempOption:
        return TempOption("autoNormalize", after)

    @staticmethod
    def allowTracking(after: bool) -> TempOption:
        return TempOption("allowTracking", after)

    @staticmethod
    def reverseBitIndex(after: bool) -> TempOption:
        return TempOption("reverseBitIndex", after)

    @staticmethod
    def QFTwithNumpy(after: bool) -> TempOption:
        return TempOption("QFTwithNumpy", after)

    @staticmethod
    def checkCleaningSystem(after: bool) -> TempOption:
        return TempOption("checkCleaningSystem", after)
