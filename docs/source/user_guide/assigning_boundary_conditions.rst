
Assigning boundary conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All boundary condition operations can be performed directly from the LizzyModel. For example we can create inlets using the :meth:`~lizzy.LizzyModel.create_inlet` and :meth:`~lizzy.LizzyModel.assign_inlet` methods:

.. code-block::

    model.create_inlet(1e+05, "inlet_tag")
    model.assign_inlet("inlet_tag", "boundary_tag")

Other methods, like :meth:`~lizzy.LizzyModel.change_inlet_pressure`, allow to manage inlet behaviour during the infusion. More details about boundary condition operations can be found in the :ref:`inlet_operations` section.

