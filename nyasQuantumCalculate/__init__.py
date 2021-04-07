# -*- coding: utf-8 -*-

from typing import List, Literal, Tuple

from .Operate import *
from .System import *
from .Options import *


def Probability(qb: Qubit) -> Tuple[float, float]:
    """获得量子位的测量出0和1的概率

    Args:
        qb: 单个量子位

    Returns:
        第0个元素为测量得到0的概率, 第1个元素为得到1的概率"""
    return qb.system.probability(qb.index)


def Measure(qb: Qubit) -> Literal[0, 1]:
    """测量量子位*

    Args:
        qb: 单个量子位

    Returns:
        当测量到0时返回0, 否则返回1."""
    return qb.system.measure(qb.index)


def Reset(qb: Qubit) -> None:
    """重置量子位

    注意量子位只能重置振幅而不能重置相位, 如果可能的话
    请使用位门偏转相位再重置量子位.

    Args:
        qb: 单个量子位"""
    qb.system.reset(qb.index)


def MeasureAll(qbs: Qubits) -> List[Literal[0, 1]]:
    """测量多个量子位

    测量qbs里所有量子位并返回结果列表

    Args:
        qbs: 需要测量的多个量子位

    Returns:
        测量结果的列表"""
    result: List[Literal[0, 1]] = list()
    for index in qbs.indexes:
        result.append(qbs.system.measure(index))
    return result


def ResetAll(qbs: Qubits) -> None:
    """重置多个量子位

    注意量子位只能重置振幅而不能重置相位, 如果可能的话
    请使用位门偏转相位再重置量子位.

    Args:
        qbs: 需要重置的多个量子位"""
    for index in qbs.indexes:
        qbs.system.reset(index)
