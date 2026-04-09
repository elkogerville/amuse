import warnings
from amuse.ic.evrard_test import (
    MakeEvrardTest,
    MakeEvrardModel,
    body_centered_grid_unit_cube,
    glass_unit_cube,
    new_evrard_gas_sphere,
    regular_grid_unit_cube,
    sobol_unit_cube,
    uniform_random_unit_cube,
    uniform_unit_cube,
    uniform_unit_sphere
)

warnings.warn(
    'amuse.ext.evrard_test is deprecated and will be removed in the future. '
    'Import from amuse.ic.evrard_test instead: '
    '"from amuse.ic.evrard_test import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
