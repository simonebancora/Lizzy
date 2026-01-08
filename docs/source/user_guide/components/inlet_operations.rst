.. _inlet_operations:

==================
Inlet operations
==================

 We will limit ourselves to using the :class:`~lizzy.LizzyModel` user-facing methods, as this is the way Lizzy is intended to be used. For more details about the underlying core components, please refer to the :ref:`api_reference_index` documentation.

Preparing the mesh boundaries
-----------------------------

Before we can create and assign inlets to the model, we need to ensure that the mesh we are using has named boundaries. Named boundaries are essential to identify where inlets should be assigned. When creating a mesh using GMSH, named boundaries can be created using Physical Groups. For example, in a 2D mesh, we can create a Line Physical Group and give it a name like "left_edge". This name will be used later when assigning the inlet to the mesh.


.. image:: ../../../images/physical_boundary_tag.png
   :width: 80%
   :align: center

.. important::

    When using .msh format, ensure the file is exported in Version 4 ASCII, as Lizzy currently only supports this format.



