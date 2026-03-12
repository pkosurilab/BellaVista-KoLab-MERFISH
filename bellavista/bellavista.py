#Author: Annabelle Coles
#Version: KoLab-MERFISH Mouse Heart Paper

import argparse
import glob
import os
import sys
from json import load
from pathlib import Path
from typing import Dict

import napari
from qtpy import QtWidgets

from . import input_data
from . import widget_utils
from demo import download_sample_data

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

def run_demo():
    # download sample data from dropbox
    download_sample_data.main()
    
    save_folder = os.getcwd()
    folder_name = "KoLab_MERFISH_TAC_single_FOV"

    data_folder = Path(os.path.join(save_folder, folder_name))
    input_file = data_folder / "TAC_bellavista_config.json"

    # load dataset-specific JSON (first argument)
    with open(input_file, 'r') as f:
        json_file = load(f)
    
    json_file["data_folder"] = Path(input_file).resolve().parent

    return json_file

def main():

    parser = argparse.ArgumentParser(description='Process input file for BellaVista')
    
    # user provided JSON file
    parser.add_argument('positional_input_file', type=str, nargs='?', 
                        help='Path to dataset JSON config file. Use "demo" to run the sample demo dataset')
    
    parser.add_argument('-i', '--input-file', type=str, help='Path to dataset JSON config file. Use "demo" to run the sample demo dataset')
    parser.add_argument('--demo', action='store_true', help='Visualize the sample demo dataset')
    # parser.add_argument('--help', action='store_true')

    args = parser.parse_args()
    
    # If no input provided, run demo by default
    if len(sys.argv) == 1:
        print('Processing sample demo dataset')
        args.demo = True

    # "Quick Start" demo with a single sample FOV of TAC dataset
    if args.demo:
        json_file = run_demo()

    elif args.input_file or args.positional_input_file:
        input_path = args.input_file or args.positional_input_file

        if os.path.isdir(input_path):
            print("Directory provided, will look for a config.json in this folder")

            json_files = glob.glob(os.path.join(input_path, "*config.json"))
            if not json_files:
                raise FileNotFoundError(f"No JSON config file found in directory: {input_path}")
            if len(json_files) > 1:
                raise ValueError(f"Multiple JSON files found, please specify one: {json_files}")
            else:
                input_file = json_files[0]
        
        elif os.path.isfile(input_path) and input_path.endswith(".json"):
            input_file = args.input_file
            # load dataset-specific JSON (first argument)
            with open(input_file, 'r') as f:
                json_file = load(f)

        else:
            print("Unrecognized input — must be a directory or JSON config file. Will visualize the sample TAC FOV.")
            json_file = run_demo()

        current_dir = Path(input_file).resolve().parent

        if "data_folder" in json_file:
            data_folder = Path(json_file.get('data_folder'))
            if not (data_folder.exists()) & (data_folder.is_dir()):
                    print(f"Path {data_folder} is not a valid directory -- will look for dataset data in current directory {current_dir}")
                    json_file["data_folder"] = current_dir
        else:
            print(f"No data folder path provided -- will look fo dataset data in current directory {current_dir}")
            json_file["data_folder"] = current_dir
    
    data_folder = json_file["data_folder"]
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