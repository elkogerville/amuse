from amuse.community.interface.gd import GravitationalDynamics
from amuse.community.interface.gd import GravitationalDynamicsInterface
#from amuse.community.interface.gd import GravityFieldInterface
from amuse.community.interface.gd import GravityFieldCode
from amuse.community.interface.stopping_conditions import StoppingConditions, StoppingConditionInterface
from amuse.rfi.core import CodeInterface, legacy_function, LegacyFunctionSpecification
from amuse.support.interface import MethodWithUnitsDefinition
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.units import nbody_system

class TidymessInterface(
    CodeInterface,
    LiteratureReferencesMixIn,
    GravitationalDynamicsInterface,
    StoppingConditionInterface,
    #GravityFieldInterface
):
    """

    """

    include_headers = ['tidymess_worker.h', 'stopcond.h']


    def __init__(self, **options):
        CodeInterface.__init__(
            self, name_of_the_worker='tidymess_worker', **options
        )
        LiteratureReferencesMixIn.__init__(self)


    @legacy_function
    def new_particle():
        '''
        Define a new particle in the stellar dynamics code. The particle is
        initialized with the provided mass, radius, position, velocity, moment
        of inertia factor, fluid love number, fluid relaxation time, spin, and
        magnetic breaking coefficient. This function returns an index that can
        be used to refer to this particle.
        '''
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
            dtype='float64', direction=function.IN,
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
            'xi',
            dtype='float64',
            direction=function.IN,
            description='Moment of inertia factor',
            default=0
        )
        function.addParameter(
            'kf',
            dtype='float64',
            direction=function.IN,
            description='Fluid Love number from potential',
            default=0
        )
        function.addParameter(
            'tau',
            dtype='float64',
            direction=function.IN,
            description='Fluid relaxation time',
            default=0
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.IN,
            description='Spin',
            default=0
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.IN,
            description='Spin',
            default=0
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.IN,
            description='Spin',
            default=0
        )
        function.addParameter(
            'a_mb',
            dtype='float64',
            direction=function.IN,
            description='Magnetic braking coefficient',
            default=0
        )
        function.addParameter(
            'id',
            dtype='int32',
            direction=function.IN,
            description=(
                'Identifier of the particle, '
                'option for restoring state after loading'
            ),
            default=-1,
        )
        function.result_type = 'int32'
        function.result_doc = '''\
            0 - OK
                particle was created and added to the model
        -1 - ERROR
                particle could not be created
        '''

        return function


    @legacy_function
    def get_spin():
        '''
        Retrieve the spin vector of a particle. Spin is a vector
        property, this function has 3 OUT arguments.
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'index_of_the_particle',
            dtype='int32',
            direction=function.IN,
            description=(
                'Index of the particle to get the state from. This index must '
                'have been returned by an earlier call to :meth:`new_particle`'
            )
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.OUT,
            description='The current spin vector of the particle'
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.OUT,
            description='The current spin vector of the particle'
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.OUT,
            description='The current spin vector of the particle'
        )
        function.result_type = 'int32'
        function.can_handle_array = True
        function.result_doc = '''\
            0 - OK
                current value was retrieved
        -1 - ERROR
                particle could not be found
        -2 - ERROR
                not yet implemented
        '''

        return function


    @legacy_function
    def set_spin():
        '''
        Update the spin of a particle.
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'index_of_the_particle',
            dtype='int32',
            direction=function.IN,
            description=(
                'Index of the particle for which the state is to be updated. '
                'This index must have been returned by an earlier call to '
                ':meth:`new_particle`'
            )
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.IN,
            description='The new spin vector of the particle'
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.IN,
            description='The new spin vector of the particle'
            )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.IN,
            description='The new spin vector of the particle'
        )
        function.result_type = 'int32'
        function.can_handle_array = True
        function.result_doc = '''\
            0 - OK
                particle was found in the model and the information was set
        -1 - ERROR
                particle could not be found
        -2 - ERROR
                code does not support updating of a particle
        '''

        return function


    @legacy_function
    def set_tidal_model():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'tidal_model',
            dtype='int32',
            direction=function.IN,
            description=(
                '0=none, 1=conservative, 2=linear, '
                '3=creep direct, 4=creep tidymess (default)'
            )
        )
        function.result_type = 'int32'
        function.result_doc = ''''''
        return function


    @legacy_function
    def get_tidal_model():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'tidal_model',
            dtype='int32',
            direction=function.OUT,
            description=(
                '0=none, 1=conservative, 2=linear, '
                '3=creep direct, 4=creep tidymess (default)'
            )
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_pn_order():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'pn_order',
            dtype='int32',
            direction=function.IN,
            description='Post-Newtonian order: 0=none, 1=1pn, 2=1+2pn, 25=1+2+2.5pn'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_pn_order():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'pn_order',
            dtype='int32',
            direction=function.OUT,
            description='Post-Newtonian order: 0=none, 1=1pn, 2=1+2pn, 25=1+2+2.5pn'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_magnetic_braking():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'magnetic_braking',
            dtype='int32',
            direction=function.IN,
            description='Magnetic braking. 0=off, 1=on'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_magnetic_braking():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'magnetic_braking',
            dtype='int32',
            direction=function.OUT,
            description='Magnetic braking. 0=off, 1=on'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_speed_of_light():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'speed_of_light',
            dtype='float64',
            direction=function.IN,
            description='')
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_speed_of_light():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'speed_of_light',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_dt_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_mode',
            dtype='int32',
            direction=function.IN,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_dt_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_mode',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_dt_const():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_const',
            dtype='float64',
            direction=function.IN,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_dt_const():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_const',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_time_step():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'time_step',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_eta():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'eta',
            dtype='float64',
            direction=function.IN,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_eta():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'eta',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_n_iter():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'n_iter',
            dtype='int32',
            direction=function.IN,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_n_iter():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'n_iter',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_collision_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'collision_mode',
            dtype='int32',
            direction=function.IN,
            description='0=off, 1=flag, 2=exception, 3=replace'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_collision_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'collision_mode',
            dtype='int32',
            direction=function.OUT,
            description='0=off, 1=flag, 2=exception, 3=replace')
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_roche_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'roche_mode',
            dtype='int32',
            direction=function.IN,
            description='0=off, 1=flag, 2=exception'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_roche_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'roche_mode',
            dtype='int32',
            direction=function.OUT,
            description='0=off, 1=flag, 2=exception'
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def set_breakup_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'breakup_mode',
            dtype='int32',
            direction=function.IN,
            description=(
                'Centrifugal breakup speed detection. '
                '0=off, 1=flag, 2=exception'
            )
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_breakup_mode():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'breakup_mode',
            dtype='int32',
            direction=function.OUT,
            description=(
                'Centrifugal breakup speed detection. '
                '0=off, 1=flag, 2=exception'
            )
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def get_num_integration_step():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'num_integration_step',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def detect_collision():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'collision_flag',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.addParameter(
            'n_collisions',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.addParameter(
            'index1',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.addParameter(
            'index2',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        #function.addParameter(
        #    'indices_of_colliding_particles', dtype='int32', direction=function.OUT,
        #    description="")
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def convert_spin_vectors_to_inertial():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'lod',
            dtype='float64',
            direction=function.IN,
            description=''
        )
        function.addParameter(
            'obl',
            dtype='float64',
            direction=function.IN,
            description=''
        )
        function.addParameter(
            'psi',
            dtype='float64',
            direction=function.IN,
            description=''
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


    @legacy_function
    def merge_collided_particles():
        '''
        '''
        function = LegacyFunctionSpecification()
        function.addParameter(
            'number_of_particles',
            dtype='int32',
            direction=function.OUT,
            description=(
                'should be equivalent to collision '
                'handling when collision_mode==3'
            )
        )
        function.result_type = 'int32'
        function.result_doc = ''''''

        return function


class Tidymess(GravitationalDynamics, GravityFieldCode):

    def __init__(self, convert_nbody=None, **options):

        legacy_interface = TidyMessInterface(**options)

        GravitationalDynamics.__init__(
            self,
            legacy_interface,
            convert_nbody,
            **options
        )

        # should this be here or before?
        self.stopping_conditions = StoppingConditions(self)


    def define_state(self, handler):
        GravitationalDynamics.define_state(self, handler)
        handler.add_method('RUN', 'get_spin')
        handler.add_transition('RUN', 'UPDATE', 'set_spin', False)
        handler.add_method('UPDATE', 'set_spin')

        self.stopping_conditions.define_state(handler)


    def define_methods(self, handler):

        GravitationalDynamics.define_methods(self, handler)

        # Turn interface functions into methods.
        handler.add_method(
            'new_particle',
            (
                nbody_system.mass,
                nbody_system.length,
                nbody_system.length,
                nbody_system.length,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.length, # radius

                handler.NO_UNIT,     # xi, moment of inertia factor
                handler.NO_UNIT,     # kf, fluid Love number for potential
                nbody_system.time,   # tau, fluid relaxation time
                1/nbody_system.time, # wx
                1/nbody_system.time, # wy
                1/nbody_system.time, # wz

                handler.NO_UNIT,   # a_mb, magnetic braking coefficient
            ),
            (
                handler.INDEX,
                handler.ERROR_CODE
            )
        )
        handler.add_method(
            'get_num_integration_step',
            (),
            (
                handler.INDEX,
                handler.ERROR_CODE
            )
        )
        handler.add_method(
            'detect_collision',
            (),
            (
                handler.INDEX,
                handler.INDEX,
                handler.INDEX,
                handler.INDEX,
                handler.ERROR_CODE
            )
        )
        handler.add_method(
            'get_dt_const',
            (),
            (
                nbody_system.time,
                handler.ERROR_CODE
            )
        )

        handler.add_method(
            'convert_spin_vectors_to_inertial',
            (
                nbody_system.time,
                handler.NO_UNIT,
                handler.NO_UNIT,
            ),
            (
                1/nbody_system.time, # wx
                1/nbody_system.time, # wy
                1/nbody_system.time, # wz
                handler.ERROR_CODE
            )
        )

        handler.add_method(
            'set_spin',
            (
                handler.NO_UNIT,
                1/nbody_system.time,
                1/nbody_system.time,
                1/nbody_system.time,
            ),
            (
                handler.ERROR_CODE
            )
        )
        handler.add_method(
            'get_spin',
            (
                handler.NO_UNIT,
            ),
            (
                1/nbody_system.time,
                1/nbody_system.time,
                1/nbody_system.time,
                handler.ERROR_CODE
            )
        )

        self.stopping_conditions.define_methods(handler)


    def define_parameters(self, handler):
        # Set/get parameters specific to the module, not part of the
        # standard interface.  Accessors used here must be defined
        # above and reflected in interface.cc.  Python access is
        # (e.g.)
        #
        #        TidyMess.parameters.timestep_parameter = xxx
        #
        handler.add_method_parameter(
            'get_tidal_model',
            'set_tidal_model',
            'tidal_model',
            '0=none, 1=conservative, 2=linear, 3=creep direct, 4=creep tidymess (default)',
            default_value=4,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_pn_order',
            'set_pn_order',
            'pn_order',
            'Post-Newtonian order: 0=none (default), 1=1pn, 2=1+2pn, 25=1+2+2.5pn',
            default_value=0,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_magnetic_braking',
            'set_magnetic_braking',
            'magnetic_braking',
            'Magnetic braking. 0=off (default), 1=on',
            default_value=0,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_speed_of_light',
            'set_speed_of_light',
            'speed_of_light',
            '',
            default_value=1e100,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_dt_mode',
            'set_dt_mode',
            'dt_mode',
            '0=constant dt, 1=adaptive dt, 2=adaptive, weighted dt',
            default_value=1, # of 2?
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_eta',
            'set_eta',
            'eta',
            'accuracy parameter; timestep multiplication factor, default=0.0625 (only used if dt_mode>0)',
            default_value=0.0625,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_n_iter',
            'set_n_iter',
            'n_iter',
            'Number of iterations to improve reversibility (default=1)',
            default_value=1,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_collision_mode',
            'set_collision_mode',
            'collision_mode',
            '0=off (default), 1=flag, 2=exception, 3=replace',
            default_value=0,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_roche_mode',
            'set_roche_mode',
            'roche_mode',
            '0=off, 1=flag, 2=exception',
            default_value=0,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_breakup_mode',
            'set_breakup_mode',
            'breakup_mode',
            'Centrifugal breakup speed detection. 0=off, 1=flag, 2=exception',
            default_value=0,
            is_vector=False,
            must_set_before_get=False,
        )

        self.stopping_conditions.define_parameters(handler)


    def define_particle_sets(self, handler):
        handler.define_set('particles', 'index_of_the_particle')
        handler.set_new('particles', 'new_particle')
        handler.set_delete('particles', 'delete_particle')
        handler.add_setter('particles', 'set_state')
        handler.add_getter('particles', 'get_state')
        handler.add_setter('particles', 'set_mass')
        handler.add_getter('particles', 'get_mass', names=('mass',))
        handler.add_setter('particles', 'set_position')
        handler.add_getter('particles', 'get_position')
        handler.add_setter('particles', 'set_velocity')
        handler.add_getter('particles', 'get_velocity')
        handler.add_setter('particles', 'set_spin')
        handler.add_getter('particles', 'get_spin')
        handler.add_setter('particles', 'set_radius')
        handler.add_getter('particles', 'get_radius')
        handler.add_query(
            'particles', 'get_indices_of_colliding_particles',
            public_name='select_colliding_particles'
        )
