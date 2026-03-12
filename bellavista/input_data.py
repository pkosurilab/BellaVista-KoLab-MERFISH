#Author: Annabelle Coles
#Version: KoLab-MERFISH Mouse Heart Paper

import logging
import json
import os  
from datetime import datetime
from pathlib import Path
from typing import Dict

import zarr
from dask_image.imread import imread
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image

def setup_logger(bellavista_output_folder: str):
    # Remove any handlers that were set up earlier
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    # Set a log file in the output folder
    logging.basicConfig(filename=os.path.join(bellavista_output_folder, 'error_log.log'),  # Absolute path
                        level=logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def create_inputs(json_file: Dict):

    '''
        Create input files for visualization in BellaVista.

        The list of transformation is used to write registered images and 
        the transformation list is archived.

        Args:
            json_file: A dictionary storing input file parameters parsed from user's input JSON file.

    '''

    data_folder = Path(json_file.get('data_folder'))
    if not data_folder.is_dir():
        raise FileNotFoundError(f'Directory {data_folder} does not exist.')

    json_file_input_files = json_file.get('input_files')

    bellavista_output_folder = data_folder / "BellaVista_outputs"

    if not bellavista_output_folder.is_dir():
        print(f'"BellaVista_outputs" does not exist -- creating the directory!')
        os.makedirs(bellavista_output_folder)

    setup_logger(bellavista_output_folder)

    from . import input_data_kolab

    

    args = [data_folder, json_file_input_files]
    
    # system = json_file.get('system')
    # if (system.lower() == 'kolabmerfish'):

    print('Creating BellaVista input files for KoLab-MERFISH:')
    um_px_transforms = input_data_kolab.create_micron_pixel(*args)
    create_ome_zarr(*args, transforms=um_px_transforms)
    input_data_kolab.create_transcripts(*args)
    input_data_kolab.process_segmentations(*args)
    input_data_kolab.process_network_graph_celltype(*args)

    print('BellaVista input files created!', end='\n\n')


def create_ome_zarr(data_folder: Path, json_file_input_files: Dict, transforms: Dict):
    '''
        Converts TIFF to multiscale pyramidal OME-Zarr images.

        Args:
            data_folder: Path to folder containing dataset files.
            json_file_input_files: A dictionary storing input file parameters parsed from user's input JSON file, containing image paths.
            transforms: @ BELLA FILL THIS IN !!
            
        '''

    bellavista_output_folder = data_folder / "BellaVista_outputs"
    images = json_file_input_files.get('images')

    if images is None:
        print('No image files provided, skipping image processing')
        return

    try:
        # print('Creating OME-Zarr Images')
        if isinstance(images, str):
            images = [images]
        
        z_plane = json_file_input_files.get('z_plane', 0)
        
        # if images have been processed previously, exit early
        ome_zarr_path = bellavista_output_folder / "Images.zarr"
        store = parse_url(ome_zarr_path, mode="a").store
        root = zarr.group(store=store)

        existing_images = list(root.group_keys())
        file_names = [Path(Path(file).stem).stem.replace("_", " ") for file in images]
        previously_processed = list(set(existing_images).intersection(set(file_names)))
        if len(previously_processed) > 0:
            print(f"{', '.join(previously_processed)} image(s) processed previously. Skipping reprocessing.")

        
        for image in images:
            file_name = Path(image).stem

            if not file_name in root.group_keys():
                print(f"Processing {file_name} image...", end="", flush=True)
                data = imread(data_folder / image)

                if data.ndim == 2:
                    data = data[None, ...]  # add z-axis
                
                elif data.shape[0] == 1:
                    data = data

                elif z_plane < data.shape[0]:
                    data = data[z_plane:z_plane+1]
                
                else:
                    print(f" Warning: z_plane {z_plane} out of range for {file_name}. Using first plane.")
                    data = data[0:1]

                transforms["px_val_min"] = data.min().compute()
                transforms["px_val_max"] = data.max().compute()

                zarr_group = root.create_group(file_name)

                write_image(
                    image=data,
                    group=zarr_group,
                    axes="zyx",
                    chunks=(1,1024, 1024),
                    metadata=transforms
                )
                print(f' {file_name} OME-Zarr image saved successfully!')
            
    except Exception as e:
        print(f'An error occurred during create_ome_zarr.')
        print(f'Please check the log file for details: {(bellavista_output_folder / "error_log.log")}', end='\n\n')
        logging.error(f'Error in create_ome_zarr: {e}', exc_info=True)
    
    return