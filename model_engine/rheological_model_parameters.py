from scipy.optimize import curve_fit,least_squares
from matplotlib import pyplot as plt
from definitions import flow_curve_image_directory


def yieldpowerlaw(args, sr, ss):
    ty, k, m = args
    result = ty + k * (sr ** m) - ss
    return result


def power_law_model(sr, k, m):
    return k * (sr ** m)


def rheological_parameters(shear_rate, shear_stress, fluid_type):
    rheology_parameters, cov = curve_fit(power_law_model, shear_rate, shear_stress)
    taoy = 0
    taoy_limit = 5  # limits the max Taoy value
    k = rheology_parameters[0]
    m = rheology_parameters[1]
    if fluid_type == "YPL":
        x0 = [0, 0, 1]
        result = least_squares(fun=yieldpowerlaw, x0=x0, args=(shear_rate, shear_stress), bounds=([0, 0, 0], [taoy_limit, 5, 1]))
        taoy = result.x[0]
        k = result.x[1]
        m = result.x[2]
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


#
#
# shearrate = [1020,510,340,170,10.2,5.1]
# # shearstress = [54,38,31,23,8,7]
# shearstress = [46,30,24,16,6,5]
#


# def powerlaw(args, sr, ss):
#     k, m = args
#     result = k * (sr ** m) - ss
#     return result
#
#
# x0 = [1, .5]
# result = least_squares(fun=powerlaw, x0=x0, args=(shearrate,shearstress))
# print(result.x)




