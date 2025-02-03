"""
TransientBVD - Transducer Model

This module defines the `Transducer` class, which represents an ultrasound
transducer with predefined parameters. The transducer stores electrical circuit
parameters and additional metadata such as the manufacturer and resonance frequency.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import Optional


@dataclass
class Transducer:
    """
    Represents an ultrasound transducer with predefined parameters.

    Attributes
    ----------
    rs : float
        Series resistance in ohms. Must be positive.
    ls : float
        Inductance in henries. Must be positive.
    cs : float
        Series capacitance in farads. Must be positive.
    c0 : float
        Parallel capacitance in farads. Must be positive.
    rp : Optional[float], default=None
        Parallel resistance in ohms. If provided, must be positive.
    name : str, default="Unknown"
        The name of the transducer.
    manufacturer : Optional[str], default=None
        Manufacturer information for the transducer.
    """

    rs: float
    ls: float
    cs: float
    c0: float
    rp: Optional[float] = None
    name: str = "Unknown"
    manufacturer: Optional[str] = None

    def __post_init__(self):
        """
        Validate parameters upon initialization.
        """
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """
        Ensure all electrical parameters are positive.

        Raises
        ------
        ValueError
            If any parameter is non-positive.
        """
        if self.rs <= 0:
            raise ValueError("Series resistance (rs) must be positive.")
        if self.ls <= 0:
            raise ValueError("Inductance (ls) must be positive.")
        if self.cs <= 0:
            raise ValueError("Series capacitance (cs) must be positive.")
        if self.c0 <= 0:
            raise ValueError("Parallel capacitance (c0) must be positive.")
        if self.rp is not None and self.rp <= 0:
            raise ValueError("Parallel resistance (rp) must be positive if provided.")

    @property
    def frequency(self) -> float:
        """
        Compute the resonance frequency dynamically.

        Returns
        -------
        float
            Resonance frequency in Hz.
        """
        return 1 / (2 * math.pi * (self.ls * self.cs) ** 0.5)

    def set_name(self, name: str) -> "Transducer":
        """
        Set the transducer's name.

        Parameters
        ----------
        name : str
            The name to assign to the transducer.

        Returns
        -------
        Transducer
            The updated transducer instance (supports method chaining).
        """
        self.name = name
        return self

    def set_manufacturer(self, manufacturer: str) -> "Transducer":
        """
        Set the manufacturer of the transducer.

        Parameters
        ----------
        manufacturer : str
            The manufacturer name.

        Returns
        -------
        Transducer
            The updated transducer instance (supports method chaining).
        """
        self.manufacturer = manufacturer
        return self

    def set_rp(self, rp: float) -> "Transducer":
        """
        Set the parallel resistance (`rp`) value.

        Parameters
        ----------
        rp : float
            Parallel resistance in ohms. Must be positive.

        Returns
        -------
        Transducer
            The updated transducer instance (supports method chaining).

        Raises
        ------
        ValueError
            If `rp` is not positive.
        """
        if rp <= 0:
            raise ValueError("Parallel resistance (rp) must be positive.")
        self.rp = rp
        return self

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the transducer.

        Returns
        -------
        str
            A formatted string with transducer details.
        """
        return (
            f"Transducer: {self.name}\n"
            f"Manufacturer: {self.manufacturer or 'Unknown'}\n"
            f"Rs={self.rs:.4f} Ω, Ls={self.ls:.6f} H, Cs={self.cs:.2e} F, C0={self.c0:.2e} F\n"
            f"Resonance Frequency: {self.frequency:.2f} Hz\n"
            f"Parallel Resistance (Rp): {self.rp if self.rp else 'None'} Ω"
        )


# Default path to the JSON file containing pre-measured transducers
DEFAULT_JSON_FILE_PATH = Path(__file__).parent / "data" / "transducers.json"


def load_transducers(json_file: str = str(DEFAULT_JSON_FILE_PATH)) -> Dict[str, Transducer]:
    """
    Load transducer data from a JSON file and create Transducer objects.

    Parameters
    ----------
    json_file : str, optional
        Path to the JSON file containing transducer data.
        Defaults to the predefined transducer data file.

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
            rs=params["rs"],
            ls=params["ls"],
            cs=params["cs"],
            c0=params["c0"],
            rp=params.get("rp")
        ).set_name(name).set_manufacturer(params.get("manufacturer", "Unknown"))
        for name, params in data.items()
    }


def load_measured_transducers(json_file: str = str(DEFAULT_JSON_FILE_PATH)) -> Dict[
    str, Transducer]:
    """
    Load and return the dictionary of predefined transducers from a JSON file.

    Parameters
    ----------
    json_file : str, optional
        Path to the JSON file containing transducer data.
        Defaults to the predefined transducer data file.

    Returns
    -------
    Dict[str, Transducer]
        A dictionary of predefined transducer objects.
    """
    return load_transducers(json_file)


def select_transducer(name: str, json_file: str = str(DEFAULT_JSON_FILE_PATH)) -> Transducer:
    """
    Retrieve a predefined transducer by its name.

    Parameters
    ----------
    name : str
        Name of the transducer to retrieve.
    json_file : str, optional
        Path to the JSON file containing transducer data.
        Defaults to the predefined transducer data file.

    Returns
    -------
    Transducer
        The Transducer object corresponding to the given name.

    Raises
    ------
    ValueError
        If the specified transducer name does not exist.
    """
    measured_transducers = load_measured_transducers(json_file)

    if name not in measured_transducers:
        available = ", ".join(measured_transducers.keys())
        raise ValueError(f"Transducer '{name}' not found. Available transducers: {available}")

    return measured_transducers[name]


def predefined_transducers(json_file: str = str(DEFAULT_JSON_FILE_PATH)) -> Dict[str, Transducer]:
    """
    Get a dictionary of all predefined transducers.

    Parameters
    ----------
    json_file : str, optional
        Path to the JSON file containing transducer data.
        Defaults to the predefined transducer data file.

    Returns
    -------
    Dict[str, Transducer]
        A dictionary mapping transducer names to Transducer objects.
    """
    return load_measured_transducers(json_file)
