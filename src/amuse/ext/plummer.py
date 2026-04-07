import warnings

from amuse.ic.plummer import (
    MakePlummerModel,
    new_plummer_model,
    new_plummer_sphere
)

warnings.warn(
    'amuse.ext.plummer is deprecated and will be removed in the future. '
    'Import from amuse.ic.plummer instead: "from amuse.ic.plummer import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
