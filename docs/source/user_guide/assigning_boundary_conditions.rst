==================================
Boundary conditions operations
==================================

In this section we look at various boundary condition operations, including creating boundary conditions and modifying them at runtime.
All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods. For more details about the underlying core components, please refer to the :ref:`api_reference_index` documentation.

.. admonition:: Under the hood

    The :class:`~lizzy.core.bcond.BCManager` core component of the :class:`~lizzy.LizzyModel` is responsible for all boundary conditions related operations, including inlet creation and runtime modification. The LizzyModel wraps some of its methods to provide user-facing APIs.

Creating an inlet
------------------

To create an inlet, we use the :meth:`~lizzy.LizzyModel.create_inlet` method. This method requires two arguments: the inlet initial pressure (in Pa) and a unique string identifier (tag) for the inlet. For example, we can create an inlet with a pressure of 1.0E05 Pa tagged as "inlet_1":

.. code-block::

    model.create_inlet(1e5, "inlet_1")

.. important::

    Currently, only pressure boundary conditions at inlets are supported. Other types of inlet boundary conditions (e.g., flow rate) will be added in the future.

Once that method is called, an :class:`~lizzy.core.bcond.Inlet` object is created and stored in the model, but it is not assigned yet. To assign the inlet to a specific boundary, we use the :meth:`~lizzy.LizzyModel.assign_inlet` method, providing the inlet tag of the inlet that we just created and the name of the mesh boundary where we want to assign it:

.. code-block::

    model.assign_inlet("inlet_1", "left_edge")

The boundary tag must correspond to an existing named boundary in the mesh (a "physical line" in the case of a .MSH mesh).

Modifying inlet pressure at runtime
-----------------------------------

To modify the pressure of an existing inlet during the simulation, we can use the :meth:`~lizzy.LizzyModel.change_inlet_pressure` method. This method requires two arguments: the inlet tag and the new pressure value. For example, to change the pressure of the inlet tagged as "inlet_1" to 2.0E05 Pa, we would do:

.. code-block::

    model.change_inlet_pressure("inlet_1", 2e5)

This method can be called at any time during the simulation. The new value will be applied at the next time step in the simulation, allowing for dynamic boundary conditions. We can also specify whether the new pressure value should be applied as a new absolute value or as a relative change to the current pressure by using the optional third argument `mode` which can be `set` (default) or `delta`.

- `mode = "set"`: sets the inlet pressure to the new value provided.
- `mode = "delta"`: increases the current inlet pressure by the new value provided.

For example, to increase the pressure of "inlet_1" by 5.0E04 Pa, we would do:

.. code-block::

    model.change_inlet_pressure("inlet_1", 5e4, "delta")

.. tip::

    The :meth:`~lizzy.LizzyModel.change_inlet_pressure` function works well with the :meth:`~lizzy.LizzyModel.solve_step` method. For example, we can advance the simulation by a given amount of time, then modify the inlet pressure, and resume the filling:

    .. code-block::
        
        # advance simulation by 300 seconds
        sol = model.solve_step(300)

        # decrease inlet pressure by 60000 Pa (mode = "delta")
        model.change_inlet_pressure("inlet_tag", -60000, "delta")

        # advance simulation by another 800 seconds
        sol = model.solve_step(800)

        # set inlet pressure to 3E05 Pa (default mode = "set")
        model.change_inlet_pressure("inlet_tag", 3e05)
        
        # advance simulation till part fill
        sol = model.solve()
    

    .. image:: ../../images/change_inlet_p_loop.gif
       :width: 70%
       :align: center


Opening / closing inlets at runtime
------------------------------------

To open or close an existing inlet during the simulation, we can use the :meth:`~lizzy.LizzyModel.open_inlet` and :meth:`~lizzy.LizzyModel.close_inlet` methods, respectively. Both methods require a single argument: the inlet tag. For example, to close the inlet tagged as "inlet_1", we would do:

.. code-block::

    model.close_inlet("inlet_1")

This expression turns the inlet boundary into a wall boundary (Neumann natural boundary condition). To reopen the inlet at any time, we would do:

.. code-block::

    model.open_inlet("inlet_1")

This expression restores the inlet boundary condition with the last assigned pressure value.

.. tip::
    
    The :meth:`~lizzy.LizzyModel.open_inlet` and :meth:`~lizzy.LizzyModel.close_inlet` functions work well with the :meth:`~lizzy.LizzyModel.solve_step` method. For example, we can advance the simulation by a given amount of time, then close an inlet, and resume the filling:

    .. code-block::
        
        # advance simulation by 150 seconds
        sol = model.solve_step(150)

        # close the inlet
        model.close_inlet("inlet_left")

        # advance simulation by another 400 seconds
        sol = model.solve_step(400)

        # reopen the inlet
        model.open_inlet("inlet_left")
        
        # advance simulation till part fill
        sol = model.solve()

    .. image:: ../../images/openclose_inlets_loop.gif
       :width: 70%
       :align: center