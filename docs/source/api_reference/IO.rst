.. py:currentmodule:: lizzy._core.io

lizzy._core.io
==============

The IO module provides functionality to read in input data and write out simulation results. The two main objects implemented by module are the :class:`~lizzy._core.io.Reader` and the :class:`~lizzy._core.io.Writer` classes. Both are instantiated automatically by the :class:`~lizzy.lizmodel.LizzyModel` class when the :meth:`~lizzy.lizmodel.LizzyModel.read_mesh_file` is called.

.. autoclass:: lizzy._core.io.Reader

    .. rubric:: Methods

    .. automethod:: lizzy._core.io.Reader.print_mesh_info


.. important::
    Currently, only the ``msh`` format is supported. More will be added in future updates.


.. autoclass:: lizzy._core.io.Writer

    .. rubric:: Methods

    .. automethod:: Writer.save_results
