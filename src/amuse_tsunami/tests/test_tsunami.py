from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import tsunami

from amuse.datamodel import Particle, Particles
from amuse.ext.orbital_elements import generate_binaries
from amuse.support.testing.amusetest import TestWithMPI
from amuse_tsunami.interface import TsunamiInterface, Tsunami
from amuse.units import constants as c, nbody_system as ns, units as u

# if True, show comparison plots for certain tests
show_plots = False

class TestTsunamiInterface(TestWithMPI):

    def test_initialization(self):
        """
        Test Tsunami initialization.
        """
        instance = self.new_instance_of_an_optional_code(TsunamiInterface)
        assert instance is not None

        self.assertEquals(0, instance.initialize_code())
        self.assertEquals(0, instance.commit_parameters())
        self.assertEquals(0, instance.cleanup_code())
        instance.stop()

    def test_setters_and_getters(self):
        """
        Test TsunamiInterface setters and getters.
        """
        instance = self.new_instance_of_an_optional_code(TsunamiInterface)
        assert instance is not None

        self.assertEquals(0, instance.initialize_code())

        instance.set_units(2, 2)
        self.assertEquals(instance.get_Mscale()['Mscale'], 2)
        self.assertEquals(instance.get_Lscale()['Lscale'], 2)
        self.assertAlmostRelativeEquals(
            instance.get_Vscale()['Vscale'], 29.78469182967693
        )
        self.assertAlmostRelativeEquals(
            instance.get_Tscale()['Tscale'], 0.31831589802181726
        )
        self.assertAlmostRelativeEquals(
            instance.get_speed_of_light()['speed_of_light'],
            10065.320121972596
        )

        instance.set_equilibrium_tides(True)
        self.assertEquals(
            instance.get_equilibrium_tides()['equilibrium_tides'],
            True
        )

        instance.set_dynamical_tides(True)
        self.assertEquals(
            instance.get_dynamical_tides()['dynamical_tides'],
            True
        )

        instance.set_alpha(2)
        self.assertEquals(instance.get_alpha()['alpha'], 2)
        instance.set_beta(2)
        self.assertEquals(instance.get_beta()['beta'], 2)
        instance.set_gamma(2)
        self.assertEquals(instance.get_gamma()['gamma'], 2)

        instance.set_pn(True)
        self.assertEquals(instance.get_pn()['pn'], True)
        instance.set_pn1(True)
        self.assertEquals(instance.get_pn1()['pn1'], True)
        instance.set_pn2(True)
        self.assertEquals(instance.get_pn2()['pn2'], True)
        instance.set_pn25(True)
        self.assertEquals(instance.get_pn25()['pn25'], True)
        instance.set_pn3(True)
        self.assertEquals(instance.get_pn3()['pn3'], True)
        instance.set_pn35(True)
        self.assertEquals(instance.get_pn35()['pn35'], True)

        instance.set_units(1, 1)

        self.assertEquals(0, instance.commit_parameters())

        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 0)

        result = instance.new_particle(3,0,1,3,0,0,0,0,0,0,0)
        self.assertEquals(result['index_of_the_particle'], 0)

        result = instance.new_particle(4,0,-2,-1,0,0,0,0,1,1,1)
        self.assertEquals(result['index_of_the_particle'], 1)

        result = instance.new_particle(5,0,1,-1,0,0,0,0,0,0,0)
        self.assertEquals(result['index_of_the_particle'], 2)

        instance.commit_particles()
        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 3)

        result = instance.get_state(0)
        self.assertEquals(result['mass'], 3.0)
        self.assertEquals(result['radius'], 0.0)
        self.assertEquals(result['x'], 1.0)
        self.assertEquals(result['y'], 3.0)
        self.assertEquals(result['z'], 0.0)
        self.assertEquals(result['vx'], 0.0)
        self.assertEquals(result['vy'], 0.0)
        self.assertEquals(result['vz'], 0.0)
        self.assertEquals(result['wx'], 0.0)
        self.assertEquals(result['wy'], 0.0)
        self.assertEquals(result['wz'], 0.0)

        result = instance.get_state(1)
        self.assertEquals(result['mass'], 4)
        self.assertEquals(result['radius'], 0)
        self.assertEquals(result['x'], -2)
        self.assertEquals(result['y'], -1)
        self.assertEquals(result['z'], 0)
        self.assertEquals(result['vx'], 0)
        self.assertEquals(result['vy'], 0)
        self.assertEquals(result['vz'], 0)
        self.assertEquals(result['wx'], 1)
        self.assertEquals(result['wy'], 1)
        self.assertEquals(result['wz'], 1)

        result = instance.get_state(2)
        self.assertEquals(result['mass'], 5)
        self.assertEquals(result['radius'], 0)
        self.assertEquals(result['x'], 1)
        self.assertEquals(result['y'], -1)
        self.assertEquals(result['z'], 0)
        self.assertEquals(result['vx'], 0)
        self.assertEquals(result['vy'], 0)
        self.assertEquals(result['vz'], 0)
        self.assertEquals(result['wx'], 0)
        self.assertEquals(result['wy'], 0)
        self.assertEquals(result['wz'], 0)

        instance.set_mass(0, 1.5)
        self.assertEquals(instance.get_mass(0)['mass'], 1.5)

        self.assertEquals(instance.get_radius(0)['radius'], 0.0)

        instance.set_position(0, 2.5, 3.5, 4.5)
        result = instance.get_position(0)
        self.assertEquals(result['x'], 2.5)
        self.assertEquals(result['y'], 3.5)
        self.assertEquals(result['z'], 4.5)

        instance.set_velocity(0, 5.5, 6.5, 7.5)
        result = instance.get_velocity(0)
        self.assertEquals(result['vx'], 5.5)
        self.assertEquals(result['vy'], 6.5)
        self.assertEquals(result['vz'], 7.5)

        result = instance.get_spin(1)
        self.assertEquals(result['wx'], 1)
        self.assertEquals(result['wy'], 1)
        self.assertEquals(result['wz'], 1)

        instance.delete_particle(0)
        instance.recommit_particles()
        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 2)

        result = instance.get_state(1)
        self.assertEquals(result['mass'], 4)
        self.assertEquals(result['radius'], 0)
        self.assertEquals(result['x'], -2)
        self.assertEquals(result['y'], -1)
        self.assertEquals(result['z'], 0)
        self.assertEquals(result['vx'], 0)
        self.assertEquals(result['vy'], 0)
        self.assertEquals(result['vz'], 0)
        self.assertEquals(result['wx'], 1)
        self.assertEquals(result['wy'], 1)
        self.assertEquals(result['wz'], 1)

        result = instance.get_state(2)
        self.assertEquals(result['mass'], 5)
        self.assertEquals(result['radius'], 0)
        self.assertEquals(result['x'], 1)
        self.assertEquals(result['y'], -1)
        self.assertEquals(result['z'], 0)
        self.assertEquals(result['vx'], 0)
        self.assertEquals(result['vy'], 0)
        self.assertEquals(result['vz'], 0)
        self.assertEquals(result['wx'], 0)
        self.assertEquals(result['wy'], 0)
        self.assertEquals(result['wz'], 0)

        instance.set_state(
            1,
            5, 5,
            5, 5, 5,
            5, 5, 5,
            5, 5, 5
        )
        result = instance.get_state(1)
        self.assertEquals(result['mass'], 5)
        self.assertEquals(result['x'], 5)
        self.assertEquals(result['y'], 5)
        self.assertEquals(result['z'], 5)
        self.assertEquals(result['vx'], 5)
        self.assertEquals(result['vy'], 5)
        self.assertEquals(result['vz'], 5)

        # check that this is still the same
        result = instance.get_state(2)
        self.assertEquals(result['mass'], 5)
        self.assertEquals(result['radius'], 0)
        self.assertEquals(result['x'], 1)
        self.assertEquals(result['y'], -1)
        self.assertEquals(result['z'], 0)
        self.assertEquals(result['vx'], 0)
        self.assertEquals(result['vy'], 0)
        self.assertEquals(result['vz'], 0)
        self.assertEquals(result['wx'], 0)
        self.assertEquals(result['wy'], 0)
        self.assertEquals(result['wz'], 0)

        self.assertEquals(0, instance.cleanup_code())
        instance.stop()


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

    def validate_tsunami_state_equality(self, state: list, particle: Particle) -> None:
        """
        Validate that a state retrieved by `Tsunami.get_state`
        matches the state of `particle` exactly.

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


    def validate_tsunami_state_relative_equality(
        self,
        state: list,
        particle: Particle,
        places: int = 7
    ) -> None:
        """
        Validate that a state retrieved via `Tsunami.get_state` matches
        the corresponding attributes of `particle`, within relative tolerance.

        Parameters
        ----------
        state : list
            State vector as returned by `get_state`, ordered as
            [mass, radius, x, y, z, vx, vy, vz, wx, wy, wz].
        particle : amuse.datamodel.particles.Particle
            Particle instance whose attributes are compared against `state`.
        places : int, optional, default=7
            Number of decimal places of relative precision required for equality.

        Raises
        ------
        AssertionError
            If any corresponding value in `state` and `particle` does not match
            within `places` relative precision.

        """
        self.assertAlmostRelativeEquals(state[0], particle.mass, places=places)
        self.assertAlmostRelativeEquals(state[1], particle.radius, places=places)
        self.assertAlmostRelativeEquals(state[2], particle.x, places=places)
        self.assertAlmostRelativeEquals(state[3], particle.y, places=places)
        self.assertAlmostRelativeEquals(state[4], particle.z, places=places)
        self.assertAlmostRelativeEquals(state[5], particle.vx, places=places)
        self.assertAlmostRelativeEquals(state[6], particle.vy, places=places)
        self.assertAlmostRelativeEquals(state[7], particle.vz, places=places)
        self.assertAlmostRelativeEquals(state[8], particle.wx, places=places)
        self.assertAlmostRelativeEquals(state[9], particle.wy, places=places)
        self.assertAlmostRelativeEquals(state[10], particle.wz, places=places)

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

        self.validate_tsunami_state_equality(state0, system[0])
        self.validate_tsunami_state_equality(state1, system[1])
        self.validate_tsunami_state_equality(state2, system[2])

        self.assertEquals(system[0].key, instance.particles[0].key)
        self.assertEquals(system[1].key, instance.particles[1].key)
        self.assertEquals(system[2].key, instance.particles[2].key)

        instance.particles.remove_particle(system[0])
        self.assertEquals(instance.get_number_of_particles(), len(system)-1)

        state1 = instance.get_state(1)
        state2 = instance.get_state(2)

        self.validate_tsunami_state_equality(state1, system[1])
        self.validate_tsunami_state_equality(state2, system[2])

        instance.stop()

    def test_tsunami_pythagorean_triple(self):
        """
        Test identical to `test_tsunami.py` from the TSUNAMI package.
        Simulation results should be identical to standalone TSUNAMI.
        """
        system = self.generate_pythagorean()

        instance = self.new_instance_of_an_optional_code(Tsunami, redirection='none')
        assert instance is not None

        instance.parameters.wPNs = False
        instance.parameters.wEqTides = False
        instance.parameters.wDynTides = False
        instance.commit_parameters()

        instance.particles.add_particles(system)
        instance.commit_particles()

        t_end = 65 | ns.time
        dt = 0.1 | ns.time
        while instance.model_time <  t_end:
            instance.evolve_model(instance.model_time + dt)

        # validate energies
        self.assertAlmostRelativeEquals(instance.potential_energy.number, 22.461771188652676)
        self.assertAlmostRelativeEquals(instance.kinetic_energy.number, 9.645104521979146)
        self.assertAlmostRelativeEquals(instance.deltaE, 3.055333763768898e-13)

        self.assertAlmostRelativeEquals(instance.model_time, t_end, places=2)
        state0 = instance.get_state(0)
        state1 = instance.get_state(1)
        state2 = instance.get_state(2)

        # compare with standalone TSUNAMI simulation results
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

    def test_delete_particle_and_restart(self):
        """
        This test simulates a pythagorean triangle system
        identical to `test_tsunami_pythagorean_triangle`,
        but instead of evolving to time t=65, it first evolves
        to time t=30, then deletes a particle, then adds it back
        in before finishing the integration to t=65.
        Both this test and `test_tsunami_pythagorean_triangle`
        should agree. Due to integration differences, the results
        of the two different simulations differ by more than 1 decimal
        point, and the states are not compared in this test.
        Set `show_plots=True` at the top of the test file to show the
        comparison plot.
        """
        system = self.generate_pythagorean()

        instance = self.new_instance_of_an_optional_code(Tsunami, redirection='none')
        assert instance is not None

        instance.parameters.wPNs = False
        instance.parameters.wEqTides = False
        instance.parameters.wDynTides = False
        instance.commit_parameters()

        instance.particles.add_particles(system)
        channel = instance.particles.new_channel_to(system)
        instance.commit_particles()

        particles = []

        t_midpoint = 30 | ns.time
        dt = 0.1 | ns.time
        while instance.model_time <  t_midpoint:
            instance.evolve_model(instance.model_time + dt)
            channel.copy()
            particles.append(system.copy())

        self.assertAlmostRelativeEquals(instance.model_time, t_midpoint, places=2)

        # save original state after evolving to t=30
        pars = instance.particles.copy()

        # remove particle 0
        instance.particles.remove_particle(instance.particles[0])
        self.assertEquals(instance.get_number_of_particles(), 2)

        # add 'particle 0' back in
        instance.particles.add_particle(pars[0])
        instance.recommit_particles()
        self.assertEquals(instance.get_number_of_particles(), 3)

        # check that new starting state is the same as t=30 state before deleting
        # particle 0 now has id=3 because ids are unique and increasing monotonically
        state0 = instance.get_state(3)
        state1 = instance.get_state(1)
        state2 = instance.get_state(2)
        self.validate_tsunami_state_relative_equality(state0, pars[0], places=10)
        self.validate_tsunami_state_relative_equality(state1, pars[1], places=10)
        self.validate_tsunami_state_relative_equality(state2, pars[2], places=10)

        t_end = 65 | ns.time
        dt = 0.1 | ns.time
        while instance.model_time <  t_end:
            instance.evolve_model(instance.model_time + dt)
            channel.copy()
            particles.append(system.copy())

        self.assertAlmostRelativeEquals(instance.model_time, t_end, places=2)

        if show_plots:
            colors = ['#483d8b', '#d81b60', '#dbb0ff']
            ax = self.plot_particles_xy(
                particles, colors=colors, labels=['star1', 'star2', 'star3']
            )
            self.plot_tsunami_pythagorean_triangle(ax)
            ax.legend(edgecolor='w')
            plt.show()

        instance.stop()

    def test_tsunami_does_not_rescale_to_com_frame(self):
        """
        By default Tsunami will rescale a system to its center
        of mass frame. Test that this behavior is turned off.
        """
        p = Particles(3)
        p.mass = [1,4,8] | ns.mass
        p.radius = [1,1,2] | ns.length
        p.position = [[0,1,2],[3,4,5],[6,7,8]] | ns.length
        p.velocity = [[6,7,8],[9,10,11],[12,13,14]] | ns.speed
        p.wx = [12,15,19] | 1 / ns.time
        p.wy = [13,16,20] | 1 / ns.time
        p.wz = [14,17,21] | 1 / ns.time

        instance = self.new_instance_of_an_optional_code(Tsunami, redirection='none')
        instance.particles.add_particles(p)
        instance.commit_particles()

        state0 = instance.get_state(0)
        state1 = instance.get_state(1)
        state2 = instance.get_state(2)

        self.validate_tsunami_state_equality(state0, p[0])
        self.validate_tsunami_state_equality(state1, p[1])
        self.validate_tsunami_state_equality(state2, p[2])

        instance.delete_particle(1)

        state0 = instance.get_state(0)
        state2 = instance.get_state(2)
        self.validate_tsunami_state_relative_equality(state0, p[0])
        self.validate_tsunami_state_relative_equality(state2, p[2])

        instance.stop()


    def test_pns(self):
        def setup_binary(a=0.1, e=0.99, m1=50.0, m2=50.0, nu=0.0, pn1=True, pn2=True):
            i = ome = Ome = 0.0 # rad
            pos_vel2 = np.array([0.,0.,0., 0.,0.,0.])

            print("\nGenerating binary")

            print("kepl_to_cart corrections:\n  PN1 = {}\n  PN2 = {}".format(pn1, pn2))

            pos_vel1 = keplutils.kepl_to_cart(pos_vel2, m1, m2, a, e, i, ome, Ome, nu, pn1=pn1, pn2=pn2)

            m = np.array([m1, m2])
            p = np.array([pos_vel1[:3], pos_vel2[:3]])
            v = np.array([pos_vel1[3:], pos_vel2[3:]])

            return m, p, v
        keplutils = tsunami.KeplerUtils()
        instance = self.new_instance_of_an_optional_code(Tsunami, redirection='none')
        assert instance is not None

        instance.parameters.wPNs = True


    def plot_particles_xy(
        self,
        particles: list[Particles],
        colors: list[str],
        labels: list[str] | None = None,
        figsize: tuple[float, float] = (6,6)
    ) -> Axes:
        """
        Plot the xy position of a list of `Particles`.

        Parameters
        ----------
        particles : list[Particles]
            List of `amuse.datamodel.particles.Particles`, where each `Particles`
            in the list is a simulation snapshot containing each `Particle` in the system.
        colors : list[ColorType]
            List of colors for each particle. Should have same length as the number of particles
            in the system.
        labels : list[str]
            Label for each particle. Should have same length as the number of particles
            in the system.
        figsize : tuple[float, float]
            Size of the figure.
        """
        data = [[], [], []]

        for p in particles:
            for i in range(len(p)):
                data[i].append((p[i].x.number, p[i].y.number))

        fig = plt.figure(figsize=figsize, tight_layout=True)
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        ax.minorticks_on()
        ax.tick_params(
            axis='both', length=2, direction='in',
            which='both', right=True, top=True
        )

        for i, (color, pts) in enumerate(zip(colors, data)):
            xs, ys = zip(*pts)
            l = None if labels is None else labels[i]
            ax.plot(xs, ys, color=color, linewidth=0.8, label=l)

        ax.set_xlabel('x')
        ax.set_ylabel('y')

        return ax

    def plot_tsunami_pythagorean_triangle(self, ax: Axes) -> None:
        """
        Plot `test_tsunami.py` from the standalone TSUNAMI package.
        """
        import tsunami
        code = tsunami.Tsunami(1.0, 1.0)

        code.Conf.wPNs = False
        code.Conf.wEqTides = False
        code.Conf.wDynTides = False
        code.Conf.wExt = False

        code.Conf.dcoll = 0.0

        m = np.array([3., 4., 5.])
        p = np.array([[1.,3.,0.], [-2.,-1.,0.], [1.,-1.,0.]])
        v = np.array([[0.,0.,0.], [0.,0.,0.], [0.,0.,0.]])
        R = np.array([0., 0., 0.])
        sp = np.array([[0.,0.,0.], [0.,0.,0.], [0.,0.,0.]])
        st = np.array([-1, -1, -1])
        code.add_particle_set(p, v, m, R, st, sp)

        code.sync_internal_state(p, v, sp)
        totp = [p.copy()]

        dt = 0.1
        ft = 65

        time = 0
        while time < ft:
            time = time + dt

            code.evolve_system(time)
            time = code.time
            code.sync_internal_state(p, v, sp)

            totp.append(p.copy())

        totp = np.vstack(totp)
        code.sync_masses(m)
        code.sync_radii(R)

        colors = ['#26dcba', '#7d7ff3', '#cfe23c']

        ax.plot(totp[::3,0], totp[::3,1], lw=0.8, ls='--', color=colors[0], label='star1 tsunami')
        ax.plot(totp[1::3,0], totp[1::3,1], lw=0.8, ls='--', color=colors[1], label='star2 tsunami')
        ax.plot(totp[2::3,0], totp[2::3,1], lw=0.8, ls='--', color=colors[2], label='star3 tsunami')
