.. TransientBVD master doc

============================================
TransientBVD — Transient Response Analysis
============================================

**TransientBVD** is a Python library for analyzing and optimizing the transient
response of ultrasound transducers (or other resonant systems) modeled by the
Butterworth-Van Dyke (BVD) equivalent circuit. It implements advanced methods
for both open-circuit (resistive damping) and closed-circuit (voltage overboost)
strategies, significantly reducing transient response times.

This library is developed at the
`Measurement and Sensor Technology Group, TU Darmstadt <https://www.etit.tu-darmstadt.de/must/home_must/index.en.jsp>`_
to support our ongoing research in rapid transient control for ultrasound transducers.
You can find the source code on our lab's GitHub:
`TUDA-MUST <https://github.com/TUDA-MUST/TransientBVD>`_.

Contents
--------
.. toctree::
   :maxdepth: 2

   usage
   reference
   examples

Research Paper
--------------
This repository and library support the research findings presented in:

"Rapid Transient Control Strategies for Ultrasound Transducers"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:Status: In Preparation

.. image:: https://img.shields.io/badge/DOI-10.1234%2Fexample-blue.svg
   :target: https://doi.org/10.1234/example
   :alt: DOI Badge


If you find **TransientBVD** helpful in your own research, please cite:

.. code-block:: bibtex

   @article{doersamSuppeltKupnik2024,
     title     = {Rapid Transient Control Strategies for Ultrasound Transducers},
     author    = {Dörsam, Jan Helge and Suppelt, Sven and Kupnik, Mario},
     journal   = {IEEE TRANSACTIONS ON ULTRASONICS, FERROELECTRICS, AND FREQUENCY CONTROL},
     year      = {2025},
     volume    = {??},
     number    = {??},
     pages     = {??-??},
     doi       = {10.1234/example},
   }

Acknowledgements
----------------
This work was supported through multiple grants and collaborations:

- **Carl Zeiss Stiftung** under the CZS Wildcard **SOPHIMA** project.
- **DFG** under **Grant No. 509096131**.
- **German Federal Ministry for Economic Affairs and Climate Action** under **Grant No. 03LB3029**.
- **European Union (Chips Joint Undertaking)** under **Grant No. 101096884** (Listen2Future*)

.. note::

   *For the Listen2Future project*:

   Views and opinions expressed are those of the author(s) and do not necessarily
   reflect those of the European Union or Chips Joint Undertaking. Neither the
   European Union nor the granting authority can be held responsible for them.
   The project is supported by the CHIPS JU and its members (including top-up
   funding by Austria, Belgium, Czech Republic, Germany, Netherlands, Norway,
   and Spain).



Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


