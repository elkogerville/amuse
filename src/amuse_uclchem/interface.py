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

class Uclchem:
    pass
