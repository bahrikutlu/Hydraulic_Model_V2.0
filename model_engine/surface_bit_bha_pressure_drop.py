from math import pi
from utilities.unit_converters import *


def bit_pressure_drop_psi(nozzle_list, mud_density_ppg, flow_rate_gpm):
    # from Applied Drilling Engineering
    sum_square = 0
    discharge_coefficient = 0.95
    for nozzle in nozzle_list:
        sum_square += nozzle ** 2
    total_flow_area_tfa_sqin = sum_square * (pi / (4 * (32 ** 2)))
    fixed_term = 8.311 * (10 ** -5) / (discharge_coefficient ** 2)
    bit_pressure_drop = fixed_term * mud_density_ppg * (flow_rate_gpm ** 2) / (total_flow_area_tfa_sqin ** 2)
    return bit_pressure_drop


def surface_pressure_drop():
    # place holder function to be changed later with actual calculation
    result = 200
    return result


def mud_motor_pressure_drop():
    # place holder function to be changed later with actual calculation
    result = 300
    return result


def mwd_pressure_drop():
    # place holder function to be changed later with actual calculation
    result = 500
    return result


def misc_parasitic_losses(nozzle_list, mud_density_kgm3, flow_rate_m3s):
    mud_density_ppg = unit_converter_density_kgm3_to_ppg(mud_density_kgm3)
    flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_m3s)

    result = surface_pressure_drop() + \
             bit_pressure_drop_psi(nozzle_list, mud_density_ppg, flow_rate_gpm) + \
             mwd_pressure_drop() + \
             mud_motor_pressure_drop()
    result = unit_converter_psi_to_pascal(result) * 3.28084
    return result
