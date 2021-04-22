# -*- coding: utf-8 -*-

"""用于控制库的一些默认行为

see more: `help(Options)` or `help(TemporaryOptions)`
"""

from typing import Any


__all__ = ["Options", "TemporaryOptions", "TempOption"]


class _options:
    """不应该由用户实例化这个对象

    Attributes:
        autoNormalize: 自动在作用位门后归一化系统 [default: True]
        allowTracking: 跟踪量子位系统的每一个操作 [default: False]
        littleEndian: 小端模式 [default: False]
        QFTwithNumpy: 使用numpy而不是位门实现QFT [default: True]
        checkCleaningSystem: 清除系统时检查系统是否已被重置 [default: True]
        QFTswap: 默认QFT在末端有SWAP操作, 但有些操作不需要SWAP [default: True]
        inputCheck: 对位门输入进行检查, 避免造成错误的逻辑结果 [default: True]

    To use: (littleEndian)
    >>> qbsys = QubitsSystem(2)
    >>> H(qbsys[0])
    >>> qbsys.states
    array([[0.70710678+0.j],
       [0.        +0.j],
       [0.70710678+0.j],
       [0.        +0.j]])
    >>> Options.reverseBitIndex = True
    array([[0.70710678+0.j],
       [0.70710678+0.j],
       [0.        +0.j],
       [0.        +0.j]])
    """
    def __init__(self) -> None:
        self.autoNormalize = True
        self.allowTracking = False
        self.littleEndian = False
        self.QFTwithNumpy = True
        self.checkCleaningSystem = True
        self.QFTswap = True
        self.inputCheck = True


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
    def littleEndian(after: bool) -> TempOption:
        return TempOption("littleEndian", after)

    @staticmethod
    def QFTwithNumpy(after: bool) -> TempOption:
        return TempOption("QFTwithNumpy", after)

    @staticmethod
    def checkCleaningSystem(after: bool) -> TempOption:
        return TempOption("checkCleaningSystem", after)

    @staticmethod
    def QFTswap(after: bool) -> TempOption:
        return TempOption("QFTswap", after)

    @staticmethod
    def inputCheck(after: bool) -> TempOption:
        return TempOption("inputCheck", after)
