from model_engine.fluid_characterization import *
from utilities.unit_converters import *
import matplotlib.pyplot as plt

# ##########################troubleshoot FLUID TEST INPUT############################
hole_size_input = 0
pipe_od_input = 0
pipe_id_input = 1.248
yield_stress_tao_y_input = 0#3.316912
consistency_index_k_input = 0.15950418#0.397099 #(lbf*s^m/100ft2)
fluid_behavior_index_m = 0.675249#0.591268
flow_rate_q_input = 8.75226280952381
mud_density_input = 8.33
conduit_type = "pipe"
length = 9.5
tool_joint_od_input = 6.625
tool_joint_id_input = 1.248

#converted units for input
hole_size = unit_converter_inches_to_meter(hole_size_input)
flow_rate_q = unit_converter_flow_rate_gpm_to_m3persec(flow_rate_q_input)
pipe_od = unit_converter_inches_to_meter(pipe_od_input)
pipe_id = unit_converter_inches_to_meter(pipe_id_input)
tool_joint_od = unit_converter_inches_to_meter(tool_joint_od_input)
tool_joint_id = unit_converter_inches_to_meter(tool_joint_id_input)
yield_stress_tao_y = unit_converter_yield_stress_field_units_to_pascal(yield_stress_tao_y_input)
consistency_index_k = unit_converter_consistency_index_k_field_units_to_pascal(consistency_index_k_input)
mud_density = unit_converter_density_ppg_to_kgm3(mud_density_input)


# G:\Archive\Research Data\DTF\Drilling Fluid\080513\0%.xlsm
flow_rates = [3.520872414,4.88522471,6.219356714,7.548508619,8.75226281,9.989415571,11.20815048,12.44405762,13.65370905,15.14058143,16.63345333,18.12482143,19.60997381,21.08090333,22.52814143,23.98316381]
experimental_results = [0.137480591,0.176377061,0.210283996,0.242244655,0.269804151,0.298734491,0.325050707,0.346767059,0.375540403,0.405740225,0.439307525,0.473652171,0.515200965,0.563636273,0.642166654,0.721850006]

# flow_rates = [3.016623391
# ,4.368250994
# ,5.739565764
# ,7.109591192
# ,8.476268246
# ,9.825581864
# ,11.15128943
# ,12.49349025
# ,13.81272203
# ,13.42791439
# ,14.93934269
# ,16.45606639
# ,17.96385528
# ,19.52208751
# ]
# experimental_results = [0.484269448
# ,0.551202492
# ,0.610473428
# ,0.664866398
# ,0.712607319
# ,0.754614293
# ,0.791331057
# ,0.823992492
# ,0.850057125
# ,0.840955978
# ,0.881760234
# ,0.920911022
# ,0.950570833
# ,0.951253527
# ]


results = []
for rate in flow_rates:
    pressure_drop = pressure_drop_calculator(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,
                                             unit_converter_flow_rate_gpm_to_m3persec(rate), mud_density, conduit_type, hole_size, pipe_od,
                                             pipe_id, tool_joint_od)
    pressure_drop=unit_converter_pascalovermeter_to_psioverft(pressure_drop) * length
    results.append(pressure_drop)

# print(results)

import numpy as np
plt.style.use('seaborn-whitegrid')
x_experimental = flow_rates
y_experimental = experimental_results

x_model = flow_rates
y_model = results

plt.plot(x_experimental, y_experimental, 'o', color='black')
plt.plot(x_model, y_model, 'o', color='red')

plt.show()

corr = np.corrcoef(results,experimental_results)
print(corr)


from sklearn.metrics import mean_squared_error
print(mean_squared_error(experimental_results, results))