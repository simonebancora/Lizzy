.. py:currentmodule:: lizzy.IO

lizzy.IO
=========

The IO module provides functionality to read in input data and write out simulation results. The two main objects implemented by module are the ``Reader`` and the ``Writer`` classes.


.. autoclass:: lizzy.IO.IO.Reader


Currently, only the ``msh`` format is supported. More will be added in future updates.
The ``Reader`` constructor parses the mesh file and populates a dictionary ``mesh_data`` with all the information contained in the mesh file.

.. code-block:: python

    print(mesh_reader.mesh_data.keys())
    >>> dict_keys(['all_nodes_coords', 'nodes_conn', 'lines_conn', 'physical_lines_conn', 'physical_domains', 'physical_lines', 'physical_nodes'])

The purpose of the ``mesh_data`` dictionary is to collect the mesh data from any input format into a format that will be read by Lizzy when instantiating a ``Mesh`` object for the analysis.


