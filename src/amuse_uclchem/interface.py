"""
AMUSE interface for UCLCHEM, a gas-grain chemical code that
propagates the abundances of chemical species through a network
of user-defined reactions according to the physical conditions of the gas.

Date Created:  April 01, 2026
Date Modified: April 30, 2026
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


habing = u.named('habing', 'hab', 1.6e-3 * u.erg * u.cm**-2 * u.s**-1)

class UclchemImplementation(object):

    def __init__(self):
        self.current_time: float = 0
        self.model: Literal['cloud', 'collapse', 'cshock', 'hot_core', 'jshock'] = 'cloud'
        self.collapse: Literal['BE1.1', 'BE4', 'filament', 'ambipolar'] = 'BE1.1'
        # self.MODEL_MAP: dict = {
        #     'cloud': uclchem.model.Cloud,
        #     'collapse': uclchem.model.collapse,
        #     'cshock': uclchem.model.cshock,
        #     'hot_core': uclchem.model.hot_core,
        #     'jshock': uclchem.model.jshock,
        # }
        self.param_dict: dict = {}
        self.particles = Particles()

    def initialize_code(self):
        # self.parameters = uclchem.advanced.GeneralSettings()
        return 0

    def cleanup_code(self):
        return 0

    def commit_parameters(self):
        return 0

    def commit_particles(self):
        return 0

    def recommit_parameters(self):
        return 0

    def recommit_particles(self):
        return 0

    # def synchronize_model(self):
    #     return 0

    # def evolve_model(self, time) -> int:
    #     model = self.MODEL_MAP.get(self.model, None)
    #     if model is None:
    #         return -1
    #     model(param_dict=self.param_dict, return_array=True)

    #     return 0

    def new_particle(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ) -> int:
        p = Particle()
        p.number_density = number_density
        p.temperature = temperature
        p.ionrate = ionrate
        p.radfield = radfield
        index_of_the_particle.value = len(self.particles)
        self.particles.add_particle(p)

        return 0

    def get_state(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ) -> int:
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
        i = index_of_the_particle

        if not self._is_valid_particle_index(i):
            return -1

        p = self.particles
        p[i].number_density = number_density
        p[i].temperature = temperature
        p[i].ionrate = ionrate
        p[i].radfield = radfield
        return 0

    def _is_valid_particle_index(self, i):
        if i < 0 or i >= len(self.particles):
            return False
        return True


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
        # Standard function
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
    def get_abundance():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('aid', dtype='int32', direction=function.IN)
        function.addParameter('abundance', dtype='float64', direction=function.OUT)
        function.result_type = 'int32'
        return function

    @legacy_function
    def set_abundance():
        function = LegacyFunctionSpecification()
        function.can_handle_array = True
        function.addParameter('index_of_the_particle', dtype='int32', direction=function.IN)
        function.addParameter('aid', dtype='int32', direction=function.IN)
        function.addParameter('abundance', dtype='float64', direction=function.IN)
        function.result_type = 'int32'
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
            'get_abundance',
            (handler.INDEX, handler.INDEX),
            (handler.NO_UNIT, handler.ERROR_CODE),
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


    def define_parameters(self, handler):
        handler.add_interface_parameter(
            "out_species", "Array of molecules to use", default_value=["H", "H2"]
        )

    def define_particle_sets(self, handler):
        handler.define_set("particles", "index_of_the_particle")
        handler.set_new("particles", "new_particle")
        handler.set_delete("particles", "delete_particle")
        handler.add_setter("particles", "set_state")
        handler.add_getter("particles", "get_state")
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
        handler.add_method("EDIT", "delete_particle")
        handler.add_transition("EDIT", "RUN", "commit_particles")
        handler.add_transition("RUN", "UPDATE", "new_particle", False)
        handler.add_transition("RUN", "UPDATE", "delete_particle", False)
        handler.add_transition("UPDATE", "RUN", "recommit_particles")
        handler.add_method("RUN", "evolve_model")
        handler.add_method("RUN", "get_state")
        handler.add_method("RUN", "get_abundance")
