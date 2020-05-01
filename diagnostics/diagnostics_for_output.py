



import datetime
from model_engine.results_array_calculator import *
from model_engine.rheological_model_parameters import*
from model_engine.surface_bit_bha_pressure_drop import bit_pressure_drop_psi

np.set_printoptions(precision=5, suppress=True,threshold=sys.maxsize)

####################INPUTS#########################
casing_design = list()
drill_string = list()
bottom_hole_assembly = list()
drill_string.append([5, 4.276, 10000, 0])
bottom_hole_assembly.append([6.75, 3.5, 10150, 10000])
bit_nozzles= [16,16,16,13,13,13]


shear_rate = [1022, 511, 340, 170, 10.22, 5.11]
shear_stress = [54, 38, 31, 23, 8, 7]
fluid_type = "PL"
print(rheological_parameters(shear_rate, shear_stress, fluid_type))

hole_size_input = 8.5
eccentricity_e = 0
yield_stress_tao_y_input = rheological_parameters(shear_rate, shear_stress, fluid_type)[0]
consistency_index_k_input = rheological_parameters(shear_rate, shear_stress, fluid_type)[1] #(lbf*s^m/100ft2)
fluid_behavior_index_m = rheological_parameters(shear_rate, shear_stress, fluid_type)[2]
flow_rate_q_input = 600
mud_density_input = 10
conduit_type = "annular"


# ###########################NEWTONIAN FLUID TEST INPUT############################
# hole_size_input = 8.5
# eccentricity_e = 0
# yield_stress_tao_y_input = 0
# consistency_index_k_input = 0.0017888 #(lbf*s^m/100ft2)
# fluid_behavior_index_m = 1
# flow_rate_q_input = 600
# mud_density_input = 10
# conduit_type = "annular"

# converted units
open_hole_size = unit_converter_inches_to_meter(hole_size_input)
flow_rate_q = unit_converter_flow_rate_gpm_to_m3persec(flow_rate_q_input)
yield_stress_tao_y = unit_converter_yield_stress_field_units_to_pascal(yield_stress_tao_y_input)
consistency_index_k = unit_converter_consistency_index_k_field_units_to_pascal(consistency_index_k_input)
mud_density = unit_converter_density_ppg_to_kgm3(mud_density_input)


# ####################INPUTS#########################

# wellbore_schematic(drill_string,bottom_hole_assembly,casing_design,hole_size_input)


begin_time = datetime.datetime.now()

print(bit_pressure_drop_psi(bit_nozzles,mud_density_input,flow_rate_q_input))
test=ResultArray(drill_string, bottom_hole_assembly, casing_design, hole_size_input, 'input/directional_plan.csv')
# results = test.pressure_drop_calculations_si_units(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m, flow_rate_q, mud_density, eccentricity_e,bit_nozzles)
# results = test.pressure_drop_calculations_field_units(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m, flow_rate_q, mud_density, eccentricity_e, bit_nozzles)
# results = test.final_results_field_units_with_surface_bit_mwd_pressure_drop(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m, flow_rate_q, mud_density, eccentricity_e,bit_nozzles)
# results = test.show_inputs_in_field_units()
# print(results)
print(f"code run time {datetime.datetime.now() - begin_time}")
# np.savetxt('output/pressure_drop_field.csv', results, delimiter=',', fmt='%1.3f')
# data_frame_creator('output/pressure_drop_field.csv')

