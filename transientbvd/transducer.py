"""
TransientBVD - Transducer Model

This module defines the `Transducer` class, which represents an ultrasound
transducer with predefined parameters. The transducer stores electrical circuit
parameters and additional metadata such as the manufacturer and resonance frequency.
"""

import json
import math
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Dict, Optional, Any, Mapping, Union


@dataclass
class Transducer:
    """
    Represents an ultrasound transducer described by a BVD equivalent circuit.

    Parameters
    ----------
    rs : float
        Series resistance in ohms. Must be positive.
    ls : float
        Inductance in henries. Must be positive.
    cs : float
        Series capacitance in farads. Must be positive.
    c0 : float
        Parallel capacitance in farads. Must be positive.
    rp : Optional[float], optional
        Parallel resistance in ohms. If provided, must be positive.
    name : str, optional
        Human-readable transducer name.
    manufacturer : Optional[str], optional
        Manufacturer name.
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


# Environment variable that can override the transducer database location
TRANSDUCERS_ENV_VAR = "TRANSIENTBVD_TRANSDUCERS_JSON"

# Relative path inside the package for the bundled default database
DEFAULT_TRANSDUCERS_RESOURCE = "data/transducers.json"


JsonPath = Union[str, Path]


def _load_transducer_db_json(json_file: Optional[JsonPath] = None) -> Mapping[str, Any]:
    """
    Load the transducer database JSON using a clean precedence order:

    1) Explicit `json_file` argument (path on disk)
    2) Environment variable TRANSIENTBVD_TRANSDUCERS_JSON (path on disk)
    3) Bundled default resource inside the installed package

    This works for normal installs and wheels because it uses importlib.resources
    for the bundled default.
    """
    # 1) explicit path wins
    if json_file is not None:
        json_path = Path(json_file)
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # 2) environment override
    env_path = os.environ.get(TRANSDUCERS_ENV_VAR)
    if env_path:
        json_path = Path(env_path)
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # 3) bundled default (package data)
    # Note: resources.files(...) is available in Python 3.9+
    resource = resources.files("transientbvd").joinpath(DEFAULT_TRANSDUCERS_RESOURCE)
    with resource.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_transducers(json_file: Optional[JsonPath] = None) -> Dict[str, Transducer]:
    """
    Load transducer data and create Transducer objects.

    Parameters
    ----------
    json_file : Optional[Union[str, Path]]
        Path to a JSON file. If None:
        - will try env var TRANSIENTBVD_TRANSDUCERS_JSON
        - otherwise loads the bundled default database.

    Returns
    -------
    Dict[str, Transducer]
        Dictionary keyed by transducer name.
    """
    data = _load_transducer_db_json(json_file=json_file)

    transducers: Dict[str, Transducer] = {}
    for name, params in data.items():
        t = (
            Transducer(
                rs=float(params["rs"]),
                ls=float(params["ls"]),
                cs=float(params["cs"]),
                c0=float(params["c0"]),
                rp=float(params["rp"]) if params.get("rp") is not None else None,
            )
            .set_name(str(name))
            .set_manufacturer(params.get("manufacturer", "Unknown"))
        )
        transducers[str(name)] = t

    return transducers


def load_measured_transducers(
    json_file: Optional[JsonPath] = None,
) -> Dict[str, Transducer]:
    """
    Backwards-compatible alias for load_transducers().
    """
    return load_transducers(json_file=json_file)


def select_transducer(name: str, json_file: Optional[JsonPath] = None) -> Transducer:
    """
    Retrieve a predefined transducer by its name.

    Parameters
    ----------
    name : str
        Name of the transducer to retrieve.
    json_file : Optional[Union[str, Path]]
        Optional JSON database path override.

    Raises
    ------
    ValueError
        If the transducer name does not exist.
    """
    measured_transducers = load_measured_transducers(json_file=json_file)

    if name not in measured_transducers:
        available = ", ".join(measured_transducers.keys())
        raise ValueError(
            f"Transducer '{name}' not found. Available transducers: {available}"
        )

    return measured_transducers[name]


def predefined_transducers(
    json_file: Optional[JsonPath] = None,
) -> Dict[str, Transducer]:
    """
    Get a dictionary of all predefined transducers.

    Parameters
    ----------
    json_file : Optional[Union[str, Path]]
        Optional JSON database path override.

    Returns
    -------
    Dict[str, Transducer]
        Dictionary mapping transducer names to Transducer objects.
    """
    return load_measured_transducers(json_file=json_file)
