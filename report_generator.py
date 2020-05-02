from jinja2 import Environment, FileSystemLoader
import pandas as pd
from utilities import excel_input_import as inputs
from definitions import output_template_html_directory, output_report_directory

simulation_name = 'well2' # THIS IS THE ONLY VARIABLE THAT NEEDS TO BE CHANGED IN CODE
importer = inputs.ImportFromExcel(simulation_name)

casing_design = importer.all_casing_strings()
drill_string = importer.all_drill_strings()
bottom_hole_assembly = importer.all_bha()
bit = importer.bit()


class ReportCreator:
    def __init__(self, casing_design, drill_string, bha, bit):
        self.casing = casing_design
        self.drillpipe = drill_string
        self.bottomholeass = bha
        self.drillbit = bit

    def casing_table(self):
        header = ["Name", "OD, in", "ID, in", "Set Depth, ft", "Top Depth, in"]
        for casing in self.casing:
            casing.insert(0, casing.pop(4))

        self.casing.insert(0, header)
        df = (pd.DataFrame(data=self.casing))
        return df

    def drillstring_and_bha_table(self):
        header = ["Name", "OD, in", "ID, in", "Bottom Depth, ft", "Top Depth, in"]
        for pipe in self.drillpipe:
            pipe.insert(0, pipe.pop(4))
        self.drillpipe.insert(0, header)

        for pipe in self.bottomholeass:
            pipe.insert(0, pipe.pop(4))

        if self.drillbit is not None:
            self.drillbit[0].insert(0, "Bit")

        df = (pd.DataFrame(data=(self.drillpipe+self.bottomholeass+self.drillbit)))
        return df




htmlreport = ReportCreator(casing_design,drill_string,bottom_hole_assembly, bit)


env = Environment(loader=FileSystemLoader('.'))
template = env.get_template(output_template_html_directory)
casing = htmlreport.casing_table()
stringbha = htmlreport.drillstring_and_bha_table()

template_vars = {"title": "Hydraulics Report",
                 "casing_table": casing.to_html(header=False, index=False),
                 "drill_string_and_bha_table": stringbha.to_html(header=False, index=False)}

html_out = template.render(template_vars)


with open(output_report_directory, "w") as result_file:
    result_file.write(html_out)

print("done")


