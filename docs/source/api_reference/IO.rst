.. py:currentmodule:: lizzy.IO

lizzy.IO
=========

The IO module provides functionality to read in input data and write out simulation results. The two main objects implemented by module are the :class:`~lizzy.IO.IO.Reader` and the :class:`~lizzy.IO.IO.Writer` classes. Both are instantiated automatically by the :class:`~lizzy.lizmodel.lizmodel.LizzyModel` class when the :meth:`~lizzy.lizmodel.lizmodel.LizzyModel.read_mesh_file` is called.

.. autoclass:: lizzy.IO.IO.Reader

    .. rubric:: Methods

    .. automethod:: lizzy.IO.IO.Reader.print_mesh_info


.. important::
    Currently, only the ``msh`` format is supported. More will be added in future updates.


.. autoclass:: lizzy.IO.IO.Writer

    .. rubric:: Methods

    .. automethod:: lizzy.IO.IO.Writer.save_results

