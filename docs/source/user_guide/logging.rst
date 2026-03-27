.. _logging:

Logging
=======

Lizzy uses Python's standard :mod:`logging` module for communication. See the standard library documentation for more information. By default, if no logger is set up, all termninal output is suppressed. This complies with standard logging practice.

Enabling log output
-------------------

Call :func:`logging.basicConfig` before creating a :class:`~lizzy.LizzyModel` instance:

.. code-block:: python

    import logging
    import lizzy

    logging.basicConfig(level=logging.INFO)

    model = lizzy.LizzyModel()
    # ... etc ...


This will produce output in the console when the script is run:

.. code-block:: console
              
     |    _)                
     |     | _  / _  /  |  |
    ____| _| ___| ___| \_, |
                      ___/ 
            v0.1.0
    
    INFO:lizzy.io: Reading mesh file: ../mesh_file.msh
    INFO:lizzy.mesh: Creating Mesh...
    INFO:lizzy.solver: Preprocessing...
    INFO:lizzy.solver: Solving...
    INFO:lizzy.solver: Solve completed in $ seconds
    INFO:lizzy.io: Saving results...
    INFO:lizzy.io: Results saved in results/NAME_RES

It is recommended to use logging in normal Lizzy use - otherwise you won't get any feedback on what is happning.

.. note::
    Configure logging **before** creating a :class:`~lizzy.LizzyModel`.

Logger hierarchy
----------------

Lizzy uses the following logger names, which follow the standard Python hierarchy under the ``lizzy`` root:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Logger
     - What it covers
   * - ``lizzy``
     - Root logger
   * - ``lizzy.model``
     - Model setup and operations
   * - ``lizzy.solver``
     - Preprocessing and solving logic
   * - ``lizzy.io``
     - Mesh file reading, result saving
   * - ``lizzy.mesh``
     - Mesh operations

Log levels
----------

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Level
     - What it shows
   * - ``INFO``
     - General operational information. Recommended in mose cases.
   * - ``WARNING``
     - Non-critial issues that may require attention (e.g. unassigned parameters running with default values)
   * - ``DEBUG``
     - PETSc convergence - not fully implemented yet


Progress bar
------------

In addition to log messages, Lizzy can display a `tqdm <https://tqdm.github.io>`_ progress bar while solving. This is independent of the logging system and is controlled by the ``progress_bar`` parameter of :meth:`~lizzy.LizzyModel.set_simulation_parameters`:

.. code-block:: python

    model.set_simulation_parameters(progress_bar=True)