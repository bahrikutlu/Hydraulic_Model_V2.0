from scipy.optimize import curve_fit
from matplotlib import pyplot as plt

shear_rate = [1022, 511, 340, 170, 10.22, 5.11]
shear_stress = [54, 38, 31, 23, 8, 7]
fluid_type = "PL"
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
    plt.plot(shear_rate, shear_stress, 'o', color='red', label="data")
    plt.plot(shear_rate, flow_curve, '--', color='blue', label="optimized data")
    plt.legend()
    plt.savefig(flow_curve_image_directory)
    plt.close()


# USE FOLLOWING TO CALL THE FUNCTIONS
print(rheological_parameters(shear_rate, shear_stress, fluid_type))
fluid_properties_plotter(shear_rate, shear_stress, fluid_type)