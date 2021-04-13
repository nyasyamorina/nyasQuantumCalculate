# -*- coding: utf-8 -*-

from typing import List, Tuple, Union, Any

import numpy as np

from nyasQuantumCalculate.Options import *
from nyasQuantumCalculate.Utils import *


__all__ = ["QubitsSystem"]


class id_manager:
    _last_id = -1

    @classmethod
    def getID(cls) -> int:
        cls._last_id += 1
        return cls._last_id


class QubitsSystem:
    """QubitsSystem(nQubits)

    用于储存和模拟量子位系统的类, 注意这个类不能被量子位过程(QubitsOperation)作用.

    退出程序或释放QubitsSystem实例前需要重置整个系统

    Attributes:
        stopTracking: 设置为False后, 就算allowTracking为True都不会继续跟踪操作.

    To use:
    >>> qbsys = QubitsSystem(2)
    >>> qbsys.id
    0
    >>> qbsys.nQubits
    2
    >>> qbsys.states
    array([[1.+0.j],
        [0.+0.j],
        [0.+0.j],
        [0.+0.j]])
    """

    def __init__(self, nQubits: int) -> None:
        self.statesNd = np.zeros([2] * nQubits, np.complex128)
        self.statesNd.__setitem__((*([0] * nQubits),), 1.)
        self._id = id_manager.getID()
        self._ctlBits: List[int] = list()
        self._ctlBitPkgs: List[List[int]] = list()
        self._qIndex = list(range(self.nQubits))
        self._qIndexR = list(range(self.nQubits))
        self._tracker: List[Tuple[Tuple[int, ...],
                                  Tuple[int, ...], str]] = list()
        self.stopTracking = False

    def __del__(self) -> None:
        print(f"Cleaning up qubits system with id:{self._id} ...")
        if Options.checkCleaningSystem and \
                not equal0(np.abs(
                    self.statesNd.__getitem__((*([0] * self.nQubits),))
                ) - 1.):
            raise RuntimeError("Before cleaning up qubits system, "
                               "all qubits in system should be reset.")

    @property
    def nQubits(self) -> int: return self.statesNd.ndim

    @property
    def nControllingQubits(self) -> int: return len(self._ctlBits)

    @property
    def id(self) -> int: return self._id

    @property
    def states(self) -> np.ndarray:
        # shape of states should be (2^n, 1) (column vector)
        indexes = self._qIndex[::-1] \
            if Options.reverseBitIndex else self._qIndex
        return self.statesNd. \
            transpose(indexes). \
            reshape([-1, 1])

    def __str__(self) -> str:
        return f"QubitsSystem({self.nQubits})"

    def __repr__(self) -> str:
        return f"QubitsSystem(nQubits:{self.nQubits},id:{self._id})"

    def __getitem__(self, idx: Union[int, slice]) -> Any:
        raise NotImplementedError

    def getQubit(self, idx: int) -> Any:
        """得到系统内的一个量子位

        Args:
            idx: 量子位的索引, 应该从0开始到nQubits-1

        Returns:
            (Qubit)可以被量子位过程作用的量子位"""
        raise NotImplementedError

    def getQubits(self, *idxs: int) -> Any:
        """得到系统内的多个量子位

        Args:
            idxs: 量子位的索引, 应该从0开始到nQubits-1

        Returns:
            (Qubit)可以被量子位过程作用的量子位"""
        raise NotImplementedError

    def normalize(self) -> None:
        """归一化系统"""
        self.statesNd /= np.sqrt(sss(self.statesNd))

    def getTracker(self):
        """返回系统内记录步骤的对象

        Returns:
            (List[Tuple[Tuple[int, ...], Tuple[int, ...], str]])
            列表内按顺序每项是系统经历的步骤. 步骤里第一项是控制位
            (如果不是控制位门则为空), 第二项是被控制位, 第三项是步骤的名字
            (由外部提供). 比如:

            [((), (0,), 'H'), ((0,), (1,), 'X'), ((), (1,), 'Z'),
             ((), (0, 1), 'SWAP'), ((), (0,), 'MEASURE'), ((), (1,), 'MEASURE'),
             ((), (0,), 'RESET'), ((), (1,), 'RESET')]
            步骤: 先把H门作用在第0位, 然后把第0位设位控制位, 第1位设为被控制位, 作
            用CNOT, 把Z门作用在第1位, 交换第0位和第1位, 测量第0和第1位, 重置第0和
            第1位"""
        return self._tracker

    def restart(self) -> None:
        self.statesNd *= 0.
        self.statesNd.__setitem__((*([0] * self.nQubits),), 1.)
        self._ctlBits.clear()
        self._ctlBitPkgs.clear()
        self._qIndex = list(range(self.nQubits))
        self._qIndexR = list(range(self.nQubits))
        self._tracker.clear()
        self.stopTracking = False

    # TODO def isEntangled(self, idx: int) -> bool:

    ##########################  Related to tracking  ##########################

    def canTrack(self) -> bool:
        """系统是否可以跟踪量子位操作

        把属性stopTracking可以停止系统里的跟踪

        Returns:
            返回当前系统是否可以跟踪"""
        return Options.allowTracking and not self.stopTracking

    def addTrack(self, name: str, *idxs: int) -> None:
        """添加跟踪条目

        调用此方法会无视任何条件, 给跟踪器加上条目. 正常使用应该要
        先使用`canTrack()`判断是否可以跟踪再进行添加.

        Args:
            name: 操作的名字
            idxs: 被控制位 或 操作的作用位"""
        self._tracker.append((tuple(self._ctlBits), tuple(idxs), name))

    ###########################################################################
    ################## * 一般情况下, 你不应该调用以下方法  #######################
    ###########################################################################

    ####################  Related to controlling qubits  ######################

    def checkQuickIndexCorrect(self) -> bool:
        """检查内部快速索引是否正常

        没有实际用途, 只在 DEBUG 时会用上."""
        if len(self._qIndex) != self.statesNd.ndim:
            return False
        if len(self._qIndex) != len(self._qIndexR):
            return False
        if not all(idx0 == idx1
                   for idx0, idx1 in
                   zip(self._ctlBits, self._qIndexR[-len(self._ctlBits):])):
            return False
        for (idx0, idxx0), (idx1, idxx1) in zip(
            enumerate(self._qIndex),
            enumerate(self._qIndexR)
        ):
            if self._qIndex[idxx1] != idx1:
                return False
            if self._qIndexR[idxx0] != idx0:
                return False
        return True

    def statesNdIndex(self, idx: int, reverse: bool = False) -> int:
        """内部数组的索引

        当存在控制位时, 内部数组的索引与量子位索引不一致, 这个
        方法是用于得到正确的索引的. 无论在什么时候都没必要调用这个方法

        Args:
            idx: 量子位的索引, 应该从0开始到nQubits-1.
            reverse: 当为True, 从数组索引得到量子位索引

        Returns:
            索引"""
        if not 0 <= idx < self.nQubits:
            raise ValueError(f"索引为 {idx} 的量子位不存在")
        if not self._ctlBits:
            return idx
        if reverse:
            return self._qIndexR[idx]
        return self._qIndex[idx]

    def addControllingQubits(self, *idxs: int) -> None:
        """增加一组控制位*

        用于多重控制的情况, 新增控制位不可以与已有控制位相同, 使用
        popControllingQubiys()来取消控制位.

        *请使用 `Controlled(opr, ctlQbs, ...)` 来控制过程

        Args:
            idxs: 量子位的索引, 应该从0开始到nQubits-1"""
        if not idxs:
            return
        if any(idx in self._ctlBits for idx in idxs):
            raise ValueError("控制位被重复添加")
        self._ctlBitPkgs.append(list(idxs))
        self.updateControllingQubits()

    def popControllingQubits(self) -> None:
        """删除一组控制位

        删除最近添加的一组控制位"""
        if not self._ctlBitPkgs:
            return
        self._ctlBitPkgs.pop()
        self.updateControllingQubits()

    def updateQuickIndex(self) -> None:
        """更新快速索引

        使用_ctlBits更新_qIndex和_qIndexR"""
        if not self._ctlBitPkgs:
            self._qIndex = list(range(self.nQubits))
            self._qIndexR = list(range(self.nQubits))
            return
        self._qIndexR = [index for index in range(self.nQubits)
                         if index not in self._ctlBits]
        self._qIndexR += self._ctlBits
        if len(self._qIndex) != self.nQubits:
            self._qIndex = list(range(self.nQubits))
        for index0, index1 in enumerate(self._qIndexR):
            self._qIndex[index1] = index0

    def updateControllingQubits(self) -> None:
        """更新控制位

        使用_ctlBitPkgs来更新_ctlBits"""
        if self._ctlBits:
            self.statesNd = self.statesNd.transpose(self._qIndex)
        self._ctlBits.clear()
        if not self._ctlBitPkgs:
            self.updateQuickIndex()
            return
        for pkg in self._ctlBitPkgs:
            self._ctlBits += pkg
        self._ctlBits.sort()
        self.updateQuickIndex()
        self.statesNd = self.statesNd.transpose(self._qIndexR)

    #####################  Related to temporary qubit  ########################

    def addQubits(self, nQubits: int) -> None:
        """增加量子位*

        在系统里增加nQubits个量子位, 并分配在其他量子位末端.

        *请使用 `TemporaryQubit` 或 `TemporaryQubits` 分配临时量子位

        Args:
            nQubits: 新增量子位的数量"""
        if nQubits <= 0:
            raise ValueError(f"Cannot add {nQubits} qubits.")
        if self._ctlBits:
            self.statesNd = self.statesNd.transpose(self._qIndex)
        new_states = np.zeros([2] * (self.nQubits + nQubits), np.complex128)
        new_states.__setitem__((..., *([0] * nQubits)), self.statesNd)
        self.statesNd = new_states
        self.updateQuickIndex()
        if self._ctlBits:
            self.statesNd = self.statesNd.transpose(self._qIndexR)

    def popQubits(self, nQubits: int) -> None:
        """移除量子位

        移除系统末端的nQubits个量子位, 量子位在被移除前需要被重置, 并且确保
        被移除的量子位不是控制位

        Args:
            nQubits: 移除量子位的数量"""
        if nQubits <= 0:
            raise ValueError(f"Cannot pop {nQubits} qubits.")
        if any(idx >= self.nQubits - nQubits for idx in self._ctlBits):
            raise ValueError("被移除的量子位是控制位")
        if self._ctlBits:
            self.statesNd = self.statesNd.transpose(self._qIndex)
        states = self.statesNd.__getitem__((..., *([0] * nQubits)))
        if not equal0(sss(states) - 1.):
            if self._ctlBits:
                self.statesNd = self.statesNd.transpose(self._qIndexR)
            raise RuntimeError("被移除的量子位未重置")
        self.statesNd = states.copy()
        self.updateQuickIndex()
        if self._ctlBits:
            self.statesNd = self.statesNd.transpose(self._qIndexR)
