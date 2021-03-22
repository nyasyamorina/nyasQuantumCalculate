from typing import NoReturn, List, Tuple, Iterable, Union, Any

class _option:
    """ 控制一些行为\n
    使用 Options.xxx 控制设置的开关\n
    如 'opt = Options.checkUnitGate' 获得目前状态,
    'Options.checkUnitGate = False' 关闭与checkUnitGate相应的行为\n
    \n
    note: 这个类型不应该被实例化\nn
    \nn
    :option: autoNormalize [默认: True]\n
    如果为true, 量子系统会在通过operation之后或被测量之前进行归一化.
    设置为false可以加快运行速度.\n
    \n
    :option: checkUnitGate [默认: True]\n
    如果为true, 在构建门或修改门(乘上常数或两门相乘)时, 会自动计算门n
    是否符合量子门(即酉矩阵).\n
    设置为false可以加快运行速度, 但调用SingleQubitGate.isUnitary时仍会计算,
    该属性(SingleQubitGate.isUnitary)在计算完后会被储存起来, 直到下次修改门\n
    \n
    :option: ignoreWarning [default: False]\n
    目前只有构建 qubits >= 14 的量子系统会发出警告\n
    \n
    :option: checkQubitIdx [default: True]\n
    如果为true, 在进行MultiQubits的量子位操作前判断操作位是否越界
    设置为False可能会因为越界引起程序的崩溃, 除非明白自己在做什么!
    """
    autoNormalize: bool = True
    checkUnitGate: bool = True
    ignoreWarning: bool = False
    checkQubitIdx: bool = True


class TempOption:
    """ 配合with语句暂时控制option的对象

    note: 这个类型不应该由用户实例化 """
    def __init__(self, option_pointer: Any,
                 after: bool, check: Any) -> None: pass
    def __enter__(self) -> None: pass
    def __exit__(self, exc_type: Any,
                 exc_value: Any, traceback: Any) -> None: pass


class _temp_options:
    """ 暂时地控制一些语句 (通过'with'实现)\n
    例子: '''\n
    with TemporaryOptions.autoNormalize(False):\n
        # block1 '''\n
    可以在block1里设置autoNormalize为False, 退出代码块时自动恢复之前的设置\n
    \n
    note: 这个类型不应该被实例化
    """
    def autoNormalize(self, after: bool) -> TempOption: pass
    def checkUnitGate(self, after: bool) -> TempOption: pass
    def ignoreWarning(self, after: bool) -> TempOption: pass
    def checkQubitIdx(self, after: bool) -> TempOption: pass


class QuantumObject:
    """一个接口类型, 你不应该实例化这个类型"""
    pass


class Qubit(QuantumObject):
    """一个接口类型, 你不应该实例化这个类型"""
    def apply(self, gate: "SingleQubitGate") -> None: pass
    def measure(self) -> bool: pass


class QuantumOperation:
    """一个接口类型, 你不应该实例化这个类型"""
    pass


class SingleQubitOperation(QuantumOperation):
    """一个接口类型, 你不应该实例化这个类型"""
    def __call__(self, q: Qubit) -> None: pass


class SingleQubitGate(SingleQubitOperation):
    """一个作用在单个量子位上的门\n
    SingleQubitGate(complex, complex, complex, complex)\n
    \n
    如果Options.checkUnitGate为true, 则会在初始化或修改门后自动计算门是否符合量子门\n
    \n
    乘法: 门就像矩阵一样支持数乘和矩阵乘法\n
    支持 'gate *= s' 和 'new_gate = gate * s', 其中s是复数\n
    'new_gate = gateL @ gateR' 矩阵乘法与数学定义一样\n
    note: 'new_gate = s * gate' 是不支持的, 见SingleQubitGate.__rmul__\n
    \n
    可以使用 'gate(qb)' 代替语句 'qb.apply(gate)'\n
    \n
    内置的gates: I, H, X, Y, Z, S, T, Rx*, Ry*, Rz*, R1*\n
    *note: 旋转门是以函数实现的, 而不是对象\n
    \n
    :property: isUnitary\n
    如果门是量子门, 返回true, 否则返回false\n
    \n
    :property: matrix  ((a, b), (c, d))\n
    返回这个门的复矩阵
    """
    isUnitary: bool = False
    matrix: Tuple[Tuple[complex, complex], Tuple[complex, complex]] = \
            ((1.+0.j, 0.+0.j), (0.+0.j, 1.+0.j))

    def __init__(self, a: complex, b: complex, c: complex, d: complex) -> None:
        """gate的形状为 [[a b] [c d]], 与数学定义相符"""
        pass

    def __imul__(self, s: complex) -> SingleQubitGate: pass
    def __mul__(self, s: complex) -> SingleQubitGate: pass
    def __matmul__(self, gateR: SingleQubitGate) -> SingleQubitGate: pass


    def __rmul__(self, s: complex) -> NoReturn:
        """由于未知的原因, python把语句 'new_gate = s * gate'(s是复数)
        解释为 'new_gate = SingleQubitGate.__mul__(s, gate)', 这明显是错误的"""
        raise RuntimeError


class SingleQubit(Qubit):
    """单个量子位\n
    SingleQubit()\n
    \n
    当实例化时会自动分配默认状态:
    ∣0❭: 1.0; ∣1❭: 0.0\n
    \n
    :property: states  (('∣0❭',), ('∣1❭',))\n
    返回一个元组包含目前的状态 (复数)\n
    \n
    :method: normalize\n
    :method: reset\n
    :method: apply\n
    :method: measure\n
    """
    states: Tuple[Tuple[complex], Tuple[complex]] = ((1.+0.j,), (0.+0.j,))

    def __init__(self) -> None:
        pass

    def normalize(self) -> None:
        pass

    def reset(self) -> None:
        """重置量子位到0状态.\n
        note: ∣0❭ 的辐角不会被重置."""
        pass

    def apply(self, opr: SingleQubitOperation) -> None:
        """把opr作用在量子位上. 如果Options.autoNormalize为true, 操作后会归一化.\n
        note: 目前只支持类型为SingleQubitGate的操作"""
        pass

    def measure(self) -> bool:
        """测量这个量子位, 测量后量子位的状态会坍缩.\n
        如果测量结果为0, 则返回false, 否则为true\n
        如果Options.autoNormalize为true, 测量前会进行归一化"""
        pass


class MultiQubits(QuantumObject):
    """多量子位系统\n
    MultiQubits(int)\n
    \n
    储存了qubits system所有可能的状态, 用于模拟量子行为.\n
    note: 为了模拟量子行为, 需要2^(n+4) bytes内存储存,
    同样需要2^(n+4) bytes内存运算.\n
    \n
    :property: states  (..., (|x>,), ...) # 总共2^n个状态\n
    返回一个元组包含目前的状态 (复数)\n
    \n
    :property: nQubits\n
    返回一个整数代表系统内有多少量子位\n
    \n
    :method: normalize\n
    :method: resetAll\n
    :method: applyTo\n
    :method: measure\n
    :method: control\n
    :method: getQubit\n
    """
    states: Tuple[Tuple[complex], ...] = \
            ((1. + 0.j,), (0. + 0.j,), (0. + 0.j,), (0. + 0.j,))
    nQubits: int = 2

    def __init__(self, n: int) -> None:
        """n是模拟的量子位的数量. 因为类型限制, 最多只支持63个.\n
        在n=14时, 就需要常驻2GiB内存, 和瞬时4GiB内存去满足模拟需求.\n
        \n
        errors: ValueError, MemoryError"""
        pass

    def normalize(self) -> None:
        pass

    def resetAll(self) -> None:
        """重置整个系统到0状态\n
        note: ∣0❭ 的辐角不会被重置."""
        pass

    def applyTo(self, opr: SingleQubitOperation, idx: int) -> None:
        """把opr作用在第idx量子位上. 如果Options.autoNormalize为true,
        操作后会对系统归一化.\n
        note: 目前只支持类型为SingleQubitGate的操作\n
        \n
        errors: IndexError, MemoryError"""
        pass

    def measure(self, idx: int) -> bool:
        """测量第idx个量子位, 测量后量子位的状态会坍缩.\n
        如果测量结果为0, 则返回false, 否则为true\n
        如果Options.autoNormalize为true, 测量前会对系统归一化.\n
        \n
        errors: IndexError"""
        pass

    def control(self, opr: SingleQubitOperation, intList: List[int], idx: int) -> \
                None:
        """当intList作为索引代表的量子位全部为1时, 会把opr作用在第idx个qubit上.\n
        note: 目前只支持类型为SingleQubitGate的操作\n
        \n
        errors: IndexError, ValueError, TypeError, MemoryError"""
        pass

    def getQubit(self, idx: int) -> "QubitIndex":
        """返回这个系统里第idx个量子位, 也可以使用索引或切片操作获得:
        'qb = mutiQb[4]' and 'qbList = mutiQb[5:0:-2]'"""
        pass

    def __len__(self) -> int:
        """ the same as  :property: nQubits"""
        pass

    def __getitem__(self, idx: slice) -> List["QubitIndex"]:
        """errors: IndexError, TypeError, RuntimeError"""
        pass

    def __getitem__(self, idx: int) -> "QubitIndex":
        pass

    # TODO: reset(self, idx: int) -> None


class QubitIndex(Qubit):
    """代表MultiQubits里索引为index的量子位\n
    QubitIndex(int, MultiQubits)\n
    \n
    :property: index\n
    :property: system\n
    \n
    :method: apply\n
    :method: measure\n
    """
    index: int = 0
    system: MultiQubits = None

    def __init__(self, idx: int, sys: MultiQubits) -> None:
        """errors: IndexError"""
        pass

    def apply(self, opr: SingleQubitOperation) -> None:
        """把opr作用量子位上. 如果Options.autoNormalize为true,
        操作后会对系统归一化.\n
        note: 目前只支持类型为SingleQubitGate的操作\n
        \n
        errors: MemoryError"""
        pass

    def measure(self) -> bool:
        """测量量子位, 测量后量子位的状态会坍缩
        如果测量结果为0, 则返回false, 否则为true\n
        如果Options.autoNormalize为true, 测量前会对系统归一化."""
        pass

    # TODO: reset(self) -> None


def convert_number(s: complex) -> Tuple[float, float]:
    """ 把复数从'a+bi'形式转化为'L*e^(ti)'形式\n
    \n
    errors: TypeError"""
    pass

def convert_states(states: Iterable[Iterable[complex]]) -> \
            Tuple[Tuple[float, float], ...]:
    """ 把量子状态从'a+bi'形式转化为'L*e^(ti)'形式\n
    \n
    errors: TypeError"""
    pass


def ApplyToEach(opr: SingleQubitOperation, qubits: MultiQubits) -> None:
    """ 把opr作用在qubits里每个量子位上\n
    note: 目前只支持类型为SingleQubitGate的操作\n
    \n
    errors: TypeError"""
    pass


def MeasureAll(qubits: MultiQubits) -> Tuple[bool]:
    """ 测量qubits里所有量子位, 并返回一个元组包含测量结果\n
    \n
    errors: TypeError"""
    pass


def ColorWheel2RGB(theta: float, is01: bool) -> \
            Union[Tuple[float, float, float], Tuple[int, int, int]]:
    """ 从HSV空间里得到RGB颜色 (h = theta, s = 1, v = 1)\n
    如果is01位true, 则返回范围为[0,1]的浮点数, 否则返回范围为[0,255]的整数"""
    pass


def CNOT(q0: "QubitIndex", q1: "QubitIndex") -> None:
    """note: 'q0' 和 'q1' 应该在同一个系统内
    'CNOT(qbs[0], qbs[1])' 等价于 'qbs.control(X, [0], 1)'"""
    pass



Options: _option = None
TemporaryOptions: _temp_options = None


###########################  Single Qubit Gates  ###############################
# rsqrt2 = 1 / sqrt(2)
I: SingleQubitGate = None       # [[1, 0], [0, 1]]
H: SingleQubitGate = None       # [[rsqrt2, rsqrt2], [rsqrt2, -rsqrt2]]
X: SingleQubitGate = None       # [[0, 1], [1, 0]]
Y: SingleQubitGate = None       # [[0, -i], [i, 0]]
Z: SingleQubitGate = None       # [[1, 0], [0, -1]]
S: SingleQubitGate = None       # [[1, 0], [0, i]]
T: SingleQubitGate = None       # [[1, 0], [0, e^(i*pi/4)]]

# Rx(a)  ->  [[cos(a), -i*sin(a)], [-i*sin(a), cos(a)]]
def Rx(angle: float) -> SingleQubitGate: pass
# Ry(a)  ->  [[cos(a), -sin(a)], [sin(a), cos(a)]]
def Ry(angle: float) -> SingleQubitGate: pass
# Rz(a)  ->  [[e^(-i*a/2), 0], [0, e^(i*a/2)]]
def Rz(angle: float) -> SingleQubitGate: pass
# R1(a)  ->  [[1, 0], [0, e^(i*a)]]
def R1(angle: float) -> SingleQubitGate: pass
