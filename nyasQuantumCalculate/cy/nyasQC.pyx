# cython: language_level = 3
# cython: boundscheck = False
# cython: wraparound = False
# cython: cdivision = True

from libc.math cimport sqrt, sin, cos, acos, fmod
from libc.math cimport M_SQRT1_2, M_PI
from libc.stdlib cimport calloc, free
from libc.time cimport time as ctime, clock
from libc.limits cimport UINT_MAX as UNIT32_MAX
from cpython.slice cimport PySlice_Unpack
from cpython.tuple cimport PyTuple_New, PyTuple_SET_ITEM



###############################################################################
################################  C Basic  ####################################
###############################################################################

ctypedef unsigned char uint8
ctypedef unsigned int uint32
ctypedef unsigned long long int uint64
ctypedef signed long long int int64
ctypedef float float32
ctypedef double float64
ctypedef double complex complex128

ctypedef unsigned char execCode
cdef execCode SUCCESS = 0, MEMORYERROE = 1, SLICEERROR = 2

cdef float64 PI2 = 2. * M_PI

#assert sizeof(uint64) == 8 and sizeof(complex128) == 16
#################################  Utils  #####################################

cdef float64 absSqr(complex128 s):
    # return s * s_bar
    cdef float64 real = s.real, imag = s.imag
    return real * real + imag * imag

cdef complex128 conj(complex128 s):
    # return s_bar
    return s.real - s.imag

cdef uint8 floatEqual0(float64 x):
    return x < 1e-8

cdef float32 clamp(float32 x, float32 a, float32 b):
    if b < x:
        return b
    if a > x:
        return a
    return x

cdef float32 color_f(uint8 n, float32 h_pi_3):
    cdef float32 k = <float32>fmod(n + h_pi_3, 6.)
    if k < 2:
        return clamp(k, 0., 1.)
    return clamp(<float32>4. - k, 0., 1.)

cdef execCode correctIndex(slice sli, int64 max, int64 *start, int64 *stop, int64 *step):
    cdef Py_ssize_t pyStart, pyStop, pyStep
    cdef int code = PySlice_Unpack(sli, &pyStart, &pyStop, &pyStep)
    if code != 0:
        return SLICEERROR
    if pyStep > 0:
        start[0] = <int64>pyStart if pyStart >= 0 else 0
        stop[0] = <int64>pyStop if pyStop < max else max
    elif pyStep < 0:
        start[0] = <int64>pyStart if pyStart < max else max - 1
        stop[0] = <int64>pyStop if pyStop >= 0 else -1
    else:
        return SLICEERROR
    step[0] = <int64> pyStep
    return SUCCESS

#######################  Random Method from Java  #############################

cdef uint64 _random_state = (<uint64>ctime(NULL) << 8) ^ clock()
cdef uint64 _random_m = (<uint64>1 << 48) - 1, _random_a = 0x5DEECE66D, _random_c = 11

cdef uint32 random_nextInt():       # return value in [0, 2^32-1]
    global _random_state
    _random_state = (_random_state * _random_a + _random_c) & _random_m
    return (_random_state >> 16) & UNIT32_MAX

cdef float32 random_nextFloat():    # return value in [0., 1.]
    return <float32>random_nextInt() / UNIT32_MAX

#########################  Single Qubit Struct  ###############################

cdef struct SingleQubit_s:
    complex128 x0           # state  |0>
    complex128 x1           # state  |1>

cdef void SQ_normalize(SingleQubit_s *data):
    cdef float64 rR = 1. / sqrt(absSqr(data.x0) + absSqr(data.x1))
    data.x0 *= rR
    data.x1 *= rR

cdef void SQ_reset(SingleQubit_s *data):
    data.x1 = 0.
    cdef float64 r0 = absSqr(data.x0)
    if floatEqual0(r0):
        data.x0 = 1.
    else:
        data.x0 /= sqrt(r0)

cdef uint8 SQ_measure(SingleQubit_s *data):
    cdef float64 r = absSqr(data.x0)                    # probability of (measure result = 0)
    cdef uint8 meas1 = random_nextFloat() > r           # is (measure = 1)?
    # apply result to qubit state and normalize
    if meas1:
        r = absSqr(data.x1)
        data.x0 = 0.
        data.x1 /= sqrt(r)
    else:
        data.x0 /= sqrt(r)
        data.x1 = 0.
    return meas1

cdef void SQ_apply(SingleQubit_s *data, SingleQubitGate_s *gate):
    cdef complex128 x0 = data.x0
    data.x0 = x0 * gate.a + data.x1 * gate.b
    data.x1 = x0 * gate.c + data.x1 * gate.d

#########################  Single Qubit Gate Struct  ##########################

cdef struct SingleQubitGate_s:
    # [[a, b],
    #  [c, d]]
    complex128 a
    complex128 b
    complex128 c
    complex128 d

cdef uint8 SQG_isUnit(SingleQubitGate_s *data):             # is a unitary matrix?
    if not floatEqual0(absSqr(data.a * conj(data.c) + data.b * conj(data.d))):
        return 0
    if not floatEqual0(absSqr(data.a * conj(data.b) + data.c * conj(data.d))):
        return 0
    cdef double absA = absSqr(data.a), absB = absSqr(data.b), absC = absSqr(data.c), absD = absSqr(data.d)
    if floatEqual0(absA + absB - 1.) and floatEqual0(absA + absC - 1.) and \
       floatEqual0(absD + absB - 1.) and floatEqual0(absD + absC - 1.):
       return 1
    return 0

cdef void SQG_multiConst(SingleQubitGate_s *data, complex128 s):
    data.a *= s
    data.b *= s
    data.c *= s
    data.d *= s

cdef void SQG_matrixMul(SingleQubitGate_s *data, SingleQubitGate_s *IN_right):
    cdef complex128 a = data.a, c = data.c
    data.a = a * IN_right.a + data.b * IN_right.c
    data.b = a * IN_right.b + data.b * IN_right.d
    data.c = c * IN_right.a + data.d * IN_right.c
    data.d = c * IN_right.b + data.d * IN_right.d

#########################  Multiple Qubits Struct  ############################

cdef struct MultiQubits_s:
    complex128 *states
    uint64 length

cdef struct QubitIndexList:
    uint8 *idxs
    uint8 length

cdef void MQ_clearState(MultiQubits_s *data):
    cdef uint64 index
    for index in range(data.length):
        data.states[index] = 0.

cdef void MQ_normalize(MultiQubits_s *data):
    cdef float64 r = 0.
    cdef uint64 index
    for index in range(data.length):
        r += absSqr(data.states[index])
    r = 1. / sqrt(r)
    for index in range(data.length):
        data.states[index] *= r

cdef void MQ_resetAll(MultiQubits_s *data):
    cdef complex128 x0 = data.states[0]
    MQ_clearState(data)
    cdef float64 r0 = absSqr(x0)
    if floatEqual0(r0):
        data.states[0] = 1.
    else:
        data.states[0] = x0 / sqrt(r0)

cdef execCode MQ_applyTo(MultiQubits_s *data, SingleQubitGate_s *gate, uint8 idx):
    # copy and clean states
    cdef complex128 *old_states = <complex128 *>calloc(data.length, 16)
    if old_states == NULL:
        return MEMORYERROE
    cdef uint64 i, j
    for i in range(data.length):
        old_states[i] = data.states[i]
        data.states[i] = 0.
    cdef uint64 tag = (<uint64>1) << idx
    cdef complex128 tmp
    # matrix multiplication
    for i in range(data.length):
        tmp = old_states[i]
        j = i ^ tag
        if i & tag:
            data.states[i] += gate.d * tmp
            data.states[j] += gate.b * tmp
        else:
            data.states[i] += gate.a * tmp
            data.states[j] += gate.c * tmp
    # clean up
    free(old_states)
    old_states = NULL
    return SUCCESS

cdef uint8 MQ_measure(MultiQubits_s *data, uint8 idx):
    cdef uint64 tag = (<uint64>1) << idx
    cdef float64 r = 0.
    cdef uint64 index, range0 = data.length - tag
    # calculate probability of (measure result = 0)
    for index in range(range0):
        if not index & tag:
            r += absSqr(data.states[index])
    cdef uint8 meas1 = random_nextFloat() > r           # is measure result = 1 ?
    # apply result to qubit state and normalize
    r = 0.
    for index in range(data.length):
        if (index & tag != 0) ^ meas1:
            data.states[index] = 0.
        else:
            r += absSqr(data.states[index])
    r = 1. / sqrt(r)
    for index in range(data.length):
        if (index & tag == 0) ^ meas1:
            data.states[index] *= r
    return meas1

cdef execCode MQ_controll(MultiQubits_s *data, SingleQubitGate_s *gate,
                            QubitIndexList *ctrlBits, uint8 idx):
    # copy and clear states
    cdef uint64 i, j
    cdef complex128 *old_states = <complex128 *>calloc(data.length, 16)
    if old_states == NULL:
        return MEMORYERROE
    for i in range(data.length):
        old_states[i] = data.states[i]
        data.states[i] = 0.
    # get control bits
    cdef uint64 tags = 0
    for i in range(ctrlBits.length):
        tags |= (<uint64>1) << ctrlBits.idxs[i]
    cdef uint64 tag = (<uint64>1) << idx
    cdef complex128 tmp
    # matrix multiplication
    for i in range(data.length):
        tmp = old_states[i]
        if i & tags ^ tags == 0:
            j = i ^ tag
            if i & tag:
                data.states[i] += gate.d * tmp
                data.states[j] += gate.b * tmp
            else:
                data.states[i] += gate.a * tmp
                data.states[j] += gate.c * tmp
        else:
            data.states[i] = tmp
    # clean up
    free(old_states)
    old_states = NULL
    return SUCCESS

cdef void MQ_reset(MultiQubits_s *data, uint8 idx):
    # TODO
    pass

###############################################################################
############################  Expose to Python  ###############################
###############################################################################

#################################  Options  ###################################

cdef uint8 autoNormalize = 1
cdef uint8 checkUnitGate = 1
cdef uint8 ignoreWarning = 0
cdef uint8 checkQubitIdx = 1

cdef uint8 _is_init_options = 0
cdef class _options:
    def __init__(_options self):
        global _is_init_options
        if _is_init_options:
            raise AttributeError(f"type object '{self.__class__.__name__}' has no attribute '__init__'")
        else:
            _is_init_options = 1
    property autoNormalize:
        def __get__(self):
            return <bint>autoNormalize
        def __set__(self, bint b):
            global autoNormalize
            autoNormalize = <uint8>b
    property checkUnitGate:
        def __get__(self):
            return <bint>checkUnitGate
        def __set__(self, bint b):
            global checkUnitGate
            checkUnitGate = <uint8>b
    property ignoreWarning:
        def __get__(self):
            return <bint>ignoreWarning
        def __set__(self, bint b):
            global ignoreWarning
            ignoreWarning = <uint8>b
    property checkQubitIdx:
        def __get__(self):
            return <bint>checkQubitIdx
        def __set__(self, bint b):
            global checkQubitIdx
            checkQubitIdx = <uint8>b

##########################  Temporary Options  ################################

cdef class TempOption:
    cdef:
        uint8 *opt_p
        uint8 before_
        uint8 after_
    def __init__(TempOption self, uint64 option_pointer, bint after, uint64 check):
        if <uint8 *>check != &_is_init_temp_options:
            raise RuntimeError
        self.opt_p = <uint8 *>option_pointer
        self.after_ = after

    def __enter__(TempOption self):
        self.before_ = self.opt_p[0]
        self.opt_p[0] = self.after_

    def __exit__(TempOption self, object exc_type, object exc_value, object traceback):
        self.opt_p[0] = self.before_

cdef uint8 _is_init_temp_options = 0
cdef class _temp_options:
    def __init__(_temp_options self):
        global _is_init_temp_options
        if _is_init_temp_options:
            raise AttributeError(f"type object '{self.__class__.__name__}' has no attribute '__init__'")
        else:
            _is_init_temp_options = 1

    def autoNormalize(_temp_options self, bint after):
        return TempOption(<uint64>&autoNormalize, after, <uint64>&_is_init_temp_options)

    def checkUnitGate(_temp_options self, bint after):
        return TempOption(<uint64>&checkUnitGate, after, <uint64>&_is_init_temp_options)

    def ignoreWarning(_temp_options self, bint after):
        return TempOption(<uint64>&ignoreWarning, after, <uint64>&_is_init_temp_options)

    def checkQubitIdx(_temp_options self, bint after):
        return TempOption(<uint64>&checkQubitIdx, after, <uint64>&_is_init_temp_options)

###########################  Interface  Class  ################################

cdef class QuantumObject:
    def __init__(QuantumObject self):
        raise NotImplementedError(f"cannot instantiate interface class: {self.__class__.__name__}")

cdef class Qubit(QuantumObject):
    def apply(Qubit self, SingleQubitOperation op):
        raise NotImplementedError(f"{self.__class__.__name__}.apply is not defined")

    def measure(Qubit self):
        raise NotImplementedError(f"{self.__class__.__name__}.measure is not defined")

cdef class QuantumOperation:
    # TODO: Using Quantumoperation.name to track qubits system
    def __init__(QuantumOperation self):
        raise NotImplementedError(f"cannot instantiate interface class: {self.__class__.__name__}")

cdef class SingleQubitOperation(QuantumOperation):
    # TODO: SingleQubitOperation: multiple SingleQubitGate operation
    def __call__(SingleQubitGate self, Qubit q):
        raise NotImplementedError(f"{self.__class__.__name__}.__call__ is not defined")

##############################  Single Qubit  #################################

cdef class SingleQubit(Qubit):
    # TODO: SingleQubit is Qubit and QubitsSystem
    cdef SingleQubit_s data
    def __init__(SingleQubit self):
        self.data.x0 = 1.
        self.data.x1 = 0.

    property states:
        def __get__(self):
            return ((self.data.x0,), (self.data.x1,))

    def normalize(SingleQubit self):
        SQ_normalize(&self.data)

    def reset(SingleQubit self):
        SQ_reset(&self.data)

    def apply(SingleQubit self, SingleQubitOperation opr):
        if isinstance(opr, SingleQubitGate):
            SQ_apply(&self.data, &(<SingleQubitGate>opr).data)
        if autoNormalize:
            SQ_normalize(&self.data)

    def measure(SingleQubit self):
        if autoNormalize:
            SQ_normalize(&self.data)
        return <bint>SQ_measure(&self.data)

############################  Single Qubit Gate  ##############################

cdef class SingleQubitGate(SingleQubitOperation):
    cdef:
        SingleQubitGate_s data
        char isUnit             # -1 = Unknown, 0 = False, 1 = True
    def __init__(SingleQubitGate self, complex128 a, complex128 b, complex128 c, complex128 d):
        self.data.a = a
        self.data.b = b
        self.data.c = c
        self.data.d = d
        self.isUnit = SQG_isUnit(&self.data) if checkUnitGate else -1

    property isUnitary:
        def __get__(self):
            if self.isUnit == -1:
                self.isUnit = SQG_isUnit(&self.data)
            return <bint>(self.isUnit == 1)

    property matrix:
        def __get__(self):
            return ((self.data.a, self.data.b), (self.data.c, self.data.d))

    def __imul__(SingleQubitGate self, complex128 s):
        SQG_multiConst(&self.data, s)
        if checkUnitGate:
            if self.isUnit == 1 and not floatEqual0(absSqr(s) - 1.):
                self.isUnit = 0
            else:
                self.isUnit = SQG_isUnit(&self.data)
        else:
            self.isUnit = -1
        return self

    def __mul__(SingleQubitGate self, complex128 s):
        global checkUnitGate
        cdef uint8 before_ = checkUnitGate
        checkUnitGate = 0
        cdef SingleQubitGate new_SQG = SingleQubitGate(self.data.a, self.data.b, self.data.c, self.data.d)
        checkUnitGate = before_
        # new_SQG.__imul__
        SQG_multiConst(&new_SQG.data, s)
        if checkUnitGate:
            if self.isUnit == 1 and not floatEqual0(absSqr(s) - 1.):
                new_SQG.isUnit = 0
            else:
                new_SQG.isUnit = SQG_isUnit(&new_SQG.data)
        return new_SQG

    def __rmul__(SingleQubitGate self, complex128 s):
        # TODO: new_gate = s * gate
        raise RuntimeError("For unknown reason, 'new_gate=s*gate' always matches 'SingleQubitGate.__mul__' "
                           "instead of 'SingleQubitGate.__rmul__'")

    def __matmul__(SingleQubitGate self, SingleQubitGate right):
        global checkUnitGate
        cdef uint8 before_ = checkUnitGate
        checkUnitGate = 0
        cdef SingleQubitGate new_SQG = SingleQubitGate(self.data.a, self.data.b, self.data.c, self.data.d)
        checkUnitGate = before_
        SQG_matrixMul(&new_SQG.data, &right.data)
        if checkUnitGate:
            if self.isUnit == 1 and right.isUnit == 1:
                new_SQG.isUnit = 1
            else:
                new_SQG = SQG_isUnit(&new_SQG.data)
        return new_SQG

    def __call__(SingleQubitGate self, Qubit q):
        q.apply(self)

#########################  Multiple Qubits System  ############################

cdef class MultiQubits(QuantumObject):
    cdef:
        MultiQubits_s data
        readonly uint8 nQubits
    def __cinit__(MultiQubits self, uint8 n):
        if n >= 64:
            raise ValueError("only support up to 64 qubits")
        if not ignoreWarning and n >= 14:
            print(f"Warning: allocating {n} qubits system, "
                  f"it will need around {self.data.length * 32} bytes to simulate")
        self.data.length = (<uint64>1) << n
        self.data.states = <complex128 *>calloc(self.data.length, 16)
        if self.data.states == NULL:
            raise MemoryError("In method 'MultiQubits.__cinit__', no adequate memory to be allocated, "
                             f"{self.data.length * 16} bytes available memory size is needed")
    def __init__(MultiQubits self, uint8 n):
        self.nQubits = n
        self.data.states[0] = 1.

    property states:
        def __get__(self):
            cdef uint64 index
            return tuple((self.data.states[index],) for index in range(self.data.length))

    def __len__(self):
        return self.nQubits

    def __dealloc__(MultiQubits self):
        free(self.data.states)
        self.data.states = NULL

    def normalize(MultiQubits self):
        MQ_normalize(&self.data)

    def resetAll(MultiQubits self):
        MQ_resetAll(&self.data)

    def applyTo(MultiQubits self, SingleQubitOperation opr, uint8 idx):
        cdef execCode code
        if checkQubitIdx and (idx >= self.nQubits or idx < 0):
            raise IndexError(f"{self.nQubits} qubits system has no qubit with index {idx}")
        if isinstance(opr, SingleQubitGate):
            code = MQ_applyTo(&self.data, &(<SingleQubitGate>opr).data, idx)
            if code == MEMORYERROE:
                raise MemoryError("In method 'MultiQubits.applyTo', no adequate memory to be allocated, "
                                 f"{self.data.length * 16} bytes available memory size is needed")
        if autoNormalize:
            MQ_normalize(&self.data)

    def measure(MultiQubits self, uint8 idx):
        if checkQubitIdx and (idx >= self.nQubits or idx < 0):
            raise IndexError(f"{self.nQubits} qubits system has no qubit with index {idx}")
        if autoNormalize:
            MQ_normalize(&self.data)
        return <bint>MQ_measure(&self.data, idx)

    def control(MultiQubits self, SingleQubitGate gate, object intList, uint8 idx):
        if checkQubitIdx and (idx >= self.nQubits or idx < 0):
            raise IndexError(f"{self.nQubits} qubits system has no qubit with index {idx}")
        cdef QubitIndexList cList
        cdef int list_length = <int>len(intList)    # TypeError
        if list_length >= 63:
            raise ValueError(f"list length >= 63")
        cList.length = <uint8>list_length
        cList.idxs = <uint8 *>calloc(cList.length, 1)
        if cList.idxs == NULL:
            raise MemoryError("In method 'MultiQubits.controlled', no adequate memory to be allocated, "
                             f"{cList.length} bytes available memory size is needed")
        cdef uint8 ele, i = 0
        for ele in intList:                         # TypeError
            if ele == idx:
                raise ValueError(f"controlled-qubit and control-qubit should not be the same: qubit index {idx}")
            if checkQubitIdx and (ele >= self.nQubits or ele < 0):
                raise IndexError(f"{self.nQubits} qubits system has no qubit with index {ele}")
            cList.idxs[i] = ele
            i += 1
        cdef execCode code = MQ_controll(&self.data, &gate.data, &cList, idx)
        if code == MEMORYERROE:
            free(cList.idxs)
            cList.idxs = NULL
            raise MemoryError("In method 'MultiQubits.controlled', no adequate memory to be allocated, "
                             f"aronud {self.data.length * 16} bytes available memory size is needed")
        #clean up
        free(cList.idxs)
        cList.idxs = NULL
        if autoNormalize:
            MQ_normalize(&self.data)

    def getQubit(MultiQubits self, uint8 idx):
        return QubitIndex(idx, self)

    def __getitem__(MultiQubits self, object idx):
        global checkQubitIdx
        cdef int64 start, stop, step, index
        cdef execCode code
        cdef uint8 before_ = checkQubitIdx
        checkQubitIdx = 0
        cdef object result
        if isinstance(idx, int):
            index = idx
            if index < 0:
                index += self.nQubits
            if before_ and (index >= 0 and index >= self.nQubits):
                checkQubitIdx = before_
                raise IndexError(f"{self.nQubits} qubits system has no qubit with index {index}")
            result = QubitIndex(index, self)
        elif isinstance(idx, slice):
            code = correctIndex(idx, self.nQubits, &start, &stop, &step)
            if code != SUCCESS:
                raise RuntimeError(f"error in MultiQubits.__getitem__: {code}")
            result = [QubitIndex(index, self) for index in range(start, stop, step)]
        else:
            checkQubitIdx = before_
            raise TypeError(f"indices must be integers or slices, not{type(idx)}")
        checkQubitIdx = before_
        return result
    # TODO: reset(self, idx: int) -> None


cdef class QubitIndex(Qubit):
    cdef:
        readonly uint8 index
        readonly MultiQubits system
    def __init__(QubitIndex self, uint8 idx, MultiQubits sys):
        if checkQubitIdx and (idx >= sys.nQubits or idx < 0):
            raise IndexError(f"{sys.nQubits} qubits system has no qubit with index {idx}")
        self.index = idx
        self.system = sys

    #def reset(QubitIndex self): pass # TODO

    def apply(QubitIndex self, SingleQubitOperation opr):
        cdef execCode code
        if isinstance(opr, SingleQubitGate):
            code = MQ_applyTo(&self.system.data, &(<SingleQubitGate>opr).data, self.index)
            if code == MEMORYERROE:
                raise MemoryError("In method 'QubitIndex.apply', no adequate memory to be allocated, "
                                 f"{self.data.length * 16} bytes available memory size is needed")
        if autoNormalize:
            MQ_normalize(&self.system.data)

    def measure(QubitIndex self):
        if autoNormalize:
            MQ_normalize(&self.system.data)
        return <bint>MQ_measure(&self.system.data, self.index)

    def __str__(QubitIndex self):
        return f"Qubit{self.index}"

    def __repr__(QubitIndex self):
        return f"QubitIndex({self.index})"

############################  Default Objects  ################################

Options = _options()
TemporaryOptions = _temp_options()

# Single Qubit Gates
checkUnitGate = 0
I = SingleQubitGate(1., 0., 0., 1.)
(<SingleQubitGate>I).isUnit = 1
H = SingleQubitGate(M_SQRT1_2, M_SQRT1_2, M_SQRT1_2, -M_SQRT1_2)
(<SingleQubitGate>H).isUnit = 1
X = SingleQubitGate(0., 1., 1., 0.)
(<SingleQubitGate>X).isUnit = 1
Y = SingleQubitGate(0., -1.j, 1.j, 0.)
(<SingleQubitGate>Y).isUnit = 1
Z = SingleQubitGate(1., 0., 0., -1.)
(<SingleQubitGate>Z).isUnit = 1
S = SingleQubitGate(1., 0., 0., 1.j)
(<SingleQubitGate>S).isUnit = 1
T = SingleQubitGate(1., 0., 0., M_SQRT1_2 + 1j*M_SQRT1_2)
(<SingleQubitGate>T).isUnit = 1
checkUnitGate = 1
def Rx(float64 angle):
    global checkUnitGate
    cdef uint8 before_ = checkUnitGate
    checkUnitGate = 0
    cdef float64 half_angle = angle / 2.
    cdef float64 a = cos(half_angle)
    cdef complex128 b = -1j * sin(half_angle)
    cdef SingleQubitGate result = SingleQubitGate(a, b, b, a)
    result.isUnit = 1
    checkUnitGate = before_
    return result
def Ry(double angle):
    global checkUnitGate
    cdef uint8 before_ = checkUnitGate
    checkUnitGate = 0
    cdef float64 half_angle = angle / 2.
    cdef float64 a = cos(half_angle)
    cdef float64 b = sin(half_angle)
    cdef SingleQubitGate result = SingleQubitGate(a, -b, b, a)
    result.isUnit = 1
    checkUnitGate = before_
    return result
def Rz(double angle):
    global checkUnitGate
    cdef uint8 before_ = checkUnitGate
    checkUnitGate = 0
    cdef float64 half_angle = angle / 2.
    cdef float64 a = cos(half_angle)
    cdef complex128 b = 1j * sin(half_angle)
    cdef SingleQubitGate result = SingleQubitGate(a - b, 0., 0., a + b)
    result.isUnit = 1
    checkUnitGate = before_
    return result
def R1(double angle):
    global checkUnitGate
    cdef uint8 before_ = checkUnitGate
    checkUnitGate = 0
    cdef float64 a = cos(angle)
    cdef float64 b = sin(angle)
    cdef SingleQubitGate result = SingleQubitGate(1., 0., 0., a + 1j*b)
    result.isUnit = 1
    checkUnitGate = before_
    return result

# CNOT gate (syntactic sugar)
def CNOT(QubitIndex q0, QubitIndex q1):
    if q0.system != q1.system:
        raise TypeError("'q0' and 'q1' is not in the same system")
    q0.system.control(X, [q0.index], q1.index)

# apply operation to every qubit in system (syntactic sugar)
def ApplyToEach(SingleQubitOperation opr, MultiQubits qubits):
    global autoNormalize, checkQubitIdx
    cdef uint8 before0 = autoNormalize, before1 = checkQubitIdx
    autoNormalize = 0; checkQubitIdx = 0
    cdef uint8 index
    for index in range(qubits.nQubits):
        qubits.applyTo(opr, index)
    if before0:
        qubits.normalize()
    autoNormalize = before0; checkQubitIdx = before1

def MeasureAll(MultiQubits qubits):
    global autoNormalize, checkQubitIdx
    cdef uint8 before0 = autoNormalize, before1 = checkQubitIdx
    autoNormalize = 0; checkQubitIdx = 0
    cdef uint8 index
    cdef tuple result = PyTuple_New(qubits.nQubits)
    if before0:
        qubits.normalize()
    for index in range(qubits.nQubits):
        PyTuple_SET_ITEM(result, index, qubits.measure(index))
    autoNormalize = before0; checkQubitIdx = before1
    return result

# convert states format 'a+bi' to 'L*e^(ti)'
def convert_number(complex128 s):
    cdef float64 r = s.real, i = s.imag
    cdef float64 L = sqrt(r * r + i * i)
    cdef float64 theta = 0.
    if not floatEqual0(L):
        theta = acos(r / L)
    if i < 0:
        return (L, -theta)
    return (L, theta)

def convert_states(object states):
    return tuple(convert_number(s[0]) for s in states)

# simple get color on color wheel
def ColorWheel2RGB(float32 theta, bint is01):
    # https://en.wikipedia.org/wiki/HSL_and_HSV
    cdef float32 theta_ = <float32>fmod(theta, PI2)
    if theta < 0.:
        theta_ += <float32>PI2
    cdef float32 h_pi_3 = <float32>(3. * theta_ / M_PI)
    cdef float32 R = color_f(2, h_pi_3)
    cdef float32 G = color_f(0, h_pi_3)
    cdef float32 B = color_f(4, h_pi_3)
    if is01:
        return (R, G, B)
    else:
        return (<uint8>(R * 255), <uint8>(G * 255), <uint8>(B * 255))


###############################################################################
###################################  End  #####################################
###############################################################################
