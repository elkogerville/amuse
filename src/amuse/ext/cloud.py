import warnings
from amuse.ic.cloud import (
    fill_grid_with_cloud_and_medium,
    fill_grid_with_spherical_cloud,
    fill_grid_with_cloud_shock
)

warnings.warn(
    'amuse.ext.cloud is deprecated and will be removed in the future. '
    'Import from amuse.ic.cloud instead: '
    '"from amuse.ic.cloud import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
