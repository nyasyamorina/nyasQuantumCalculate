from typing import NoReturn, List, Tuple, Iterable, Union, Any


class _option:
    """ control some behavior\n
    Using Options.xxx to trun on or off the features given below.\n
    e.g. Gain current states by using 'opt = Options.checkUnitGate',
    'Options.checkUnitGate = False' is used to close it.\n
    \n
    Note: class _option should not be instantiated.\n
    \n
    :option: autoNormalize [efault: True]\n
    If true, quantum system will be normalized after operation or before
    measurement. Setting it to false can acclerate running speed.\n
    \n
    :option: checkUnitGate [default: True]\n
    If ture, when built or modified gate (multiplied by scalars or two gates are
    multiplied), gates will be checked automatically whether they are coincident
    with quantum gates (i.e. unitary matrix). Setting it to false can acclerate
    running speed, but it is still calculated when SingleQubitGate.isUnitary is
    called. SingleQubitGate.isUnitary will be stored after calculation is
    complete, used until the gates are modified again.\n
    \n
    :option: ignoreWarning [default: False]\n
    At present, warn will be thrown out, when the quantum system that having
    more than 14 qubits is built.\n
    \n
    :option: checkQubitIdx [default: True]\n
    If true, control bits will be checked whether out of range before doing
    qubit-wise oeration on MultiQubits. Setting it to false may cause program
    crashes due to out of range, unless you know what are you doing!
    """
    autoNormalize: bool = True
    checkUnitGate: bool = True
    ignoreWarning: bool = False
    checkQubitIdx: bool = True


class TempOption:
    """ Control option objects used with 'with' temporarily.\n
    \n
    Note: This class should not be instantiated by user."""
    def __init__(self, option_pointer: Any,
                 after: bool, check: Any) -> None: pass

    def __enter__(self) -> None: pass
    def __exit__(self, exc_type: Any, exc_value: Any,
                 traceback: Any) -> None: pass


class _temp_options:
    """ Control option objects used with 'with' temporarily.\n
    e.g. '''\n
    with TemporaryOptions.autoNormalize(False):\n
        # block1 '''\n
    You can set the autoNormalize to False in the block1, it will reset the
    settigns as before, when going to exit code block.\n
    \n
    Note:This class should not be instantiated.
    """
    def autoNormalize(self, after: bool) -> TempOption: pass
    def checkUnitGate(self, after: bool) -> TempOption: pass
    def ignoreWarning(self, after: bool) -> TempOption: pass
    def checkQubitIdx(self, after: bool) -> TempOption: pass


class QuantumObject:
    """An interface class, you should not instantiate it."""
    pass


class Qubit(QuantumObject):
    """An interface class, you should not instantiate it."""
    def apply(self, gate: "SingleQubitGate") -> None: pass
    def measure(self) -> bool: pass


class QuantumOperation:
    """An interface class, you should not instantiate it."""
    pass


class SingleQubitOperation(QuantumOperation):
    """An interface class, you should not instantiate it."""
    def __call__(self, q: Qubit) -> None: pass


class SingleQubitGate(SingleQubitOperation):
    """ A gate can operate a single qubit.\n
    SingleQubitGate(complex, complex, complex, complex)\n
    \n
    If Options.checkUnitGate is true, after initialized or modified, gate
    will be checked automatically whether it is coincident with quantum gates.\n
    \n
    Multiplication: This gate supports scalar multiplication and matrix
    multiplication as matrix.\n
    Support 'gate *= s' and 'new_gate = gate * s' where s is complex number.\n
    'new_gate = gateL @ gateR', which same as maths definition.\n
    Note: 'new_gate = s * gate' are not supported,
    see SingleQubitGate.__rmul__.\n
    \n
    qb.apply(gate) can be substituted for gate(qb).\n
    \n
    Built-in gates: I, H, X, Y, Z, S, T, Rx*, Ry*, Rz*, R1*\n
    *Note: Rotation gate is implemented as a function, not an object.\n
    \n
    :property: isUnitary\n
    Return true when the matrix of this gate is unitary,
    otherwise return false.\n
    \n
    :property: matrix  ((a, b), (c, d))\n
    Return the matrix of this gate (complex number).
    """
    isUnitary: bool = False
    matrix: Tuple[Tuple[complex, complex], Tuple[complex, complex]] = \
            ((1.+0.j, 0.+0.j), (0.+0.j, 1.+0.j))

    def __init__(self, a: complex, b: complex, c: complex, d: complex) -> None:
        """The shape of gate is [[a b] [c d]], which is coincident with
        maths difinition"""
        pass

    def __imul__(self, s: complex) -> SingleQubitGate: pass
    def __mul__(self, s: complex) -> SingleQubitGate: pass
    def __matmul__(self, gateR: SingleQubitGate) -> SingleQubitGate: pass

    def __rmul__(self, s: complex) -> NoReturn:
        """For unknown reasons, python will interpret 'new_gate = s * gate'
        (where s is complex) as 'new_gate = SingleQubitGate.__mul__(s, gate)',
        which is clearly incorrect."""
        raise RuntimeError


class SingleQubit(Qubit):
    """A single qubit\n
    SingleQubit()\n
    \n
    Automatically allocated default states when instantiating:
    ∣0❭: 1.0; ∣1❭: 0.0\n
    \n
    :property: states  (('∣0❭',), ('∣1❭',))\n
    Return a tuple with current state (complex number)\n
    \n
    :method: normalize\n
    :method: reset\n
    :method: apply\n
    :method: measure
    """
    states: Tuple[Tuple[complex], Tuple[complex]] = ((1.+0.j,), (0.+0.j,))

    def __init__(self) -> None:
        pass

    def normalize(self) -> None:
        pass

    def reset(self) -> None:
        """Reset qubit to 0 state.\n
        Note: the angle of ∣0❭ will not be reset."""
        pass

    def apply(self, opr: SingleQubitOperation) -> None:
        """Operate qubit. If Options.autoNormalize is true, the qubit which is
        being operated will be normalized after operation.\n
        Note: Only support type is SingleQubitGate's operation at present."""
        pass

    def measure(self) -> bool:
        """Measure qubit, the states of qubit will collapse after measurement.
        Return False if measure result is 0, otherwise return True.\n
        If Options.autoNormalize is true, system will be normailized before
        measurement."""
        pass


class MultiQubits(QuantumObject):
    """Multiple qubits system.\n
    MultiQubits(int)\n
    \n
    Storing all possible states of qubits system,
    used to simulate quantums' behavior.\n
    Note: In order to store quantums' states, 2^(n+4) bytes memory space is
    needed, similarly 2^(n+4) bytes memory space is also needed for
    calculation.\n
    \n
    :property: states  (..., (∣x❭,), ...) # total 2^n states\n
    Return a tuple with current state (complex number)\n
    \n
    :property: nQubits\n
    Return a number shows how many qubits in this system\n
    \n
    :method: normalize\n
    :method: resetAll\n
    :method: applyTo\n
    :method: measure\n
    :method: control\n
    :method: getQubit
    """
    states: Tuple[Tuple[complex], ...] = \
            ((1. + 0.j,), (0. + 0.j,), (0. + 0.j,), (0. + 0.j,))
    nQubits: int = 2

    def __init__(self, n: int) -> None:
        """n is the number of qubit you want to simulate. Because of type
        limited, maximum number of qubits is 63.\n
        When n = 14, 2GiB of permanent memory and 4GiB of instantaneous memory\n
        are required to meet the simulation requirements.\n
        \n
        errors: ValueError, MemoryErro"""
        pass

    def normalize(self) -> None:
        pass

    def resetAll(self) -> None:
        """Reset all system to 0 state\n
        Note: the angle of ∣0❭ will not be reseted."""
        pass

    def applyTo(self, opr: SingleQubitOperation, idx: int) -> None:
        """Operate the idx-th qubit. If Options.autoNormalize is true,
        the qubit which is being operated will be normalized after operation.\n
        Note: Only support type is SingleQubitGate's operation at present.\n
        \n
        errors: IndexError, MemoryError"""
        pass

    def measure(self, idx: int) -> bool:
        """Measure the idx-th qubit, the states of qubit will
        collapse after measurement.\n
        Return False if measure result is 0, otherwise return True.\n
        If Options.autoNormalize is true, the system will be
        normalized before measurement.\n
        \n
        errors: IndexError"""
        pass

    def control(self, opr: SingleQubitOperation, intList: List[int], idx: int) -> \
                None:
        """When all of qubits indexed by intList are equal to 1,
        the idx-th qubit will be operated.\n
        Note: Only support type is SingleQubitGate's operation at present.\n
        \n
        errors: IndexError, ValueError, TypeError, MemoryError"""
        pass

    def getQubit(self, idx: int) -> "QubitIndex":
        """Return the idx-th qubit of the system, which you can also use
        index or slice operation to obtain.\n
        'qb = mutiQb[4]' and 'qbList = mutiQb[5:0:-2]'"""
        pass

    def __len__(self) -> int:
        """Same as  :property: nQubits"""
        pass

    def __getitem__(self, idx: slice) -> List["QubitIndex"]:
        """errors: IndexError, TypeError, RuntimeError"""
        pass

    def __getitem__(self, idx: int) -> "QubitIndex":
        pass


class QubitIndex(Qubit):
    """Represent the qubit of multiqubits system which is indexed by idx.\n
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
        """Operate qubit. If Options.autoNormalize is true,
        the qubit will be normalized after operation.\n
        Note: Only support type is SingleQubitGate's operation at present.\n
        \n
        errors: IndexError, MemoryError"""
        pass

    def measure(self) -> bool:
        """measure qubit, the states of qubit will collapse after measurement.\n
        Return False if measure result is 0, otherwise return True.\n
        If Options.autoNormalize is true, the system will be
        normalized before measurement."""
        pass


def convert_number(s: complex) -> Tuple[float, float]:
    """Convert a complex number from 'a+bi' to 'L*e^(i*t)'\n
    \n
    errors: TypeError"""
    pass


def convert_states(states: Iterable[Iterable[complex]]) -> \
            Tuple[Tuple[float, float], ...]:
    """Convert states from 'a+bi' to 'L*e^(i*t)'\n
    \n
    errors: TypeError"""
    pass


def ApplyToEach(opr: SingleQubitOperation, qubits: MultiQubits) -> None:
    """Apply opr to each qubit in qubits.\n
    Note: Only support type is SingleQubitGate's operation at present.\n
    \n
    errors: TypeError"""
    pass


def MeasureAll(qubits: MultiQubits) -> Tuple[bool]:
    """Measure all qubit in system, and return a tuple of boolean\n
    \n
    errors: TypeError"""
    pass


def ColorWheel2RGB(theta: float, is01: bool) -> \
        Union[Tuple[float, float, float], Tuple[int, int, int]]:
    """Simply get RGB color from HSV space (h = theta, s = 1, v = 1)\n
    if 'is01' is true, then return floats ranging in [0., 1.],
    otherwise, return integers ranging in [0, 255]"""
    pass


def CNOT(q0: "QubitIndex", q1: "QubitIndex") -> None:
    """Note: 'q0' and 'q1' should be in the same system.\n
    'CNOT(qbs[0], qbs[1])' equal 'qbs.control(X, [0], 1)'"""
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
