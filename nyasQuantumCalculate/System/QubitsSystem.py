# -*- coding: utf-8 -*-

from typing import List, Literal, Tuple, Union, Any

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
        self._qIndex = list(range(self.nQubits))
        self._qIndexR = list(range(self.nQubits))
        self._tracker: List[Tuple[Tuple[int, ...],
                                  Tuple[int, ...], str]] = list()

    def __del__(self) -> None:
        print(f"Cleaning up qubits system with id:{self._id} ...")
        get_state = False
        for stateL in np.abs(self.statesNd.flat):
            if not equal0(stateL):
                if get_state:
                    raise RuntimeError("Before cleaning up qubits system, "
                                       "system should be reset.")
                get_state = True

    @property
    def nQubits(self) -> int: return self.statesNd.ndim

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

    # TODO def isEntangled(self, idx: int) -> bool:

    ###########################################################################
    ################## * 一般情况下, 你不应该调用以下方法  #######################
    ###########################################################################

    def reset(self, idx: int) -> None:
        """重置一个量子位*

        注意量子位只能重置振幅而不能重置相位, 如果可能的话
        请使用位门偏转相位再重置量子位.

        *请使用 `Reset(qb)` 或 `ResetAll(qbs)` 来重置量子位.

        Args:
            idx: 量子位的索引, 应该从0开始到nQubits-1"""
        states = self.statesNd.swapaxes(0, self.statesNdIndex(idx))
        prob0 = sss(states[0, ...])
        if equal0(prob0):
            states[0, ...] = states[1, ...]
        states[0, ...] /= np.sqrt(sss(states[0, ...]))
        states[1, ...] *= 0.
        if Options.allowTracking:
            self._tracker.append(((), (idx,), "RESET"))

    def swap(self, idx0: int, idx1: int) -> None:
        """交换两个量子位*

        *请使用 `SWAP(qb0, qb1)` 来交换量子位.

        Args:
            idx0: 量子位的索引, 应该从0开始到nQubits-1
            idx1: 量子位的索引, 应该从0开始到nQubits-1"""
        self.statesNd = self.statesNd.swapaxes(
            self.statesNdIndex(idx0),
            self.statesNdIndex(idx1)
        )
        if Options.allowTracking:
            self._tracker.append(((), (idx0, idx1), "SWAP"))

    def apply(self, m: np.ndarray, idx: int, name: str = "") -> None:
        """把单量子位门应用到量子位上*

        当self.controlBits存在时, 位门变为控制位门. 并且
        被应用位门的量子位不能是被控制位.

        *请使用 `U(qb)` 来应用位门, U为单量子位门.

        Args:
            m: 2x2复矩阵
            idx: 量子位的索引, 应该从0开始到nQubits-1
            name: 位门的名字, 用于记录步骤
        """
        if m.shape != (2, 2):
            raise ValueError(f"m的形状应该为(2,2), 而不是{m.shape}.")
        if idx in self._ctlBits:
            raise ValueError("被作用门作用的Qubit不能是控制位.")
        states = self.statesNd.swapaxes(0, self.statesNdIndex(idx))
        old_states = states.copy()
        # python 3.10 以上不再支持在索引里解包了
        controlling0 = (0, ..., *([1] * len(self._ctlBits)))
        controlling1 = (1, ..., *([1] * len(self._ctlBits)))
        states.__setitem__(controlling0,
                           m[0, 0] * old_states.__getitem__(controlling0) +
                           m[0, 1] * old_states.__getitem__(controlling1))
        states.__setitem__(controlling1,
                           m[1, 0] * old_states.__getitem__(controlling0) +
                           m[1, 1] * old_states.__getitem__(controlling1))
        if Options.autoNormalize:
            self.normalize()
        if Options.allowTracking:
            self._tracker.append((tuple(self._ctlBits), (idx,), name))

    #########################  Related to measuring  ##########################

    def probability(self, idx: int) -> Tuple[float, float]:
        """量子位被测量时得到0或1的概率*

        *请使用 `Probability(qb)` 来获得概率

        Args:
            idx: 量子位的索引, 应该从0开始到nQubits-1

        Returns:
            第0个元素为测量得到0的概率, 第1个元素为得到1的概率"""
        states = self.statesNd.swapaxes(0, self.statesNdIndex(idx))
        prob0 = sss(states[0, ...])
        prob1 = sss(states[1, ...])
        total = prob0 + prob1
        return (prob0 / total, prob1 / total)

    def measure(self, idx: int) -> Literal[0, 1]:
        """测量量子位*

        *请使用 `Measure(qb)` 或 `MeasureAll(qbs)` 来测量量子位.

        Args:
            idx: 量子位的索引, 应该从0开始到nQubits-1.

        Returns:
            当测量到0时返回0, 否则返回1."""
        states = self.statesNd.swapaxes(0, self.statesNdIndex(idx))
        prob0 = sss(states[0, ...])
        prob1 = sss(states[1, ...])
        choice = 0 if np.random.random() * (prob0 + prob1) <= prob0 else 1
        states[choice, ...] /= np.sqrt(sss(states[choice, ...]))
        states[1 - choice, ...] *= 0.
        if Options.allowTracking:
            self._tracker.append(((), (idx,), "MEASURE"))
        return choice

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

    def setControllingQubits(self, *idxs: int) -> None:
        """设置控制位*

        在设置控制位后, 作用在量子位上的位门全部会变为控制位门. 在
        设置控制位之前必须先移除之前的控制位

        *请使用 `Controlled(opr, ctlQbs, ...)` 来控制过程

        Args:
            idxs: 量子位的索引, 应该从0开始到nQubits-1"""
        if self._ctlBits:
            raise RuntimeError("Before setting control qubit, "
                               "previous ones should be removed.")
        if not all(0 <= index < self.nQubits for index in idxs):
            raise ValueError("输入参数内有超出范围的索引")
        if len(idxs) >= self.nQubits:
            raise ValueError("控制位太多了, 以至于无法执行位门操作")
        self._ctlBits = list(idxs)
        self._ctlBits.sort()
        self._qIndexR = [index for index in range(self.nQubits)
                         if index not in self._ctlBits]
        self._qIndexR += self._ctlBits
        for index0, index1 in enumerate(self._qIndexR):
            self._qIndex[index1] = index0
        self.statesNd = self.statesNd.transpose(self._qIndexR)

    def removeControllingQubits(self) -> None:
        """移除控制位"""
        if not self._ctlBits:
            return
        self.statesNd = self.statesNd.transpose(self._qIndex)
        self._qIndex = list(range(self.nQubits))
        self._qIndexR = list(range(self.nQubits))
        self._ctlBits = list()

    #####################  Related to temporary qubit  ########################

    def addQubit(self, nQubits: int = 1) -> None:
        """增加量子位*

        在系统里增加nQubits个量子位, 并分配在其他量子位末端.

        *请使用 `TemporaryQubit` 或 `TemporaryQubits` 分配临时量子位

        Args:
            nQubits: 新增量子位的数量"""
        isControlling = False
        controlBits: List[int] = list()
        if self._ctlBits:
            isControlling = True
            controlBits = self._ctlBits
            self.removeControllingQubits()
        new_states = np.zeros([2] * (self.nQubits + nQubits), np.complex128)
        new_states.__setitem__((..., *([0] * nQubits)), self.statesNd)
        extra_indexes = list(range(self.nQubits, self.nQubits + nQubits))
        self._qIndex += extra_indexes
        self._qIndexR += extra_indexes
        self.statesNd = new_states
        if isControlling:
            self.setControllingQubits(*controlBits)

    def popQubit(self, nQubits: int = 1) -> None:
        """移除量子位

        移除系统末端的nQubits个量子位, 量子位在被移除前会被重置

        Args:
            nQubits: 移除量子位的数量"""
        isControlling = False
        controlBits: List[int] = list()
        if self._ctlBits:
            isControlling = True
            controlBits = self._ctlBits
            self.removeControllingQubits()
        for index in range(self.nQubits - nQubits, self.nQubits):
            self.reset(index)
        self.statesNd = self.statesNd.__getitem__(
            (..., *([0] * nQubits))
        ).copy()
        self._qIndex = self._qIndex[:self.nQubits]
        self._qIndexR = self._qIndexR[:self.nQubits]
        if isControlling:
            self.setControllingQubits(*controlBits)
