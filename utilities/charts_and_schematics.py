from math import pi

from bokeh.palettes import Category20c
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import cumsum
from matplotlib import pyplot as plt

import pandas as pd
import numpy as np

from minimum_curvature_method import mincurve
from report_generator import ReportContentCreator
from utilities.utilities_for_input_processing import DiameterProfile, results_csv_loader
from utilities import column_names as columns
from definitions import wellbore_schematic_image_directory, ecd_chart_directory, ecd_chart_zoomed_directory, \
    pipe_pressure_drop_chart_directory, annular_pressure_drop_chart_directory, pump_pressure_chart_directory, \
    tvd_verticalsec_chart_directory, input_directional_plan_directory, output_directional_directory, \
    output_data_frame, pressure_by_component


def wellbore_schematic(drill_string, bottom_hole_assembly, casing_design, open_hole_size):

    annulus_inner_diameter_profile = DiameterProfile(casing_design,
                                                     drill_string,
                                                     bottom_hole_assembly,
                                                     open_hole_size)
    drill_string_outer_diameter_profile = DiameterProfile(casing_design,
                                                          drill_string,
                                                          bottom_hole_assembly,
                                                          open_hole_size)
    drill_string_inner_diameter_profile = DiameterProfile(casing_design,
                                                          drill_string,
                                                          bottom_hole_assembly,
                                                          open_hole_size)

    x_annulus = (np.array(annulus_inner_diameter_profile.annulus_outer_diameters())) / 2
    x2_annulus = -x_annulus
    y_annulus = annulus_inner_diameter_profile.annulus_depths()

    x_drillpipe = (np.array(drill_string_outer_diameter_profile.drill_string_outer_diameters())) / 2
    x2_drillpipe = -x_drillpipe
    y_drillpipe = drill_string_outer_diameter_profile.drill_string_depths()

    x_drillpipe_inner = (np.array(drill_string_inner_diameter_profile.drill_string_inner_diameters())) / 2
    x2_drillpipe_inner = -x_drillpipe_inner
    y_drillpipe_inner = drill_string_inner_diameter_profile.drill_string_depths()

    plt.plot(x_annulus, y_annulus, '', x2_annulus, y_annulus, color='black', linestyle='solid', linewidth=1)
    plt.plot(x_annulus, y_annulus, '', x_annulus, y_annulus, color='black', linestyle='solid', linewidth=1)

    plt.plot(x_drillpipe, y_drillpipe, '', x2_drillpipe, y_drillpipe, color='black', linestyle='solid', linewidth=1)
    plt.plot(x_drillpipe, y_drillpipe, '', x_drillpipe, y_drillpipe, color='black', linestyle='solid', linewidth=1)

    plt.plot(x_drillpipe_inner, y_drillpipe_inner, '', x2_drillpipe_inner, y_drillpipe_inner, color='black',
             linestyle='solid', linewidth=1)
    plt.plot(x_drillpipe_inner, y_drillpipe_inner, '', x_drillpipe_inner, y_drillpipe_inner, color='black',
             linestyle='solid', linewidth=1)

    plt.gca().invert_yaxis()
    plt.gcf().set_size_inches(2, 6, forward=True)
    plt.tick_params(labelsize=6, labelrotation=90)
    plt.savefig(wellbore_schematic_image_directory)
    plt.close()


def ecd_profile_chart(result_array):  # plots a chart that shows measured depth vs ecd
    array = np.genfromtxt(result_array, delimiter=',', skip_header=1)
    output_file(ecd_chart_directory)
    lines_to_skip: int = 10
    measured_depth = array[lines_to_skip:, columns.names['composite_list_columns_md']]
    ecd = array[lines_to_skip:, columns.names['composite_list_columns_equivalent_circulating_density']]
    tool_tips = [("(x,y)", "(@x{1.11} ppg, @y ft)")]
    ecd_chart = figure(plot_width=400, plot_height=400, tooltips=tool_tips, title="ECD Along the Wellbore")
    ecd_chart.line(ecd, measured_depth, line_width=2)
    ecd_chart.y_range.flipped = True
    ecd_chart.xaxis.axis_label = "ECD, ppg"
    ecd_chart.yaxis.axis_label = "MD, ft"
    save(ecd_chart)


def ecd_profile_zoomed_chart(result_array):  # plots a chart that shows measured depth vs ecd zoomed to lateral
    array = results_csv_loader(result_array)
    output_file(ecd_chart_zoomed_directory)
    lines_to_skip: int = 10
    inc = array[lines_to_skip:, columns.names['composite_list_columns_inc']]
    threshold = 70
    itemindex = np.where(inc > threshold)
    inclination_horizontal = itemindex[0][0]  # finds the index of row where inclination exceeds 70 degrees
    measured_depth = array[inclination_horizontal:, columns.names['composite_list_columns_md']]
    ecd = array[inclination_horizontal:, columns.names['composite_list_columns_equivalent_circulating_density']]
    tool_tips = [("(x,y)", "(@x{1.11} ppg, @y ft)")]
    ecd_chart_z = figure(plot_width=400, plot_height=400, tooltips=tool_tips,
                         title="ECD Along the Wellbore (Lateral Zoom)")
    ecd_chart_z.line(ecd, measured_depth, line_width=2)
    ecd_chart_z.y_range.flipped = True
    ecd_chart_z.xaxis.axis_label = "ECD, ppg"
    ecd_chart_z.yaxis.axis_label = "MD, ft"
    save(ecd_chart_z)


def pipe_pressure_drop_chart(result_array):
    array = results_csv_loader(result_array)
    output_file(pipe_pressure_drop_chart_directory)
    lines_to_skip: int = 10
    measured_depth = array[lines_to_skip:, columns.names['composite_list_columns_md']]
    pipe_pressure_drop = array[lines_to_skip:, columns.names['composite_list_columns_cumulative_pipe_pressure_drop']]
    tool_tips = [("(x,y)", "(@x{1.1} psi, @y ft)")]
    pipe_p_drop = figure(plot_width=400, plot_height=400, tooltips=tool_tips,
                         title="Total P Drop in Surf. Lines, Drill String, BHA and Bit")
    pipe_p_drop.line(pipe_pressure_drop, measured_depth, line_width=2)
    pipe_p_drop.y_range.flipped = True
    pipe_p_drop.xaxis.axis_label = "Pressure Drop, psi"
    pipe_p_drop.yaxis.axis_label = "MD, ft"
    save(pipe_p_drop)


def annular_pressure_drop_chart(result_array):
    array = results_csv_loader(result_array)
    output_file(annular_pressure_drop_chart_directory)
    lines_to_skip: int = 10
    measured_depth = array[lines_to_skip:, columns.names['composite_list_columns_md']]
    annular_pressure_drop = array[lines_to_skip:,
                            columns.names['composite_list_columns_cumulative_annular_pressure_drop']]
    tool_tips = [("(x,y)", "(@x{1.1} psi, @y ft)")]
    annular_p_drop = figure(plot_width=400, plot_height=400, tooltips=tool_tips, title="Annular Pressure Drop")
    annular_p_drop.line(annular_pressure_drop, measured_depth, line_width=2)
    annular_p_drop.y_range.flipped = True
    annular_p_drop.xaxis.axis_label = "Pressure Drop, psi"
    annular_p_drop.yaxis.axis_label = "MD, ft"
    save(annular_p_drop)


def pump_pressure_chart(result_array):
    array = results_csv_loader(result_array)
    output_file(pump_pressure_chart_directory)
    lines_to_skip: int = 10
    measured_depth = array[lines_to_skip:, columns.names['composite_list_columns_md']]
    pump_pressure_drop = array[lines_to_skip:, columns.names['composite_list_columns_pump_pressure']]
    tool_tips = [("(x,y)", "(@x{1.1} psi, @y ft)")]
    annular_p_drop = figure(plot_width=400, plot_height=400, tooltips=tool_tips, title="Estimated Pump Pressure")
    annular_p_drop.line(pump_pressure_drop, measured_depth, line_width=2)
    annular_p_drop.y_range.flipped = True
    annular_p_drop.xaxis.axis_label = "Pump Pressure, psi"
    annular_p_drop.yaxis.axis_label = "MD, ft"
    save(annular_p_drop)


def tvd_vs_chart():
    mincurve.generate_full_directional_plan(input_directional_plan_directory)
    array = np.genfromtxt(output_directional_directory, delimiter=',', skip_header=1)
    output_file(tvd_verticalsec_chart_directory)
    lines_to_skip: int = 1
    tvd = array[lines_to_skip:, 3]
    distance = array[lines_to_skip:, 8]
    md = array[lines_to_skip:, 0]
    source = ColumnDataSource(data={
        'TVD': tvd,
        'VS': distance,
        'MD': md})
    # tool_tips = [("(x,y)", "(@x{1.1} Closure Distance, ft, @y TVD, ft)")]
    profile = figure(plot_width=400, plot_height=400, title="Wellbore Profile")
    profile.line(x='VS', y='TVD', line_width=2, source=source)

    profile.add_tools(HoverTool(
        tooltips=[
            ('TVD', '@TVD{1} ft'),
            ('VS', '@VS{1} ft'),  # use @{ } for field names with spaces
            ('MD', '@MD{1} ft'),
        ],
    ))

    profile.y_range.flipped = True
    profile.xaxis.axis_label = "Closure Distance, ft"
    profile.yaxis.axis_label = "TVD, ft"
    save(profile)


def pressure_pie_chart(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles, shear_rate, shear_stress,
                       fluid_type, yield_stress_tao_y_input, consistency_index_k_input, fluid_behavior_index_m,
                       mud_density_input, flow_rate_q_input):

    tablescreator = ReportContentCreator(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles,
                                         shear_rate, shear_stress, fluid_type, yield_stress_tao_y_input,
                                         consistency_index_k_input, fluid_behavior_index_m, mud_density_input,
                                         flow_rate_q_input)
    sumtable = tablescreator.result_summary_table()
    sumtable = sumtable.T.to_dict('list')
    for key in sumtable:
        sumtable[key] = sumtable[key][0]
    del sumtable['Est. Pump Pressure']

    output_file(pressure_by_component)
    x = sumtable

    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'component'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = Category20c[len(x)]

    p = figure(plot_height=350, title="Pressure Drop by Component", toolbar_location=None,
               tools="hover", tooltips="@component: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='component', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    save(p)


def data_frame_creator(result_array):
    array = results_csv_loader(result_array)
    array = np.delete(array, [3, 4, 5, 6, 7], 1)
    length = array.shape
    row_count = length[0] +1
    df = pd.DataFrame(data = array, index=[np.arange(1, row_count)], columns=columns.dataframe_columns)
    df.to_csv(output_data_frame, index=False)
