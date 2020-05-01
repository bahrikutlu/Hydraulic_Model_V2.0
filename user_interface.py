from model_engine.rheological_model_parameters import rheological_parameters, fluid_properties_plotter
from utilities.excel_input_import import ImportFromExcel
from utilities.charts_and_schematics import wellbore_schematic
from utilities.unit_converters import *
import datetime
from model_engine.results_array_calculator import ResultArray

# inputs are pulled from the input.xlsx excel file located in the input folder.
# change the simulation name variable below to the name of the sheet in excel if
# a new sheet is created to place new inputs.
simulation_name = 'well1'  # THIS IS THE ONLY VARIABLE THAT NEEDS TO BE CHANGED IN CODE
importer = ImportFromExcel(simulation_name)
# calling the inputs from excel file
casing_design = importer.all_casing_strings()
drill_string = importer.all_drill_strings()
bottom_hole_assembly = importer.all_bha()
bit_nozzles = importer.all_bit_nozzles()
shear_rate = importer.viscometer_readings()[0]
shear_stress = importer.viscometer_readings()[1]
fluid_type = importer.fluid_type()
hole_size_input = importer.hole_size()
eccentricity_e = importer.eccentricity()
flow_rate_q_input = importer.flow_rate()
mud_density_input = importer.mud_weight()
unit_system = importer.units()
bit = importer.bit()

# calculating the rheological parameters taoy, K and m from the viscometer readings
# yield stress is taoy, consistency index is K, fluid behavior index is m
# depending on the input selection fluid will be modeled either for Power Law fluid
# or Herschel Bulkley rheological model.
yield_stress_tao_y_input = rheological_parameters(shear_rate,
                                                  shear_stress,
                                                  fluid_type)[0]

consistency_index_k_input = rheological_parameters(shear_rate,
                                                   shear_stress,
                                                   fluid_type)[1]  # (lbf*s^m/100ft2)

fluid_behavior_index_m = rheological_parameters(shear_rate,
                                                shear_stress,
                                                fluid_type)[2]

# five lines of code below will change the units from field units to SI units for calculation purposes
open_hole_size = unit_converter_inches_to_meter(hole_size_input)
flow_rate_q = unit_converter_flow_rate_gpm_to_m3persec(flow_rate_q_input)
yield_stress_tao_y = unit_converter_yield_stress_field_units_to_pascal(yield_stress_tao_y_input)
consistency_index_k = unit_converter_consistency_index_k_field_units_to_pascal(consistency_index_k_input)
mud_density = unit_converter_density_ppg_to_kgm3(mud_density_input)

# the following three function calls draw the flow curve and wellbore schematic
fluid_properties_plotter(shear_rate,
                         shear_stress,
                         fluid_type)

wellbore_schematic(drill_string,
                   bottom_hole_assembly,
                   casing_design,
                   hole_size_input)


begin_time = datetime.datetime.now()
input_data = ResultArray(bit,
                         drill_string,
                         bottom_hole_assembly,
                         casing_design,
                         hole_size_input,
                         'input/directional_plan.csv')

if unit_system == 'field':
    results = input_data.pressure_drop_calculations_field_units(yield_stress_tao_y,
                                                                consistency_index_k,
                                                                fluid_behavior_index_m,
                                                                flow_rate_q,
                                                                mud_density,
                                                                eccentricity_e,
                                                                bit_nozzles)
else:
    results = input_data.pressure_drop_calculations_si_units(yield_stress_tao_y,
                                                             consistency_index_k,
                                                             fluid_behavior_index_m,
                                                             flow_rate_q,
                                                             mud_density,
                                                             eccentricity_e,
                                                             bit_nozzles)

print(f"code run time {datetime.datetime.now() - begin_time}")
