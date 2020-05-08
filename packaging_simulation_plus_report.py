from model_engine.rheological_model_parameters import rheological_parameters, fluid_properties_plotter
from report_generator import html_report_creator
from utilities.excel_input_import import ImportFromExcel
from utilities.charts_and_schematics import wellbore_schematic, annular_pressure_drop_chart, pump_pressure_chart, \
    ecd_profile_chart, ecd_profile_zoomed_chart, pipe_pressure_drop_chart, tvd_vs_chart, pressure_pie_chart
from utilities.unit_converters import *
from utilities.utilities_for_input_processing import create_folders
import datetime
from model_engine.results_array_calculator import ResultArray
from definitions import input_directional_plan_directory, output_raw_field_units


def simulation_and_reporting_package(sheet_name):
    begin_time = datetime.datetime.now()

    print("Simulation Started")

    create_folders()

    print("Necessary folders are Created if they didn't already exist")

    # inputs are pulled from the input.xlsx excel file located in the input folder.
    # change the simulation name variable below to the name of the sheet in excel if
    # a new sheet is created to place new inputs.
    simulation_name = sheet_name  # THIS IS THE ONLY VARIABLE THAT NEEDS TO BE CHANGED IN CODE
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
    step = importer.calculation_step_difference()
    surface_lines_class = importer.surf_lines_class()

    print(f"Inputs are pulled from the sheet named {simulation_name} of input.xlsx")

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

    print("Rheological parameters for drilling fluid are calculated")

    # five lines of code below will change the units from field units to SI units for calculation purposes
    flow_rate_q = unit_converter_flow_rate_gpm_to_m3persec(flow_rate_q_input)
    yield_stress_tao_y = unit_converter_yield_stress_field_units_to_pascal(yield_stress_tao_y_input)
    consistency_index_k = unit_converter_consistency_index_k_field_units_to_pascal(consistency_index_k_input)
    mud_density = unit_converter_density_ppg_to_kgm3(mud_density_input)

    print("Inputs are converted to SI units for calculations")

    input_data = ResultArray(bit,
                             drill_string,
                             bottom_hole_assembly,
                             casing_design,
                             hole_size_input,
                             input_directional_plan_directory, step, consistency_index_k_input, surface_lines_class)

    print("Inputs are processed and placed in an array, proceeding with pressure drop calculations...")
    if unit_system == 'field':
        input_data.pressure_drop_calculations_field_units(yield_stress_tao_y,
                                                                    consistency_index_k,
                                                                    fluid_behavior_index_m,
                                                                    flow_rate_q,
                                                                    mud_density,
                                                                    eccentricity_e,
                                                                    bit_nozzles)
    else:
        input_data.pressure_drop_calculations_si_units(yield_stress_tao_y,
                                                                 consistency_index_k,
                                                                 fluid_behavior_index_m,
                                                                 flow_rate_q,
                                                                 mud_density,
                                                                 eccentricity_e,
                                                                 bit_nozzles)

    print("Calculations for pressure and ECD are completed and results are saved in the output folder")

    # The interactive charts for the results are created here:
    fluid_properties_plotter(shear_rate,
                             shear_stress,
                             fluid_type)

    wellbore_schematic(drill_string,
                       bottom_hole_assembly,
                       casing_design,
                       hole_size_input)

    print("Flow curve and wellbore schematic are drawn")

    file = output_raw_field_units
    annular_pressure_drop_chart(file)
    pump_pressure_chart(file)
    ecd_profile_chart(file)
    ecd_profile_zoomed_chart(file)
    pipe_pressure_drop_chart(file)
    tvd_vs_chart()
    pressure_pie_chart(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles, shear_rate,shear_stress,
                           fluid_type, yield_stress_tao_y_input, consistency_index_k_input,fluid_behavior_index_m,
                           mud_density_input, flow_rate_q_input, simulation_name, surface_lines_class, hole_size_input)

    print("Interactive charts for the report are created")

    # Output report is created:
    html_report_creator(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles, shear_rate,
                        shear_stress, fluid_type, yield_stress_tao_y_input, consistency_index_k_input,
                        fluid_behavior_index_m, mud_density_input, flow_rate_q_input, simulation_name, surface_lines_class, hole_size_input)

    print("Output report is created")

    print(f"code run time {datetime.datetime.now() - begin_time}")