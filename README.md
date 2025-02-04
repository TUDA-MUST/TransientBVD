# TransientBVD
[![PyPI](https://img.shields.io/pypi/v/transientbvd.svg?style=flat-square)](https://pypi.python.org/pypi/transientbvd)
[![Documentation Status](https://readthedocs.org/projects/transientbvd/badge/?version=latest&style=flat-square)](https://transientbvd.readthedocs.io/en/latest/)
![Tests](https://github.com/TUDA-MUST/TransientBVD/actions/workflows/tests.yml/badge.svg)
![Pylint](https://github.com/TUDA-MUST/TransientBVD/actions/workflows/pylint.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.1234%2Fexample-blue.svg?style=flat-square)](https://doi.org/10.1234/example)

**TransientBVD** is a Python library for analyzing and optimizing the transient response of ultrasound transducers (or other resonant systems) modeled by the Butterworth-Van Dyke (BVD) equivalent circuit. It implements advanced methods for both open-circuit (resistive damping) and closed-circuit (voltage overboost) strategies, significantly reducing transient response times.

## Features

- **Open-circuit damping**: Quickly compute an optimal parallel resistor \(R_p\) to minimize open-circuit transient response times.
- **Closed-circuit overboost**: Determine switching strategies (e.g. voltage amplitude changes) to reduce closed-circuit transient response times.
- **Comprehensive analysis**: Includes handy methods like `print_open_potential` and `print_closed_potential` for quick insights.
- **Transducer utility**: Load already measured example transducers or define your own BVD parameters.
- **Integration**: Based on Python (NumPy, SciPy, Sympy) for symbolic and numeric calculations.

## Documentation

For detailed usage instructions, examples, and API references, visit the 
[**TransientBVD Documentation**](https://transientbvd.readthedocs.io/en/latest/).

## Research Context

Developed at the 
[Measurement and Sensor Technology Group, TU Darmstadt](https://www.etit.tu-darmstadt.de/must/home_must/index.en.jsp),
this library supports the research findings presented in:

> **"Rapid Transient Control Strategies for Ultrasound Transducers"**
> 
> Status: In Preparation

If you find **TransientBVD** helpful in your academic work, please cite:

```bibtex
@article{doersamTransientBVD2025,
  title     = {Rapid Transient Control Strategies for Ultrasound Transducers},
  author    = {Dörsam, Jan H. and Suppelt, Sven and Kleber, Carsten and Altmann, Alexander A. and Schmitt, Daniel and Schmitt, Toni and Haugwitz, Christoph and Soennecken, Soeren and Wismath, Sonja and Harth, Anne and Heyl, Christoph and Kupnik, Mario},
  journal   = {IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control},
  year      = {2025},
  volume    = {??},
  number    = {??},
  pages     = {??-??},
  doi       = {10.1234/example},
}
```

## Acknowledgements
 
This work was supported through multiple grants and collaborations:
 
- **Carl Zeiss Stiftung** under the CZS Wildcard **SOPHIMA** project
- **DFG** under Grant No. 509096131
- **German Federal Ministry for Economic Affairs and Climate Action** under Grant No. 03LB3029
- **Listen2Future*** is co-funded by the European Union (Chips Joint Undertaking) under **Grant No. 101096884**.

> *Views and opinions expressed are those of the author(s) only and do not necessarily reflect 
> those of the European Union or Chips Joint Undertaking. Neither the European Union nor the 
> granting authority can be held responsible for them. The project is supported by the CHIPS JU and its members 
> (including top-up funding by Austria, Belgium, Czech Republic, Germany, Netherlands, Norway, and Spain).
