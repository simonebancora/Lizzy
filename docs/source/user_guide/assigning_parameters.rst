Assigning simulation parameters
================================

When simulating an infusion using Lizzy, there are some process and simulation parameters which are assigned globally. These are notably the resin viscosity, the frequence of solution write-outs and more. All global parameters are assigned to the model using the :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method:

.. code-block::

    model.assign_simulation_parameters(mu=0.1, wo_delta_time=100)

In this example, we have assigned a resin viscosity value of 0.1 Pa.s and we have told the solver to save a solution state every 100 seconds of simulation time. The :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method accepts keyword arguments to assign parameters. For the detailed list of possible arguments and their effect, see the linked API reference page.