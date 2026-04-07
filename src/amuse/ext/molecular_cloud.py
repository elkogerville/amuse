import warnings
from amuse.ic.molecular_cloud import (
    constant_density_div_free_power_law_v_ism_cube,
    molecular_cloud,
    interpolate_trilinear,
    ism_cube,
    make_div_free,
    make_ifft_real,
    new_ism_cube,
    random_field
)

warnings.warn(
    'amuse.ext.molecular_cloud is deprecated and will be removed in the future. '
    'Import from amuse.ic.molecular_cloud instead: '
    '"from amuse.ic.molecular_cloud import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
