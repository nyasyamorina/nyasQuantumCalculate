# nyasQuantumCalculate
一个简单的量子计算模拟库
```python
from nyasQuantumCalculate import *

qbsys = QubitsSystem(1)
qubit = qbsys[0]
H(qubit)
result = Measure(qubit)
print(result)               # 0 or 1
```

---

## 安装

1.  下载这个仓库
2.  运行`python setup.py install`
3.  试着运行`examples/`里的例子

---

## 使用

1.  量子位系统

    *   使用 `QubitsSystem(int)` 初始化量子位系统

2.  量子位

    *   常用的量子位类型有 `Qubit` 和 `Qubits`
    *   可以通过 `qbsys.getQubit(int)` int和 `qbsys.getQubit(int, ...)` 获得量子位, 其中`qbsys`是`QubitsSystem`实例
    *   当然也可以通过 `qbsys` 的索引方法获得

3.  量子位门

    *   常用的量子位门 `I`, `H`, `X`, `Y`, `Z`, `S`, `T`, `SReverse`, `TReverse`, `CNOT`, `CCNOT`
    *   使用 `Rx(float)`, `Ry(float)`, `Rz(float)`, `R1(float)` 可以获取旋转门
    *   量子位门通过 `__call__` 方法作用在量子位上, 如: `X(qb)`
    *   或使用方法 `ApplyToAll` 把单量子位们作用在 `Qubits` 里每个量子位上
    *   提供了 `Control` 方法, 实现可控过程

3.  测量系统

    *   可以使用方法 `Measure` 测量`Qubit`, 并返回测量结果 (`0` 或 `1`)
    *   或使用方法 `MeasureAll` 测量`Qubits`, 并返回包含测量结果的列表

4.  重置系统

    *   使用方法 `Reset` 重置`Qubit`, 方法 `ResetAll` 重置`Qubits`
    *   可以直接使用语句 `ResetAll(qbsys.getQubits())` 重置整个系统
    *   退出程序或释放`QubitsSystem`实例前重置整个系统是好习惯

---

## FAQ

*   这个库有前置库吗

    需要 `numpy` 来执行底层运算. 推荐安装 `matplotlib` 来使用比较美观的量子系统可视化方法 `DumpMachineFig`

*   为什么不把库放到`pypi`上呢

    目前这个库还只是半成品. 并且pypi上可以安装qsharp等更好的库, ~~不想继续增加pip里面的垃圾了~~.

*   内置的方法好少, 使用好困难

    目前这个库还是第一个版本, 仅仅确保了*可运行*, 日后会增加更多功能, 比如多量子位门, QFT等

*   我可以跟别人分享这个库吗, 有什么限制

    莫得限制, 随便来就好, 最好可以标注一下作者啦

---

## 0.1.0

完全从`Cython`迁移到 `prue Python`+`numpy`, 使得代码结构具有层次, 容易修改和添加

但这无疑牺牲了运行速度, 比如说, 自制测试用的[Grover算法](https://en.wikipedia.org/wiki/Grover%27s_algorithm), 在10qubits(加上临时量子位共16qubits)用时`~2.4s`.

---

### 联系方式

qq群 ~~瑟图群~~ : 274767696

作者: **nyasyamorina** *[qq: 1275935966]* (加好友时请备注来意, 免得当作机器人了)


特别感谢 **_hyl** 提供 `pyi` 文件的翻译, _hyl: `"如果发现翻译有错的话, 可以去找我商讨"` *[qq: 2738846947]*  ~~[至版本0.0.1]~~

还有非常感激广大群友提供技术支持
