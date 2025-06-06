# TransientBVD
[![PyPI](https://img.shields.io/pypi/v/transientbvd.svg?style=flat-square)](https://pypi.python.org/pypi/transientbvd)
[![Documentation Status](https://readthedocs.org/projects/transientbvd/badge/?version=latest&style=flat-square)](https://transientbvd.readthedocs.io/en/latest/)
![Tests](https://github.com/TUDA-MUST/TransientBVD/actions/workflows/tests.yml/badge.svg)
![Pylint](https://github.com/TUDA-MUST/TransientBVD/actions/workflows/pylint.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.1234%2Fexample-blue.svg?style=flat-square)](https://doi.org/10.1234/example)

**TransientBVD** is a Python library for analyzing and optimizing the transient response of ultrasound transducers (or other resonant systems) modeled by the Butterworth-Van Dyke (BVD) equivalent circuit. It implements advanced methods for both **deactivation** (resistive damping) and **activation** (voltage overboost) strategies, significantly reducing transient response times.

## Features

- **Deactivation damping**: Quickly compute an optimal parallel resistor \(R_p\) to minimize deactivation transient response times.
- **Activation overboost**: Determine switching strategies (e.g. voltage amplitude changes) to reduce activation transient response times.
- **Comprehensive analysis**: Includes handy methods like `print_deactivation_potential` and `print_activation_potential` for quick insights.
- **Transducer utility**: Load already measured example transducers or define your own BVD parameters.
- **Integration**: Built on Python (NumPy, SciPy, Sympy) for both symbolic and numeric calculations.

## Documentation

For detailed usage instructions, examples, and API references, visit the 
[**TransientBVD Documentation**](https://transientbvd.readthedocs.io/en/latest/).

## Research Context

Developed at the 
[Measurement and Sensor Technology Group, TU Darmstadt](https://www.etit.tu-darmstadt.de/must/home_must/index.en.jsp),
this library supports the research findings presented in:

> **"Rapid Transient Control Strategies for Ultrasound Transducers"**
> 
> Status: Submitted
> DOI: [10.1234/example](https://doi.org/10.1234/example)  *(Link to be updated upon publication)*


If you find **TransientBVD** helpful in your academic work, please cite:

```bibtex
@article{doersamTransientBVD2025,
  title     = {Rapid Transient Control Strategies for Ultrasound Transducers},
  author    = {Dörsam, Jan H. and Suppelt, Sven and Kleber, Carsten and Altmann, Alexander A. and Schrödel, Yannick and Schmitt, Daniel and Schmitt, Toni and Haugwitz, Christoph and Wismath, Sonja and Soennecken, Sören and Heyl, Christoph M. and Kupnik, Mario},
  journal   = {IEEE Transactions on Ultrasonics, Ferroelectrics, and Frequency Control},
  year      = {2025},
  volume    = {??},
  number    = {??},
  pages     = {??-??},
  doi       = {10.1234/example},
}
