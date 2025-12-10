#include "tidymess_worker.h"

#include <iostream>

// AMUSE STOPPING CONDITIONS SUPPORT
#include <stopcond.h>
#include <time.h>

using namespace std;

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
static vector<Body> bodies = tidymess.get_particles();

int highest_index = 0;
static double begin_time = 0;


int get_ind_from_index(int index_of_the_particle) {
    // find the position in bodies of the Body with a given index
    vector<Body> bodies = tidymess.get_particles();
    int ind;
    int i;
    for (i=0; i<bodies.size(); i++) {
        if (bodies[i].id == index_of_the_particle) {
            ind = i;
        }
    }
    return ind;}

int set_shapes_and_momenta() {  // copied from tidymess.cpp
    // Set initial shapes and angular momenta
    if(tidymess.get_tidal_model() > 0) {
        switch(init.initial_shape) {
            case 0:
                tidymess.set_to_spherical_shape();
                break;
            case 1:
                tidymess.set_to_equilibrium_shape();
                break;
        }
        tidymess.update_angular_momentum();
    }
    return 0;}

int determine_dt_sgn(double t_end) {  // copied from tidymess.cpp
    bool dt_pos;
    int dt_sgn;
    if(t_end > tidymess.get_model_time()) {   // ** takes negative time step when evolving to 0, causes problems
        dt_pos = true;
        dt_sgn = 1;
    }
    else {
        dt_pos = false;
        dt_sgn = -1;
    }
    tidymess.set_dt_sgn(dt_sgn);
    return 0;}

// tidymess-specific setters & getters

int get_tidal_model(int * tidal_model){
    *tidal_model = tidymess.get_tidal_model();
    return 0;}
int set_tidal_model(int tidal_model){
    tidymess.set_tidal_model(tidal_model);
    set_shapes_and_momenta();
    return 0;}

int get_pn_order(int * pn_order){
    *pn_order = tidymess.get_pn_order();
    return 0;}
int set_pn_order(int pn_order){
    tidymess.set_pn_order(pn_order);
    return 0;}

int get_magnetic_braking(int * magnetic_braking){
    *magnetic_braking = tidymess.get_magnetic_braking();
    return 0;}
int set_magnetic_braking(int magnetic_braking){
    tidymess.set_magnetic_braking(magnetic_braking);
    return 0;}

int get_speed_of_light(double * speed_of_light){
    *speed_of_light = tidymess.get_speed_of_light();
    return 0;}
int set_speed_of_light(double speed_of_light){
    tidymess.set_speed_of_light(speed_of_light);
    return 0;}

int get_dt_mode(int * dt_mode){
    *dt_mode = tidymess.get_dt_mode();
    return 0;}
int set_dt_mode(int dt_mode){
    tidymess.set_dt_mode(dt_mode);
    return 0;}

int get_dt_const(double * dt_const){
    *dt_const = tidymess.get_dt_const();
    return 0;}
int set_dt_const(double dt_const){
    tidymess.set_dt_const(dt_const);
    return 0;}

int get_eta(double * eta){
    *eta = tidymess.get_eta();
    return 0;}
int set_eta(double eta){
    tidymess.set_eta(eta);
    return 0;}

int get_n_iter(int * n_iter){
    *n_iter = tidymess.get_n_iter();
    return 0;}
int set_n_iter(int n_iter){
    tidymess.set_n_iter(n_iter);
    return 0;}

int get_collision_mode(int * collision_mode){
    *collision_mode = tidymess.get_collision_mode();
    // maybe check if Tidy and Collision have the same value set
    return 0;}
int set_collision_mode(int collision_mode){
    tidymess.set_collision_mode(collision_mode);
    collision.set_collision_mode(collision_mode);
    collision.setup();
    return 0;}

int get_roche_mode(int * roche_mode){
    *roche_mode = collision.roche_mode; // doesn't appear in Tidy
    return 0;}
int set_roche_mode(int roche_mode){
    collision.set_roche_mode(roche_mode); // doesn't appear in Tidy
    collision.setup();
    return 0;}

int get_breakup_mode(int * breakup_mode){
    *breakup_mode = breakup.mode; /// niet in Tidy
    return 0;}
int set_breakup_mode(int breakup_mode){
    breakup.set_breakup_mode(breakup_mode);
    breakup.setup();
    return 0;}

int get_num_integration_step(int * num_integration_step) {
    *num_integration_step = tidymess.get_num_integration_step();
    return 0;}


// For CommonCodeInterface
// https://github.com/amusecode/amuse/blob/main/src/amuse/community/interface/common.py

int initialize_code(){
    // """
    // Run the initialization for the code, called before
    // any other call on the code (so before any parameters
    // are set or particles are defined in the code).
    // """

    //initialize_stopping_conditions();

    // AMUSE STOPPING CONDITIONS SUPPORT
    //set_support_for_condition(COLLISION_DETECTION);
    return 0;}

int cleanup_code(){
    // """
    // Run the cleanup for the code, called
    // just before stopping the code. No functions
    // should be called after this code.
    // """
    return 0;}

int commit_parameters(){
    // """
    // Perform initialization in the code dependent on the
    // values of the parameters.
    // Called after the parameters have been set or updated.
    // """
    return 0;}
int recommit_parameters(){
    // """
    // Perform initialization actions after parameters
    // have been updated (after commit_parameters and
    // particles have been loaded).
    // """
    return 0;}


// For GravitationalDynamicsInterface
// https://github.com/amusecode/amuse/blob/main/src/amuse/community/interface/gd.py

int new_particle(int * index_of_the_particle, double mass, double x,
    double y, double z, double vx, double vy, double vz, double radius,
    double xi, double kf, double tau, double wx, double wy, double wz, double a_mb, int id){
    // """
    // Define a new particle in the stellar dynamics code. The particle is
    // initialized with the provided mass, radius, position and velocity. This
    // function returns an index that can be used to refer to this particle.
    // """

    vector<Body> bodies = tidymess.get_particles();

    Body newbody = {mass, radius, xi, kf, tau, a_mb, wx, wy, wz, x, y, z, vx, vy, vz};
    *index_of_the_particle = highest_index;
    newbody.set_id(highest_index);
    highest_index++;

    bodies.push_back(newbody);
    tidymess.set_particles(bodies);

    tidymess.commit_parameters();

    return 0;}

int delete_particle(int index_of_the_particle){
    vector<Body> bodies = tidymess.get_particles();
    int ind = get_ind_from_index(index_of_the_particle);
    bodies.erase(bodies.begin()+ind);
    tidymess.set_particles(bodies);
    return 0;}

// setters & getters

int set_state(int index_of_the_particle, double mass, double x, double y,
    double z, double vx, double vy, double vz, double radius){
    vector<Body> bodies = tidymess.get_particles();
    int ind = get_ind_from_index(index_of_the_particle);
    bodies[ind].m = mass;
    bodies[ind].R = radius;
    bodies[ind].r = {x, y, z};
    bodies[ind].v = {vx, vy, vz};
    tidymess.set_particles(bodies);
    return 0;}
int get_state(int index_of_the_particle, double * mass, double * x,
    double * y, double * z, double * vx, double * vy, double * vz,
    double * radius){
    vector<Body> bodies = tidymess.get_particles();
    Body body = bodies[get_ind_from_index(index_of_the_particle)];
    *mass = body.m;
    *x = body.r[0];
    *y = body.r[1];
    *z = body.r[2];
    *vx = body.v[0];
    *vy = body.v[1];
    *vz = body.v[2];
    *radius = body.R;
    return 0;}

int get_mass(int index_of_the_particle, double * mass){
    vector<Body> bodies = tidymess.get_particles();
    *mass = bodies[get_ind_from_index(index_of_the_particle)].m;
    return 0;}
int set_mass(int index_of_the_particle, double mass){
    vector<Body> bodies = tidymess.get_particles();
    bodies[get_ind_from_index(index_of_the_particle)].m = mass;
    tidymess.set_particles(bodies);
    return 0;}

int get_radius(int index_of_the_particle, double * radius){
    vector<Body> bodies = tidymess.get_particles();
    *radius = bodies[get_ind_from_index(index_of_the_particle)].R;
    return 0;}
int set_radius(int index_of_the_particle, double radius){
    vector<Body> bodies = tidymess.get_particles();
    bodies[get_ind_from_index(index_of_the_particle)].R = radius;
    tidymess.set_particles(bodies);
    return 0;}

int get_position(int index_of_the_particle, double * x, double * y,
    double * z){
    vector<Body> bodies = tidymess.get_particles();
    array<double, 3> position = bodies[get_ind_from_index(index_of_the_particle)].r;
    *x = position[0];
    *y = position[1];
    *z = position[2];
    return 0;}
int set_position(int index_of_the_particle, double x, double y, double z){
    vector<Body> bodies = tidymess.get_particles();
    bodies[get_ind_from_index(index_of_the_particle)].r = {x, y, z};
    tidymess.set_particles(bodies);
    return 0;}

int get_velocity(int index_of_the_particle, double * vx, double * vy,
    double * vz){
    vector<Body> bodies = tidymess.get_particles();
    array<double, 3> velocity = bodies[get_ind_from_index(index_of_the_particle)].v;
    *vx = velocity[0];
    *vy = velocity[1];
    *vz = velocity[2];
    return 0;}
int set_velocity(int index_of_the_particle, double vx, double vy,
    double vz){
    vector<Body> bodies = tidymess.get_particles();
    bodies[get_ind_from_index(index_of_the_particle)].v = {vx, vy, vz};
    tidymess.set_particles(bodies);
    return 0;}

int get_spin(int index_of_the_particle, double * wx, double * wy,
    double * wz){
    vector<Body> bodies = tidymess.get_particles();
    array<double, 3> spin = bodies[get_ind_from_index(index_of_the_particle)].w;
    *wx = spin[0];
    *wy = spin[1];
    *wz = spin[2];
    return 0;}
int set_spin(int index_of_the_particle, double wx, double wy,
    double wz){
    vector<Body> bodies = tidymess.get_particles();
    bodies[get_ind_from_index(index_of_the_particle)].w = {wx, wy, wz};
    tidymess.set_particles(bodies);
    return 0;}

int get_acceleration(int index_of_the_particle, double * ax, double * ay,
    double * az){
    return 0;}
int set_acceleration(int index_of_the_particle, double ax, double ay,
    double az){
    return 0;}

int get_eps2(double * epsilon_squared){
    return 0;}
int set_eps2(double epsilon_squared){
    return 0;}

int get_potential(int index_of_the_particle, double * potential){
    return 0;}

int get_kinetic_energy(double * kinetic_energy){
    return 0;}
int get_potential_energy(double * potential_energy){
    return 0;}

int get_time(double * time){
    *time = tidymess.get_model_time();
    return 0;}

int get_begin_time(double * time){
    *time = begin_time;
    return 0;}
int set_begin_time(double time){
    begin_time = time;
    return 0;}

int get_time_step(double * time_step){
    *time_step = tidymess.get_dt_const();
    if (tidymess.get_dt_mode() > 0) {
        *time_step = tidymess.get_dt_prev();
    }
    return 0;}

int get_total_mass(double * mass){
    vector<Body> bodies = tidymess.get_particles();
    *mass = 0.0;
    for (int i = 0; i< bodies.size(); i++)  {
        *mass += bodies[i].m;
    }
    return 0;}

int get_total_radius(double * radius){
    vector<Body> bodies = tidymess.get_particles();
    *radius = 0.0;
    for (int i = 0; i< bodies.size(); i++)  {
        *radius += bodies[i].R;
    }
    return 0;}

int get_center_of_mass_position(double * x, double * y, double * z){
    array<double, 3> position = tidymess.get_center_of_mass();
    *x = position[0];
    *y = position[1];
    *z = position[2];
    return 0;}
int get_center_of_mass_velocity(double * vx, double * vy, double * vz){
    array<double, 3> velocity = tidymess.get_center_of_mass_velocity();
    *vx = velocity[0];
    *vy = velocity[1];
    *vz = velocity[2];
    return 0;}

int get_number_of_particles(int * number_of_particles){
    vector<Body> bodies = tidymess.get_particles();
    *number_of_particles = bodies.size();
    return 0;}

int get_index_of_first_particle(int * index_of_the_particle){
    Body body =  tidymess.get_particles()[0];
    *index_of_the_particle = body.id;
    return 0;}
int get_index_of_next_particle(int index_of_the_particle,
    int * index_of_the_next_particle){
    vector<Body> bodies = tidymess.get_particles();
    Body body = bodies[get_ind_from_index(index_of_the_particle)+1];
    *index_of_the_next_particle = body.id;
    return 0;}


// evolving

int evolve_model(double time){
    // Evolve the model until the given time, or until a stopping condition is set.

    tidymess.commit_parameters(); // has to be called sometime before evolving
    determine_dt_sgn(time);

    tidymess.evolve_model(time);
    return 0;}

int commit_particles(){
    return 0;}
int recommit_particles(){
    return 0;}

int synchronize_model(){
    return 0;}

int get_potential_at_point(double eps, double x, double y, double z,
    double * phi, int npoints){
    return 0;}

int get_gravity_at_point(double eps, double x, double y, double z,
    double * ax, double * ay, double * az, int npoints){
    return 0;}


// compute spin vector (largely copied from Initializer)
int convert_spin_vectors_to_inertial(double P, double obl, double psi, double * wx, double * wy, double * wz) {

        if(P == 0) {
            *wx = 0.;
            *wy = 0.;
            *wz = 0.;
        }
        else {
            double wmag = 2*M_PI/P;

            vector<double> w_vec(3);
            w_vec[0] = 0;
            w_vec[1] = 0;
            w_vec[2] = wmag;

            w_vec = init.rotZrotX(psi, obl, w_vec);

            *wx = w_vec[0];
            *wy = w_vec[1];
            *wz = w_vec[2];
        }
    return 0;}


// collision detection

int detect_collision(int * collision_flag, int * n_collisions, int * index1, int * index2) {
    // Collision handling
    *collision_flag = tidymess.get_collision_flag();
    vector< array<int, 2> > collided_indices = tidymess.get_collision_indices();
    *n_collisions = collided_indices.size();
    *index1 = 0;
    *index2 = 0;

    if (collided_indices.size() > 0) {
        array<int, 2> collided_index = collided_indices[0];
        *index1 = collided_index[0];
        *index2 = collided_index[1];
    }

    return 0;}

int merge_collided_particles(int * number_of_particles) {
    vector< array<int, 2> > cindex = tidymess.get_collision_indices();
    collision.replace(bodies, cindex);

    tidymess.set_particles(bodies);
    tidymess.commit_particles();

    vector<Body> bodies = tidymess.get_particles();
    *number_of_particles = bodies.size();
    return 0;}
