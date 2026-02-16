from enum import IntEnum
import numpy as np
from amuse.support.interface import InCodeComponentImplementation
from amuse.community.interface.gd import GravitationalDynamics
from amuse.community.interface.gd import GravitationalDynamicsInterface
from amuse.community.interface.gd import GravityFieldInterface
from amuse.community.interface.gd import GravityFieldCode
from amuse.community.interface.stopping_conditions import StoppingConditions, StoppingConditionInterface
from amuse.rfi.core import CodeInterface, legacy_function, LegacyFunctionSpecification
from amuse.support.interface import MethodWithUnitsDefinition
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.units import generic_unit_system, nbody_system


class TsunamiPtype(IntEnum):
    LOW_MASS_MS = 0
    HIGH_MASS_MS = 1
    HGAP = 2
    GIANT_BRANCH = 3
    CORE_HE_BURN = 4
    EARLY_AGBe = 5
    TP_AGB = 6
    NAKED_HE = 7
    NAKED_HE_HGAP = 8
    NAKED_HE_GIANT = 9
    HE_WD = 10
    CO_WD = 11
    ONE_WD = 12
    NS = 13
    BH = 14
    # planets
    ROCKY = 100
    GAS_GIANT = 101
    # null
    UNCLASSIFIED = -1

class TsunamiInterface(
    CodeInterface,
    LiteratureReferencesMixIn,
    GravitationalDynamicsInterface,
    StoppingConditionInterface,
):
    """
    Description of the interface with the community code.

    This class describes a set of functions in C++ or Fortran that are part of the AMUSE
    wrapper of the community code. These functions in turn will call functions in the
    community code, or update variables in it directly.

    These functions will be called by the worker program when it receives the
    corresponding request from the Python part of AMUSE.
    """

    include_headers = ['tsunami_worker.h', 'stopcond.h']

    def __init__(self, **keyword_arguments):
        CodeInterface.__init__(
            self, name_of_the_worker='tsunami_worker', **keyword_arguments
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
        function.addParameter(
            'stype',
            dtype='float64',
            direction=function.IN,
            description='The physical type of the particle',
            default=0
        )
        function.result_type = 'int32'
        function.can_handle_array = True
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
