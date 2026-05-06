"""
AMUSE interface for UCLCHEM, a gas-grain chemical code that
propagates the abundances of chemical species through a network
of user-defined reactions according to the physical conditions of the gas.

Date Created:  April 01, 2026
Date Modified: May 06, 2026
"""

from typing import Literal
from amuse.community.interface.common import CommonCode, CommonCodeInterface
from amuse.community import (
    LiteratureReferencesMixIn,
    legacy_function,
    LegacyFunctionSpecification,
)
from amuse.datamodel import Particle, Particles
from amuse.rfi.core import PythonCodeInterface
from amuse.support.interface import InCodeComponentImplementation
from amuse.units import units as u
import uclchem
from uclchem.model import get_species_names


habing = u.named('habing', 'hab', 1.6e-3 * u.erg * u.cm**-2 * u.s**-1)

class UclchemImplementation(object):

    def __init__(self):
        self.current_time: float = 0
        self.chem_model: Literal['cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'] = 'cloud'
        self.collapse: Literal['BE1.1', 'BE4', 'filament', 'ambipolar'] = 'BE1.1'
        self.MODEL_MAP: dict = {
            'cloud': uclchem.model.Cloud,
            'collapse': uclchem.model.Collapse,
            'cshock': uclchem.model.CShock,
            'prestellarcore': uclchem.model.PrestellarCore,
            'jshock': uclchem.model.JShock,
        }
        self.param_dict: dict = {}
        self.particles = Particles()
        self.output_models: list = []

    def initialize_code(self) -> int:
        # self.parameters = uclchem.advanced.GeneralSettings()
        return 0

    def cleanup_code(self) -> int:
        self.particles.remove_particles(self.particles)
        return 0

    def commit_parameters(self) -> int:
        return 0

    def commit_particles(self) -> int:
        self.particles.add_vector_attribute('abundance', ('H', 'H2'))
        return 0

    def recommit_parameters(self) -> int:
        return 0

    def recommit_particles(self) -> int:
        return 0

    # def synchronize_model(self):
    #     return 0

    def evolve_model(self, time) -> int:
        model = self.MODEL_MAP.get(self.chem_model, None)
        if model is None:
            raise ValueError(
                'chem_model must be one of the following options: '
                "'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'"
            )

        dt = float(time - self.current_time)

        for i, particle in enumerate(self.particles):
            params = self._particle_to_dict(particle)
            params['finalTime'] = dt

            if i < len(self.output_models):
                prev_model = self.output_models[i]
            else:
                prev_model = None

            new_model = model(param_dict=params, previous_model=prev_model)

            if i < len(self.output_models):
                self.output_models[i] = new_model
            else:
                self.output_models.append(new_model)

            print('\n')
            print(self.output_models[i].get_dataframes())

        self.current_time = float(time)
        return 0

    def new_particle(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ) -> int:
        """
        Add a new particle to Uclchem.

        Parameters
        ----------
        index_of_the_particle : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the index of the new particle.
        number_density : float
            Number density of the particle in units of cm**-3.
        temperature : float
            Temperature of the particle in units of K.
        ionrate : float
            Ionization rate of the particle in units of s**-1.
        radfield : float
            Radiation field of the particle in units of habing.

        Returns
        -------
        int :
            0 on success
        """
        p = Particle()
        p.number_density = number_density
        p.temperature = temperature
        p.ionrate = ionrate
        p.radfield = radfield
        index_of_the_particle.value = len(self.particles)
        self.particles.add_particle(p)
        return 0

    def delete_particle(self, index_of_the_particle) -> int:
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        print('delete_particle', self.particles)
        self.particles.remove_particles(self.particles[i].as_set())
        print('now', self.particles)

        return 0

    def get_state(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ) -> int:
        """
        Retrieve the state of a particle by index.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        number_density : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the number density
            of the particle in units of cm**-3.
        temperature : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the temperature
            of the particle in units of K.
        ionrate : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the ionization
            rate of the particle in units of s**-1.
        radfield : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the radiation
            field of the particle in units of habing.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        number_density.value = p.number_density
        temperature.value = p.temperature
        ionrate.value = p.ionrate
        radfield.value = p.radfield
        return 0

    def set_state(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ) -> int:
        """
        Set the state of a particle by index.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        number_density : float
            Number density of the particle in units of cm**-3.
        temperature : float
            Temperature of the particle in units of K.
        ionrate : float
            Ionization rate of the particle in units of s**-1.
        radfield : float
            Radiation field of the particle in units of habing.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        p.number_density = number_density
        p.temperature = temperature
        p.ionrate = ionrate
        p.radfield = radfield
        return 0

    def get_number_density(self, index_of_the_particle, number_density) -> int:
        """
        Retrieve the number density of a particle by index.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        number_density : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the number density
            of the particle in units of cm**-3.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        number_density.value = p.number_density
        return 0

    def set_number_density(self, index_of_the_particle, number_density) -> int:
        """
        Set the number density of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        number_density: float
            Number density of the particle in units of cm**-3.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        p.number_density = number_density
        return 0

    def get_temperature(self, index_of_the_particle, temperature) -> int:
        """
        Retrieve the temperature of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        temperature : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the temperature
            of the particle in units of K.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        temperature.value = p.temperature
        return 0

    def set_temperature(self, index_of_the_particle, temperature) -> int:
        """
        Set the temperature of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        temperature : float
            Temperature of the particle in units of K.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        p.temperature = temperature
        return 0

    def get_ionrate(self, index_of_the_particle, ionrate) -> int:
        """
        Retrieve the ionization rate of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        ionrate : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the ionization
            rate of the particle in units of s**-1.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        ionrate.value = p.ionrate
        return 0

    def set_ionrate(self, index_of_the_particle, ionrate) -> int:
        """
        Retrieve the ionization rate of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        ionrate : float
            Ionization rate of the particle in units of s**-1.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        p.ionrate = ionrate
        return 0

    def get_radfield(self, index_of_the_particle, radfield) -> int:
        """
        Retrieve the radiation field of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        ionrate : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the radiation
            field of the particle in units of habing.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        radfield.value = p.radfield
        return 0

    def set_radfield(self, index_of_the_particle, radfield) -> int:
        """
        Set the radiation field of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        ionrate : float
            Radiation field of the particle in units of habing.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles[i]
        p.radfield = radfield
        return 0

    def get_abundance(self, index_of_the_particle, abundance_index, abundance) -> int:
        i = index_of_the_particle
        if not (0 <= i < len(self.output_models)):
            return -1

        abundances = self.output_models[i].chemical_abun_array
        abundance.value = abundances[-1, 0, abundance_index]
        return 0

    def get_chemical_model(self, chem_model) -> int:
        """
        Retrieve the chemical model type used by UCLCHEM.
        This is the physics model used internally by UCLCHEM
        to evolve the chemistry.

        Possible values are `'cloud'`, `'collapse'`, `'cshock'`,
        `'jshock'`, and `'prestellarcore'`.

        Parameters
        ----------
        chem_model : amuse.rfi.python_code.ValueHolder
            Mutable container used to return the current
            model type.

        Returns
        -------
        int :
            0 on success.
        """
        chem_model.value = self.chem_model
        return 0

    def set_chemical_model(self, chem_model) -> int:
        """
        Set the chemical model used by UCLCHEM. This is
        the physics model used internally by UCLCHEM to
        evolve the chemistry.

        Possible values are `'cloud'`, `'collapse'`, `'cshock'`,
        `'jshock'`, and `'prestellarcore'`.

        Parameters
        ----------
        chem_model : {'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'}
            Chemical model specifying the chemistry physics when evolving the particles.

        Returns
        -------
        int :
            0 on success.

        Raises
        ------
        ValueError :
            If `chem_model` is not one of the allowed models.
        """
        if chem_model not in {'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'}:
            raise ValueError(
                'chem_model must be one of the following options: '
                "'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'"
            )
        self.chem_model = chem_model
        return 0

    def get_species_name(self, i, name) -> int:
        species_names = get_species_names()
        if not 0 <= i < len(species_names):
            return -1

        name.value = species_names[i]
        return 0

    def get_species_index(self, name, i) -> int:
        species_names = get_species_names()

        try:
            idx = species_names.index(name)
        except ValueError:
            return -1

        i.value = idx
        return 0

    def get_time(self, time) -> int:
        time.value = self.current_time
        return 0

    def _is_valid_particle_index(self, i: int) -> bool:
        """
        Verify that the index of a particle is a valid reference
        to a particle stored in the UclchemImplementation class.

        Parameters
        ----------
        i : int
            Index of a particle as returned by `new_particle`.

        Returns
        -------
        bool :
            True if `i` is a valid index to a particle.
        """
        return 0 <= i < len(self.particles)

    def _particle_to_dict(self, particle: Particle) -> dict:
        """
        Format an AMUSE Particle into a parameter dictionary
        readable by UCLCHEM.

        Unlike AMUSE, UCLCHEM does not work with particles but
        rather a dictionary of parameters. This is a helper function
        to be called before evolving a particle with UCLCHEM.

        Parameters
        ----------
        particle : amuse.datamodel.Particle
            Particle to evolve by UCLCHEM.
        """
        param_dict = {
            'initialDens': float(particle.number_density),
            'initialTemp': float(particle.temperature),
        }
        return param_dict




class UclchemInterface(CommonCodeInterface, PythonCodeInterface, LiteratureReferencesMixIn):
    """
    UCLCHEM: A Gas-Grain Chemical Code for astrochemical modelling

    .. [#] ADS:2017AJ....154...38H (Holdship, J. ; Viti, S, ; Jiménez-Serra, I.; Makrymallis, A. ; Priestley, F. , 2017, AJ)
    """
    def __init__(self, **options):
        PythonCodeInterface.__init__(
            self,
            UclchemImplementation,
            'uclchem_worker',
            **options
        )
        LiteratureReferencesMixIn.__init__(self)

    @legacy_function
    def commit_parameters():
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function

    @legacy_function
    def commit_particles():
        function = LegacyFunctionSpecification()
        function.result_type = 'int32'
        return function

    @legacy_function
    def recommit_particles():
        function = LegacyFunctionSpecification()
        function.result_type = "i"
        return function

    @legacy_function
    def evolve_model():
        function = LegacyFunctionSpecification()
        function.addParameter('time', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def new_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.OUT)
        for x in ['number_density', 'temperature', 'ionrate', 'radfield']:
            function.addParameter(x, dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def delete_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_state():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        for x in ['number_density', 'temperature', 'ionrate', 'radfield']:
            function.addParameter(x, dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_state():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        for x in ['number_density', 'temperature', 'ionrate', 'radfield']:
            function.addParameter(x, dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_number_density():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('number_density', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_number_density():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('number_density', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_temperature():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('temperature', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_temperature():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('temperature', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_ionrate():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('ionrate', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_ionrate():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('ionrate', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_radfield():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('radfield', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_radfield():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('radfield', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_chemical_model():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('chem_model', dtype='string', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_chemical_model():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('chem_model', dtype='string', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_abundance():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('abundance_index', dtype='int32', direction=function.IN)
        function.addParameter('abundance', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_abundance():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('abundance_index', dtype='int32', direction=function.IN)
        function.addParameter('abundance', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_species_name():
        function = LegacyFunctionSpecification()
        function.addParameter('i', dtype='int32', direction=function.IN)
        function.addParameter('name', dtype='string', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_species_index():
        function = LegacyFunctionSpecification()
        function.addParameter('name', dtype='string', direction=function.IN)
        function.addParameter('i', dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_time():
        """
        Retrieve the model time. This time should be close to the end time
        specified in the evolve code. Or, when a collision was detected, it
        will be the model time of the collision.
        """
        function = LegacyFunctionSpecification()
        function.addParameter('time', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        function.result_doc = """
        0 - OK
            Current value of the time was retrieved
        """
        return function


class Uclchem(CommonCode):
    def __init__(self, unit_converter=None, **options):

        if unit_converter is not None:
            raise ValueError('Uclchem uses predefined units')

        chem_interface = UclchemInterface(**options)

        InCodeComponentImplementation.__init__(
            self,
            chem_interface
        )

    def define_methods(self, handler):
        CommonCode.define_methods(self, handler)
        handler.add_method(
            'evolve_model',
            (u.yr,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'new_particle',
            (u.cm**-3, u.K, u.s**-1, habing),
            (
                handler.INDEX,
                handler.ERROR_CODE,
            ),
        )

        handler.add_method(
            'delete_particle',
            (handler.INDEX,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_state',
            (handler.INDEX,),
            (
                u.cm**-3,
                u.K,
                u.s**-1,
                habing,
                handler.ERROR_CODE,
            ),
        )

        handler.add_method(
            'set_state',
            (
                handler.INDEX,
                u.cm**-3,
                u.K,
                u.s**-1,
                habing,
            ),
            (handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_number_density',
            (handler.INDEX,),
            (u.cm**-3, handler.ERROR_CODE,),
        )

        handler.add_method(
            'set_number_density',
            (handler.INDEX, u.cm**-3,),
            (handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_temperature',
            (handler.INDEX,),
            (u.K, handler.ERROR_CODE,),
        )

        handler.add_method(
            'set_temperature',
            (handler.INDEX, u.K,),
            (handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_ionrate',
            (handler.INDEX,),
            (u.s**-1, handler.ERROR_CODE,),
        )

        handler.add_method(
            'set_ionrate',
            (handler.INDEX, u.s**-1,),
            (handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_radfield',
            (handler.INDEX,),
            (habing, handler.ERROR_CODE,),
        )

        handler.add_method(
            'set_radfield',
            (handler.INDEX, habing,),
            (handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_abundance',
            (handler.INDEX, handler.INDEX,),
            (handler.NO_UNIT, handler.ERROR_CODE,),
        )

        handler.add_method(
            'set_abundance',
            (
                handler.INDEX,
                handler.INDEX,
                handler.NO_UNIT,
            ),
            (handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_species_name',
            (handler.INDEX,),
            (handler.NO_UNIT, handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_species_index',
            (handler.NO_UNIT,),
            (handler.INDEX, handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_time',
            (),
            (u.yr, handler.ERROR_CODE,)
        )


    def define_parameters(self, handler):
        handler.add_method_parameter(
            'get_chemical_model',
            'set_chemical_model',
            'chem_model',
            "'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'",
            default_value='cloud'
        )
        handler.add_interface_parameter(
            'out_species', 'Array of molecules to use', default_value=['H', 'H2']
        )

    def define_properties(self, handler):
        handler.add_property('get_time', public_name='model_time')

    def define_particle_sets(self, handler):
        handler.define_set('particles', 'index_of_the_particle')
        handler.set_new('particles', 'new_particle')
        handler.set_delete('particles', 'delete_particle')
        handler.add_setter('particles', 'set_state')
        handler.add_getter('particles', 'get_state')
        # handler.add_gridded_getter(
        #     "particles",
        #     "get_abundance",
        #     "get_firstlast_abundance",
        #     names=("abundances",),
        # )
        # handler.add_gridded_setter(
        #     "particles",
        #     "set_abundance",
        #     "get_firstlast_abundance",
        #     names=("abundances",),
        # )

    def define_state(self, handler):
        CommonCode.define_state(self, handler)
        handler.add_transition("INITIALIZED", "EDIT", "commit_parameters")
        handler.add_transition("RUN", "PARAMETER_CHANGE_A", "invoke_state_change2")
        handler.add_transition("EDIT", "PARAMETER_CHANGE_B", "invoke_state_change2")
        handler.add_transition("PARAMETER_CHANGE_A", "RUN", "recommit_parameters")
        handler.add_transition("PARAMETER_CHANGE_B", "EDIT", "recommit_parameters")
        handler.add_method("EDIT", "new_particle")
        handler.add_method('EDIT', 'delete_particle')
        handler.add_transition("EDIT", "RUN", "commit_particles")
        handler.add_transition("RUN", "UPDATE", "new_particle", False)
        handler.add_transition("RUN", "UPDATE", "delete_particle", False)
        handler.add_transition("UPDATE", "RUN", "recommit_particles")
        handler.add_method("RUN", "evolve_model")
        handler.add_method("RUN", "get_state")
        handler.add_method("RUN", "get_abundance")
