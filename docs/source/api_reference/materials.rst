.. py:currentmodule:: lizzy.core.materials

lizzy.core.materials
====================

The MATERIALS module provides functionality related to all material operations. The most important component is the :class:`~lizzy.core.materials.MaterialManager` class, which is responsible for managing all materials. The :class:`~lizzy.core.materials.MaterialManager` is instantiated by the constructor of the :class:`~lizzy.lizmodel.LizzyModel`, and belongs to the model.

.. autoclass:: lizzy.core.materials.MaterialManager

    .. rubric:: Properties

    .. autoproperty:: MaterialManager.assigned_materials
    .. autoproperty:: MaterialManager.assigned_rosettes
    .. autoproperty:: MaterialManager.existing_materials
    
    .. rubric:: Methods

    .. automethod:: MaterialManager.create_material
    .. automethod:: MaterialManager.assign_material
    .. automethod:: MaterialManager.fetch_material

.. autoclass:: lizzy.core.materials.PorousMaterial


.. autoclass:: lizzy.core.materials.Rosette
