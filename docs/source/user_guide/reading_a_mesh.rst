Reading a mesh file
^^^^^^^^^^^^^^^^^^^^^^^^

Lizzy can read a mesh file that contains tagged domains and boundaries.
Currently, the only supported mesh format is `.msh` (Version 4 ASCII). This is the typical mesh format that can be exported using software like GMSH. Continuing development, more formats will gradually be supported.

The `.msh` file has some requirements to be compatible with Lizzy:

- The mesh must be composed uniquely of 2D triangle elements (quads are not supported).
- Physical groups must be defined for all material domains and for all edges where a boundary condition will be applied. The name of the physical groups will be used to identify the different boundaries and materials in the mesh. To learn more about how to prepare a mesh for Lizzy using GMSH, refer to the `GMSH documentation <https://gmsh.info/doc/texinfo/gmsh.html#Elementary-entities-vs-physical-groups>`_ .

Reading an existing mesh file is typically the first operation that we perform after instantiating a LizzyModel object. To read a mesh, we call the :meth:`~lizzy.LizzyModel.read_mesh_file` method:

.. code-block::

    model.read_mesh_file("PATH_TO_FILE")

After reading the mesh, we can use the :meth:`~lizzy.LizzyModel.print_mesh_info` method to verify that the mesh has been read correctly, and that all physical groups are present:

.. code-block:: console

    >>> model.print_mesh_info()
    >>> 
        Mesh file format: MSH (v4 ASCII),
        Case name:    CHANNEL_INFUSION,
        Mesh contains 1500 nodes, 3000 elements.
        Physical domains:        ['domain_1', 'domain_2']
        Physical lines:          ['left_edge', 'right_edge', 'walls']
