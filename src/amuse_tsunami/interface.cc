#include <tuple>
#include <cstddef>
#include <iostream>
#include <array>

#include "tsunami_worker.h"

// AMUSE STOPPING CONDITIONS SUPPORT
#include <stopcond.h>
#include <time.h>
#include <vector>

#include "chain.hpp"
#include "custom_types.hpp"
#include "errhand.hpp"
#include "tsunami.hpp"

static TsunamiCode Tsunami;

int particle_id_counter = 0;

struct ParticleData {
    double mass;
    double pos[3];
    double vel[3];
    double radius;
    double spin[3];
    long stype;
};
std::vector<ParticleData> particle_buffer;


/**
 * Check that the index_of_the_particle points to
 * an actual particle inside of Tsunami
 */
inline bool index_in_bounds(int index_of_the_particle)
{
    const ChainSys& system = Tsunami.System;

    return index_of_the_particle >= 0 &&
           index_of_the_particle < static_cast<int>(system.Npart);
}


/**
 * Define a new particle within Tsunami, initialized with the
 * provided mass, radius, position, velocity, spin, and particle type.
 * The particle type at the moment does nothing and is just 0 of type double.
 * In the future, it seems stype could be used to specify a particle as a
 * specific astronomical object, however this has not been implemented yet.
 * This function returns an index that can be used to refer to this particle.
 */
int new_particle(
    int* index_of_the_particle,
    double mass,
    double x,
    double y,
    double z,
    double vx,
    double vy,
    double vz,
    double radius,
    double wx,
    double wy,
    double wz,
    long stype
) {
    if (!index_of_the_particle) return -1;

    ParticleData p = {
        mass,
        {x, y, z},
        {vx, vy, vz},
        radius,
        {wx, wy, wz},
        stype
    };

    particle_buffer.push_back(p);
    *index_of_the_particle = particle_id_counter;
    particle_id_counter++;
    return 0;
}


/**
 * Commits all new particles into Tsunami
 *
 * Pre-existing particles along any new particles added to
 * the buffer are copied into a set of arrays and passed to
 * Tsunami.add_particle_set which reallocates all the arrays
 * within Tsunami and copies the particles over.
 */
int commit_particles() {

    size_t N_existing = Tsunami.System.Npart;
    size_t N_new = particle_buffer.size();
    size_t N_total = N_existing + N_new;

    // no new particles
    if (N_new == 0)
        return 0;
    // not enough particles to commit
    if (N_total < 2)
        return -1;

    // preallocate vectors
    std::vector<double> pos(3 * N_total);
    std::vector<double> vel(3 * N_total);
    std::vector<double> spin(3 * N_total);
    std::vector<double> mass(N_total);
    std::vector<double> radius(N_total);
    std::vector<long> stype(N_total);

    for (size_t i = 0; i < N_existing; i++) {
        pos[3*i] = Tsunami.System.pos[i].x;
        pos[3*i + 1] = Tsunami.System.pos[i].y;
        pos[3*i + 2] = Tsunami.System.pos[i].z;

        vel[3*i] = Tsunami.System.vel[i].x;
        vel[3*i + 1] = Tsunami.System.vel[i].y;
        vel[3*i + 2] = Tsunami.System.vel[i].z;

        spin[3*i] = Tsunami.System.spin[i][0];
        spin[3*i + 1] = Tsunami.System.spin[i][1];
        spin[3*i + 2] = Tsunami.System.spin[i][2];

        mass[i] = Tsunami.System.mass[i];
        radius[i] = Tsunami.System.radius[i];
        stype[i] = static_cast<long>(Tsunami.System.xdata[i].stype);

    }
    for (size_t i = 0; i < N_new; i++) {
        size_t idx = N_existing + i;
        const ParticleData& p = particle_buffer[i];

        pos[3*idx] = p.pos[0];
        pos[3*idx + 1] = p.pos[1];
        pos[3*idx + 2] = p.pos[2];

        vel[3*idx] = p.vel[0];
        vel[3*idx + 1] = p.vel[1];
        vel[3*idx + 2] = p.vel[2];

        spin[3*idx] = p.spin[0];
        spin[3*idx + 1] = p.spin[1];
        spin[3*idx + 2] = p.spin[2];

        mass[idx] = p.mass;
        radius[idx] = p.radius;
        stype[idx] = p.stype;
    }

    Tsunami.add_particle_set(
        pos.data(), N_total, 3,
        vel.data(), N_total, 3,
        mass.data(), N_total,
        radius.data(), N_total,
        stype.data(), N_total,
        spin.data(), N_total, 3
    );
    // clear particle buffer
    particle_buffer.clear();

    return 0;
}

/**
 * Get state of a particle
 */
int get_state(
    int index_of_the_particle,
    double* mass,
    double* x,
    double* y,
    double* z,
    double* vx,
    double* vy,
    double* vz,
    double* radius,
    double* wx,
    double* wy,
    double* wz,
    long* stype
) {
    if (!mass || !x || !y || !z || !vx || !vy || !vz ||
        !radius || !wx || !wy || !wz || !stype) return -1;

    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    *x = system.pos[index_of_the_particle].x;
    *y = system.pos[index_of_the_particle].y;
    *z = system.pos[index_of_the_particle].z;

    *vx = system.vel[index_of_the_particle].x;
    *vy = system.vel[index_of_the_particle].y;
    *vz = system.vel[index_of_the_particle].z;

    *wx = system.spin[index_of_the_particle][0];
    *wy = system.spin[index_of_the_particle][1];
    *wz = system.spin[index_of_the_particle][2];

    *mass = system.mass[index_of_the_particle];
    *radius = system.radius[index_of_the_particle];
    *stype = static_cast<long>(system.xdata[index_of_the_particle].stype);

    return 0;
}
/**
 * Set state of a particle
 */
int set_state(
    int index_of_the_particle,
    double mass,
    double x,
    double y,
    double z,
    double vx,
    double vy,
    double vz,
    double radius,
    double wx,
    double wy,
    double wz,
    long stype
) {
    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    system.pos[index_of_the_particle].x = x;
    system.pos[index_of_the_particle].y = y;
    system.pos[index_of_the_particle].z = z;

    system.vel[index_of_the_particle].x = x;
    system.vel[index_of_the_particle].y = y;
    system.vel[index_of_the_particle].z = z;

    system.spin[index_of_the_particle][0] = wx;
    system.spin[index_of_the_particle][1] = wy;
    system.spin[index_of_the_particle][2] = wz;

    system.mass[index_of_the_particle] = mass;
    system.radius[index_of_the_particle] = radius;
    system.xdata[index_of_the_particle].stype = static_cast<ptype>(stype);

    return 0;
}

/**
 * Get mass of a particle
 */
int get_mass(int index_of_the_particle, double* mass) {
    if (!mass) return -1;

    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    *mass = system.mass[index_of_the_particle];

    return 0;
}
/**
 * Set mass of a particle
 */
int set_mass(int index_of_the_particle, double mass) {
    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    system.mass[index_of_the_particle] = mass;

    return 0;
}

/**
 * Get radius of a particle
 */
int get_radius(int index_of_the_particle, double* radius) {
    if (!radius) return -1;

    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    *radius = system.radius[index_of_the_particle];

    return 0;
}
/**
 * Set radius of a particle
 */
int set_radius(int index_of_the_particle, double radius) {
    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    system.radius[index_of_the_particle] = radius;

    return 0;
}

/**
 * Get position of a particle
 */
int get_position(int index_of_the_particle, double* x, double* y, double* z) {
    if (!x || !y || !z) return -1;

    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    *x = system.pos[index_of_the_particle].x;
    *y = system.pos[index_of_the_particle].y;
    *z = system.pos[index_of_the_particle].z;

    return 0;
}
/**
 * Set position of a particle
 */
int set_position(int index_of_the_particle, double x, double y, double z) {
    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    system.pos[index_of_the_particle].x = x;
    system.pos[index_of_the_particle].y = y;
    system.pos[index_of_the_particle].z = z;

    return 0;
}

/**
 * Get velocity of a particle
 */
int get_velocity(int index_of_the_particle, double* vx, double* vy, double* vz) {
    if (!vx || !vy || !vz) return -1;

    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    *vx = system.vel[index_of_the_particle].x;
    *vy = system.vel[index_of_the_particle].y;
    *vz = system.vel[index_of_the_particle].z;

    return 0;
}
/**
 * Set velocity of a particle
 */
int set_velocity(int index_of_the_particle, double vx, double vy, double vz) {
    ChainSys& system = Tsunami.System;

    if (!index_in_bounds(index_of_the_particle))
        return -1;

    system.vel[index_of_the_particle].x = vx;
    system.vel[index_of_the_particle].y = vy;
    system.vel[index_of_the_particle].z = vz;

    return 0;
}

/**
 * Compute the acceleration onto a particle due to the
 * gravitational influence from all other particles
 */
int get_acceleration(
    int index_of_the_particle,
    double *ax,
    double *ay,
    double *az
) {
    ChainSys& system = Tsunami.System;
    int i = index_of_the_particle;

    double ax_i = 0.0;
    double ay_i = 0.0;
    double az_i = 0.0;

    for (size_t j = i; j < system.Npart; j++) {
        if (i == j) continue;
        std::tuple<std::array<double,3>, std::array<double,3>> accel_pair =
            Tsunami.get_accelerations_of_particles(i, j);

    const std::array<double,3>& acc_i = std::get<0>(accel_pair);

    ax_1 += acc_i[0];
    ay_1 += acc_i[1];
    az_1 += acc_i[2];
    }

    *ax = ax_i;
    *ay = ay_i;
    *az = az_i;

    return 0;
}

/**
 * Set Tsunami code units
 */
int set_units(double Mscale, double Lscale) {

    Tsunami.set_units(Mscale, Lscale);
    return 0;
}

/**
 * Get post-Newtonian correction flag value
 * True enables post-Newtonian corrections
 */
int get_wPNs(bool *wPNs) {
    if (!wPNs) return -1;

    *wPNs = Tsunami.Conf.wPNs;
    return 0;
}
/**
 * Set post-Newtonian correction flag value
 * True enables post-Newtonian corrections
 */
int set_wPNs(bool wPNs) {

    Tsunami.Conf.wPNs = wPNs;
    return 0;
}

/**
 * Get equilibrium tides flag value
 * True enables equilibrium tides
 */
int get_wEqTides(bool *wEqTides) {
    if (!wEqTides) return -1;

    *wEqTides = Tsunami.Conf.wEqTides;
    return 0;
}
/**
 * Set equilibrium tides flag value
 * True enables equilibrium tides
 */
int set_wEqTides(bool wEqTides) {

    Tsunami.Conf.wEqTides = wEqTides;
    return 0;
}

/**
 * Get external potential flag value
 * True enables external potentials
 */
int get_wExt(bool *wExt) {
    if (!wExt) return -1;

    *wExt = Tsunami.Conf.wExt;
    return 0;
}
/**
 * Set external potential flag value
 * True enables external potentials
 */
int set_wExt(bool wExt) {

    Tsunami.Conf.wExt = wExt;
    return 0;
}

/**
 * get external potential flag value
 * True enables external potentials
 */
int get_wExt_vdep(bool *wExt_vdep) {
    if (!wExt_vdep) return -1;

    *wExt_vdep = Tsunami.Conf.wExt_vdep;
    return 0;
}
/**
 * set external potential flag value
 * True enables external potentials
 */
int set_wExt_vdep(bool wExt_vdep) {

    Tsunami.Conf.wExt_vdep = wExt_vdep;
    return 0;
}

/**
 * get alpha regularization parameter
 */
int get_alpha(double *alpha) {
    if (!alpha) return -1;

    *alpha = Tsunami.Config.alpha;
    return 0;
}
/**
 * set alpha regularization parameter
 */
int set_alpha(double alpha) {

    Tsunami.Config.alpha = alpha;
    return 0;
}

/**
 * get beta regularization parameter
 */
int get_beta(double *beta) {
    if (!beta) return -1;

    *beta = Tsunami.Config.beta
    return 0;
}
/**
 * set beta regularization parameter
 */
int set_beta(double beta) {

    Tsunami.Config.beta = beta;
    return 0;
}

/**
 * get gamma regularization parameter
 */
int get_gamma(double *gamma) {
    if (!gamma) return -1;

    *gamma = Tsunami.Config.gamma
    return 0;
}
/**
 * set gamma regularization parameter
 */
int set_gamma(double gamma) {

    Tsunami.Config.gamma = gamma;
    return 0;
}

/**
 * get multiplying factor for particle radii that is
 * used when checking for collisions. A collision
 * between two particles is registered whenever:
 *     d < d_coll * (R1 +  R2)
 */
int get_dcoll(double *dcoll) {
    if (!dcoll) return -1;

    *dcoll = Tsunami.Config.dcoll
    return 0;
}
/**
 * set multiplying factor for particle radii that is
 * used when checking for collisions. A collision
 * between two particles is registered whenever:
 *     d < d_coll * (R1 +  R2)
 */
int set_dcoll(double dcoll) {

    Tsunami.Config.dcoll = dcoll;
    return 0;
}

/**
 * get pn1 flag value
 * True enables first order post-Newtonian corrections
 */
int get_pn1(double *pn1) {
    if (!pn1) return -1;

    *pn1 = Tsunami.Config.pn1
    return 0;
}
/**
 * set pn1 flag value
 * True enables first order post-Newtonian corrections
 */
int set_pn1(double pn1) {

    Tsunami.Config.pn1 = pn1;
    return 0;
}

/**
 * get pn2 flag value
 * True enables second order post-Newtonian corrections
 */
int get_pn2(double *pn2) {
    if (!pn2) return -1;

    *pn2 = Tsunami.Config.pn2;
    return 0;
}
/**
 * set pn2 flag value
 * True enables second order post-Newtonian corrections
 */
int set_pn2(double pn2) {

    Tsunami.Config.pn2 = pn2;
    return 0;
}

/**
 * get pn2 flag value
 * True enables 2.5 order post-Newtonian corrections
 */
int get_pn25(double *pn25) {
    if (!pn25) return -1;

    *pn25 = Tsunami.Config.pn25;
    return 0;
}
/**
 * set pn25 flag value
 * True enables 2.5 order post-Newtonian corrections
 */
int set_pn25(double pn25) {

    Tsunami.Config.pn25 = pn25;
    return 0;
}

/**
 * get pn3 flag value
 * True enables third order post-Newtonian corrections
 */
int get_pn3(double *pn3) {
    if (!pn3) return -1;

    *pn3 = Tsunami.Config.pn3;
    return 0;
}
/**
 * set pn3 flag value
 * True enables third order post-Newtonian corrections
 */
int set_pn3(double pn3) {

    Tsunami.Config.pn3 = pn3;
    return 0;
}

/**
 * get pn35 flag value
 * True enables 3.5 order post-Newtonian corrections
 */
int get_pn35(double *pn35) {
    if (!pn35) return -1;

    *pn35 = Tsunami.Config.pn35;
    return 0;
}
/**
 * set pn35 flag value
 * True enables 3.5 order post-Newtonian corrections
 */
int set_pn35(double pn35) {

    Tsunami.Config.pn35 = pn35;
    return 0;
}

/**
 * Evolve Tsunami system
 */
int evolve_model(double time) {
    try {
        Tsunami.evolve_system(time);
        return 0;
    } catch (const TsuError& e) { //FIXME
        std::cerr << "evolve_model error: " << e.what() << std::endl;
        return -1;
    }
}

/**
 * Get total kinetic energy of the system
 */
int get_kinetic_energy(double *kinetic_energy) {
    if (!kinetic_energy) return -1;

    *kinetic_energy = Tsunami.kin;
    return 0;
}

/**
 * Get total potential energy of the system
 */
int get_potential_energy(double *potential_energy) {
    if (!potential_energy) return -1;

    *potential_energy = Tsunami.pot;
    return 0;
}

/**
 * Get total energy of the system
 */
int get_total_energy(double *total_energy) {
    if (!total_energy) return -1;

    *total_energy = Tsunami.energy;
    return 0;
}

/**
 * Get current simulation timescale in years
 */
int get_time(double *time) {
    if (!time) return -1;

    *time = Tsunami.Tscale;
    return 0;
}

/**
 * Get total mass of all particles in Tsunami
 */
int get_total_mass(double *mass) {
    if (!mass) return -1;

    ChainSys& system = Tsunami.System;
    double m_total = 0.0;

    for (size_t i = 0; i < system.Npart; i++) {
        m_total += system.mass[i];
    }

    *mass = m_total;
    return 0;
}

/**
 * Get position center of mass of all particles
 */
int get_center_of_mass_position(double *x, double *y, double *z) {
    if (!x || !y || !z) return -1;

    ChainSys& system = Tsunami.System;
    size_t Npart = system.Npart;

    if (Npart == 0) { // FIXME
        *x = 0.0;
        *y = 0.0;
        *z = 0.0;
        return 0;
    }

    double m_total = 0.0;
    double xcom = 0.0;
    double ycom = 0.0;
    double zcom = 0.0;

    for (size_t i = 0; i < Npart; i++) {
        m_total += system.mass[i];
        xcom += system.mass[i] * system.pos[i].x;
        ycom += system.mass[i] * system.pos[i].y;
        zcom += system.mass[i] * system.pos[i].z;
    }

    if (m_total == 0)
        return -1;

    *x = xcom / m_total;
    *y = ycom / m_total;
    *z = zcom / m_total;

    return 0;
}

/**
 * Get velocity center of mass of all particles
 */
int get_center_of_mass_velocity(double *vx, double *vy, double *vz) {
    if (!vx || !vy || !vz) return -1;

    ChainSys& system = Tsunami.System;
    size_t Npart = system.Npart;

    if (Npart == 0) { // FIXME
        *vx = 0.0;
        *vy = 0.0;
        *vz = 0.0;
        return 0;
    }

    double m_total = 0.0;
    double vxcom = 0.0;
    double vycom = 0.0;
    double vzcom = 0.0;

    for (size_t i = 0; i < Npart; i++) {
        m_total += system.mass[i];
        vxcom += system.mass[i] * system.vel[i].x;
        vycom += system.mass[i] * system.vel[i].y;
        vzcom += system.mass[i] * system.vel[i].z;
    }

    if (m_total == 0)
        return -1;

    *vx = vxcom / m_total;
    *vy = vycom / m_total;
    *vz = vzcom / m_total;

    return 0;
}

/**
 * Get the minimum radius of a sphere centered around
 * the center of mass of all particles that contains
 * every particle within Tsunami
 */
int get_total_radius(double *radius) {
    if (!radius) return -1;

    ChainSys& system = Tsunami.System;
    double xcom, ycom, zcom;
    double rsq_max = 0.0;

    // compute the COM
    if (get_center_of_mass_position(&xcom, &ycom, &zcom) != 0)
        return -1;

    for (size_t i = 0; i < system.Npart; i++) {
        // compute distance between particle and COM
        double dx = system.pos[i].x - xcom;
        double dy = system.pos[i].y - ycom;
        double dz = system.pos[i].z - zcom;

        double r_sq = dx*dx + dy*dy + dz*dz;
        if (rsq_max < r_sq)
            rsq_max = r_sq;
    }

    *radius = std::sqrt(rsq_max);
    return 0;
}

/**
 * Get number of particles in Tsunami
 */
int get_number_of_particles(int* number_of_particles) {
    if (!number_of_particles) return -1;

    ChainSys& system = Tsunami.System;

    std::vector<double> pos(3 * N_total) = Tsunami.System.pos;

    *number_of_particles = static_cast<int>(Tsunami.System.Npart);
    return 0;
}

/**
 * Get the index of the first particle
 */
int get_index_of_first_particle(int *index_of_the_particle)
{
    if (!index_of_the_particle)
        return -1;

    ChainSys& system = Tsunami.System;

    if (system.Npart == 0)
        return -1;

    *index_of_the_particle = 0;

    return 0;
}

/**
 * Get the index of the next particle
 * given a particle index
 */
int get_index_of_next_particle(
    int index_of_the_particle,
    int *index_of_the_next_particle
) {
    if (!index_of_the_next_particle)
        return -1;

    ChainSys& system = Tsunami.System;

    int next = index_of_the_particle + 1;

    if (next >= (int)system.Npart)
        return -1;

    *index_of_the_next_particle = next;

    return 0;
}
