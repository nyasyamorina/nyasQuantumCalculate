from typing import Union, Tuple, List
from math import log10

have_matplotlib: bool = True
try:
    from matplotlib import pyplot as plt
except ModuleNotFoundError:
    have_matplotlib = False

from .cy.nyasQC import convert_number, convert_states, ColorWheel2RGB, \
        SingleQubit, MultiQubits


__all__ = ["convert_number", "convert_states", "have_matplotlib",
           "ColorWheel2RGB", "DumpMachineText", "DumpMachineFig"]


log10_2: float = log10(2.)

def DumpMachineText(sys: Union[SingleQubit, MultiQubits]) -> None:
    states: Tuple[Tuple[complex], ...] = sys.states
    if isinstance(sys, SingleQubit):
        print("# states in 1 qubit system")
        format_str: str = "{:01}"
        length: int = 20
    else:
        print(f"# states in {sys.nQubits} qubits system")
        idx_length: int = 1 + int(sys.nQubits * log10_2)
        format_str: str = '{' + f":0{idx_length}" + '}'
        length: int = 21 - idx_length
    for i in range(len(states)):
        a_b: Tuple[float, float] = (states[i][0].real, states[i][0].imag)
        L_theta: Tuple[float, float] = convert_number(states[i][0])
        prob: float = L_theta[0] * L_theta[0]
        bar_length: int = int(prob * length)
        if a_b[1] >= 0.:
            print('∣' + format_str.format(i) + f"❭  [{a_b[0]: .4f} + {a_b[1]:.4f}i]  |{'='*bar_length}"
                  f"{' '*(length-bar_length)}|  [prob: {prob:.4f}] [rad:{L_theta[1]: .4f}]")
        else:
            print('∣' + format_str.format(i) + f"❭  [{a_b[0]: .4f} - {-a_b[1]:.4f}i]  |{'='*bar_length}"
                  f"{' '*(length-bar_length)}|  [prob: {prob:.4f}] [rad:{L_theta[1]: .4f}]")
    print()


def DumpMachineFig(sys: Union[SingleQubit, MultiQubits], block: bool = True) -> None:
    if not have_matplotlib:
        raise ModuleNotFoundError("No module named 'matplotlib'")
    L, theta = zip(*convert_states(sys.states))
    range_ = range(len(L))
    if isinstance(sys, SingleQubit):
        lables: List[str] = ["∣0❭", "∣1❭"]
    else:
        idx_length: int = 1 + int(sys.nQubits * log10_2)
        format_str: str = "∣{" + f":0{idx_length}" + "}❭"
        lables: List[str] = [format_str.format(i) for i in range(len(L))]
    prob: List[float] = [l*l for l in L]
    color: List[str] = ["#{:02X}{:02X}{:02x}".format(*ColorWheel2RGB(t, False)) for t in theta]
    plt.clf()
    plt.xticks(range_, lables, size=6, rotation="vertical", fontfamily="monospace")
    plt.ylim(0., 1.1)
    plt.ylabel("Probability")
    plt.bar(range_, prob, color=color, ec="#000000", ls='-', lw=0.75)
    plt.show(block=block)
