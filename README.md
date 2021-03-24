# nyasQuantumCalculate
一个简单的量子计算模拟库
```python
from nyasQuantumCalculate import *
from nyasQuantumCalculate import Gates

qubit = SingleQubit()
Gates.H(qubit)
result = M(qubit)
print(result)           # False or True
```

---

## 安装

*   python 3.9 on Windows

    1.  下载这个仓库
    2.  在release里下载 `nyasQC.cp39-win_amd64.pyd`
    3.  把 `nyasQC.cp39-win_amd64.pyd` 放到 `~\nyasQuantumCalculate\cy\` 处
    4.  在终端运行 `python -c "import nyasQuantumCalculate"`
    5.  没有错误发生即代表成功

*   others

    1.  确保环境里有合适的C编译器, 如`vs`, `mingw`
    2.  使用 `python -m pip install cython` 安装Cython
    3.  编译`pyx`文件: `python ".\nyasQuantumCalculate\cy\setupNyasQC.py build_ext --inplace"`
    6.  在终端运行 `python -c "import nyasQuantumCalculate"`
    7.  没有错误发生即代表成功

*   安装到python  (all python version)

    1.  确保环境里有合适的C编译器, 如`vs`, `mingw`
    2.  使用 `python -m pip install cython` 安装Cython
    3.  下载这个仓库
    4.  在终端运行 `python setup.py install`
    5.  在终端运行 `python -c "import nyasQuantumCalculate"`
    7.  没有错误发生即代表成功

**如发生错误可以参考最下面的 FAQ**

最后请运行一次 `test_all.py` 确保编译正确

---

## 使用

1.  量子系统

    *   `SingleQubit()` 可以实例化单量子位的系统
    *   `MultiQubits(int)` 可以实例化多量子位系统, 其中int是量子位的数量, 并且使用 `qbs[index]` 可以获取多量子位系统里第index个量子位

2.  量子位门

    *   `SingleQubiteGate(complex,complex,complex,complex)` 可以实例化一个单量子位门, 输入的数字分别代表矩阵的 `左上,右上,左下,右下` 元素
    *   自带一些常用的单量子位门 `I`, `H`, `X`, `Y`, `Z`, `S`, `T`
    *   使用 `Rx(float)`, `Ry(float)`, `Rz(float)`, `R1(float)` 可以获取旋转门
    *   量子位门可以通过 `__call__` 方法作用在量子位上.
    *   对于更复杂的位门, 提供了 `Control` 方法, 并且内置一个双量子位门 `CNOT`, 已知只有 `Rotation Gates` 和 `CNOT` 的量子计算系统的 *完备* 的

3.  测量系统

    *   可以使用方法 `M` 测量一个量子位, 并返回测量结果 (如果测量结果为0, 则返回`False`, 否则为`True`)
    *   或使用方法 `MeasureAll` 测量一个多量子位系统, 并返回包含测量结果的元组

4.  重置系统

    *   对于 `SingleQubit` 可以使用方法 `Reset` 到0状态
    *   而 `MultiQubits` 使用方法 `ResetAll` 重置全部量子位
    *   在程序退出前或清除量子位系统前重置系统是一个良好的习惯

---

## FAQ

*   这个库有前置库吗

    编译文件需要Cython. 但如果有相应的编译好的pyd库, 实际上什么库也不需要. 推荐安装 `matplotlib` 来使用比较美观的量子系统可视化方法 `DumpMachineFig`

*   Cython安装不了怎么办呢 & 我不想安装Cython

    可以在下方猛戳群号或私聊作者获取相应的c文件自行编译为pyd文件

*   `python -c "import nyasQuantumCalculate"` 运行失败

    1.  如果没有把库安装到python里, 确保运行目录与 `nyasQuantumCalculate` 是同一级, 确保`nyasQuantumCalculate\cy\`下有 `nyasQC.*.pyd` , 如果没有, 可以参考`安装`.

    2.  如果把库安装到了python里, 确保运行目录**不**与 `nyasQuantumCalculate` 同一级, 然后参考上面第一步, 但这是库的目录是在 `<你的python安装路径>\Lib\site-packages\nyasQuantumCalculate`

    3.  如果问题仍然没解决可以猛戳下面群号寻求帮助

*   为什么不把库放到pypi上呢

    目前这个库还只是半成品. 并且pypi上可以安装qsharp等更好的库, ~~不想继续增加pip里面的垃圾了~~.

*   为什么要把单个量子位系统做成单独的类呢 & 用多量子位系统模拟单个量子位可以吗

    单独做一个`SingleQubit`是提高了运算速度, 并且为日后的 `Bloch Sqhere` 可视化 做准备. 用多量子位系统模拟单个量子位是可行的, 但是运行速度稍微缓慢

*   内置的位门好少, 使用好困难

    目前这个库还是第一个版本, 仅仅确保了*可运行*, 日后会增加更多功能, 比如多量子位门, QFT, 和量子系统跟踪等

*   我可以跟别人分享这个库吗, 有什么限制

    莫得限制, 随便来就好, 最好可以标注一下作者啦

---

### 已知问题

*   语句 `s*gate` 其中s是数字, gate是`SingleQubitGate`, python解释为 `SingleQubitGate.__mul__(s, gate)`, 而不是 `SingleQubitGate.__rmul__(gate, s)`

*   `setup` 并不会包含文件 `~\nyasQuantumCalculate\cy\nyaQC.*.pyd`, 这个库绝大部分逻辑都是在这个文件里实现的. 尽管 `setup.py` 是可以运作的, 但是打开`setup.py`内部可以看到只是把`pyd`复制过去而已

上述问题真心向大家求助, 如果可以提供参考意见的话真的非常感谢

---

### 联系方式

qq群 ~~瑟图群~~ : 274767696

作者: **nyasyamorina** *[qq: 1275935966]* (加好友时请备注来意, 免得当作机器人了)


特别感谢 **_hyl** 提供 `pyi` 文件的翻译, _hyl: `"如果发现翻译有错的话, 可以去找我商讨"` *[qq: 2738846947]*

还有非常感激广大群友提供技术支持
