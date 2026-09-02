import matplotlib.pyplot as plt
import numpy as np
from uclchem.model import get_species_names as _get_species_names

from amuse.datamodel import Particle, Particles
from amuse.support.testing.amusetest import TestWithMPI
from amuse.units import units as u
from amuse_uclchem.interface import UclchemInterface, Uclchem, habing


class TestUclchemInterface(TestWithMPI):

    def test_getters_and_setters(self):
        instance = self.new_instance_of_an_optional_code(UclchemInterface)
        assert instance is not None

        instance.new_particle(1, 2, 3, 4)
        instance.new_particle(11, 12, 13, 14)

        result = instance.get_state(0)
        self.assertEquals(result['number_density'], 1)
        self.assertEquals(result['temperature'], 2)
        self.assertEquals(result['ionrate'], 3)
        self.assertEquals(result['radfield'], 4)

        result = instance.get_state(1)
        self.assertEquals(result['number_density'], 11)
        self.assertEquals(result['temperature'], 12)
        self.assertEquals(result['ionrate'], 13)
        self.assertEquals(result['radfield'], 14)

        instance.set_state(0, 5, 6, 7, 8)
        result = instance.get_state(0)
        self.assertEquals(result['number_density'], 5)
        self.assertEquals(result['temperature'], 6)
        self.assertEquals(result['ionrate'], 7)
        self.assertEquals(result['radfield'], 8)

        instance.set_number_density(0, 10)
        result = instance.get_number_density(0)
        self.assertEquals(result['number_density'], 10)

        instance.set_temperature(0, 20)
        result = instance.get_temperature(0)
        self.assertEquals(result['temperature'], 20)

        instance.set_ionrate(0, 30)
        result = instance.get_ionrate(0)
        self.assertEquals(result['ionrate'], 30)

        instance.set_radfield(0, 40)
        result = instance.get_radfield(0)
        self.assertEquals(result['radfield'], 40)

        instance.set_chemical_model('prestellarcore')
        result = instance.get_chemical_model()
        self.assertEquals(result['chem_model'], 'prestellarcore')

        H_index = _get_species_names().index('H')
        result = instance.get_species_name(H_index)
        self.assertEquals(result['name'], 'H')
        result = instance.get_species_index('H')
        self.assertEquals(result['abundance_index'], H_index)

        result = instance.get_time()
        self.assertEquals(result['time'], 0)

        instance.commit_particles()
        instance.set_abundance(0, 0, 5)

        result = instance.get_abundance(0, 0)
        self.assertEquals(result['abundance'], 5)

        instance.stop()

class TestUclchem(TestWithMPI):

    def generate_single_particle(self):
        p = Particle()
        p.number_density = 1e4 | u.cm**-3
        p.temperature = 10 | u.K
        p.ionrate = 1.3e-17 | u.s**-1
        p.radfield = 1 | habing

        return p

    def generate_two_particles(self):
        p = Particles(2)
        p[0].number_density = 1e4 | u.cm**-3
        p[0].temperature = 10 | u.K
        p[0].ionrate = 1.3e-17 | u.s**-1
        p[0].radfield = 1 | habing

        p[1].number_density = 1e5 | u.cm**-3
        p[1].temperature = 20 | u.K
        p[1].ionrate = 1.3e-17 | u.s**-1
        p[1].radfield = 1 | habing

        return p

    def _validate_particle_state(self, particle1, particle2):
        attributes = ['key', 'number_density', 'temperature', 'ionrate', 'radfield']
        for attr in attributes:
            self.assertEquals(getattr(particle1, attr), getattr(particle2, attr))

    def test_parameters(self):
        """Test parameters defined for Uclchem."""
        instance = self.new_instance_of_an_optional_code(Uclchem)
        assert instance is not None

        self.assertEquals(instance.parameters.chem_model, 'cloud')
        instance.parameters.chem_model = 'jshock'
        self.assertEquals(instance.parameters.chem_model, 'jshock')

        instance.stop

    def test_methods(self):
        """Test methods defined for Uclchem."""
        instance = self.new_instance_of_an_optional_code(Uclchem)
        assert instance is not None

        p = self.generate_two_particles()
        instance.particles.add_particles(p)

        new_state = [10 | u.cm**-3, 20 | u.K, 30 | u.s**-1, 40 | habing]
        instance.set_state(0, *new_state)
        self.assertEquals(instance.get_state(0), new_state)

        instance.set_number_density(1, 200 | u.cm**-3)
        self.assertEquals(instance.get_number_density(1), 200 | u.cm**-3)

        instance.set_temperature(1, 200 | u.K)
        self.assertEquals(instance.get_temperature(1), 200 | u.K)

        instance.set_ionrate(1, 200 | u.s**-1)
        self.assertEquals(instance.get_ionrate(1), 200 | u.s**-1)

        instance.set_radfield(1, 200 | habing)
        self.assertEquals(instance.get_radfield(1), 200 | habing)

        self.assertEquals(instance.get_number_of_particles(), 2)
        self.assertEquals(len(instance.particles), 2)

        instance.stop()

    def test_add_particle(self):
        """Test add single particle."""
        p = self.generate_single_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem)
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p)

        self.assertEquals(instance.get_number_of_particles(), 1)
        self._validate_particle_state(instance.particles, p)

        instance.evolve_model(1e3 | u.yr)
        self.assertAlmostEquals(instance.model_time, 1e3| u.yr)

        instance.evolve_model(2e3 | u.yr)
        self.assertAlmostEquals(instance.model_time, 2e3| u.yr)

        instance.stop()

    def test_add_particles(self):
        """Test add 2 particles."""
        p = self.generate_two_particles()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particles(p)
        instance.commit_particles()

        self.assertEquals(instance.get_number_of_particles(), 2)

        self._validate_particle_state(instance.particles, p)

        instance.stop()

    def test_add_and_remove_particle(self):
        """Add then delete a particle."""
        p = self.generate_single_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p)

        self.assertEquals(instance.get_number_of_particles(), 1)

        instance.particles.remove_particle(instance.particles[0])
        self.assertEquals(instance.get_number_of_particles(), 0)
        self.assertEquals(instance.particles.is_empty(), True)

        instance.stop()

    def test_add_and_remove_particles(self):
        """Test add and delete multiple particles."""
        p1 = self.generate_two_particles()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particles(p1)

        self._validate_particle_state(instance.particles[0], p1[0])
        self._validate_particle_state(instance.particles[1], p1[1])

        self.assertEquals(instance.get_number_of_particles(), 2)

        instance.particles.remove_particle(instance.particles[1])

        self.assertEquals(instance.get_number_of_particles(), 1)
        self._validate_particle_state(instance.particles[0], p1[0])

        p2 = self.generate_two_particles()
        instance.particles.add_particles(p2)

        self.assertEquals(instance.get_number_of_particles(), 3)

        instance.particles.remove_particles(instance.particles)
        self.assertEquals(instance.get_number_of_particles(), 0)
        self.assertEquals(instance.particles.is_empty(), True)

        instance.stop()

    def test_set_abundance(self):
        """Test setting a single chemical abundance for a particle."""
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        p = self.generate_two_particles()
        instance.particles.add_particles(p)
        instance.commit_particles()

        instance.set_abundance(0, 0, 5)
        assert instance.get_abundance(0, 0) == 5

        instance.set_abundance(1, 230, 0.45283)
        assert instance.get_abundance(1, 230) == 0.45283

        instance.stop()

    def test_set_abundances(self):
        """Test setting all abundances of a particle from an array."""
        instance = self.new_instance_of_an_optional_code(Uclchem)
        assert instance is not None

        p = self.generate_two_particles()
        instance.particles.add_particles(p)
        instance.commit_particles()

        abundances = np.random.rand(335)

        instance.set_abundances(0, abundances)
        assert np.all(instance.particles.abundances[0,:] == abundances)
        assert np.all(instance.particles.abundances[1,:] == np.zeros(335))

        instance.stop()

    def test_evolve_abundances(self):
        """
        Test evolving a cloud model and getting the abundances.
        The expected abundances are the default starting abundances
        in UCLCHEM.
        """
        p = self.generate_single_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem)
        assert instance is not None

        instance.set_chemical_model = 'cloud'
        instance.commit_parameters()

        instance.particles.add_particle(p)
        instance.commit_particles()

        instance.evolve_model(1e3 | u.yr)

        abundances = instance.get_abundances(0, 'H')
        self.assertAlmostEquals(abundances[0], 0.499372, places=5)

        abundances = instance.get_abundances(0, ['H', 'H2', 'H2O', 'CO', 'CH3OH'])
        expected = [0.499372, 0.250314, 3.540059e-10, 1.994706e-07, 2.242720e-14]
        for abund, exp in zip(abundances, expected):
            self.assertAlmostEquals(abund, exp, places=5)

        instance.stop()

    def test_evolve_model(self):
        """Test evolve model."""
        p = Particle()
        p.number_density = 10010.000467300415 | u.cm**-3
        p.temperature = 10.0 | u.K
        p.ionrate = 1.3e-17 | u.s**-1
        p.radfield = 1 | habing

        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.parameters.chem_model = 'cloud'
        instance.commit_parameters()

        instance.particles.add_particle(p)
        instance.commit_particles()

        instance.evolve_model(1e6 | u.yr)
        abund = instance.get_abundances(0, ['H', 'H2', 'H2O', 'CO', 'CH3OH'])

        expected_abundances = [
            0.000067, 0.499391, 2.694883e-7, 2.674191e-5, 3.488843e-7
        ]

        for a, ea in zip(abund, expected_abundances):
            self.assertAlmostEqual(a, ea)

        instance.stop()
