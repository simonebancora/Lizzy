.. currentmodule:: lizzy.lizzymodel

**********
LizzyModel
**********

The LizzyModel is the main component for user interaction with the solver. For any simulation task in Lizzy, the first step is to create a LizzyModel object:

.. code-block::

    import lizzy as liz
    model = liz.LizzyModel()

The main function of the LizzyModel is to provide all the APIs necessary for scripting the simulation scenario. Lizzy is designed so that, in most cases, the user should be able to perform any operation in the solver using the methods exposed by the LizzyModel class.
For the most part, writing a Lizzy script consists of a sequence of expressions that look like this:

.. code-block::

    output = model.MethodYouWantToCall(args)

There are methods that are not directly accessible from the LizzyModel, however these are currently not reported in documentation and mostly reserved for advanced users / authors.
In this section we will go through all the main methods accessible via the LizzyModel class.

Boundary Conditions Management
==============================





