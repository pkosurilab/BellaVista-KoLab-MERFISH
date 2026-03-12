#Author: Annabelle Coles
#Version: KoLab-MERFISH Mouse Heart Paper

import logging
import os
import pickle
from collections import defaultdict
from json import load
from pathlib import Path
from typing import Dict

import h5py
import pandas as pd
import numpy as np
import shapely
from tqdm import tqdm

def create_micron_pixel(data_folder: str, json_file_input_files: Dict):
    microscope_parameters = json_file_input_files.get('microscope_parameters')
    bellavista_output_folder = data_folder / "BellaVista_outputs"

    if microscope_parameters is None: 
        
        print('No microscope parameter file provided, skipping processing. Micron per pixel value will be set to 1.')
        logging.warning(f'MISSING INPUT FILE: No microscope parameter file provided --> cannot process micron to pixel transforms. micron per pixel will be set to 1')
        return {}

    try:
        # print('Calculating micron to pixel transform')
        with open(os.path.join(data_folder, microscope_parameters), 'r') as f:
            microscope_parameters = load(f)

        um_per_pixel = float(microscope_parameters.get('microns_per_pixel'))
        # find coordinates of left-most, top coordinate of the imaging area 
        minx = float(microscope_parameters.get('min_x'))
        miny = float(microscope_parameters.get('min_y'))

        um_to_px_transform_dict = {'um_per_pixel_x': um_per_pixel, 'um_per_pixel_y': um_per_pixel, 'x_shift': minx, 'y_shift': miny}

    except Exception as e: 
        # Log the exception with traceback
        print(f'An error occurred during create_micron_pixel.')
        print(f'Please check the log file for details: {os.path.join(bellavista_output_folder, "error_log.log")}', end='\n\n')
        logging.error(f'Error in create_micron_pixel: {e}', exc_info=True)
        return {}
    return um_to_px_transform_dict


def create_transcripts(data_folder: str, json_file_input_files: Dict):

    '''
        Saves HDF5 file with transcript coordinates for each gene. This will be used when loading transcripts in napari.

        Args:
            data_folder: Path to folder containing dataset files.
            json_file_input_files: A dictionary storing input file parameters parsed from user's input JSON file containg path to transcript file(s).

    '''

    bellavista_output_folder = data_folder / "BellaVista_outputs"
    transcript_filenames = json_file_input_files.get('transcript_files')

    if transcript_filenames is None:
        print('No transcript files provided, skipping transcript processing.')
        return


    try: 
        if isinstance(transcript_filenames, str):
            transcript_filenames = [transcript_filenames]
        
        with h5py.File(bellavista_output_folder / 'transcripts.hdf5', 'a') as f:

            if "Transcripts" not in f:
                txs_group = f.create_group("Transcripts")
            else:
                txs_group = f["Transcripts"]

            # Load existing genes if any
            all_genes = set()
            if "Genes" in txs_group:
                existing_genes = list(txs_group["Genes"][:])
                # Decode bytes to str if needed
                all_genes.update(g.decode() if isinstance(g, bytes) else g for g in existing_genes)

            # create hdf5 group
            if "Category" not in txs_group:
                categories = txs_group.create_group("Category")
            else:
                categories = txs_group["Category"]
            
            existing_txs_categories = list(categories.keys())
            file_names = [Path(Path(file).stem).stem.replace("_", " ") for file in transcript_filenames]
            previously_processed = list(set(existing_txs_categories).intersection(set(file_names)))
            if len(previously_processed) > 0:
                print(f"{', '.join(previously_processed)} processed previously. Skipping reprocessing.")

            for file in transcript_filenames:
                try:
                    txs_category = Path(Path(file).stem).stem
                    txs_category = txs_category.replace("_", " ")
                    
                    if not txs_category in categories:
                        if(str(file).endswith(".csv")): 
                            txs = pd.read_csv(data_folder / file)
                        elif(str(file).endswith(".csv.gz")): 
                            txs = pd.read_csv(data_folder / file)
                        elif(str(file).endswith(".parquet")): 
                            txs = pd.read_parquet(data_folder / file)
                        
                        else:
                            print(f'Invalid file type: {file}, skipping this file')
                            continue
                        
                        all_genes.update(txs["gene"].astype(str))
                        
                        barcodes = categories.create_group(txs_category)
                        for gene, group in tqdm(txs.groupby('gene'), total=txs['gene'].nunique(), desc=f"Processing {file}"):
                            coords = group[['global_y', 'global_x']].values
                            barcodes.create_dataset(str(gene), data=coords)
                    
                except Exception as e: 
                    # Log the exception with traceback
                    print(f'An error occurred while processing {file}')
                    print(f'Please check the log file for details: {os.path.join(bellavista_output_folder, "error_log.log")}', end='\n\n')
                    logging.error(f'Error in create_transcripts while processing {file}: {e}', exc_info=True)
                    continue
            
            # update gene list
            if "Genes" in txs_group:
                del txs_group["Genes"]  # replace old dataset
            txs_group.create_dataset("Genes", data=list(sorted(all_genes)))

            # set empty gene coord lists to absent genes in a transcript categories
            for txs_category in categories:
                genes_in_ds = list(categories[txs_category].keys())
                genes_missing = set(all_genes).difference(set(genes_in_ds))

                for gene in genes_missing:
                    categories[txs_category].create_dataset(str(gene), data=[])

    except Exception as e: 
        # Log the exception with traceback
        print(f'An error occurred during create_transcripts.')
        print(f'Please check the log file for details: {os.path.join(bellavista_output_folder, "error_log.log")}', end='\n\n')
        logging.error(f'Error in create_transcripts: {e}', exc_info=True)
        return

    return

def process_segmentations(data_folder: str, json_file_input_files: Dict):

    '''
        Saves HDF5 with transcript coordinates for each gene. This will be used when loading transcripts in napari. 

        Args:
            data_folder: Path to folder containing dataset files.
            json_file_input_files: A dictionary storing input file parameters parsed from user's input JSON file containg path to transcript file(s).

    '''

    bellavista_output_folder = data_folder / "BellaVista_outputs"

    segmentation_filenames = json_file_input_files.get('segmentation_files')

    if segmentation_filenames is None:
        print('No segmentation files provided, skipping segmentation processing.')
        return
    try:
        if isinstance(segmentation_filenames, str):
            segmentation_filenames = [segmentation_filenames]

        with h5py.File(bellavista_output_folder / 'segmentations.hdf5', 'a') as f:

            seg_group = f.require_group("Segmentations")
            categories = seg_group.require_group("Category")

            existing_seg_categories = list(categories.keys())
            file_names = [Path(Path(file).stem).stem.replace("_", " ") for file in segmentation_filenames]
            previously_processed = list(set(existing_seg_categories).intersection(set(file_names)))
            if len(previously_processed) > 0:
                print(f"{', '.join(previously_processed)} processed previously. Skipping reprocessing.")

            for file in segmentation_filenames:
                
                try:
                    seg_category = Path(Path(file).stem).stem
                    seg_category = seg_category.replace("_", " ")

                    if not seg_category in categories:
                    
                        if(str(file).endswith(".parquet")): 
                            cell_df = pd.read_parquet(data_folder / file)
                        elif(str(file).endswith(".csv")): 
                            cell_df = pd.read_csv(data_folder / file)
                        elif(str(file).endswith(".csv.gz")): 
                            cell_df = pd.read_csv(data_folder / file)
                        else:
                            print(f'Invalid file type: {file}, skipping this file')
                            continue
                        
                        counter = 0
                        
                        all_seg_bounds = []
                        
                        for ind, row in tqdm(cell_df.iterrows(), desc=f'Processing {file}', total=len(cell_df)):
                            
                            # convert hex->binary->Shapely geometry object, extract boundary coordinates of geometry
                            geom = shapely.from_wkb(bytes.fromhex(row['geometry']))
                            polys = [geom] if geom.geom_type == 'Polygon' else geom.geoms

                            for poly in polys:
                                coords = np.asarray(poly.exterior.coords)[:, ::-1] # flip to match napari y,x axes
                                # create 4D numpy array storing segmentation coordinates 
                                zeros_array = np.tile([counter, 0], (coords.shape[0], 1))
                                all_seg_bounds.append(np.hstack((zeros_array, coords)))
                                counter += 1

                        data = np.vstack(all_seg_bounds)
                        categories.create_dataset(seg_category, data=data)

                except Exception as e: 
                    # Log the exception with traceback
                    print(f'An error occurred while processing {file}')
                    print(f'Please check the log file for details: {os.path.join(bellavista_output_folder, "error_log.log")}', end='\n\n')
                    logging.error(f'Error in create_transcripts while processing {file}: {e}', exc_info=True)
                    continue

    except Exception as e: 
        # Log the exception with traceback
        print(f'An error occurred during process_segmentations.')
        print(f'Please check the log file for details: {os.path.join(bellavista_output_folder, "error_log.log")}', end='\n\n')
        logging.error(f'Error in process_segmentations: {e}', exc_info=True)
        return
    return


def process_network_graph_celltype(data_folder: str, json_file_input_files: Dict):
    
    bellavista_output_folder = data_folder / "BellaVista_outputs"
    network_graph_file = json_file_input_files.get('network_file')
    
    if network_graph_file is None:
        print('No network graph file provided, skipping network processing.')
        return
    
    try:
        with open(os.path.join(data_folder, network_graph_file), 'rb') as f:
            network_graph_data = pickle.load(f)
    except:
        print('Error loading network graph pickle, will skip processing for now!')
        return

    with h5py.File(bellavista_output_folder / 'cell_networks.hdf5', 'a') as f:
        
        network_group = f.require_group("cell_networks")
        categories = network_group.require_group("networks")

        if 'connectome' in categories:
            print(f"Cell network graph processed previously. Skipping reprocessing.")
            return
        
        celltype_centroids = defaultdict(list)
        celltype_node_ids = defaultdict(list)

        try:

            G = network_graph_data

            ## get cell centroids from network graph pickle
            for node in tqdm(G.nodes, desc=f'Processing cell network graph nodes', total=len(G.nodes)):
                celltype_centroids[G.nodes[node]['celltype']].append(np.flip(G.nodes[node]['pos']))
                celltype_node_ids[G.nodes[node]['celltype']].append(node)
            
            celltype_network_edges = {}

            for celltype in ["CM", "EC", "IC", "FB"]:
                filtered_edges = [(u, v) for u, v in G.edges() if (G.nodes[u].get('celltype') == 'CM' and G.nodes[v].get('celltype') == celltype) or
                        (G.nodes[v].get('celltype') == 'CM' and G.nodes[u].get('celltype') == celltype)
                    ]
            
                vector_data = []
                for i, (start_node, end_node) in tqdm(enumerate(filtered_edges), \
                                                        desc=f'Processing {celltype} network graph edges', total=len(filtered_edges)):
                    start_pos = np.flip(G.nodes[start_node]['pos'])
                    end_pos = np.flip(G.nodes[end_node]['pos'])
                    direction = end_pos - start_pos
                    vector_data.append([start_pos, direction])
                celltype_network_edges[celltype] = vector_data

            connectome = categories.create_group('connectome')
            node_data = connectome.create_group('nodes')

            for celltype in ['CM', 'EC', 'FB', 'IC']:
                node_data.create_dataset(f'{celltype}_centroids', data=celltype_centroids[celltype][:])
                node_data.create_dataset(f'{celltype}_node_ids', data=celltype_node_ids[celltype][:])

            edge_data = connectome.create_group('graph_edges')

            for celltype in ["CM", "EC", "IC", "FB"]:
                edge_data.create_dataset(celltype, data=celltype_network_edges[celltype])

            return
        
        except Exception as e: 
            # Log the exception with traceback
            print(f'An error occurred during process_network_graph_celltype.')
            print(f'Please check the log file for details: {os.path.join(bellavista_output_folder, "error_log.log")}', end='\n\n')
            logging.error(f'Error in process_network_graph_celltype: {e}', exc_info=True)
            return