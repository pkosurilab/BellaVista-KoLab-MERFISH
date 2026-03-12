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

def run_demo():
    print("Running Quick Start Demo!")
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

    return json_file, input_file


def select_json_config(json_files):
    print("Multiple possible JSON config files found in folder, please select one:")
    for i, f in enumerate(json_files, 1):
        print(f"  {i}. {f}")
    print(f"  {len(json_files) + 1}. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter number: "))
            if choice == len(json_files) + 1:
                print("Exiting...")
                sys.exit(0)
            elif 1 <= choice <= len(json_files):
                return json_files[choice - 1]
        except ValueError:
            pass
        print("Invalid choice, try again.")

def main():

    parser = argparse.ArgumentParser(description='Process input file for BellaVista')
    
    # user provided JSON file
    parser.add_argument('positional_input_file', type=str, nargs='?', 
                        help='Path to dataset JSON config file. Use "demo" to run the sample demo dataset')
    
    parser.add_argument('-i', '--input-file', type=str, help='Path to dataset JSON config file. Use "demo" to run the sample demo dataset')
    parser.add_argument('--demo', action='store_true', help='Visualize the sample demo dataset')

    args = parser.parse_args()
    
    # If no input provided, run demo by default
    if len(sys.argv) == 1:
        args.demo = True

    # "Quick Start" demo with a sample FOV from the TAC dataset
    if args.demo:
        json_file, input_file = run_demo()

    elif args.input_file or args.positional_input_file:
        input_path = args.input_file or args.positional_input_file

        if os.path.isdir(input_path):
            print("Directory provided, will look for a config.json in this folder")
            json_files = glob.glob(os.path.join(input_path, "*config*.json"))
            if not json_files:
                raise FileNotFoundError(f"No JSON files found in directory: {input_path}")
            if len(json_files) > 1:
                input_file = select_json_config(json_files)
            else:
                input_file = json_files[0]

            with open(input_file, 'r') as f:
                json_file = load(f)

            if not "data_folder" in json_file:
                current_dir = Path(input_file).resolve().parent
                print(f"No 'data_folder' path specified in config -- looking for dataset files in {current_dir}")
                json_file["data_folder"] = current_dir

        elif os.path.isfile(input_path) and input_path.endswith(".json"):
            
            input_file = input_path
            current_dir = Path(input_file).resolve().parent

            with open(input_file, 'r') as f:
                json_file = load(f)

            if not "data_folder" in json_file:
                print(f"No 'data_folder' path specified in config -- looking for dataset files in {current_dir}")
                json_file["data_folder"] = current_dir

        else:
            print("Unrecognized input — must be a directory or JSON config file. Will visualize the sample TAC FOV.")
            json_file, input_file = run_demo()

        data_folder = Path(json_file.get('data_folder'))
        if not (data_folder.exists() and data_folder.is_dir()):
            current_dir =  Path(input_file).resolve().parent
            print(f"Data folder {data_folder} provided is not a valid directory -- looking for dataset files in {current_dir}")
            json_file["data_folder"] = current_dir

    data_folder = Path(json_file["data_folder"])
    json_file_param = json_file.get('visualization_parameters')
    create_bellavista_inputs = json_file.get('create_bellavista_inputs', True)
        
    if create_bellavista_inputs:
        input_data.create_inputs(json_file)

    bellavista_output_folder = data_folder / "BellaVista_outputs"

    bellavista(
        folder = bellavista_output_folder,
        params = json_file_param,
        window_title = data_folder.stem
    )

if __name__ == '__main__':
    main()