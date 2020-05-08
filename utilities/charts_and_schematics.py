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


    # annular diameter profile is divided to two. for 8" hole the lines are drawn at x_annulus=4" and x2_annulus=-4"
    x_annulus = (np.array(annulus_inner_diameter_profile.annulus_outer_diameters())) / 2
    x2_annulus = -x_annulus
    y_annulus = annulus_inner_diameter_profile.annulus_depths()


    # drill string/bha profile is divided to two. for 5" pipe the lines are drawn at x_drillpipe_outer=2.5" and x2_drillpipe_outer=-2.5"
    x_drillpipe_outer = (np.array(drill_string_outer_diameter_profile.drill_string_outer_diameters())) / 2
    x2_drillpipe_outer = -x_drillpipe_outer
    y_drillpipe = drill_string_outer_diameter_profile.drill_string_depths()

    #same as previous comment about drill pipe. This one is for the ID of the pipe
    x_drillpipe_inner = (np.array(drill_string_inner_diameter_profile.drill_string_inner_diameters())) / 2
    x2_drillpipe_inner = -x_drillpipe_inner

    # plot the annulus profile
    plt.plot(x_annulus, y_annulus, '', x2_annulus, y_annulus, color='black', linestyle='solid', linewidth=1.5)

    # plot the drill string outer diameter profile
    plt.plot(x_drillpipe_outer, y_drillpipe, '', x2_drillpipe_outer, y_drillpipe, color='black', linestyle='solid', linewidth=1)

    # plot the drill string inner diameter profile
    plt.plot(x_drillpipe_inner, y_drillpipe, '', x2_drillpipe_inner, y_drillpipe, color='black', linestyle='solid', linewidth=1)

    # fill between outer and inner diameter of the drill string
    plt.fill_betweenx(y_drillpipe,x_drillpipe_outer,x_drillpipe_inner, color="black")
    plt.fill_betweenx(y_drillpipe,x2_drillpipe_outer,x2_drillpipe_inner, color="black")

    # add annotations
    font_size = 10
    annotation_additional_distance_from_edge = open_hole_size/1.5  # last term so it doesn't overlap chart
    shoes = list()
    i = 0
    string_count = len(casing_design)
    while i < string_count:
        od = casing_design[i][columns.string_input_columns['input_list_outer_diameter']]
        innerdiam = casing_design[i][columns.string_input_columns['input_list_inner_diameter']]
        if i == (string_count - 1):
            set_depth = casing_design[i][columns.string_input_columns['input_list_bottom_depth']]
            shoes.append([od, innerdiam, casing_design[i][4], set_depth])  # 9.625" casing set at 4000'
        else:
            if casing_design[i + 1][columns.string_input_columns['input_list_top_depth']] > 0:  # evaluates if there is a liner and notes the hanger depth
                set_depth = casing_design[i + 1][columns.string_input_columns['input_list_top_depth']]
                shoes.append([od, innerdiam, "Liner Hanger", set_depth])
            else:
                set_depth = casing_design[i][columns.string_input_columns['input_list_bottom_depth']]
                shoes.append([od, innerdiam,casing_design[i][columns.string_input_columns['input_list_component_type']], set_depth])
        i += 1

    #  Annotate casing strings
    if len(shoes) > 0:
        # plot if list is not empty
        for string in shoes:
            size = string[0]
            type = string[2]
            bottom_depth = string[3]
            where_to_place_annotation_x = open_hole_size/2 + annotation_additional_distance_from_edge
            where_to_place_annotation_y = string[3]
            annotation = f'''{size}" {type} at {"{:,}".format(bottom_depth)}ft'''
            plt.text(where_to_place_annotation_x, where_to_place_annotation_y, annotation, fontsize=font_size)

    if len(shoes) > 0:
        beginning_of_open_hole = shoes[-1][3]
        td = (drill_string + bottom_hole_assembly)[-1][2]
        # annotate td
        where_to_place_annotation_x = open_hole_size/2 + annotation_additional_distance_from_edge
        where_to_place_annotation_y = td + 300  # push annotation lower 200' to prevent overlapping with BHA annotation
        annotation = f'''TD at {"{:,}".format(td)}ft'''
        plt.text(where_to_place_annotation_x, where_to_place_annotation_y, annotation, fontsize=font_size)

        if td - beginning_of_open_hole > 0:
            open_hole_annotation_depth = beginning_of_open_hole + (td - beginning_of_open_hole) / 2
            # annotate open hole
            where_to_place_annotation_x = open_hole_size/2 + annotation_additional_distance_from_edge
            where_to_place_annotation_y = open_hole_annotation_depth
            annotation = f'''{open_hole_size}" OH'''
            plt.annotate(annotation,
                         xy=(open_hole_size/2,where_to_place_annotation_y),
                         xycoords='data',xytext=(x_annulus[0]*7 + where_to_place_annotation_x, 0),
                         textcoords='offset points',
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                         horizontalalignment='left', verticalalignment='bottom')
    else:
        beginning_of_open_hole = 0  # entire well is open hole if there is not a casing string
        td = (drill_string + bottom_hole_assembly)[-1][2]
        open_hole_annotation_depth = beginning_of_open_hole + (td - beginning_of_open_hole) / 2
        # annotate open hole in the case there is no casing in the hole
        where_to_place_annotation_x = open_hole_size / 2 + annotation_additional_distance_from_edge
        where_to_place_annotation_y = open_hole_annotation_depth
        annotation = f'''{open_hole_size}" OH'''
        plt.annotate(annotation,
                     xy=(open_hole_size / 2, where_to_place_annotation_y),
                     xycoords='data', xytext=(x_annulus[0] * 7 + where_to_place_annotation_x, 0),
                     textcoords='offset points',
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                     horizontalalignment='left', verticalalignment='bottom')

    if len(bottom_hole_assembly) > 0:
        bha_annotation = bottom_hole_assembly[0][columns.string_input_columns['input_list_top_depth']]
        # plot bha annotation
        where_to_place_annotation_x = open_hole_size / 2 + annotation_additional_distance_from_edge
        where_to_place_annotation_y = bha_annotation
        annotation = f'''BHA starts at {"{:,}".format(bha_annotation)}ft'''
        plt.annotate(annotation,
                     xy=(bottom_hole_assembly[0][columns.string_input_columns['input_list_outer_diameter']] / 2, where_to_place_annotation_y),
                     xycoords='data', xytext=(x_annulus[0] * 8 + where_to_place_annotation_x, 0),
                     textcoords='offset points',
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                     horizontalalignment='left', verticalalignment='bottom')

    if len(drill_string) > 0:
        ds_annotation = drill_string[0][columns.string_input_columns['input_list_top_depth']]
        # plot drill string annotation
        where_to_place_annotation_x = open_hole_size / 2 + annotation_additional_distance_from_edge
        where_to_place_annotation_y = ds_annotation
        annotation = 'Drill String'
        # plt.text(where_to_place_annotation_x, where_to_place_annotation_y, annotation, fontsize=font_size)
        plt.annotate(annotation,
                     xy=(drill_string[0][columns.string_input_columns['input_list_outer_diameter']] / 2, where_to_place_annotation_y),
                     xycoords='data', xytext=(x_annulus[0] * 8 + where_to_place_annotation_x, 0),
                     textcoords='offset points',
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                     horizontalalignment='left', verticalalignment='bottom')

    # add triangles to indicate casing shoe depths
    for shoe in shoes:
        if shoe[2] == "Casing" or shoe[2] == "Liner":
            innerdiam = shoe[1]
            depth = shoe[3]
            pointsxright = [innerdiam/2, innerdiam/1.5, innerdiam/2]   # innerdiam/1.5 is for having a scalable size for the base of triangle
            pointsxleft = [-1*innerdiam/2, -1*(innerdiam/1.5), -1*innerdiam/2]
            pointsy = [depth, depth, depth - y_annulus[-1]*0.03]  # height is 3% of the y axis scale
            plt.fill(pointsxleft, pointsy, "black", pointsxright, pointsy, "black")

    # add squares to indicate liner hanger
    i = 0
    string_count = len(casing_design)
    while i < string_count:
        if shoes[i][2] == "Liner Hanger":
            od = shoes[i][0]
            innerdiam = shoes[i][1]
            depth = shoes[i][3]
            pointsxright = [shoes[i+1][1]/2, shoes[i][1]/2, shoes[i][1]/2, shoes[i+1][1]/2]
            pointsxleft = [-1*shoes[i+1][1]/2, -1*shoes[i][1]/2, -1*shoes[i][1]/2, -1*shoes[i+1][1]/2]
            pointsy = [depth, depth, depth-300, depth - y_annulus[-1]*0.03]  # height is 3% of the y axis scale
            plt.fill(pointsxleft, pointsy, "black", pointsxright, pointsy, "black")
        i += 1

    plt.gca().invert_yaxis()
    plt.gcf().set_size_inches(1.5, 6, forward=True)
    plt.tick_params(labelsize=6, labelrotation=90)
    plt.tick_params(axis='x',  # changes apply to the x-axis
                    which='both',  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off

    plt.savefig(wellbore_schematic_image_directory, bbox_inches='tight')
    plt.close()


def ecd_profile_chart(result_array):  # plots a chart that shows measured depth vs ecd
    array = np.genfromtxt(result_array, delimiter=',', skip_header=1)
    output_file(ecd_chart_directory)
    lines_to_skip: int = 10
    measured_depth = array[lines_to_skip:, columns.names['composite_list_columns_md']]
    ecd = array[lines_to_skip:, columns.names['composite_list_columns_equivalent_circulating_density']]
    tool_tips = [("(x,y)", "(@x{1.11} ppg, @y ft)")]
    ecd_chart = figure(plot_width=600, plot_height=600, tooltips=tool_tips, title="ECD Along the Wellbore")
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
    try:
        itemindex = np.where(inc > threshold)
        inclination_horizontal = itemindex[0][0]  # finds the index of row where inclination exceeds 70 degrees
        measured_depth = array[inclination_horizontal:, columns.names['composite_list_columns_md']]
        ecd = array[inclination_horizontal:, columns.names['composite_list_columns_equivalent_circulating_density']]
        tool_tips = [("(x,y)", "(@x{1.11} ppg, @y ft)")]
        ecd_chart_z = figure(plot_width=600, plot_height=600, tooltips=tool_tips,
                             title="ECD Along the Wellbore (Lateral Zoom)")
        ecd_chart_z.line(ecd, measured_depth, line_width=2)
        ecd_chart_z.y_range.flipped = True
        ecd_chart_z.xaxis.axis_label = "ECD, ppg"
        ecd_chart_z.yaxis.axis_label = "MD, ft"
        save(ecd_chart_z)
    except IndexError:
        return


def pipe_pressure_drop_chart(result_array):
    array = results_csv_loader(result_array)
    output_file(pipe_pressure_drop_chart_directory)
    lines_to_skip: int = 10
    measured_depth = array[lines_to_skip:, columns.names['composite_list_columns_md']]
    pipe_pressure_drop = array[lines_to_skip:, columns.names['composite_list_columns_cumulative_pipe_pressure_drop']]
    tool_tips = [("(x,y)", "(@x{1.1} psi, @y ft)")]
    pipe_p_drop = figure(plot_width=600, plot_height=600, tooltips=tool_tips,
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
    annular_p_drop = figure(plot_width=600, plot_height=600, tooltips=tool_tips, title="Annular Pressure Drop")
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
    annular_p_drop = figure(plot_width=600, plot_height=600, tooltips=tool_tips, title="Estimated Pump Pressure")
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
    profile = figure(plot_width=600, plot_height=300, title="Wellbore Profile")
    profile.line(x='VS', y='TVD', line_width=10, line_color='black',source=source)

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
                       mud_density_input, flow_rate_q_input, sheet_name, surf_class, holesize):

    tablescreator = ReportContentCreator(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles,
                                         shear_rate, shear_stress, fluid_type, yield_stress_tao_y_input,
                                         consistency_index_k_input, fluid_behavior_index_m, mud_density_input,
                                         flow_rate_q_input, sheet_name, surf_class, holesize)
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
