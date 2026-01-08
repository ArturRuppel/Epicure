from ast import main
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from xml.dom import minidom
import xml.etree.ElementTree as ET

# import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import DisjointSet
from skimage.measure import find_contours

import epicure.Utils as ut


# Load metadata
# just a dict

# Load positions
# numpy array of label, pos t, pos x, pos y

# Load segmentation
# numpy  with the same dims as the image (t, y, x)

# Load tracks
# a unique dict of {label_of_daughter_cell: [label_of_mother_cell]}


if __name__ == "__main__":
    tm_file = "test_data/FakeTracks.xml"
