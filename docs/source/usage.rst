Usage & Quickstart
==================

Installation
------------
Use Poetry or pip. Example (pip):

.. code-block:: bash

   pip install transientbvd


Basic Example
-------------
Using open-circuit potential analysis:

.. code-block:: python

   import transientbvd as tbvd

   tbvd.print_open_potential(
       rs=24.764,
       ls=38.959e-3,
       cs=400.33e-12,
       c0=3970.1e-12
   )

Closed-circuit potential with overboost:

.. code-block:: python

    import transientbvd as tbvd

   tbvd.print_closed_potential(
       rs=24.764,
       ls=38.959e-3,
       cs=400.33e-12,
       c0=3970.1e-12,
       ucw=40.0,
       ub=60.0
   )

See :doc:`reference` for full API details.
