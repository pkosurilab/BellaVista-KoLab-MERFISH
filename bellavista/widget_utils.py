#Author: Annabelle Coles
#Version: KoLab-MERFISH Mouse Heart Paper

import csv 
import random, colorsys
import warnings
from pathlib import Path
from typing import List, Dict

import h5py
import numpy as np
import zarr
from qtpy import QtWidgets
from ome_zarr.io import parse_url

import napari
from napari.utils.colormaps import standardize_color, Colormap, AVAILABLE_COLORMAPS
from napari.utils.notifications import show_info
from napari.utils.translations import trans

def set_celltype_colors(self):

    celltype_colors = {
        'CM': "#F08080",
        'FB': "#FFBC42",
        'IC': "#4895EF",
        'EC': "#52B788"
    }

    subcluster_colors = {
        "Sham": "#808080",
        "CM1": '#800080',
        "CM2": '#83c0e5',
        "CM3":  '#ff1493'
    }
    
    self.celltype_colors = celltype_colors
    self.subcluster_colors = subcluster_colors


def rotate(angle_deg) -> np.ndarray:

    angle_rad = np.radians(angle_deg)
    cos_theta = np.cos(angle_rad)
    sin_theta = np.sin(angle_rad)

    return np.array([
        [cos_theta, -sin_theta],
        [sin_theta, cos_theta]
    ])

def get_txs_info(txs_data):

    if 'Genes' in txs_data.keys():
        genes = [g.decode("utf-8") if isinstance(g, bytes) else g for g in txs_data['Genes']]
        hdf_categories = list(txs_data['Category'])
        hdf_categories_lower = {cat.lower(): cat for cat in hdf_categories}

        # preferred order in widget drop down
        preferred_order = ["all transcripts", "cm transcripts", "ec transcripts", "ic transcripts", "fb transcripts", "cm scrub transcripts"]

        # add preferred first, then any remaining
        categories_sorted = (
            [hdf_categories_lower[cat] for cat in preferred_order if cat in hdf_categories_lower] +
            [cat for cat in hdf_categories if cat.lower() not in preferred_order]
        )

    else:
        return [], []
    return genes, categories_sorted

def get_seg_info(seg_data):
    
    hdf_categories = list(seg_data.keys())
    hdf_categories_lower = {cat.lower(): cat for cat in hdf_categories}

    # preferred order in widget drop down
    preferred_order = ["all boundaries", "cm boundaries", "ec boundaries", "ic boundaries", "fb boundaries", "cm scrub boundaries"]

    # add preferred first, then any remaining
    categories_sorted = (
        [hdf_categories_lower[cat] for cat in preferred_order if cat in hdf_categories_lower] +
        [cat for cat in hdf_categories if cat.lower() not in preferred_order]
    )

    return categories_sorted

def get_imgs(img_zarr) -> List:
    data = zarr.open(img_zarr, mode='r')
    return list(data.group_keys())

class BellaVistaWidget(QtWidgets.QWidget):
    def __init__(
            self,
            viewer: napari.Viewer,
            data_dir: Path,
            txs_data: h5py.File = None,
            seg_data: h5py.File = None,
            img_zarr: Path = None,
            network_data: h5py.File = None, 
            params: Dict = {}
    ):
        
        super().__init__()
        self.viewer = viewer

        self.data_dir = data_dir
        self.img_zarr = img_zarr
        self.rotate_angle = params.get('rotate_angle', 0)
        self.contrast_lims = params.get('contrast_limits')
        self.gamma = params.get('gamma', 1)
        self.point_size = params.get('transcript_point_size', 1)
        set_celltype_colors(self)

        widget_list = []

        if img_zarr:
            self.imgs = get_imgs(self.img_zarr)
            if len(self.imgs) > 0:
                self.image_widget = self._create_image_widget()
                widget_list.append(self.image_widget)


        if txs_data:
            self.txs_data = txs_data['Transcripts']
            
            ## only make widget if there is data inside hdf5 
            if len(self.txs_data) > 0:
                self.genes, self.genes_categories = get_txs_info(self.txs_data)
                if len(self.genes_categories) > 0:
                    self.gene_widget = self._create_txs_widget()
                    widget_list.append(self.gene_widget)
            
        if seg_data: 
            self.seg_data = seg_data['Segmentations']['Category']

            ## only make widget if there is data inside hdf5 
            if len(self.seg_data) > 0:
                self.seg_categories = get_seg_info(self.seg_data)
                self.seg_colormaps = self._create_colormaps()
                self.segmentation_widget = self._create_seg_widget()
                widget_list.append(self.segmentation_widget)

        if network_data:
            self.network_data = network_data['cell_networks']['networks']
            self.node_size = 5 # change this to make node point size larger!
            self.node_layers = []

            self.network_widget = self._create_network_widget()
            widget_list.append(self.network_widget)
            
            set_celltype_colors(self)

        self.curr_position = None
        self.saved_positions = {}
        self.position_names = []

        self.location_widget = self._create_location_widget()
        widget_list.append(self.location_widget)
        
        layout = QtWidgets.QVBoxLayout()
        for widget in widget_list: 
            layout.addWidget(widget)
        
        self.setLayout(layout)


    def _create_network_widget(self):
  
        widget_panel = QtWidgets.QGroupBox(" Networks 🤝")
        panel_layout = QtWidgets.QVBoxLayout()
        
        plot_button = QtWidgets.QPushButton("Plot")
        plot_button.clicked.connect(self._plot_network)

        size_input = QtWidgets.QSpinBox()
        size_input.setValue(5)
        size_button =  QtWidgets.QPushButton("Set Node Size")
        size_button.clicked.connect(self.set_node_sizes)

        size_row = QtWidgets.QHBoxLayout()
        size_row.addWidget(size_input)
        size_row.addWidget(size_button)

        panel_layout.addWidget(plot_button)
        panel_layout.addLayout(size_row)
        
        self.size_input = size_input
        widget_panel.setLayout(panel_layout)
        
        return widget_panel
    
    def _create_seg_widget(self):
    
        # Load cell segmentation boundaries
        widget_panel =  QtWidgets.QGroupBox(" Segmentations 🌈")
        panel_layout = QtWidgets.QVBoxLayout()

        seg_dropdown = QtWidgets.QComboBox()
        seg_dropdown.addItems(self.seg_categories)
        plot_button = QtWidgets.QPushButton("Plot")
        plot_button.clicked.connect(self._plot_segmentations)

        panel_layout.addSpacerItem(QtWidgets.QSpacerItem(0,10))
        panel_layout.addWidget(seg_dropdown)
        panel_layout.addWidget(plot_button)
        widget_panel.setLayout(panel_layout)

        self.seg_dropdown = seg_dropdown
        
        return widget_panel

    def _create_location_widget(self):

        widget_panel = QtWidgets.QGroupBox(" Locations 🦎") #" Locations 📍"
        panel_layout = QtWidgets.QVBoxLayout()

        ## subpanel to save new locations to dropdown menu
        locations_panel = QtWidgets.QGroupBox("Save Current Location")
        locations_layout = QtWidgets.QVBoxLayout()

        location_name = QtWidgets.QLineEdit()
        location_name.setPlaceholderText("New Location Name")

        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self._add_position)

        locations_layout.addWidget(location_name)
        locations_layout.addWidget(save_button)
        locations_panel.setLayout(locations_layout)
        
        row = QtWidgets.QHBoxLayout()
        row.addWidget(location_name)
        row.addWidget(save_button)
        panel_layout.addLayout(row)

        ## subpanel to move napari viewer camera 
        relocate_panel = QtWidgets.QGroupBox("Set Location")
        relocate_layout = QtWidgets.QVBoxLayout()

        locations_dropdown = QtWidgets.QComboBox()
        locations_dropdown.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        locations_dropdown.setPlaceholderText("Select Location")

        move_button = QtWidgets.QPushButton("Move")
        move_button.clicked.connect(self._move_camera)

        relocate_layout.addWidget(locations_dropdown)
        relocate_layout.addWidget(move_button)
        relocate_panel.setLayout(relocate_layout)

        move_row = QtWidgets.QHBoxLayout()
        move_row.addWidget(locations_dropdown)
        move_row.addWidget(move_button)
        panel_layout.addLayout(move_row)

        ## subpanel to import/export saved camera positions  
        import_panel = QtWidgets.QGroupBox("Import / Export Locations")
        import_layout = QtWidgets.QVBoxLayout()

        import_button = QtWidgets.QPushButton("Load CSV")
        export_button = QtWidgets.QPushButton("Export CSV")

        import_button.clicked.connect(self._load_positions)
        export_button.clicked.connect(self._export_positions)

        import_layout.addWidget(import_button)
        import_layout.addWidget(export_button)
        import_panel.setLayout(import_layout)

        import_row = QtWidgets.QHBoxLayout()
        import_row.addWidget(import_button)
        import_row.addWidget(export_button)
        panel_layout.addLayout(import_row)

        widget_panel.setLayout(panel_layout)

        self.location_name = location_name
        self.locations_dropdown = locations_dropdown
    
        return widget_panel

    def _create_image_widget(self):

        # Load images
        widget_panel = QtWidgets.QGroupBox(" Images 🫀")
        panel_layout = QtWidgets.QVBoxLayout()
    
        img_dropdown = QtWidgets.QComboBox()
        img_dropdown.addItems(self.imgs)
        img_dropdown.setPlaceholderText("Select Image")

        plot_button = QtWidgets.QPushButton("Plot")
        plot_button.clicked.connect(self._plot_image)

        panel_layout.addWidget(img_dropdown)
        panel_layout.addSpacerItem(QtWidgets.QSpacerItem(0,10))
        panel_layout.addWidget(plot_button)

        widget_panel.setLayout(panel_layout)

        self.img_dropdown = img_dropdown
        
        return widget_panel
    
    def _create_txs_widget(self):

        widget_panel = QtWidgets.QGroupBox(" Genes 🧬")
        panel_layout = QtWidgets.QVBoxLayout()

        gene_dropdown = QtWidgets.QComboBox()
        gene_dropdown.addItems(self.genes)
        gene_dropdown.setPlaceholderText("Select Gene")

        category_dropdown = QtWidgets.QComboBox()
        category_dropdown.addItems(self.genes_categories)

        plot_button = QtWidgets.QPushButton("Plot")
        plot_button.clicked.connect(self._plot)

        color_input = QtWidgets.QLineEdit()
        color_input.setPlaceholderText("Layer Color")

        set_color = QtWidgets.QPushButton("Change")
        set_color.clicked.connect(self._change_layer_color)

        panel_layout.addSpacerItem(QtWidgets.QSpacerItem(0,10))
        panel_layout.addWidget(gene_dropdown)
        panel_layout.addWidget(QtWidgets.QLabel("Category:"))
        panel_layout.addWidget(category_dropdown)
        panel_layout.addWidget(plot_button)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(color_input)
        row.addWidget(set_color)
        panel_layout.addLayout(row)

        widget_panel.setLayout(panel_layout)

        self.gene_dropdown = gene_dropdown
        self.category_dropdown = category_dropdown
        self.color_input = color_input

        return widget_panel
    
    def _create_seg_widget(self):
    
        widget_panel =  QtWidgets.QGroupBox(" Segmentations 🌈")
        panel_layout = QtWidgets.QVBoxLayout()

        seg_dropdown = QtWidgets.QComboBox()
        seg_dropdown.addItems(self.seg_categories)
        plot_button = QtWidgets.QPushButton("Plot")
        plot_button.clicked.connect(self._plot_segmentations)

        panel_layout.addSpacerItem(QtWidgets.QSpacerItem(0,10))
        panel_layout.addWidget(seg_dropdown)
        panel_layout.addWidget(plot_button)
        widget_panel.setLayout(panel_layout)

        self.seg_dropdown = seg_dropdown
        
        return widget_panel
        
    def _create_colormaps(self):
        
        # add colormaps to napari 
        seg_colormaps = []
        # create black, white, gainsboro (light gray) colormaps
        for color in ["black", "white", "gray"]:

            cmap_name = f"single-hue {color}"

            custom_cmap = Colormap([color, color], name=cmap_name)
            AVAILABLE_COLORMAPS[cmap_name] = custom_cmap
            seg_colormaps.append(cmap_name)

        ## create colormaps for celltype cell boundaries 
        for celltype in self.celltype_colors:
            
            cmap_name = f"single-hue {celltype}"
            
            color = self.celltype_colors[celltype]
            custom_cmap = Colormap([color, color], name=cmap_name)
            AVAILABLE_COLORMAPS[cmap_name] = custom_cmap
            seg_colormaps.append(cmap_name)

        # for subcluster in self.subcluster_colors:
            
        #     cmap_name = f"single-hue {subcluster}"

        #     color = self.subcluster_colors[subcluster]
        #     custom_cmap = Colormap([color, color], name=cmap_name)
        #     AVAILABLE_COLORMAPS[cmap_name] = custom_cmap
        #     seg_colormaps.append(cmap_name)

        return seg_colormaps
    
    def _plot_network(self):
        
        ## only plot outgoing edges from CM nodes
        ## network edges colored by neighbor node celltype 
        for celltype in ["IC", "FB", "EC", "CM"]:
            self.viewer.add_vectors(
                self.network_data['connectome']['graph_edges'][celltype][:], 
                name=f'{celltype} Network Edges', 
                edge_color= self.celltype_colors[celltype], 
                opacity=1, 
                vector_style='line', 
                rotate=self.rotate_angle
                )
        
        node_data = self.network_data['connectome']['nodes']
        for celltype in ["IC", "FB", "EC", "CM"]:
            coords = node_data[f'{celltype}_centroids'][:]
            self.viewer.add_points(
                coords,
                name=f'{celltype} nodes', 
                face_color=self.celltype_colors[celltype], 
                border_color=self.celltype_colors[celltype], 
                size=self.node_size,
                rotate=self.rotate_angle
                )
            self.node_layers.append(f'{celltype} nodes')

    def set_node_sizes(self):
        
        size = self.size_input.value()
        for layer in self.node_layers:
            self.viewer.layers[layer].size = size

    def _plot_image(self):

        img_name = self.img_dropdown.currentText()
        path = self.img_zarr / img_name

        store = parse_url(path, mode="r").store
        root = zarr.group(store=store)
        image_meta = root.attrs.get('multiscales', [{}])[0].get('metadata', {})

        um_per_pixel_y, um_per_pixel_x = (
            image_meta.get('um_per_pixel_y', 1), 
            image_meta.get('um_per_pixel_x', 1)
        )
        y_shift, x_shift = image_meta.get('y_shift',0), image_meta.get('x_shift',0)

        rotated = rotate(self.rotate_angle) @ np.array([y_shift, x_shift])

        rotated_yshift = rotated[0]
        rotated_xshift = rotated[1]

        if not self.contrast_lims:
            self.contrast_lims = [image_meta.get('px_val_min',0), 
                                image_meta.get('px_val_max', 65535)]
            
        self.viewer.open(path,
                        name=img_name, 
                        plugin='napari-ome-zarr',
                        blending='additive', 
                        scale=(1, um_per_pixel_y, um_per_pixel_x),
                        translate=(0, rotated_yshift, rotated_xshift), 
                        rotate=self.rotate_angle,
                        contrast_limits=self.contrast_lims,
                        colormap = 'gray')
        
    def _pre_load_image(self):
        
        ## default plot WGA image, if not plot other images in list e.g. DAPI
        img_name = next((name for name in self.imgs if "WGA" in name), None)
        
        if img_name is None:
            img_name = self.img_dropdown.currentText()

        if img_name is None:
            return 
        
        path = self.img_zarr / img_name

        store = parse_url(path, mode="r").store
        root = zarr.group(store=store)
        image_meta = root.attrs.get('multiscales', [{}])[0].get('metadata', {})

        um_per_pixel_y, um_per_pixel_x = (
            image_meta.get('um_per_pixel_y', 1), 
            image_meta.get('um_per_pixel_x', 1)
        )
        y_shift, x_shift = image_meta.get('y_shift',0), image_meta.get('x_shift',0)

        rotated = rotate(self.rotate_angle) @ np.array([y_shift, x_shift])

        rotated_yshift = rotated[0]
        rotated_xshift = rotated[1]

        if not self.contrast_lims:
            self.contrast_lims = [image_meta.get('px_val_min',0), 
                                image_meta.get('px_val_max', 65535)]
            
        self.viewer.open(path,
                        name=img_name, 
                        plugin='napari-ome-zarr',
                        blending='additive', 
                        scale=(1, um_per_pixel_y, um_per_pixel_x),
                        translate=(0, rotated_yshift, rotated_xshift), 
                        rotate=self.rotate_angle,
                        contrast_limits=self.contrast_lims,
                        gamma=self.gamma,
                        colormap = 'gray')
        
    def _plot(self):
        gene = self.gene_dropdown.currentText()
        gene_group = self.category_dropdown.currentText()

        layer_name = gene
        if gene_group != 'Barcodes':
            layer_name += f' ({gene_group})'

        try:
            # generate random, bright point color
            h = random.random()
            s = random.uniform(0.8, 1.0)
            v = random.uniform(0.8, 1.0)

            layer_color = colorsys.hsv_to_rgb(h, s, v)
            layer_color = standardize_color.transform_color(layer_color)
        except:
            layer_color = 'magenta'

        if layer_name not in self.viewer.layers:
            self.viewer.add_points(
                self.txs_data['Category'][gene_group][gene], 
                name=layer_name, 
                face_color=layer_color, 
                border_color=layer_color, 
                size=self.point_size,
                rotate=self.rotate_angle
                )

        else:
            self.viewer.layers[layer_name].visible=True

    def _change_layer_color(self):
        
        color = self.color_input.text()
        if color:
            selected_layer = self.viewer.layers.selection.active
            
            if isinstance(selected_layer, napari.layers.Points):
                try:
                    ## check if user-defined color is valid
                    transformed = standardize_color.transform_color(color)
                    selected_layer.face_color = color
                    selected_layer.border_color = color

                    # Toggle visibility on/off to update the layer menu preview image
                    selected_layer.visible = False  
                    selected_layer.visible = True  
                
                except (AttributeError, ValueError, KeyError):
                    warnings.warn(
                    trans._(
                        'Invalid color "{elem_name}"',
                        deferred=True,
                        elem_name=color
                    )
                )
        self.color_input.setPlaceholderText("Layer Color")

    def _plot_segmentations(self):

        seg = self.seg_dropdown.currentText()
        cmap = 'single-hue gray'

        ## plot boundaries in respective celltype coloring
        cell_types = list(self.subcluster_colors.keys()) + list(self.celltype_colors.keys())
        for celltype in cell_types:
            if celltype in seg:
                cmap = f'single-hue {celltype}'
                break
        
        layer_name = seg 
        if layer_name not in self.viewer.layers:
             # plot segmentations as napari tracks layers
            self.viewer.add_tracks(
                self.seg_data[seg][:], 
                name=seg, 
                colormap = cmap, 
                blending = 'opaque', 
                rotate=self.rotate_angle,
                tail_width=0.5
                )
        else:
            self.viewer.layers[layer_name].visible=True

    def _add_position(self):
        """Callable function A."""
        camera = self.viewer.camera
        Position_Name = self.location_name.text()
        
        if "Previous Position" not in self.position_names:
            self.saved_positions["Previous Position"] = {
                    "name": "Previous Position",
                    "zoom": camera.zoom,
                    "center": camera.center
            }
            self.position_names.append("Previous Position")
            self.locations_dropdown.insertItem(0, "Previous Position")
            
        if Position_Name not in self.position_names:
            self.saved_positions[Position_Name] = {
                "name": Position_Name,
                "zoom": camera.zoom,
                "center": camera.center
            }
            self.position_names.append(Position_Name)
            
            self.locations_dropdown.insertItem(0, Position_Name)
            show_info(f'{Position_Name} position saved')
            self.location_name.clear()

        else:
            warnings.warn(
                        trans._(
                            'Position "{elem_name}" already exists, please choose a new name.',
                            deferred=True,
                            elem_name=Position_Name
                        )
                    )
                
    def _move_camera(self):
        
        Position = self.locations_dropdown.currentText()
        if Position != self.curr_position and len(self.position_names) > 0:
            prev_zoom = self.viewer.camera.zoom
            prev_center = self.viewer.camera.center

            position_data = self.saved_positions[Position]
            self.viewer.camera.zoom = position_data["zoom"]
            self.viewer.camera.center = position_data["center"]

            self.saved_positions["Previous Position"] = {
                "name": "Previous Position",
                "zoom": prev_zoom,
                "center": prev_center
            }

            show_info(f'Moved to: {Position}!')
            self.curr_position = Position

    def _load_positions(self):
        
        ## load pre-saved camera positions from CSV file
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
            caption="Select Saved Positions CSV", dir="~", filter="CSV Files (*.csv)")
        
        if not file_paths:
            return
        
        for filename in file_paths:
            print(filename)
            with open(str(filename), 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if row:
                        try:
                            position_name, zoom, z, center_x, center_y = row
                            
                            # Add the position to saved_positions dictionary
                            self.saved_positions[position_name] = {
                                "name": position_name,
                                "zoom": float(zoom),
                                "center": (float(z), float(center_x), float(center_y))
                            }
                            
                            # Add the position name to the dropdown
                            if position_name not in self.position_names:
                                self.position_names.append(position_name)
                                self.locations_dropdown.insertItem(0, position_name)
                        
                        except: pass

        show_info(f'Camera Positions Loaded!')

    def _export_positions(self):
        show_info("Writing locations to CSV")

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption="Save Positions as CSV", filter="CSV Files (*.csv)")
        
        if not file_path:
            return
        
        with open(str(file_path), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Position Name", "Zoom", "Z", "Center X", "Center Y"])

            for position_name, position in self.saved_positions.items():
                zoom = position["zoom"]
                z, center_x, center_y = position["center"]
                writer.writerow([position_name, zoom, z, center_x, center_y])

        show_info(f"{len(self.saved_positions)} Locations saved to CSV!")

def create_widget(viewer: napari.Viewer, folder: Path, params: Dict):

    transcripts = None
    segmentations = None
    img_zarr = None 
    cell_networks = None

    if (folder / 'transcripts.hdf5').is_file():
        transcripts = h5py.File(folder / 'transcripts.hdf5', 'r')
    if (folder / "segmentations.hdf5").is_file():
        segmentations = h5py.File(folder / "segmentations.hdf5", mode='r')
    if (folder / "Images.zarr").is_dir():
        img_zarr = folder / "Images.zarr"
    if (folder / "cell_networks.hdf5").is_file():
        cell_networks = h5py.File(folder / "cell_networks.hdf5", mode='r')

    widget = BellaVistaWidget(viewer, folder, transcripts, segmentations, img_zarr, cell_networks, params)
    return widget 

