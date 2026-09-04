from amuse.community.interface.chem import (
    ChemicalEvolution, ChemicalEvolutionInterface
)
from amuse.rfi.core import (
    CodeInterface,
    LegacyFunctionSpecification,
    legacy_function,
    remote_function
)
from amuse.support.literature import LiteratureReferencesMixIn
from amuse.units import units


# (Grevesse & Sauval, 1998, Space Sci. Rev. 85, 161)
solar_abundances= dict(
    H = 1.0, HE = 0.085,
    C = 3.31e-4, N = 8.3e-5, O = 6.76e-4,
    Ne = 1.2e-4, SI = 3.55e-5, Fe = 3.2e-5
)


class KromeInterface(
    CodeInterface,
    ChemicalEvolutionInterface,
    LiteratureReferencesMixIn
):
    """
    KROME - a package to embed chemistry in astrophysical simulations

    .. [#] Grassi, T.; Bovino, S.; Schleicher, D. R. G.; Prieto, J.; Seifried, D.; Simoncini, E.; Gianturco, F. A., MNRAS, 439, 3, p.2386-2419 [2014MNRAS.439.2386G]
    """

    def __init__(self, **options):
        CodeInterface.__init__(self, name_of_the_worker = self.name_of_the_worker(), **options)
        LiteratureReferencesMixIn.__init__(self)

    def name_of_the_worker(self):
        return 'krome_worker'

    @legacy_function
    def new_particle():
        """
        Add a new particle to Krome.

        Parameters
        ----------
        index_of_the_particle : int
            Index assigned to the newly created particle, returned by Krome.
        rho : float
            Density of the particle in units of g*cm**-3.
        u : float
            Internal energy of the particle in units of cm**2*s**-2.
        gamma : float
            Adiabatic index of the particle. Dimensionless.
        mu : float
            Mean molecular weight of the particle in units of g.
        ionrate : float
            Ionization rate of the particle in units of s**-1.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.OUT
        )
        for x in ['rho', 'u', 'gamma', 'mu', 'ionrate']:
            function.addParameter(x, dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def get_state():
        """
        Get the state of a particle.

        Parameters
        ----------
        index_of_the_particle : int
            Index of the particle to retrieve the state of.
        rho : float
            Density retrieved from the particle, in units of g*cm**-3.
        u : float
            Internal energy retrieved from the particle in units of cm**2*s**-2.
        gamma : float
            Adiabatic index retrieved from the particle. Dimensionless.
        mu : float
            Mean molecular weight retrieved from the particle, in units of g.
        ionrate : float
            Ionization rate retrieved from the particle, in units of s**-1.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        for x in ['rho', 'u', 'gamma', 'mu', 'ionrate']:
            function.addParameter(x, dtype='d', direction=function.OUT)
        function.result_type = 'i'
        return function

    @legacy_function
    def set_state():
        """
        Set the state of a particle.

        Parameters
        ----------
        index_of_the_particle : int
             Index of the particle to set the state of.
        rho : float
            Density to set for the particle, in units of g*cm**-3.
        u : float
            Internal energy to set for the particle, in units of cm**2*s**-2.
        gamma : float
            Adiabatic index to set for the particle. Dimensionless.
        mu : float
            Mean molecular weight to set for the particle, in units of g.
        ionrate : float
            Ionization rate to set for the particle, in units of s**-1.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        for x in ['rho', 'u', 'gamma', 'mu', 'ionrate']:
            function.addParameter(x, dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def get_internal_energy():
        """
        Get the internal energy of a particle.

        Parameters
        ----------
        index_of_the_particle : int
             Index of the particle to retrieve the internal energy of.
        u : float
            Internal energy retrieved from the particle, in units of cm**2*s**-2.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        function.addParameter('u', dtype='d', direction=function.OUT)
        function.result_type = 'i'
        return function

    @legacy_function
    def set_internal_energy():
        """
        Set the internal energy of a particle.

        Parameters
        ----------
        index_of_the_particle : int
             Index of the particle to set the internal energy of.
        u : float
            Internal energy to set for the particle, in units of cm**2*s**-2.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        function.addParameter('u', dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def get_density():
        """
        Get the density of a particle.

        Parameters
        ----------
        index_of_the_particle : int
             Index of the particle to retrieve the density of.
        rho : float
            Density retrieved from the particle, in units of g*cm**-3.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        function.addParameter('rho', dtype='d', direction=function.OUT)
        function.result_type = 'i'
        return function

    @legacy_function
    def set_density():
        """
        Set the density of a particle.

        Parameters
        ----------
        index_of_the_particle : int
             Index of the particle to set the density of.
        rho : float
            Density to set for the particle, in units of g*cm**-3.

        Returns
        -------
        int :
            0 on success.
        """
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter(
            'index_of_the_particle', dtype='i', direction=function.IN
        )
        function.addParameter('rho', dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @remote_function
    def set_amu_in_g(amu_in_g='d'):
        """
        Set the value of the atomic mass unit in grams.
        This function is used internally by AMUSE to
        send the value of amu in grams to Krome at runtime.
        """
        returns ()

class Krome(ChemicalEvolution):

    def __init__(self, unit_converter=None, **options):

        if unit_converter is not None:
            raise Exception('Krome uses predefined units')

        ChemicalEvolution.__init__(self, KromeInterface(**options))

        first, last = self.get_firstlast_species_index()
        self.species = dict()
        for i in range(first, last+1):
          self.species[self.get_species_name(i)] = i - 1

        amu_in_g = (1 | units.amu).value_in(units.g)
        self.set_amu_in_g(amu_in_g)

    def define_properties(self, handler):
        handler.add_property('get_time', public_name='model_time')

    def define_methods(self, handler):
        ChemicalEvolution.define_methods(self, handler)
        handler.add_method(
            'evolve_model',
            (units.s,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'new_particle',
            (
                units.g * units.cm**-3,
                units.cm**2 * units.s**-2,
                handler.NO_UNIT,
                units.g,
                units.s**-1,
            ),
            (handler.INDEX, handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_state',
            (handler.INDEX,),
            (
                units.g * units.cm**-3,
                units.cm**2 * units.s**-2,
                handler.NO_UNIT,
                units.g,
                units.s**-1,
                handler.ERROR_CODE,
            )
        )

        handler.add_method(
            'set_state',
            (
                handler.INDEX,
                units.g * units.cm**-3,
                units.cm**2 * units.s**-2,
                handler.NO_UNIT,
                units.g,
                units.s**-1,
            ),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_density',
            (handler.INDEX,),
            (units.g * units.cm**-3, handler.ERROR_CODE,)
        )

        handler.add_method(
            'set_density',
            (handler.INDEX, units.g * units.cm**-3,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_internal_energy',
            (handler.INDEX,),
            (units.cm**2 * units.s**-2, handler.ERROR_CODE,)
        )

        handler.add_method(
            'set_internal_energy',
            (handler.INDEX, units.cm**2 * units.s**-2,),
            (handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_time',
            (),
            (units.s, handler.ERROR_CODE,)
        )

    def define_particle_sets(self, handler):
        ChemicalEvolution.define_particle_sets(self, handler)
        handler.add_getter('particles', 'get_density')
        handler.add_setter('particles', 'set_density')
        handler.add_getter('particles', 'get_internal_energy')
        handler.add_setter('particles', 'set_internal_energy')
