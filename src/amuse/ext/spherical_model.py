import warnings

from amuse.ic.spherical_model import (
    EnclosedMassInterpolator,
    UniformSphericalDistribution,
    new_gas_plummer_distribution,
    new_plummer_distribution,
    new_plummer_spatial_distribution,
    new_spherical_particle_distribution,
    new_uniform_spherical_particle_distribution,
    random_direction,
    sample_from_velocity_distribution
)

warnings.warn(
    'amuse.ext.spherical_model is deprecated and will be removed in the future. '
    'Import from amuse.ic.spherical_model instead: "from amuse.ic.spherical_model import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
