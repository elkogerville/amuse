"""
Date Created : December 10, 2025
Last Updated : April 24, 2026
Tests for Tidymess and TidymessInterface
"""

from amuse.datamodel import Particles
from amuse.ext.orbital_elements import generate_binaries
from amuse.support.testing.amusetest import TestWithMPI
from amuse.units import constants as c, nbody_system, units as u
from amuse.units.quantities import VectorQuantity
from amuse_tidymess.interface import Tidymess, TidymessInterface
import numpy as np


class TestTidymessInterface(TestWithMPI):

    def test1(self):
        """
        Test Tidymess initialization.
        """
        print('Test initialization')
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
        print('Test setters and getters')
        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        assert instance is not None

        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 0)

        result = instance.new_particle(*np.arange(1, 16))

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

        result = instance.get_time_step()
        self.assertEquals(result['time_step'], 0)

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

        result = instance.get_num_integration_step()
        self.assertEquals(result['num_integration_step'], 0)

        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 1)

        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test3(self):
        """
        Test TidymessInterface creating and deleting particles.
        """
        print('Test creating and deleting particles')
        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        assert instance is not None

        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        # initialize new particle with all attributes set to 1
        result = instance.new_particle(*np.ones(15)*1)
        self.assertEqual(result['index_of_the_particle'], 0)

        # initialize new particle with all attributes set to 1.1
        result = instance.new_particle(*np.ones(15)*1.1)
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
        print('Test evolve_model')
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


    def HD80606b_system(self):
        """
        Initial conditions for the exoplanet system
        HD80606b. Initial conditions from Tidymess.
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
        HD80606[0].xi = 0.07
        HD80606[0].kf = 0.0
        HD80606[0].tau = 0.0 | u.yr
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
        HD80606[1].xi = 0.25
        HD80606[1].kf = 0.5
        HD80606[1].tau = 1e-2 | u.yr
        HD80606[1].wx = 0.0 | 1 / u.s
        HD80606[1].wy = 0.0 | 1 / u.s
        HD80606[1].wz = 0.000145444104333 | 1 / u.s

        return HD80606

    def figure8_system(self):
        figure8 = Particles(3)
        figure8[0].name = 'Star1'
        figure8[0].mass = 1 | nbody_system.mass
        figure8[0].radius = 5e-2 | nbody_system.length
        figure8[0].x = 0 | nbody_system.length
        figure8[0].y = 0 | nbody_system.length
        figure8[0].z = 0 | nbody_system.length
        figure8[0].vx = -0.93240737 | nbody_system.speed
        figure8[0].vy = -0.86473146 | nbody_system.speed
        figure8[0].vz = 0 | nbody_system.speed
        figure8[0].xi = 0.07
        figure8[0].kf = 0.02
        figure8[0].tau = 1e-2 | nbody_system.time
        figure8[0].wx = 0 | 1 / nbody_system.time
        figure8[0].wy = 0 | 1 / nbody_system.time
        figure8[0].wz = 0 | 1 / nbody_system.time

        figure8[1].name = 'Star2'
        figure8[1].mass = 1 | nbody_system.mass
        figure8[1].radius = 5e-2 | nbody_system.length
        figure8[1].x = 0.9700436 | nbody_system.length
        figure8[1].y = -0.24308753 | nbody_system.length
        figure8[1].z = 0 | nbody_system.length
        figure8[1].vx = 0.466203685 | nbody_system.speed
        figure8[1].vy = 0.43236573 | nbody_system.speed
        figure8[1].vz = 0 | nbody_system.speed
        figure8[1].xi = 0.07
        figure8[1].kf = 0.02
        figure8[1].tau = 1e-2 | nbody_system.time
        figure8[1].wx = 0 | 1 / nbody_system.time
        figure8[1].wy = 0 | 1 / nbody_system.time
        figure8[1].wz = 0 | 1 / nbody_system.time

        figure8[2].name = 'Star3'
        figure8[2].mass = 1 | nbody_system.mass
        figure8[2].radius = 5e-2 | nbody_system.length
        figure8[2].x = -0.9700436 | nbody_system.length
        figure8[2].y = 0.24308753 | nbody_system.length
        figure8[2].z = 0 | nbody_system.length
        figure8[2].vx = 0.466203685 | nbody_system.speed
        figure8[2].vy = 0.43236573 | nbody_system.speed
        figure8[2].vz = 0 | nbody_system.speed
        figure8[2].xi = 0.07
        figure8[2].kf = 0.02
        figure8[2].tau = 1e-2 | nbody_system.time
        figure8[2].wx = 0 | 1 / nbody_system.time
        figure8[2].wy = 0 | 1 / nbody_system.time
        figure8[2].wz = 0 | 1 / nbody_system.time

        return figure8

    def test1(self):
        """
        Test Tidymess parameters attribute and their defaults
        """
        print('Test parameters and their default values')
        system = self.earth_moon_system()
        converter = nbody_system.nbody_to_si(
            1 | u.MEarth, 1 | u.AU
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
        print('Test adding and deleting particles')
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
        print('Test converting spin vectors')
        converter = nbody_system.nbody_to_si(1 | u.MEarth, 1 | u.REarth)
        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        lod = 24 | u.hour
        obl = 10 | u.deg
        psi = 0 | u.deg

        spin = instance.convert_spin_vectors_to_inertial(lod, obl, psi)

        self.assertAlmostEquals(spin[0], 0 | 1/u.s)
        self.assertAlmostEquals(spin[1], -1.26280518349e-5 | 1/u.s)
        self.assertAlmostEquals(spin[2], 7.16172407885e-5 | 1/u.s)

        instance.stop()

    def test4(self):
        """
        Test that setting a begin time correctly creates a time offset.
        """
        print('Test setting begin_time')
        dt = 5 | u.yr
        begin_time = (50 | u.yr).as_quantity_in(u.s)
        end_time = begin_time + dt

        system = self.earth_moon_system()
        converter = nbody_system.nbody_to_si(
            1 | u.MEarth, 1 | u.au
        )
        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        instance.parameters.tidal_model = 0
        instance.parameters.dt_mode = 2
        instance.parameters.eta = 0.015625
        instance.commit_parameters()

        self.assertEquals(instance.get_begin_time(), instance.model_time)
        self.assertEquals(instance.get_begin_time(), 0 | u.s)

        instance.set_begin_time(begin_time)
        instance.particles.add_particles(system)

        instance.evolve_model(instance.model_time + dt)

        self.assertAlmostEquals(instance.get_begin_time(), begin_time, places=3)
        self.assertAlmostEquals(instance.model_time, end_time, places=3)

        instance.stop()

    def test5(self):
        """
        Test evolving backwards in time.

        2 identical figure 8 systems are created and evolved to t1.
        The second system is then evolved to t2 where t2 > t1.
        Finally the second system is evolved 'backwards' back to t1.
        System 2 should be identical to system 1 at the end of the
        backwards evolution.
        """
        print('Test evolving backwards in time')
        t1 = 1e3 | nbody_system.time
        t2 = 2e3 | nbody_system.time
        self.assertFalse(t1 > t2)

        # System 1
        # --------
        system1 = self.figure8_system()

        instance = self.new_instance_of_an_optional_code(Tidymess)
        assert instance is not None

        instance.parameters.tidal_model = 0
        instance.parameters.dt_mode = 2
        instance.parameters.eta = 0.015625
        instance.commit_parameters()

        instance.particles.add_particles(system1)
        channel1 = instance.particles.new_channel_to(system1)

        instance.evolve_model(t1)
        channel1.copy()
        self.assertEquals(instance.model_time, t1)

        instance.stop()

        # System 2
        # --------
        system2 = self.figure8_system()

        instance = self.new_instance_of_an_optional_code(Tidymess)
        assert instance is not None

        instance.parameters.tidal_model = 0
        instance.parameters.dt_mode = 2
        instance.parameters.eta = 0.015625
        instance.commit_parameters()

        instance.particles.add_particles(system2)
        channel2 = instance.particles.new_channel_to(system2)

        instance.evolve_model(t2)
        channel2.copy()
        self.assertEquals(instance.model_time, t2)

        instance.evolve_model(t1)
        channel2.copy()
        self.assertEquals(instance.model_time, t1)

        instance.stop()

        attributes = [
            'x', 'y', 'z',
            'vx', 'vy', 'vz',
            'wx', 'wy', 'wz',
            'mass', 'radius',
            'xi', 'kf', 'tau'
        ]

        for attr in attributes:
            self.assertAlmostEquals(
                getattr(system1, attr),
                getattr(system2, attr)
            )

    def test6(self):
        """
        Evolve a system of Particles without tides
        """
        end_time = 1 | u.yr
        dt_diag = 1e-4 | u.yr

        system = self.earth_moon_system()
        converter = nbody_system.nbody_to_si(
            system.mass.sum(), 1 | u.au
        )

        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        instance.parameters.tidal_model = 0
        instance.parameters.dt_mode = 2
        instance.parameters.eta = 0.0625
        instance.commit_parameters()

        instance.particles.add_particles(system)
        channel = instance.particles.new_channel_to(system)

        times = [] | u.yr
        times.append(0.0 | u.yr)
        particles = [system.copy()]

        while instance.model_time < end_time:
            time = instance.model_time + dt_diag
            instance.evolve_model(time)
            channel.copy()

            particles.append(system.copy())
            times.append(instance.model_time)

        self.assertAlmostEquals(
            particles[-1].position[0],
            VectorQuantity([3554487.97163, -3026275.21595, 0.0], u.m),
            places=1
        )
        self.assertAlmostEquals(
            particles[-1].position[1],
            VectorQuantity([-289132566.932, 246166178.762, 0.0], u.m),
            places=1
        )
        self.assertAlmostEquals(
            particles[-1].velocity[0],
            VectorQuantity([8.06599003995, 9.47384574385, 0.0], u.ms),
            places=1
        )
        self.assertAlmostEquals(
            particles[-1].velocity[1],
            VectorQuantity([-656.111491645, -770.630639491, 0.0], u.ms),
            places=1
        )
        self.assertAlmostRelativeEqual(times[-1], end_time, places=3)

        instance.stop()

    def test6(self):
        """
        Evolve the HD80606b exoplanet system with tides
        """
        end_time = 2e3 | u.yr
        dt_diag = 1 | u.yr

        system = self.HD80606b_system()
        converter = nbody_system.nbody_to_si(
            system.mass.sum(), end_time
        )

        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        assert instance is not None

        instance.parameters.tidal_model = 4
        instance.parameters.dt_mode = 2
        instance.parameters.eta = 0.0625
        instance.commit_parameters()

        instance.particles.add_particles(system)
        channel = instance.particles.new_channel_to(system)

        times = [] | u.yr
        times.append(0.0 | u.yr)
        particles = [system.copy()]

        while instance.model_time < end_time:
            time = instance.model_time + dt_diag
            instance.evolve_model(time)
            channel.copy()

            particles.append(system.copy())
            times.append(instance.model_time)

        # check that the last snapshot is correct
        self.assertAlmostEquals(
            particles[-1].position[0],
            VectorQuantity([137405.552133, -84398.2017397, 0.0], u.km),
            places=4
        )
        self.assertAlmostEquals(
            particles[-1].position[1],
            VectorQuantity([-35634334.1197, 21887570.4121, 0.0], u.km),
            places=4
        )
        self.assertAlmostEquals(
            particles[-1].velocity[0],
            VectorQuantity([0.249251771924, -0.0361309584992, 0.0], u.kms),
            places=4
        )
        self.assertAlmostEquals(
            particles[-1].velocity[1],
            VectorQuantity([-64.6401899292, 9.37009194233, 0.0], u.kms),
            places=4
        )
        self.assertAlmostRelativeEqual(times[-1], end_time, places=3)

        instance.stop()
