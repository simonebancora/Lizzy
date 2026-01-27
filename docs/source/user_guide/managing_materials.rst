Managing materials
==================

In this section we describe how to create and assign materials in Lizzy. All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods.

Materials in Lizzy
-------------------

In Lizzy, a material is represented by the :class:`~lizzy.materials.PorousMaterial` class. This class encapsulates the properties of a porous material, including its permeability, porosity, and thickness. Each material is defined by the following properties:

- **Name**: A unique string identifier for the material.
- **Permeability (k1, k2, k3)**: The permeability of the material in three principal directions (in m²).
- **Porosity**: The porosity of the material (dimensionless, between 0 and 1).
- **Thickness**: The thickness of the material (in m). A material can represent a single layer of fabric, or a multi-layer laminate. In the latter case, the thickness represents the total thickness of the laminate.

The current version of Lizzy does not allow to compose a multi-layer laminate automatically by defining its layers. Instead, the user must compute the equivalent permeability, porosity, and thickness of the laminate externally and define a single :class:`~lizzy.materials.PorousMaterial` object representing the entire laminate. This is tipically done using arithmetic average schemes :cite:`calado1996effective` :cite:`bancora2018effective`. We plan to implement an automated multi-layer laminate definition feature in future releases.

Creating materials
-------------------

.. note::
    The following operations are to be performed **before** the solver is initialised by calling :meth:`~lizzy.LizzyModel.initialise_solver`.

We can create a porous material using the :meth:`~lizzy.LizzyModel.create_material` method. This method requires a unique name for the material, the permeability values (as a tuple), porosity and thickness. For example, to create a material named "material_01" with permeability values of 1E-10 m² in all directions, a porosity of 0.5 and a thickness of 1.0 mm, we would type:

.. code-block::

    model.create_material("material_01", (1E-10, 1E-10, 1E-10), 0.5, 0.001)

A :class:`~lizzy.materials.PorousMaterial` object is created and stored in the model, but it is not assigned yet.

Creating an orientation Rosette
-------------------------------

When working with anisotropic materials, it is necessary to define how the principal directions of permeability are oriented in the domain. To do so, we can create a :class:`~lizzy.materials.Rosette` object. A rosette is a local basis :math:`\hat e_1, \hat e_2, \hat e_3` that defines an orientation in space. When associated to a material, the principal directions of permeability will be aligned with the basis defined by the rosette. In Lizzy, we don't define the basis components directly. Instead, for any given rosette, we define a single orientation vector :math:`u_1` that will be projected onto the mesh elements to calculate the local basis :math:`\hat e_1, \hat e_2, \hat e_3` (more on this below). To create a rosette, we can use the :meth:`~lizzy.LizzyModel.create_rosette` method by providing a name for the rosette and the vector :math:`u_1`. For example, we can create a rosette named "rosette_01" with a vector :math:`u_1` oriented along (1, 1, 0) by typing:

.. code-block::

    model.create_rosette("rosette_01", (1,1,0))

Assigning materials
--------------------

To assign a material to a labeled domain, we use the :meth:`~lizzy.LizzyModel.assign_material` method, providing the following arguments:

- the name of the material to assign
- the name of the mesh domain where we want to assign it
- the rosette of orientation

For example, to assign the material "material_01" to a mesh domain labelled as "domain_01" and orient it using using the rosette "rosette_01", we would type:

.. code-block::

    model.assign_material("material_01", "domain_01", "rosette_01")

When the assignment happens, the remaining components of the local rosette (:math:`\hat e_1, \hat e_2, \hat e_3`) are calculated and registered for  as follows:

- :math:`\hat e_1`: is calculated as the projection of :math:`u_1` along the normals of the elements in the domain
- :math:`\hat e_3`: is calculated as the normal of the elements in the domain
- :math:`\hat e_2`: is calculated as :math:`\hat e_1 \times \hat e_3`

.. note::
    If a rosette is not provided, a default orientation is used with :math:`\hat e_1, \hat e_2, \hat e_3` aligned with global axes :math:`e_1, e_2, e_3`. This can be convenient when working with isotropic materials, since we don't care about their orientation. For example:

    .. code-block::
        
        k_iso = 1.0E-11
        model.create_material("material_iso", (k_iso, k_iso, k_iso), 0.5, 1.0)
        model.assign_material("material_iso", "domain_01")



References
----------

.. bibliography:: ../refs.bib
   :style: unsrt