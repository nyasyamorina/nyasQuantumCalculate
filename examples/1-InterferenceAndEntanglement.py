import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from nyasQuantumCalculate import *
from nyasQuantumCalculate import Gates
from nyasQuantumCalculate import Utils



#############  干涉  Interference

# 量子具有波动性, 也就是像水波一样在"波峰-波峰"和"波谷-波谷"的地方会增长
# 而在"波谷-波峰"的地方会消减

# 制备一个同时具有∣0❭和∣1❭的量子位, 并且相位相同
q = SingleQubit()
Gates.H(q)
Utils.DumpMachineText(q)

# 把量子通过"双缝", 在∣0❭处相位相同, 产生了增长, 而在∣1❭处相位相异, 产生了消减
Gates.H(q)
Utils.DumpMachineText(q)
# 尽管这里可以解释为H门的逆为自身, 使用会产生H门后再H门会得到原来的状态
# 不过把H门看作双缝不是挺优美的吗 (bushi
Reset(q)        # 做完一次实验就Reset量子系统是良好的习惯

# 这次来制备与上面情况差不多的量子位, 但∣1❭的相位相差了pi  (-1 = e^(i*pi))
Gates.H(q)
Gates.Z(q)
Utils.DumpMachineText(q)

# 这时候再通过"双缝", 可以看到因为相位的偏差, 这里∣0❭产生消减∣1❭产生增长
Gates.H(q)
Utils.DumpMachineText(q)

Reset(q)
q = None        # 在python里把对象设置为None即可删除对象
# *前提是对象在其他地方没有引用



#################  纠缠  Entanglement

# 在量子力学里纠缠意味着两个或以上个粒子的状态互相绑定在一起
# 在测量其中一个粒子时, 另外的粒子状态也会坍缩到特定状态

# 先来制备具有纠缠态的两个量子位的系统
q = MultiQubits(2)
Gates.H(q[0])
Gates.CNOT(q[0], q[1])
Utils.DumpMachineText(q)

# ∣0❭ (∣00❭) 是两个量子位都为0的状态
# ∣1❭ (∣01❭) 是第二个量子位为0, 第一个量子位为1的状态, 以此类推

# 看到系统只在∣0❭和∣3❭有分布, 而在∣1❭和∣2❭没有分布
# 可以推测当第一个粒子测量为0时, 第二个粒子必定为0, 对于结果1也类似
print(f"Measure Qubit-0: {M(q[0])}")
Utils.DumpMachineText(q)
print(f"Measure Qubit-1: {M(q[1])}")

q.resetAll()
# 可以把下面的代码重复运行多几次试试看

q = None
