import warnings
from amuse.ic.LagrangianRadii import (
    LagrangianRadii,
    distance_sq
)

warnings.warn(
    'amuse.ext.LagrangianRadii is deprecated and will be removed in the future. '
    'Import from amuse.ic.LagrangianRadii instead: '
    '"from amuse.ic.LagrangianRadii import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
