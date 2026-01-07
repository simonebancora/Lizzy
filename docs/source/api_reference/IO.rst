.. py:currentmodule:: lizzy.core.io

lizzy.core.io
=============

The IO module provides functionality to read in input data and write out simulation results. The two main objects implemented by module are the :class:`~lizzy.core.io.Reader` and the :class:`~lizzy.core.io.Writer` classes. Both are instantiated automatically by the :class:`~lizzy.lizmodel.lizmodel.LizzyModel` class when the :meth:`~lizzy.lizmodel.lizmodel.LizzyModel.read_mesh_file` is called.

.. autoclass:: lizzy.core.io.Reader

    .. rubric:: Methods

    .. automethod:: lizzy.core.io.Reader.print_mesh_info


.. important::
    Currently, only the ``msh`` format is supported. More will be added in future updates.


.. autoclass:: lizzy.core.io.Writer

    .. rubric:: Methods

    .. automethod:: Writer.save_results
