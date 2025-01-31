Examples
========

Below are various example scripts from the ``TransientBVD/examples`` directory,
demonstrating how to use TransientBVD in different scenarios. Each snippet is
embedded here for convenient reference.


Basic Example
-------------
A minimal script showing how to import TransientBVD and call a simple method.

.. literalinclude:: ../../examples/basic_example.py
   :language: python
   :linenos:

Basic Predefined Transducer Example
-----------------------------------
Demonstrates creating a predefined transducer object and using library methods.

.. literalinclude:: ../../examples/basic_predefined_transducer_example.py
   :language: python
   :linenos:

Decay Time Example
------------------
Shows how to compute decay time (τ) in different conditions.

.. literalinclude:: ../../examples/decay_time_example.py
   :language: python
   :linenos:

Decay Time Over Rp Example
--------------------------
Explores how decay time changes over various parallel resistance values (Rp).

.. literalinclude:: ../../examples/decay_time_over_rp_example.py
   :language: python
   :linenos:

Optimum Resistance Example
--------------------------
Uses the library’s optimization routine to find the best Rp for minimal decay.

.. literalinclude:: ../../examples/optimum_resistance_example.py
   :language: python
   :linenos:

Plot Closed Current Example
---------------------------
Plots the transient current response under a closed-circuit with overboost.

.. literalinclude:: ../../examples/plot_closed_current_example.py
   :language: python
   :linenos:

Regular Decay Example
---------------------
Illustrates “regular” or default decay behavior without special damping or overboost.

.. literalinclude:: ../../examples/regular_decay_example.py
   :language: python
   :linenos:

Results Saving Example
----------------------
Showcases how to capture and save computation results (e.g., to CSV or JSON).

.. literalinclude:: ../../examples/results_saving_example.py
   :language: python
   :linenos: