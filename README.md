# BellaVista - KoLab-MERFISH edition

This development version is curated for visualization of KoLab-MERFISH datasets from the mouse heart.  

## DropBox data information:

The dataset files for both the Sham and TAC datasets are on DropBox, and can be accessed via the private link we shared. There are 2 folders, one for each dataset. Here, you can find the files for each of the 4 key dataset components: (1) WGA & DAPI images (2) Cell boundaries (3) Transcripts (4) Cell network connectivity graphs. After downloading the zipped folder from DropBox, unzip the folder, and open the BellaVista JSON config file.

> [!NOTE]  
> Each dataset contain a large volume of data ~12GB for the Sham, and ~15GB for the TAC dataset. This is because each dataset contains high resolution WGA & DAPI images, tens-of-thousands of cells, and hundreds-of-millions of transcripts. For visualization, these data will be converted to visualization files that will also require approximately the same amount of space as the raw datasets. So please keep this in mind when downloading the data! 

## Installation
The following instructions require that you have [Anaconda](https://www.anaconda.com/) installed.
- In MacOS, run the following commands from the Terminal.
- In Windows, run the following commands from the Anaconda Prompt.
- BellaVista requires Python 3.9 or above and is dependent on GPU for rendering. We recommend using Python 3.12.

Create and activate a new virtual environment:

```
conda create -n bellavista_env python=3.12
conda activate bellavista_env
```

Install from GitHub repo:

```
conda install git
git clone https://github.com/pkosurilab/BellaVista-KoLab-MERFISH
pip install -e BellaVista-KoLab-MERFISH
```

After installing the BellaVista package, you can visualize each KoLab-MERFISH dataset by providing a JSON config file:
* The JSON file argument should contain the file path to your JSON file. Replace TAC_bellavista_config.json with the dataset of your choice. The JSON files are located in the DropBox folders.

```
bellavista /path/to/TAC_bellavista_config.json
```

> [!NOTE]
> It will take a few minutes to create the required data files. The terminal will print updates & have progress bars for time consuming steps.


### Configuring the JSON file:

The BellaVista JSON config file for each dataset can be found within the respective data folder. The only line you need to change is the **data_folder** parameter. This should be changed to the absolute path to the folder containing the dataset files. If no valid path is provided, BellaVista will search for input files in the parent folder of the JSON file. See further details below.

## BellaVista GUI:

After successfully loading BellaVista with the command `bellavista /path/to/TAC_bellavista_config.json`, you should see the message Data Loaded! in the terminal.

A napari window should appear displaying the data similar to the image below (TAC dataset shown here):

<p align="middle">
<img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/TAC_WGA.png?raw=true" alt="BellaVista TAC dataset zoom out" width="800" />
</p>

Now, you can interactively move around the napari canvas to explore the data.
Try zooming in & out, plotting cell-type-specific transcripts, cell boundaries, and cell networks!

<p align="middle">
<img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/BellaVista_demo.png?raw=true" alt="BellaVista TAC dataset" width="800" />
</p>

BellaVista uses the napari interface and features a widget located on the right side of the napari window to plot each dataset feature. The widget has five components:

### Images 🫀

The "Images 🫀" widget features a dropdown menu with the images that are available to plot. Both datasets contain WGA and DAPI images. 

### Genes 🧬

The "Genes 🧬" widget features a dropdown menu with the genes in the gene panel, and a dropdown menu to select cell-type-specific transcripts. 

* "all transcripts" = all transcript molecules (un-partitioned) -- this includes all transcripts, both transcripts assigned to cells and unassigned transcripts
* "CM transcripts" = cardiomyocyte transcripts
* "EC transcripts" = endothelial cell transcripts
* "IC transcripts" = immune cell transcripts
* "FB transcripts" = fibroblast transcripts
* "CM scrub transcripts" = spatially-scrubbed cardiomyocyte transcripts (see methods section)

To plot the transcripts from a gene, select the gene from the dropdown gene list, select your cell-type of interest, then press `Plot`! Each individual transcript molecule will be plotted as a single point. The layer color is random, and can be changed using the "Layer Color" text input & button. The input color value can be provided as a hexcode value e.g. `#FF00FF` or by name e.g. `Magenta`.

### Segmentations 🌈

The "Segmentations 🌈" widget features a dropdown menu with cell-type-specific cell segmentation boundaries. 

* "all boundaries" = all segmentation mask boundaries
* "CM boundaries" = cardiomyocyte boundaries
* "EC boundaries" = endothelial cell boundaries
* "IC boundaries" = immune cell boundaries
* "FB boundaries" = fibroblast boundaries
* "CM scrub boundaries" = spatially-scrubbed cardiomyocyte boundaries (see methods section)

The boundaries for each cell type will be colored as follows: CM: pink, EC: green, IC: blue, FB: yellow. To change the color of the cell boundaries, use the "colormap" option on the layer control menu. For the best visualization, you should select a colormap starting with "single-hue"!

### Networks 🤝

The "Networks 🤝" widget can be used to plot the cell connectivity networks. The centroid of each cell is plotted as a node (napari point layer), and is colored by its corresponding cell type: CM: pink, EC: green, IC: blue, FB: yellow. Cardiomyocyte->cell-type-specific edges are plotted, and are colored by the cell-type identity of the corresponding cardiomyocyte's neighbor. The node size can be adjusted with this widget.   

### Locations 🦎

The "Locations 🦎" widget can be used to save and move to marked camera coordinates. Additionally, the "Load CSV" & "Export CSV" buttons can be used to export your saved locations or load previously saved locations from a previous session. 

> [!NOTE]  
> If the input files for a feature was not provided or an error occurred during data processing, the corresponding widget may not be available. A detailed log file `error_log.log` can be found in the `BellaVista_outputs` subfolder inside the data folder. 


## Configuration JSON file structure

In order to visualize a KoLab-MERFISH dataset in BellaVista, you will need to create a dataset-specific JSON configuration file containing paths to the KoLab-MERFISH outputs for the dataset. These output files will be processed to generate visualization files for BellaVista. Creating these visualization files will take a few minutes but only need to be created once. For subsequent runs, `create_inputs` can be set to `False`.

JSON params
```
"input_files": {
        "images": ["Images/WGA.tif", "Images/DAPI.tif"],
        "microscope_parameters": "microscope_parameters.json",

        "transcript_files": [
                            "Transcripts/all_transcripts.csv.gzs", 
                            "Transcripts/CM_transcripts.csv.gz", 
                            "Transcripts/EC_transcripts.csv.gz", 
                            "Transcripts/FB_transcripts.csv.gz", 
                            "Transcripts/IC_transcripts.csv.gz",
                            "Transcripts/CM_scrub_transcripts.csv.gz"],
        
        "segmentation_files": [
                                "CellBoundaries/all_boundaries.csv.gz",
                                "CellBoundaries/CM_boundaries.csv.gz", 
                                "CellBoundaries/EC_boundaries.csv.gz", 
                                "CellBoundaries/FB_boundaries.csv.gz",
                                "CellBoundaries/IC_boundaries.csv.gz",
                                "CellBoundaries/CM_scrub_boundaries.csv.gz"],
        "network_file": "network_graph.pkl"
    }
```

## General parameters

**data_folder**: *string*

* The path to the folder where the KoLab-MERFISH dataset output files are stored. BellaVista visualization files will be saved in a new folder named `BellaVista_outputs` within the data_folder.
  
**create_bellavista_inputs**: *boolean, default=true*

* Specifies whether to generate the necessary visualization files for BellaVista. It should be set to `true` when loading the data for the first time. It can be set to `false` in later runs, as the files will already have been created.

  > If set to `true` and the visualization files already exist from a previous run, BellaVista will skip recreating those files and only generate any missing ones.


## Visualization parameters

**contrast_limits**: *tuple array of integers, default=None*

* Range of values [0, 65535] used to set the contrast limits for the displayed image(s)

**transcript_point_size**: *float, default=1*

* Size of the points representing individual transcript coordinates

**rotate_angle**: *integer, default=0*

* Rotation angle in degrees, within the range [0, 360], by which to rotate the data

## Input file parameters

**transcript_filenames**: *string or 1D array of strings*

* relative path to Parquet or CSV file(s) containing transcript spatial coordinates. If None, no transcripts will be processed

**images**: *string or 1D array of strings, default=None*

* relative path to stitched image file(s). Must be a TIFF file. If None, no images will be processed
  > When visualizing a single image, provide the file path as a string. For multiple images, pass them as a list of filenames. For example, use "DAPI.tif" for a single image or ["DAPI.tif", "WGA.tif"] for multiple images

**microscope_parameters**: *string*

* relative path to JSON file containing microscope micron to pixel transform.

**segmentation_files**: *string or 1D array of strings*

* relative path to Parquet or CSV file(s) containing cell boundary coordinates. If None, no cell boundaries will be processed

**network_file**: *string*

* relative path to pickle file containing KoLab-MERFISH network data

> [!IMPORTANT]  
> All input file paths **must** be relative paths to `data_folder`
