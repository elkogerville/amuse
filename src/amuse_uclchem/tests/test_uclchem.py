
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

    def generate_chem_particle(self):
        p = Particle()
        p.number_density = 1 | u.cm**-3
        p.temperature = 2 | u.K
        p.ionrate = 3 | u.s**-1
        p.radfield = 4 | habing

        return p

    def generate_chem_particles(self):
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

    def test_add_particle(self):

        p = self.generate_chem_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p)

        instance.stop()

    def test_add_particles(self):

        p = self.generate_chem_particles()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particles(p)

        instance.stop()
