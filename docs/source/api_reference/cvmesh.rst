.. py:currentmodule:: lizzy._core.cvmesh

lizzy._core.cvmesh
==================

The CVMESH module contains the :class:`~lizzy._core.cvmesh.Mesh` class, which stores data about nodes, elements and control volumes. The :class:`~lizzy._core.cvmesh.VMesh` is instantiated by the constructor of the :class:`~lizzy.lizmodel.LizzyModel`, and belongs to the model.

.. autoclass:: lizzy._core.cvmesh.Mesh

    .. rubric:: Methods

    .. automethod:: Mesh.preprocess