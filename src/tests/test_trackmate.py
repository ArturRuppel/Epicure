import epicure.epicuring as epicure
import os

raw_path = os.path.join( ".", "test_data", "003_crop.tif" )
seg_path = os.path.join(".", "test_data", "003_crop_epyseg.tif")

epic = epicure.EpiCure()
epic.verbose = 3  # 0: minimal to 3: debug informations
epic.load_movie(raw_path)
epic.go_epicure(outdir="epics", segmentation_file=seg_path)

epic.outputing.output_mode.setCurrentText("All cells")
epic.outputing.save_tm_xml()
assert os.path.exists( os.path.join(".", "test_data", "epics", "003_crop.xml" ))
