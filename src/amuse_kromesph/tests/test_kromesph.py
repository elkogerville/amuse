from amuse.datamodel import Particles
from amuse.ic.molecular_cloud import new_molecular_cloud
from amuse.support.testing.amusetest import TestWithMPI
from amuse.units import units, nbody_system
from amuse_kromesph.interface import (
    KromeSph, KromeSphInterface, solar_abundances
)
import numpy as np


default_options = dict(redirection='none')

try:
    # dynamically retrieve the species list from Krome since it can change
    # based on the compilation options
    instance = KromeSph()
    krome_species = [key for key in instance.species.keys()]
    E_index = krome_species.index('E')
    krome_species.pop(E_index)
except:
    krome_species = None

class TestKromeSphInterface(TestWithMPI):

    def test_initialization(self):
        print("Test 1: initialization")
        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test_getters_and_setters(self):
        print("Test 2: getters and setters")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = 1.e5
        u = 500
        gamma = 5/3
        mu = 1.23
        ion = 1.e-11
        id, err = instance.new_particle(dens, u, gamma, mu, ion)

        new_dens = 2e5
        new_u = 1000
        new_gamma = 10/3
        new_mu = 2.23
        new_ionrate = 1e-12

        instance.set_density(1, new_dens)
        instance.set_internal_energy(1, new_u)
        instance.set_gamma(1, new_gamma)
        instance.set_mu(1, new_mu)
        instance.set_ionrate(1, new_ionrate)

        res = instance.get_density(1)
        self.assertEquals(res['rho'], new_dens)
        res = instance.get_internal_energy(1)
        self.assertEquals(res['u'], new_u)
        res = instance.get_gamma(1)
        self.assertEquals(res['gamma'], new_gamma)
        res = instance.get_mu(1)
        self.assertEquals(res['mu'], new_mu)
        res = instance.get_ionrate(1)
        self.assertEquals(res['ionrate'], new_ionrate)

        instance.stop()

    def test_add_1_particle_and_get_state(self):
        print("Test 3: add particle, get state")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = 1.e5
        u = 500
        gamma = 5/3
        mu = 1.23
        ion = 1.e-11
        id, err = instance.new_particle(dens, u, gamma, mu, ion)

        self.assertEqual(err, 0)

        self.assertEqual(instance.commit_particles(), 0)

        dens_, u_, gamma_, mu_, ion_, err = instance.get_state(id)

        self.assertEqual(err, 0)

        self.assertEqual(dens_, dens)
        self.assertEqual(u_, u)
        self.assertEqual(gamma_, gamma)
        self.assertEqual(mu_, mu_)
        self.assertEqual(ion_, ion)

        self.assertEqual(0, instance.cleanup_code())

        instance.stop()

    def test_add_2_particles_and_get_state(self):
        print("Test 4: add 2 particles, get state")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = [1.e5, 2.e5]
        u = [500, 550]
        gamma = [5/3, 6/4]
        mu = [1.23, 2.23]
        ion = [1.e-11, 2.e-11]
        ids, err = instance.new_particle(dens, u, gamma, mu, ion)

        self.assertEqual(err, 0)

        self.assertEqual(instance.commit_particles(), 0)

        for i in range(2):
            dens_, u_, gamma_, mu_, ion_, err = instance.get_state(ids[i])

            self.assertEqual(err, 0)

            self.assertEqual(dens_, dens[i])
            self.assertEqual(u_, u[i])
            self.assertEqual(gamma_, gamma[i])
            self.assertEqual(mu_, mu[i])
            self.assertEqual(ion_, ion[i])

        self.assertEqual(0, instance.cleanup_code())

        instance.stop()

    def test_add_100_particles_and_get_state(self):
        print("Test 5: add 100 particles, get state")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = 1.e5*np.random.random(100)
        u = 500.*np.random.random(100)
        gamma = 3/5.*np.random.random(100)
        mu = 1.23*np.random.random(100)
        ion = 1.e-11*np.random.random(100)
        ids, err = instance.new_particle(dens, u, gamma, mu, ion)

        self.assertEqual(err, 0)

        self.assertEqual(instance.commit_particles(), 0)

        for i in range(100):
            dens_, u_, gamma_, mu_, ion_, err = instance.get_state(ids[i])

            self.assertEqual(err, 0)

            self.assertEqual(dens_, dens[i])
            self.assertEqual(u_, u[i])
            self.assertEqual(gamma_, gamma[i])
            self.assertEqual(mu_, mu[i])
            self.assertEqual(ion_, ion[i])

        self.assertEqual(0, instance.cleanup_code())

        instance.stop()

    def test_get_species(self):
        print("Test 6: can we get species?")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None

        first, last, err = instance.get_firstlast_species_index()
        self.assertEqual(err, 0)
        self.assertTrue(last-first > 0)

        for i in range(first, last+1):
            name, err = instance.get_species_name(i)
            print(name)
            self.assertEqual(err, 0)
            index, err = instance.get_species_index(name)
            self.assertEqual(i, index)

        instance.stop()

    def test_add_and_remove_particles(self):
        print("Test 7: add 100 particles, remove particles")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = 1.e5*np.random.random(100)
        u = 500.*np.random.random(100)
        gamma = 3/5.*np.random.random(100)
        mu = 1.23*np.random.random(100)
        ion = 1.e-11*np.random.random(100)
        ids, err = instance.new_particle(dens, u, gamma, mu, ion)

        self.assertEqual(err, 0)

        self.assertEqual(instance.commit_particles(), 0)

        for i in ids[:10]:
            instance.delete_particle(i)

        instance.recommit_particles()

        for i in range(10, 100):
            dens_, u_, gamma_, mu_, ion_, err = instance.get_state(ids[i])

            self.assertEqual(err, 0)

            self.assertEqual(dens_, dens[i])
            self.assertEqual(u_, u[i])
            self.assertEqual(gamma_, gamma[i])
            self.assertEqual(mu_, mu[i])
            self.assertEqual(ion_, ion[i])

        dens_, u_, gamma_, mu_, ion_, err = instance.get_state(ids[0])

        self.assertEqual(err, -1)

        self.assertEqual(0, instance.cleanup_code())

        instance.stop()

    def test_add_particle_and_set_abundances(self):
        print("Test 8: add particle, set abundances")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = 1.e5
        u = 500.
        gamma = 5/3
        mu = 1.23
        ion = 1.e-11
        id, err = instance.new_particle(dens, u, gamma, mu, ion)

        instance.commit_particles()

        first, last, err = instance.get_firstlast_species_index()
        for i in range(first, last+1):
            x, err = instance.get_abundance(id, i)
            self.assertTrue((x >= 0.) & (x <= 1.))
            self.assertEqual(err, 0)
        x, err = instance.get_abundance(id, last+1)
        self.assertEqual(err, -1)

        if krome_species is not None:
            xs = np.random.rand(len(krome_species))
            for i, s in enumerate(krome_species):
                x = xs[i]
                aid, err = instance.get_species_index(s)
                instance.set_abundance(id, aid, x)

            for i, s in enumerate(krome_species):
                x = xs[i]
                aid, err = instance.get_species_index(s)
                xx, err = instance.get_abundance(id, aid)
                self.assertEqual(x, xx)
                self.assertEqual(err, 0)

    def test_evolve(self):
        print("Test 9: evolve test")

        instance = self.new_instance_of_an_optional_code(KromeSphInterface, **default_options)
        assert instance is not None
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())

        dens = 1.86510064359e-17
        u = 204790703997.0
        gamma = 5./3.
        mu = 1.23
        ion = 0
        id, err = instance.new_particle(dens, u, gamma, mu, ion)
        instance.commit_particles()

        first, last, err = instance.get_firstlast_species_index()
        for i in range(first, last+1):
            err = instance.set_abundance(id, i, 1e-40)
            print(instance.get_abundance(id, i))

        yr = 365*24*3600.
        err = instance.evolve_model(10000*yr)
        self.assertEqual(err, 0)
        time, err = instance.get_time()
        self.assertEqual(err, 0)
        self.assertEqual(time, 10000.*yr)

        instance.stop()


class TestKromeSph(TestWithMPI):
    def molecular_cloud(self, N):
        """Make a molecular cloud with N particles."""
        Mgas = 3e4 | units.MSun
        Rgas = 0.14 | units.pc

        converter = nbody_system.nbody_to_si(Mgas, Rgas)
        cloud = new_molecular_cloud(
            target_number_of_particles=N,
            convert_nbody=converter
        )
        cloud.rho = 1.86510064359e-17 | units.g * units.cm**-3
        cloud.u = 204790703997.0 | units.cm**2 * units.s**-2
        gamma = 5./3.
        cloud.mu = 1.23 | units.amu
        cloud.gamma = gamma
        cloud.ionrate = 0.0 | units.s**-1
        cloud.index = range(N)
        return cloud

    def test_startup(self):
        print("Test 1: basic startup and flow")
        instance = self.new_instance_of_an_optional_code(KromeSph)
        assert instance is not None

        self.assertEqual(instance.get_name_of_current_state(), 'UNINITIALIZED')
        instance.initialize_code()
        self.assertEqual(instance.get_name_of_current_state(), 'INITIALIZED')
        instance.commit_parameters()
        self.assertEqual(instance.get_name_of_current_state(), 'EDIT')
        instance.commit_particles()
        self.assertEqual(instance.get_name_of_current_state(), 'RUN')

        instance.cleanup_code()
        instance.stop()

    def test_add_particles(self):
        print("Test 2: adding particles")

        instance = self.new_instance_of_an_optional_code(KromeSph)
        assert instance is not None

        parts = self.molecular_cloud(5)

        self.assertEqual(len(instance.particles), 0)
        instance.particles.add_particles(parts)
        self.assertEqual(len(instance.particles), len(parts))

        self.assertEqual(instance.get_name_of_current_state(), 'EDIT')

        instance.commit_particles()
        self.assertEqual(instance.get_number_of_particles(), len(parts))

        part2 = instance.particles.copy()

        self.assertAlmostRelativeEquals(parts.rho, part2.rho, 12)
        self.assertAlmostRelativeEquals(parts.u, part2.u, 12)
        self.assertAlmostRelativeEquals(parts.gamma, part2.gamma, 12)
        self.assertAlmostRelativeEquals(parts.mu, part2.mu, 12)
        self.assertAlmostRelativeEquals(parts.ionrate, part2.ionrate, 12)

        instance.cleanup_code()
        instance.stop()

    def test_add_particles_with_abundances(self):
        print("Test 3: adding particles w abund.")

        instance = self.new_instance_of_an_optional_code(KromeSph)
        assert instance is not None

        cloud = self.molecular_cloud(100)
        instance.particles.add_particles(cloud)

        channel_chem_2_gas = instance.particles.new_channel_to(cloud)
        channel_gas_2_chem = cloud.new_channel_to(instance.particles)

        for p in cloud.index:
            instance.set_abundance(p+1, instance.species['H']+1, 0.76875095999999998)
            instance.set_abundance(p+1, instance.species['H2']+1, 0.0023031866999999998)
            instance.set_abundance(p+1, instance.species['H+']+1, 5.8058537999999997e-09)
            instance.set_abundance(p+1, instance.species['HE']+1, 0.23894584999999999)

        instance.commit_particles()
        instance.evolve_model(100 | units.yr)
        self.assertAlmostRelativeEquals(
            instance.model_time.as_quantity_in(units.yr), 100 | units.yr
        )
        instance.cleanup_code()
        instance.stop()

    def test_1000_particles_evolve(self):
        print("Test 4: evolve test (1000 part)")

        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        parts = self.molecular_cloud(1000)

        Ns = len(instance.species)
        parts.abundances = np.zeros((1000, Ns))

        instance.particles.add_particles(parts)

        instance.evolve_model(1. | units.Myr)

        self.assertAlmostRelativeEquals(
            instance.model_time.as_quantity_in(units.Myr), 1 | units.Myr
        )

        instance.cleanup_code()
        instance.stop()

    def test_delete_particles_and_abundances(self):
        print("Test 5: Delete particles")

        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        N_particles = 10
        parts = self.molecular_cloud(N_particles)

        instance.particles.add_particles(parts)
        instance.commit_particles()

        instance.evolve_model(100 | units.yr)

        N_species = len(instance.species)
        abundances = instance.particles.abundances
        self.assertEquals(abundances.shape, (N_particles, N_species))
        self.assertEquals(instance.get_number_of_particles(), N_particles)

        instance.particles.remove_particle(parts[0])
        instance.recommit_particles()
        self.assertEquals(instance.get_number_of_particles(), N_particles-1)
        self.assertEquals(instance.particles.abundances.shape, (N_particles-1, N_species))
        self.assertEquals(instance.particles.abundances.shape, abundances[1:, :].shape)
        self.assertEquals(instance.particles.abundances, abundances[1:, :])

        instance.particles.remove_particle(parts[1:5])
        instance.recommit_particles()
        self.assertEquals(instance.get_number_of_particles(), N_particles-5)
        self.assertEquals(instance.particles.abundances.shape, (N_particles-5, N_species))
        self.assertEquals(instance.particles.abundances, abundances[5:, :])

        instance.particles.remove_particles(parts[5:])
        instance.recommit_particles()
        self.assertEquals(instance.get_number_of_particles(), 0)

        instance.cleanup_code()
        instance.stop()

    def test_species_index(self):
        print("Test 6: test querying species")
        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        species = instance.species
        for name, index in species.items():
            self.assertEquals(
                instance.species[name], instance.get_species_index(name)
            )

            self.assertEquals(
                name, instance.get_species_name(index)
            )

        first, last = instance.get_firstlast_species_index()
        print(first, last)
        # boundary check 1: first and last index round-trip correctly
        for i in (first, last):
            print(i)
            name = instance.get_species_name(i)
            idx = instance.get_species_index(name)
            assert idx == i, f"boundary mismatch at i={i}: name={name}, got idx={idx}"

        # boundary check 2: full round-trip over every index, not just species dict membership
        for i in range(first, last + 1):
            print(i)
            name = instance.get_species_name(i)
            idx = instance.get_species_index(name)
            assert idx == i, f"mismatch at i={i}: name={name!r}, idx={idx}"

        instance.cleanup_code()
        instance.stop()

    def test_get_abundance(self):
        print("Test 7: get_abundance")

        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        cloud = self.molecular_cloud(100)
        instance.particles.add_particles(cloud)

        reference_abundances = {
            'H': 0.76875095999999998,
            'H2': 0.0023031866999999998,
            'H+': 5.8058537999999997e-09,
            'HE': 0.23894584999999999,
        }

        for p in cloud.index:
            for species, value in reference_abundances.items():
                instance.set_abundance(p+1, instance.species[species], value)

        instance.commit_particles()

        for species, expected in reference_abundances.items():
            result = instance.get_abundance(1, instance.species[species])
            self.assertAlmostRelativeEquals(result, expected, 7)

        instance.cleanup_code()
        instance.stop()

    def test_set_abundance(self):
        print("Test 8: set_abundance")

        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        cloud = self.molecular_cloud(100)
        instance.particles.add_particles(cloud)

        instance.set_abundance(1, instance.species['H2'], 0.0023031866999999998)
        instance.commit_particles()

        result = instance.get_abundance(1, instance.species['H2'])
        self.assertEquals(result, 0.0023031866999999998)

        instance.cleanup_code()
        instance.stop()

    def test_set_abundances(self):
        print("Test 9: set_abundances from array")

        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        cloud = self.molecular_cloud(2)
        instance.particles.add_particles(cloud)

        n_species = len(instance.species)
        abundances = np.zeros(n_species)
        abundances[instance.species['H'] - 1] = 0.76875095999999998
        abundances[instance.species['H2'] - 1] = 0.0023031866999999998
        abundances[instance.species['H+'] - 1] = 5.8058537999999997e-09
        abundances[instance.species['HE'] - 1] = 0.23894584999999999

        instance.set_abundances(1, abundances)
        instance.set_abundances(2, abundances*2)
        instance.commit_particles()

        for species, expected in [
            ('H', 0.76875095999999998),
            ('H2', 0.0023031866999999998),
            ('H+', 5.8058537999999997e-09),
            ('HE', 0.23894584999999999),
        ]:
            result = instance.get_abundance(1, instance.species[species])
            self.assertAlmostRelativeEquals(result, expected, 7)
            result = instance.get_abundance(2, instance.species[species])
            self.assertAlmostRelativeEquals(result, expected*2, 7)

        instance.cleanup_code()
        instance.stop()

    def test_get_abundances_by_name(self):
        print("Test 10: get_abundances_by_name")

        instance = self.new_instance_of_an_optional_code(KromeSph, **default_options)
        assert instance is not None

        cloud = self.molecular_cloud(10)
        instance.particles.add_particles(cloud)

        reference_abundances = {
            'H': 0.76875095999999998,
            'H2': 0.0023031866999999998,
            'H+': 5.8058537999999997e-09,
            'HE': 0.23894584999999999,
        }

        for p in cloud.index:
            for species, value in reference_abundances.items():
                instance.set_abundance(p+1, instance.species[species], value)

        instance.commit_particles()

        # single-name input
        result_single = instance.get_abundances_by_name(1, 'H')
        self.assertAlmostRelativeEquals(result_single[0], reference_abundances['H'], 7)

        # sequence-of-names input, order must be preserved
        names = ['H', 'H2', 'H+', 'HE']
        result_seq = instance.get_abundances_by_name(1, names)
        expected_seq = np.array([reference_abundances[n] for n in names])
        self.assertAlmostRelativeEquals(result_seq, expected_seq, 7)

        instance.cleanup_code()
        instance.stop()
