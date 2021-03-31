# -*- coding: utf-8 -*-

import numpy as np

from nyasQuantumCalculate.Utils import *
from .QubitsSystem import *

have_matplotlib: bool = True
try:
    from matplotlib import pyplot as plt
except ModuleNotFoundError:
    have_matplotlib = False


__all__ = ["DumpSystemText", "DumpSystemFig", "have_matplotlib"]


log10_2: float = np.log10(2.)


def DumpSystemText(sys: QubitsSystem) -> None:
    """以字符串形式打印系统所有状态

    Args:
        sys: 需要查看的系统"""
    print(f"# states in {sys.nQubits} qubits system")
    index_length = 1 + int(sys.nQubits * log10_2)
    format_str = '{' + f":0{index_length}" + '}'
    length = 21 - index_length
    for index, state in enumerate(sys.states[:, 0]):
        prob = np.square(np.abs(state))
        angle = np.angle(state)
        bar_length = int((prob + 1e-8) * length)
        print('∣' + format_str.format(index) + '❭', end="  ")
        Simag = np.abs(state.imag)
        if state.imag >= 0.:
            print(f"[{state.real: .4f} + {Simag:.4f}i]", end="  ")
        else:
            print(f"[{state.real: .4f} - {Simag:.4f}i]", end="  ")
        print(f"| {'='*bar_length}{' '*(length-bar_length)} |", end="  ")
        print(f"[prob: {prob:.4f}] [rad:{angle: .4f}]")
    print()


def DumpSystemFig(sys: QubitsSystem, block: bool = True) -> None:
    """以字符串形式打印系统所有状态

    使用前请确保已安装 matplotlib

    Args:
        sys: 需要查看的系统"""
    if not have_matplotlib:
        raise ModuleNotFoundError("No module named 'matplotlib'")
    states = sys.states[:, 0]
    prob = np.square(np.abs(states))
    angle = np.angle(states)
    index_length = 1 + int(sys.nQubits * log10_2)
    format_str = "∣{" + f":0{index_length}" + "}❭"
    lable_range = range(0, len(states), max(len(states) >> 5, 1))
    lables = [format_str.format(i) for i in lable_range]
    color = ["#{:02X}{:02X}{:02x}".format(*ColorWheel2RGB(theta))
             for theta in angle]
    lw = 0.75 if len(states) < 128 else 0.0
    plt.clf()
    plt.xticks(lable_range, lables, size=6,
               rotation="vertical", fontfamily="monospace")
    plt.ylim(0., 1.1)
    plt.ylabel("Probability")
    plt.bar(range(len(states)), prob, color=color, ec="#000000", ls='-', lw=lw)
    plt.show(block=block)


# TODO def DumpRegisterText(qbs: Qubits) -> None:
# TODO def DumpRegisterFig(qbs: Qubits, block: bool = True) -> None:
