from math import pi
from utilities.unit_converters import *
from utilities.column_names import string_input_columns


def tfa_calculator(nozzle_list):
    sum_square = 0
    for nozzle in nozzle_list:
        sum_square += nozzle ** 2
    total_flow_area_tfa_sqin = sum_square * (pi / (4 * (32 ** 2)))
    return total_flow_area_tfa_sqin


def bit_pressure_drop_psi(nozzle_list, mud_density_ppg, flow_rate_gpm):
    # from Applied Drilling Engineering
    discharge_coefficient = 0.95
    tfa = tfa_calculator(nozzle_list)
    fixed_term = 8.311 * (10 ** -5) / (discharge_coefficient ** 2)
    bit_pressure_drop = fixed_term * mud_density_ppg * (flow_rate_gpm ** 2) / (tfa ** 2)
    return bit_pressure_drop


def surface_pressure_drop(density_ppg, flow_rate_ppg, k_index, class_1_2_3_4):
    # Used IADC class 1 as it is close to what i have observed in the field in West Texas. There is not a standard
    # across the field...
    # A sample table and the typical formula can be found in:
    # http://www.drillingformulas.com/pressure-drop-through-surface-equipment/
    coefficients = {"1": 22, "2": 8, "3": 5, "4": 4}
    coeff = coefficients[str(class_1_2_3_4)]
    k_index *= 20.885  # conversion from lb/100ft2 to cP
    visc_factor_vf = (k_index/density_ppg) ** 0.14
    result = 0.00001 * coeff * density_ppg * visc_factor_vf * (flow_rate_ppg ** 1.86)
    return result


def mud_motor_pressure_drop(flow_rate_si_m3s, bha):
    # correlations are from curve fitting the data in Cougar Directional Drilling Motor Book (2012)
    flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_si_m3s)
    motor_od = 0
    for item in bha:
        if item[string_input_columns['input_list_component_type']] == "Motor":
            motor_od = item[string_input_columns['input_list_outer_diameter']]
    if motor_od >= 8:
        result = 0.2145 * flow_rate_gpm - 39.664
    elif 5.5 < motor_od < 8:
        result = 0.173 * flow_rate_gpm + 101.9
    elif 3 < motor_od <= 5.5:
        result = 0.668 * flow_rate_gpm -34
    else:
        result = 0
    return result


def mwd_pressure_drop(flow_rate_si_m3s, bha):
    # correlations are copied from motor data. this needs to be updated
    flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_si_m3s)
    mwd_od = 0
    for item in bha:
        if item[string_input_columns['input_list_component_type']] == "MWD":
            mwd_od = item[string_input_columns['input_list_outer_diameter']]
    if mwd_od >= 5.5:
        result = 1.3393 * flow_rate_gpm - 192.68
    elif 2 < mwd_od < 5.5:
        result = 2.405 * flow_rate_gpm - 262.17
    else:
        result = 0
    return result


def misc_parasitic_losses(nozzle_list, mud_density_kgm3, flow_rate_m3s, bha, k, surface_class):
    mud_density_ppg = unit_converter_density_kgm3_to_ppg(mud_density_kgm3)
    flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_m3s)
    bit_p_drop = bit_pressure_drop_psi(nozzle_list, mud_density_ppg, flow_rate_gpm)
    result = surface_pressure_drop(mud_density_ppg, flow_rate_gpm, k, surface_class) + bit_p_drop + mwd_pressure_drop(flow_rate_m3s, bha) + mud_motor_pressure_drop(flow_rate_m3s, bha)
    result = unit_converter_psi_to_pascal(result) * 3.28084  #result is returned in Pascal, for the results array
    return result
