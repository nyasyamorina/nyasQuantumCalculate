from typing import Tuple

from .cy.nyasQC import Options, Qubits, TempOption, TemporaryOptions, QuantumObject, \
    Qubit, QuantumOperation, SingleQubitOperation, SingleQubit, \
    SingleQubitGate, MultiQubits, QubitIndex


__all__ = ["Options", "QuantumObject", "Qubit", "QuantumOperation", "SingleQubitOperation",
           "SingleQubit", "SingleQubitGate", "MultiQubits", "QubitIndex", "M",
           "TempOption", "TemporaryOptions", "Reset", "MeasureAll", "Qubits",
           "ResetAll"]


def M(qubit: Qubit) -> bool:
    """ Measure a qubit and return result
    see 'SingleQubit.measure()' or 'QubitIndex.measure()' """
    return qubit.measure()


def Reset(qubit: Qubit) -> None:
    qubit.reset()


def MeasureAll(qubits: Qubits) -> Tuple[bool]:
    return qubits.measureAll()


def ResetAll(qubits: Qubits) -> None:
    qubits.resetAll()
