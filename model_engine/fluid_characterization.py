import math
from utilities.utilities_for_input_processing import annulus_pressure_coefficient


def hydraulic_diameter(hole_size, pipe_od, pipe_id, conduit_type):
    if conduit_type == "pipe":
        return pipe_id
    return hole_size - pipe_od


def pipe_and_annular_velocity_calculator(flow_rate_q,
                                         hole_size,
                                         pipe_od,
                                         pipe_id,
                                         conduit_type):
    if conduit_type == "annular":
        return flow_rate_q / (math.pi / 4 * ((hole_size ** 2) - (pipe_od ** 2)))
    return flow_rate_q / (math.pi / 4 * (pipe_id ** 2))


def geometric_parameter_a_calculator(conduit_type):

    if conduit_type == "pipe":
        return 3/4
    elif conduit_type == "annular":
        return 1


def geometric_parameter_b_calculator(conduit_type):

    if conduit_type == "pipe":
        return 1/4
    elif conduit_type == "annular":
        return 1/2


def generalized_consistency_index_k_prime(wall_shear_stress_tao_w,
                                          yield_power_law_newtonian_shear_rate,
                                          generalized_flow_behavior_index_n):

    return wall_shear_stress_tao_w * (yield_power_law_newtonian_shear_rate ** -generalized_flow_behavior_index_n)


def generalized_reynolds_number(mud_density,
                                fluid_velocity,
                                hole_size,
                                pipe_od,
                                pipe_id,
                                generalized_flow_behavior_index_n,
                                generalized_consistency_index_k_prime,
                                conduit_type):

    d_hyd = hydraulic_diameter(hole_size, pipe_od, pipe_id, conduit_type)
    return mud_density * (fluid_velocity ** (2 - generalized_flow_behavior_index_n)) * (d_hyd ** generalized_flow_behavior_index_n) / ((8 ** (generalized_flow_behavior_index_n - 1)) * generalized_consistency_index_k_prime)


def yield_power_law_newtonian_shear_rate(yield_stress_tao_y,
                                         consistency_index_k,
                                         fluid_behavior_index_m,
                                         wall_shear_stress_tao_w,
                                         conduit_type):

    geometric_parameter_a = geometric_parameter_a_calculator(conduit_type)
    geometric_parameter_b = geometric_parameter_b_calculator(conduit_type)

    term_4 = ((fluid_behavior_index_m - 1) * (2 * fluid_behavior_index_m - 1) * wall_shear_stress_tao_w ** 2 - 2 * (
            2 * fluid_behavior_index_m ** 2 + fluid_behavior_index_m - 1) * wall_shear_stress_tao_w * yield_stress_tao_y + (
                      2 * fluid_behavior_index_m ** 2 + fluid_behavior_index_m + 1) * yield_stress_tao_y ** 2)
    term_3 = ((5 / 6) ** (1 / fluid_behavior_index_m) * ((5 * wall_shear_stress_tao_w + yield_stress_tao_y) / 6) ** (
            geometric_parameter_a / geometric_parameter_b - 1) + (2 / 3) ** (1 / fluid_behavior_index_m) * (
                      (2 * wall_shear_stress_tao_w + yield_stress_tao_y) / 3) ** (
                      geometric_parameter_a / geometric_parameter_b - 1) + 3 ** (-1 / fluid_behavior_index_m) * (
                      (wall_shear_stress_tao_w + 2 * yield_stress_tao_y) / 3) ** (
                      geometric_parameter_a / geometric_parameter_b - 1) + 2 ** (
                      1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m) * (
                      wall_shear_stress_tao_w + yield_stress_tao_y) ** (
                      geometric_parameter_a / geometric_parameter_b - 1) + 6 ** (
                      1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m) * (
                      wall_shear_stress_tao_w + 5 * yield_stress_tao_y) ** (
                      geometric_parameter_a / geometric_parameter_b - 1))
    term_2 = (wall_shear_stress_tao_w ** (geometric_parameter_a / geometric_parameter_b - 1) + 2 * term_3)
    term_1 = (-(2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m) * (
            wall_shear_stress_tao_w + yield_stress_tao_y) ** (
                        geometric_parameter_a / geometric_parameter_b - 3)) * (
                      geometric_parameter_a ** 2 * fluid_behavior_index_m ** 2 * (
                      wall_shear_stress_tao_w - yield_stress_tao_y) ** 2 - geometric_parameter_a * geometric_parameter_b * fluid_behavior_index_m * (
                              wall_shear_stress_tao_w - yield_stress_tao_y) * (
                              (3 * fluid_behavior_index_m - 2) * wall_shear_stress_tao_w - (
                              3 * fluid_behavior_index_m + 2) * yield_stress_tao_y) + geometric_parameter_b ** 2 * term_4) / (
                      geometric_parameter_a ** 2 * fluid_behavior_index_m ** 2) + 9 * term_2)

    return (consistency_index_k * wall_shear_stress_tao_w ** (-geometric_parameter_a / geometric_parameter_b) * (
            (wall_shear_stress_tao_w - yield_stress_tao_y) / consistency_index_k) ** (
                    1 + 1 / fluid_behavior_index_m) * term_1) / (108 * geometric_parameter_b)


def generalized_flow_behavior_index_n(yield_stress_tao_y,
                                      fluid_behavior_index_m,
                                      wall_shear_stress_tao_w,
                                      conduit_type):

    geometric_parameter_a = geometric_parameter_a_calculator(conduit_type)
    geometric_parameter_b = geometric_parameter_b_calculator(conduit_type)

    trap_4 = ((2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) *
              (geometric_parameter_a - 3 * geometric_parameter_b) * ((wall_shear_stress_tao_w + yield_stress_tao_y) **
              (-4 + geometric_parameter_a / geometric_parameter_b)) * ((geometric_parameter_a ** 2) *
              (fluid_behavior_index_m ** 2) * ((wall_shear_stress_tao_w - yield_stress_tao_y) ** 2) -
              geometric_parameter_a * geometric_parameter_b * fluid_behavior_index_m * (wall_shear_stress_tao_w -
              yield_stress_tao_y) * ((-2 + 3 * fluid_behavior_index_m) * wall_shear_stress_tao_w - (2 + 3 *
              fluid_behavior_index_m) * yield_stress_tao_y) + (geometric_parameter_b ** 2) * ((1 - 3 *
              fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * (wall_shear_stress_tao_w ** 2) - 2 * (-1
              + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * wall_shear_stress_tao_w *
              yield_stress_tao_y + (1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) *
              (yield_stress_tao_y ** 2))))
    trap_3 = (-(((2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) *
             ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-3 + geometric_parameter_a / geometric_parameter_b)) *
             ((geometric_parameter_a ** 2) * (fluid_behavior_index_m ** 2) *
             ((wall_shear_stress_tao_w - yield_stress_tao_y) ** 2) - geometric_parameter_a * geometric_parameter_b *
             fluid_behavior_index_m * (wall_shear_stress_tao_w - yield_stress_tao_y) *
             ((-2 + 3 * fluid_behavior_index_m) * wall_shear_stress_tao_w - (2 + 3 * fluid_behavior_index_m) *
             yield_stress_tao_y) + (geometric_parameter_b ** 2) * ((-1 + fluid_behavior_index_m) *
             (-1 + 2 * fluid_behavior_index_m) * (wall_shear_stress_tao_w ** 2) - 2 *
             (-1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * wall_shear_stress_tao_w *
             yield_stress_tao_y + (1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) *
             (yield_stress_tao_y ** 2)))) / ((geometric_parameter_b ** 2) * (fluid_behavior_index_m ** 2))) + 9 *
             ((wall_shear_stress_tao_w ** (-1 + geometric_parameter_a / geometric_parameter_b)) + 2 * (((5 / 6) **
             (1 / fluid_behavior_index_m)) * (((5 * wall_shear_stress_tao_w) / 6 + yield_stress_tao_y / 6) **
             (-1 + geometric_parameter_a / geometric_parameter_b)) + ((2 / 3) ** (1 / fluid_behavior_index_m)) *
             (((2 * wall_shear_stress_tao_w) / 3 + yield_stress_tao_y / 3) **
             ( -1 + geometric_parameter_a / geometric_parameter_b)) + ( (wall_shear_stress_tao_w / 3 +
             (2 * yield_stress_tao_y) / 3) ** (-1 + geometric_parameter_a / geometric_parameter_b)) / (3 **
             (1 / fluid_behavior_index_m)) + (2 **(1 - geometric_parameter_a / geometric_parameter_b - 1 /
             fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + yield_stress_tao_y) **
             (-1 + geometric_parameter_a / geometric_parameter_b)) + (6 **
             (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) *
             ((wall_shear_stress_tao_w + 5 * yield_stress_tao_y) **
             (-1 + geometric_parameter_a / geometric_parameter_b)))))
    trap_5 = ((wall_shear_stress_tao_w ** (-1 + geometric_parameter_a / geometric_parameter_b)) + 2 * (((5 / 6) ** (1 / fluid_behavior_index_m)) * (((5 * wall_shear_stress_tao_w) / 6 + yield_stress_tao_y / 6) ** (-1 + geometric_parameter_a / geometric_parameter_b)) + ((2 / 3) ** (1 / fluid_behavior_index_m)) * (((2 * wall_shear_stress_tao_w) / 3 + yield_stress_tao_y / 3) ** (-1 + geometric_parameter_a / geometric_parameter_b)) + ((wall_shear_stress_tao_w / 3 + (2 * yield_stress_tao_y) / 3) ** (-1 + geometric_parameter_a / geometric_parameter_b)) / (3 **(1 / fluid_behavior_index_m)) + (2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-1 + geometric_parameter_a / geometric_parameter_b)) + (6 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + 5 * yield_stress_tao_y) **(-1 + geometric_parameter_a / geometric_parameter_b))))
    trap_6 = ((geometric_parameter_a ** 2) * (fluid_behavior_index_m ** 2) * ((wall_shear_stress_tao_w - yield_stress_tao_y) ** 2) - geometric_parameter_a * geometric_parameter_b * fluid_behavior_index_m * (wall_shear_stress_tao_w - yield_stress_tao_y) * ((-2 + 3 * fluid_behavior_index_m) * wall_shear_stress_tao_w - (2 + 3 * fluid_behavior_index_m) * yield_stress_tao_y) + (geometric_parameter_b ** 2) * ((-1 + fluid_behavior_index_m) * (-1 + 2 * fluid_behavior_index_m) * (wall_shear_stress_tao_w ** 2) - 2 * (-1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * wall_shear_stress_tao_w * yield_stress_tao_y + (1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * (yield_stress_tao_y ** 2)))
    trap_7 = (3 * (wall_shear_stress_tao_w ** (-2 + geometric_parameter_a / geometric_parameter_b)) + ((5 ** (1 + 1 / fluid_behavior_index_m)) * (((5 * wall_shear_stress_tao_w) / 6 + yield_stress_tao_y / 6) ** (-2 + geometric_parameter_a / geometric_parameter_b))) / (6 ** (1 / fluid_behavior_index_m)) + ((2 ** (2 + 1 / fluid_behavior_index_m)) * (((2 * wall_shear_stress_tao_w) / 3 + yield_stress_tao_y / 3) ** (-2 + geometric_parameter_a / geometric_parameter_b))) / (3 ** (1 / fluid_behavior_index_m)) + (2 * ((wall_shear_stress_tao_w / 3 + (2 * yield_stress_tao_y) / 3) ** (-2 + geometric_parameter_a / geometric_parameter_b))) / (3 ** (1 / fluid_behavior_index_m)) + 3 * (2 ** (2 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-2 + geometric_parameter_a / geometric_parameter_b)) + (6 ** (2 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + 5 * yield_stress_tao_y) ** (-2 + geometric_parameter_a / geometric_parameter_b)))
    trap_8 = (1 + fluid_behavior_index_m) * yield_stress_tao_y
    trap_9 = ((geometric_parameter_a ** 2) * (fluid_behavior_index_m ** 2) * ((wall_shear_stress_tao_w - yield_stress_tao_y) ** 2) - geometric_parameter_a * geometric_parameter_b * fluid_behavior_index_m * (wall_shear_stress_tao_w - yield_stress_tao_y) * ((-2 + 3 * fluid_behavior_index_m) * wall_shear_stress_tao_w - (2 + 3 * fluid_behavior_index_m) * yield_stress_tao_y) + (geometric_parameter_b ** 2) * ((-1 + fluid_behavior_index_m) * (-1 + 2 * fluid_behavior_index_m) * (wall_shear_stress_tao_w ** 2) - 2 * (-1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * wall_shear_stress_tao_w * yield_stress_tao_y + (1 + fluid_behavior_index_m + 2 * (fluid_behavior_index_m ** 2)) * (yield_stress_tao_y ** 2)))
    trap_2 = (geometric_parameter_a * (wall_shear_stress_tao_w - yield_stress_tao_y) * (-(((2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-3 + geometric_parameter_a / geometric_parameter_b)) * trap_6) / ((geometric_parameter_b ** 2) * (fluid_behavior_index_m ** 2))) + 9 * trap_5))
    trap_1 = (wall_shear_stress_tao_w * (geometric_parameter_b * (wall_shear_stress_tao_w - yield_stress_tao_y) * (3 * (-1 + geometric_parameter_a / geometric_parameter_b) * trap_7 - ((2 ** (2 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * (-geometric_parameter_b - geometric_parameter_a * fluid_behavior_index_m + 2 * geometric_parameter_b * fluid_behavior_index_m) * ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-3 + geometric_parameter_a / geometric_parameter_b)) * (geometric_parameter_a * fluid_behavior_index_m * (-wall_shear_stress_tao_w + yield_stress_tao_y) + geometric_parameter_b * ((-1 + fluid_behavior_index_m) * wall_shear_stress_tao_w - trap_8))) / ((geometric_parameter_b ** 2) * (fluid_behavior_index_m ** 2)) - trap_4 / ((geometric_parameter_b ** 3) * (fluid_behavior_index_m ** 2))) + geometric_parameter_b * (1 + 1 / fluid_behavior_index_m) * trap_3 - trap_2 / wall_shear_stress_tao_w))

    return (geometric_parameter_b * (wall_shear_stress_tao_w - yield_stress_tao_y) * (-(((2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-3 + geometric_parameter_a / geometric_parameter_b)) * trap_9) / ((geometric_parameter_b ** 2) * (fluid_behavior_index_m ** 2))) + 9 * ((wall_shear_stress_tao_w ** (-1 + geometric_parameter_a / geometric_parameter_b)) + 2 * (((5 / 6) ** (1 / fluid_behavior_index_m)) * (((5 * wall_shear_stress_tao_w) / 6 + yield_stress_tao_y / 6) ** (-1 + geometric_parameter_a / geometric_parameter_b)) + ((2 / 3) ** (1 / fluid_behavior_index_m)) * (((2 * wall_shear_stress_tao_w) / 3 + yield_stress_tao_y / 3) ** (-1 + geometric_parameter_a / geometric_parameter_b)) + ((wall_shear_stress_tao_w / 3 + (2 * yield_stress_tao_y) / 3) ** (-1 + geometric_parameter_a / geometric_parameter_b)) / (3 ** (1 / fluid_behavior_index_m)) + (2 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + yield_stress_tao_y) ** (-1 + geometric_parameter_a / geometric_parameter_b)) + (6 ** (1 - geometric_parameter_a / geometric_parameter_b - 1 / fluid_behavior_index_m)) * ((wall_shear_stress_tao_w + 5 * yield_stress_tao_y) ** (-1 + geometric_parameter_a / geometric_parameter_b)))))) / trap_1


def fann_friction_factor(generalized_reynolds_number,
                         generalized_flow_behavior_index_n,
                         geometric_parameter_a,
                         geometric_parameter_b):
    transition_reynolds_number = 2100
    turbulent_reynolds_number = 2400 #2400

    f_laminar = 16/generalized_reynolds_number

    if generalized_reynolds_number < transition_reynolds_number:
        return f_laminar
    elif generalized_reynolds_number < turbulent_reynolds_number:
        return f_laminar  # this method is reasonable however, it can be improved in the future for transitional
    else:
        iteration_difference = 1
        friction_factor = f_laminar
        while iteration_difference > 0.02:  # multiply the number with 100 to get percent difference
            f_iteration = (4 / (generalized_flow_behavior_index_n ** 0.75) * (math.log((generalized_reynolds_number * friction_factor ** (1 - generalized_flow_behavior_index_n / 2)), 10)) - 0.4 / (generalized_flow_behavior_index_n ** 1.2) + 4 * (generalized_flow_behavior_index_n ** 0.25) * math.log((4 * (geometric_parameter_a + geometric_parameter_b * generalized_flow_behavior_index_n)) / (3 * generalized_flow_behavior_index_n + 1),10)) ** -2
            iteration_difference = abs((f_iteration - friction_factor)/f_laminar)
            friction_factor = f_iteration

    return friction_factor


def pressure_drop_calculator(yield_stress_tao_y,
                             consistency_index_k,
                             fluid_behavior_index_m,
                             flow_rate,
                             fluid_density,
                             conduit_type,
                             hole_size,
                             pipe_od,
                             pipe_id, tool_joint_od):

    d_hyd = hydraulic_diameter(hole_size, pipe_od, pipe_id, conduit_type)

    geometric_parameter_a = geometric_parameter_a_calculator(conduit_type)
    geometric_parameter_b = geometric_parameter_b_calculator(conduit_type)
    velocity = pipe_and_annular_velocity_calculator(flow_rate,hole_size,pipe_od,pipe_id,conduit_type)
    wall_shear_stress_tao_w = yield_stress_tao_y + consistency_index_k * ((8 * velocity) / d_hyd) ** fluid_behavior_index_m

    iteration_difference = 1
    tao_w_initial = wall_shear_stress_tao_w
    while iteration_difference > 0.02:  # multiply the number with 100 to get percent difference
        shear_rate_updated = yield_power_law_newtonian_shear_rate(yield_stress_tao_y,consistency_index_k,fluid_behavior_index_m,tao_w_initial,conduit_type)
        flow_behavior_index_updated = generalized_flow_behavior_index_n(yield_stress_tao_y,fluid_behavior_index_m,tao_w_initial,conduit_type)

        generalized_consistency_index_updated = generalized_consistency_index_k_prime(tao_w_initial,shear_rate_updated,flow_behavior_index_updated)
        generalized_reynolds_number_updated = generalized_reynolds_number(fluid_density,velocity,hole_size,pipe_od,pipe_id,flow_behavior_index_updated,generalized_consistency_index_updated,conduit_type)
        fann_friction_factor_updated = fann_friction_factor(generalized_reynolds_number_updated,flow_behavior_index_updated,geometric_parameter_a,geometric_parameter_b)

        tao_w_updated = fann_friction_factor_updated * fluid_density *(velocity**2)/2
        iteration_difference = abs((tao_w_updated - tao_w_initial) / tao_w_initial)

        if flow_behavior_index_updated < 0.1:  # this is to prevent returning an exception and exiting the loop. The Dodge Metzner friction factor calculation is not suited for flow behavior index less than 0.2
            iteration_difference = 0.01
        tao_w_initial = tao_w_updated
    pressure_drop = 4 * tao_w_updated / d_hyd

    if conduit_type == "annular":
        r = annulus_pressure_coefficient(flow_behavior_index_updated,pipe_od,hole_size,tool_joint_od)
        pressure_drop *= r

    return pressure_drop