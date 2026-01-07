import numpy as np
import matplotlib.pyplot as plt

from amuse.support.testing.amusetest import TestWithMPI
from amuse_tidymess.interface import Tidymess, TidymessInterface
from amuse.units import units as u
from amuse.units import constants as c
from amuse.units import generic_unit_system, nbody_system
from amuse.datamodel import Particles
from amuse.ext.orbital_elements import generate_binaries, new_binary_from_orbital_elements

class TidymessInterfaceTests(TestWithMPI):

    def test1(self):
        """
        Test Tidymess initialization.
        """

        instance = self.new_instance_of_an_optional_code(TidymessInterface)
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test2(self):
        """
        Test TidymessInterface setters and getters.
        """

        instance = self.new_instance_of_an_optional_code(TidymessInterface)

        result = instance.get_number_of_particles()
        self.assertEquals(result['number_of_particles'], 0)

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
        )

        self.assertEqual(result['index_of_the_particle'], 0)

        # test get/set_mass
        instance.set_mass(0, 2.0)
        result = instance.get_mass(0)
        self.assertEquals(result['mass'], 2.0)

        # test get/set_position
        instance.set_position(0, 1.2, 1.2, 1.2)
        result = instance.get_position(0)
        self.assertEquals(result['x'], 1.2)
        self.assertEquals(result['y'], 1.2)
        self.assertEquals(result['z'], 1.2)

        # test get/set velocity
        instance.set_velocity(0, 1.3, 1.3, 1.3)
        result = instance.get_velocity(0)
        self.assertEquals(result['vx'], 1.3)
        self.assertEquals(result['vy'], 1.3)
        self.assertEquals(result['vz'], 1.3)

        # test get/set radius
        instance.set_radius(0, 1.0)
        result = instance.get_radius(0)
        self.assertEquals(result['radius'], 1.0)

        # test get/set spin
        instance.set_spin(0, 1.4, 1.4, 1.4)
        result = instance.get_spin(0)
        self.assertEquals(result['wx'], 1.4)
        self.assertEquals(result['wy'], 1.4)
        self.assertEquals(result['wz'], 1.4)

        # test get/set state
        result = instance.get_state(0)
        self.assertEquals(result['mass'], 2.0)
        self.assertEquals(result['x'], 1.2)
        self.assertEquals(result['y'], 1.2)
        self.assertEquals(result['z'], 1.2)
        self.assertEquals(result['vx'], 1.3)
        self.assertEquals(result['vy'], 1.3)
        self.assertEquals(result['vz'], 1.3)
        self.assertEquals(result['radius'], 1.0)

        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test3(self):
        """
        Test TidymessInterface creating and deleting particles.
        """

        instance = self.new_instance_of_an_optional_code(TidymessInterface)

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
        )

        self.assertEqual(result['index_of_the_particle'], 1)

        # check number of particles
        result = instance.get_number_of_particles()
        self.assertEqual(result['number_of_particles'], 2)

        # check that indexes are correct
        first = instance.get_index_of_first_particle()
        self.assertEqual(first['index_of_the_particle'], 0)

        next = instance.get_index_of_next_particle(0)
        self.assertEqual(next['index_of_the_next_particle'], 1)

        # delete particle
        instance.delete_particle(1)

        result = instance.get_number_of_particles()
        self.assertEqual(result['number_of_particles'], 1)

        first = instance.get_index_of_first_particle()
        self.assertEqual(first['index_of_the_particle'], 0)

        instance.stop()


class TestTidymess(TestWithMPI):

    def test1(self):
        """
        Test Tidymess parameters attribute.
        """

        instance = self.new_instance_of_an_optional_code(Tidymess)

        instance.set_tidal_model(4)
        self.assertEquals(instance.get_tidal_model(), 4)

        instance.set_tidal_model(0)
        self.assertEquals(instance.parameters.tidal_model, 0)

        self.assertEquals(instance.get_pn_order(), 0)
        instance.set_pn_order(1)
        self.assertEquals(instance.parameters.pn_order, 1)

        self.assertEquals(instance.get_magnetic_braking(), 0)
        instance.set_magnetic_braking(1)
        self.assertEquals(instance.parameters.magnetic_braking ,1)

        self.assertEquals(instance.get_collision_mode(), 0)
        instance.set_collision_mode(1)
        self.assertEquals(instance.parameters.collision_mode, 1)

        self.assertEquals(instance.get_roche_mode(), 0)
        instance.set_roche_mode(2)
        self.assertEquals(instance.parameters.roche_mode, 2)

        self.assertEquals(instance.get_breakup_mode(), 0)
        instance.set_breakup_mode(1)
        self.assertEquals(instance.parameters.breakup_mode, 1)

        instance.stop()

    def test2(self):
        """
        Test Tidymess add_particles method.
        """

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

        system = Particles()
        system.add_particles(planet)
        system.add_particles(moon)

        converter = nbody_system.nbody_to_si(system.mass.sum(), planet.position.length())
        instance = self.new_instance_of_an_optional_code(Tidymess, converter)
        instance.set_tidal_model(0)

        instance.particles.add_particles(system)
        instance.set_tidal_model(0)

        self.assertEquals(instance.get_time_step(), 0 | u.s)

        self.assertGreater(instance.get_total_mass(), 6.04562e24 | u.kg)
        self.assertLess(instance.get_total_mass(), 6.04563e24 | u.kg)
        self.assertEquals(instance.get_total_radius(), 8108400.0 | u.m)

        instance.stop()

    def test5(self):
        '''
        #Evolve a system of Particles
        '''

        system = new_binary_from_orbital_elements(
            5.9724e24 | u.kg,
            0.0735e24 | u.kg,
            0.3844e6 | u.km,
            G=c.G)
        planet = system[0]
        moon = system[1]

        planet.radius = 6371. | u.km
        planet.xi = 0.3308
        planet.kf = 0
        planet.tau = 180 | u.s
        planet.wx = 0.0 | 1/u.yr
        planet.wy = 0.0 | 1/u.yr
        planet.wz = 0.0 | 1/u.yr
        moon.radius = 1737.4 | u.km
        moon.xi = 0.394
        moon.kf = 0
        moon.tau = 0 | u.s
        moon.wx = 0.0 | 1/u.yr
        moon.wy = 0.0 | 1/u.yr
        moon.wz = 0.0 | 1/u.yr

        system.move_to_center()

        converter = nbody_system.nbody_to_si(system.mass.sum(), planet.position.length())
        instance = TIDYMESS(converter)
        tidal_model = 0
        instance.set_tidal_model(tidal_model)

        instance.particles.add_particles(system)  # hier wordt tidal_model weer naar 4 gezet?? waarom?
        instance.set_tidal_model(tidal_model)

        self.assertGreater(instance.get_total_mass(), 6.0458e24 | u.kg)
        self.assertLess(instance.get_total_mass(),    6.0460e24 | u.kg)
        self.assertEquals(instance.get_total_radius(), 8108400.0 | u.m)

        instance.set_dt_mode(2)

        # Empty lists for properties to track
        star_positions = []
        planet_positions = []
        moon_positions = []
        channel = instance.particles.new_channel_to(system)

        # Running gravity code
        end_time = 1
        dt = 0.1
        times = np.arange(0, end_time, dt) | u.yr

        for t in times:

            instance.evolve_model(t)
            channel.copy()

            system.move_to_center()

            planet_positions.append([planet.position.number[0], planet.position.number[1], planet.position.number[2]])
            moon_positions.append([moon.position.number[0], moon.position.number[1], moon.position.number[2]])

        planet_positions = np.asarray(planet_positions)
        moon_positions = np.asarray(moon_positions)

        self.assertNotEqual(planet_positions[0,0],planet_positions[-1,0]) # check if it evolved at all

        instance.stop()

    def test6(self):
        '''
        #Evolve a system
        '''

        converter = nbody_system.nbody_to_si(1|u.MEarth, 1|u.REarth)
        instance = TIDYMESS(converter)

        index_earth = instance.new_particle(
            1.0 | u.MEarth,
            -4.6706380895356489e+06 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m/u.s,
            -1.2449006368729913e+01 | u.m/u.s,
            0.0000000000000000e+00 | u.m/u.s,
        )
        self.assertEquals(index_earth, 0)

        index_moon = instance.new_particle(
            7.3460000000000003e+22 | u.kg,
            3.7972936191046441e+08 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m,
            0.0000000000000000e+00 | u.m/u.s,
            1.0121215033569634e+03 | u.m/u.s,
            0.0000000000000000e+00 | u.m/u.s,
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


    def test7(self):
        '''
        #Test the function for converting spin vectors
        '''

        converter = nbody_system.nbody_to_si(1|u.MEarth, 1|u.REarth)
        instance = TIDYMESS(converter)

        lod = 24 | u.hour
        obl = 10 | u.deg
        psi = 0 | u.deg

        spin = instance.convert_spin_vectors_to_inertial(lod, obl, psi)

        self.assertLess(np.abs(spin[2].number-7.1617240788458890e-05), 1e-19)


    def test8(self):
        '''
        #Test collisions (just remove both particles)
        '''

        def merge_two_stars(bodies, particles_in_encounter):
            com_pos = particles_in_encounter.center_of_mass()
            com_vel = particles_in_encounter.center_of_mass_velocity()
            d = (particles_in_encounter[0].position - particles_in_encounter[1].position)
            v = (particles_in_encounter[0].velocity - particles_in_encounter[1].velocity)
            print("Actually merger occurred:")
            print("Two stars (M=",particles_in_encounter.mass.in_(units.MSun),
                  ") collided with d=", d.length().in_(units.au))
            new_particle=Particles(1)
            new_particle.mass = particles_in_encounter.total_mass()
            new_particle.age = min(particles_in_encounter.age) \
                             * max(particles_in_encounter.mass)/new_particle.mass
            new_particle.position = com_pos
            new_particle.velocity = com_vel
            new_particle.radius = particles_in_encounter.radius.sum()
            bodies.add_particles(new_particle)
            bodies.remove_particles(particles_in_encounter)


        converter = nbody_system.nbody_to_si(1|u.MEarth, 1|u.REarth)
        instance = TIDYMESS(converter)

        index_earth = instance.new_particle(
            1.0 | u.MEarth,
            -2e8 | u.m,
            0.0 | u.m,
            0.0 | u.m,
            0.0 | u.m/u.s,
            0.0 | u.m/u.s,
            0.0 | u.m/u.s,
            3000 | u.km
        )
        self.assertEquals(index_earth, 0)

        index_moon = instance.new_particle(
            0.1 | u.kg,
            0.0e8 | u.m,
            -1.0e8 | u.m,
            0.0 | u.m,
            0.0 | u.m/u.s,
            1.0e3 | u.m/u.s,
            0.0 | u.m/u.s,
            3000 | u.km
        )
        self.assertEquals(index_moon, 1)

        dummy1 = instance.new_particle(
            0.1 | u.kg,
            100 | u.m,
            1.0e8 | u.m,
            0.0 | u.m,
            0.0 | u.m/u.s,
            -1.0e3 | u.m/u.s,
            0.0 | u.m/u.s,
            3000 | u.km
        )
        self.assertEquals(dummy1, 2)

        dummy2 = instance.new_particle(
            0.1 | u.kg,
            1.e8 | u.m,
            -2.0e8 | u.m,
            0.0 | u.m,
            0.0 | u.m/u.s,
            1.0e3 | u.m/u.s,
            0.0 | u.m/u.s,
            3000 | u.km
        )
        self.assertEquals(dummy2, 3)

        dummy3 = instance.new_particle(
            0.1 | u.kg,
            1e8 | u.m,
            2.0e8 | u.m,
            0.0 | u.m,
            0.0 | u.m/u.s,
            -1.0e3 | u.m/u.s,
            0.0 | u.m/u.s,
            3000 | u.km
        )
        self.assertEquals(dummy3, 4)

        dummy4 = instance.new_particle(
            0.1 | u.kg,
            1.4e8 | u.m,
            0.0 | u.m,
            0.0 | u.m,
            0.0 | u.m/u.s,
            1.0e3 | u.m/u.s,
            0.0 | u.m/u.s,
            3000 | u.km
        )
        self.assertEquals(dummy4, 5)

        appendix = ""

        tidal_model = 0
        instance.set_tidal_model(tidal_model)
        dt_mode = 2
        instance.set_dt_mode(dt_mode)


        # Running gravity code
        end_time = 5
        dt = end_time/13
        times = np.arange(0, end_time, dt) | u.day
        print("times:",times)

        planet_pos = instance.get_position(0)
        moon_pos = instance.get_position(1)

        def get_particle_indices():
            N = instance.get_number_of_particles()
            idx = instance.get_index_of_first_particle()
            indices = [idx]
            while len(indices) < N:
                idx = instance.get_index_of_next_particle(idx)
                indices.append(idx)
            return indices

        # Empty lists for properties to track
        positions = [[], [], [], [], [], []]
        self.assertEquals(len(positions), instance.get_number_of_particles())

        instance.set_collision_mode(3) # 0=off, 1=ignore, 2=exception, 3=replace
        print("collision_mode:", instance.parameters.collision_mode, "(0=off, 1=ignore, 2=exception, 3=replace)")

        for t in times:
            print(t)

            instance.evolve_model(t)

            indices = get_particle_indices()
            print("indices:", indices)
            for idx in indices:
                pos = instance.get_position(idx)
                positions[idx].append([pos[0].number, pos[1].number, pos[2].number])

            collision_flag, n_collisions, collider1, collider2 = instance.detect_collision()
            if n_collisions > 0:
                print("botsing! deeltjes", collider1, collider2)
                instance.delete_particle(collider2)
                instance.delete_particle(collider1)
                print("deleted colliding particles")
            else:
                print("geen botsingen")

        for i in range(len(positions)):
            pos = np.asarray(positions[i])
            plt.plot(pos[:,0], pos[:,1], marker='.', alpha=0.5)

        plt.axis("equal")
        plt.title("tidal_model="+str(tidal_model)+", dt_mode="+str(dt_mode)+", dt="+str(dt)+", end_time="+str(end_time)+"\n"+appendix)
        #plt.show()

        instance.stop()

    def test9(self):
        '''
        #Test collisions (replace particles)
        '''

        def merge_two_stars(bodies, particles_in_encounter):
            com_pos = particles_in_encounter.center_of_mass()
            com_vel = particles_in_encounter.center_of_mass_velocity()
            d = (particles_in_encounter[0].position - particles_in_encounter[1].position)
            v = (particles_in_encounter[0].velocity - particles_in_encounter[1].velocity)
            new_particle=Particles(1)
            new_particle.mass = particles_in_encounter.total_mass()
            new_particle.position = com_pos
            new_particle.velocity = com_vel
            new_particle.radius = particles_in_encounter.radius.sum()
            bodies.add_particles(new_particle)
            bodies.remove_particles(particles_in_encounter)


        converter = nbody_system.nbody_to_si(1|u.MEarth, 1|u.REarth)
        instance = TIDYMESS(converter)


        system = Particles(6)

        # planeet staat stil
        system[0].mass = 1.0 | u.MEarth
        system[0].x = -2e8 | u.m
        system[0].y =  0.0 | u.m
        system[0].z =  0.0 | u.m
        system[0].vx = 0.0 | u.m/u.s
        system[0].vy = 0.0 | u.m/u.s
        system[0].vz = 0.0 | u.m/u.s
        system[0].radius = 3000 | u.km
        system[0].index = 0

        # 1e botser van boven
        system[1].mass = 0.1 | u.kg
        system[1].x =  0.0 | u.m
        system[1].y = -1.0e8 | u.m
        system[1].z =  0.0 | u.m
        system[1].vx = 0.0 | u.m/u.s
        system[1].vy = 1.0e3 | u.m/u.s
        system[1].vz = 0.0 | u.m/u.s
        system[1].radius = 3000 | u.km
        system[1].index = 1

        # 1e botser van beneden
        system[2].mass = 0.1 | u.kg
        system[2].x = 100 | u.m
        system[2].y = 1.0e8 | u.m
        system[2].z = 0.0 | u.m
        system[2].vx = 0.0 | u.m/u.s
        system[2].vy = -1.0e3 | u.m/u.s
        system[2].vz = 0.0 | u.m/u.s
        system[2].radius = 3000 | u.km
        system[2].index = 2

        # 2e botser van boven
        system[3].mass = 0.1 | u.kg
        system[3].x = 1.0e8 | u.m
        system[3].y = -2.0e8 | u.m
        system[3].z =  0.0 | u.m
        system[3].vx = 0.0 | u.m/u.s
        system[3].vy = 1.0e3 | u.m/u.s
        system[3].vz = 0.0 | u.m/u.s
        system[3].radius = 3000 | u.km
        system[3].index = 3

        # 2e botser van beneden
        system[4].mass = 0.1 | u.kg
        system[4].x = 1.0e8 | u.m
        system[4].y = 2.0e8 | u.m
        system[4].z = 0.0 | u.m
        system[4].vx = 0.0 | u.m/u.s
        system[4].vy = -1.0e3 | u.m/u.s
        system[4].vz = 0.0 | u.m/u.s
        system[4].radius = 3000 | u.km
        system[4].index = 4

        # botst niet
        system[5].mass = 0.1 | u.kg
        system[5].x =  1.4e8 | u.m
        system[5].y =  0.0 | u.m
        system[5].z =  0.0 | u.m
        system[5].vx = 0.0 | u.m/u.s
        system[5].vy = 1.0e3 | u.m/u.s
        system[5].vz = 0.0 | u.m/u.s
        system[5].radius = 3000 | u.km
        system[5].index = 5

        instance.particles.add_particles(system)

        appendix = ""

        tidal_model = 0
        instance.set_tidal_model(tidal_model)
        dt_mode = 2
        instance.set_dt_mode(dt_mode)


        # Running gravity code
        end_time = 5
        dt = end_time/13
        times = np.arange(0, end_time, dt) | u.day

        planet_pos = instance.get_position(0)
        moon_pos = instance.get_position(1)

        def get_particle_indices():
            N = instance.get_number_of_particles()
            idx = instance.get_index_of_first_particle()
            indices = [idx]
            while len(indices) < N:
                idx = instance.get_index_of_next_particle(idx)
                indices.append(idx)
            return indices

        # Empty lists for properties to track
        positions = [[], [], [], [], [], []]
        self.assertEquals(len(positions), instance.get_number_of_particles())
        channel = instance.particles.new_channel_to(system)

        instance.set_collision_mode(3) # 0=off, 1=ignore, 2=exception, 3=replace

        for t in times:
            print("\ntijd:", t)

            instance.evolve_model(t)

            indices = get_particle_indices()
            print("indices:", indices)
            for idx in indices:
                pos = instance.get_position(idx)
                positions[idx].append([pos[0].number, pos[1].number, pos[2].number])

            collision_flag, n_collisions, collider1, collider2 = instance.detect_collision()
            if n_collisions > 0:
                print("botsing! deeltjes", collider1, "en", collider2)

                particle_indices = []
                for i in range(len(system)):
                    if system[i].index in [collider1, collider2]:
                        particle_indices.append(i)
                encountering_particles = system[particle_indices]

                indices.remove(collider1)
                indices.remove(collider2)
                indices.append(max(indices)+1)
                merge_two_stars(system, encountering_particles)
                system[-1].index = max(indices)
                system.synchronize_to(instance.particles)
                positions.append([])
                print("new system indices:",system.index)
            else:
                print("geen botsingen")
            channel.copy()

        for i in range(len(positions)):
            pos = np.asarray(positions[i])
            plt.plot(pos[:,0], pos[:,1], marker='.', alpha=0.5)

        plt.axis("equal")
        plt.title("tidal_model="+str(tidal_model)+", dt_mode="+str(dt_mode)+", dt="+str(dt)+", end_time="+str(end_time)+"\n"+appendix)
        #plt.show()

        instance.stop()
