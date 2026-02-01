Basics
======

The philosophy of Lizzy is inspired to popular FE libraries like `FEniCS <https://fenicsproject.org>`_: we provide a flexible scripting API that allows the user to define any type of infusion scenario. Everything in Lizzy is accomplished by writing a Python script.

Lizzy workflow
-----------------

The basic workflow for using Lizzy in a Python script involves the following key steps:

1. Import the Lizzy package.
2. Instantiate a :class:`~lizzy.LizzyModel` object.
3. Use the :class:`~lizzy.LizzyModel` API to define and run the simulation.
4. Save results.

Lizzy is designed so that most of the operations can be performed using the :class:`~lizzy.LizzyModel` class.

Units and conventions
----------------------
The solver assumes consistent units and does not enforce any. The user is free to use any system of units, as long as they are consistent throughout the script. We recommend to stick to the SI units:

- Permeability: m²
- Viscosity: Pa·s
- Length: m
- Time: s
- Pressure: Pa
- Velocity: m/s


The LizzyModel class
---------------------

The :class:`~lizzy.LizzyModel` class is the main protagonist of any Lizzy script. This class provides APIs to execute all the core fucntionalities of the solver.
When writing a Lizzy script, typically the first step (after importing the library) is to instantiate a :class:`~lizzy.LizzyModel` object:

.. code-block::

    model = liz.LizzyModel()

The Lizzy API is designed so that, in most cases, the :class:`~lizzy.LizzyModel` class is the only one the user needs do access to do any operation:

.. code-block::

    operation_output = model.some_method(args)


The :ref:`using_lizzy` section of this documentation is dedicated to showing how elementary operations can be done in Lizzy. The :ref:`api_reference_index` provides detailed information about the LizzyModel functionalities anf other namespaces of Lizzy.
