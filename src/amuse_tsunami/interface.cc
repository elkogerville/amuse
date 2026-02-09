#include "tsunami_worker.h"
#include <iostream>

// AMUSE STOPPING CONDITIONS SUPPORT
#include <stopcond.h>
#include <time.h>

#include "tsunami.hpp"

static TsunamiCode Tsunami;


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
    int stype,
    double wx,
    double wy,
    double wz,
    double polyt,
    double kaps,
    double inert,
    double taulag,
    double taumigx,
    double taumigy,
    double taumigz,
    double eloss,
    bool haspn,
    bool hastide,
    double sigmadiss,
    double Atide
) {
    if (!index_of_the_particle) return -1;

    std::vector<>

    std::vector<Body>& bodies = tidymess.bodies;

    Body newbody(
        mass, radius, xi, kf, tau, a_mb,
        wx, wy, wz, x, y, z, vx, vy, vz
    );

    newbody.set_id(particle_id_counter);

    *index_of_the_particle = particle_id_counter;
    particle_id_counter++;

    bodies.push_back(newbody);
    return 0;
}
