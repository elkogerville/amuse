"""
Evolve a population of N stars.
initial mass function between Mmin and Mmax and with stellar evolution with
metalicity z.
"""

import numpy
import matplotlib.pyplot as plt

from amuse.units import units
from amuse.datamodel import Particles
from amuse.community.seba import Seba
from amuse.community.sse import Sse
from amuse.community.mesa_r2208 import Mesa
from amuse.io import write_set_to_file, read_set_from_file

# from amuse.community.seba.interface import SeBa


def _get_stellar_temperature_and_luminosity(
    stars, C, z=0.02, t_end=100 | units.Myr, write=False
):

    if C.find("SeBa") >= 0:
        stellar = Seba()
        filename = "Stellar_SeBa.amuse"
    if C.find("SSE") >= 0:
        stellar = Sse()
        filename = "Stellar_SSE.amuse"
    if C.find("MESA") >= 0:
        stellar = Mesa()
        filename = "Stellar_MESA.amuse"
    if C.find("EVtwin") >= 0:
        stellar = Seba()
        filename = "Stellar_EVtwin.amuse"

    stellar.parameters.metallicity = z
    stellar.particles.add_particles(stars)

    for si in stellar.particles:
        try:
            si.evolve_for(t_end)
        except:
            print("Failed to evolve star: m=", si.mass.in_(units.MSun))
            # stellar.evolve_model(t_end)
    if write:
        # write_set_to_file(stellar.particles.savepoint(t_end), filename, 'amuse')
        write_set_to_file(stellar.particles, filename)
    stellar.stop()


def get_stellar_temperature_and_luminosity(
    stars, C, z=0.02, t_end=100 | units.Myr, write=False
):

    if C.find("SeBa") >= 0:
        filename = "Stellar_SeBa.amuse"
        stellar = Seba()
        stellar.parameters.metallicity = z
        stellar.particles.add_particles(stars)
        channel_to_framework = stellar.particles.new_channel_to(stars)
        stellar.evolve_model(t_end)
        channel_to_framework.copy_attributes(["radius", "temperature", "luminosity"])
        stellar.stop()
    else:
        if C.find("MESA") >= 0:
            filename = "Stellar_MESA.amuse"
        if C.find("EVtwin") >= 0:
            filename = "Stellar_EVtwin.amuse"

        for si in stars:
            stellar = Mesa()
            stellar.parameters.metallicity = z
            stellar.particles.add_particle(si)
            # stellar.commit_particles()
            channel_to_framework = stellar.particles.new_channel_to(stars)
            try:
                stellar.evolve_model(t_end)
                channel_to_framework.copy_attributes(
                    ["radius", "temperature", "luminosity"]
                )
                print("Successvolly evolved star: m=", si.mass.in_(units.MSun))
            except:
                print("Failed to evolve star: m=", si.mass.in_(units.MSun))
                # stellar.evolve_model(t_end)
            stellar.stop()
    if write:
        write_set_to_file(stars, filename)


def plot_hrd(filename, ax):
    stars = read_set_from_file(filename)
    T = stars.temperature.value_in(units.K)
    L = stars.luminosity.value_in(units.LSun)
    R = stars.radius.value_in(units.RSun)

    R = 80 * numpy.sqrt(R)
    ax.scatter(T, L, lw=0, s=R)


def stellar_isochrone(N, t_end, z, C="SeBa", plot=False):
    if "SeBa" not in C:
        x_label = "T [K]"
        y_label = "L [L$_\odot$]"
        figure = plt.figure()
        ax = figure.add_subplot(1, 1, 1)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(1.0e5, 1.0e3)
        ax.set_ylim(1.0e-4, 1.0e4)
        filename = "Stellar_" + "SeBa" + ".amuse"
        plot_hrd(filename, ax)
        filename = "Stellar_" + C + ".amuse"
        plot_hrd(filename, ax)
        plt.savefig("HRD_N3000at4500Myr")
    elif not plot:
        numpy.random.seed(1)
        masses = new_salpeter_mass_distribution(N)
        stars = Particles(mass=masses)
        get_stellar_temperature_and_luminosity(stars, C=C, z=z, t_end=t_end, write=True)
    else:
        x_label = "T [K]"
        y_label = "L [L$_\odot$]"
        figure = plt.figure()
        ax = figure.add_subplot(1, 1, 1)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(1.0e5, 1.0e3)
        ax.set_ylim(1.0e-4, 1.0e4)
        filename = "Stellar_" + C + ".amuse"
        plot_hrd(filename, ax)
        plt.savefig("HRD_N3000at4500Myr.pdf")


def new_argument_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-C", default="SeBa", help="stellar evolution code"
    )
    parser.add_argument(
        "-N", type=int, default=3000, help="number of stars"
    )
    parser.add_argument(
        "-t",
        "--time_end",
        type=units.Myr,
        default=4500.0 | units.Myr,
        help="end time of the simulation",
    )
    parser.add_argument(
        "-z", type=float, default=0.02, help="metalicity"
    )
    parser.add_argument(
        "-p", "--plot", action="store_true", default=False, help="plot"
    )
    return parser


def main()
    args = new_argument_parser().parse_args()
    stellar_isochrone(**args.__dict__)


if __name__ == "__main__":
    main()
