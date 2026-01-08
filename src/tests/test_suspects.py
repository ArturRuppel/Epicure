import numpy as np
import os
import epicure.epicuring as epi
import epicure.Utils as ut
#from unittest.mock import Mock
#from vispy import keys
import napari


def test_suspect_frame():
    """ Flag possible errors on a single frame, looking at possible outliers """
    test_img = os.path.join(".", "test_data", "area3_Composite.tif")
    test_seg = os.path.join(".", "test_data", "area3_Composite_epyseg.tif")
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    epic.set_chanel(1, 1)
    assert epic.viewer is not None
    epic.go_epicure("test_epics", test_seg)

    ## flag cells if area smaller than given threshold 
    segedit = epic.inspecting
    assert segedit is not None
    segedit.min_area.setText("70")
    segedit.event_area_threshold()
    assert "Events" in epic.viewer.layers
    outlier = epic.viewer.layers["Events"]
    assert len(outlier.data)>=5
    ## check is done on frame 0 only
    assert outlier.data[1][0] == 0

    ## flag if the intensity ratio is to high 
    nsus = len(outlier.data)
    segedit.fintensity_out.setText("0.5")
    segedit.event_intensity(True)
    assert len(outlier.data) > (nsus+5)

def test_suspect_track():
    """ Track and flag weird tracks """
    test_img = os.path.join(".", "test_data", "003_crop.tif")
    test_seg = os.path.join(".", "test_data", "003_crop_epyseg.tif")

    ## load and initialize
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    epic.go_epicure("test_epics", test_seg)
    track = epic.tracking
    susp = epic.inspecting

    ## initialisation: no suspects
    assert susp.nb_events() == 0
    # default tracking
    track.do_tracking()
    ## after tracking, only possible events are division 
    assert susp.nb_events() == susp.nb_type("division")
    nev = susp.nb_events()
    assert nev > 0
    ## manually add a suspect
    susp.add_event( (5,50,50), 10, "test" )
    assert susp.nb_events() == (nev+1)
    ## test default parameter inspection
    susp.check_size.setChecked( False )
    susp.check_length.setChecked( False )
    susp.inspect_tracks()
    assert susp.nb_events() > 30
    assert susp.nb_events() < 60
    ## test minimum track length inspection
    susp.check_length.setChecked( True )
    susp.min_length.setText("5")
    nmin_prev =  susp.nb_events()
    susp.inspect_tracks()
    nmin =  susp.nb_events()
    assert nmin > nmin_prev
    assert nmin > 50 
    ## test reset all
    susp.reset_all_events()
    assert susp.nb_events() == 0
    ## Test reloading the divisions from the track graph
    susp.get_divisions()
    assert susp.nb_events() == nev
    ## Track feature change test
    susp.check_size.setChecked( True )
    susp.inspect_tracks()
    assert susp.nb_events() > 50 

def test_boundaries():
    """ Detecting cells on border/boundaries and removing border cells """
    test_img = os.path.join(".", "test_data", "003_crop.tif")
    test_seg = os.path.join(".", "test_data", "003_crop_epyseg.tif")

    ## load and initialize
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    epic.go_epicure("test_epics", test_seg)

    ## check that doesn't find any boundary cells (touching background)
    epic.inspecting.get_boundaries_cells()
    assert len(epic.inspecting.boundary_cells[0]) == 0

    ## remove the border cells, so now should find boundary cells
    epic.editing.remove_border()
    epic.inspecting.get_boundaries_cells()
    assert len(epic.inspecting.boundary_cells[0]) > 20

if __name__ == "__main__":
    test_suspect_frame()
    test_suspect_track()
    test_boundaries()
    print("********* Test suspects cure completed ***********")
