import numpy as np
import sys

from definitions import output_raw_si_units, output_raw_field_units
from utilities.unit_converters import *
from utilities import column_names as columns
from model_engine.surface_bit_bha_pressure_drop import misc_parasitic_losses
from utilities.utilities_for_input_processing import WellTrajectory, bit_depth_finder, DiameterProfile, step_calculator, step_calculator_zeros
from model_engine.fluid_characterization import pressure_drop_calculator
from utilities.charts_and_schematics import data_frame_creator


np.set_printoptions(precision=5, suppress=True, threshold=sys.maxsize)


class ResultArray:
    def __init__(self, bit_info, drill_string, bottom_hole_assembly,
                 casing_design, hole_size_input, well_trajectory_file, calculation_step_difference, consistency_index_k, surf_class):
        self.bit = bit_info
        self.drillstring = drill_string
        self.bha = bottom_hole_assembly
        self.csgdesign = casing_design
        self.openholesize = hole_size_input
        self.k = consistency_index_k
        self.surfacelineclass = surf_class
        self.wellplan = well_trajectory_file
        self.welltrajectory = WellTrajectory(self.wellplan)
        self.step = calculation_step_difference
        self.bit_depth = bit_depth_finder(self.drillstring, self.bha)
        self.measured_depths = step_calculator(self.bit_depth, self.step)
        self.inclination_list = step_calculator_zeros(self.bit_depth, self.step)
        self.tvd_list = step_calculator_zeros(self.bit_depth, self.step)
        self.ann_id_list = step_calculator_zeros(self.bit_depth, self.step)
        self.string_od_list = step_calculator_zeros(self.bit_depth, self.step)
        self.string_id_list = step_calculator_zeros(self.bit_depth, self.step)
        self.tj_od_list = step_calculator_zeros(self.bit_depth, self.step)
        self.tj_id_list = step_calculator_zeros(self.bit_depth, self.step)
        self.diameter_calculator = DiameterProfile(self.csgdesign, self.drillstring, self.bha, self.openholesize)

    def show_inputs_in_field_units(self):
        index = 0
        for i in self.measured_depths:
            inc = self.welltrajectory.inclination_finder(i)
            tvd = self.welltrajectory.tvd_finder(i)
            inner_diameter = self.diameter_calculator.annulus_id_finder_with_depth_input(i)
            outer_diameter = self.diameter_calculator.drill_string_od_finder_with_depth_input(i)
            string_inner_diameter = self.diameter_calculator.drill_string_id_finder_with_depth_input(i)

            self.inclination_list[index] = inc
            self.tvd_list[index] = tvd
            self.ann_id_list[index] = inner_diameter
            self.string_od_list[index] = outer_diameter
            self.string_id_list[index] = string_inner_diameter

            index += 1

        composite_list_field_units = np.hstack((self.measured_depths, self.inclination_list, self.tvd_list,
                                                self.ann_id_list, self.string_od_list, self.string_id_list))

        return composite_list_field_units

    def tj_od_id_array_field_units(self):
        index = 0
        for i in self.measured_depths:
            tj_inner_diameter = self.diameter_calculator.tool_joint_id_finder_with_depth_input(i)
            tj_outer_diameter = self.diameter_calculator.tool_joint_od_finder_with_depth_input(i)

            self.tj_od_list[index] = tj_outer_diameter
            self.tj_id_list[index] = tj_inner_diameter

            index += 1

        array = np.hstack((self.tj_od_list, self.tj_id_list))
        return array

    def tj_od_id_array_si_units(self):
        tool_joints_si_units = self.tj_od_id_array_field_units()
        tool_joints_si_units[:, 0] = unit_converter_inches_to_meter(tool_joints_si_units[:, 0])
        tool_joints_si_units[:, 1] = unit_converter_inches_to_meter(tool_joints_si_units[:, 1])
        return tool_joints_si_units

    def show_inputs_in_si_units(self):
        composite_list_si_units = self.show_inputs_in_field_units()
        composite_list_si_units[:, columns.names['composite_list_columns_md']] = unit_converter_feet_to_meter(
            composite_list_si_units[:, columns.names['composite_list_columns_md']])
        composite_list_si_units[:, columns.names['composite_list_columns_tvd']] = unit_converter_feet_to_meter(
            composite_list_si_units[:, columns.names['composite_list_columns_tvd']])
        composite_list_si_units[:,
        columns.names['composite_list_columns_annulus_diameter']] = unit_converter_inches_to_meter(
            composite_list_si_units[:, columns.names['composite_list_columns_annulus_diameter']])
        composite_list_si_units[:, columns.names['composite_list_columns_string_od']] = unit_converter_inches_to_meter(
            composite_list_si_units[:, columns.names['composite_list_columns_string_od']])
        composite_list_si_units[:, columns.names['composite_list_columns_string_id']] = unit_converter_inches_to_meter(
            composite_list_si_units[:, columns.names['composite_list_columns_string_id']])

        return composite_list_si_units

    def pressure_drop_calculations_si_units(self, yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,
                                            flow_rate_q, mud_density, nozzle_list, tj_frequency, tj_length):
        results_si_units = self.show_inputs_in_si_units()
        shape_of_data = results_si_units.shape
        row_count = shape_of_data[0]
        results_si_units = np.c_[results_si_units, np.zeros(row_count), np.zeros(row_count)]
        row_index = 0
        length_of_steps = unit_converter_feet_to_meter(self.step)
        tool_joint_dimensions = self.tj_od_id_array_si_units()
        # define variables for tool joint effect calculations
        joint_length = tj_frequency
        a = joint_length / length_of_steps
        b = np.ceil(a)  # this number means add tool joint pressure drop to every b rows
        coefficient = b/a  # this number is to be multiplied with the tool joint length
        for row in self.show_inputs_in_si_units():
            if row_index % b == 0:
                pipe_p_drop_tube = (pressure_drop_calculator(yield_stress_tao_y, consistency_index_k,fluid_behavior_index_m,
                                                       flow_rate_q, mud_density, 'pipe',
                                                       row[columns.names['composite_list_columns_annulus_diameter']],
                                                       row[columns.names['composite_list_columns_string_od']],
                                                       row[columns.names['composite_list_columns_string_id']], tool_joint_dimensions[row_index][0])) * (length_of_steps-tj_length * coefficient)  # this will calculate the pressure drop for the inside of the string except the tool joint

                pipe_p_drop_tool_joint = (pressure_drop_calculator(yield_stress_tao_y, consistency_index_k,
                                                             fluid_behavior_index_m,
                                                             flow_rate_q, mud_density, 'pipe',
                                                             row[columns.names['composite_list_columns_annulus_diameter']],
                                                             row[columns.names['composite_list_columns_string_od']], tool_joint_dimensions[row_index][1],
                                                             tool_joint_dimensions[row_index][0])) * (tj_length * coefficient)  # this will calculate the pressure drop for the inside of the tool joint

                p_drop_pipe_si_units = pipe_p_drop_tube + pipe_p_drop_tool_joint

            else:
                p_drop_pipe_si_units = (pressure_drop_calculator(yield_stress_tao_y, consistency_index_k,fluid_behavior_index_m,
                                                       flow_rate_q, mud_density, 'pipe',
                                                       row[columns.names['composite_list_columns_annulus_diameter']],
                                                       row[columns.names['composite_list_columns_string_od']],
                                                       row[columns.names['composite_list_columns_string_id']], tool_joint_dimensions[row_index][0])) * length_of_steps

            if row_index == 0:
                p_drop_pipe_si_units = misc_parasitic_losses(nozzle_list, mud_density, flow_rate_q, self.bha, self.k, self.surfacelineclass)

            p_drop_annular_si_units = (pressure_drop_calculator(yield_stress_tao_y, consistency_index_k,
                                                               fluid_behavior_index_m, flow_rate_q, mud_density, 'annular',
                                                               row[columns.names['composite_list_columns_annulus_diameter']],
                                                               row[columns.names['composite_list_columns_string_od']],
                                                               row[columns.names['composite_list_columns_string_id']], tool_joint_dimensions[row_index][0])) * length_of_steps

            results_si_units[row_index, columns.names['composite_list_columns_pipe_pressure_drop']] = p_drop_pipe_si_units
            results_si_units[row_index, columns.names['composite_list_columns_annulus_pressure_drop']] = p_drop_annular_si_units
            row_index += 1

        # send results to another function to calculate cumulative pressure drop per depth
        results_si_units = cumulative_pressure_drop_calculator(results_si_units,mud_density,flow_rate_q, nozzle_list)

        # send results to another function to calculate ecd
        results_si_units = equivalent_circulating_density_calculator(results_si_units, mud_density)
        # save results as csv file and pandas data frame
        file_name_and_directory = output_raw_si_units
        np.savetxt(file_name_and_directory, results_si_units, delimiter=',', fmt='%1.3f')
        data_frame_creator(file_name_and_directory)
        return results_si_units

    def pressure_drop_calculations_field_units(self, yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,
                                               flow_rate_q, mud_density, nozzle_list, tj_frequency, tj_length):
        results_field_units = self.show_inputs_in_field_units()
        pressure_drops = np.copy(
            self.pressure_drop_calculations_si_units(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,
                                                     flow_rate_q, mud_density, nozzle_list, tj_frequency, tj_length))
        equivalent_circulating_density = pressure_drops[:,columns.names['composite_list_columns_equivalent_circulating_density']]
        equivalent_circulating_density = unit_converter_density_kgm3_to_ppg(equivalent_circulating_density)
        equivalent_circulating_density = equivalent_circulating_density.reshape(-1, 1)
        pressure_drops = pressure_drops[:, columns.names['composite_list_columns_pipe_pressure_drop']:(columns.names['composite_list_columns_pump_pressure'] + 1)]
        pressure_drops = unit_converter_pascal_to_psi(pressure_drops)

        results_field_units = np.concatenate([results_field_units, pressure_drops, equivalent_circulating_density],
                                             axis=1)
        # save results as csv file and pandas data frame
        file_name_and_directory = output_raw_field_units
        np.savetxt(file_name_and_directory, results_field_units, delimiter=',', fmt='%1.3f')
        data_frame_creator(file_name_and_directory)
        return results_field_units




def cumulative_pressure_drop_calculator(results_array, mud_density, flow_rate_q, bit_nozzles):
    extract_pipe_pressure_drop = results_array[:, [columns.names['composite_list_columns_pipe_pressure_drop']]]
    extract_annular_pressure_drop = results_array[:, [columns.names['composite_list_columns_annulus_pressure_drop']]]

    cum_sum_pipe = np.cumsum(extract_pipe_pressure_drop)
    cum_sum_annulus = np.cumsum(extract_annular_pressure_drop)
    pump_pressure = cum_sum_pipe + cum_sum_annulus

    cum_sum_pipe = cum_sum_pipe.reshape(-1, 1)
    cum_sum_annulus = cum_sum_annulus.reshape(-1, 1)
    pump_pressure = pump_pressure.reshape(-1, 1)

    results_array = np.concatenate([results_array, cum_sum_pipe, cum_sum_annulus, pump_pressure], axis=1)
    return results_array


def equivalent_circulating_density_calculator(results_array, mud_density):
    cumulative_annular_p_drop = results_array[:,
                                [columns.names['composite_list_columns_cumulative_annular_pressure_drop']]]
    true_vertical_depth = results_array[:, [columns.names['composite_list_columns_tvd']]]
    max_row = len(cumulative_annular_p_drop)
    ecd = np.zeros(max_row).reshape(-1, 1)

    row_index = 0
    for _ in ecd:
        ecd[row_index] = (cumulative_annular_p_drop[row_index] / (
                    9.81 * true_vertical_depth[row_index]) + mud_density) if row_index > 0 else mud_density
        row_index += 1

    results_array = np.concatenate([results_array, ecd], axis=1)
    return results_array
