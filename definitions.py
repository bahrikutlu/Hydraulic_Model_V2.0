import errno
import os
from shutil import rmtree
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

# output folders
output_root = os.path.join(root_dir, Path('output'))
raw_results = os.path.join(root_dir, Path('output/calculation_results/raw')) #use with makedirs
charts_folder = os.path.join(root_dir, Path('output/charts'))
directional_plan_folder = os.path.join(root_dir, Path('output/directional_plan'))
output_report = os.path.join(root_dir, Path('output/output_report'))
output_plots = os.path.join(root_dir, Path('output/plots'))

# output report
output_template_html_directory = "input/report_template/output_template.html"
output_report_directory = os.path.join(root_dir, Path('output/output_report/output.html'))
cssforstyling = os.path.join(root_dir, Path('input/report_template/styles.css'))

# interactive charts
ecd_chart_directory = os.path.join(root_dir, Path('output/charts/ecd.html'))
ecd_chart_zoomed_directory = os.path.join(root_dir, Path('output/charts/ecd_zoomed.html'))
pipe_pressure_drop_chart_directory = os.path.join(root_dir, Path('output/charts/drill_pipe_pressure_drop.html'))
annular_pressure_drop_chart_directory = os.path.join(root_dir, Path('output/charts/annular_pressure_drop.html'))
pump_pressure_chart_directory = os.path.join(root_dir, Path('output/charts/pump_pressure.html'))
tvd_verticalsec_chart_directory = os.path.join(root_dir, Path('output/charts/tvd_vs_distance.html'))
pressure_by_component = os.path.join(root_dir, Path('output/charts/pressure_by_component.html'))


def silentremove_file(filename):
    try:

        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def silentremove_folder(folder):
    try:
        rmtree(folder, ignore_errors=True)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def silentremove_all_files_in_folder(folder):
    try:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred

