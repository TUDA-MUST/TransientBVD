"""
TransientBVD - Transducer Model

This module defines the `Transducer` class, which represents an ultrasound
transducer with predefined parameters. The transducer internally uses the
`EquivalentCircuitParams` class to store electrical circuit parameters.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .utils import resonance_frequency


@dataclass
class EquivalentCircuitParams:
    """
    Represents the parameters of a Butterworth-Van Dyke (BVD) equivalent circuit.

    Attributes
    ----------
    rs : float
        Series resistance in ohms.
    ls : float
        Inductance in henries.
    cs : float
        Series capacitance in farads.
    c0 : float
        Parallel capacitance in farads.
    rp : float, optional
        Parallel resistance in ohms (default: None, meaning no parallel resistance).
    """

    rs: float
    ls: float
    cs: float
    c0: float
    rp: Optional[float] = None  # Optional parallel resistance

    def __repr__(self) -> str:
        """
        Returns a formal string representation of the object, useful for debugging.

        Returns
        -------
        str
            A detailed string representation of the circuit parameters.
        """
        return (f"EquivalentCircuitParams(rs={self.rs}, ls={self.ls}, cs={self.cs}, "
                f"c0={self.c0}, rp={self.rp})")

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of the circuit parameters.

        Returns
        -------
        str
            A readable summary of the equivalent circuit parameters.
        """
        return (f"Equivalent Circuit Parameters:\n"
                f"  - Series Resistance (Rs): {self.rs:.2f} Ω\n"
                f"  - Inductance (Ls): {self.ls:.6e} H\n"
                f"  - Series Capacitance (Cs): {self.cs:.6e} F\n"
                f"  - Parallel Capacitance (C0): {self.c0:.6e} F\n"
                f"  - Parallel Resistance (Rp): {self.rp if self.rp else 'None'} Ω")

    def pretty_print(self) -> None:
        """
        Prints the circuit parameters in a well-formatted way.
        """
        print("=" * 50)
        print(" Butterworth-Van Dyke Equivalent Circuit ")
        print("=" * 50)
        print(f"Series Resistance (Rs): {self.rs:.2f} Ω")
        print(f"Inductance (Ls): {self.ls:.6e} H")
        print(f"Series Capacitance (Cs): {self.cs:.6e} F")
        print(f"Parallel Capacitance (C0): {self.c0:.6e} F")
        print(f"Parallel Resistance (Rp): {self.rp if self.rp else 'None'} Ω")
        print("=" * 50)


@dataclass
class Transducer(EquivalentCircuitParams):
    """
    Represents an ultrasound transducer with predefined parameters.

    Inherits from EquivalentCircuitParams, allowing direct access to all
    electrical circuit parameters while also storing metadata such as
    the transducer's name, manufacturer, and resonance frequency.

    Attributes
    ----------
    name : str
        The name of the transducer.
    manufacturer : Optional[str]
        Manufacturer information for the transducer.
    frequency : float
        Resonance frequency of the transducer, calculated upon initialization.
    """

    name: Optional[str] = "Unknown"
    manufacturer: Optional[str] = None
    frequency: float = field(init=False)  # Calculated after initialization

    def __post_init__(self):
        """
        Calculate the resonance frequency of the transducer after initialization.
        This ensures the `frequency` attribute is always available.
        """
        self.frequency = resonance_frequency(self.rs, self.ls, self.cs, self.c0)

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the transducer.
        """
        return (
            f"Transducer: {self.name}\n"
            f"Manufacturer: {self.manufacturer or 'Unknown'}\n"
            f"{super().__str__()}\n"
            f"Resonance Frequency: {self.frequency:.2f} Hz"
        )

    @classmethod
    def from_parameters(
        cls,
        name: str,
        rs: float,
        ls: float,
        cs: float,
        c0: float,
        rp: Optional[float] = None,
        manufacturer: Optional[str] = None
    ) -> "Transducer":
        """
        Create a `Transducer` instance directly from circuit parameters.

        Parameters
        ----------
        name : str
            Name of the transducer.
        rs : float
            Series resistance in ohms.
        ls : float
            Inductance in henries.
        cs : float
            Series capacitance in farads.
        c0 : float
            Parallel capacitance in farads.
        rp : Optional[float], default=None
            Parallel resistance in ohms.
        manufacturer : Optional[str], default=None
            Manufacturer information.

        Returns
        -------
        Transducer
            A `Transducer` instance with the specified parameters.
        """
        return cls(name=name, rs=rs, ls=ls, cs=cs, c0=c0, rp=rp, manufacturer=manufacturer)


def load_transducers(json_file: str) -> Dict[str, Transducer]:
    """
    Load transducer data from a JSON file and create Transducer objects.

    Parameters
    ----------
    json_file : str
        Path to the JSON file containing transducer data.

    Returns
    -------
    Dict[str, Transducer]
        A dictionary of Transducer objects, keyed by their names.

    Raises
    ------
    FileNotFoundError
        If the specified JSON file does not exist.
    JSONDecodeError
        If the JSON file is malformed.
    """
    json_path = Path(json_file)
    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)  # Load data from JSON file

    # Create Transducer objects from loaded data
    return {
        name: Transducer(
            name=name,
            manufacturer=params.get("manufacturer"),
            circuit_params=EquivalentCircuitParams(
                rs=params["rs"],
                ls=params["ls"],
                cs=params["cs"],
                c0=params["c0"],
                rp=params.get("rp")  # Ensure optional rp
            )
        )
        for name, params in data.items()
    }


# Path to the JSON file containing pre-measured transducers
_json_file_path = Path(__file__).parent / "data" / "transducers.json"

# Internal dictionary for managing measured transducers
_measured_transducers: Optional[Dict[str, Transducer]] = None


def _load_transducers():
    """
    Lazily load the transducer data into `_measured_transducers` if not already loaded.
    """
    global _measured_transducers
    if _measured_transducers is None:
        _measured_transducers = load_transducers(str(_json_file_path))


def predefined_transducer(name: str) -> Transducer:
    """
    Retrieve a predefined transducer by its name.

    Parameters
    ----------
    name : str
        Name of the transducer to retrieve.

    Returns
    -------
    Transducer
        The Transducer object corresponding to the given name.

    Raises
    ------
    ValueError
        If the specified transducer name does not exist.
    """
    _load_transducers()  # Ensure transducers are loaded
    if name not in _measured_transducers:
        available = ", ".join(_measured_transducers.keys())
        raise ValueError(f"Transducer '{name}' not found. Available transducers: {available}")
    return _measured_transducers[name]


def predefined_transducers() -> List[str]:
    """
    Get a list of all predefined transducer names, sorted alphabetically.

    Returns
    -------
    List[str]
        A sorted list of available transducer names.
    """
    _load_transducers()  # Ensure transducers are loaded
    return sorted(_measured_transducers.keys())