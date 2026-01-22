import numpy as np
import os
import epicure.epicuring as epi
import epicure.Utils as ut
#from unittest.mock import Mock
#from vispy import keys
import napari


def test_output_selected():
    """ Selection of cells to export segmentation as ROI/labels """
    test_img = os.path.join(".", "test_data", "area3_Composite.tif")
    test_seg = os.path.join(".", "test_data", "area3_Composite_epyseg.tif")
    viewer = napari.Viewer(show=False)
    epic = epi.EpiCure(viewer)
    resaxis, resval = epic.load_movie(test_img)
    epic.set_chanel(1, 1)
    assert epic.viewer is not None
    epic.go_epicure("test_epics", test_seg)

    ## test changing the current selection of export (one cell or all cells)
    output = epic.outputing
    assert output is not None
    output.output_mode.setCurrentText("All cells")
    sel = output.get_selection_name()
    assert sel == ""
    output.output_mode.setCurrentText("Only selected cell")
    sel = output.get_selection_name()
    assert sel == "_cell_1"
    ## export a cell segmentation as Fiji ROI
    output.save_choice.setCurrentText("ROI")
    roi_file = os.path.join(".", "test_data", "test_epics", "area3_Composite_rois_cell_1.zip")
    if os.path.exists(roi_file):
        os.remove(roi_file)
    output.save_segmentation()
    assert os.path.exists(roi_file)
    
def test_measure_vertices():
    """ Find the vertices (TCJ) and measure their intensity and nb of neighbors """

    test_img = os.path.join(".", "test_data", "area3_Composite.tif")
    test_seg = os.path.join(".", "test_data", "area3_Composite_epyseg.tif")
    viewer = napari.Viewer(show=False)
    epic = epi.EpiCure(viewer)
    resaxis, resval = epic.load_movie(test_img)
    epic.set_chanel(1, 1)
    assert epic.viewer is not None
    epic.go_epicure("test_epics", test_seg)

    output = epic.outputing
    assert output is not None

    # Default vertex sizes
    output.vertice_radius.setText("1.25")
    output.measure_vertices()
    assert "Vertices" in viewer.layers
    vertices = viewer.layers["Vertices"].data
    frame = 1
    props = ut.binary_properties(vertices[frame])
    nvertex = len(props)
    assert nvertex > 150
    assert nvertex < 250
    nneigh = np.array((output.table["nb_neighbors"]))
    ## Nb of neighbor shuold in majority 3, and between 2 and 6-ish max
    assert np.min(nneigh>=2)
    assert np.max(nneigh<=6)
    assert np.floor(np.median(nneigh)) == 3

    ## Take bigger vertex: merge neighboring ones
    output.vertice_radius.setText("4")
    output.measure_vertices()
    vertices = viewer.layers["Vertices"].data
    props = ut.binary_properties(vertices[frame])
    assert len(props)>100
    assert len(props)<nvertex

def test_measure_events():
    """ Measure/export of events """
    test_img = os.path.join(".", "test_data", "013_crop.tif")
    viewer = napari.Viewer(show=False)
    epic = epi.EpiCure(viewer)
    epic.load_movie(test_img)
    epic.go_epicure("epics")
    output = epic.outputing

    ## Export of number of events by frame
    output.output_mode.setCurrentText("All cells") ## ensure to measure all cells
    tab = output.count_events()
    ## should have only one division at frame 3
    assert int(tab.loc[tab["frame"]==2, 'division'].iloc[0]) == 0
    assert int(tab.loc[tab["frame"]==3, 'division'].iloc[0]) == 1
    assert np.sum(tab['extrusion']) == 0

if __name__ == "__main__":
    #test_output_selected()
    #test_measure_events()
    test_measure_vertices()
    print("********* Test outputs cure completed ***********")
