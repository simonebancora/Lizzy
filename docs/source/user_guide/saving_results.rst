.. _saving_results:

Saving results
==============

In this section we look at how we can save simulation results to files that can be read externally.
All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods. For more details about the underlying core components, please refer to the :ref:`api_reference_index` documentation.

The Solution object
-------------------

Every call to :meth:`~lizzy.LizzyModel.solve` or :meth:`~lizzy.LizzyModel.solve_time_interval` returns a :class:`~lizzy.datatypes.Solution` object containing the full time series of solution fields (fill factor, pressure, velocity, free surface) for all write-out time steps.

The solution is also automatically stored inside the model and is accessible via the :attr:`~lizzy.LizzyModel.latest_solution` property. This means that calling :meth:`~lizzy.LizzyModel.save_results` with no arguments will always save the most recent result:

.. code-block::

    model.solve()
    model.save_results()  # saves model.latest_solution automatically

Capturing the return value is only necessary for advanced use cases, such as saving results from multiple intermediate solve intervals independently:

.. code-block::

    sol_1 = model.solve_time_interval(300)
    model.change_inlet_pressure("inlet", 2e5)
    sol_2 = model.solve_time_interval(300)

    model.save_results(sol_1, "results_phase_1")
    model.save_results(sol_2, "results_phase_2")

Saving to file
--------------

Results are saved in the `XDMF <https://www.xdmf.org/>`_ format, backed by an HDF5 binary file. This format is natively supported by `Paraview <https://www.paraview.org/>`_ and can be loaded directly for time-series visualisation.

To save results, use the :meth:`~lizzy.LizzyModel.save_results` method:

.. code-block::

    model.save_results()

This creates two files in a ``results/`` folder in the current working directory:

- ``<name>_RES.xdmf``: the XDMF descriptor file (open this in Paraview).
- ``<name>_RES.h5``: the HDF5 binary file containing all field data.

By default, ``<name>`` is taken from the mesh file name. A custom name can be provided as the second argument:

.. code-block::

    model.save_results(result_name="my_simulation")

The following fields are saved at each write-out time step:

- **FillFactor**: fill factor at each node (0 = empty, 1 = filled).
- **FreeSurface**: flow front indicator.
- **Pressure**: pressure field [Pa].
- **Velocity**: Darcy velocity field [m/s].

Lightweight mode
----------------

When running many short solve intervals in a loop (e.g. to update boundary conditions frequently, or in a parametric study with a large number of simulations), packing the :class:`~lizzy.datatypes.Solution` at each step has a cost. Lightweight mode skips this step, reducing memory usage and overhead:

.. code-block::

    model.lightweight = True

In lightweight mode, :meth:`~lizzy.LizzyModel.solve_time_interval` does not create any :class:`~lizzy.datatypes.Solution` object and :meth:`~lizzy.LizzyModel.save_results` cannot be used.

.. note::

    Lightweight mode can be toggled at any time before or after solver initialisation.
