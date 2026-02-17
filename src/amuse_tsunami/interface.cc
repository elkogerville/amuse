#include <cstddef>
#include <iostream>

#include "tsunami_worker.h"

// AMUSE STOPPING CONDITIONS SUPPORT
#include <stopcond.h>
#include <time.h>
#include <vector>

#include "chain.hpp"
#include "custom_types.hpp"
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

    size_t N_existing = Tsunami.System.Nparts;
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
