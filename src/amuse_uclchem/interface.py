"""
AMUSE interface for UCLCHEM, a gas-grain chemical code that
propagates the abundances of chemical species through a network
of user-defined reactions according to the physical conditions of the gas.

Date Created: 2026-04-01
Date Modified: 2026-04-17
"""

from typing import Literal
from amuse.community.interface.common import CommonCode
from amuse.community import (
    LiteratureReferencesMixIn,
    legacy_function,
    LegacyFunctionSpecification,
)
from amuse.rfi.core import PythonCodeInterface


class UclchemImplementation(object):

    def __init__(self):
        import uclchem
        self.uclchem = uclchem
        self.current_time: float = 0
        self.model: Literal['cloud', 'collapse', 'cshock', 'hot_core', 'jshock'] = 'cloud'
        self.collapse: Literal['BE1.1', 'BE4', 'filament', 'ambipolar'] = 'BE1.1'

    def initialize_code(self):
        self.parameters = self.uclchem.advanced.GeneralSettings()
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

    def synchronize_model(self):
        return 0

    def get_state(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ):
        return 0

    def set_state(
        self,
        index_of_the_particle,
        number_density,
        temperature,
        ionrate,
        radfield
    ):
        return 0



class UclchemInterface(PythonCodeInterface):
    def __init__(self, **options):
        PythonCodeInterface.__init__(
            self,
            UclchemImplementation,
            'uclchem_worker',
            **options
        )


class Uclchem:
    pass
