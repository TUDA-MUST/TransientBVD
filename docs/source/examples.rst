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

Deactivation Time Example
-------------------------------
Shows how to compute deactivation time (τ) in different conditions for deactivation.

.. literalinclude:: ../../examples/deactivation_time_example.py
   :language: python
   :linenos:

Deactivation Time Over Rp Example
----------------------------------------
Explores how deactivation time changes over various parallel resistance values (Rp)
in the deactivation scenario.

.. literalinclude:: ../../examples/deactivation_time_over_rp_example.py
   :language: python
   :linenos:

Optimum Resistance Example
--------------------------
Uses the library’s optimization routine to find the best Rp for minimal deactivation time.

.. literalinclude:: ../../examples/optimum_resistance_example.py
   :language: python
   :linenos:

Plot Activation Current Example
-------------------------------
Plots the transient current response under an activation scenario with overboost.

.. literalinclude:: ../../examples/activation_current_plot_example.py
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
