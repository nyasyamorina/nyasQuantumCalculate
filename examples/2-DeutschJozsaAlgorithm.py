import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import numpy as np

from nyasQuantumCalculate import *



# Deutsche Jozsa 算法 是一个很好的展示量子计算的简单算法
# 它足够简单, 只需要几个位门即可完成, 并且相比传统算法运算快很多*
# *当然对于模拟量子计算来说是不会有速度提升的, 但是也不妨碍在这里用作例子


###################  什么是 Deutsche Jozsa 算法  ################################
""" Deutsche Jozsa 算法:

有一个未知函数 f: {0,1}^n -> {0,1}*, 并且已知f要么是常数函数, 要么是均衡函数**, 判断f
是常数函数还是均衡函数***

*   按人话说就是f输入n个0或1, 然后输出一个0或1
**  均衡的意思是, 在对于所有可能的输入来说, 有一半结果是0, 另外一半是1
*** 只需要判断f是哪种类型的函数, 而不在意f的输出结果
"""


##############################  传统算法  #######################################
"""
把 f 的输入"{0,1}^n"可以看作"[0,2^n)&Z" (按人话来说就是从0到2^n但不包含2^n的整数)

在传统算法里, 只能从0开始历遍, 当历遍到有值与之前的值不一致时, 说明f不是常数函数, 那必
然是均衡函数. 并且历遍超过可能输入的一半时, 说明f不是均衡函数, 是常数函数.

按照上述思路, 实现算法至少需要2步, 至多需要2^(n-1)+1步
"""

# 这里提供几种常见的函数    (为了节省篇幅就省略一点空行了)
class UnknownFunctionClassical:
    def __init__(self, n: int = 0) -> None:
        raise NotImplementedError
    def __call__(self, x: int) -> bool:
        raise NotImplementedError

class Constant0C(UnknownFunctionClassical):
    def __init__(self, n: int) -> None:
        pass
    def __call__(self, x: int) -> bool:
        return False

class Constant1C(UnknownFunctionClassical):
    def __init__(self, n: int) -> None:
        pass
    def __call__(self, x: int) -> bool:
        return True

class IfNthBitC(UnknownFunctionClassical):
    # 如果第n个bit为1, 则返回1, 否则为0
    def __init__(self, n: int) -> None:
        self.tag = 1 << n
    def __call__(self, x: int) -> bool:
        return x & self.tag != 0

class Even1BitsC(UnknownFunctionClassical):
    # 如果有偶数个1, 则返回0, 否则为1
    def __init__(self, n: int) -> None:
        pass
    def __call__(self, x: int) -> bool:
        count = 0
        while x >= 1:
            if x & 1:
                count += 1
            x >>= 1
        return count & 1 == 0

class RandomFunC(UnknownFunctionClassical):
    def __init__(self, n: int) -> None:
        self.choice = np.array(())
    def setTotalBits(self, n: int) -> None:
        self.choice = np.random.choice(1 << n, 1 << (n - 1), False)
    def __call__(self, x: int) -> bool:
        return x in self.choice


#################  算法本体

def DeutscheJozsaClassical(totalBits: int,
                           func: UnknownFunctionClassical) -> bool:
    if isinstance(func, RandomFunC):
        func.setTotalBits(totalBits)
    # 如果func为常数函数则返回True, 否则为False
    f0 = func(0)
    steps = 1
    isConstant = True
    # python 的 range 并不包含最后一个数字a
    for x in range(1, (1 << (totalBits - 1)) + 1):
        steps += 1
        if func(x) != f0:
            isConstant = False
            break
    print(f"Total Steps: {steps} (Classical)")
    return isConstant

print(f"Is constant function?(C): {DeutscheJozsaClassical(5, IfNthBitC(3))}")
# 可以自己尝试调一下数据试着运行



###############################  量子算法  ######################################
"""
量子计算的一个巨大的优点就是并行运算. 这给了一点启示: 可以把f全部可能的输入都计算一遍,
然后再统计结果.

对于函数 f, 需要把它变为应该可以作用在量子位上的位门 U, 可以设计为如果f输出1, 则位门U
把系统状态反转 (乘上-1).

如果f是均衡函数, 那么量子系统里有一半的状态都被反转, 这时候把状态全部互相干涉的话, 结果
不会在∣0❭聚集. 反之, 如果全部状态的相位抑制, 那么互相干涉后状态会在∣0❭聚集
"""

# 这里提供几种常见的函数    (为了节省篇幅就省略一点空行了)
class UnknownFunctionQuantum:
    def __init__(self, n: int = 0) -> None:
        raise NotImplementedError
    def __call__(self, qbs: Qubits) -> None:
        raise NotImplementedError

class Constant0Q(UnknownFunctionQuantum):
    def __init__(self, n: int) -> None:
        pass
    def __call__(self, qbs: Qubits) -> None:
        pass

class Constant1Q(UnknownFunctionQuantum):
    def __init__(self, n: int) -> None:
        self.reversStateGate = I * -1
    def __call__(self, qbs: Qubits) -> None:
        self.reversStateGate(qbs[0])

class IfNthBitQ(UnknownFunctionQuantum):
    def __init__(self, n: int) -> None:
        self.n = n

    def __call__(self, qbs: Qubits) -> None:
        if self.n >= len(qbs):
            return
        Z(qbs[self.n])

class Even1BitsQ(UnknownFunctionQuantum):
    def __init__(self, n: int) -> None:
        pass
    def __call__(self, qbs: Qubits) -> None:
        ApplyToEach(Z, qbs)

class RandomFunQ(UnknownFunctionQuantum):
    def __init__(self, n: int) -> None:
        pass
    def __call__(self, qbs: Qubits) -> None:
        n = len(qbs)
        choice = np.random.choice(1 << n, 1 << (n - 1), False)
        print(choice)
        with TemporaryQubit(qbs.system) as tmQ:
            # 使用了所谓的"相位反冲技巧"
            X(tmQ)
            H(tmQ)
            for integer in choice:
                ControlledOnInt(X, integer, qbs, tmQ)
            H(tmQ)
            X(tmQ)


#################  算法本体

def DeutscheJozsaQuantum(totalBits: int,
                         func: UnknownFunctionQuantum) -> bool:
    # 如果func为常数函数则返回True, 否则为False
    sytm = QubitsSystem(totalBits)
    qubits: Qubits = sytm[:]
    DumpSystemFig(sytm) if have_matplotlib else DumpSystemText(sytm)

    ApplyToEach(H, qubits)
    DumpSystemFig(sytm) if have_matplotlib else DumpSystemText(sytm)

    func(qubits)
    DumpSystemFig(sytm) if have_matplotlib else DumpSystemText(sytm)

    ApplyToEach(H, qubits)
    DumpSystemFig(sytm) if have_matplotlib else DumpSystemText(sytm)

    result = MeasureAll(qubits)
    ResetAll(qubits)
    return not any(result)

print(f"Is constant function?(Q): {DeutscheJozsaQuantum(5, IfNthBitQ(3))}")
# 可以自己尝试调一下数据试着运行


#######################  强烈注意
# 大多数情况下, DeutscheJozsa算法的示例是使用标记黑盒, 需要totalBits+1个量子位
# 但这里是使用的是相位黑盒, 所以只需要totalBits个量子位
