from amuse.datamodel import Particle, Particles
from amuse.ext.orbital_elements import generate_binaries
from amuse.support.testing.amusetest import TestWithMPI
from amuse_tsunami.interface import TsunamiInterface, Tsunami
from amuse.units import constants as c, nbody_system as ns, units as u

# class TestTsunamiInterface(TestWithMPI):

#     def test_echo_int(self):
#         instance = TsunamiInterface()

#         instance.stop()


class TestTsunami(TestWithMPI):
    def generate_HD80606b_system(self):
        """
        Initial conditions for the exoplanet system
        HD80606b. Initial conditions courtesy of
        Dr. Tjarda Boekholt.
        """
        HD80606 = Particles(2)
        star, planet = generate_binaries(
            primary_mass=2.0088092e30 | u.kg,
            secondary_mass=7.7459434e27 | u.kg,
            semi_major_axis=0.455 | u.au,
            eccentricity=0.9330
        )
        HD80606[0].name = 'HD80606'
        HD80606[0].mass = star.mass
        HD80606[0].radius = 702455.0 | u.km
        HD80606[0].x = star.x.as_quantity_in(u.km)
        HD80606[0].y = star.y.as_quantity_in(u.km)
        HD80606[0].z = star.z.as_quantity_in(u.km)
        HD80606[0].vx = star.vx.as_quantity_in(u.kms)
        HD80606[0].vy = star.vy.as_quantity_in(u.kms)
        HD80606[0].vz = star.vz.as_quantity_in(u.kms)
        HD80606[0].wx = 0.0 | 1 / u.s
        HD80606[0].wy = 0.0 | 1 / u.s
        HD80606[0].wz = 2.97188607137e-6 | 1 / u.s

        HD80606[1].name = 'HD80606b'
        HD80606[1].mass = planet.mass
        HD80606[1].radius = 68488.3446 | u.km
        HD80606[1].x = planet.x.as_quantity_in(u.km)
        HD80606[1].y = planet.y.as_quantity_in(u.km)
        HD80606[1].z = planet.z.as_quantity_in(u.km)
        HD80606[1].vx = planet.vx.as_quantity_in(u.kms)
        HD80606[1].vy = planet.vy.as_quantity_in(u.kms)
        HD80606[1].vz = planet.vz.as_quantity_in(u.kms)
        HD80606[1].wx = 0.0 | 1 / u.s
        HD80606[1].wy = 0.0 | 1 / u.s
        HD80606[1].wz = 0.000145444104333 | 1 / u.s

        return HD80606

    def generate_pythagorean(self):
        """Generate 3 particles in a pythagorean triangle configuration."""
        p = Particles(3)

        p[0].mass = 3 | ns.mass
        p[0].radius = 0 | ns.length
        p[0].x = 1 | ns.length
        p[0].y = 3 | ns.length
        p[0].z = 0 | ns.length
        p[0].vx = 0 | ns.speed
        p[0].vy = 0 | ns.speed
        p[0].vz = 0 | ns.speed
        p[0].wx = 0 | 1 / ns.time
        p[0].wy = 0 | 1 / ns.time
        p[0].wz = 0 | 1 / ns.time

        p[1].mass = 4 | ns.mass
        p[1].radius = 0 | ns.length
        p[1].x = -2 | ns.length
        p[1].y = -1 | ns.length
        p[1].z = 0 | ns.length
        p[1].vx = 0 | ns.speed
        p[1].vy = 0 | ns.speed
        p[1].vz = 0 | ns.speed
        p[1].wx = 0 | 1 / ns.time
        p[1].wy = 0 | 1 / ns.time
        p[1].wz = 0 | 1 / ns.time

        p[2].mass = 5 | ns.mass
        p[2].radius = 0 | ns.length
        p[2].x = 1 | ns.length
        p[2].y = -1 | ns.length
        p[2].z = 0 | ns.length
        p[2].vx = 0 | ns.speed
        p[2].vy = 0 | ns.speed
        p[2].vz = 0 | ns.speed
        p[2].wx = 0 | 1 / ns.time
        p[2].wy = 0 | 1 / ns.time
        p[2].wz = 0 | 1 / ns.time

        return p

    def validate_tsunami_state(self, state, particle) -> None:
        """
        Validate that a state retrieved by `Tsunami.get_state`
        matches the state of `particle`.

        Parameters
        ----------
        state : list
            List containing the state of the particle,
            as returned by `get_state`.
        particle : amuse.datamodel.particles.particle
            Particle to validate against `state`.

        Raises
        ------
        AssertionError : If the states don't match.
        """
        self.assertEquals(state[0], particle.mass)
        self.assertEquals(state[1], particle.radius)
        self.assertEquals(state[2], particle.x)
        self.assertEquals(state[3], particle.y)
        self.assertEquals(state[4], particle.z)
        self.assertEquals(state[5], particle.vx)
        self.assertEquals(state[6], particle.vy)
        self.assertEquals(state[7], particle.vz)
        self.assertEquals(state[8], particle.wx)
        self.assertEquals(state[9], particle.wy)
        self.assertEquals(state[10], particle.wz)

    def test_add_and_delete_particles(self):
        """Test adding and deleting particles in Tsunami."""
        system = self.generate_pythagorean()

        instance = self.new_instance_of_an_optional_code(Tsunami)
        assert instance is not None

        instance.particles.add_particles(system)
        instance.commit_particles()

        self.assertEquals(instance.get_number_of_particles(), len(system))

        state0 = instance.get_state(0)
        state1 = instance.get_state(1)
        state2 = instance.get_state(2)

        self.validate_tsunami_state(state0, system[0])
        self.validate_tsunami_state(state1, system[1])
        self.validate_tsunami_state(state2, system[2])

        self.assertEquals(system[0].key, instance.particles[0].key)
        self.assertEquals(system[1].key, instance.particles[1].key)
        self.assertEquals(system[2].key, instance.particles[2].key)

        instance.particles.remove_particle(system[0])
        self.assertEquals(instance.get_number_of_particles(), len(system)-1)

        instance.stop()

    def test_tsunami_pythagorean_triple(self):
        system = self.generate_pythagorean()

        instance = Tsunami(redirection='none')
        assert instance is not None

        instance.parameters.pn = False
        instance.commit_parameters()

        instance.particles.add_particles(system)
        instance.commit_particles()

        t_end = 65 | ns.time
        dt = 0.1 | ns.time
        while instance.model_time <  t_end:
            instance.evolve_model(instance.model_time + dt)

        state0 = instance.get_state(0)
        state1 = instance.get_state(1)
        state2 = instance.get_state(2)

        self.assertEquals(state0[0], 3 | ns.mass)
        self.assertEquals(state0[1], 0 | ns.length)
        self.assertAlmostRelativeEquals(state0[2], 4.15498855 | ns.length, places=7)
        self.assertAlmostRelativeEquals(state0[3], 12.01338805 | ns.length, places=7)
        self.assertEquals(state0[4], 0 | ns.length)
        self.assertAlmostRelativeEquals(state0[5], 0.59219296 | ns.speed, places=7)
        self.assertAlmostRelativeEquals(state0[6], 1.75695995 | ns.speed, places=7)
        self.assertEquals(state0[7], 0 | ns.speed)
        self.assertEquals(state0[8], 0 | 1 / ns.time)
        self.assertEquals(state0[9], 0 | 1 / ns.time)
        self.assertEquals(state0[10], 0 | 1 / ns.time)

        self.assertEquals(state1[0], 4 | ns.mass)
        self.assertEquals(state1[1], 0 | ns.length)
        self.assertAlmostRelativeEquals(state1[2], -0.86025151 | ns.length, places=7)
        self.assertAlmostRelativeEquals(state1[3], -4.09450317 | ns.length, places=7)
        self.assertEquals(state1[4], 0 | ns.length)
        self.assertAlmostRelativeEquals(state1[5], 0.61291976 | ns.speed, places=7)
        self.assertAlmostRelativeEquals(state1[6], -0.92151518 | ns.speed, places=7)
        self.assertEquals(state1[7], 0 | ns.speed)
        self.assertEquals(state1[8], 0 | 1 / ns.time)
        self.assertEquals(state1[9], 0 | 1 / ns.time)
        self.assertEquals(state1[10], 0 | 1 / ns.time)

        self.assertEquals(state2[0], 5 | ns.mass)
        self.assertEquals(state2[1], 0 | ns.length)
        self.assertAlmostRelativeEquals(state2[2], -1.80479192 | ns.length, places=7)
        self.assertAlmostRelativeEquals(state2[3], -3.9324303 | ns.length, places=7)
        self.assertEquals(state2[4], 0 | ns.length)
        self.assertAlmostRelativeEquals(state2[5], -0.84565158 | ns.speed, places=7)
        self.assertAlmostRelativeEquals(state2[6], -0.31696382 | ns.speed, places=7)
        self.assertEquals(state2[7], 0 | ns.speed)
        self.assertEquals(state2[8], 0 | 1 / ns.time)
        self.assertEquals(state2[9], 0 | 1 / ns.time)
        self.assertEquals(state2[10], 0 | 1 / ns.time)

        instance.stop()
