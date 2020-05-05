from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from definitions import flow_curve_image_directory


def yield_power_law_model(sr, taoy, k, m):
    return taoy+k*(sr**m)


def power_law_model(sr, k, m):
    return k * (sr ** m)


def rheological_parameters(shear_rate, shear_stress, fluid_type):
    rheology_parameters, cov = curve_fit(power_law_model, shear_rate, shear_stress)
    taoy = 0
    k = rheology_parameters[0]
    m = rheology_parameters[1]
    if fluid_type == "YPL":
        rheology_parameters, cov = curve_fit(yield_power_law_model, shear_rate, shear_stress)
        taoy = rheology_parameters[0]
        k = rheology_parameters[1]
        m = rheology_parameters[2]
    results = [taoy,k,m]
    return results


def fluid_properties_plotter(shear_rate, shear_stress, fluid_type):
    rheology = rheological_parameters(shear_rate, shear_stress, fluid_type)
    flow_curve = rheology[1]*(shear_rate ** rheology[2])
    if fluid_type == "YPL":
        rheology = rheological_parameters(shear_rate, shear_stress, fluid_type)
        flow_curve = rheology[0] + rheology[1]*(shear_rate ** rheology[2])
    plt.figure(figsize=(4,4))
    plt.plot(shear_rate, shear_stress, 'o', color='red', label="data")
    plt.plot(shear_rate, flow_curve, '--', color='blue', label="optimized data")
    plt.legend()
    plt.xlabel("Shear Rate (1/s)")
    plt.ylabel("Shear Stress (lbf/100ft2)")
    plt.savefig(flow_curve_image_directory, bbox_inches='tight')
    plt.close()