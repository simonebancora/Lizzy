Basics
======

The philosophy of Lizzy is inspired to popular FE libraries like `FEniCS <https://fenicsproject.org>`_: we provide a flexible scripting API that allows the user to define any type of infusion scenario. Everything in Lizzy is accomplished by writing a Python script.

Units and conventions
----------------------
The solver assumes consistent units and does not enforce any. The user is free to use any system of units, as long as they are consistent throughout the script. We recommend to stick to the SI units:

- Permeability: m²
- Viscosity: Pa·s
- Length: m
- Time: s
- Pressure: Pa
- Velocity: m/s

Lizzy script structure
----------------------

A typical Lizzy script is structured as follows:

.. code-block::

    # 1. Import the Lizzy package
    import lizzy

    # 2. Model setup
    model = lizzy.LizzyModel()
    model.do_setup_stuff( ... )
    ...

    # 3. Solver initialisation
    model.initialise_solver()

    # 4. Execution
    model.solve()

    # 5. Save results
    model.save_results()

As Lizzy is just an imported package, the solver can be used within any Python script. This offers the possibility of advanced scripting and automation. For example, we can set up a parametric study by writing a simple loop, run a simulation in a Jupyter notebook, and much more. This user guide aims at teaching the core concepts of the Lizzy API, so that the user can write their own scripts and use the solver in the most flexible way possible. We also provide some :ref:`tutorials` as a starting point for writing scripts with Lizzy.

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
