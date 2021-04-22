# -*- coding: utf-8 -*-

from typing import Union as _U, List as _L

from .Dump import *
from .Qubits import *
from .Qubit import *
from .QubitsSystem import *


def inSameSystem(*args: _U[Qubit, Qubits, QubitsSystem]) -> bool:
    """检查输入是否处于同一个量子位系统内"""
    ele0 = args[0]
    id = (ele0 if isinstance(ele0, QubitsSystem) else ele0.system).id
    for ele in args[1:]:
        if (ele if isinstance(ele, QubitsSystem) else ele.system).id != id:
            return False
    return True


def isControllingQubits(*args: _U[Qubit, Qubits]) -> _L[bool]:
    """检查输入量子位是否为控制位 (这个方法不会检查是否为同一个系统)"""
    res: _L[bool] = list()
    qbsys = args[0].system
    for ele in args:
        if isinstance(ele, Qubit):
            res.append(qbsys.isControlling(ele.index))
            continue
        res += [qbsys.isControlling(index) for index in ele.indexes]
    return res


def haveSameQubit(*args: _U[Qubit, Qubits]) -> bool:
    tmp: _L[int] = list()
    for ele in args:
        if isinstance(ele, Qubit):
            index = ele.index
            if index in tmp:
                return True
            tmp.append(index)
            continue
        if any(index in tmp for index in ele.indexes) or ele.haveSameQubit():
            return True
        tmp += ele.indexes
    return False
