# BellaVista - KoLab-MERFISH edition

BellaVista is a visualization tool for interactive exploration of imaging-based transcriptomic data. This development version is designed for data already processed through the KoLab-MERFISH pipeline. BellaVista can be used to visualize the 4 key dataset components of each KoLab-MERFISH dataset: (1) WGA & DAPI images, (2) Cell segmentation boundaries, (3) Transcript locations, (4) Cell network connectivity graphs. Note: BellaVista is purely a visualization tool - it does not perform data processing or analysis :)


## Quick Start

1. Install [Python](https://www.python.org/downloads/) (if not previously installed)
2. Install [git](https://git-scm.com/install/windows) (if not previously installed)
3. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) 

Launch the BellaVista demo in a terminal with the single-line command:

```
uvx -p 3.12 --from git+https://github.com/pkosurilab/BellaVista-KoLab-MERFISH bellavista
```

> [!NOTE]
> It will take a few minutes to download and create the required data files. The terminal will print updates & display progress bars for time consuming steps. The sample data is a single FOV from the TAC mouse heart and is ~17MB. 

After successfully loading the BellaVista, you should see the message Data Loaded! in the terminal. A napari window should appear displaying the sample data similar to the image below (TAC sample FOV dataset shown here):

<p align="middle">
<img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/BellaVista_demo_launch_screen.png?raw=true" alt="BellaVista demo sample TAC dataset initial screen" width="800" />
</p>

Now, you can interactively move around the napari canvas to explore the data.
Try zooming in & out, plotting cell-type-specific transcripts, cell boundaries, and cell networks!

<p align="middle">
<img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/BellaVista_sample_demo.png?raw=true" alt="BellaVista demo sample TAC dataset" width="800" />
</p>

## BellaVista Widget Menu

BellaVista uses the napari interface and features a widget located on the right side of the napari window to plot each dataset feature. The widget has four components:


<!-- 
<p align="left">
  
  <h3 align="left">Image Widget</h3>
  <img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/image_widget.png?raw=true"
  alt="BellaVista image widget" width="200" />

  The image widget features a dropdown menu with the images that are available to plot. The demo dataset contains WGA and DAPI images. 
</p> -->


<p align="left">
  
  <h3 align="left">Gene Widget</h3>
  <img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/gene_widget.png?raw=true"
  alt="BellaVista gene widget" width="200" />
  
  The gene widget features a dropdown menu with the genes in the gene panel, and a dropdown menu to select cell-type-specific transcripts. 

* "all transcripts" = all transcript molecules (un-partitioned) -- this includes all transcripts, both transcripts assigned to cells and unassigned transcripts
* "CM transcripts" = cardiomyocyte transcripts
* "EC transcripts" = endothelial cell transcripts
* "IC transcripts" = immune cell transcripts
* "FB transcripts" = fibroblast transcripts
* "CM scrub transcripts" = spatially-scrubbed cardiomyocyte transcripts (see methods section)

To plot the transcripts from a gene, select the gene from the dropdown gene list, select your cell-type of interest, then press `Plot`! Each individual transcript molecule will be plotted as a single point. The layer color is random, and can be changed using the "Layer Color" text input & button. The input color value can be provided as a hexcode value e.g. `#FF00FF` or by name e.g. `Magenta`.

</p>

<p align="left">
  
  <h3 align="left">Segmentation Widget</h3>
  <img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/segmentation_widget.png?raw=true"
  alt="BellaVista segmentation widget" width="200" />

  The segmentation widget features a dropdown menu with cell-type-specific cell segmentation boundaries. 

* "all boundaries" = all segmentation mask boundaries
* "CM boundaries" = cardiomyocyte boundaries
* "EC boundaries" = endothelial cell boundaries
* "IC boundaries" = immune cell boundaries
* "FB boundaries" = fibroblast boundaries
* "CM scrub boundaries" = spatially-scrubbed cardiomyocyte boundaries (see methods section)

The boundaries for each cell type will be colored as follows: CM: pink, EC: green, IC: blue, FB: yellow. To change the color of the cell boundaries, use the "colormap" option on the layer control menu. For the best visualization, you should select a colormap starting with "single-hue"!

</p>

<p align="left">
  
  <h3 align="left">Network Widget</h3>
  <img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/network_widget.png?raw=true"
  alt="BellaVista network widget" width="200" />

  The network widget can be used to plot the cell connectivity networks. The centroid of each cell is plotted as a node (napari point layer), and is colored by its corresponding cell type: CM: pink, EC: green, IC: blue, FB: yellow. Cardiomyocyte->cell-type-specific edges are plotted, and are colored by the cell-type identity of the corresponding cardiomyocyte's neighbor. The node size can be adjusted with this widget.  
  </p>

<p align="left">
  
  <h3 align="left">Location Widget</h3>
  <img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/location_widget.png?raw=true"
  alt="BellaVista location widget" width="200" />

  The location widget can be used to save and move to marked camera coordinates. Additionally, the "Load CSV" & "Export CSV" buttons can be used to export your saved locations or load previously saved locations from a previous session. 
  </p>

> [!NOTE]  
> If the input files for a feature was not provided or an error occurred during data processing, the corresponding widget may not be available. A detailed log file `error_log.log` can be found in the `BellaVista_outputs` subfolder inside the data folder. 

> **That's it for the Quick Start!**
> 
> The section below describes how to visualize the full-scale datasets. 

# Visualizing full datasets

We will share the commands to visualize the Sham and TAC datasets, including the private url-links. To visualize a dataset hosted on the web, use the following single-line command:

```
uvx -p 3.12 --from git+https://github.com/pkosurilab/BellaVista-KoLab-MERFISH bellavista --dataset-url "url-link-to-dataset"
```

> [!NOTE]
> It will take a few minutes to download and create the required data files. The terminal will print updates & display progress bars for time consuming steps.


After successfully launching BellaVista, you should see the message `Data Loaded!` in the terminal. A napari window should appear displaying the data similar to the image below (TAC dataset shown here):

<p align="middle">
<img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/TAC_WGA.png?raw=true" alt="BellaVista TAC dataset zoom out" width="800" />
</p>

Now, you can interactively move around the napari canvas to explore the data.
Try zooming in & out, plotting cell-type-specific transcripts, cell boundaries, and cell networks!

<p align="middle">
<img src="https://github.com/pkosurilab/BellaVista-KoLab-MERFISH/blob/main/images/BellaVista_demo.png?raw=true" alt="BellaVista TAC dataset" width="800" />
</p>

> [!IMPORTANT]  
> Each dataset contains a volume of data ~2GB for the Sham, and ~2.5GB for the TAC dataset. Each dataset contains WGA & DAPI images, tens-of-thousands of cells, and hundreds-of-millions of transcripts. For visualization, these data will be converted to visualization files that will also require approximately the same amount of space as the raw datasets. So please keep this in mind when downloading the data!
>
> Each folder contains 4 key data components: (1) WGA & DAPI images, (2) Cell boundaries, (3) Transcripts, (4) Cell network connectivity graphs, along with auxiliary files. 

> **That's it for the example Sham and TAC datasets!** 
>
> The following section covers the config file structure in detail — feel free to skip if you're using the quick-start demo :)

# Installation

For a full installation, we recommend using [Anaconda](https://www.anaconda.com/).
- In MacOS, run the following commands from the Terminal.
- In Windows, run the following commands from the Anaconda Prompt.
- BellaVista requires Python 3.10 or above and is dependent on GPU for rendering. We recommend Python 3.12.

### Using conda/pip

```
conda create -n bellavista_env python=3.12
conda activate bellavista_env
git clone https://github.com/pkosurilab/BellaVista-KoLab-MERFISH
pip install -e BellaVista-KoLab-MERFISH
```

After successfully installing BellaVista to your conda environment, this environment can be used to relaunch BellaVista in the future. 

<!-- ### Using uv (recommended)

```
uv venv -p 3.12 bellavista_env
# macOS/Linux:
source bellavista_env/bin/activate
# Windows:
bellavista_env\Scripts\activate

uv pip install "bellavista-kolab-merfish @ git+https://github.com/pkosurilab/BellaVista-KoLab-MERFISH.git"
```

For development (editable install):

```
git clone https://github.com/pkosurilab/BellaVista-KoLab-MERFISH
cd BellaVista-KoLab-MERFISH
uv venv -p 3.12
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

uv pip install -e .
``` -->


# KoLab-MERFISH Dataset Configuration

BellaVista uses a JSON config file to specify dataset-specific paths to input files and optional visualization parameters. 

### Configuration JSON file structure

To visualize a KoLab-MERFISH dataset, you will need to create a dataset-specific JSON config file that points to your KoLab-MERFISH dataset files. These files will be processed to generate visualization files for BellaVista. Creating these visualization files will take a few minutes but only need to be created once. For subsequent runs, `create_inputs` can be set to `False`.


**Example KoLab-MERFISH dataset folder structure:**

```
.
└── dataset_folder
    ├── CellBoundaries
    │   ├── CM_boundaries.csv.gz
    │   ├── CM_scrub_boundaries.csv.gz
    │   ├── EC_boundaries.csv.gz
    │   ├── FB_boundaries.csv.gz
    │   ├── IC_boundaries.csv.gz
    │   └── all_boundaries.csv.gz
    ├── Images
    │   ├── DAPI.tif
    │   └── WGA.tif
    ├── dataset_bellavista_config.json
    ├── dataset_network_graph.pkl
    ├── Transcripts
    │   ├── CM_scrub_transcripts.csv.gz
    │   ├── CM_transcripts.csv.gz
    │   ├── EC_transcripts.csv.gz
    │   ├── FB_transcripts.csv.gz
    │   ├── IC_transcripts.csv.gz
    │   └── all_transcripts.csv.gz
    └── microscope_parameters.json
```

**dataset_config.json:**
```
{ 
    "system": "KoLabMERFISH",
    "create_bellavista_inputs": true,
    "data_folder": "/path/to/dataset_folder"


    "visualization_parameters": {
        "contrast_limits": [0, 60000],
        "gamma": 2,
        "transcript_point_size": 1,
        "rotate_angle": 0 
    },


    "input_files": {
        "images": ["Images/WGA.tif", "Images/DAPI.tif"],
        "microscope_parameters": "microscope_parameters.json",
        "transcript_files": [
                            "Transcripts/all_transcripts.csv.gz", 
                            "Transcripts/CM_scrub_transcripts.csv.gz", 
                            "Transcripts/CM_transcripts.csv.gz", 
                            "Transcripts/EC_transcripts.csv.gz", 
                            "Transcripts/FB_transcripts.csv.gz", 
                            "Transcripts/IC_transcripts.csv.gz"],
        
        "segmentation_files": [
                                "CellBoundaries/all_boundaries.csv.gz",
                                "CellBoundaries/CM_scrub_boundaries.csv.gz",
                                "CellBoundaries/CM_boundaries.csv.gz", 
                                "CellBoundaries/EC_boundaries.csv.gz", 
                                "CellBoundaries/FB_boundaries.csv.gz",
                                "CellBoundaries/IC_boundaries.csv.gz"],
        "network_file": "TAC_network_graph.pkl"
    }
}

```

After activating your conda environment, launch your dataset in BellaVista by providing the path to your configured JSON config file:

```
bellavista /path/to/your/dataset_config.json
```

## JSON configuration parameters

### General parameters

**data_folder**: *string*

* The path to the folder where the KoLab-MERFISH dataset output files are stored. BellaVista visualization files will be saved in a new folder named `BellaVista_outputs` within the data_folder. 

  > If no valid path is provided, BellaVista will look for the input files in the same parent folder as the JSON configuration file.   
  
**create_bellavista_inputs**: *boolean, default=true*

* Specifies whether to generate the necessary visualization files for BellaVista. It should be set to `true` when loading the data for the first time. It can be set to `false` in later runs, as the files will already have been created.

  > If set to `true` and the visualization files already exist from a previous run, BellaVista will skip recreating those files and only generate any missing ones.


### Visualization parameters (optional)

**contrast_limits**: *tuple array of integers, default=None*

* Range of values [0, 65535] used to set the contrast limits for the displayed image(s)

**gamma**: *float, default=1*

* Gamma correction value for the displayed image(s)

**transcript_point_size**: *float, default=1*

* Size of the points representing individual transcript coordinates

**rotate_angle**: *integer, default=0*

* Rotation angle in degrees, within the range [0, 360], by which to rotate the data

### Input file parameters

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

* relative path to pickle file containing KoLab-MERFISH network graph data

> [!IMPORTANT]  
> All input file paths **must** be relative paths to `data_folder`
