import warnings
from amuse.ic.grid_to_sph import (
    Grid2SPH,
    convert_grid_to_SPH
)

warnings.warn(
    'amuse.ext.grid_to_sph is deprecated and will be removed in the future. '
    'Import from amuse.ic.grid_to_sph instead: '
    '"from amuse.ic.grid_to_sph import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
