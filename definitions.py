import os
from pathlib import Path

# This is your Project Root
root_dir = os.path.dirname(os.path.abspath(__file__))

# inputs
input_well = os.path.join(root_dir, Path('input/input.xlsx'))
input_directional_plan_directory = os.path.join(root_dir, Path('input/directional_plan.csv'))

# output files raw and with header
output_raw_field_units = os.path.join(root_dir, Path('output/calculation_results/raw/pressure_drop_field.csv'))
output_raw_si_units = os.path.join(root_dir, Path('output/calculation_results/raw/pressure_drop_si.csv'))
output_data_frame = os.path.join(root_dir, Path('output/calculation_results/output.csv'))
output_directional_directory = os.path.join(root_dir, Path('output/directional_plan/directional_plan_processed.csv'))

# static images
wellbore_schematic_image_directory = os.path.join(root_dir, Path('output/plots/wellbore_schematic.png'))
flow_curve_image_directory = os.path.join(root_dir, Path('output/plots/flow_curve.png'))

# output report
output_template_html_directory = "output/report_template/output_template.html"
output_report_directory = os.path.join(root_dir, Path('output/output_report/output.html'))

# interactive charts
ecd_chart_directory = os.path.join(root_dir, Path('output/charts/ecd.html'))
ecd_chart_zoomed_directory = os.path.join(root_dir, Path('output/charts/ecd_zoomed.html'))
pipe_pressure_drop_chart_directory = os.path.join(root_dir, Path('output/charts/drill_pipe_pressure_drop.html'))
annular_pressure_drop_chart_directory = os.path.join(root_dir, Path('output/charts/annular_pressure_drop.html'))
pump_pressure_chart_directory = os.path.join(root_dir, Path('output/charts/pump_pressure.html'))
tvd_verticalsec_chart_directory = os.path.join(root_dir, Path('output/charts/tvd_vs_distance.html'))



