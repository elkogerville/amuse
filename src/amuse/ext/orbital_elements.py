import warnings
from amuse.ic.orbital_elements import (
    center_of_mass_array,
    derive_G,
    equal_length_array_or_scalar,
    generate_binaries,
    get_orbital_elements_from_arrays,
    get_orbital_elements_from_binaries,
    get_orbital_elements_from_binary,
    new_binary_from_orbital_elements,
    newton,
    normalize_vector,
    orbital_elements,
    orbital_elements_for_rel_posvel_arrays,
    orbital_elements_from_binary,
    orbital_period_to_semimajor_axis,
    rel_posvel_arrays_from_orbital_elements,
    semimajor_axis_to_orbital_period,
    true_anomaly_from_eccentric_anomaly,
)

warnings.warn(
    'amuse.ext.orbital_elements is deprecated and will be removed in the future. '
    'Import from amuse.ic.orbital_elements instead: '
    '"from amuse.ic.orbital_elements import ..."',
    category=DeprecationWarning,
    stacklevel=2
)
