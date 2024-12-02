import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .utils import resonance_frequency


@dataclass
class Transducer:
    """
    Represents a transducer with predefined parameters for testing or simulation.

    Attributes
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
    manufacturer : Optional[str]
        Manufacturer information for the transducer.
    frequency : float
        Resonance frequency of the transducer, calculated upon initialization.
    """
    name: str
    rs: float
    ls: float
    cs: float
    c0: float
    manufacturer: Optional[str] = None
    frequency: float = field(init=False)  # Calculated after initialization

    def __str__(self) -> str:
        """
        Provide a human-readable string representation of the transducer.
        """
        details = (
            f"Transducer: {self.name}\n"
            f"Manufacturer: {self.manufacturer or 'Unknown'}\n"
            f"Parameters (rs, ls, cs, c0): ({self.rs:.4f} Ω, {self.ls:.6f} H, "
            f"{self.cs:.2e} F, {self.c0:.2e} F)\n"
            f"Resonance Frequency: {self.frequency:.2f} Hz"
        )
        return details

    def __post_init__(self):
        """
        Calculate the resonance frequency of the transducer after initialization.
        This ensures the `frequency` attribute is always available.
        """
        self.frequency = resonance_frequency(self.rs, self.ls, self.cs, self.c0)

    def parameters(self) -> tuple:
        """
        Retrieve the core electrical parameters of the transducer.

        Returns
        -------
        tuple
            A tuple of (rs, ls, cs, c0) representing the transducer's electrical parameters.
        """
        return self.rs, self.ls, self.cs, self.c0


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
    return {name: Transducer(**params) for name, params in data.items()}


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
    Get a list of all predefined transducer names.

    Returns
    -------
    List[str]
        A list of available transducer names.
    """
    _load_transducers()  # Ensure transducers are loaded
    return list(_measured_transducers.keys())
