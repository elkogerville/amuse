
from amuse.datamodel import Particle, Particles
from amuse.support.testing.amusetest import TestWithMPI
from amuse.units import units as u
from amuse_uclchem.interface import UclchemInterface, Uclchem, habing

class TestUclchemInterface(TestWithMPI):

    def test_getters_and_setters(self):
        instance = self.new_instance_of_an_optional_code(UclchemInterface, redirection='none')
        assert instance is not None

        instance.new_particle(1, 2, 3, 4)
        instance.new_particle(11, 12, 13, 14)

        result = instance.get_state(0)
        self.assertEquals(result['number_density'], 1)
        self.assertEquals(result['temperature'], 2)
        self.assertEquals(result['ionrate'], 3)
        self.assertEquals(result['radfield'], 4)

        instance.set_state(0, 5, 6, 7, 8)
        result = instance.get_state(0)
        self.assertEquals(result['number_density'], 5)
        self.assertEquals(result['temperature'], 6)
        self.assertEquals(result['ionrate'], 7)
        self.assertEquals(result['radfield'], 8)

        instance.set_number_density(0, 10)
        result = instance.get_number_density(0)
        self.assertEquals(result['number_density'], 10)

        instance.stop()

class TestUclchem(TestWithMPI):

    def generate_single_particle(self):
        p = Particle()
        p.number_density = 1 | u.cm**-3
        p.temperature = 2 | u.K
        p.ionrate = 3 | u.s**-1
        p.radfield = 4 | habing

        return p

    def generate_two_particles(self):
        p = Particles(2)
        p[0].number_density = 1 | u.cm**-3
        p[0].temperature = 2 | u.K
        p[0].ionrate = 3 | u.s**-1
        p[0].radfield = 4 | habing

        p[1].number_density = 5 | u.cm**-3
        p[1].temperature = 6 | u.K
        p[1].ionrate = 7 | u.s**-1
        p[1].radfield = 8 | habing

        return p

    def test_parameters(self):
        """Test parameters defined for Uclchem."""
        instance = self.new_instance_of_an_optional_code(Uclchem)
        assert instance is not None

        self.assertEquals(instance.parameters.chem_model, 'cloud')
        instance.parameters.chem_model = 'JSHOCK'
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

        instance.stop()

    def test_add_and_remove_particle(self):

        p = self.generate_single_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p)

        self.assertEquals(len(instance.particles), 1)

        instance.particles.remove_particle(instance.particles[0])
        # instance.delete_particle(0)
        self.assertEquals(len(instance.particles), 0)

        instance.stop()

    def test_add_and_delete_particle(self):
        """Test add and delete single particle from set"""
        p = self.generate_single_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p)

        self.assertEquals(len(instance.particles), 1)
        instance.delete_particle(0)

        print(instance.particles)

        instance.stop()

    def test_add_two_particles(self):
        """Test add and delete particles"""
        p = self.generate_two_particles()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p[0])
        instance.particles.add_particle(p[1])

        self.assertEquals(len(instance.particles), 2)
        instance.particles.remove_particle(instance.particles[0])
        # instance.delete_particle(0)
        # instance.particles

        print('printing state now', instance.get_state(0))

        print('len', len(instance.particles))
        print(instance.particles)

        instance.stop()
