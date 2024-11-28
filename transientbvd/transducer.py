from typing import Dict, Optional, List, Tuple


class Transducer:
    """
    A class representing a transducer with predefined parameters for quick testing.
    All measurements are in SI units and done with a network analyzer
    (Vector Network Analyzer E5061B, Keysight, Santa Rosa, CA, USA).

    Parameters
    ----------
    name : str
        The name of the transducer.
    rs : float
        Series resistance in ohms.
    ls : float
        Inductance in henries.
    cs : float
        Series capacitance in farads.
    c0 : float
        Parallel capacitance in farads.
    manufacturer : Optional[str], default=None
        The manufacturer of the transducer.
    frequency : Optional[float], default=None
        The operational frequency of the transducer in Hz.
    """
    def __init__(
        self,
        name: str,
        rs: float,
        ls: float,
        cs: float,
        c0: float,
        manufacturer: Optional[str] = None,
        frequency: Optional[float] = None,
    ):
        self.name = name
        self.rs = rs
        self.ls = ls
        self.cs = cs
        self.c0 = c0
        self.manufacturer = manufacturer
        self.frequency = frequency

    def parameters(self) -> Tuple[float, float, float, float]:
        """
        Retrieve the core parameters of the transducer.

        Returns
        -------
        Tuple[float, float, float, float]
            The parameters (rs, ls, cs, c0) in correct order.
        """
        return self.rs, self.ls, self.cs, self.c0

    def __repr__(self):
        info = (
            f"Transducer(name='{self.name}', rs={self.rs}, ls={self.ls}, "
            f"cs={self.cs}, c0={self.c0}"
        )
        if self.manufacturer:
            info += f", manufacturer='{self.manufacturer}'"
        if self.frequency:
            info += f", frequency={self.frequency} Hz"
        info += ")"
        return info

    def __str__(self):
        info = f"Transducer '{self.name}'"
        if self.manufacturer:
            info += f" by {self.manufacturer}"
        if self.frequency:
            info += f" at {self.frequency} Hz"
        return info


# Dictionary of pre-measured transducers
measured_transducers: Dict[str, Transducer] = {
    "SMBLTD45F40H": Transducer(
        name="SMBLTD45F40H", rs=24.764, ls=38.959e-3, cs=400.33e-12, c0=3970.1e-12,
        manufacturer="STEINER & MARTINS INC., Davenport, USA", frequency=40.000
    ),
    "MA40S4S": Transducer(
        name="MA40S4S", rs=6.43186339335e+002, ls=6.88719499245e-002, cs=2.30489066295e-010, c0=2.40188114400e-009,
        manufacturer="Murata, Nagaokakyō, Japan", frequency=40.000
    ),
}


def predefined_transducer(name: str) -> Transducer:
    """
    Retrieve a predefined transducer by name.

    Parameters
    ----------
    name : str
        The name of the transducer.

    Returns
    -------
    Transducer
        The matching Transducer object.

    Raises
    ------
    ValueError
        If the transducer name is not found in the predefined list.

    Notes
    -----
    Transducers are retrieved from a predefined list of measured transducer parameters.
    """
    if name not in measured_transducers:
        available_names = ", ".join(measured_transducers.keys())
        raise ValueError(
            f"Transducer '{name}' not found. Available transducers: {available_names}"
        )
    return measured_transducers[name]


def predefined_transducers() -> List[str]:
    """
    List the names of all predefined transducers.

    Returns
    -------
    List[str]
        A list of transducer names.
    """
    return list(measured_transducers.keys())
