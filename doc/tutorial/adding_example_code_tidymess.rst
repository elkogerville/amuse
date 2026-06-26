.. _adding_example_code_tidymess:

Adding a C++ N-Body Code to AMUSE
=================================

In this tutorial, we will create an interface from scratch for the
TIdal DYnamics of Multi-body ExtraSolar Systems code, or TIDYMESS,
written by Dr. Tjarda Boekholt and Dr. Alexandre Correia
(https://doi.org/10.48550/arXiv.2209.03955). This code implements detailed
tidal forces into an N-body code to track the deformation of bodies.
This community code has already been implemented into AMUSE so you
can follow along this tutorial.

.. NOTE::

    In this guide, TIDYMESS refers to the standalone simulation package,
    while ``Tidymess`` refers to the TIDYMESS package inside of AMUSE.


Getting Started
===============

This tutorial assumes you have a working amuse or amuse development build,
preferably in seperated environment (virtualenv, venv or conda etc).
Please ensure that amuse is set up correctly, this can be verified by running the
``amusifier`` .

.. code-block:: bash

    > amusifier --help

Naming our project
~~~~~~~~~~~~~~~~~~
PEP-8 naming conventions for classes follows PascalCase, so we will name our project ``Tidymess``.

Creating the initial directory structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To start, we need to create the directory structure for ``Tidymess``, along with the
necessary files to build our interface. The fastest method to setup the directory is
by using the ``amusifier`` script with ``--mode=dir``.

Since TIDYMESS is a native C++ code with no other dependencies, we will specify
``--type=c``, but the ``amusifier`` can also build the interface directory for
``f90`` and ``python`` codes. Make sure you run the ``amusifier`` in the ``amuse/src/`` directory.

.. code-block:: bash

    > cd amuse/src/
    > amusifier --type=c --mode=dir Tidymess

Having run the ``amusifier``, we now have our new directory in ``amuse/src/amuse_tidymess``.
There should be all the required folders for building our interface, as well as a few code
stubs to expand upon.

Building the code
=================
Before we start working on the interface, we should try to install and compile TIDYMESS
inside of ``AMUSE``.

Defining dependencies
~~~~~~~~~~~~~~~~~~~~~
The AMUSE build system needs to know what packages and libraries our project depends on.
Navigate to ``amuse_tidymess/packages/amuse_tidymess.amuse_deps``, which is where we define every
dependency we will need. By default it will look like:

.. code-block:: text

   c c++ fortran java python cmake install download mpi openmp cuda opencl x11 opengl blas lapack gsl gmp mpfr fftw hdf5 netcdf4

Since ``TIDYMESS`` is a standalone C++ code, we can delete most of those and simplify our dependencies to:

.. code-block:: text

   c++

To test that we did everything properly, we can run ``./setup`` from the top-level directory of AMUSE

.. code-block:: text

    > cd amuse/
    > ./setup

    Checking for dependencies, one moment please...

    *** Configuration complete ***
    Detected features: c c++ fortran python python-dev gmake cmake install
    download patch tar unzip gunzip bunzip2 unxz perl bison mpi openmp blas
    lapack gsl gmp mpfr fftw libz hdf5 netcdf4 qhull healpix-cxx

    ** Enabled packages **

    Packages marked i) are currently installed.

    i) amuse-framework           amuse-hop                 amuse-petar
       amuse-aarsethzare         amuse-huayno-openmp       amuse-ph4
       amuse-adaptb              amuse-huayno              amuse-phantom
       amuse-athena              amuse-kepler              amuse-phigrape
       amuse-bhtree              amuse-kepler-orbiters     amuse-rebound
       amuse-brutus              amuse-krome               amuse-sakura
       amuse-bse                 amuse-mameclot            amuse-seba
       amuse-capreole            amuse-mercury             amuse-secularmultiple
       amuse-evtwin              amuse-mesa-r15140         amuse-sei
       amuse-fastkick            amuse-mesa-r2208          amuse-simplex
       amuse-fi                  amuse-mi6                 amuse-smalln
       amuse-fractalcluster      amuse-mikkola             amuse-sphray
       amuse-gadget2             amuse-mmams               amuse-sse
       amuse-galactics           amuse-mobse               amuse-symple
       amuse-galaxia             amuse-mocassin            amuse-tidymess
       amuse-halogen             amuse-mosse               amuse-tupan
       amuse-hermite             amuse-mpiamrvac           amuse-twobody
       amuse-hermite-grx         amuse-nbody6xx            amuse-vader

We can see that the AMUSE framework is correctly installed, indicated by the ``i)`` symbol. We can
also see our package ``amuse-tidymess`` is listed meaning the AMUSE build system now knows of our project
and we are ready to move on!

Setting up Autoconf
~~~~~~~~~~~~~~~~~~~
We now need to determine what compilers and libraries are on the system and how to use them. For this we will edit
the ``configure.ac`` file in ``amuse_tidymess/support/``. This file contains a set of macros which will
detect the tools and libraries needed to build our package. The template should contain all the macros
needed for our package, so its just a matter of deleting what we don't need. Delete any comment prefaced
with ``#####``, but only after following the direction of the comment. Since TIDYMESS is a native C++ code,
most of the optional macros can be deleted, especially the ones related to external libraries like ``CUDA``,
``MPI``, ``FFTW``, etc... The only optional macros we will keep are ``AMUSE_LIB_STOPCOND()`` for enabling stopping
conditions in our project, as well as ``AMUSE_DOWNLOAD()`` and ``AC_CHECK_TOOL(TAR, tar)`` for dynamically
downloading TIDYMESS from github into our project when the user tries to install it (so we don't need to package
the source code directly into AMUSE).

Once ``configure.ac`` is setup correctly, we can edit ``config.mk.in``, and remove any unneeded variables
as well as any ``#####`` comment. This file is a template for ``config.mk``, which will contain a description
of all the compiler and library variables needed for our package. Just like ``configure.ac``, the only optional variables
we will keep are again related to the ``STOPCOND`` library and downloading our package.

Once these files are cleaned up, run ``autoreconf`` to (re)create the ``configure`` script, then run
``./configure``. This will test the detection and check for errors. As a sanity check, run ``cat config.mk``
and ensure that there are no ``@VARIABLE@`` symbols left! If there are, check that ``configure.ac`` and
``config.mk.in`` were setup correctly.

.. WARNING::

    Make sure the the ``amuse_tidymess/support/shared/`` folder is a symlink to ``amuse/support/shared/``
    to ensure that there is no code duplication in the codebase, and that bug fixes are propagated to each
    package automatically. This should be done automatically by the ``amusifier`` but can be a source of bugs
    if not setup correctly.

Setting up the Makefile
~~~~~~~~~~~~~~~~~~~~~~~
With our build system detection working, we now need to download ``TIDYMESS`` into ``AMUSE``!
This is where the Makefiles come in. ``AMUSE`` packages typically have 2 Makefiles.


Creating the Interfaces
=======================
With ``TIDYMESS`` compiled into ``AMUSE``, we can now begin the process of creating our interface!
The interface system allows community codes, which are all unique and depend on diverse libraries and
programming languages, to communicate with the ``AMUSE`` framework, which is native Python. ``AMUSE``
interfaces define a number of interface functions, which provide a standardized way for ``AMUSE`` to
communicate with each community code. This way, the experience of using any ``AMUSE`` code is identical:
all codes can be evolved with the ``evolve_model`` method, particles are represented as
``amuse.datamodel.particles``, etc... The strength of ``AMUSE`` lies in its ability to prototype quickly:
If the user wants to see what solution a different code would give for the same calculation, all they have
to do is switch which code they are using, and the script most likely does not need to change.

Therefore, our job when creating an interface is to map the community code functions to the ``AMUSE`` interface
functions. The amusifier already created all the files we need: the ``interface.py`` and the ``interface.cc``.

Defining the Python interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``interface.py`` actually defines two classes: the high-level and low-level Python interfaces. The high-level
interface is what the user interacts with when using the community code. This defines the methods, parameters,
and properties of each community code, and defines how the ``amuse.datamodel.particles`` work within that code.
The ``amusifer`` generates a minimal code stub for the ``interface.py``, which is enough to get us started.
The process of defining our interface starts with figuring out what type of code we are adding to ``AMUSE``.
``AMUSE`` has a set of predefined Python interfaces we can use to build our interface from.


+-----------------------------------+-------------------------------------------+
| Interface:                        | Example codes:                            |
+-----------------------------------+-------------------------------------------+
| ``GravitationDynamicsInterface``  | N-body: Tidymess, Ph4, Huayano            |
+-----------------------------------+-------------------------------------------+
| ``HydrodynamicsInterface``        | Hydrodynamical: Capreole                  |
+-----------------------------------+-------------------------------------------+
| ``MagnetoHydrodynamicsInterface`` | MHD: Athena                               |
+-----------------------------------+-------------------------------------------+
| ``StellarEvolutionInterface``     | Stellar: MESA, EVtwin, SeBa               |
+-----------------------------------+-------------------------------------------+

These interfaces define many
of the required interface functions so that we don't have to.
In this case, ``TIDYMESS`` is a N-Body code, and therefore falls under the
