import numpy as np
import os
import epicure.epicuring as epi

def test_load_movie():
    test_img = os.path.join(".", "test_data", "003_crop.tif")
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    assert epic.img.shape == (11,189,212)

def test_load_movie_with_chanel():
    test_img = os.path.join(".", "test_data", "area3_Composite.tif")
    test_seg = os.path.join(".", "test_data", "area3_Composite_epyseg.tif")
    epic = epi.EpiCure()
    resaxis, resval = epic.load_movie(test_img)
    # check the dimensions are correctly loaded
    assert epic.img.shape == (5,2,146,228)
    assert resaxis == 1
    assert resval == 2
    ## check the channels are correctly set
    assert np.mean(epic.img)>=150
    epic.set_chanel(1, 1)
    assert np.mean(epic.img)<150
    assert np.mean(epic.img)>100

def test_load_segmentation():
    test_seg = os.path.join(".", "test_data", "003_crop_epyseg.tif")
    epic = epi.EpiCure()
    epic.load_segmentation(test_seg)
    assert epic.seg.shape == (11,189,212)
    assert np.max(epic.seg) == 1294

def test_suggest():
    test_img = os.path.join(".", "test_data", "003_crop.tif")
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    segfile = epic.suggest_segfile("epics")
    assert segfile is None
    test_img = os.path.join(".", "test_data", "area3_Composite.tif")
    epic.load_movie(test_img)
    segfile = epic.suggest_segfile("epics")
    assert segfile == os.path.join(".", "data_test", "epics", "area3_Composite_labels.tif")

def test_init_epic():
    epic = epi.EpiCure()
    assert epic.img is None

if __name__ == "__main__":
    test_load_movie()
    test_suggest()
    print("********* Test cure completed ***********")
