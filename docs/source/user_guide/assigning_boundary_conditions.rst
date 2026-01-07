==================================
Boundary conditions operations
==================================

In this section we look at various boundary condition operations, including creating boundary conditions and modifying them at runtime.
All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods. For more details about the underlying core components, please refer to the :ref:`api_reference_index` documentation.

.. admonition:: Under the hood

    The :class:`~lizzy.core.bcond.BCManager` core component of the :class:`~lizzy.LizzyModel` is responsible for all boundary conditions related operations, including inlet creation and runtime modification. The LizzyModel wraps some of its methods to provide user-facing APIs.

Creating an inlet
------------------

To create an inlet, we use the :meth:`~lizzy.LizzyModel.create_inlet` method. This method requires two arguments: the inlet initial pressure (in Pa) and a unique string identifier (tag) for the inlet. For example, to create an inlet with a pressure of 1e5 Pa and the tag "inlet_1", we would write:

.. code-block::

    model.create_inlet(1e5, "inlet_1")

.. important::

    Currently, only pressure boundary conditions at inlets are supported. Other types of inlet boundary conditions (e.g., flow rate) will be added in the future.

Once that method is called, an :class:`~lizzy.core.bcond.Inlet` object is created and stored in the model, but it is not assigned yet. To assign the inlet to a specific boundary, we use the :meth:`~lizzy.LizzyModel.assign_inlet` method, providing the inlet tag of the inlet that we just created and the name of the mesh boundary where we want to assign it:

.. code-block::

    model.assign_inlet("inlet_1", "left_edge")

The boundary tag must correspond to an existing named boundary in the mesh (in this case the one we have created in the GMSH example).
