# -*- coding: utf-8 -*-

from typing import List, Literal, Tuple

from .System import *
from .Operate import *


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


def SWAP(q0: Qubit, q1: Qubit) -> None:
    """交换量子位数据

    量子数据可以移动但不可复制, 这里是直接交换两个量子位的数据. 两个
    量子位必须处于相同的量子位系统.

    Args"""
    if q0.system.id != q1.system.id:
        raise ValueError("两个量子位处于不同的量子位系统")
    q0.system.swap(q0.index, q1.index)
