"""
Chemical Evolution Interface Definition
"""

from collections.abc import Sequence

from amuse.community.interface import common
from amuse.rfi.core import legacy_function, remote_function
from amuse.rfi.core import LegacyFunctionSpecification
from amuse.units import units as u
import numpy as np
from numpy.typing import NDArray


class ChemicalEvolutionInterface(common.CommonCodeInterface):

    @legacy_function
    def commit_particles():
        """
        Let the code perform initialization actions
        after all particles have been loaded in the model.
        Should be called before the first evolve call and
        after the last new_particle call.
        """
        function = LegacyFunctionSpecification()
        function.result_type = 'i'
        function.result_doc = """
            0 - OK
                Model is initialized and evolution can start
            -1 - ERROR
                Error happened during initialization, this error needs to be
                further specified by every code implemention
        """
        return function

    @legacy_function
    def recommit_particles():
        """
        Let the code perform initialization actions
        after the number of particles have been updated
        or particle attributes have been updated from
        the script.
        """
        function = LegacyFunctionSpecification()
        function.result_type = 'i'
        function.result_doc = """
            0 - OK
                Model is initialized and evolution can start
            -1 - ERROR
                Error happened during initialization, this error needs to be
                further specified by every code implemention
        """
        return function

    @legacy_function
    def evolve_model():
        """
        Evolve the model until the given time, or until a stopping
        condition is set. The model will be evolved until this time
        is reached exactly or just after.
        """
        function = LegacyFunctionSpecification()
        function.addParameter('time', dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def delete_particle():
        """
        Remove the definition of particle from the code. After calling this
        function the particle is no longer part of the model evolution. It is
        up to the code if the index will be reused.
        This function is optional.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        function.result_type = 'i'
        function.result_doc = """
            0 - OK
                particle was removed from the model
            -1 - ERROR
                particle could not be removed
        """
        return function

    @remote_function(can_handle_array=True)
    def get_abundance(index_of_the_particle='i', abundance_index='i'):
        """
        Retrieve the chemical abundance of a species by index for a given particle.

        The `abundance_index` can be queried for using the methods `get_species_index`
        and `get_species_name`.
        """
        returns (abundance='d')

    @remote_function(can_handle_array=True)
    def set_abundance(
        index_of_the_particle='i', abundance_index='i', abundance='d'
    ):
        """
        Set the chemical abundance of a species by index for a given particle.

        The `abundance_index` can be queried for using the methods `get_species_index`
        and `get_species_name`.
        """
        returns ()

    @legacy_function
    def set_abundances():
        function = LegacyFunctionSpecification()
        function.must_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        function.addParameter('abundances', dtype='d', direction=function.IN)
        function.addParameter('N', dtype='i', direction=function.LENGTH)
        function.result_type = 'i'
        return function

    @remote_function(can_handle_array=True)
    def get_firstlast_species_index():
        returns (first='i', last='i')

    @remote_function
    def get_species_index(name='s'):
        """
        Given the name of a chemical species in the
        chemical abundance array, retrieve its index.

        Chemical abundances for each particle are stored
        as a 1D array, where each element corresponds to
        the abundance of a particular species.

        Examples
        --------
        >>> chem.get_species_index('H')
        0
        """
        returns (abundance_index='i')

    @remote_function
    def get_species_name(abundance_index='i'):
        """
        Given the index of a chemical species in the
        chemical abundance array, retrieve its name.

        Chemical abundances for each particle are stored
        as a 1D array, where each element corresponds to
        the abundance of a particular species.

        Examples
        --------
        >>> chem.get_species_name(0)
        'H'
        """
        returns (name='s')

    @remote_function
    def get_time():
        """
        Retrieve the model time. This time should be close to the end time
        specified in the evolve code.
        """
        returns (time='d')

    @remote_function
    def get_number_of_particles():
        """Retrieve the total number of particles defined in the code."""
        returns (number_of_particles='i')


class ChemicalEvolution(common.CommonCode):

    def __init__(self, legacy_interface, unit_converter=None, **options):
        self.unit_converter = unit_converter

        common.CommonCode.__init__(self, legacy_interface, **options)

    def get_abundances_by_name(
        self,
        index_of_the_particle: int,
        species_names: str | Sequence[str]
    ) -> NDArray:
        """
        Get the abundances of a particle at the current simulation time
        by species name. Both a single species name or a sequence of names
        are valid inputs.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle as returned by `new_particle`.
        species_names : str | Sequence[str]
            Species name(s) to query. Each name must be a species
            tracked by the chemistry code network. A single name is
            also a valid input.

        Returns
        -------
        abundances : np.ndarray[float]
            Array containing the current abundances of the particle for
            each species name passed in.

        Examples
        --------
        >>> chem = Krome()
        >>> chem.particles.add_particles(particles)
        >>> chem.get_abundances_by_name(1, ['H','H2'])
        [1.00000000e-40, 1.00000000e-40]

        Notes
        -----
        To obtain a dictionary of each (species: index) in a chemistry code:
        >>> chem = Krome()
        >>> chem.species
        {'E': 0, 'H-': 1, 'H': 2, 'HE': 3, 'H2': 4, ...}
        """
        i = index_of_the_particle
        if isinstance(species_names, str):
            species_names = [species_names]

        indices = [
            self.get_species_index(species) for species in species_names
        ]
        return np.asarray([self.get_abundance(i, aid) for aid in indices])

    def define_properties(self, handler):
        handler.add_property('get_time', public_name='model_time')

    def define_methods(self, handler):
        common.CommonCode.define_methods(self, handler)

        handler.add_method('evolve_model', (u.yr,), (handler.ERROR_CODE,))

        handler.add_method(
            'delete_particle', (handler.INDEX,), (handler.ERROR_CODE,)
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
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'set_abundances',
            (handler.INDEX, handler.NO_UNIT,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_firstlast_species_index',
            (),
            (
                handler.NO_UNIT,
                handler.NO_UNIT,
                handler.ERROR_CODE,
            )
        )

        handler.add_method(
            'get_time',
            (),
            (u.yr, handler.ERROR_CODE,),
        )

        handler.add_method(
            'get_number_of_particles',
            (),
            (handler.NO_UNIT, handler.ERROR_CODE,),
        )

    def define_particle_sets(self, handler):
        handler.define_set('particles', 'index_of_the_particle')
        handler.set_new('particles', 'new_particle')
        handler.set_delete('particles', 'delete_particle')
        handler.add_setter('particles', 'set_state')
        handler.add_getter('particles', 'get_state')
        handler.add_gridded_getter(
            'particles',
            'get_abundance',
            'get_firstlast_species_index',
            names=('abundances',),
        )
        handler.add_gridded_setter(
            'particles',
            'set_abundance',
            'get_firstlast_species_index',
            names=('abundances',),
        )

    def define_state(self, handler):
        common.CommonCode.define_state(self, handler)
        handler.add_transition('INITIALIZED', 'EDIT', 'commit_parameters')
        handler.add_transition('RUN', 'PARAMETER_CHANGE_A', 'invoke_state_change2')
        handler.add_transition('EDIT', 'PARAMETER_CHANGE_B', 'invoke_state_change2')
        handler.add_transition('PARAMETER_CHANGE_A', 'RUN', 'recommit_parameters')
        handler.add_transition('PARAMETER_CHANGE_B', 'EDIT', 'recommit_parameters')
        handler.add_method('EDIT', 'new_particle')
        handler.add_method('EDIT', 'delete_particle')
        handler.add_transition('EDIT', 'RUN', 'commit_particles')
        handler.add_transition('RUN', 'UPDATE', 'new_particle', False)
        handler.add_transition('RUN', 'UPDATE', 'delete_particle', False)
        handler.add_transition('UPDATE', 'RUN', 'recommit_particles')
        handler.add_method('RUN', 'evolve_model')
        handler.add_method('RUN', 'get_state')
        handler.add_method('RUN', 'get_abundance')
