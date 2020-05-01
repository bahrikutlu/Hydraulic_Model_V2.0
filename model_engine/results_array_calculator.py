import numpy as np
import sys
from utilities.unit_converters import *
from utilities import column_names as columns
from model_engine.surface_bit_bha_pressure_drop import misc_parasitic_losses
from utilities.utilities_for_input_processing import WellTrajectory, bit_depth_finder, DiameterProfile
from model_engine.fluid_characterization import pressure_drop_calculator
from utilities.charts_and_schematics import data_frame_creator


np.set_printoptions(precision=5, suppress=True, threshold=sys.maxsize)


class ResultArray:
    def __init__(self, bit_info, drill_string, bottom_hole_assembly, casing_design, hole_size_input, well_trajectory_file):
        self.bit = bit_info
        self.drillstring = drill_string
        self.bha = bottom_hole_assembly
        self.csgdesign = casing_design
        self.openholesize = hole_size_input
        self.wellplan = well_trajectory_file
        self.welltrajectory = WellTrajectory(self.wellplan)
        self.bit_depth = bit_depth_finder(self.drillstring, self.bha)
        self.measured_depths = np.arange(self.bit_depth).reshape((self.bit_depth, 1))
        self.inclination_list = np.zeros((self.bit_depth, 1))
        self.tvd_list = np.zeros((self.bit_depth, 1))
        self.ann_id_list = np.zeros((self.bit_depth, 1))
        self.string_od_list = np.zeros((self.bit_depth, 1))
        self.string_id_list = np.zeros((self.bit_depth, 1))
        self.diameter_calculator = DiameterProfile(self.csgdesign, self.drillstring, self.bha,self.openholesize)

    def show_inputs_in_field_units(self):
        i = 0
        while i < self.bit_depth:
            inc = self.welltrajectory.inclination_finder(self.measured_depths[i, 0])
            tvd = self.welltrajectory.tvd_finder(self.measured_depths[i, 0])
            inner_diameter = self.diameter_calculator.annulus_id_finder_with_depth_input(self.measured_depths[i, 0])
            outer_diameter = self.diameter_calculator.drill_string_od_finder_with_depth_input(
                self.measured_depths[i, 0])
            string_inner_diameter = self.diameter_calculator.drill_string_id_finder_with_depth_input(
                self.measured_depths[i, 0])

            self.inclination_list[i, 0] = inc
            self.tvd_list[i, 0] = tvd
            self.ann_id_list[i, 0] = inner_diameter
            self.string_od_list[i, 0] = outer_diameter
            self.string_id_list[i, 0] = string_inner_diameter

            i += 1

        composite_list_field_units = np.hstack((self.measured_depths, self.inclination_list, self.tvd_list,
                                                self.ann_id_list, self.string_od_list, self.string_id_list))
        return composite_list_field_units

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
                                            flow_rate_q, mud_density, eccentricity_e, nozzle_list):
        results_si_units = self.show_inputs_in_si_units()
        shape_of_data = results_si_units.shape
        row_count = shape_of_data[0]
        results_si_units = np.c_[results_si_units, np.zeros(row_count), np.zeros(row_count)]
        row_index = 0
        for row in self.show_inputs_in_si_units():
            pipe_p_drop = pressure_drop_calculator(yield_stress_tao_y, consistency_index_k,
                                                            fluid_behavior_index_m, flow_rate_q, mud_density,
                                                            eccentricity_e, 'pipe',
                                                            row[columns.names['composite_list_columns_annulus_diameter']],
                                                            row[columns.names['composite_list_columns_string_od']],
                                                            row[columns.names['composite_list_columns_string_id']])
            if row_index == 0:
                p_drop_pipe_si_units = misc_parasitic_losses(nozzle_list, mud_density, flow_rate_q)
            else:
                p_drop_pipe_si_units = pipe_p_drop
            p_drop_annular_si_units = pressure_drop_calculator(yield_stress_tao_y, consistency_index_k,
                                                               fluid_behavior_index_m, flow_rate_q, mud_density,
                                                               eccentricity_e, 'annular',
                                                               row[columns.names['composite_list_columns_annulus_diameter']],
                                                               row[columns.names['composite_list_columns_string_od']],
                                                               row[columns.names['composite_list_columns_string_id']])
            results_si_units[
                row_index, columns.names['composite_list_columns_pipe_pressure_drop']] = p_drop_pipe_si_units
            results_si_units[
                row_index, columns.names['composite_list_columns_annulus_pressure_drop']] = p_drop_annular_si_units
            row_index += 1

        # send results to another function to calculate cumulative pressure drop per depth
        results_si_units = cumulative_pressure_drop_calculator(results_si_units,mud_density,flow_rate_q, nozzle_list)

        # send results to another function to calculate ecd
        results_si_units = equivalent_circulating_density_calculator(results_si_units, mud_density)
        # save results as csv file and pandas data frame
        file_name_and_directory = 'output/calculation_results/raw/pressure_drop_si.csv'
        np.savetxt(file_name_and_directory, results_si_units, delimiter=',', fmt='%1.3f')
        data_frame_creator(file_name_and_directory)
        return results_si_units

    def pressure_drop_calculations_field_units(self, yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,
                                               flow_rate_q, mud_density, eccentricity_e, nozzle_list):
        results_field_units = self.show_inputs_in_field_units()
        pressure_drops = np.copy(
            self.pressure_drop_calculations_si_units(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,
                                                     flow_rate_q, mud_density, eccentricity_e, nozzle_list))
        equivalent_circulating_density = pressure_drops[:,
                                         columns.names['composite_list_columns_equivalent_circulating_density']]
        equivalent_circulating_density = unit_converter_density_kgm3_to_ppg(equivalent_circulating_density)
        equivalent_circulating_density = equivalent_circulating_density.reshape(-1, 1)
        pressure_drops = pressure_drops[:, columns.names['composite_list_columns_pipe_pressure_drop']:(
                    columns.names['composite_list_columns_pump_pressure'] + 1)]
        pressure_drops = unit_converter_pascalovermeter_to_psioverft(pressure_drops)

        results_field_units = np.concatenate([results_field_units, pressure_drops, equivalent_circulating_density],
                                             axis=1)
        # save results as csv file and pandas data frame
        file_name_and_directory = 'output/calculation_results/raw/pressure_drop_field.csv'
        np.savetxt(file_name_and_directory, results_field_units, delimiter=',', fmt='%1.3f')
        data_frame_creator(file_name_and_directory)
        return results_field_units

    # def final_results_si_units_with_surface_bit_mwd_pressure_drop(self,yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,flow_rate_q, mud_density, eccentricity_e ,bit_nozzles):
    #     output = self.pressure_drop_calculations_si_units(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,flow_rate_q, mud_density, eccentricity_e)
    #     shape_of_array = output.shape
    #     row_count = shape_of_array[0]
    #     mud_density_ppg = unit_converter_density_kgm3_to_ppg(mud_density)
    #     flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_q)
    #     first_row_of_pump_pressure = output[0][columns.names['composite_list_columns_pump_pressure']]
    #     bit_pressure_drop = unit_converter_psi_to_pascal(bit_p_drop(bit_nozzles,mud_density_ppg,flow_rate_gpm))
    #     first_row_of_pump_pressure += bit_pressure_drop
    #     return output
    #
    # def final_results_field_units_with_surface_bit_mwd_pressure_drop(self,yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,flow_rate_q, mud_density, eccentricity_e ,bit_nozzles):
    #     output = self.pressure_drop_calculations_field_units(yield_stress_tao_y, consistency_index_k, fluid_behavior_index_m,flow_rate_q, mud_density, eccentricity_e)
    #     shape_of_array = output.shape
    #     row_count = shape_of_array[0]
    #     mud_density_ppg = unit_converter_density_kgm3_to_ppg(mud_density)
    #     flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_q)
    #     first_row_of_pump_pressure = output[0,columns.names['composite_list_columns_pump_pressure']]
    #     bit_pressure_drop = bit_p_drop(bit_nozzles,mud_density_ppg,flow_rate_gpm)
    #     first_row_of_pump_pressure = bit_pressure_drop
    #     output[0,0] = bit_pressure_drop
    #     return output


def cumulative_pressure_drop_calculator(results_array, mud_density, flow_rate_q, bit_nozzles):
    extract_pipe_pressure_drop = results_array[:, [columns.names['composite_list_columns_pipe_pressure_drop']]]
    extract_annular_pressure_drop = results_array[:, [columns.names['composite_list_columns_annulus_pressure_drop']]]

    # mud_density_ppg = unit_converter_density_kgm3_to_ppg(mud_density)
    # flow_rate_gpm = unit_converter_flow_rate_m3persec_to_gpm(flow_rate_q)
    # extract_pipe_pressure_drop[0] = unit_converter_psi_to_pascal(bit_p_drop(bit_nozzles, mud_density_ppg, flow_rate_gpm))

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
                    32.2 * true_vertical_depth[row_index]) + mud_density) if row_index > 0 else mud_density
        row_index += 1

    results_array = np.concatenate([results_array, ecd], axis=1)
    return results_array