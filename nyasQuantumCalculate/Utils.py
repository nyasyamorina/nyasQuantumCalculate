# -*- coding: utf-8 -*-

"""一些库内大量使用的方法和小工具

这个包不会被显式引用

delta: 控制浮点数比较精度 [default: 1e-8]
ColorWeel2RGB()
TimeChunck
"""

from typing import Any, Dict, List, Tuple, Union
from time import time

import numpy as np


__all__ = ["equal0", "sss", "delta", "ColorWheel2RGB", "TimeChunck"]


delta = 1e-8


def equal0(x: float) -> bool:
    return abs(x) <= delta


def sss(arr: np.ndarray) -> Any:
    return np.sum(np.square(np.abs(arr)))


def colorF(n: int, h: float) -> float:
    k = np.mod(n + h, 6.)
    if k <= 2:
        return np.clip(k, 0., 1.)
    return np.clip(4. - k, 0., 1.)


def ColorWheel2RGB(theta: float, get01: bool = False) -> \
        Union[Tuple[int, int, int], Tuple[float, float, float]]:
    """从色环上获取颜色

    输入色环角度可以获取RGB颜色, 0为红色, 2*pi/3为绿色, 4*pi/3为蓝色

    Args:
        theta: 色环角度
        get01: 如果为真, 返回[0.~1.]的浮点数, 否则为[0~255]的整数

    Return:
        返回包含RGB颜色的元组"""
    h_pi_3 = 3. * theta / np.pi
    red = colorF(2, h_pi_3)
    green = colorF(0, h_pi_3)
    blue = colorF(4, h_pi_3)
    if get01:
        return red, green, blue
    return int(red * 255.), int(green * 255.), int(blue * 255.)


totaltimer: Dict[str, List[Union[int, float]]] = dict()

class TimeChunck:
    """TimeChunk(str)

    配合with语句计算特定代码块调用的次数和总共运行时间

    To use:
    >>> for _ in range(15):
    ...     with TimeChunck("test"):
    ...         time.sleep(0.03)
    ...
    >>> TimeChunck.getAll()
    {'test': [15, 0.47789764404296875]}
    """
    def __init__(self, name: str):
        self.name = name
        self.start = 0.

    @staticmethod
    def getAll() -> Dict[str, List[Union[int, float]]]:
        """得到全部计时条目

        Returns:
            一个字典包含计时名词, 和调用次数与总共运行时间的列表"""
        return totaltimer

    def __enter__(self):
        if self.name not in totaltimer:
            totaltimer[self.name] = [0, 0.]
        self.start = time()

    def __exit__(self, _:Any, __: Any, ___: Any) -> None:
        totaltimer[self.name][0] += 1
        totaltimer[self.name][1] += time() - self.start
