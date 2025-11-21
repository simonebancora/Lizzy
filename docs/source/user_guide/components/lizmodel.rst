.. currentmodule:: lizzy.lizmodel


LizzyModel
==========

The LizzyModel is the main component for user interaction with the solver. For any simulation task in Lizzy, the first step is to create a LizzyModel object:

.. code-block::

    model = liz.LizzyModel()

The main function of the LizzyModel is to provide all the APIs necessary for scripting the simulation scenario. Under the hood, the LizzyModel wraps all the core components of the library: BCManager, MaterialManager, SensorManager and Solver. These are registered as private members of the LizzyModel class, and are not intended to be accessed directly. Instead, the LizzyModel directly provides wrappers for a series of core components methods, which are exposed publicly. Lizzy is designed so that, in most cases, the user should be able to perform any operation in the solver using the methods exposed by the LizzyModel class. In this section, we will illustrate the most common operations that can be performed using the LizzyModel API.

Reading a mesh file
-------------------

Reading an existing mesh file is typically the first operation that we perform after instantiating a LizzyModel object. To read a mesh, we can call the :meth:`~lizzy.LizzyModel.read_mesh_file` method:


.. code-block::

    model.read_mesh_file("PATH_TO_FILE")

Currently, the only supported mesh format is `.msh` (Version 4 ASCII). This is the typical mesh format that can be exported using software like GMSH. Continuing development, more formats will gradually be supported.

Assigning simulation parameters
-------------------------------

When simulating an infusion using Lizzy, there are some process and simulation parameters which are assigned globally. These are notably the resin viscosity, the frequence of solution write-outs and more. All global parameters are assigned to the model using the :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method:

.. code-block::

    model.assign_simulation_parameters(mu=0.1, wo_delta_time=100)

In this example, we have assigned a resin viscosity value of 0.1 Pa.s and we have told the solver to save a solution state every 100 seconds of simulation time. The :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method accepts keyword arguments to assign parameters. For the detailed list of possible arguments and their effect, see the linked API reference page.

Managing materials
------------------

The LizzyModel provides all relevant methods to create and assign any number of porous materials to the various mesh regions. The main methods to be used when performing material operations are :meth:`~lizzy.LizzyModel.create_material` and :meth:`~lizzy.LizzyModel.assign_material`. Under the hood, the LizzyModel is using the MaterialManager core component to perform these operations. We detail these functionality in the **Material operations** section.

Assigning boundary conditions
-----------------------------

All boundary condition definitions and management operations can be performed directly from the LizzyModel. At a base implementation, we can add inlet conditions to our simulation using the :meth:`~lizzy.LizzyModel.create_inlet` and :meth:`~lizzy.LizzyModel.assign_inlet` methods.