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

        return p

    def test_tsunami(self):
        system = self.generate_pythagorean()

        instance = Tsunami(redirection='none')
        assert instance is not None


        print(instance.parameters)

        instance.commit_parameters()

        instance.particles.add_particles(system)
        import matplotlib.pyplot as plt

        instance.commit_particles()
        channel = instance.particles.new_channel_to(system)

        print('ic\n', instance.particles)

        t_end = 65 | ns.time
        dt = 0.1 | ns.time
        particles = []

        while instance.model_time <  t_end:
            instance.evolve_model(instance.model_time + dt)
            channel.copy()
            particles.append(system.copy())
            print(instance.model_time)

        colors = ['darkslateblue', 'mediumvioletred', 'c']
        data = [[], [], []]

        for p in particles:
            for i in range(3):
                data[i].append((p[i].x.number, p[i].y.number))

        import visualastro as va
        with va.style('smplot'):
            fig = plt.figure(figsize=(5,8), tight_layout=True)
            ax = fig.add_subplot(111)
            for i, (color, pts) in enumerate(zip(colors, data)):
                xs, ys = zip(*pts)
                ax.plot(xs, ys, color=color, linewidth=0.8)

        plt.show()


        instance.stop()
