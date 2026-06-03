import numpy as np
from numpy.typing import NDArray
from amuse.community.interface.common import CommonCode, CommonCodeInterface
import tsunami

from amuse.support.interface import InCodeComponentImplementation
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
    CodeInterface,
    LegacyFunctionSpecification,
    PythonCodeInterface,
    legacy_function,
    remote_function
)
from amuse.support.interface import MethodWithUnitsDefinition
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.units import generic_unit_system, nbody_system


class TsunamiImplementation(object):
    """
    Notes:
        what to do with spin? can be compiled with or without
        what to do with import tsunami
        what to do with setters

    """

    def __init__(self):

        self.tsunami = tsunami.Tsunami()

        # temporary buffers for staging particles
        self._pos_list: list[list[float]] = []
        self._vel_list: list[list[float]] = []
        self._spin_list: list[list[float]] = []
        self._mass_list: list[float] = []
        self._radius_list: list[float] = []

        # commited particles
        self._pos: NDArray = np.empty((0, 3), dtype=np.float64)
        self._vel: NDArray = np.empty((0, 3), dtype=np.float64)
        self._spin: NDArray = np.empty((0, 3), dtype=np.float64)
        self._mass: NDArray = np.empty(0, dtype=np.float64)
        self._radius: NDArray = np.empty(0, dtype=np.float64)
        self._stype: NDArray = np.empty(0, dtype=np.int64)

    def initialize_code(self) -> int:
        return 0

    def cleanup_code(self) -> int:
        return 0

    def commit_parameters(self) -> int:
        self.tsunami.commit_parameters()

        return 0

    def commit_particles(self) -> int:
        """
        Add all particles stored in the particle buffers
        into the Tsunami code. Tsunami does not support
        adding individual particles and instead requires
        preallocated np.ndarrays of particles.

        This method grabs all pre-existing particles in Tsunami
        as well as any particles inside the temporary buffers
        and formats them as a particle set to be read by Tsunami.

        Returns
        -------
        0 : If particles were added to Tsunami succesfully or if no
            new particles are available to be added
        -1 : If less than 2 particles between the pre-existing particles
            and the particles in the buffer, or if the shapes of the
            particleset arrays dont match.
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
            len(self._vel_list) == N_new and
            len(self._spin_list) == N_new and
            len(self._mass_list) == N_new and
            len(self._radius_list) == N_new
        ):
            return -1

        # preallocate particleset for Tsunami
        pos = np.empty((N_total, 3), dtype=np.float64)
        vel = np.empty((N_total, 3), dtype=np.float64)
        spin = np.empty((N_total, 3), dtype=np.float64)
        mass = np.empty(N_total, dtype=np.float64)
        radius = np.empty(N_total, dtype=np.float64)
        stype = np.ones(N_total, dtype=np.int64) * -1

        # add any existing Tsunami particles
        if N_existing != 0:
            pos[:N_existing, :] = self._pos
            vel[:N_existing, :] = self._vel
            spin[:N_existing, :] = self._spin
            mass[:N_existing] = self._mass
            radius[:N_existing] = self._radius

        # add new particles
        pos[N_existing:, :] = np.asarray(self._pos_list, dtype=np.float64).reshape(-1, 3)
        vel[N_existing:, :] = np.asarray(self._vel_list, dtype=np.float64).reshape(-1, 3)
        spin[N_existing:, :] = np.asarray(self._spin_list, dtype=np.float64).reshape(-1, 3)
        mass[N_existing:] = np.asarray(self._mass_list, dtype=np.float64)
        radius[N_existing:] = np.asarray(self._radius_list, dtype=np.float64)

        self.tsunami.add_particle_set(pos, vel, mass, radius, stype, spin)

        self._pos = pos
        self._vel = vel
        self._spin = spin
        self._mass = mass
        self._radius = radius
        self._stype = stype
        self._clear_temporary_particle_buffers()

        return 0

    def recommit_parameters(self) -> int:
        self.tsunami.commit_parameters()

        return 0

    def recommit_particles(self) -> int:
        self.commit_particles()

        return 0

    def evolve_model(self, time) -> int:
        if time <= self.tsunami.time:
            return -1

        self.tsunami.evolve_system(time)

        self.tsunami.sync_internal_state(self._pos, self._vel, self._spin)

        return 0

    def get_state(
        self,
        index_of_the_particle,
        mass,
        x,
        y,
        z,
        vx,
        vy,
        vz,
        radius,
        wx,
        wy,
        wz
    ) -> int:
        i = index_of_the_particle
        mass.value = self._mass[i]
        x.value = self._pos[i,0]
        y.value = self._pos[i,1]
        z.value = self._pos[i,2]
        vx.value = self._vel[i,0]
        vy.value = self._vel[i,1]
        vz.value = self._vel[i,2]
        radius.value = self._radius[i]
        wx.value = self._spin[i,0]
        wy.value = self._spin[i,1]
        wz.value = self._spin[i,2]
        return 0

    def set_state(
        self,
        index_of_the_particle,
        mass,
        x,
        y,
        z,
        vx,
        vy,
        vz,
        radius,
        wx,
        wy,
        wz
    ) -> int:
        # i = index_of_the_particle
        # mass.value = self._mass[i]
        # x.value = self._pos[i,0]
        # y.value = self._pos[i,1]
        # z.value = self._pos[i,2]
        # vx.value = self._vel[i,0]
        # vy.value = self._vel[i,1]
        # vz.value = self._vel[i,2]
        # radius.value = self._radius[i]
        # wx.value = self._spin[i,0]
        # wy.value = self._spin[i,1]
        # wz.value = self._spin[i,2]
        return 0

    def new_particle(
        self,
        index_of_the_particle,
        mass,
        x,
        y,
        z,
        vx,
        vy,
        vz,
        radius,
        wx,
        wy,
        wz,
    ) -> int:
        self._pos_list.append([x, y, z])
        self._vel_list.append([vx, vy, vz])
        self._mass_list.append(mass)
        self._radius_list.append(radius)
        self._spin_list.append([wx, wy, wz])

        index_of_the_particle.value = len(self._pos_list) - 1

        return 0

    def get_position(self, index_of_the_particle, x, y, z) -> int:
        if self._pos.shape[0] == 0:
            return -1

        self.tsunami.sync_internal_state(self._pos, self._vel, self._spin)

        x.value = self._pos[index_of_the_particle, 0]
        y.value = self._pos[index_of_the_particle, 1]
        z.value = self._pos[index_of_the_particle, 2]

        return 0

    def set_position(self, index_of_the_particle, x, y, z) -> int:

        self.tsunami.sync_internal_state(self._pos, self._vel, self._spin)

        self._pos[index_of_the_particle, 0] = x
        self._pos[index_of_the_particle, 1] = y
        self._pos[index_of_the_particle, 2] = z

        self.tsunami.override_position_and_velocities(self._pos, self._vel)

        return 0

    def set_units(self, Mscale, Lscale) -> int:
        """
        Set the mass and length units for Tsunami.

        Used for changing the unit system of
        Tsunami after initialization.
        """
        self.tsunami.set_units(Mscale, Lscale)

        return 0

    def get_mscale(self, Mscale) -> int:
        """
        Get mass unit of Tsunami in MSun.
        """
        Mscale.value = self.tsunami.Mscale

        return 0

    def set_mscale(self, Mscale) -> int:
        """
        Set mass unit of Tsunami in MSun.

        Used for changing the length unit of
        Tsunami after initialization.
        """
        self.tsunami.set_units(Mscale, self.tsunami.Lscale)

        return 0

    def get_lscale(self, Lscale) -> int:
        """
        Get length unit of Tsunami in AU.
        """
        Lscale.value = self.tsunami.Lscale

        return 0

    def set_lscale(self, Lscale) -> int:
        """
        Set length unit of Tsunami in AU.

        Used for changing the length unit of
        Tsunami after initialization.
        """
        self.tsunami.set_units(self.tsunami.Mscale, Lscale)

        return 0

    def get_tscale(self, Tscale) -> int:
        """
        Get time unit of Tsunami in years.
        Derived from Mscale, Lscale, and G=1.

        This value is read only; to set it change
        Mscale and Lscale.
        """
        Tscale.value = self.tsunami.Tscale

        return 0

    def get_vscale(self, Vscale) -> int:
        """
        Get velocity unit of Tsunami in km/s.
        Derived from Mscale, Lscale, and G=1.

        This value is read only; to set it change
        Mscale and Lscale.
        """
        Vscale.value = self.tsunami.Vscale

        return 0

    def get_time(self, time) -> int:
        """
        Get current model time.

        tsunami.time returns time in N-body units.
        """
        time.value = self.tsunami.time
        return 0

    def get_wpn(self, wpn) -> int:
        wpn.value = self.tsunami.Conf.wPNs
        return 0

    def set_wpn(self, wpn) -> int:
        self.tsunami.Conf.wPNs = bool(wpn)
        return 0

    def get_potential_energy(self, potential_energy) -> int:
        potential_energy.value = self.tsunami.pot

        return 0

    def get_kinetic_energy(self, kinetic_energy) -> int:
        kinetic_energy.value = self.tsunami.kin

        return 0

    def get_total_energy(self, total_energy) -> int:
        total_energy.value = self.tsunami.energy

        return 0

    def synchronize_model(self) -> int:
        return 0

    def _clear_temporary_particle_buffers(self) -> None:
        """Clear temporary particle buffers after commiting particles"""
        self._pos_list.clear()
        self._vel_list.clear()
        self._spin_list.clear()
        self._mass_list.clear()
        self._radius_list.clear()

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

    @legacy_function
    def new_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle',
            dtype='int32',
            direction=function.OUT,
            description=(
                'An index assigned to the newly created particle. '
                'This index is supposed to be a local index for the code '
                '(and not valid in other instances of the code or in other codes)'
            ),
        )
        function.addParameter(
            'mass',
            dtype='float64',
            direction=function.IN,
            description='The mass of the particle',
        )
        function.addParameter(
            'x',
            dtype='float64',
            direction=function.IN,
            description='The initial position vector of the particle',
        )
        function.addParameter(
            'y',
            dtype='float64',
            direction=function.IN,
            description='The initial position vector of the particle',
        )
        function.addParameter(
            'z',
            dtype='float64',
            direction=function.IN,
            description='The initial position vector of the particle',
        )
        function.addParameter(
            'vx',
            dtype='float64',
            direction=function.IN,
            description='The initial velocity vector of the particle',
        )
        function.addParameter(
            'vy',
            dtype='float64',
            direction=function.IN,
            description='The initial velocity vector of the particle',
        )
        function.addParameter(
            'vz',
            dtype='float64',
            direction=function.IN,
            description='The initial velocity vector of the particle',
        )
        function.addParameter(
            'radius',
            dtype='float64',
            direction=function.IN,
            description='The radius of the particle',
            default=0,
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.IN,
            description='The initial spin vector of the particle',
            default=0
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.IN,
            description='The initial spin vector of the particle',
            default=0
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.IN,
            description='The initial spin vector of the particle',
            default=0
        )
        function.result_type = 'int32'
        function.can_handle_array = True
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
        function.addParameter(
            'time',
            dtype='float64',
            direction=function.OUT,
            description='time to evolve to'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            System was evolved to time
        -1 - ERROR
            Requested time is <= current model time
        """
        return function


    @remote_function(can_handle_array=True)
    def get_state(
        index_of_the_particle='i'
    ):
        returns (
            mass='d',
            x='d', y='d', z='d',
            vx='d', vy='d', vz='d',
            radius='d',
            wx='d', wy='d', wz='d'
        )


    # @legacy_function
    # def get_state():
    #     """
    #     Retrieve the current state of a particle. The *minimal* information of
    #     a stellar dynamics particle (mass, radius, position and velocity) is
    #     returned.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.can_handle_array = True
    #     function.addParameter(
    #         'index_of_the_particle',
    #         dtype='int32',
    #         direction=function.IN,
    #         description=(
    #             "Index of the particle to get the state from. This index must "
    #             "have been returned by an earlier call to :meth:`new_particle`"
    #         ),
    #     )
    #     function.addParameter(
    #         'mass',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current mass of the particle',
    #     )
    #     function.addParameter(
    #         'x',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current position vector of the particle',
    #     )
    #     function.addParameter(
    #         'y',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current position vector of the particle',
    #     )
    #     function.addParameter(
    #         'z',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current position vector of the particle',
    #     )
    #     function.addParameter(
    #         'vx',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current velocity vector of the particle',
    #     )
    #     function.addParameter(
    #         'vy',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current velocity vector of the particle',
    #     )
    #     function.addParameter(
    #         'vz',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current velocity vector of the particle',
    #     )
    #     function.addParameter(
    #         'radius',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current radius of the particle',
    #     )
    #     function.addParameter(
    #         'wx',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current spin of the particle',
    #     )
    #     function.addParameter(
    #         'wy',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current spin of the particle',
    #     )
    #     function.addParameter(
    #         'wz',
    #         dtype='float64',
    #         direction=function.OUT,
    #         description='The current spin of the particle',
    #     )
    #     function.result_type = 'int32'
    #     function.result_doc = """
    #     0 - OK
    #         particle was removed from the model
    #     -1 - ERROR
    #         particle could not be found
    #     """
    #     return function

    @legacy_function
    def set_state():
        """
        Update the current state of a particle. The *minimal* information of a
        stellar dynamics particle (mass, radius, position and velocity) is
        updated.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle',
            dtype='int32',
            direction=function.IN,
            description=(
                "Index of the particle for which the state is to be updated. "
                "This index must have been returned by an earlier call to "
                ":meth:`new_particle`"
            ),
        )
        function.addParameter(
            'mass',
            dtype='float64',
            direction=function.IN,
            description='The new mass of the particle',
        )
        function.addParameter(
            'x',
            dtype='float64',
            direction=function.IN,
            description='The new position vector of the particle',
        )
        function.addParameter(
            'y',
            dtype='float64',
            direction=function.IN,
            description='The new position vector of the particle',
        )
        function.addParameter(
            'z',
            dtype='float64',
            direction=function.IN,
            description='The new position vector of the particle',
        )
        function.addParameter(
            'vx',
            dtype='float64',
            direction=function.IN,
            description='The new velocity vector of the particle',
        )
        function.addParameter(
            'vy',
            dtype='float64',
            direction=function.IN,
            description='The new velocity vector of the particle',
        )
        function.addParameter(
            'vz',
            dtype='float64',
            direction=function.IN,
            description='The new velocity vector of the particle',
        )
        function.addParameter(
            'radius',
            dtype='float64',
            direction=function.IN,
            description='The new radius of the particle',
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.IN,
            description='The current spin of the particle',
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.IN,
            description='The current spin of the particle',
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.IN,
            description='The current spin of the particle',
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the information was set
        -1 - ERROR
            particle could not be found
        """
        return function


class Tsunami(GravitationalDynamics, GravityFieldCode):
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
        # for example:
        # handler.set_initial_state('UNINITIALIZED')
        # handler.add_transition('!UNINITIALIZED!STOPPED', 'END', 'cleanup_code')
        # handler.add_transition('END', 'STOPPED', 'stop', False)
        # handler.add_transition(
        #     'UNINITIALIZED', 'INITIALIZED', 'initialize_code')
        # handler.add_method('STOPPED', 'stop')
        pass

    def define_properties(self, handler):
        # handler.add_property('name_of_the_getter', public_name="name_of_the_property")
        pass

    def define_methods(self, handler):
        """
        Map legacy functions in TsunamiInterface into
        Tsunami user methods.
        """

        GravitationalDynamics.define_methods(self, handler)

        handler.add_method(
            'new_particle',
            (
                generic_unit_system.mass,
                generic_unit_system.length,
                generic_unit_system.length,
                generic_unit_system.length,
                generic_unit_system.speed,
                generic_unit_system.speed,
                generic_unit_system.speed,
                generic_unit_system.length,        # radius
                1 / generic_unit_system.time,      # wx
                1 / generic_unit_system.time,      # wy
                1 / generic_unit_system.time,      # wz
                handler.NO_UNIT,                   # stype
            ),
            (handler.INDEX, handler.ERROR_CODE)
        )

    def define_parameters(self, handler):
        """Define model parameters.

        These have a native function for getting their value, another one for setting,
        and a name, description and default value. Functions with the appropriate names
        must be defined in the native wrapper code.
        """
        # handler.add_method_parameter(
        #     "name_of_the_getter",
        #     "name_of_the_setter",
        #     "parameter_name",
        #     "description",
        #     default_value = <default value>
        # )
        pass

    def define_particle_sets(self, handler):
        """Define any particle sets inside the model."""
        # handler.define_set('particles', 'index_of_the_particle')
        # handler.set_new('particles', 'new_particle')
        # handler.set_delete('particles', 'delete_particle')
        # handler.add_setter('particles', 'set_state')
        # handler.add_getter('particles', 'get_state')
        # handler.add_setter('particles', 'set_mass')
        # handler.add_getter('particles', 'get_mass', names=('mass',))
        pass

    def define_grids(self, handler):
        """Define any grids inside the model."""
        # handler.define_grid('grid',axes_names = ["x", "y"], grid_class=StructuredGrid)
        # handler.set_grid_range('grid', '_grid_range')
        # handler.add_getter('grid', 'get_grid_position', names=["x", "y"])
        # handler.add_getter('grid', 'get_rho', names=["density"])
        # handler.add_setter('grid', 'set_rho', names=["density"])
        pass

    # def define_converter(self, handler):
        # """Handle unit conversion if an (optional) unit converter is specified."""
        #     if self.unit_converter is not None:
        #         handler.set_converter(
        #             self.unit_converter.as_converter_from_si_to_generic()
        #         )
