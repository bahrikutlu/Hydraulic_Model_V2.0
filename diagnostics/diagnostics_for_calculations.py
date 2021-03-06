# this file helps diagnose every step of the pressure drop calculation and was used during development to ensure
# all equations are implemented properly and yield accurate results
#This file may be needed in the future while implementing new features to test the effect of changes in every step
from model_engine.fluid_characterization import *
from utilities.unit_converters import *

# ##########################troubleshoot FLUID TEST INPUT############################
# hole_size_input = 8.5
# pipe_od_input = 5
# pipe_id_input = 0
# yield_stress_tao_y_input = 4.307
# consistency_index_k_input = 1.06 #(lbf*s^m/100ft2)
# fluid_behavior_index_m = 0.555
# flow_rate_q_input = 600
# mud_density_input = 10
# conduit_type = "annular"
###########################YIELD POWER LAW FLUID TEST INPUT#####################################
## 600/300/200/100/6/3 : 54/38/31/23/8/7
## tao_y = 4.29 , K (lbf*s/100ft2) = 1.06601170, m = 0.55

hole_size_input = 8.5
pipe_od_input = 5
pipe_id_input = 4.276
yield_stress_tao_y_input = 1.29
consistency_index_k_input = 1.066 #(lbf*s^m/100ft2)
fluid_behavior_index_m = 0.55
flow_rate_q_input = 600
mud_density_input = 10
tool_joint_od_input = 6.625
tool_joint_id_input = 3.25
conduit_type = "annular"


# # ###########################NEWTONIAN FLUID TEST INPUT############################
# hole_size_input = 8.5
# pipe_od_input = 6.625
# pipe_id_input = 3.25
# yield_stress_tao_y_input = 4.29
# consistency_index_k_input = 1.066 #0.0017888 #(lbf*s^m/100ft2) dynamic visc of water at 80F. multiply this unit with 479 to get visc as centipoise
# fluid_behavior_index_m = 0.55
# flow_rate_q_input = 200
# mud_density_input = 10
# tool_joint_od_input = 6.625
# tool_joint_id_input = 3.25
# conduit_type = "pipe"

# converted units
hole_size = unit_converter_inches_to_meter(hole_size_input)
flow_rate_q = unit_converter_flow_rate_gpm_to_m3persec(flow_rate_q_input)
pipe_od = unit_converter_inches_to_meter(pipe_od_input)
pipe_id = unit_converter_inches_to_meter(pipe_id_input)
tool_joint_od = unit_converter_inches_to_meter(tool_joint_od_input)
tool_joint_id = unit_converter_inches_to_meter(tool_joint_id_input)
yield_stress_tao_y = unit_converter_yield_stress_field_units_to_pascal(yield_stress_tao_y_input)
consistency_index_k = unit_converter_consistency_index_k_field_units_to_pascal(consistency_index_k_input)
mud_density = unit_converter_density_ppg_to_kgm3(mud_density_input)

wall_shear_stress_tao_w = yield_stress_tao_y + consistency_index_k * (
        (8 * pipe_and_annular_velocity_calculator(flow_rate_q, hole_size, pipe_od, pipe_id, conduit_type)) / (
        hydraulic_diameter(hole_size,pipe_od,pipe_id,conduit_type))) ** fluid_behavior_index_m

###########################################################################
print(f"consistency index K: {consistency_index_k}")
print(f"pipe id: {pipe_id}")
print(f"flow rate: {flow_rate_q}")


print(f"tao_w: {wall_shear_stress_tao_w}")
newtonianshearrate = yield_power_law_newtonian_shear_rate(yield_stress_tao_y, consistency_index_k,
                                                          fluid_behavior_index_m,
                                                          wall_shear_stress_tao_w, conduit_type)
print(f"YPL Shear rate: {newtonianshearrate}")

N=generalized_flow_behavior_index_n(yield_stress_tao_y,fluid_behavior_index_m,wall_shear_stress_tao_w,conduit_type)
print(f"generalized flow behavior index: {N}")

Kprime=generalized_consistency_index_k_prime(wall_shear_stress_tao_w,newtonianshearrate,N)
print(f"generalized consistency index: {Kprime}")

fluid_velocity= pipe_and_annular_velocity_calculator(flow_rate_q,hole_size,pipe_od,pipe_id,conduit_type)
print(f"fluid velocity: {fluid_velocity}")

general_reynolds = generalized_reynolds_number(mud_density,fluid_velocity,hole_size,pipe_od,pipe_id,N,Kprime,conduit_type)
print(f"generalized reynolds number: {general_reynolds}")

a=geometric_parameter_a_calculator(conduit_type)
print(f"geometric a : {a}")

b=geometric_parameter_b_calculator(conduit_type)
print(f"geometric b : {b}")

fann_friction = fann_friction_factor(general_reynolds,N,a,b)
print(f"fann friction factor : {fann_friction}")

pressure_drop = pressure_drop_calculator(yield_stress_tao_y,consistency_index_k,fluid_behavior_index_m,flow_rate_q,mud_density,conduit_type,hole_size,pipe_od,pipe_id, tool_joint_od)
print(f"Pressure Drop (Pa) : {pressure_drop}")
print(f"Pressure Drop (psi) for 1ft: {unit_converter_pascalovermeter_to_psioverft(pressure_drop)}")
print(f"Pressure Drop (psi) for 3.75ft: {unit_converter_pascalovermeter_to_psioverft(pressure_drop)*3.75}")
print(f"Pressure Drop (pascal) for 1.143m: {pressure_drop * 1.143}")


if conduit_type == 'annular':
    print(f"ECD is {unit_converter_pascalovermeter_to_psioverft(pressure_drop)/0.052}")
else:
    print(f"ECD is calculated only for the annulus calculations")


