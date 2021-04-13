from nyasQuantumCalculate import *

qbsys = QubitsSystem(3)
q0 = qbsys[0]
q1 = qbsys[1]
q2 = qbsys[2]

Builtin.H(q0)
Builtin.H(q1)
Builtin.CCNOT(q0, q1, q2)
DumpSystemText(qbsys)

Builtin.H(q2)
Builtin.CNOT(q1, q2)
Builtin.S(q2)
Builtin.T(q2)
Builtin.CNOT(q0, q2)
Builtin.T(q2)
Builtin.CNOT(q1, q2)
Builtin.S(q2)
Builtin.T(q2)
Builtin.CNOT(q0, q2)
Builtin.T(q2)
Builtin.H(q2)
Builtin.T(q1)
Builtin.CNOT(q0, q1)
Builtin.T(q0)
Builtin.S(q1)
Builtin.T(q1)
Builtin.CNOT(q0, q1)
DumpSystemText(qbsys)

Builtin.RA(qbsys.getQubits())
