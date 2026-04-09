import warnings
from amuse.ic.gasplummer import MakePlummerGasModel

warnings.warn(
    'amuse.ext.gasplummer is deprecated and will be removed in the future. '
    'Import from amuse.ic.gasplummer instead: '
    '"from amuse.ic.gasplummer import MakePlummerGasModel"',
    category=DeprecationWarning,
    stacklevel=2
)
