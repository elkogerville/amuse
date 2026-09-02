from typing import Literal

import numpy as np
from numpy.typing import NDArray
import uclchem
from uclchem.model import (
    get_species_names as _get_species_names, AbstractModel
)

from amuse.community.interface.chem import (
    ChemicalEvolution, ChemicalEvolutionInterface
)
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.datamodel import Particle, Particles
from amuse.rfi.core import (
    LegacyFunctionSpecification, PythonCodeInterface, legacy_function
)
from amuse.units import units as u


habing = u.named('habing', 'hab', 1.6e-3 * u.erg * u.cm**-2 * u.s**-1)

"""
* arepo interface?
* print(chem.particles fails because abundance attr is an array and the print method expects float, how to deal)
"""

class UclchemImplementation(object):
    def __init__(self):
        """
        Implementation of Uclchem legacy interface functions.

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
        self.param_dict : dict
            Dictionary to hold any additional parameters sent to Uclchem before evolving.
            Parameter getters and setters should modify this dictionary.
        uclchem_particles : amuse.datamodel.Particles
            Particles datamodel for storing UCLCHEM particles.
        _ids : np.ndarray[int]
            Array of unique ids for each particle in `uclchem_particles`.
        _next_particle_id : int
            Next particle index. New ids are assigned by `_get_new_id`.
        """
        self.current_time: float = 0
        self.chem_model: str = 'cloud'
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
        self.param_dict: dict = {}
        self.uclchem_particles: Particles = Particles()
        self._ids: NDArray = np.empty(0, dtype=np.int64)
        self._next_particle_id: int = 0

    def initialize_code(self) -> int:
        # self.parameters = uclchem.advanced.GeneralSettings()
        return 0

    def cleanup_code(self) -> int:
        """Remove all the particles stored in UCLCHEM."""
        self.uclchem_particles.remove_particles(self.uclchem_particles)
        return 0

    def commit_parameters(self) -> int:
        """
        Convert the chemical model string name to its corresponding AbstractModel class.

        Validates that the chemical model specified by the user maps to a valid
        UCLCHEM model class.

        Returns
        -------
        int :
            0 on success.

        Raises
        ------
        ValueError :
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
        species = tuple(_get_species_names())
        self.uclchem_particles.add_vector_attribute('abundances', species)
        self.uclchem_particles.abundances = np.zeros(len(species)) #+ 1-30
        return 0

    def recommit_parameters(self) -> int:
        """
        Convert the chemical model name to its corresponding AbstractModel class.

        Validates that the chemical model specified by the user maps to a valid
        UCLCHEM model class.

        Returns
        -------
        int :
            0 on success.

        Raises
        ------
        ValueError :
            If `chem_model` is not a valid model name.
        """
        self.commit_parameters()
        return 0

    def recommit_particles(self) -> int:
        return 0

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
            params.update(self.param_dict)

            starting_chem = (
                particle.abundances[np.newaxis, :] if
                np.any(particle.abundances) else None
            )
            new_model = self.model_class(
                param_dict=params,
                starting_chemistry=starting_chem
            )
            physics = new_model.physics_array
            particle.number_density = physics[-1, 0, 1]
            particle.temperature = physics[-1, 0, 2]
            particle.abundances = new_model.next_starting_chemistry_array[0, :]

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
            0 on success.
        """
        p = Particle()
        p.number_density = number_density
        p.temperature = temperature
        p.ionrate = ionrate
        p.radfield = radfield

        id = self._get_new_id()
        index_of_the_particle.value = id
        self.uclchem_particles.add_particle(p)
        self._ids = np.append(self._ids, id)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

        print('IIIIII', i)
        print('KEY', self.uclchem_particles.key)
        print('INDECES', self.uclchem_particles.get_indices_of_keys(self.uclchem_particles.key))
        print('delete this 1: ', self.uclchem_particles[i].key)

        self.uclchem_particles.remove_particles(self.uclchem_particles[i].as_set())
        self._ids = np.delete(self._ids, i)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)

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
        i = self._get_particle_index_by_id(index_of_the_particle)
        abundance.value = self.uclchem_particles[i].abundances[abundance_index]
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
        i = self._get_particle_index_by_id(index_of_the_particle)

        abundances = self.uclchem_particles[i].abundances
        abundances[abundance_index] = abundance
        self.uclchem_particles[i].abundances = abundances
        return 0

    def set_abundances(self, index_of_the_particle, abundances, N) -> int:
        """
        Set the full chemical abundance array for a given particle.

        Parameters
        ----------
        index_of_the_particle : np.ndarray[int]
            Index of the particle as returned by `new_particle`. If an array,
            only the first element is used.
        abundances : np.ndarray[float]
            Abundance values to assign to the particle, of length `N`.
        N : int
            Number of abundance values in `abundances`. Must match the
            particle's existing abundance array length.

        Returns
        -------
        int :
            0 on success.

        Raises
        ------
        ValueError
            If `N` does not match the particle's existing number of abundances.
        """
        if not isinstance(index_of_the_particle, int):
            index_of_the_particle = index_of_the_particle[0]
        i = self._get_particle_index_by_id(index_of_the_particle)
        N_abundances = self.uclchem_particles[i].abundances.shape[0]
        if N != N_abundances:
            raise ValueError(
                f'abundances must have shape {N_abundances}, got {N}!'
            )
        self.uclchem_particles[i].abundances = abundances
        return 0

    def get_firstlast_species_index(self, first, last) -> int:
        """
        Get the index of the first and last species inside UCLCHEM.

        This is a helper method for accessing the abundance array as
        `instance.particles.abundances`.

        Parameters
        ----------
        first : amuse.rfi.python_code.ValueHolder[int]
            Index of the first species in the abundance array.
        last : amuse.rfi.python_code.ValueHolder[int]
            Index of the last species in the abundance array.

        Returns
        -------
        int :
            0 on success.
        """
        first.value = 0
        last.value = len(get_species_names()) - 1
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

    def get_species_index(self, name, index) -> int:
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
        index : amuse.rfi.python_code.ValueHolder[int]
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

        index.value = idx
        return 0

    def get_species_name(self, index, name) -> int:
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
        if not 0 <= index < len(species_names):
            return -1

        name.value = species_names[index]
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

    def get_number_of_particles(self, number_of_particles) -> int:
        """
        Retrieve the current number of particles in the code.

        Parameters
        ----------
        number_of_particles : amuse.rfi.python_code.ValueHolder[int]
            Mutable container used to return the
            current number of particles.

        Returns
        -------
        int :
            0 on success.
        """
        number_of_particles.value = len(self.uclchem_particles)
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

    def _validate_chemical_model(self, model: type[AbstractModel] | None) -> type[AbstractModel]:
        """
        Validate chemical model class.

        Parameters
        ----------
        model : type[AbstractModel] | None
            Model class to validate.

        Returns
        -------
        type[AbstractModel] :
            Validated model class.

        Raises
        ------
        ValueError :
            If `model` is `None`.
        """
        if model is None:
            raise ValueError(
                'chem_model must be one of the following options: '
                "'cloud', 'collapse', 'cshock', 'jshock', 'prestellarcore'! "
                f'Got {self.chem_model}.'
            )
        return model

    def _get_particle_index_by_id(self, index_of_the_particle: int) -> int:
        idx = np.where(self._ids == index_of_the_particle)[0]
        if idx.size == 0:
            raise ValueError(f'Particle id: {index_of_the_particle} not found!')

        return int(idx[0])

    def _get_new_id(self) -> int:
        """Create a unique, monotonically increasing id for `new_particle`."""
        new_id = self._next_particle_id
        self._next_particle_id += 1

        return int(new_id)

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


class UclchemInterface(
    ChemicalEvolutionInterface,
    PythonCodeInterface,
    LiteratureReferencesMixIn,
):
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
    def new_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.OUT)
        for x in ['number_density', 'temperature', 'ionrate', 'radfield']:
            function.addParameter(x, dtype='float64', direction=function.IN)
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

    # @legacy_function
    # def get_abundance():
    #     """
    #     Retrieve the chemical abundance of a species by index for a given particle.

    #     The `abundance_index` can be queried for using the methods `get_species_index`
    #     and `get_species_name`.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.can_handle_array = True
    #     function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
    #     function.addParameter('abundance_index', dtype='int32', direction=function.IN)
    #     function.addParameter('abundance', dtype='float64', direction=function.OUT)
    #     function.result_type = 'int32'
    #     return function

    # @legacy_function
    # def set_abundance():
    #     """
    #     Set the chemical abundance of a species by index for a given particle.

    #     The `abundance_index` can be queried for using the methods `get_species_index`
    #     and `get_species_name`.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.can_handle_array = True
    #     function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
    #     function.addParameter('abundance_index', dtype='int32', direction=function.IN)
    #     function.addParameter('abundance', dtype='float64', direction=function.IN)
    #     function.result_type = 'int32'
    #     return function

    # @legacy_function
    # def get_firstlast_abundance():
    #     function = LegacyFunctionSpecification()
    #     function.can_handle_array = True
    #     function.addParameter('first', dtype='int32', direction=function.OUT)
    #     function.addParameter('last', dtype='int32', direction=function.OUT)
    #     function.result_type = 'int32'
    #     return function

    # @legacy_function
    # def get_species_index():
    #     """
    #     Given the name of a chemical species in the
    #     chemical abundance array, retrieve its index.

    #     Chemical abundances for each particle are stored
    #     as a 1D array, where each element corresponds to
    #     the abundance of a particular species.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.addParameter('name', dtype='string', direction=function.IN)
    #     function.addParameter('i', dtype='int32', direction=function.OUT)
    #     function.result_type = 'int32'
    #     return function

    # @legacy_function
    # def get_species_name():
    #     """
    #     Given the index of a chemical species in the
    #     chemical abundance array, retrieve its name.

    #     Chemical abundances for each particle are stored
    #     as a 1D array, where each element corresponds to
    #     the abundance of a particular species.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.addParameter('i', dtype='int32', direction=function.IN)
    #     function.addParameter('name', dtype='string', direction=function.OUT)
    #     function.result_type = 'int32'
    #     return function

    # @legacy_function
    # def get_time():
    #     """
    #     Retrieve the model time. This time should be close to the end time
    #     specified in the evolve code.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.addParameter('time', dtype='float64', direction=function.OUT)
    #     function.result_type = 'int32'
    #     function.result_doc = """
    #         0 - OK
    #             Current value of the time was retrieved
    #     """
    #     return function

    # @legacy_function
    # def get_number_of_particles():
    #     """
    #     Retrieve the total number of particles defined in the code.
    #     """
    #     function = LegacyFunctionSpecification()
    #     function.addParameter(
    #         'number_of_particles',
    #         dtype='int32',
    #         direction=function.OUT,
    #         description='Count of the particles in the code',
    #     )
    #     function.result_type = 'int32'
    #     function.result_doc = """
    #         0 - OK
    #             Count could be determined
    #         -1 - ERROR
    #             Unable to determine the count
    #     """
    #     return function


class Uclchem(ChemicalEvolution):

    def __init__(self, unit_converter=None, **options):

        if unit_converter is not None:
            raise ValueError('Uclchem uses predefined units')

        chem_interface = UclchemInterface(**options)

        ChemicalEvolution.__init__(
            self,
            chem_interface
        )

        first, last = self.get_firstlast_species_index()
        self.species = dict()
        for i in range(first, last+1):
          self.species[self.get_species_name(i)] = i

    def get_abundances(
        self,
        index_of_the_particle: int,
        species_names: str | list[str]
    ) -> list[float]:
        """
        Get the abundances of a particle at the current simulation time
        by species name. Both a single species name or a list of names
        are valid inputs.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        species_names : str | list[str]
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
        ChemicalEvolution.define_methods(self, handler)
        handler.add_method(
            'new_particle',
            (u.cm**-3, u.K, u.s**-1, habing),
            (
                handler.INDEX,
                handler.ERROR_CODE,
            ),
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
