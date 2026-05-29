.. _adding_example_code_tidymess:

Adding a C++ N-Body Code to AMUSE
=================================

In this tutorial, we will create an interface from scratch for the
TIdal DYnamics of Multi-body ExtraSolar Systems code, or ``TIDYMESS``,
written by Dr. Tjarda Boekholt and Dr. Alexandre Correia. This code
implements detailed tidal forces into an N-body code to track the deformation
of bodies. This community code has already been implemented into AMUSE so you
can follow along this tutorial.

Getting Started
===============

This tutorial assumes you have a working amuse or amuse development build,
preferrably in seperated environment (virtualenv, venv or conda etc).
Please ensure that amuse is setup correctly, this can be verified by running the
``amusifier`` .

.. code-block:: bash

    > amusifier --help

Naming our project
~~~~~~~~~~~~~~~~~~
Amuse naming conventions typically follows PascalCase, so we will name our project Tidymess.

Creating the initial directory structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To start, we need to create the directory structure for ``Tidymess``, along with the
necessary files to build our interface. The fastest method to setup the directory is
by using the ``amusifier`` script with ``--mode=dir``.

Since ``TIDYMESS`` is a native C++ code with no other dependencies, we will specify
``--type=c``, but the ``amusifier`` can also build the interface directory for
``f90`` and ``python`` codes.

.. code-block:: bash

    > amusifier --type=c --mode=dir Tidymess

Having run the ``amusifier``, we now have our new directory in ``amuse/src/amuse_tidymess``.
There should be all the required folders for building our interface, as well as a few code
stubs to expand upon.

Building the code
=================
Before we start working on the interface, we should try and install and compile ``TIDYMESS``
inside of ``AMUSE``.

Defining dependencies
~~~~~~~~~~~~~~~~~~~~~
The ``AMUSE`` build system needs to know what packages and libraries our project depends on.
Navigate to ``amuse_tidymess/packages/amuse_tidymess.amuse_deps``, which is where we define every
dependency we will need. By default it will look like:

.. code-block:: text

   c c++ fortran java python cmake install download mpi openmp cuda opencl x11 opengl blas lapack gsl gmp mpfr fftw hdf5 netcdf4

Since ``TIDYMESS`` is a standalone C++ code, we can delete most of those and simplify our dependencies to:

.. code-block:: text

   c c++

Setting up Autoconf
~~~~~~~~~~~~~~~~~~~
The ``amuse_deps`` file we just created informs the ``AMUSE`` build system about whether or not our
package is buildable given the available compilers and libraries detected on your computer. We now need
to determine what compilers and libraries are on the system and how to use them. For this we will edit
the ``configure.ac`` file in ``amuse_tidymess/support/``. This file contains a set of macros which will
detect the tools and libraries needed to build our package. The template should contain all the macros
needed for our package, so its just a matter of deleting what we don't need.

.. WARNING::

    Make sure the the ``amuse_tidymess/support/shared/`` folder is a simlink to ``amuse/support/shared/``
    to ensure that there is no code duplication in the codebase, and that bug fixes are propagated to each
    package automatically.
