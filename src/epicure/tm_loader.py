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

from cProfile import label
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

from skimage.draw import polygon2mask

import numpy as np

# TODO: re-enable warnings when working EpiCure environment
# import epicure.Utils as ut


def _get_ImageData_tag(xml_path: Path) -> ET.Element:
    """
    Extract the 'ImageData' tag from an XML file.

    This function parses an XML file to find and extract the 'ImageData' tag.
    Once found, a new element with only the attributes is created and returned.

    Args:
        xml_path (Path): The file path of the XML file to be parsed.

    Returns:
        ET.Element: An `ET.Element` object with the 'ImageData' attributes.

    Raises:
        LookupError: If the 'ImageData' tag is not found in the XML file.
    """
    img_data_tag = None
    with open(xml_path, "rb") as f:
        it = ET.iterparse(f, events=["start", "end"])
        _, root = next(it)  # Saving the root of the tree for later cleaning.

        for event, element in it:
            if event == "end" and element.tag == "ImageData":
                # Create a new element with only the attributes (no children subtree).
                img_data_tag = ET.Element(element.tag, element.attrib)
                root.clear()  # Cleaning the tree to free up memory.
                break  # We found what we need, exit early.
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


def _get_units(
    element: ET.Element,
) -> dict[str, str]:
    """Extract units information from an XML element and return it as a dictionary.

    This function deep copies the attributes of the XML element into a dictionary,
    then clears the element to free up memory.

    Args:
        element (ET._Element): The XML element holding the units information.

    Returns:
        dict[str, str]: A dictionary containing the units information.
        Keys are 'spatialunits' and 'timeunits'.

    Warns:
        If the 'spatialunits' or 'timeunits' attributes are not found,
        defaulting them to 'pixel' and 'frame', respectively.
    """
    units = {}  # type: dict[str, str]
    if element.attrib:
        units = deepcopy(element.attrib)
    if "spatialunits" not in units:
        # ut.show_warning("No space unit found in the XML file. Setting to 'pixel'.")
        units["spatialunits"] = "pixel"  # TrackMate default value.
    if "timeunits" not in units:
        # ut.show_warning("No time unit found in the XML file. Setting to 'frame'.")
        units["timeunits"] = "frame"  # TrackMate default value.
    element.clear()  # We won't need it anymore so we free up some memory.
    # .clear() does not delete the element: it only removes all subelements
    # and clears or sets to `None` all attributes.
    return units


def _parse_all_spots(
    it: ET.iterparse,
    positions: np.ndarray,
    segmentation: np.ndarray,
) -> None:
    """
    Parse the 'AllSpots' XML element to extract spot positions and segmentation data.

    This function iterates through the XML elements under 'AllSpots' to extract
    spot positions and update the segmentation array.

    Args:
        it (ET.iterparse): An iterator for parsing XML elements.
        positions (np.ndarray): A NumPy array to store the extracted positions.
        segmentation (np.ndarray): A NumPy array to store segmentation data.
    """
    spot_index = 0
    for event, element in it:
        if element.tag == "Spot" and event == "start":
            t = int(float(element.attrib["POSITION_T"]))  # or should I take FRAME?
            x = float(element.attrib["POSITION_X"])
            y = float(element.attrib["POSITION_Y"])
            label = int(element.attrib["ID"])
            positions[spot_index] = [label, t, x, y]

            contour = element.text
            npoints = int(element.attrib["ROI_N_POINTS"])
            # FIX: coordinates are in real space, need to convert to pixel space.
            # FIX: in EC, t is in real time units or frame units?
            # TODO: wrap this section into a dedicated function.
            if contour is not None:
                coords = np.array([float(x) for x in contour.split()])
                dimension = len(coords) // npoints
                coords = coords.reshape(-1, dimension)
                # TODO: check that the axes are not inverted.
                contour_rc = np.flip(coords, axis=1)  # x, y to row, col
            mask = polygon2mask(segmentation[t].shape, contour_rc)
            segmentation[t][mask] = label

            spot_index += 1
            element.clear()
        elif element.tag == "AllSpots" and event == "end":
            break


def _parse_Model_tag(
    xml_path: Path, metadata: dict[str, int | float], segmentation: np.ndarray
) -> None:
    """
    Extract the 'Model' tag from an XML file.

    This function parses an XML file to find and extract the 'Model' tag.
    Once found, the tag is deep copied and returned.

    Args:
        xml_path (Path): The file path of the XML file to be parsed.
        metadata (dict[str, int | float]): A dictionary to update with extracted units information.
        segmentation (np.ndarray): A NumPy array to store segmentation data.

    Returns:
        np.ndarray: A NumPy array containing the positions data.
    """
    with open(xml_path, "rb") as f:
        it = ET.iterparse(f, events=["start", "end"])
        _, root = next(it)  # Saving the root of the tree for later cleaning.

        units: dict[str, str] = {}
        for event, element in it:
            # Check for the 'Model' tag
            if element.tag == "Model" and event == "start":
                units = _get_units(element)
                metadata.update(units)
                root.clear()  # Cleaning the tree to free up some memory.
                # All the browsed subelements of `root` are deleted.

            # From AllSpots we extract the positions and segmentation.
            if element.tag == "AllSpots" and event == "start":
                positions = np.zeros((int(element.attrib["nspots"]), 4), dtype=np.float32)
                _parse_all_spots(it, positions, segmentation)
                root.clear()

            # From AllTracks we extract the dict of tracks.
            if element.tag == "AllTracks" and event == "start":
                tracks = {}
                # for event, element in it:
                #     print(event, element.tag)
                # tracks_attributes = _build_tracks(it, element)
                root.clear()

                # Removal of filtered spots / nodes.
                # if not keep_all_spots:
                #     # Those nodes belong to no tracks: they have a degree of 0.
                #     lone_nodes = [n for n, d in graph.degree if d == 0]
                #     graph.remove_nodes_from(lone_nodes)

            # Filtering out tracks and adding tracks attribute.
            # if element.tag == "FilteredTracks" and event == "start":
            #     # Removal of filtered tracks.
            #     id_to_keep = _get_filtered_tracks_ID(it, element)
            #     if not keep_all_tracks:
            #         to_remove = [n for n, t in graph.nodes(data="TRACK_ID") if t not in id_to_keep]
            #         graph.remove_nodes_from(to_remove)

            if element.tag == "Model" and event == "end":
                root.clear()
                break  # We are not interested in the following data.

    return positions, tracks


# Load positions
# numpy array of label, pos t, pos x, pos y
# Size of the array is (num_spots, 4) and num_spots is stored in tag AllSpots, attribute nspots

# Load segmentation
# numpy array with the same dims as the image (t, y, x)

# Load tracks
# a unique dict of {label_of_daughter_cell: [label_of_mother_cell]}


if __name__ == "__main__":
    tm_file = "test_data/FakeTracks.xml"
    np.set_printoptions(suppress=True, floatmode="maxprec_equal")

    img_data_tag = _get_ImageData_tag(Path(tm_file))
    metadata = _get_metadata(img_data_tag)
    segmentation = np.zeros(
        (metadata["nframes"], metadata["height"], metadata["width"]), dtype=np.uint16
    )
    positions, tracks = _parse_Model_tag(Path(tm_file), metadata, segmentation)
    # positions, tracks, segmentation = _remap_labels(positions, tracks, segmentation)
    print(metadata)
    print(positions.shape)
    print(positions)

    print(tracks)
