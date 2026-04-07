import warnings
from amuse.ic.kingmodel import (
    MakeKingModel,
    new_king_model
)

warnings.warn(
    'amuse.ext.kingmodel is deprecated and will be removed in the future. '
    'Import from amuse.ic.kingmodel instead: '
    '"from amuse.ic.kingmodel import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
