from jinja2 import Environment, FileSystemLoader
import pandas as pd
import numpy as np
from utilities.column_names import string_input_columns

from model_engine.rheological_model_parameters import rheological_parameters
from model_engine.surface_bit_bha_pressure_drop import tfa_calculator, surface_pressure_drop, mwd_pressure_drop, \
    mud_motor_pressure_drop, bit_pressure_drop_psi
from utilities import excel_input_import as inputs
from definitions import output_template_html_directory, output_report_directory, wellbore_schematic_image_directory, \
    flow_curve_image_directory, output_data_frame

simulation_name = 'well2' # THIS IS THE ONLY VARIABLE THAT NEEDS TO BE CHANGED IN CODE
importer = inputs.ImportFromExcel(simulation_name)

casing_design = importer.all_casing_strings()
drill_string = importer.all_drill_strings()
bottom_hole_assembly = importer.all_bha()
bit = importer.bit()
bit_nozzles = importer.all_bit_nozzles()
shear_rate = importer.viscometer_readings()[0]
shear_stress = importer.viscometer_readings()[1]
fluid_type = importer.fluid_type()
mud_density_input = importer.mud_weight()
flow_rate_q_input = importer.flow_rate()

yield_stress_tao_y_input = rheological_parameters(shear_rate,
                                                  shear_stress,
                                                  fluid_type)[0]

consistency_index_k_input = rheological_parameters(shear_rate,
                                                   shear_stress,
                                                   fluid_type)[1]  # (lbf*s^m/100ft2)

fluid_behavior_index_m = rheological_parameters(shear_rate,
                                                shear_stress,
                                                fluid_type)[2]


class ReportContentCreator:
    def __init__(self, casing_design, drill_string, bha, bit, nozzles, shear_rate, shear_stress, fluid_type, taoy,
                 k, m, mud_weight, flow_rate):
        self.casing = casing_design
        self.drillpipe = drill_string
        self.bottomholeass = bha
        self.drillbit = bit
        self.bitnozzles = nozzles
        self.sr = shear_rate
        self.ss = shear_stress
        self.fluidtype = fluid_type
        self.yieldstress = taoy
        self.k_index = k
        self.behaviorindex = m
        self.density = mud_weight
        self.flowrate = flow_rate

    def casing_table(self):
        header = ["OD, in", "ID, in", "Set Depth, ft", "Top Depth, in"]
        index_name = []
        for item in self.casing:
            index_name.append(item.pop(string_input_columns['input_list_component_type']))

        df = (pd.DataFrame(data=self.casing, columns=header, index=index_name))
        return df

    def drillstring_and_bha_table(self):
        header = ["OD, in", "ID, in", "Bottom Depth, ft", "Top Depth, in"]
        index_name = []
        for pipe in self.drillpipe:
            # deleting duplicate column created above
            index_name.append(pipe.pop(string_input_columns['input_list_component_type']))

        for pipe in self.bottomholeass:
            # deleting duplicate column created above
            index_name.append(pipe.pop(string_input_columns['input_list_component_type']))

        if self.drillbit is not None:
            index_name.append("Bit")

        df = (pd.DataFrame(data=(self.drillpipe+self.bottomholeass+self.drillbit), columns=header, index=index_name))
        return df

    def bit_nozzle_table(self):
        nozzle_count = len(self.bitnozzles)
        rangeofheader = list(np.arange(1, nozzle_count + 1))
        rangeofheader.append("TFA, sqin")
        tfa = round(tfa_calculator(self.bitnozzles),2)
        nozzle = self.bitnozzles
        nozzle.append(tfa)
        data = [nozzle]
        df = pd.DataFrame(data=data, columns=rangeofheader)
        return df

    def viscometer_readings_table(self):
        header = ["RPM", "Reading, lb/100ft2"]
        self.sr[:] = [x / 1.7 for x in self.sr]
        df = (pd.DataFrame(data=(self.sr, self.ss), index=header)).astype(int)
        return df

    def fluid_properties(self):
        headers = ['Yield Stress (lb/100ft^2)', 'Consistency Index (lb*s^m/100sqft)', 'Fluid Behavior Index']
        properties = [round(self.yieldstress,3), round(self.k_index,3), round(self.behaviorindex,3)]
        if fluid_type == 'PL':
            headers.pop(0)
            properties.pop(0)
        df = pd.DataFrame(data=properties).T
        df.columns = headers
        return df

    def result_summary_table(self):
        header_pressure = ['Pressure, psi']
        index_name_pressure = ['Surface Lines', 'Drill String', 'MWD', 'Motor', 'Bit', 'Annulus', 'Est. Pump Pressure']
        read_data=pd.read_csv(output_data_frame)
        data = read_data.set_index("MD", drop=False)
        annulus_p_drop = int(data.iloc[-1]["Annular P Drop"])
        surface_p_drop = int(surface_pressure_drop())
        mwd_p_drop = int(mwd_pressure_drop())
        motor_p_drop = int(mud_motor_pressure_drop())
        bit_p_drop = int(bit_pressure_drop_psi(self.bitnozzles,self.density,self.flowrate))
        dp_p_drop = int(data.iloc[-1]["Pipe P Drop"]) - surface_p_drop - mwd_p_drop - motor_p_drop - bit_p_drop
        pump_pressure = dp_p_drop + annulus_p_drop + surface_p_drop + mwd_p_drop + motor_p_drop + bit_p_drop
        df_p_drop = (pd.DataFrame(data=(surface_p_drop, dp_p_drop, mwd_p_drop, motor_p_drop, bit_p_drop, annulus_p_drop,
                                        pump_pressure), columns=header_pressure, index=index_name_pressure))
        return df_p_drop

    def ecd_table(self):
        header_ecd = ['ECD, ppg']
        index_name_ecd = ['ECD at Shoe','ECD at Bottom Hole']
        read_data=pd.read_csv(output_data_frame)
        data = read_data.set_index("MD", drop=False)
        ecd_td = round(data.iloc[-1]["ECD"], 2)
        if len(self.casing) > 0:
            shoe_depth = self.casing[-1][string_input_columns['input_list_bottom_depth']]
            ecd_shoe = round(data.loc[shoe_depth, "ECD"], 2)
        else:
            ecd_shoe = "-"
        df_ecd = (pd.DataFrame(data=(ecd_shoe,ecd_td), columns=header_ecd, index=index_name_ecd))
        return df_ecd


def html_report_creator(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles, shear_rate,
                        shear_stress, fluid_type, yield_stress_tao_y_input, consistency_index_k_input,
                        fluid_behavior_index_m, mud_density_input, flow_rate_q_input):

    htmlreport = ReportContentCreator(casing_design, drill_string, bottom_hole_assembly, bit, bit_nozzles, shear_rate,
                                      shear_stress, fluid_type, yield_stress_tao_y_input, consistency_index_k_input,
                                      fluid_behavior_index_m, mud_density_input, flow_rate_q_input)

    stringbha = htmlreport.drillstring_and_bha_table()
    bittable = htmlreport.bit_nozzle_table()
    viscreading = htmlreport.viscometer_readings_table()
    sumtable = htmlreport.result_summary_table()
    ecdtable = htmlreport.ecd_table()  # this goes before casing table. Process this before htmlreport.casing_table()
    casing = htmlreport.casing_table()
    fluidproperties = htmlreport.fluid_properties()

    template_vars = {"title": "Hydraulics Report",
                     "casing_table": casing.to_html(header=True, index=True),
                     "drill_string_and_bha_table": stringbha.to_html(header=True, index=True),
                     "wellboreschematic": wellbore_schematic_image_directory,
                     "flowcurve": flow_curve_image_directory,
                     "bit_table": bittable.to_html(index=False),
                     "viscometer_reading": viscreading.to_html(header=False),
                     "summary_table": sumtable.to_html(header=True, index=True),
                     "ecd_table": ecdtable.to_html(header=True, index=True),
                     "fluid_properties": fluidproperties.to_html(header=True, index=False)
                     }

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(output_template_html_directory)
    html_out = template.render(template_vars)
    with open(output_report_directory, "w") as result_file:
        result_file.write(html_out)
