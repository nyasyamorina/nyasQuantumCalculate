# -*- coding: utf-8 -*-

"""一些库内大量使用的方法和小工具

这个包不会被显式引用

delta: 控制浮点数比较精度 [default: 1e-8]
ColorWeel2RGB()
TimeChunck
"""

from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple, Union
from time import time

import numpy as np


__all__ = ["equal0", "sss", "delta", "ColorWheel2RGB", "TimeChunck",
           "Bools2Int", "Int2Bools", "pi"]


pi = np.pi

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
    h_pi_3 = 3. * theta / pi
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


def Bools2Int(bools: Iterable[Union[Literal[0, 1], bool]]) -> int:
    """把bit列表转为int

    Args:
        l: 可迭代的对象, 内部元素为bool或0,1

    Returns:
        把列表l的第1个元素作为整数的高位, 逐位排列组成的整数"""
    res = 0
    for ele in bools:
        res <<= 1
        res |= int(ele)
    return res


def Int2Bools(x: int, n: Optional[int] = None) -> List[bool]:
    """把int转为bit列表

    Args:
        x: 需要转化的整数, 必须大于等于0
        n: 输出列表的长度, 默认为可以表示x的最短长度

    Returns:
        bool列表, 第1个为x的高位"""
    if x < 0:
        raise ValueError("负数不能转化为bools")
    if n is None:
        res: List[bool] = list()
        while x > 0:
            res.append(x & 1 == 1)
            x >>= 1
    else:
        res: List[bool] = [False] * n
        for i in range(n):
            if x <= 0:
                break
            res[i] = x & 1 == 1
            x >>= 1
    return res[::-1]


def FlipBools(bools: Iterable[Union[Literal[0, 1], bool]]) -> List[bool]:
    """翻转列表里的所有布尔值

    Args:
        l: 可迭代对象, 内部元素为bool或0,1

    Returns:
        翻转布尔值后的数组"""
    return [not bool(ele) for ele in bools]
