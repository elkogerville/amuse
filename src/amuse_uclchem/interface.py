"""
AMUSE interface for UCLCHEM, a gas-grain chemical code that
propagates the abundances of chemical species through a network
of user-defined reactions according to the physical conditions of the gas.

Date Created:  April 01, 2026
Date Modified: May 06, 2026
"""

from typing import Literal
import numpy as np
import uclchem
from uclchem.model import get_species_names, AbstractModel

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


habing = u.named('habing', 'hab', 1.6e-3 * u.erg * u.cm**-2 * u.s**-1)
# set run_type to 'external', model doesnt start immediately

class UclchemImplementation(object):

    def __init__(self):
        """
        Parameters
        ----------
        current_time : float
            Current simulation time.
        chem_model : {'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'}
            UCLCHEM model for the chemistry evolution.
        MODEL_MAP : dict[str, type[AbstractModel]]
            Dictionary to map `chem_model` to a UCLCHEM AbstractModel class.
            These are the actual models which compute the chemistry.
        model_class : type[AbstractModel]
            Current UCLCHEM AbstractModel class used when calling `evolve_model`.
        particles : amuse.datamodel.Particles
            Particles datamclass for storing UCLCHEM particles.
        """
        self.current_time = 0
        self.chem_model = 'cloud'
        self.MODEL_MAP = {
            'cloud': uclchem.model.Cloud,
            'collapse': uclchem.model.Collapse,
            'cshock': uclchem.model.CShock,
            'prestellarcore': uclchem.model.PrestellarCore,
            'jshock': uclchem.model.JShock,
        }
        self.model_class = self._validate_chemical_model(
            self.MODEL_MAP.get(self.chem_model, None)
        )
        self.collapse: Literal['BE1.1', 'BE4', 'filament', 'ambipolar'] = 'BE1.1'
        self.param_dict: dict = {}
        self.uclchem_particles = Particles()

    def initialize_code(self) -> int:
        # self.parameters = uclchem.advanced.GeneralSettings()
        return 0

    def cleanup_code(self) -> int:
        """Remove all the particles stored in UCLCHEM."""
        self.uclchem_particles.remove_particles(self.uclchem_particles)
        return 0

    def commit_parameters(self) -> int:
        """
        Convert the chemical model name to its corresponding AbstractModel class.

        Validates that the chemical model specified by the user maps to a valid
        UCLCHEM model class.

        Returns
        -------
        int
            0 on success.

        Raises
        ------
        ValueError
            If `chem_model` is not a valid model name.
        """
        model = self.MODEL_MAP.get(self.chem_model, None)
        self.model_class = self._validate_chemical_model(model)
        return 0

    def commit_particles(self) -> int:
        """
        Initializes the abundances for all particles to an array of zeros
        as a `Particles` vector attribute.
        """
        species = tuple(get_species_names())
        self.uclchem_particles.add_vector_attribute('abundance', species)
        self.uclchem_particles.abundance = np.zeros(len(species))
        return 0

    def recommit_parameters(self) -> int:
        """
        Convert the chemical model name to its corresponding AbstractModel class.

        Validates that the chemical model specified by the user maps to a valid
        UCLCHEM model class.

        Returns
        -------
        int
            0 on success.

        Raises
        ------
        ValueError
            If `chem_model` is not a valid model name.
        """
        self.commit_parameters()
        return 0

    def recommit_particles(self) -> int:
        return 0

    # def synchronize_model(self) -> int:
    #     return 0

    def evolve_model(self, time) -> int:
        """
        Evolve the current model to a specified end time in years.
        The chemistry physics can be changed by calling
        `set_chemical_model`.

        Parameters
        ----------
        time : float
            Time to evolve the chemistry to in years.

        Returns
        -------
        int :
            0 on success, -1 if `time` is less than or equal
            to the current simulation time.
        """
        dt = float(time - self.current_time)
        if dt <= 0:
            return -1

        for particle in self.uclchem_particles:
            params = self._particle_to_dict(particle)
            params['finalTime'] = dt

            starting_chem = (
                particle.abundance[np.newaxis, :] if
                np.any(particle.abundance) else None
            )
            new_model = self.model_class(
                param_dict=params,
                starting_chemistry=starting_chem
            )
            physics = new_model.physics_array
            particle.number_density = physics[-1, 0, 1]
            particle.temperature = physics[-1, 0, 2]
            particle.abundance = new_model.next_starting_chemistry_array[0, :]

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
        Add a new particle to UCLCHEM.

        Parameters
        ----------
        index_of_the_particle : amuse.rfi.python_code.ValueHolder[int]
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
        index_of_the_particle.value = len(self.uclchem_particles)
        self.uclchem_particles.add_particle(p)
        return 0

    def delete_particle(self, index_of_the_particle) -> int:
        """
        Delete a particle in UCLCHEM.

        Parameters
        ----------
        index_of_the_particle : int
            index of the particle to delete, as returned by 'new_particle`.

        Returns
        -------
        int :
            0 if particle was deleted, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        self.uclchem_particles.remove_particles(self.uclchem_particles[i].as_set())

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
        number_density : amuse.rfi.python_code.ValueHolder[float]
            Mutable container used to return the number density
            of the particle in units of cm**-3.
        temperature : amuse.rfi.python_code.ValueHolder[float]
            Mutable container used to return the temperature
            of the particle in units of K.
        ionrate : amuse.rfi.python_code.ValueHolder[float]
            Mutable container used to return the ionization
            rate of the particle in units of s**-1.
        radfield : amuse.rfi.python_code.ValueHolder[float]
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

        p = self.uclchem_particles[i]
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

        p = self.uclchem_particles[i]
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
        number_density : amuse.rfi.python_code.ValueHolder[float]
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

        p = self.uclchem_particles[i]
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

        p = self.uclchem_particles[i]
        p.number_density = number_density
        return 0

    def get_temperature(self, index_of_the_particle, temperature) -> int:
        """
        Retrieve the temperature of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        temperature : amuse.rfi.python_code.ValueHolder[float]
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

        p = self.uclchem_particles[i]
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

        p = self.uclchem_particles[i]
        p.temperature = temperature
        return 0

    def get_ionrate(self, index_of_the_particle, ionrate) -> int:
        """
        Retrieve the ionization rate of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        ionrate : amuse.rfi.python_code.ValueHolder[float]
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

        p = self.uclchem_particles[i]
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

        p = self.uclchem_particles[i]
        p.ionrate = ionrate
        return 0

    def get_radfield(self, index_of_the_particle, radfield) -> int:
        """
        Retrieve the radiation field of a particle by index.

        Parameters
        ----------
        index_of_the_particle: int
            Index of the particle as returned by `new_particle`.
        radfield : amuse.rfi.python_code.ValueHolder[float]
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

        p = self.uclchem_particles[i]
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

        p = self.uclchem_particles[i]
        p.radfield = radfield
        return 0

    def get_abundance(self, index_of_the_particle, abundance_index, abundance) -> int:
        """
        Retrieve the chemical abundance of a species by index for a given particle.

        The `abundance_index` can be queried for using the methods `get_species_index`
        and `get_species_name`.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        abundance_index : int
            Index of the abundance in the abundance array of the particle.
            The `abundance_index` can be calculated using `get_species_index`.
        abundance : amuse.rfi.python_code.ValueHolder[float]
            Mutable container used to return the abundance of a particle.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        if len(self.uclchem_particles) < 1:
            raise ValueError(
                'Uclchem has no particles!'
            )
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        abundance.value = self.uclchem_particles[i].abundance[abundance_index]
        return 0

    def set_abundance(self, index_of_the_particle, abundance_index, abundance) -> int:
        """
        Set the chemical abundance of a species by index for a given particle.

        The `abundance_index` can be queried for using the methods `get_species_index`
        and `get_species_name`.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        abundance_index : int
            Index of the abundance in the abundance array of the particle.
            The `abundance_index` can be calculated using `get_species_index`.
        abundance : float
            Abundance of the chemical species of the particle.

        Returns
        -------
        int :
            0 on success, -1 if the particle index is invalid.
        """
        i = index_of_the_particle
        if not self._is_valid_particle_index(i):
            return -1

        self.uclchem_particles[i].abundance[abundance_index] = abundance
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
        chem_model : amuse.rfi.python_code.ValueHolder[str]
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
        self.chem_model = chem_model
        self.model_class = self._validate_chemical_model(
            self.MODEL_MAP.get(self.chem_model, None)
        )
        return 0

    def get_species_index(self, name, i) -> int:
        """
        Given the name of a chemical species in the
        chemical abundance array, retrieve its index.

        Chemical abundances for each particle are stored
        as a 1D array, where each element corresponds to
        the abundance of a particular species.

        Parameters
        ----------
        name : str
            Name of chemical species. Must be one of the
            species tracked by UCLCHEM.
        i : amuse.rfi.python_code.ValueHolder[int]
            Mutable container used to return the index
            of the species.

        Returns
        -------
        int :
            0 on success, -1 if the species does not exist.

        Examples
        --------
        >>> chem = Uclchem()
        >>> chem.get_species_index('H2O')
        31
        """
        species_names = get_species_names()

        try:
            idx = species_names.index(name)
        except ValueError:
            return -1

        i.value = idx
        return 0

    def get_species_name(self, i, name) -> int:
        """
        Given the index of a chemical species in the
        chemical abundance array, retrieve its name.

        Chemical abundances for each particle are stored
        as a 1D array, where each element corresponds to
        the abundance of a particular species.

        Parameters
        ----------
        i : int
            Index of the chemical species in the abundance array.
        name : amuse.rfi.python_code.ValueHolder[str]
            Mutable container used to return the name of
            the chemical species.

        Examples
        --------
        >>> chem = Uclchem()
        >>> chem.get_species_name(31)
        'H2O'
        """
        species_names = get_species_names()
        if not 0 <= i < len(species_names):
            return -1

        name.value = species_names[i]
        return 0

    def get_time(self, time) -> int:
        """
        Retrieve current model time in years.

        Parameters
        ----------
        time : amuse.rfi.python_code.ValueHolder[float]
            Mutable container used to return the
            current time in units of years.

        Returns
        -------
        int :
            0 on success.
        """
        time.value = self.current_time
        return 0

    def _validate_chemical_model(self, model: type[AbstractModel] | None) -> type[AbstractModel]:
        """
        Validate chemical model class.

        Parameters
        ----------
        model : type[AbstractModel] | None
            Model class to validate.

        Returns
        -------
        type[AbstractModel]
            Validated model class.

        Raises
        ------
        ValueError
            If model is None.
        """
        if model is None:
            raise ValueError(
                'chem_model must be one of the following options: '
                "'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'! "
                f'Got {self.chem_model}.'
            )
        return model

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
        return 0 <= i < len(self.uclchem_particles)

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
            'zeta': float(particle.ionrate) / 1.3e-17,
            'radfield': float(particle.radfield),
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
        """
        Retrieve the chemical abundance of a species by index for a given particle.

        The `abundance_index` can be queried for using the methods `get_species_index`
        and `get_species_name`.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('abundance_index', dtype='int32', direction=function.IN)
        function.addParameter('abundance', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_abundance():
        """
        Set the chemical abundance of a species by index for a given particle.

        The `abundance_index` can be queried for using the methods `get_species_index`
        and `get_species_name`.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('abundance_index', dtype='int32', direction=function.IN)
        function.addParameter('abundance', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_species_index():
        """
        Given the name of a chemical species in the
        chemical abundance array, retrieve its index.

        Chemical abundances for each particle are stored
        as a 1D array, where each element corresponds to
        the abundance of a particular species.
        """
        function = LegacyFunctionSpecification()
        function.addParameter('name', dtype='string', direction=function.IN)
        function.addParameter('i', dtype='int32', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_species_name():
        """
        Given the index of a chemical species in the
        chemical abundance array, retrieve its name.

        Chemical abundances for each particle are stored
        as a 1D array, where each element corresponds to
        the abundance of a particular species.
        """
        function = LegacyFunctionSpecification()
        function.addParameter('i', dtype='int32', direction=function.IN)
        function.addParameter('name', dtype='string', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def get_time():
        """
        Retrieve the model time. This time should be close to the end time
        specified in the evolve code.
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

    def get_abundances(self, index_of_the_particle, species_names):
        """
        Get the abundances of a particle at the current simulation time
        by species name. Both a single species name or a list of names
        are valid inputs.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        species_names : list[str]
            List of species names to query. Each name must be a species
            tracked by the UCLCHEM network. A sigle name is also a valid input.

        Returns
        -------
        abundances : list[float]
            List containing the current abundances of the particle for
            each species name passed in.

        Notes
        -----
        To obtain the list of species in UCLCHEM:
        >>> from uclchem.model import get_species_names
        >>> get_species_names()
        ['H', 'H+', 'H2', ...]
        """
        i = index_of_the_particle
        if not isinstance(species_names, list):
            species_names = [species_names]

        indices = [self.get_species_index(species) for species in species_names]
        return [self.get_abundance(i, aid) for aid in indices]

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
