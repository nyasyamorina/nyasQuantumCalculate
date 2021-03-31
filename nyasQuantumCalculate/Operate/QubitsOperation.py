# -*- coding: utf-8 -*-

from typing import Any, Type, TypeVar

from nyasQuantumCalculate.System import *


__all__ = ["QubitsOperation", "OperationLike"]


OperationLike = TypeVar("OperationLike",
                        "QubitsOperation", Type["QubitsOperation"])


class QubitsOperation:
    """QubitsOperation(str, bool)

    用来标记量子位过程, 暂时没有什么用处

    Attributes:
        name: 量子位过程的名字
        controllable: 过程是否可控"""
    def __init__(self, name: str = "",
                 controllable: bool = False,
                 **kwargs: Any) -> None:
        self.name = name
        self.controllable = controllable

    @staticmethod
    def getOperation(opr: OperationLike) -> "QubitsOperation":
        return opr() if isinstance(opr, type) else opr

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass
