.. py:currentmodule:: lizzy

IO module
=========

The IO module provides functionality to read in input data and write out simulation results. The two main objects implemented by module are the ``Reader`` and the ``Writer`` classes.

Mesh file Reader
________________

To read a mesh file, we instantiate a Reader object:

.. code-block:: python

    import lizzy as liz
    mesh_reader = liz.Reader("path_to_file.msh")

Currently, only the ``msh`` format is supported. More will be added in future updates.
The ``Reader`` constructor parses the mesh file and populates a dictionary ``mesh_data`` with all the information contained in the mesh file.

.. code-block:: python

    print(mesh_reader.mesh_data.keys())
    >>> dict_keys(['all_nodes_coords', 'nodes_conn', 'lines_conn', 'physical_lines_conn', 'physical_domains', 'physical_lines', 'physical_nodes'])

The purpose of the ``mesh_data`` dictionary is to collect the mesh data from any input format into a format that will be read by Lizzy when instantiating a ``Mesh`` object for the analysis.

.. autoclass:: Reader()

.. autoclass:: Writer()