from .cy.nyasQC import I, H, X, Y, Z, S, T, Rx, Ry, Rz, R1, CNOT, Qubits, \
    SingleQubitOperation, Control


__all__ = ["I", "H", "X", "Y", "Z", "S", "T", "Rx", "Ry", "Rz", "R1", "CNOT",
           "ApplyToEach", "Control"]


def ApplyToEach(opr: SingleQubitOperation, qubits: Qubits):
    qubits.applyToEach(opr)
