try:
    from .cy.nyasQC import Options, TempOption, TemporaryOptions, QuantumObject, \
        Qubit, QuantumOperation, SingleQubitOperation, SingleQubit, \
        SingleQubitGate, MultiQubits, QubitIndex, MeasureAll


except ModuleNotFoundError:
    import pyximport
    pyximport.install(build_dir="./", build_in_temp=False,
                      inplace=True, language_level=3)

    from .cy.nyasQC import Options, TempOption, TemporaryOptions, QuantumObject, \
        Qubit, QuantumOperation, SingleQubitOperation, SingleQubit, \
        SingleQubitGate, MultiQubits, QubitIndex, MeasureAll


__all__ = ["Options", "QuantumObject", "Qubit", "QuantumOperation", "SingleQubitOperation",
           "SingleQubit", "SingleQubitGate", "MultiQubits", "QubitIndex", "M", "MeasureAll",
           "TempOption", "TemporaryOptions", "Reset"]


def M(qubit: Qubit) -> bool:
    """ Measure a qubit and return result
    see 'SingleQubit.measure()' or 'QubitIndex.measure()' """
    return qubit.measure()


def Reset(qubit: SingleQubit) -> None:
    qubit.reset()
