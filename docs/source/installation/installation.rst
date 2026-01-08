Installation
============

Lizzy is provided as a package. To install using pip, navigate inside the cloned `Lizzy` folder and run:

.. code-block:: console

   (.venv) $ pip install .

.. tip::
    Since Lizzy is still in early development, package versioning is not adopted yet. Therefore, it is recommended to install the package in `editable mode <https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode>`_:

    .. code-block:: console

      (.venv) $ pip install -e .

You can check that the installation was successful by typing:

.. code-block:: console

   (.venv) $ lizzy
   >>>
          |    _)                
          |     | _  / _  /  |  |
         ____| _| ___| ___| \_, |
                            ___/ 
                  v0.1.0

PETSc solvers (optional)
-------------------------

Lizzy leverages the `PETSc <https://petsc.org/release/>`_ library for some of its faster solvers. This installation is **optional** and not included by default. To use PETSc solvers, you need to install PETSc and its Python bindings PETSc4py in the same environment where Lizzy is installed:

.. code-block:: console

   (.venv) $ pip install petsc petsc4py

You can check at any time if PETSc is installed correctly by typing:

.. code-block:: console

   (.venv) $ lizzy info
   >>>

   Lizzy solver - v0.1.0

   Developed by S. Bancora and P. Mulye, Copyright 2025-2026
   Licensed under the GNU General Public License v3.0

   Optional dependencies:
   PETSc solvers: installed
   >>>
   
.. note::
    If you are using Windows, installing PETSc `might be challenging <https://petsc.org/main/install/windows/>`_. We recommend to use the Windows Subsystem for Linux 2 (WSL2) to install a Linux environment on your Windows machine, and then follow the Linux installation instructions for PETSc. Alternatively, PETSc can be manually built from source (advanced).