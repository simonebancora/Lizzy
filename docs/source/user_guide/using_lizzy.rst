===========
Using Lizzy
===========

In this section, we detail how to use Lizzy setting up and running simulations. The philosophy of Lizzy is inspired to popular FE libraries like `FEniCS <https://fenicsproject.org>`_: we provide a flexible scripting API that allows the user to define any type of infusion scenario. Everything in Lizzy is accomplished by writing a Python script.


Basic script workflow
----------------------

The basic workflow for writing a Python script to use Lizzy involves the following key steps:

1. Import the Lizzy package.
2. Instantiate a LizzyModel object.
3. Use the LizzyModel object to define the simulation.
4. Run the simulation.
5. Save results.

As we will see shortly, most of the model operations are performed using the :class:`~lizzy.LizzyModel` class directly.

Units and conventions
----------------------
The solver assumes consistent units and does not enforce any. The user is free to use any system of units, as long as they are consistent throughout the script. We recommend to stick to the SI units:

- Permeability: m²
- Viscosity: Pa·s
- Length: m
- Time: s
- Pressure: Pa
- Velocity: m/s

LizzyModel
-----------

The :class:`~lizzy.LizzyModel` class is the main protagonist of any Lizzy script. This class provides APIs to execute all the core fucntionalities of the solver.
When writing a Lizzy script, typically the first step (after importing the library) is to instantiate a :class:`~lizzy.LizzyModel` object:

.. code-block::

    model = liz.LizzyModel()

After that, every operation in the script is typically done by accessing methods of the :class:`~lizzy.LizzyModel` object, something like:

.. code-block::

    operation_output = model.some_method(args)

The Lizzy API is designed so that, in most cases, the :class:`~lizzy.LizzyModel` class is the only one the user needs do learn.

.. admonition:: Under the hood

    The LizzyModel class wraps many core components of the library: :class:`~lizzy.bcond.bcond.BCManager`, :class:`~lizzy.materials.MaterialManager`, :class:`~lizzy.sensors.sensmanager.SensorManager`, :class:`~lizzy.solver.solver.Solver` and more... These are private members of the class, and are not intended to be accessed directly. Instead, the LizzyModel provides public wrappers for all main methods of these core components. However, not all the fucntionalities of Lizzy are exposed by the LizzyModel. In some cases, it might be necessary to access a core component directly, but these special cases reserved to advanced users that are know well the solver architecture.

.. important::
    
    In a nutshell: the :class:`~lizzy.LizzyModel` class provides all user-facing APIs needed to write a Lizzy script. If something is not there, it is likely not intended to be used in a script.


.. seealso::

    :ref:`tutorials`
         A collection of tutorials to learn the LizzyModel API.

    :ref:`LizzyModel API reference <lizzymodel_api>`
        The API reference of the LizzyModel class.


In this section, we cover the most common operations that can be performed using a LizzyModel object.

Reading a mesh file
^^^^^^^^^^^^^^^^^^^^^^^^

Reading an existing mesh file is typically the first operation that we perform after instantiating a LizzyModel object. To read a mesh, we call the :meth:`~lizzy.LizzyModel.read_mesh_file` method:


.. code-block::

    model.read_mesh_file("PATH_TO_FILE")

Currently, the only supported mesh format is `.msh` (Version 4 ASCII). This is the typical mesh format that can be exported using software like GMSH. Continuing development, more formats will gradually be supported.

Assigning simulation parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When simulating an infusion using Lizzy, there are some process and simulation parameters which are assigned globally. These are notably the resin viscosity, the frequence of solution write-outs and more. All global parameters are assigned to the model using the :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method:

.. code-block::

    model.assign_simulation_parameters(mu=0.1, wo_delta_time=100)

In this example, we have assigned a resin viscosity value of 0.1 Pa.s and we have told the solver to save a solution state every 100 seconds of simulation time. The :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method accepts keyword arguments to assign parameters. For the detailed list of possible arguments and their effect, see the linked API reference page.

Managing materials
^^^^^^^^^^^^^^^^^^^^^^^^

The LizzyModel provides all relevant methods to create and assign any number of porous materials to the various mesh regions. The main methods to be used when performing material operations are :meth:`~lizzy.LizzyModel.create_material` and :meth:`~lizzy.LizzyModel.assign_material`. Under the hood, the LizzyModel is using the MaterialManager core component to perform these operations. We detail these functionality in the **Material operations** section.

Assigning boundary conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All boundary condition operations can be performed directly from the LizzyModel. For example we can create inlets using the :meth:`~lizzy.LizzyModel.create_inlet` and :meth:`~lizzy.LizzyModel.assign_inlet` methods:

.. code-block::

    model.create_inlet(1e+05, "inlet_tag")
    model.assign_inlet("inlet_tag", "boundary_tag")

Other methods, like :meth:`~lizzy.LizzyModel.change_inlet_pressure`, allow to manage inlet behaviour during the infusion. More details about boundary condition operations can be found in the :ref:`inlet_operations` section.




See also
^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   components/inlet_operations