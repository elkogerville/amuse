from amuse.community.interface.gd import GravitationalDynamics
from amuse.community.interface.gd import GravitationalDynamicsInterface
from amuse.community.interface.gd import GravityFieldInterface
from amuse.community.interface.gd import GravityFieldCode
from amuse.community.interface.stopping_conditions import StoppingConditions, StoppingConditionInterface
from amuse.rfi.core import CodeInterface, legacy_function, LegacyFunctionSpecification
from amuse.support.interface import MethodWithUnitsDefinition
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.units import units as u, nbody_system


class TidymessInterface(
    CodeInterface,
    LiteratureReferencesMixIn,
    GravitationalDynamicsInterface,
    GravityFieldInterface,
    StoppingConditionInterface,
):
    """
    Tidymess is a N-Body code with tides

    .. [#] Boekholt & Correia (MNRAS 2023, vol. 522, pp. 2885–2900)
    """

    include_headers = ['tidymess_worker.h', 'stopcond.h']

    def __init__(self, **kwargs):
        CodeInterface.__init__(
            self, name_of_the_worker='tidymess_worker', **kwargs
        )
        LiteratureReferencesMixIn.__init__(self)


    @legacy_function
    def new_particle():
        """
        Define a new particle in the stellar dynamics code. The particle is
        initialized with the provided mass, radius, position, velocity, moment
        of inertia factor, fluid love number, fluid relaxation time, spin, and
        magnetic breaking coefficient. This function returns an index that can
        be used to refer to this particle.
        """
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
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            particle was created and added to the model
        -1 - ERROR
            particle could not be created
        """
        return function

    @legacy_function
    def get_state():
        """
        Retrieve the current state of a particle.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle',
            dtype='int32',
            direction=function.IN,
            description=(
                "Index of the particle to get the state from. This index must "
                "have been returned by an earlier call to :meth:`new_particle`"
            ),
        )
        function.addParameter(
            'mass',
            dtype='float64',
            direction=function.OUT,
            description='The current mass of the particle',
        )
        function.addParameter(
            'x',
            dtype='float64',
            direction=function.OUT,
            description='The current position vector of the particle',
        )
        function.addParameter(
            'y',
            dtype='float64',
            direction=function.OUT,
            description='The current position vector of the particle',
        )
        function.addParameter(
            'z',
            dtype='float64',
            direction=function.OUT,
            description='The current position vector of the particle',
        )
        function.addParameter(
            'vx',
            dtype='float64',
            direction=function.OUT,
            description='The current velocity vector of the particle',
        )
        function.addParameter(
            'vy',
            dtype='float64',
            direction=function.OUT,
            description='The current velocity vector of the particle',
        )
        function.addParameter(
            'vz',
            dtype='float64',
            direction=function.OUT,
            description='The current velocity vector of the particle',
        )
        function.addParameter(
            'radius',
            dtype='float64',
            direction=function.OUT,
            description='The current radius of the particle',
        )
        function.addParameter(
            'xi',
            dtype='float64',
            direction=function.OUT,
            description='Moment of inertia factor',
        )
        function.addParameter(
            'kf',
            dtype='float64',
            direction=function.OUT,
            description='Fluid Love number from potential',
        )
        function.addParameter(
            'tau',
            dtype='float64',
            direction=function.OUT,
            description='Fluid relaxation time',
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.OUT,
            description='Spin',
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.OUT,
            description='Spin',
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.OUT,
            description='Spin',
        )
        function.addParameter(
            'a_mb',
            dtype='float64',
            direction=function.OUT,
            description='Magnetic braking coefficient',
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            state was retrieved from particle
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def set_state():
        """
        Update the current state of a particle.
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
            'xi',
            dtype='float64',
            direction=function.IN,
            description='Moment of inertia factor',
        )
        function.addParameter(
            'kf',
            dtype='float64',
            direction=function.IN,
            description='Fluid Love number from potential',
        )
        function.addParameter(
            'tau',
            dtype='float64',
            direction=function.IN,
            description='Fluid relaxation time',
        )
        function.addParameter(
            'wx',
            dtype='float64',
            direction=function.IN,
            description='Spin',
        )
        function.addParameter(
            'wy',
            dtype='float64',
            direction=function.IN,
            description='Spin',
        )
        function.addParameter(
            'wz',
            dtype='float64',
            direction=function.IN,
            description='Spin',
        )
        function.addParameter(
            'a_mb',
            dtype='float64',
            direction=function.IN,
            description='Magnetic braking coefficient',
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the information was set
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def get_xi():
        """
        Retrieve the moment of inertia of a particle.
        """
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
            'xi',
            dtype='float64',
            direction=function.OUT,
            description='The moment of inertia of a particle.'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the moment of inertia was retrieved
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def set_xi():
        """
        Update the current moment of inertia of a particle.
        """
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
            'xi',
            dtype='float64',
            direction=function.IN,
            description='The moment of inertia of a particle.'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the moment of inertia was set
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def get_kf():
        """
        Retrieve the fluid love number of a particle.
        """
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
            'kf',
            dtype='float64',
            direction=function.OUT,
            description='The fluid love number of a particle.'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the fluid love number was retrieved
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def set_kf():
        """
        Update the current fluid love number of a particle.
        """
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
            'kf',
            dtype='float64',
            direction=function.IN,
            description='The fluid love number of a particle.'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the fluid love number was set
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def get_tau():
        """
        Retrieve the fluid relaxation time of a particle.
        """
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
            'tau',
            dtype='float64',
            direction=function.OUT,
            description='The fluid relaxation time of a particle.'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the fluid
            relaxation time was retrieved
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def set_tau():
        """
        Update the current fluid relaxation time of a particle.
        """
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
            'tau',
            dtype='float64',
            direction=function.IN,
            description='The fluid relaxation time of a particle.'
        )
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            particle was found in the model and the fluid
            relaxation time was set
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def get_spin():
        """
        Retrieve the spin vector of a particle.
        """
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
        function.result_doc = """\
            0 - OK
                particle was found in the model and the spin was retrieved
            -1 - ERROR
                particle could not be found
        """
        return function

    @legacy_function
    def set_spin():
        """
        Update the current spin of a particle.
        """
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
        function.result_doc = """\
        0 - OK
            particle was found in the model and the spin was set
        -1 - ERROR
            particle could not be found
        """
        return function

    @legacy_function
    def get_tidal_model():
        """
        Get Tidymess tidal model.
        """
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
        function.result_doc = """\
        0 - OK
            tidal model was retrieved
        -1 - ERROR
            tidal model could not be found
        """
        return function

    @legacy_function
    def set_tidal_model():
        """
        Set Tidymess tidal model.
        """
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
        function.result_doc = """\
        0 - OK
            tidal model was set
        -1 - ERROR
            tidal model could not be set
        """
        return function

    @legacy_function
    def get_pn_order():
        """
        Get Tidymess pn order parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'pn_order',
            dtype='int32',
            direction=function.OUT,
            description='Post-Newtonian order: 0=none, 1=1pn, 2=1+2pn, 25=1+2+2.5pn'
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            pn order was retrieved
        -1 - ERROR
            pn order could not be found
        """

        return function

    @legacy_function
    def set_pn_order():
        """
        Set Tidymess pn order parameter
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'pn_order',
            dtype='int32',
            direction=function.IN,
            description='Post-Newtonian order: 0=none, 1=1pn, 2=1+2pn, 25=1+2+2.5pn'
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            pn order was set
        -1 - ERROR
            pn order could not be set
        """
        return function

    @legacy_function
    def get_magnetic_braking():
        """
        Get magnetic braking parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'magnetic_braking',
            dtype='int32',
            direction=function.OUT,
            description='Magnetic braking. 0=off, 1=on'
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            magnetic braking was retrieved
        -1 - ERROR
            magnetic braking could not be found
        """
        return function

    @legacy_function
    def set_magnetic_braking():
        """
        Set the magnetic braking parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'magnetic_braking',
            dtype='int32',
            direction=function.IN,
            description='Magnetic braking. 0=off, 1=on'
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            magnetic braking coefficient was set
        -1 - ERROR
            Could not set magnetic braking coefficient
        """
        return function

    @legacy_function
    def get_speed_of_light():
        """
        Retrieve Tidymess speed of light parameter.
        Only used in conjunction with N-body units
        and pn_order>0, otherwise equal to c.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'speed_of_light',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            speed of light was retrieved
        -1 - ERROR
            Could not find speed of light
        """
        return function

    @legacy_function
    def set_speed_of_light():
        """
        Set Tidymess speed of light. Only used in
        conjunction with N-body units and pn_order>0,
        otherwise equal to c.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'speed_of_light',
            dtype='float64',
            direction=function.IN,
            description='')
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            speed of light was set
        -1 - ERROR
            Could not set speed of light
        """
        return function

    @legacy_function
    def get_dt_mode():
        """
        Retrieve Tidymess dt mode parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_mode',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            dt mode was retrieved
        -1 - ERROR
            Could not find dt mode
        """
        return function

    @legacy_function
    def set_dt_mode():
        """
        Set Tidymess dt mode parameter. Controls
        which dt scheme is used in Tidymess.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_mode',
            dtype='int32',
            direction=function.IN,
            description='0=constant dt, 1=adaptive dt, 2=adaptive, weighted dt'
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            dt mode was set
        -1 - ERROR
            Could not set dt mode
        """
        return function

    @legacy_function
    def get_dt_const():
        """
        Retrieve Tidymess constant dt parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_const',
            dtype='float64',
            direction=function.OUT,
            description='',
            unit=nbody_system.time
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            constant dt was retrieved
        -1 - ERROR
            Could not find constant dt
        """
        return function

    @legacy_function
    def set_dt_const():
        """
        Set Tidymess constant dt parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'dt_const',
            dtype='float64',
            direction=function.IN,
            description='',
            unit=nbody_system.time
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            constant dt was set
        -1 - ERROR
            Could not set constant dt
        """
        return function

    @legacy_function
    def get_eta():
        """
        Retrieve Tidymess eta (accuracy) parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'eta',
            dtype='float64',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            eta was retrieved
        -1 - ERROR
            Could not find eta
        """
        return function

    @legacy_function
    def set_eta():
        """
        Set Tidymess eta (accuracy) parameter.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'eta',
            dtype='float64',
            direction=function.IN,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            eta was set
        -1 - ERROR
            Could not set eta
        """
        return function

    @legacy_function
    def get_n_iter():
        """
        Retrieve Tidymess n iter parameter. This is the
        number of iterations to improve reversibility.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'n_iter',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            n_iter was retrieved
        -1 - ERROR
            Could not find n_iter
        """
        return function

    @legacy_function
    def set_n_iter():
        """
        Set Tidymess n iter parameter. This is the
        number of iterations to improve reversibility.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'n_iter',
            dtype='int32',
            direction=function.IN,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """\
        0 - OK
            n_iter was set
        -1 - ERROR
            Could not set n_iter
        """
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
        """
        """
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
        """
        """
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
        """
        """
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
        function.result_doc = """"""

        return function

    @legacy_function
    def set_initial_shape():
        """
        Set Tidymess initial shape.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'initial_shape',
            dtype='int32',
            direction=function.IN,
            description='0=default'
        )
        function.result_type = 'int32'
        function.result_doc = """"""

        return function

    @legacy_function
    def get_initial_shape():
        """
        Get Tidymess initial shape value.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'initial_shape',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """"""

        return function

    @legacy_function
    def get_num_integration_step():
        """
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'num_integration_step',
            dtype='int32',
            direction=function.OUT,
            description=''
        )
        function.result_type = 'int32'
        function.result_doc = """"""

        return function

    @legacy_function
    def get_total_energy():
        """Get total energy from system"""
        function = LegacyFunctionSpecification()
        function.addParameter(
            'total_energy',
            dtype='float64',
            direction=function.OUT,
            description='Total energy of the system'
        )
        function.result_type = 'int32'
        function.result_doc = """"""

        return function

    # @legacy_function
    # def detect_collision():
    #     '''
    #     '''
    #     function = LegacyFunctionSpecification()
    #     function.addParameter(
    #         'collision_flag',
    #         dtype='int32',
    #         direction=function.OUT,
    #         description=''
    #     )
    #     function.addParameter(
    #         'n_collisions',
    #         dtype='int32',
    #         direction=function.OUT,
    #         description=''
    #     )
    #     function.addParameter(
    #         'index1',
    #         dtype='int32',
    #         direction=function.OUT,
    #         description=''
    #     )
    #     function.addParameter(
    #         'index2',
    #         dtype='int32',
    #         direction=function.OUT,
    #         description=''
    #     )
    #     #function.addParameter(
    #     #    'indices_of_colliding_particles', dtype='int32', direction=function.OUT,
    #     #    description="")
    #     function.result_type = 'int32'
    #     function.result_doc = ''''''

    #     return function


    @legacy_function
    def convert_spin_vectors_to_inertial():
        """
        Convert spin vector {length of day, obliquity, spin precession angle}
        to spin vector {wx, wy, wz}
        """
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
        function.result_doc = """\
        0 - OK
            spin converted to inertial frame succesfully
        -1 - ERROR
            Could not convert to inertial frame
        -2 - ERROR
            Negative length of day detected
        """

        return function


class Tidymess(GravitationalDynamics, GravityFieldCode):

    def __init__(self, convert_nbody=None, **options):

        legacy_interface = TidymessInterface(**options)
        self.stopping_conditions = StoppingConditions(self)

        GravitationalDynamics.__init__(
            self,
            legacy_interface,
            convert_nbody,
            **options
        )

    def define_state(self, handler):
        GravitationalDynamics.define_state(self, handler)
        GravityFieldCode.define_state(self, handler)

        handler.add_method('RUN', 'get_spin')
        handler.add_transition('RUN', 'UPDATE', 'set_spin', False)
        handler.add_method('UPDATE', 'set_spin')

        self.stopping_conditions.define_state(handler)

    def define_methods(self, handler):
        """
        Map legacy functions in TidymessInterface into
        Tidymess user methods.
        """

        GravitationalDynamics.define_methods(self, handler)

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
                nbody_system.length,   # radius
                handler.NO_UNIT,              # xi, moment of inertia factor
                handler.NO_UNIT,              # kf, fluid Love number for potential
                nbody_system.time,     # tau, fluid relaxation time
                1 / nbody_system.time, # wx
                1 / nbody_system.time, # wy
                1 / nbody_system.time, # wz
                handler.NO_UNIT,              # a_mb, magnetic braking coefficient
            ),
            (handler.INDEX, handler.ERROR_CODE)
        )

        handler.add_method(
            'get_state',
            (handler.INDEX),
            (
                nbody_system.mass,
                nbody_system.length,
                nbody_system.length,
                nbody_system.length,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.length,
                handler.NO_UNIT,
                handler.NO_UNIT,
                nbody_system.time,
                1 / nbody_system.time,
                1 / nbody_system.time,
                1 / nbody_system.time,
                handler.NO_UNIT,
                handler.ERROR_CODE,
            )
        )

        handler.add_method(
            'set_state',
            (
                handler.INDEX,
                nbody_system.mass,
                nbody_system.length,
                nbody_system.length,
                nbody_system.length,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.speed,
                nbody_system.length,
                handler.NO_UNIT,
                handler.NO_UNIT,
                nbody_system.time,
                1 / nbody_system.time,
                1 / nbody_system.time,
                1 / nbody_system.time,
                handler.NO_UNIT,
            ),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_xi',
            (handler.INDEX,),
            (handler.NO_UNIT, handler.ERROR_CODE,)
        )

        handler.add_method(
            'set_xi',
            (handler.INDEX, handler.NO_UNIT),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_kf',
            (handler.INDEX,),
            (handler.NO_UNIT, handler.ERROR_CODE,)
        )

        handler.add_method(
            'set_kf',
            (handler.INDEX, handler.NO_UNIT),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_tau',
            (handler.INDEX,),
            (nbody_system.time, handler.ERROR_CODE,)
        )

        handler.add_method(
            'set_tau',
            (handler.INDEX, nbody_system.time),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_spin',
            (handler.INDEX,),
            (
                1/nbody_system.time,
                1/nbody_system.time,
                1/nbody_system.time,
                handler.ERROR_CODE
            )
        )

        handler.add_method(
            'set_spin',
            (
                handler.INDEX,
                1/nbody_system.time,
                1/nbody_system.time,
                1/nbody_system.time,
            ),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_num_integration_step',
            (),
            (handler.INDEX, handler.ERROR_CODE)
        )

        handler.add_method(
            'convert_spin_vectors_to_inertial',
            (
                nbody_system.time,
                u.rad,
                u.rad,
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
        """
        Define setters and getters as Tidymess.parameters.
        This is the standard API for users to access and modify
        Tidymess parameters. Users should use parameters rather
        than acessing the setters and getters defined in
        TidymessInterface directly. Accessors used here must be
        defined in TidymessInterface as a legacy_function, as
        well as the interface.cc.
        User access then follows the syntax:
            Tidymess.parameters.param_name = value
        Users should not use:
            Tidymess.set_param_name(value)
        """
        GravitationalDynamics.define_parameters(self, handler)
        handler.add_method_parameter(
            'get_tidal_model',
            'set_tidal_model',
            'tidal_model',
            '0=none (default), 1=conservative, 2=linear, 3=creep direct, 4=creep tidymess',
            default_value=0,
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
            'Speed of light. Should be set depending on unit system being used, or if using post newtonian.',
            default_value=1e100,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_dt_mode',
            'set_dt_mode',
            'dt_mode',
            '0=constant dt; 1=adaptive dt; 2=adaptive, weighted dt',
            default_value=2,
            is_vector=False,
            must_set_before_get=False,
        )

        handler.add_method_parameter(
            'get_dt_const',
            'set_dt_const',
            'dt_const',
            'constant time step',
            default_value=0.015625 | nbody_system.time,
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

        handler.add_method_parameter(
            'get_initial_shape',
            'set_initial_shape',
            'initial_shape',
            'Initial shape, 0=sphere (default), 1=equilibrium',
            default_value=0,
            is_vector=False,
            must_set_before_get=False,
        )

        self.stopping_conditions.define_parameters(handler)

    def define_properties(self, handler):
        """Define read only properties of Tidymess"""
        GravitationalDynamics.define_properties(self, handler)
        handler.add_property('get_total_energy', public_name='total_energy')

    def define_particle_sets(self, handler):
        GravitationalDynamics.define_particle_sets(self, handler)

        self.stopping_conditions.define_particle_set(handler)
