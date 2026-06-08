import numpy as np
import tsunami

from amuse.community.interface.common import CommonCode, CommonCodeInterface
from amuse.community.interface.gd import (
    GravitationalDynamics,
    GravitationalDynamicsInterface,
    GravityFieldCode,
    GravityFieldInterface
)
from amuse.community.interface.stopping_conditions import (
    StoppingConditions,
    StoppingConditionInterface
)
from amuse.rfi.core import (
    LegacyFunctionSpecification,
    PythonCodeInterface,
    legacy_function,
    remote_function
)
from amuse.rfi.python_code import ValueHolder
from amuse.support.interface import InCodeComponentImplementation
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.units import nbody_system as ns


class TsunamiImplementation(object):

    def __init__(self):
        # hard code N-Body units to Lscale = Mscale = 1
        self.tsunami = tsunami.Tsunami(1, 1)

        # temporary buffers for staging particles
        self._mass_list: list[float] = []
        self._radius_list: list[float] = []
        self._pos_list: list[list[float]] = []
        self._vel_list: list[list[float]] = []
        self._spin_list: list[list[float]] = []
        self._id_list: list[int] = []

        # commited particle arrays
        self._mass = np.empty(0, dtype=np.float64)
        self._radius = np.empty(0, dtype=np.float64)
        self._pos = np.empty((0, 3), dtype=np.float64)
        self._vel = np.empty((0, 3), dtype=np.float64)
        self._spin = np.empty((0, 3), dtype=np.float64)
        self._stype = np.empty(0, dtype=np.int64)
        self._ids = np.empty(0, dtype=np.int32)

        self._next_particle_id = 0

    def initialize_code(self) -> int:
        return 0

    def cleanup_code(self) -> int:
        """Deallocate Tsunami particles."""
        self._clear_temporary_particle_buffers()
        return 0

    def commit_parameters(self) -> int:
        """Commit Tsunami parameters."""
        self.tsunami.commit_parameters()
        return 0

    def commit_particles(self) -> int:
        """
        Add all particles stored in the particle buffers
        into the TSUNAMI code. TSUNAMI does not support
        adding individual particles and instead requires
        preallocated np.ndarrays of particles.

        This method grabs all pre-existing particles in TSUNAMI
        as well as any new particles inside the temporary buffers
        and formats them as numpy arrays to be read by TSUNAMI.

        This method should only be called after 2 new particles were added.
        Calling this method with no new particles in the buffers does nothing.

        Returns
        -------
         0 : If particles were added to TSUNAMI succesfully or if no
             new particles are available to be added.
        -1 : If the shapes of the particleset arrays dont match.

        Raises
        ------
        ValueError :
            If the total particle count is less than 2 particles between
            the pre-existing particles and the particles in the buffer.
        """
        N_existing: int = self._pos.shape[0]
        N_new: int = len(self._pos_list)
        N_total: int = N_existing + N_new

        if N_new == 0:
            return 0

        if N_total < 2:
            raise ValueError(
                'Tsunami needs at least 2 particles when commiting!'
            )

        if not (
            len(self._mass_list) == N_new and
            len(self._radius_list) == N_new and
            len(self._vel_list) == N_new and
            len(self._spin_list) == N_new and
            len(self._id_list) == N_new
        ):
            return -1

        # preallocate particleset for Tsunami
        mass = np.empty(N_total, dtype=np.float64)
        radius = np.empty(N_total, dtype=np.float64)
        pos = np.empty((N_total, 3), dtype=np.float64)
        vel = np.empty((N_total, 3), dtype=np.float64)
        spin = np.empty((N_total, 3), dtype=np.float64)
        stype = np.ones(N_total, dtype=np.int64) * -1
        ids = np.empty(N_total, dtype=np.int32)

        # add any existing Tsunami particles
        if N_existing != 0:
            mass[:N_existing] = self._mass
            radius[:N_existing] = self._radius
            pos[:N_existing, :] = self._pos
            vel[:N_existing, :] = self._vel
            spin[:N_existing, :] = self._spin
            ids[:N_existing] = self._ids

        # add new particles
        mass[N_existing:] = np.asarray(self._mass_list, dtype=np.float64)
        radius[N_existing:] = np.asarray(self._radius_list, dtype=np.float64)
        pos[N_existing:, :] = np.asarray(self._pos_list, dtype=np.float64).reshape(-1, 3)
        vel[N_existing:, :] = np.asarray(self._vel_list, dtype=np.float64).reshape(-1, 3)
        spin[N_existing:, :] = np.asarray(self._spin_list, dtype=np.float64).reshape(-1, 3)
        ids[N_existing:] = np.asarray(self._id_list, dtype=np.int32)

        self.tsunami.add_particle_set(pos, vel, mass, radius, stype, spin)

        self._mass = mass
        self._radius = radius
        self._pos = pos
        self._vel = vel
        self._spin = spin
        self._stype = stype
        self._ids = ids
        self._clear_temporary_particle_buffers()
        self.synchronize_model()

        return 0

    def recommit_parameters(self) -> int:
        """Recommit parameters after commiting them."""
        self.tsunami.commit_parameters()
        return 0

    def recommit_particles(self) -> int:
        """Recommit particles after commiting them."""
        self.commit_particles()
        return 0

    def evolve_model(self, time: float) -> int:
        """
        Evolve the system to a specified final time.

        Parameters
        ----------
        time : float
            Time to evolve to.

        Returns
        -------
         0 : If the evolution is succesful.
        -1 : If `time` <= current model time.
        """
        if time <= self.tsunami.time:
            return -1

        self.tsunami.evolve_system(time)
        self.synchronize_model()

        return 0

    def evolve_model_dtmax(self, time: float) -> int:
        """
        Evolves the system for a single integration step,
        ensuring that the system time does not exceed the
        specified target `time`. This method is especially
        useful when precise control over the maximum timestep
        is needed, such as in visualizations or applications
        requiring fixed time intervals.

        Unlike evolve_system(), this method performs only one
        integration step and adapts the timestep to ensure
        it does not exceed `time`. If the integration requires
        a shorter timestep, it may stop well before `time`.

        Parameters
        ----------
        time : float
            Time to evolve to.

        Returns
        -------
         0 : If the evolution is succesful.
        -1 : If `time` <= current model time.
        """
        if time <= self.tsunami.time:
            return -1

        self.tsunami.evolve_system_dtmax(time)
        self.synchronize_model()

        return 0

    def synchronize_model(self) -> int:
        """
        Synchronize TsunamiImplementation with TSUNAMI.
        This ensures that the current particle state in
        AMUSE matches the current state of TSUNAMI.

        Call this function before accessing values to ensure
        that the returned values are up to date.
        """
        self.tsunami.sync_internal_state(self._pos, self._vel, self._spin)
        return 0

    def new_particle(
        self,
        index_of_the_particle: ValueHolder,
        mass: float,
        radius: float,
        x: float, y: float, z: float,
        vx: float, vy: float, vz: float,
        wx: float, wy: float, wz: float
    ) -> int:
        """
        Add a new particle to TSUNAMI.

        The particles are added to a temporary buffer,
        and are only added to TSUNAMI upon calling
        `commit_particles` or `recommit_particles`.

        Parameters
        ----------
        index_of_the_particle : ValueHolder[int]
             ValueHolder instance to return the index
             of the new particle.
        mass : float
            Particle mass.
        radius : float
            Particle radius.
        x, y, z : float
            Particle position.
        vx, vy, vz : float
            Particle velocity.
        wx, wy, wz : float
            Particle spin.

        Returns
        -------
        0 : Particle was created successfully.
        """
        self._mass_list.append(mass)
        self._radius_list.append(radius)
        self._pos_list.append([x, y, z])
        self._vel_list.append([vx, vy, vz])
        self._spin_list.append([wx, wy, wz])

        index_of_the_particle.value = len(self._pos_list) - 1

        return 0

    def get_state(
        self,
        index_of_the_particle: int,
        mass: ValueHolder,
        radius: ValueHolder,
        x: ValueHolder, y: ValueHolder, z: ValueHolder,
        vx: ValueHolder, vy: ValueHolder, vz: ValueHolder,
        wx: ValueHolder, wy: ValueHolder, wz: ValueHolder
    ) -> int:
        """
        Retrieve the state of a particle.

        Parameters
        ----------
        index_of_the_particle : int
            Particle index as returned by `new_particle`.
        mass : ValueHolder[float]
            ValueHolder instance to return the mass value.
        radius : ValueHolder[float]
            ValueHolder instance to return the radius value.
        x, y, z : ValueHolder[float]
            ValueHolder instance to return the particle position.
        vx, vy, vz : ValueHolder[float]
            ValueHolder instance to return the particle velocity.
        wx, wy, wz : ValueHolder[float]
            ValueHolder instance to return the particle spin.

        Returns
        -------
        0 : State was retrieved successfully.

        Raises
        ------
        ValueError : If `index_of_the_particle` is not valid.
        """
        i = index_of_the_particle
        self._validate_particle_index(i)

        self.synchronize_model()

        mass.value = self._mass[i]
        radius.value = self._radius[i]
        x.value = self._pos[i,0]
        y.value = self._pos[i,1]
        z.value = self._pos[i,2]
        vx.value = self._vel[i,0]
        vy.value = self._vel[i,1]
        vz.value = self._vel[i,2]
        wx.value = self._spin[i,0]
        wy.value = self._spin[i,1]
        wz.value = self._spin[i,2]
        return 0

    def set_state(
        self,
        index_of_the_particle: int,
        mass: float,
        radius: float,
        x: float, y: float, z: float,
        vx: float, vy: float, vz: float,
        wx: float, wy: float, wz: float
    ) -> int:
        """
        Set the state of a particle.

        Parameters
        ----------
        index_of_the_particle : int
            Particle index as returned by `new_particle`.
        mass : float
            Particle mass.
        radius : float
            Particle radius.
        x, y, z : float
            Particle position.
        vx, vy, vz : float
            Particle velocity.
        wx, wy, wz : float
            Particle spin.

        Returns
        -------
        0 : State was retrieved successfully.

        Raises
        ------
        ValueError : If `index_of_the_particle` is not valid.
        """
        i = index_of_the_particle
        self._validate_particle_index(i)

        self._mass[i] = mass
        self._radius[i] = radius
        self._pos[i,0] = x
        self._pos[i,1] = y
        self._pos[i,2] = z
        self._vel[i,0] = vx
        self._vel[i,1] = vy
        self._vel[i,2] = vz
        self._spin[i,0] = wx
        self._spin[i,1] = wy
        self._spin[i,2] = wz

        self.tsunami.override_masses(self._mass)
        self.tsunami.override_position_and_velocities(self._pos, self._vel)

        return 0

    def get_position(
        self,
        index_of_the_particle: int,
        x: ValueHolder,
        y: ValueHolder,
        z: ValueHolder
    ) -> int:
        """
        Retrieve the position of a particle.

        Parameters
        ----------
        index_of_the_particle : int
            Particle index as returned by `new_particle`.
        x, y, z : ValueHolder[float]
            ValueHolder instance to return the position
            of the particle.

        Returns
        -------
        0 : If position was set.

        Raises
        ------
        ValueError : If `index_of_the_particle` is not valid.
        """
        if self._pos.shape[0] == 0:
            return -1

        self.synchronize_model()

        x.value = self._pos[index_of_the_particle, 0]
        y.value = self._pos[index_of_the_particle, 1]
        z.value = self._pos[index_of_the_particle, 2]

        return 0

    def set_position(
        self, index_of_the_particle: int, x: float, y: float, z: float
    ) -> int:
        """
        Set the position of a particle. Ensure to update its mass first!

        Parameters
        ----------
        index_of_the_particle : int
            Particle index as returned by `new_particle`.
        x, y, z : float
            Particle position.

        Returns
        -------
        0 : If position was set.

        Raises
        ------
        ValueError : If `index_of_the_particle` is not valid.
        """
        self._validate_particle_index(index_of_the_particle)

        self._pos[index_of_the_particle, 0] = x
        self._pos[index_of_the_particle, 1] = y
        self._pos[index_of_the_particle, 2] = z

        self.tsunami.override_position_and_velocities(self._pos, self._vel)

        return 0

    def get_mscale(self, Mscale: ValueHolder) -> int:
        """
        Get mass unit of Tsunami in MSun.
        """
        Mscale.value = self.tsunami.Mscale

        return 0

    def get_lscale(self, Lscale: ValueHolder) -> int:
        """
        Get length unit of Tsunami in AU.
        """
        Lscale.value = self.tsunami.Lscale

        return 0

    def get_tscale(self, Tscale: ValueHolder) -> int:
        """
        Get time unit of Tsunami in years.
        Derived from Mscale, Lscale, and G=1.

        This value is read only.
        """
        Tscale.value = self.tsunami.Tscale

        return 0

    def get_vscale(self, Vscale: ValueHolder) -> int:
        """
        Get velocity unit of Tsunami in km/s.
        Derived from Mscale, Lscale, and G=1.

        This value is read only.
        """
        Vscale.value = self.tsunami.Vscale

        return 0

    def get_time(self, time: ValueHolder) -> int:
        """
        Get current model time.

        tsunami.time returns time in N-body units.
        """
        time.value = self.tsunami.time
        return 0

    def get_alpha(self, alpha: ValueHolder) -> int:
        alpha.value = self.tsunami.Conf.alpha
        return 0

    def set_alpha(self, alpha: float) -> int:
        self.tsunami.Conf.alpha = alpha
        return 0

    def get_beta(self, beta: ValueHolder) -> int:
        beta.value = self.tsunami.Conf.beta
        return 0

    def set_beta(self, beta: float) -> int:
        self.tsunami.Conf.beta = beta
        return 0

    def get_gamma(self, gamma: ValueHolder) -> int:
        gamma.value = self.tsunami.Conf.gamma
        return 0

    def set_gamma(self, gamma: float) -> int:
        self.tsunami.Conf.gamma = gamma
        return 0

    def get_pn(self, pn: ValueHolder) -> int:
        pn.value = self.tsunami.Conf.wPNs
        return 0

    def set_pn(self, pn: bool) -> int:
        self.tsunami.Conf.wPNs = bool(pn)
        return 0

    def get_pn1(self, pn1: ValueHolder) -> int:
        pn1.value = self.tsunami.Conf.pn1
        return 0

    def set_pn1(self, pn1: bool) -> int:
        self.tsunami.Conf.pn1 = bool(pn1)
        return 0

    def get_pn2(self, pn2: ValueHolder) -> int:
        pn2.value = self.tsunami.Conf.pn2
        return 0

    def set_pn2(self, pn2: bool) -> int:
        self.tsunami.Conf.pn2 = bool(pn2)
        return 0

    def get_pn25(self, pn25: ValueHolder) -> int:
        pn25.value = self.tsunami.Conf.pn25
        return 0

    def set_pn25(self, pn25: bool) -> int:
        self.tsunami.Conf.pn25 = bool(pn25)
        return 0

    def get_pn3(self, pn3: ValueHolder) -> int:
        pn3.value = self.tsunami.Conf.pn3
        return 0

    def set_pn3(self, pn3: bool) -> int:
        self.tsunami.Conf.pn3 = bool(pn3)
        return 0

    def get_pn35(self, pn35: ValueHolder) -> int:
        pn35.value = self.tsunami.Conf.pn35
        return 0

    def set_pn35(self, pn35: bool) -> int:
        self.tsunami.Conf.pn35 = bool(pn35)
        return 0

    def get_potential_energy(self, potential_energy: ValueHolder) -> int:
        potential_energy.value = self.tsunami.pot

        return 0

    def get_kinetic_energy(self, kinetic_energy: ValueHolder) -> int:
        kinetic_energy.value = self.tsunami.kin

        return 0

    def get_total_energy(self, total_energy: ValueHolder) -> int:
        total_energy.value = self.tsunami.energy

        return 0

    def _validate_particle_index(self, i) -> None:
        """
        Validate that the requested particle index
        refers to a particle in Tsunami.
        """
        if not 0 <= i < len(self._pos):
            raise ValueError(
                f'Incorrect index of the particle! Max index: {len(self._pos) - 1}'
            )

    def _clear_temporary_particle_buffers(self) -> None:
        """Clear temporary particle buffers after commiting particles"""
        self._mass_list.clear()
        self._radius_list.clear()
        self._pos_list.clear()
        self._vel_list.clear()
        self._spin_list.clear()

class TsunamiInterface(
    PythonCodeInterface,
    GravitationalDynamicsInterface,
    GravityFieldInterface,
    LiteratureReferencesMixIn,
):
    """
    Description of the interface with the community code.

    This class describes a set of functions in C++ or Fortran that are part of the AMUSE
    wrapper of the community code. These functions in turn will call functions in the
    community code, or update variables in it directly.

    These functions will be called by the worker program when it receives the
    corresponding request from the Python part of AMUSE.
    """

    # include_headers = ['tsunami_worker.h', 'stopcond.h']

    def __init__(self, **kwargs):
        PythonCodeInterface.__init__(
            self,
            TsunamiImplementation,
            'tsunami_worker',
            **kwargs
        )
        LiteratureReferencesMixIn.__init__(self)

    @remote_function
    def evolve_model_dtmax(time='d'):
        returns ()

    @legacy_function
    def new_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.OUT)
        for name in ['mass', 'radius', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'wx', 'wy', 'wz']:
            function.addParameter(name, dtype='d', direction=function.IN)
        function.result_type = 'i'
        function.result_doc = """
        0 - OK
            particle was added to Tsunami
        -1 - ERROR
            particle could not be added
        """
        return function

    @legacy_function
    def get_time():
        function = LegacyFunctionSpecification()
        function.addParameter('time', dtype='d', direction=function.OUT)
        function.result_type = 'i'
        function.result_doc = """
        0 - OK
            System was evolved to time
        -1 - ERROR
            Requested time is <= current model time
        """
        return function

    @legacy_function
    def get_state():
        """
        Retrieve the current state of a particle. The *minimal* information of
        a stellar dynamics particle (mass, radius, position and velocity) is
        returned.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        for name in ['mass', 'radius', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'wx', 'wy', 'wz']:
            function.addParameter(name, dtype='d', direction=function.OUT)
        function.result_type = 'i'
        function.result_doc = """
        0 - OK
            particle was removed from the model
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def set_state():
        """
        Update the current state of a particle. The *minimal* information of a
        stellar dynamics particle (mass, radius, position and velocity) is
        updated.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        for name in ['mass', 'radius', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'wx', 'wy', 'wz']:
            function.addParameter(name, dtype='d', direction=function.IN)
        function.result_type = 'i'
        function.result_doc = """
        0 - OK
            particle was found in the model and the information was set
        -1 - ERROR
            particle could not be found
        """
        return function

    @remote_function
    def get_alpha():
        returns (alpha='d')

    @remote_function
    def set_alpha(alpha='d'):
        returns ()

    @remote_function
    def get_beta():
        returns (beta='d')

    @remote_function
    def set_beta(beta='d'):
        returns ()

    @remote_function
    def get_gamma():
        returns (gamma='d')

    @remote_function
    def set_gamma(gamma='d'):
        returns ()

    @remote_function
    def get_pn():
        returns (pn='b')

    @remote_function
    def set_pn(pn='b'):
        returns ()

    @remote_function
    def get_pn1():
        returns (pn1='b')

    @remote_function
    def set_pn1(pn1='b'):
        returns ()

    @remote_function
    def get_pn2():
        returns (pn2='b')

    @remote_function
    def set_pn2(pn2='b'):
        returns ()

    @remote_function
    def get_pn25():
        returns (pn25='b')

    @remote_function
    def set_pn25(pn25='b'):
        returns ()

    @remote_function
    def get_pn3():
        returns (pn3='b')

    @remote_function
    def set_pn3(pn3='b'):
        returns ()

    @remote_function
    def get_pn35():
        returns (pn35='b')

    @remote_function
    def set_pn35(pn35='b'):
        returns ()

class Tsunami(GravitationalDynamics, GravityFieldCode, CommonCode):
    """One line description of this code

    Some more details about what it does, any special features it has beyond the
    standard interfaces, and anything else the user needs to know.
    """
    def __init__(self, convert_nbody=None, **options):
        """Create a Tsunami instance to run simulations with."""
        super().__init__(self,  TsunamiInterface(**options), **options)

        legacy_interface = TsunamiInterface(**options)

        GravitationalDynamics.__init__(
            self,
            legacy_interface,
            convert_nbody,
            **options
        )

    # the following alternative __init__ is appropiate for codes that use an unspecified
    # unit system (i.e. the quantities have dimension but no definite scale)
    #
    # def __init__(self, unit_converter=None, **options):
    #     self.unit_converter = unit_converter
    #     super().__init__(self,  tsunamiInterface(**options), **options)
    #
    # in this case you also need to use the define_converter below

    # typically the high level specification also contains the following:

    def define_state(self, handler):
        """Define the state model of the code."""
        GravitationalDynamics.define_state(self, handler)
        GravityFieldCode.define_state(self, handler)

    def define_properties(self, handler):
        handler.add_property('get_time', public_name='model_time')

    def define_methods(self, handler):
        """
        Map legacy functions in TsunamiInterface into
        Tsunami user methods.
        """

        GravitationalDynamics.define_methods(self, handler)

        handler.add_method(
            'evolve_model_dtmax',
            (ns.time,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'new_particle',
            (
                ns.mass,
                ns.length,
                ns.length, ns.length, ns.length,
                ns.speed, ns.speed, ns.speed,
                1 / ns.time, 1 / ns.time, 1 / ns.time,
            ),
            (handler.INDEX, handler.ERROR_CODE)
        )

        handler.add_method(
            'get_state',
            (handler.INDEX,),
            (
                ns.mass,
                ns.length,
                ns.length, ns.length, ns.length,
                ns.speed, ns.speed, ns.speed,
                1 / ns.time, 1 / ns.time, 1 / ns.time,
                handler.ERROR_CODE
            ),
        )

        handler.add_method(
            'set_state',
            (
                handler.INDEX,
                ns.mass,
                ns.length,
                ns.length, ns.length, ns.length,
                ns.speed, ns.speed, ns.speed,
                1 / ns.time, 1 / ns.time, 1 / ns.time,
            ),
            (handler.ERROR_CODE,)
        )

    def define_parameters(self, handler):
        """Define model parameters.

        These have a native function for getting their value, another one for setting,
        and a name, description and default value. Functions with the appropriate names
        must be defined in the native wrapper code.
        """
        handler.add_method_parameter(
            'get_alpha',
            'set_alpha',
            'alpha',
            'alpha regularization parameter.',
            default_value=1.0
        )

        handler.add_method_parameter(
            'get_beta',
            'set_beta',
            'beta',
            'beta regularization parameter.',
            default_value=0.0
        )

        handler.add_method_parameter(
            'get_gamma',
            'set_gamma',
            'gamma',
            'gamma regularization parameter.',
            default_value=0.0
        )

        handler.add_method_parameter(
            'get_pn',
            'set_pn',
            'pn',
            'enable post newtonian corrections',
            default_value=False
        )

        handler.add_method_parameter(
            'get_pn1',
            'set_pn1',
            'pn1',
            'enable post newtonian corrections of order 1',
            default_value=True
        )

        handler.add_method_parameter(
            'get_pn2',
            'set_pn2',
            'pn2',
            'enable post newtonian corrections of order 2',
            default_value=True
        )

        handler.add_method_parameter(
            'get_pn25',
            'set_pn25',
            'pn25',
            'enable post newtonian corrections of order 2.5',
            default_value=True
        )

        handler.add_method_parameter(
            'get_pn3',
            'set_pn3',
            'pn3',
            'enable post newtonian corrections of order 3',
            default_value=True
        )

        handler.add_method_parameter(
            'get_pn35',
            'set_pn35',
            'pn35',
            'enable post newtonian corrections of order 3.5',
            default_value=True
        )
        # GravitationalDynamics.define_parameters(self, handler)


    def define_particle_sets(self, handler):
        """Define any particle sets inside the model."""
        GravitationalDynamics.define_particle_sets(self, handler)
        # handler.define_set('particles', 'index_of_the_particle')
        # handler.set_new('particles', 'new_particle')
        # handler.set_delete('particles', 'delete_particle')
        # handler.add_setter('particles', 'set_state')
        # handler.add_getter('particles', 'get_state')
        # handler.add_setter('particles', 'set_mass')
        # handler.add_getter('particles', 'get_mass', names=('mass',))

    def define_converter(self, handler):
        """Handle unit conversion if an (optional) unit converter is specified."""
        if self.unit_converter is not None:
            handler.set_converter(
                self.unit_converter.as_converter_from_si_to_generic()
            )
