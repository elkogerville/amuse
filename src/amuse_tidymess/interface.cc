#include "tidymess_worker.h"
#include <cstddef>
#include <iostream>

// AMUSE STOPPING CONDITIONS SUPPORT
#include <stopcond.h>
#include <time.h>

#include "Timer.h"
#include "Banner.h"

#include "Initializer.h"
#include "Output.h"

#include "Tidy.h"

#include "Collision.h"
#include "Breakup.h"

static Tidy tidymess;
static Initializer init;
static Collision collision;
static Breakup breakup;

static int particle_id_counter = 0;
static double begin_time = 0;
static int init_shape = 0;
static int dt_sign = 1;

// TIDYMESS HELPER FUNCTIONS

/**
 * Given an AMUSE particle index, find the corresponding
 * index of that particle within Tidymess.
 *
 * @param index_of_the_particle Particle identifier
 */
int get_body_index_by_id(int index_of_the_particle) {
    const std::vector<Body>& bodies = tidymess.bodies;

    for (size_t i = 0; i < bodies.size(); i++) {
        if (bodies[i].id == index_of_the_particle) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

/**
 * Determine sign of dt value
 * for integrating foward or backwards
 * in time. copied from tidymess.cpp
 */
int determine_dt_sgn(double t_end) {
    bool dt_pos;

    if(t_end > tidymess.get_model_time()) {  // ** takes negative time step when evolving to 0, causes problems
        dt_pos = true;
        dt_sign = 1;
    }
    else {
        dt_pos = false;
        dt_sign = -1;
    }
    tidymess.set_dt_sgn(dt_sign);
    return 0;
}

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
    double xi,
    double kf,
    double tau,
    double wx,
    double wy,
    double wz,
    double a_mb
) {
    if (!index_of_the_particle) return -1;

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

/**
 * Delete a particle inside Tidymess
 */
int delete_particle(int index_of_the_particle) {
    std::vector<Body>& bodies = tidymess.bodies;
    int i = get_body_index_by_id(index_of_the_particle);

    if (i < 0) return -1;

    bodies.erase(bodies.begin() + i);

    return 0;
}

// Tidymess setters and getters

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
    double* xi,
    double* kf,
    double* tau,
    double* wx,
    double* wy,
    double* wz,
    double* a_mb
) {
    if (!mass || !x || !y || !z || !vx || !vy || !vz ||
        !radius || !xi || !kf || !tau || !wx || !wy ||
        !wz || !a_mb)
    {
        return -1;
    }

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    const Body& body = tidymess.bodies[i];

    *mass = body.m;
    *x = body.r[0];
    *y = body.r[1];
    *z = body.r[2];
    *vx = body.v[0];
    *vy = body.v[1];
    *vz = body.v[2];
    *radius = body.R;
    *xi = body.xi;
    *kf = body.kf;
    *tau = body.tau;
    *wx = body.w[0];
    *wy = body.w[1];
    *wz = body.w[2];
    *a_mb = body.a_mb;

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
    double xi,
    double kf,
    double tau,
    double wx,
    double wy,
    double wz,
    double a_mb
) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    Body& body = tidymess.bodies[i];

    body.m = mass;
    body.R = radius;
    body.r = {x, y, z};
    body.v = {vx, vy, vz};
    body.xi = xi;
    body.kf = kf;
    body.tau = tau;
    body.w = {wx, wy, wz};
    body.a_mb = a_mb;

    return 0;
}

/**
 * Get mass of a particle
 */
int get_mass(int index_of_the_particle, double* mass) {
    if (!mass) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    *mass = tidymess.bodies[i].m;
    return 0;
}
/**
 * Set mass of a particle
 */
int set_mass(int index_of_the_particle, double mass) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    tidymess.bodies[i].m = mass;
    return 0;
}

/**
 * Get radius of a particle
 */
int get_radius(int index_of_the_particle, double* radius ) {
    if (!radius) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    *radius = tidymess.bodies[i].R;
    return 0;
}
/**
 * Set radius of a particle
 */
int set_radius(int index_of_the_particle, double radius) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    tidymess.bodies[i].R = radius;
    return 0;
}

/**
 * Get position of a particle
 */
int get_position(
    int index_of_the_particle,
    double* x,
    double* y,
    double* z
) {
    if (!x || !y || !z) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    const Body& body = tidymess.bodies[i];

    *x = body.r[0];
    *y = body.r[1];
    *z = body.r[2];
    return 0;
}
/**
 * Set position of a particle
 */
int set_position(
    int index_of_the_particle,
    double x,
    double y,
    double z
) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    Body& body = tidymess.bodies[i];

    body.r = {x, y, z};
    return 0;
}

/**
 * Get velocity of a particle
 */
int get_velocity(
    int index_of_the_particle,
    double* vx,
    double* vy,
    double* vz
) {
    if (!vx || !vy || !vz) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    const Body& body = tidymess.bodies[i];

    *vx = body.v[0];
    *vy = body.v[1];
    *vz = body.v[2];
    return 0;
}
/**
 * Set velocity of a particle
 */
int set_velocity(
    int index_of_the_particle,
    double vx,
    double vy,
    double vz
) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    Body& body = tidymess.bodies[i];

    body.v = {vx, vy, vz};
    return 0;
}

/**
 * Get moment of inertia of a particle
 */
int get_xi(int index_of_the_particle, double* xi) {
    if (!xi) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    *xi = tidymess.bodies[i].xi;
    return 0;
}
/**
 * Set moment of inertia of a particle
 */
int set_xi(int index_of_the_particle, double xi) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    tidymess.bodies[i].xi = xi;
    return 0;
}

/**
 * Get fluid love number of a particle
 */
int get_kf(int index_of_the_particle, double* kf) {
    if (!kf) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    *kf = tidymess.bodies[i].kf;
    return 0;
}
/**
 * Set fluid love number of a particle
 */
int set_kf(int index_of_the_particle, double kf) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    tidymess.bodies[i].kf = kf;
    return 0;
}

/**
 * Get fluid relaxation time of a particle
 */
int get_tau(int index_of_the_particle, double* tau) {
    if (!tau) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    *tau = tidymess.bodies[i].tau;
    return 0;
}
/**
 * Set fluid relaxation time of a particle
 */
int set_tau(int index_of_the_particle, double tau) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    tidymess.bodies[i].tau = tau;
    return 0;
}

/**
 * Get spin of a particle
 */
int get_spin(
    int index_of_the_particle,
    double* wx,
    double* wy,
    double* wz
) {
    if (!wx || !wy || !wz) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    const Body& body = tidymess.bodies[i];

    *wx = body.w[0];
    *wy = body.w[1];
    *wz = body.w[2];
    return 0;
}
/**
 * Set spin of a particle
 */
int set_spin(
    int index_of_the_particle,
    double wx,
    double wy,
    double wz
) {
    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    Body& body = tidymess.bodies[i];

    body.w = {wx, wy, wz};

    return 0;
}

/**
 * FIXME
 */
int get_acceleration(
    int index_of_the_particle,
    double* ax,
    double* ay,
    double* az
) {
    if (!ax || !ay || !az) return -1;
    return 0;
}

/**
 * FIXME
 */
int get_potential(int index_of_the_particle, double* potential) {
    if (!potential) return -1;
    return 0;
}

int evolve_model(double time) {
    // Evolve the model until the given time, or until a stopping condition is set.

     // has to be called sometime before evolving
    //tidymess.set_dt_sgn(dt_sign);
    determine_dt_sgn(time);

    tidymess.evolve_model(time);
    return 0;
}

/**
 * Get Tidymess tidal model parameter
 */
int get_tidal_model(int* tidal_model) {
    if (!tidal_model) return -1;

    *tidal_model = tidymess.get_tidal_model();
    return 0;
}
/**
 * Set Tidymess tidal model parameter
 */
int set_tidal_model(int tidal_model) {
    tidymess.set_tidal_model(tidal_model);
    return 0;
}

/**
 * Get Tidymess pn order parameter
 */
int get_pn_order(int* pn_order) {
    if (!pn_order) return -1;

    *pn_order = tidymess.get_pn_order();
    return 0;
}
/**
 * Set Tidymess pn order parameter
 */
int set_pn_order(int pn_order) {
    tidymess.set_pn_order(pn_order);
    return 0;
}

/**
 * Get Tidymess magnetic braking paramter
 */
int get_magnetic_braking(int* magnetic_braking) {
    if (!magnetic_braking) return -1;

    *magnetic_braking = tidymess.get_magnetic_braking();
    return 0;
}
/**
 * Set Tidymess magnetic braking parameter
 */
int set_magnetic_braking(int magnetic_braking) {
    tidymess.set_magnetic_braking(magnetic_braking);
    return 0;
}

/**
 * Get Tidymess speed of light parameter
 */
int get_speed_of_light(double* speed_of_light) {
    if (!speed_of_light) return -1;

    *speed_of_light = tidymess.get_speed_of_light();
    return 0;
}
/**
 * Set Tidymess speed of light parameter
 */
int set_speed_of_light(double speed_of_light) {
    tidymess.set_speed_of_light(speed_of_light);
    return 0;
}

/**
 * Get Tidymess dt mode parameter
 */
int get_dt_mode(int* dt_mode) {
    if (!dt_mode) return -1;

    *dt_mode = tidymess.get_dt_mode();
    return 0;
}
/**
 * Set Tidymess dt mode parameter
 */
int set_dt_mode(int dt_mode) {
    tidymess.set_dt_mode(dt_mode);
    return 0;
}

/**
 * Get Tidymess constant dt parameter
 */
int get_dt_const(double* dt_const) {
    if (!dt_const) return -1;

    *dt_const = tidymess.get_dt_const();
    return 0;
}
/**
 * Set Tidymess constant dt parameter
 */
int set_dt_const(double dt_const) {
    tidymess.set_dt_const(dt_const);
    return 0;
}

/**
 * Get internal integrator dt value of previous timestep
 */
int get_time_step(double* time_step) {
    if (!time_step) return -1;

    if (tidymess.get_dt_mode() > 0) {
        *time_step = tidymess.get_dt_prev();
    }
    else {
        *time_step = tidymess.get_dt_const();
    }

    return 0;
}

/**
 * Get Tidymess eta (accuracy parameter)
 */
int get_eta(double* eta) {
    if (!eta) return -1;

    *eta = tidymess.get_eta();
    return 0;
}
/**
 * Set Tidymess eta (accuracy parameter)
 */
int set_eta(double eta) {
    tidymess.set_eta(eta);
    return 0;
}

/**
 * Get Tidymess n iter parameter
 */
int get_n_iter(int* n_iter) {
    if (!n_iter) return -1;

    *n_iter = tidymess.n_iter;
    return 0;
}
/**
 * Set Tidymess n iter parameter
 */
int set_n_iter(int n_iter) {
    tidymess.n_iter = n_iter;
    return 0;
}

/**
 * Get Tidymess initial shape parameter
 */
int get_initial_shape(int* initial_shape) {
    if (!initial_shape) return -1;

    *initial_shape = init_shape;
    return 0;
}
/**
 * Set Tidymess initial shape parameter
 */
int set_initial_shape(int initial_shape) {
    init_shape = initial_shape;
    return 0;
}

// FIX
int get_collision_mode(int* collision_mode) {
    if (!collision_mode) return -1;

    if (tidymess.get_collision_mode() != collision.collision_mode)
        return -1;

    *collision_mode = tidymess.get_collision_mode();

    // maybe check if Tidy and Collision have the same value set
    return 0;
}
int set_collision_mode(int collision_mode) {
    tidymess.set_collision_mode(collision_mode);
    collision.set_collision_mode(collision_mode);
    collision.setup();
    return 0;
}

int get_roche_mode(int* roche_mode) {
    if (!roche_mode) return -1;

    *roche_mode = collision.roche_mode; // doesn't appear in Tidy
    return 0;
}
int set_roche_mode(int roche_mode) {
    tidymess.set_roche_mode(roche_mode);
    collision.set_roche_mode(roche_mode); // doesn't appear in Tidy
    collision.setup();
    return 0;
}

int get_breakup_mode(int* breakup_mode) {
    if (!breakup_mode) return -1;
    *breakup_mode = breakup.mode; /// niet in Tidy
    return 0;
}
int set_breakup_mode(int breakup_mode) {
    breakup.set_breakup_mode(breakup_mode);
    breakup.setup();
    return 0;
}

int get_num_integration_step(int* num_integration_step) {
    if (!num_integration_step) return -1;

    *num_integration_step = tidymess.get_num_integration_step();
    return 0;
}

int initialize_code(){
    //
    // Run the initialization for the code, called before
    // any other call on the code (so before any parameters
    // are set or particles are defined in the code).
    // """

    //initialize_stopping_conditions();

    // AMUSE STOPPING CONDITIONS SUPPORT
    //set_support_for_condition(COLLISION_DETECTION);
    // reset id counter?
    //particle_id_counter = 0;

    return 0;}

int cleanup_code() {
    // FIXME
    // Run the cleanup for the code, called
    // just before stopping the code. No functions
    // should be called after this code.
    //
    return 0;
}

/**
 * Perform initialization in the code dependent on the
 * values of the parameters.Called after the parameters
 * have been set or updated.
 */
int commit_parameters() {
    //tidymess.commit_parameters();
    return 0;
}

int recommit_parameters() {
    // """
    // Perform initialization actions after parameters
    // have been updated (after commit_parameters and
    // particles have been loaded).
    // """
    return 0;
}

int commit_particles() {
    if (tidymess.get_tidal_model() > 0) {
        switch(init_shape) {
            case 0:
                tidymess.set_to_spherical_shape();
                break;
            case 1:
                tidymess.set_to_equilibrium_shape();
                break;
            default:
                return -1;
        }
        tidymess.update_angular_momentum();
    }

    tidymess.commit_parameters();
    return 0;
}

int recommit_particles() {
    return 0;
}

int get_eps2(double* epsilon_squared) {
    if (!epsilon_squared) return -1;
    return 0;
}
int set_eps2(double epsilon_squared) {
    return 0;
}

int get_kinetic_energy(double* kinetic_energy) {
    if (!kinetic_energy) return -1;
    return 0;
}

/**
 * Get potential energy
 */
int get_potential_energy(double* potential_energy) {
    if (!potential_energy) return -1;
    *potential_energy = tidymess.get_potential_energy();
    return 0;
}

/**
 * Get current Tidymess model time
 */
int get_time(double* time) {
    if (!time) return -1;
    *time = tidymess.get_model_time();
    return 0;
}


int get_begin_time(double* time) {
    if (!time) return -1;
    *time = begin_time;
    return 0;
}
int set_begin_time(double time) {
    begin_time = time;
    return 0;
}

/**
 * Get total mass of all particles in Tidymess
 */
int get_total_mass(double* mass) {
    if (!mass) return -1;

    const std::vector<Body>& bodies = tidymess.bodies;
    double total = 0.0;

    for (size_t i = 0; i < bodies.size(); i++)  {
        total += bodies[i].m;
    }

    *mass = total;
    return 0;
}

/**
 * Get position center of mass of all particles
 */
int get_center_of_mass_position(
    double* x,
    double* y,
    double* z
) {
    if (!x || !y || !z) {
        return -1;
    }
    const array<double, 3> position = tidymess.get_center_of_mass();

    *x = position[0];
    *y = position[1];
    *z = position[2];
    return 0;
}

/**
 * Get velocity center of mass of all particles
 */
int get_center_of_mass_velocity(
    double* vx,
    double* vy,
    double* vz
) {
    if (!vx || !vy || !vz) {
        return -1;
    }

    const array<double, 3> velocity = tidymess.get_center_of_mass_velocity();

    *vx = velocity[0];
    *vy = velocity[1];
    *vz = velocity[2];
    return 0;
}

/**
 * Get the radius of a sphere centered around
 * the center of mass of all particles that contains
 * every particle within Tidymess
 */
int get_total_radius(double* radius) {
    if (!radius) return -1;

    const std::vector<Body>& bodies = tidymess.bodies;
    double xcom, ycom, zcom;
    double rsq_max = 0.0;

    if (get_center_of_mass_position(&xcom, &ycom, &zcom) != 0)
        return -1;

    for (size_t i = 0; i < bodies.size(); i++) {
        // compute distance between particle and COM

        const Body& body = bodies[i];

        double dx = body.r[0] - xcom;
        double dy = body.r[1] - ycom;
        double dz = body.r[2] - zcom;

        double r_sq = dx*dx + dy*dy + dz*dz;
        if (rsq_max < r_sq)
            rsq_max = r_sq;
    }

    *radius = std::sqrt(rsq_max);
    return 0;
}

/**
 * Get total number of particles within Tidymess
 */
int get_number_of_particles(int* number_of_particles) {
    if (!number_of_particles) return -1;

    const std::vector<Body>& bodies = tidymess.bodies;

    *number_of_particles = static_cast<int>(bodies.size());
    return 0;
}

/**
 * Get the index of the first inside of Tidymess
 */
int get_index_of_first_particle(int* index_of_the_particle) {
    if (!index_of_the_particle) return -1;

    const std::vector<Body>& bodies = tidymess.bodies;
    if (bodies.empty()) return -1;

    *index_of_the_particle = bodies[0].id;
    return 0;
}

/**
 * Get the index of the next particle given an index
 */
int get_index_of_next_particle(
    int index_of_the_particle,
    int* index_of_the_next_particle
) {
    if (!index_of_the_next_particle) return -1;

    int i = get_body_index_by_id(index_of_the_particle);
    if (i < 0) return -1;

    const std::vector<Body>& bodies = tidymess.bodies;
    if (static_cast<size_t>(i + 1) >= bodies.size()) return -1;

    *index_of_the_next_particle = bodies[i + 1].id;
    return 0;
}

int get_potential_at_point(
    double* eps,
    double* x,
    double* y,
    double* z,
    double* phi,
    int npoints
) {
    /***
     * FIX
     */
    for (int i = 0; i < npoints; i++) {
        phi[i] = 0.0;
    }
    return 0;
}

int get_gravity_at_point(
    double* eps,
    double* x,
    double* y,
    double* z,
    double* ax,
    double* ay,
    double* az,
    int npoints
) {
    /***
     * FIX
     */
    for (int i = 0; i < npoints; i++) {
        ax[i] = 0.0;
        ay[i] = 0.0;
        az[i] = 0.0;
    }
    return 0;
}

/**
 * Convert spin vector {length of day, obliquity, spin precession angle}
 * to spin vector {wx, wy, wz}. Logic copied from Tidymess
 * Initializer::convert_spin_vectors_to_inertial()
 */
int convert_spin_vectors_to_inertial(
    double P,
    double obl,
    double psi,
    double* wx,
    double* wy,
    double* wz
) {
    if (!wx || !wy || !wz)
        return -1;

    if(P == 0) {
        *wx = 0.0;
        *wy = 0.0;
        *wz = 0.0;
    }
    else if (P < 0) {
        return -2;
    }
    else {
        double wmag = 2*M_PI/P;

        std::vector<double> w_vec(3);
        w_vec[0] = 0;
        w_vec[1] = 0;
        w_vec[2] = wmag;

        w_vec = init.rotZrotX(psi, obl, w_vec);

        *wx = w_vec[0];
        *wy = w_vec[1];
        *wz = w_vec[2];
    }
    return 0;
}

int synchronize_model() {
    return 0;
}

// FIXME
int detect_collision(
    int* collision_flag,
    int* n_collisions,
    int* index1,
    int* index2
) {
    // Collision handling
    *collision_flag = tidymess.get_collision_flag();
    std::vector< array<int, 2> > collided_indices = tidymess.get_collision_indices();
    *n_collisions = collided_indices.size();
    *index1 = 0;
    *index2 = 0;

    if (collided_indices.size() > 0) {
        array<int, 2> collided_index = collided_indices[0];
        *index1 = collided_index[0];
        *index2 = collided_index[1];
    }

    return 0;
}
