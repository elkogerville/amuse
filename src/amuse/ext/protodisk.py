import warnings
from amuse.ic.protodisk import (
    approximate_inverse_error_function,
    uniform_unit_cylinder,
    ProtoPlanetaryDisk
)

warnings.warn(
    'amuse.ext.protodisk is deprecated and will be removed in the future. '
    'Import from amuse.ic.protodisk: '
    '"from amuse.ic.protodisk import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
