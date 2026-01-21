Managing materials
==================

In this section we describe how to create and assign materials in Lizzy. All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods.

Materials in Lizzy
-------------------

In Lizzy, a material is represented by the :class:`~lizzy.materials.PorousMaterial` class. This class encapsulates the properties of a porous material, including its permeability, porosity, and thickness. Each material is defined by the following properties:

- **Permeability (k1, k2, k3)**: The permeability of the material in three principal directions (in m²).
- **Porosity**: The porosity of the material (dimensionless, between 0 and 1).
- **Thickness**: The thickness of the material (in meters). A material can represent a single layer of fabric, or a multi-layer laminate. In the latter case, the thickness represents the total thickness of the laminate.
- **Name**: A unique string identifier for the material.

The current version of Lizzy does not allow to compose a multi-layer laminate automatically by defining its layers. Instead, the user must compute the equivalent permeability, porosity, and thickness of the laminate externally and define a single :class:`~lizzy.materials.PorousMaterial` object representing the entire laminate. This is tipically done using arithmetic average schemes :cite:`calado1996effective` :cite:`bancora2018effective`. We plan to implement an automated multi-layer laminate definition feature in future releases.


Creating materials
-------------------

We can create a porous material using the :meth:`~lizzy.LizzyModel.create_material` method. This method requires the permeability values, porosity, thickness, and a unique name for the material. For example, to create a material with permeability values of 1E-10 m² in all directions, a porosity of 0.5, a thickness of 1.0 m, and named "material_01", we would do:

.. code-block::

    model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "material_01")

References
----------

.. bibliography:: ../refs.bib
   :style: unsrt