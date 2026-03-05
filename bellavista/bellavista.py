#Author: Annabelle Coles
#Version: KoLab-MERFISH Mouse Heart Paper

import argparse
import sys
from json import load
from pathlib import Path
from typing import Dict



import napari
from qtpy import QtWidgets

from . import input_data
from . import widget_utils

def bellavista(folder: Path, params: Dict, window_title: str):
    viewer = napari.Viewer()

    # create BellaVista widget object
    bellavista_widget = widget_utils.create_widget(viewer, folder, params)
    
    # pre-load WGA image (if given)
    if len(bellavista_widget.imgs) > 0:
        bellavista_widget._pre_load_image()


    print("Data Loaded!")

    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setWidget(bellavista_widget)

    # add BellaVista widget to right side of napari window
    viewer.window.add_dock_widget(scroll_area, name="BellaVista Widget", 
                                area='right', )
    
    

    if window_title:
        viewer.title = 'BellaVista: ' + window_title

    viewer.scale_bar.visible = True
    viewer.scale_bar.unit = 'um'
    viewer.reset_view()
    napari.run()
    print("Data Loaded!")

def main():

    parser = argparse.ArgumentParser(description='Process input file for BellaVista.')
    # user provided JSON file
    parser.add_argument('positional_input_file', type=str, nargs='?', 
                        help='Path to the input JSON file')
    parser.add_argument('-i', '--input-file', type=str)
    args = parser.parse_args()

    # user defined JSON
    input_file = args.input_file if args.input_file else args.positional_input_file
    if not input_file:
        print('Error: No input JSON file provided. You must provide an input file either as the first argument or with the -i/--input_file option.')
        parser.print_help()
        sys.exit(1)

    # load dataset-specific JSON (first argument)
    with open(input_file, 'r') as f:
        json_file = load(f)
    
    valid_dir = False
    if "data_folder" in json_file:
        data_folder = Path(json_file.get('data_folder'))
        if (data_folder.exists()) & (data_folder.is_dir()):
            valid_dir = True

    if not valid_dir:
        current_dir = Path(input_file).resolve().parent
        
        if "data_folder" in json_file:
            print(f"Path {data_folder} is not a valid directory -- will look for input files in current directory {current_dir}")
        else:
            print(f"No data folder path provided -- will look for input files in current directory {current_dir}")

        json_file["data_folder"] = current_dir
        data_folder = current_dir

    json_file_param = json_file.get('visualization_parameters')
    create_bellavista_inputs = json_file.get('create_bellavista_inputs', True)
        
    if create_bellavista_inputs:
        input_data.create_inputs(json_file)

    bellavista_output_folder = data_folder / "BellaVista_outputs"

    bellavista(
        folder = bellavista_output_folder,
        params = json_file_param,
        window_title = Path(data_folder).stem
    )

if __name__ == '__main__':
    main()