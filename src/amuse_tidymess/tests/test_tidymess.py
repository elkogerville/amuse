import numpy as np
import matplotlib.pyplot as plt

from amuse.support.testing.amusetest import TestWithMPI
from amuse_tidymess.interface import Tidymess, TidymessInterface
from amuse.units import units as u
from amuse.units import constants as c
from amuse.units import nbody_system
from amuse.datamodel import Particles
from amuse.ext.orbital_elements import generate_binaries, new_binary_from_orbital_elements


class TestTidymessInterface(TestWithMPI):

    def test1(self):
        """
        Test Tidymess initialization.
        """

        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test2(self):
        """
        Test TidymessInterface setters and getters.
        """

        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        assert instance is not None
        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 0)

        result = instance.new_particle(
            1.0,   # mass
            2.0,   # x
            3.0,   # y
            4.0,   # z
            5.0,   # vz
            6.0,   # vy
            7.0,   # vz
            8.0,   # radius
            9.0,   # xi
            10.0,  # kf
            11.0,  # tau
            12.0,  # wx
            13.0,  # wy
            14.0,  # wz
            15.0   # a_mb
        )
        self.assertEquals(result['index_of_the_particle'], 0.0)

        result = instance.get_state(0)
        self.assertEquals(result['mass'], 1.0)
        self.assertEquals(result['x'], 2.0)
        self.assertEquals(result['y'], 3.0)
        self.assertEquals(result['z'], 4.0)
        self.assertEquals(result['vx'], 5.0)
        self.assertEquals(result['vy'], 6.0)
        self.assertEquals(result['vz'], 7.0)
        self.assertEquals(result['radius'], 8.0)
        self.assertEquals(result['xi'], 9.0)
        self.assertEquals(result['kf'], 10.0)
        self.assertEquals(result['tau'], 11.0)
        self.assertEquals(result['wx'], 12.0)
        self.assertEquals(result['wy'], 13.0)
        self.assertEquals(result['wz'], 14.0)
        self.assertEquals(result['a_mb'], 15.0)

        instance.set_mass(0, 1.5)
        self.assertEquals(instance.get_mass(0)['mass'], 1.5)

        result = instance.get_position(0)
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

        instance.set_radius(0, 8.5)
        result = instance.get_radius(0)
        self.assertEquals(result['radius'], 8.5)

        instance.set_xi(0, 9.5)
        result = instance.get_xi(0)
        self.assertEquals(result['xi'], 9.5)

        instance.set_kf(0, 10.5)
        result = instance.get_kf(0)
        self.assertEquals(result['kf'], 10.5)

        instance.set_tau(0, 11.5)
        result = instance.get_tau(0)
        self.assertEquals(result['tau'], 11.5)

        instance.set_spin(0, 12.5, 13.5, 14.5)
        result = instance.get_spin(0)
        self.assertEquals(result['wx'], 12.5)
        self.assertEquals(result['wy'], 13.5)
        self.assertEquals(result['wz'], 14.5)

        instance.set_tidal_model(3)
        result = instance.get_tidal_model()
        self.assertEquals(result['tidal_model'], 3)

        instance.set_pn_order(2)
        result = instance.get_pn_order()
        self.assertEquals(result['pn_order'], 2)

        instance.set_magnetic_braking(1)
        result = instance.get_magnetic_braking()
        self.assertEquals(result['magnetic_braking'], 1)

        instance.set_speed_of_light(299792)
        result = instance.get_speed_of_light()
        self.assertEquals(result['speed_of_light'], 299792)

        instance.set_dt_mode(1)
        result = instance.get_dt_mode()
        self.assertEquals(result['dt_mode'], 1)

        instance.set_dt_const(0.025625)
        result = instance.get_dt_const()
        self.assertEquals(result['dt_const'], 0.025625)

        # result = instance.get_time_step()
        # self.assertEquals(result['time_step'], 0)

        instance.set_eta(0.625)
        result = instance.get_eta()
        self.assertEquals(result['eta'], 0.625)

        instance.set_n_iter(2)
        result = instance.get_n_iter()
        self.assertEquals(result['n_iter'], 2)

        instance.set_collision_mode(2)
        result = instance.get_collision_mode()
        self.assertEquals(result['collision_mode'], 2)

        instance.set_roche_mode(2)
        result = instance.get_roche_mode()
        self.assertEquals(result['roche_mode'], 2)

        instance.set_breakup_mode(1)
        result = instance.get_breakup_mode()
        self.assertEquals(result['breakup_mode'], 1)

        result = instance.get_num_integration_step() # FIXME
        self.assertEquals(result['num_integration_step'], 0)

        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test3(self):
        """
        Test TidymessInterface creating and deleting particles.
        """

        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        assert instance is not None
        result = instance.new_particle(
            1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0,
            1.0,  # radius
            1.0,  # xi
            1.0,  # kf
            1.0,  # tau
            1.0,  # wx
            1.0,  # wy
            1.0,  # wz
            1.0,  # a_mb
        )
        self.assertEqual(result['index_of_the_particle'], 0)

        result = instance.new_particle(
            1.1, 1.1, 1.1, 1.1,
            1.1, 1.1, 1.1,
            1.1,  # radius
            1.1,  # xi
            1.1,  # kf
            1.1,  # tau
            1.1,  # wx
            1.1,  # wy
            1.1,  # wz
            1.1,  # a_mb
        )
        self.assertEqual(result['index_of_the_particle'], 1)

        # check number of particles
        result = instance.get_number_of_particles()
        self.assertEqual(result['number_of_particles'], 2)

        # check that indexes are correct
        first = instance.get_index_of_first_particle()
        self.assertEqual(first['index_of_the_particle'], 0)

        next = instance.get_index_of_next_particle(
            first['index_of_the_particle']
        )
        self.assertEqual(next['index_of_the_next_particle'], 1)

        # delete particle
        instance.delete_particle(1)

        result = instance.get_number_of_particles()
        self.assertEqual(result['number_of_particles'], 1)

        first = instance.get_index_of_first_particle()
        self.assertEqual(first['index_of_the_particle'], 0)

        instance.stop()

    def test4(self):
        """
        Test TidymessInterface evolve_model with an equal mass binary.
        """
        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        assert instance is not None

        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        self.assertEqual([0, 0], list(instance.new_particle(0.5,  0.5, 0, 0,  0, 0.5, 0).values()))
        self.assertEqual([1, 0], list(instance.new_particle(0.5, -0.5, 0, 0,  0, -0.5, 0).values()))
        self.assertEqual(0, instance.commit_particles())

        self.assertEqual(0, instance.evolve_model(np.pi))  # half an orbit
        for result, expected in zip(instance.get_position(0).values(), [-0.5, 0.0, 0.0, 0]):
            self.assertAlmostEqual(result, expected, 5)

        self.assertEqual(0, instance.evolve_model(2 * np.pi))  # full orbit
        for result, expected in zip(instance.get_position(0).values(), [0.5, 0.0, 0.0, 0]):
            self.assertAlmostEqual(result, expected, 5)

        self.assertEqual(0, instance.cleanup_code())
        instance.stop()


class TestTidymess(TestWithMPI):

    def earth_moon_system(self):
        """
        Generate a Earth - moon system.

        Returns
        -------
        planet, moon : amuse.datamodel.particles.Particles
            Particle objects of the system.
        """
        system = Particles()

        planet, moon = generate_binaries(
            1 | u.MEarth,
            7.342e22 | u.kg,
            384399e3 | u.m,
            G=c.G
        )

        planet.radius = 6371. | u.km
        planet.xi = 0.3308
        planet.kf = 0.933
        planet.tau = 180 | u.s
        planet.wx = 0.0 | 1/u.yr
        planet.wy = 2.3e3 | 1/u.yr
        planet.wz = -4.7e6 | 1/u.yr
        moon.radius = 1737.4 | u.km
        moon.xi = 0.394
        moon.kf = 0
        moon.kf = 0
        moon.wx = 0.0 | 1/u.yr
        moon.wy = 8.4e1 | 1/u.yr
        moon.wz = 3.8e8 | 1/u.yr

        system.add_particles(planet)
        system.add_particles(moon)
        system.move_to_center()

        return system

    def jupiter_io_system(self):
        """
        Ephemeris Pasadena, USA, Horizons

        Jupiter and Io Ephemeris at A.D. 2026-Jan-01 00:00:00.0000

        Jupiter:
        kf from: Dong Lai 2021 Planet. Sci. J. 2 122 DOI 10.3847/PSJ/ac013b
        xi from: https://doi.org/10.1016/j.icarus.2011.09.016
        spin vector from: https://radiojove.gsfc.nasa.gov/education/jupiter/basics/jfacts.htm

        Io:
        kf from https://doi.org/10.1016/j.icarus.2025.116567
        xi from Schubert et al. 2004
        spin vector from https://doi.org/10.1016/j.icarus.2012.05.020 and ephemeris

        spin vectors were calculated from LOD, OBL, PSI using
        the ``Tidymess.convert_spin_vectors_to_inertial()`` method.

        tau values are arbitrary for both bodies.
        """
        system = Particles(2)

        system[0].name = 'Jupiter'
        system[0].mass = 1898.6e24 | u.kg
        system[0].radius = 6371.01 | u.km
        system[0].x = -2.538781102425539e8 | u.km
        system[0].y = 7.365225847926259e8 | u.km
        system[0].z = 2.626628058868796e6 | u.km
        system[0].vx = -1.250707427525374e1 | u.kms
        system[0].vy = -3.638417682823274 | u.kms
        system[0].vz = 2.949797151579847e-1 | u.kms
        system[0].kf = 0.565
        system[0].xi = 0.2629
        system[0].tau = 0 | u.s
        system[0].wx = 0.0 | 1 / u.s
        system[0].wy = -9.60092648806e-6 | 1 / u.s
        system[0].wz = 0.000175573560178 | 1 / u.s
        system[0].a_mb = 0

        system[1].name = 'Io'
        system[1].mass = 893193797311089e8 | u.kg
        system[1].radius = 1821.6 | u.km
        system[1].x = -2.535070263728397e8 | u.km
        system[1].y = 7.363212379813337e8 | u.km
        system[1].z = 2.624656018151939e6 | u.km
        system[1].vx = -4.195592326222561 | u.kms
        system[1].vy = 1.153726914561471e1 | u.kms
        system[1].vz = 9.564081722803852e-1 | u.kms
        system[1].kf = 0.125
        system[1].xi = 0.378
        system[1].tau = 0 | u.s
        system[1].wx = 0.0 | 1 / u.s
        system[1].wy = -1.43416864277e-9 | 1 / u.s
        system[1].wz = 4.10859051537e-5 | 1 / u.s
        system[1].a_mb = 0

        system.move_to_center()

        return system

    def test1(self):
        """
        Test Tidymess parameters attribute and their defaults
        """
        system = self.earth_moon_system()
        converter = nbody_system.nbody_to_si(
            system.mass.sum(), system[0].position.length()
        )
        instance = self.new_instance_of_an_optional_code(
            Tidymess, converter
        )
        assert instance is not None

        self.assertEquals(instance.parameters.tidal_model, 0)
        instance.parameters.tidal_model = 4
        self.assertEquals(instance.parameters.tidal_model, 4)

        self.assertEquals(instance.parameters.pn_order, 0)
        instance.parameters.pn_order = 1
        self.assertEquals(instance.parameters.pn_order, 1)

        self.assertEquals(instance.parameters.magnetic_braking, 0)
        instance.parameters.magnetic_braking = 1
        self.assertEquals(instance.parameters.magnetic_braking, 1)

        self.assertEquals(instance.parameters.speed_of_light, 1e100)
        instance.parameters.speed_of_light = 2e100
        self.assertEquals(instance.parameters.speed_of_light, 2e100)

        self.assertEquals(instance.parameters.dt_mode, 1)
        instance.parameters.dt_mode = 2
        self.assertEquals(instance.parameters.dt_mode, 2)

        self.assertEquals(instance.parameters.dt_const, 0.015625)
        instance.parameters.dt_const = 0.025625
        self.assertEquals(instance.parameters.dt_const, 0.025625)

        self.assertEquals(instance.parameters.eta, 0.0625)
        instance.parameters.eta = 0.0726
        self.assertEquals(instance.parameters.eta, 0.0726)

        self.assertEquals(instance.parameters.n_iter, 1)
        instance.parameters.n_iter = 2
        self.assertEquals(instance.parameters.n_iter, 2)

        self.assertEquals(instance.parameters.collision_mode, 0)
        instance.parameters.collision_mode = 1
        self.assertEquals(instance.parameters.collision_mode, 1)

        self.assertEquals(instance.parameters.roche_mode, 0)
        instance.parameters.roche_mode = 2
        self.assertEquals(instance.parameters.roche_mode, 2)

        self.assertEquals(instance.parameters.breakup_mode, 0)
        instance.parameters.breakup_mode = 1
        self.assertEquals(instance.parameters.breakup_mode, 1)

        self.assertEquals(instance.parameters.initial_shape, 0)
        instance.parameters.initial_shape = 1
        self.assertEquals(instance.parameters.initial_shape, 1)

        instance.commit_parameters()

        instance.particles.add_particles(system)

        # check that parameters are still set
        # correctly after adding a particle
        self.assertEquals(instance.parameters.tidal_model, 4)
        self.assertEquals(instance.parameters.pn_order, 1)
        self.assertEquals(instance.parameters.magnetic_braking, 1)
        self.assertEquals(instance.parameters.speed_of_light, 2e100)
        self.assertEquals(instance.parameters.dt_mode, 2)
        self.assertEquals(instance.parameters.dt_const, 0.025625)
        self.assertEquals(instance.parameters.eta, 0.0726)
        self.assertEquals(instance.parameters.n_iter, 2)
        self.assertEquals(instance.parameters.collision_mode, 1)
        self.assertEquals(instance.parameters.roche_mode, 2)
        self.assertEquals(instance.parameters.breakup_mode, 1)
        self.assertEquals(instance.parameters.initial_shape, 1)

        instance.stop()

    def test2(self):
        """
        Test Tidymess add_particles method.
        """
        system = self.earth_moon_system()
        converter = nbody_system.nbody_to_si(system.mass.sum(), system[0].position.length())

        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        instance.parameters.tidal_model = 0
        instance.particles.add_particles(system)

        self.assertEquals(instance.get_number_of_particles(), 2)

        self.assertEquals(instance.model_time, 0 | u.s)
        self.assertAlmostEquals(instance.get_total_mass(), system[0].mass + system[1].mass)
        self.assertAlmostEquals(instance.get_total_radius(), 379730731.968 | u.m, 3)

        instance.delete_particle(1)
        self.assertEquals(instance.get_number_of_particles(), 1)
        self.assertAlmostEquals(instance.get_total_mass(), system[0].mass)

        instance.stop()

    def test3(self):
        """
        Test the function for converting spin vectors
        """

        converter = nbody_system.nbody_to_si(1 | u.MEarth, 1 | u.REarth)
        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        lod = 24 | u.hour
        obl = 10 | u.deg
        psi = 0 | u.deg

        spin = instance.convert_spin_vectors_to_inertial(lod, obl, psi)

        self.assertAlmostEquals(spin[0], 0 | 1 / u.s)
        self.assertAlmostEquals(spin[1], -1.26280518349e-5 | 1 / u.s)
        self.assertAlmostEquals(spin[2], 7.16172407885e-5 | 1 / u.s)

        instance.stop()

    def test4(self):
        """
        Evolve a system of Particles
        """
        system = self.earth_moon_system()

        converter = nbody_system.nbody_to_si(
            system.mass.sum(), system[0].position.length()
        )
        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        instance.parameters.tidal_model = 0
        instance.parameters.dt_mode = 2
        instance.commit_parameters()

        instance.particles.add_particles(system)

        ratio = instance.get_total_mass() / system.mass.sum()
        self.assertAlmostEquals(ratio, 1)

        end_time = 1.1
        dt = 0.1
        times = np.arange(0, end_time, dt) | u.yr

        planet_positions = np.zeros((times.shape[0], 3))
        moon_positions = np.zeros_like(planet_positions)
        channel = instance.particles.new_channel_to(system)

        for i, t in enumerate(times):

            instance.evolve_model(t)
            channel.copy()

            planet_positions[i] = system[0].position.number
            moon_positions[i] = system[1].position.number

        evol_time = instance.get_time()
        year = u.yr.in_(u.s)

        self.assertAlmostEquals(evol_time, year)
        self.assertNotEqual(planet_positions[0,0], planet_positions[-1,0])
        self.assertNotEqual(moon_positions[0,0], moon_positions[-1,0])

        instance.stop()

    def test5(self):
        """
        Evolve a system.
        """

        converter = nbody_system.nbody_to_si(1|u.MEarth, 1|u.REarth)
        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        index_earth = instance.new_particle(
            1.0 | u.MEarth,
            -4.6706380895356489e+06 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m / u.s,
            -1.2449006368729913e+01 | u.m / u.s,
            0.0000000000000000e+00 | u.m / u.s,
        )
        self.assertEquals(index_earth, 0)

        index_moon = instance.new_particle(
            7.3460000000000003e+22 | u.kg,
            3.7972936191046441e+08 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m / u.s,
            1.0121215033569634e+03 | u.m / u.s,
            0.0000000000000000e+00 | u.m / u.s,
        )
        self.assertEquals(index_moon, 1)
        appendix = "dt_sgn changed (>=)"

        tidal_model = 0
        instance.set_tidal_model(tidal_model)
        dt_mode = 2
        instance.set_dt_mode(dt_mode)

        # Empty lists for properties to track
        star_positions = []
        planet_positions = []
        moon_positions = []

        # Running gravity code
        end_time = 0.1
        dt = 0.01
        times = np.arange(0, end_time, dt) | u.yr

        planet_pos = instance.get_position(0)
        moon_pos = instance.get_position(1)

        for t in times:

            instance.evolve_model(t)

            planet_pos = instance.get_position(0)
            moon_pos = instance.get_position(1)

            planet_positions.append([planet_pos[0].number, planet_pos[1].number, planet_pos[2].number])
            moon_positions.append([moon_pos[0].number, moon_pos[1].number, moon_pos[2].number])

        planet_positions = np.asarray(planet_positions)
        moon_positions = np.asarray(moon_positions)

        #plt.plot(planet_positions[:,0], planet_positions[:,1], marker='.')
        #plt.plot(moon_positions[:,0], moon_positions[:,1], marker='.')
        #plt.axis("equal")
        #plt.title("tidal_model="+str(tidal_model)+", dt_mode="+str(dt_mode)+", dt="+str(dt)+", end_time="+str(end_time)+"\n"+appendix)
        #plt.savefig("figures/tidal_model="+str(tidal_model)+", dt_mode="+str(dt_mode)+", dt="+str(dt)+", end_time="+str(end_time)+", "+appendix+".png")
        #plt.show()

        self.assertNotEqual(planet_positions[0,0],planet_positions[-1,0])
        self.assertNotEqual(planet_positions[0,1],planet_positions[-1,1])

        instance.stop()
