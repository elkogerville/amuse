import warnings

from amuse.ic.solarsystem import (
    get_position,
    get_sun_and_planets,
    new_argument_parser,
    new_kepler,
    new_solar_system,
    new_solar_system_for_mercury,
    old_new_solar_system,
    solar_system_in_time
)

warnings.warn(
    'amuse.ext.solarsystem is deprecated and will be removed in the future. '
    'Import from amuse.ic.solarsystem instead: "from amuse.ic.solarsystem import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
