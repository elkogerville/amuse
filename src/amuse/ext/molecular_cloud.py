import warnings
from amuse.ic.molecular_cloud import *

warnings.warn(
    'amuse.ext.molecular_cloud is deprecated and will be removed in the future. '
    'Import from amuse.ic.molecular_cloud instead: '
    '"from amuse.ic.molecular_cloud import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
