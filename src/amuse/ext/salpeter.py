import warnings

from amuse.ic.salpeter import (
    new_salpeter_mass_distribution,
    new_salpeter_mass_distribution_nbody
)

warnings.warn(
    'amuse.ext.salpeter is deprecated and will be removed in the future. '
    'Import from amuse.ic.salpeter instead: "from amuse.ic.salpeter import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
