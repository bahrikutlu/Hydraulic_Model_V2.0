from operator import itemgetter
import numpy as np
from scipy import interpolate
from utilities import column_names as columns
from minimum_curvature_method import mincurve


def results_csv_loader(pressure_drop_csv):
    array = np.genfromtxt(pressure_drop_csv, delimiter=',')
    return array


class WellTrajectory:
    def __init__(self, file_name):
        self.filename = file_name
        self.create = mincurve.generate_full_directional_plan(self.filename)
        self.load_csv = np.genfromtxt("output/directional_plan/directional_plan_processed.csv", delimiter=',', skip_header=1)
        self.measured_depths = self.load_csv[:, columns.directional_plan_column_names["measured_depth"]]
        self.inclination = self.load_csv[:, columns.directional_plan_column_names["inclination"]]
        self.azimuth = self.load_csv[:, columns.directional_plan_column_names["azimuth"]]
        self.closure_distance = self.load_csv[:, columns.directional_plan_column_names["closure_distance"]]
        self.true_vertical_depths = self.load_csv[:, columns.directional_plan_column_names["tvd"]]

    def tvd_finder(self, measured_depth):
        f = interpolate.interp1d(self.measured_depths, self.true_vertical_depths)
        return f(measured_depth)

    def inclination_finder(self, measured_depth):
        f = interpolate.interp1d(self.measured_depths, self.inclination)
        return f(measured_depth)

    def azimuth_finder(self, measured_depth):
        f = interpolate.interp1d(self.measured_depths, self.azimuth)
        return f(measured_depth)

    def closure_distance_finder(self, measured_depth):
        f = interpolate.interp1d(self.measured_depths, self.closure_distance)
        return f(measured_depth)


# well_trajectory = WellTrajectory('input/directional_plan.csv')
# print(well_trajectory.filename)
# print(well_trajectory.load_csv)
# print(well_trajectory.measured_depths)
# print(well_trajectory.true_vertical_depths)
# print(well_trajectory.tvd_finder(9700))
# print(well_trajectory.azimuth_finder(9700))
# print(well_trajectory.closure_distance_finder(15000))



def bit_depth_finder(drill_string, bottom_hole_assembly):
    entire_string = drill_string+bottom_hole_assembly
    bit_depth = 0
    for component in entire_string:
        if component[columns.string_input_columns['input_list_bottom_depth']] > bit_depth:
            bit_depth = component[columns.string_input_columns['input_list_bottom_depth']]

    return bit_depth


class DiameterProfile:
    def __init__(self, casing_design, drill_string, bottom_hole_assembly, open_hole_size):
        self.casingdesign = casing_design
        self.openholesize = open_hole_size
        self.drillstring = drill_string
        self.bha = bottom_hole_assembly
        # self.bit_info = bit
        self.entirestring = self.drillstring + self.bha
        #+ self.bit_info

    def annulus_inner_diameter_profile_calculator(self):
        # sorts the list of casing strings by third column (casing set depth)
        self.casingdesign = sorted(self.casingdesign, key=itemgetter(columns.string_input_columns['input_list_bottom_depth']))
        # logic needs to be added for error handling in case two strings are entered with top depth of zero
        well_inner_diameter_profile = []
        casing_top_depth_list = []
        for strings in self.casingdesign:
            inner_diameter = columns.string_input_columns['input_list_inner_diameter']
            diameter = inner_diameter
            well_inner_diameter_profile.append([strings[diameter], strings[columns.string_input_columns['input_list_bottom_depth']]])
            casing_top_depth_list.append(strings[columns.string_input_columns['input_list_top_depth']])
        i = 0
        for top_depth in casing_top_depth_list:
            if top_depth > 0:
                well_inner_diameter_profile[i - 1][1] = top_depth
            i += 1
        well_inner_diameter_profile.insert(0, [self.casingdesign[0][1], 0])

        i = 2
        while i < len(well_inner_diameter_profile):
            well_inner_diameter_profile.insert(i, [well_inner_diameter_profile[i][0],
                                                   well_inner_diameter_profile[i - 1][1] + 1])
            i += 2

        #append the open hole size, starting depth
        well_inner_diameter_profile.append([self.openholesize,self.casingdesign[len(self.casingdesign)-1][2]+1])
        #append the open hole size, final depth
        well_inner_diameter_profile.append([self.openholesize,self.entirestring[len(self.entirestring)-1][2]])

        #insert the hole size and td to the end
        #add the previous line as hloe size and depth+1

        return well_inner_diameter_profile

    def annulus_id_finder_with_depth_input(self, depth):
        # well_inner_diameter_profile = annulus_diameter_profile_calculator(casing_design)
        inner_diam_list = []
        depth_list = []
        for item in self.annulus_inner_diameter_profile_calculator():
            inner_diam_list.append(item[0])
            depth_list.append(item[1])

        f = interpolate.interp1d(depth_list, inner_diam_list)
        return f(depth)

    def annulus_outer_diameters(self):
        outer_diams = []
        for item in self.annulus_inner_diameter_profile_calculator():
            outer_diams.append(item[0])
        return outer_diams

    def annulus_depths(self):
        depths=[]
        for item in self.annulus_inner_diameter_profile_calculator():
            depths.append(item[1])
        return depths

    def drill_string_outer_diameter_profile_calculator(self):
        entire_string = self.entirestring
        entire_string = sorted(entire_string, key=itemgetter(columns.string_input_columns['input_list_top_depth']))
        drill_string_outer_diameter_profile = []
        drill_string_top_depth_list = []
        # columns.string_input_columns['input_list_outer_diameter'] = input_list_outer_diameter
        for tool in entire_string:
            drill_string_outer_diameter_profile.append([tool[columns.string_input_columns['input_list_outer_diameter']
], tool[columns.string_input_columns['input_list_bottom_depth']]])
            drill_string_top_depth_list.append(tool[columns.string_input_columns['input_list_top_depth']])
        i = 0
        for top_depth in drill_string_top_depth_list:
            if top_depth > 0:
                drill_string_outer_diameter_profile[i - 1][1] = top_depth
            i += 1
        drill_string_outer_diameter_profile.insert(0, [entire_string[0][columns.string_input_columns['input_list_outer_diameter']
], 0])

        i = 2
        while i < len(drill_string_outer_diameter_profile):
            drill_string_outer_diameter_profile.insert(i, [drill_string_outer_diameter_profile[i][0],
                                                   drill_string_outer_diameter_profile[i - 1][1] + 1])
            i += 2

        return drill_string_outer_diameter_profile

    def drill_string_od_finder_with_depth_input(self, depth):
        # well_inner_diameter_profile = annulus_diameter_profile_calculator(casing_design)
        outer_diam_list = []
        depth_list = []
        for item in self.drill_string_outer_diameter_profile_calculator():
            outer_diam_list.append(item[0])
            depth_list.append(item[1])

        f = interpolate.interp1d(depth_list, outer_diam_list)
        return f(depth)

    def drill_string_outer_diameters(self):
        outer_diams = []
        for item in self.drill_string_outer_diameter_profile_calculator():
            outer_diams.append(item[0])
        return outer_diams

    def drill_string_inner_diameters(self):
        inner_diams = []
        for item in self.drill_string_inner_diameter_profile_calculator():
            inner_diams.append(item[0])
        return inner_diams

    def drill_string_depths(self):
        depths=[]
        for item in self.drill_string_outer_diameter_profile_calculator():
            depths.append(item[1])
        return depths

    def drill_string_inner_diameter_profile_calculator(self):
        entire_string = self.entirestring
        entire_string = sorted(entire_string, key=itemgetter(columns.string_input_columns['input_list_top_depth']))
        drill_string_inner_diameter_profile = []
        drill_string_top_depth_list = []
        for tool in entire_string:
            drill_string_inner_diameter_profile.append([tool[columns.string_input_columns['input_list_inner_diameter']], tool[columns.string_input_columns['input_list_bottom_depth']]])
            drill_string_top_depth_list.append(tool[columns.string_input_columns['input_list_top_depth']])
        i = 0
        for top_depth in drill_string_top_depth_list:
            if top_depth > 0:
                drill_string_inner_diameter_profile[i - 1][1] = top_depth
            i += 1
        drill_string_inner_diameter_profile.insert(0, [entire_string[0][1], 0])

        i = 2
        while i < len(drill_string_inner_diameter_profile):
            drill_string_inner_diameter_profile.insert(i, [drill_string_inner_diameter_profile[i][0],
                                                   drill_string_inner_diameter_profile[i - 1][1] + 1])
            i += 2

        return drill_string_inner_diameter_profile

    def drill_string_id_finder_with_depth_input(self, depth):
        # well_inner_diameter_profile = annulus_diameter_profile_calculator(casing_design)
        inner_diam_list = []
        depth_list = []
        for item in self.drill_string_inner_diameter_profile_calculator():
            inner_diam_list.append(item[0])
            depth_list.append(item[1])

        f = interpolate.interp1d(depth_list, inner_diam_list)
        return f(depth)



