from amuse.community.interface.chem import (
    ChemicalEvolution, ChemicalEvolutionInterface
)
from amuse.rfi.core import (
    CodeInterface,
    LegacyFunctionSpecification,
    legacy_function
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
        CodeInterface.__init__(
            self, name_of_the_worker = self.name_of_the_worker(), **options
        )
        LiteratureReferencesMixIn.__init__(self)

    def name_of_the_worker(self):
        return 'krome_worker'

    @legacy_function
    def new_particle():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.OUT)
        for x in ['number_density','temperature','ionrate']:
            function.addParameter(x, dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def set_state():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        for x in ['number_density','temperature','ionrate']:
            function.addParameter(x, dtype='d', direction=function.IN)
        function.result_type = 'i'
        return function

    @legacy_function
    def get_state():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='i', direction=function.IN)
        for x in ['number_density','temperature','ionrate']:
            function.addParameter(x, dtype='d', direction=function.OUT)
        function.result_type = 'i'
        return function


class Krome(ChemicalEvolution):

    def __init__(self, unit_converter=None, **options):

        if unit_converter is not None:
            raise Exception('Krome uses predefined units')

        ChemicalEvolution.__init__(self, KromeInterface(**options))

        first, last = self.get_firstlast_species_index()
        self.species = dict()
        for i in range(first, last+1):
          self.species[self.get_species_name(i)] = i - 1

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
                units.cm**-3,
                units.K,
                units.s**-1,
            ),
            (handler.INDEX, handler.ERROR_CODE,)
        )

        handler.add_method(
            'get_state',
            (
                handler.INDEX,
            ),
            (
                units.cm**-3,
                units.K,
                units.s**-1,
                handler.ERROR_CODE,
            )
        )
        handler.add_method(
            "get_abundance",
            (
                handler.INDEX,
                handler.INDEX,
            ),
            (
                handler.NO_UNIT,
                handler.ERROR_CODE,
            )
        )
        handler.add_method(
            "set_abundance",
            (
                handler.INDEX,
                handler.INDEX,
                handler.NO_UNIT,
            ),
            (
                handler.ERROR_CODE,
            )
        )
        handler.add_method(
            "delete_particle",
            (
                handler.INDEX,
            ),
            (
                handler.ERROR_CODE,
            )
        )
        handler.add_method(
            "get_firstlast_abundance",
            (
            ),
            (
                handler.NO_UNIT,
                handler.NO_UNIT,
                handler.ERROR_CODE,
            )
        )
        handler.add_method(
            "get_time",
            (
            ),
            (
                units.s,
                handler.ERROR_CODE,
            )
        )

    def define_particle_sets(self, handler):
        handler.define_set('particles', 'id')
        handler.set_new('particles', 'new_particle')
        handler.set_delete('particles', 'delete_particle')
        handler.add_setter('particles', 'set_state')
        handler.add_getter('particles', 'get_state')
        handler.add_gridded_getter('particles', 'get_abundance','get_firstlast_abundance', names = ('abundances',))
        handler.add_gridded_setter('particles', 'set_abundance','get_firstlast_abundance', names = ('abundances',))

    def define_state(self, handler):
        CommonCode.define_state(self, handler)
        handler.add_transition('INITIALIZED','EDIT','commit_parameters')
        handler.add_transition('RUN','PARAMETER_CHANGE_A','invoke_state_change2')
        handler.add_transition('EDIT','PARAMETER_CHANGE_B','invoke_state_change2')
        handler.add_transition('PARAMETER_CHANGE_A','RUN','recommit_parameters')
        handler.add_transition('PARAMETER_CHANGE_B','EDIT','recommit_parameters')
        handler.add_method('EDIT', 'new_particle')
        handler.add_method('EDIT', 'delete_particle')
        handler.add_transition('EDIT', 'RUN', 'commit_particles')
        handler.add_transition('RUN', 'UPDATE', 'new_particle', False)
        handler.add_transition('RUN', 'UPDATE', 'delete_particle', False)
        handler.add_transition('UPDATE', 'RUN', 'recommit_particles')
        handler.add_method('RUN', 'evolve_model')
        handler.add_method('RUN', 'get_state')
        handler.add_method('RUN', 'get_abundance')


