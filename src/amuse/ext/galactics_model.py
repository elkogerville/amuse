import warnings
from amuse.ic.galactics_model import (
    new_galactics_gas_model,
    new_galactics_model,
    new_gaslactics_model
)

warnings.warn(
    'amuse.ext.galactics_model is deprecated and will be removed in the future. '
    'Import from amuse.ic.galactics_model instead: '
    '"from amuse.ic.galactics_model import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
