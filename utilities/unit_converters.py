# all inputs are US field units and are converted to SI units for calculations.

def unit_converter_inches_to_meter(inches):
    return inches * 0.0254


def unit_converter_feet_to_meter(inches):
    return inches * 0.3048


def unit_converter_yield_stress_field_units_to_pascal(lb_per_100sqft):
    return lb_per_100sqft / 0.47880258889


def unit_converter_consistency_index_k_field_units_to_pascal(lbsm_per100sqft):
    # lb * s ^ m/100sqft to Pa * s ^m
    return lbsm_per100sqft / 2.0885


def unit_converter_flow_rate_gpm_to_m3persec(flow_rate_q_input):
    return flow_rate_q_input * 0.0000631

def unit_converter_flow_rate_m3persec_to_gpm(flow_rate_m3persec_input):
    return flow_rate_m3persec_input / 0.0000631

def unit_converter_density_ppg_to_kgm3(density_input):
    return density_input * 120


def unit_converter_density_kgm3_to_ppg(density_input):
    return density_input / 120


def unit_converter_pascal_to_psi(pascal_input):
    return pascal_input/6895


def unit_converter_psi_to_pascal(psi_input):
    return psi_input*6895


def unit_converter_pascalovermeter_to_psioverft(pascalpermeter):
    return pascalpermeter*0.0000442075
