# nyasQuantumCalculate
一个简单的量子计算模拟库
```python
from nyasQuantumCalculate import *

qbsys = QubitsSystem(1)
qubit = qbsys[0]
Builtin.H(qubit)
result = Builtin.M(qubit)
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

    *   `Builtin`里有常用的量子位门 `I`, `H`, `X`, `Y`, `Z`, `S`, `T`, `SR`, `TR`, `CNOT`, `CCNOT`
    *   使用 `Rx(float)`, `Ry(float)`, `Rz(float)`, `R1(float)`, `Phase(float)` 可以获取旋转门和相位门
    *   量子位门通过 `__call__` 方法作用在量子位上, 如: `X(qb)`
    *   或使用方法 `ApplyToAll` 把单量子位们作用在 `Qubits` 里每个量子位上
    *   提供了 `Controlled` 方法, 实现可控过程
    *   `QFT` 和 `IQFT` 如同位门一样直接作用在多量子位上

3.  测量系统

    *   可以使用方法 `Builtin.M` 测量`Qubit`, 并返回测量结果 (`False` 或 `True`)
    *   或使用方法 `Builtin.MA` 测量`Qubits`, 并返回包含测量结果的列表

4.  重置系统

    *   使用方法 `Builtin.R` 重置`Qubit`, 方法 `Builtin.RA` 重置`Qubits`
    *   可以直接使用语句 `Builtin.RA(qbsys.getQubits())` 重置整个系统
    *   退出程序或释放`QubitsSystem`实例前重置整个系统是好习惯

---

## FAQ

*   这个库有前置库吗

    需要 `numpy` 来执行底层运算. 推荐安装 `matplotlib` 来使用比较美观的量子系统可视化方法 `DumpMachineFig`

*   为什么不把库放到`pypi`上呢

    目前这个库还只是半成品. 并且pypi上可以安装qsharp等更好的库, ~~不想继续增加pip里面的垃圾了~~.

*   内置的方法好少, 使用好困难

    目前这个库还是测试版本, 日后会增加更多功能

*   为什么执行`QFT`和`IQFT`的时候使用内存翻了一倍

    使用`numpy`算法的`QFT`底部逻辑是重新构建一个系统状态`statesNd`, 请确保没有在其他地方引用`qbsys.stateNd`. 如果实在需要引用`statesNd`, 可以通过 `Options.QFTwithNumpy = False` 把`QFT`逻辑切换为位门实现, 在很多量子位(如20个以上)速度会受到严重影响.

*   我可以跟别人分享这个库吗, 有什么限制吗

    莫得限制, 随便来就好, 最好可以标注一下作者啦

---

### 0.1.1

减少了部分逻辑, 使某些功能更通用. 例如支持多重控制, 删除临时量子位前必须由用户重置而不是自动重置

增加了内部库 `Builtin`, 内置的位门,测量,重置等操作都以`常量`收录在里面, 而不是直接暴露在表层

增加了 `AQFT` 和 `IAQFT` 在`Builtin`里. See more: `help(Builtin.AQFT)`

重构了库之间的引用顺序, `Reset`, `Measure`, `ResetAll`, `MeasureAll` 已被 `Builtin.R`, `Builtin.RA`, `Builtin.M`, `Builtin.MA` 替代

新增内部库 `RevCal`, 模拟电子计算机的可逆计算. 大部分方法与量子计算相同, 内置`X`(可逆NOT门), `CNOT`(可逆XOR门), `CCNOT`(可逆AND门). 使用: 输入使用`ApplyFromInt(X, int, Bits)`, 输出使用 `Builtin.MA(Bits)`.

**不要同时引用 `nyasQuantumCalculate` 和 `nyasQuantumCalculate.RevCal`**

### 0.1.2

取消 **选项**`reverseBitIndex`, 增加 **选项**`littleEndian`. 现在 `ApplyFromInt`, `ControlledOnOnt`, `Bools2Int`, `Int2Bools` 和 `Dump` 方法都受 `littleEndian` 影响.

修复 `Qubit + Qubits` 的顺序错误

现在 `SWAP` 和 `~QFT` 方法是受控过程, 并修复`Options.QFTwithNumpy`为`False`时`IQFT`的逻辑错误

增加 **选项**`inputCheck`, 用于检查输入过程参数的正确性, 比如多个量子位应该在同一个系统内, 过程作用的量子位不应该为控制位, 不应该重复输入相同的量子位, 等.

增加`|1❭`相位旋转门的管理器 `RotationGates`. See more: `help(RotationGates)`

增加高级操作 `加法`: `Add`, `AddInt`, 以及他们的逆操作`I~`, 相位版本`Phase~`和逆相位版本`IPhase~`. 增加n-bit加法电路 `Adder`.

---

### 联系方式

qq群 ~~瑟图群~~ : 274767696

作者: **nyasyamorina** *[qq: 1275935966]* (加好友时请备注来意, 免得当作机器人了)


特别感谢 **_hyl** 提供 `pyi` 文件的翻译, _hyl: `"如果发现翻译有错的话, 可以去找我商讨"` *[qq: 2738846947]*

还有非常感激广大群友提供技术支持
