Usage & Quickstart
==================

Installation
------------
Install via pip:

.. code-block:: bash

   pip install transientbvd


Basic Example
-------------
Deactivation potential analysis (damping via parallel resistor sweep):

.. code-block:: python

   import transientbvd as tbvd
   from transientbvd import Transducer

   transducer = Transducer(
       rs=24.764,
       ls=38.959e-3,
       cs=400.33e-12,
       c0=3970.1e-12,
   ).set_name("Example")

   tbvd.print_deactivation_potential(transducer, resistance_range=(10, 5000))


Activation potential (overboost):
---------------------------------
.. code-block:: python

   import transientbvd as tbvd
   from transientbvd import Transducer

   transducer = Transducer(
       rs=24.764,
       ls=38.959e-3,
       cs=400.33e-12,
       c0=3970.1e-12,
   ).set_name("Example")

   tbvd.print_activation_potential(transducer, ucw=40.0, ub=60.0)


Using predefined transducers
----------------------------
.. code-block:: python

   from transientbvd import predefined_transducers, select_transducer

   # list available names
   for name in predefined_transducers().keys():
       print(name)

   # pick one
   t = select_transducer("SMBLTD45F40H_1")
   print(t)


See :doc:`reference` for full API details.
