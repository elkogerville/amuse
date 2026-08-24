"""
Chemical Evolution Interface Definition
"""

from amuse.units import units as u
from amuse.community.interface import common

from amuse.rfi.core import legacy_function
from amuse.rfi.core import LegacyFunctionSpecification


class ChemicalEvolutionInterface(common.CommonCodeInterface):

    @legacy_function
    def evolve_model():
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
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        function.result_type = 'i'
        function.result_doc = """
        0 - OK
            particle was removed from the model
        -1 - ERROR
            particle could not be removed
        -2 - ERROR
            not yet implemented
        """
        return function

    @legacy_function
    def get_abundance():
        """
        Retrieve the chemical abundance of a species by index for a given particle.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        function.addParameter('abundance_index', dtype='i', direction=function.IN)
        function.addParameter('abundance', dtype='d', direction=function.OUT)
        function.result_type = 'i'
        return function

    @legacy_function
    def set_abundance():
        """
        Set the chemical abundance of a species by index for a given particle.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        function.addParameter('abundance_index', dtype='i', direction=function.IN)
        function.addParameter('abundance', dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def get_firstlast_abundance():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('first', dtype='i', direction=function.OUT)
        function.addParameter('last', dtype='i', direction=function.OUT)
        function.result_type = 'i'
        return function

    @legacy_function
    def get_time():
        """
        Retrieve the model time. This time should be close to the end time
        specified in the evolve code.
        """
        function = LegacyFunctionSpecification()
        function.addParameter('time', dtype='d', direction=function.OUT)
        function.result_type = 'i'
        function.result_doc = """
            0 - OK
                Current value of the time was retrieved
        """
        return function

    @legacy_function
    def get_number_of_particles():
        """
        Retrieve the total number of particles defined in the code.
        """
        function = LegacyFunctionSpecification()
        function.addParameter(
            'number_of_particles',
            dtype='int32',
            direction=function.OUT,
            description='Count of the particles in the code',
        )
        function.result_type = 'int32'
        function.result_doc = """
            0 - OK
                Count could be determined
            -1 - ERROR
                Unable to determine the count
        """
        return function
