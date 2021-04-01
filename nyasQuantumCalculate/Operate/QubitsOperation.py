# -*- coding: utf-8 -*-

from typing import Any, Type, TypeVar

from nyasQuantumCalculate.System import *


__all__ = ["QubitsOperation", "OperationLike"]


OperationLike = TypeVar("OperationLike",
                        "QubitsOperation", Type["QubitsOperation"])


class QubitsOperation:
    """QubitsOperation(str, bool)

    用来标记量子位过程, 暂时没有什么用处.

    Attributes:
        name: 量子位过程的名字
        controllable: 过程是否可控
        trackable:
            过程是否可跟踪, 当为True时, 跟踪过程"应该"覆盖掉底层操作, 当这个特性
            需要暂时由用户自己提供, 参考`QubitsSystem.stopTracking`,
            `canTrack()`,`addTrack()`

    推荐编写量子位过程的写法:
        class MyOperation(QubitsOperation):
            def __init__(self):
                super().__init__()
                self.name = "自定义过程的名字"
                # self.controllable = ...
                self.trackable = True       # 用于化简跟踪信息

            def call(self, qbs: Qubits, qb: Qubit) -> None:
                # 这个方法记述量子过程的运算
                # 一般量子过程都是不返回值的
                ...

            def __call__(self, qbs: Qubits, qb: Qubit) -> None:
                # 这个方法用于控制过程的跟踪和系统判断等
                if qbs.system.id != qb.system.id:
                    # 判断输入量子位是否在同一个系统内
                    raise ValueError(...)
                qbsys = qbs.system      # 从输入参数里获得量子位系统
                sysStopTrack = qbsys.stopTracking   # 用于在退出方法时还原
                if qbsys.canTrack() and self.trackable:
                    qbsys.addTrack(...)             # 添加跟踪条目
                    qbsys.stopTracking = True       # 停止跟踪
                self.call(qbs, qb)      # 作用过程
                if not sysStopTrack:
                    # 还原系统原本的状态
                    qbsys.stopTracking = False
    """
    def __init__(self, name: str = "",
                 controllable: bool = False,
                 trackable: bool = False,
                 **kwargs: Any) -> None:
        self.name = name
        self.controllable = controllable
        self.trackable = trackable

    @staticmethod
    def getOperation(opr: OperationLike) -> "QubitsOperation":
        return opr() if isinstance(opr, type) else opr

    #def call(self, ...) -> ...: ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
