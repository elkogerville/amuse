
from amuse.datamodel import Particle, Particles
from amuse.support.testing.amusetest import TestWithMPI
from amuse.units import units as u
from amuse_uclchem.interface import UclchemInterface, Uclchem, habing

class TestUclchemInterface(TestWithMPI):

    def test_echo_int(self):
        instance = UclchemInterface()
        print(instance.current_time)

class TestUclchem(TestWithMPI):

    def generate_chem_particle(self):
        p = Particle()
        p.number_density = 1 | u.cm**-3
        p.temperature = 2 | u.K
        p.ionrate = 3 | u.s**-1
        p.radfield = 4 | habing

        return p

    def test_add_particle(self):

        p = self.generate_chem_particle()
        instance = self.new_instance_of_an_optional_code(Uclchem, redirection='none')
        assert instance is not None

        instance.commit_parameters()
        instance.particles.add_particle(p)

        instance.stop()
