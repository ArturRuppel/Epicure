"""
Module for loading TrackMate files into EpiCure.

This loader uses an iterative parsing approach to efficiently handle large XML files.

Relevant metadata such as time step and pixel size are stored into a dictionary.
The cells positions are stored in a unique NumPy array with columns for label, time,
x position, and y position.
Segmentations are stored as NumPy arrays with dimensions matching the original image data.
Tracks are stored as a dictionary mapping daughter cell labels to their mother cell labels:
{label_of_daughter_cell: [label_of_mother_cell]}
"""

import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

# import epicure.Utils as ut


# TODO: For metadata, I still need to grab space and time units from the Model tag.


def _get_ImageData_tag(xml_path: Path) -> ET.Element:
    """
    Extract the 'ImageData' tag from an XML file.

    This function parses an XML file to find and extract the 'ImageData' tag.
    Once found, the tag is deep copied and returned.

    Args:
        xml_path (Path): The file path of the XML file to be parsed.

    Returns:
        ET.Element: A deep copied `ET.Element` object representing the 'ImageData' tag.

    Raises:
        LookupError: If the 'ImageData' tag is not found in the XML file.
    """
    img_data_tag = None
    with open(xml_path, "rb") as f:
        it = ET.iterparse(f, events=["start", "end"])
        for event, element in it:
            if event == "end" and element.tag == "ImageData":
                img_data_tag = deepcopy(element)
                element.clear()
            elif event == "end":
                element.clear()

    if img_data_tag is None:
        raise LookupError("The 'ImageData' tag was not found in the XML file.")

    return img_data_tag


def _get_metadata(img_data: ET.Element) -> dict[str, int | float]:
    """
    Extract metadata from the 'ImageData' XML element.

    Parameters
    ----------
    img_data : ET.Element
        The XML element containing the 'ImageData' information.

    Returns
    -------
    dict
        A dictionary containing the extracted image metadata.
    """
    int_keys = ["width", "height", "nframes"]
    float_keys = ["pixelwidth", "pixelheight", "timeinterval"]
    metadata = {}
    for key in int_keys + float_keys:
        metadata[key] = img_data.attrib.get(key)

    for key in int_keys:
        if metadata[key] is None:
            raise KeyError(f"No '{key}' attribute in the 'ImageData' XML element.")
        metadata[key] = int(metadata[key])
    for key in float_keys:
        if metadata[key] is None:
            raise KeyError(f"No '{key}' attribute in the 'ImageData' XML element.")
        metadata[key] = float(metadata[key])
    return metadata


# Load positions
# numpy array of label, pos t, pos x, pos y
# Size of the array is (num_spots, 4) and num_spots is stored in tag AllSpots, attribute nspots

# Load segmentation
# numpy array with the same dims as the image (t, y, x)

# Load tracks
# a unique dict of {label_of_daughter_cell: [label_of_mother_cell]}


if __name__ == "__main__":
    tm_file = "test_data/FakeTracks.xml"

    img_data_tag = _get_ImageData_tag(Path(tm_file))
    metadata = _get_metadata(img_data_tag)
    print(metadata)
