from amuse.community.arepo.interface import ArepoInterface, Arepo
from amuse.ic.molecular_cloud import new_molecular_cloud
from amuse.support.testing.amusetest import TestWithMPI
from amuse.units import nbody_system, units


class TestArepo(TestWithMPI):

    def test1(self):
        instance = ArepoInterface()
        assert instance is not None

        converter = nbody_system.nbody_to_si(1000.0 | units.MSun, 2.0 | units.RSun)
        instance.parameters.periodic_box_size = 10 | nbody_system.length

        cloud = new_molecular_cloud(targetN=20000)
        cloud.x += (0.5 * instance.parameters.periodic_box_size)
        cloud.y += (0.5 * instance.parameters.periodic_box_size)
        cloud.z += (0.5 * instance.parameters.periodic_box_size)
        instance.gas_particles.add_particles(cloud)

        instance.cleanup_code()
        instance.stop()
