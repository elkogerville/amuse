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
std::vector<ParticleData> particle_storage;


/**
 * Define a new particle in the stellar dynamics code. The particle is
 * initialized with the provided mass, radius, position and velocity.
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
    long stype,
) {
    if (!index_of_the_particle) return -1;

    ParticleData p;
    p.mass = mass;
    p.pos[0] = x;
    p.pos[1] = y;
    p.pos[2] = z;
    p.vel[0] = vx;
    p.vel[1] = vy;
    p.vel[2] = vz;
    p.radius = radius;
    p.spin[0] = wx;
    p.spin[1] = wy;
    p.spin[2] = wz;
    p.stype = static_cast<long>(stype);

    particle_buffer.push_back(p);
    *index_of_the_particle = particle_id_counter;
    particle_id_counter++;
    return 0;
}

/**
 * Insert the particles from the buffer into the
 */
int buffer_to_particle_storage() {
    particle_storage.insert(
        particle_storage.end(),
        particle_buffer.begin(),
        particle_buffer.end()
    );
    particle_buffer.clear();
}

int commit_particles() {

    size_t N = particle_storage.size();

    std::vector<double> pos(3*N);
    std::vector<double> vel(3*N);
    std::vector<double> mass(N);
    std::vector<double> radius(N);
    std::vector<long> stype(N);

    for (size_t n = 0; n < N; n++) {
        pos[3*n]   = particle_storage[n].pos[0];
        pos[3*n+1] = particle_storage[n].pos[1];
        pos[3*n+2] = particle_storage[n].pos[2];

        vel[3*n]   = particle_storage[n].vel[0];
        vel[3*n+1] = particle_storage[n].vel[1];
        vel[3*n+2] = particle_storage[n].vel[2];

        mass[n] = particle_storage[n].mass;
        radius[n] = particle_storage[n].radius;
        stype[n] = particle_storage[n].stype;
    }

    Tsunami.add_particle_set(
        pos.data(), N, 3,
        vel.data(), N, 3,
        mass.data(), N,
        radius.data(), N,
        stype.data(), N
    );

    return 0;
}
