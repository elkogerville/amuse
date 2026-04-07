import warnings
from amuse.ic.halogen_model import new_halogen_model

warnings.warn(
    'amuse.ext.halogen_model is deprecated and will be removed in the future. '
    'Import from amuse.ic.halogen_model instead: '
    '"from amuse.ic.halogen_model import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
