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
from typing import Iterator, Union

import numpy as np
from skimage.draw import polygon2mask

import epicure.Utils as ut


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


def _get_metadata(img_data: ET.Element) -> dict[str, Union[int, float, str]]:
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
        ut.show_warning("No space unit found in the XML file. Setting to 'pixel'.")
        units["spatialunits"] = "pixel"  # TrackMate default value.
    if "timeunits" not in units:
        ut.show_warning("No time unit found in the XML file. Setting to 'frame'.")
        units["timeunits"] = "frame"  # TrackMate default value.
    element.clear()  # We won't need it anymore so we free up some memory.
    # .clear() does not delete the element: it only removes all subelements
    # and clears or sets to `None` all attributes.
    return units


def _parse_all_spots(
    it: Iterator[tuple[str, ET.Element]],
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


def _parse_all_tracks(it: Iterator[tuple[str, ET.Element]], tracks: dict[int, list[int]]) -> None:
    """
    Parse the 'AllTracks' XML element to extract track information.

    This function iterates through the XML elements under 'AllTracks' to extract
    track information and populate the tracks dictionary. This dictionary maps
    daughter cell labels to their mother cell labels.

    Args:
        it (ET.iterparse): An iterator for parsing XML elements.
        tracks (dict[int, list[int]]): A dictionary to store the extracted tracks.
    """
    for event, element in it:
        if element.tag == "Edge" and event == "start":
            mother_id = int(element.attrib["SPOT_SOURCE_ID"])
            daughter_id = int(element.attrib["SPOT_TARGET_ID"])
            if daughter_id not in tracks:
                tracks[daughter_id] = [mother_id]
            else:
                tracks[daughter_id].append(mother_id)
            element.clear()

        elif element.tag == "AllTracks" and event == "end":
            break


def _build_label_mapping(positions: np.ndarray, tracks: dict[int, list[int]]) -> dict[int, int]:
    """
    Build a mapping from TrackMate labels to EpiCure labels.

    In TrackMate, each detected spot has a unique label, while in EpiCure,
    labels are constant per tracklet, hence the need for mapping.

    Args:
        positions (np.ndarray): The array of positions.
        tracks (dict[int, list[int]]): The dictionary of tracks.

    Returns:
        dict[int, int]: A dictionary mapping TrackMate labels to EpiCure labels.
    """
    # Reverse mapping from daughter to mother to get simple edges and division edges.
    mother_to_daughters = {}
    for daughter, mothers in tracks.items():
        for mother in mothers:
            if mother not in mother_to_daughters:
                mother_to_daughters[mother] = [daughter]
            else:
                mother_to_daughters[mother].append(daughter)

    edges = {m: d[0] for m, d in mother_to_daughters.items() if len(d) == 1}
    divisions = {m: d for m, d in mother_to_daughters.items() if len(d) > 1}
    fusions = {d: m for d, m in tracks.items() if len(m) > 1}
    fusion_mothers = set()  # a set of mothers that participate in fusions
    for mothers in fusions.values():
        fusion_mothers.update(mothers)

    label_mapping = {}
    new_label = 1
    frames = np.unique(positions[:, 1])

    for frame in frames:
        frame_positions = positions[positions[:, 1] == frame]
        for old_label in frame_positions[:, 0]:
            old_label_int = int(old_label)

            # Division edge => mother keeps its label, each daughter gets a new label.
            if old_label_int in divisions:
                # Assign new label to the mother when not already assigned (tracklet start).
                if old_label_int not in label_mapping:
                    label_mapping[old_label_int] = new_label
                    new_label += 1
                # Assign new labels to each daughter.
                daughters = divisions[old_label_int]
                for daughter in daughters:
                    label_mapping[int(daughter)] = new_label
                    new_label += 1

            # Mother in a fusion => gets its own label, tracklet ends here.
            elif old_label_int in fusion_mothers:
                if old_label_int not in label_mapping:
                    label_mapping[old_label_int] = new_label
                    new_label += 1

            # Daughter in a fusion => gets a new label (multiple mothers merge into this).
            elif old_label_int in fusions:
                if old_label_int not in label_mapping:
                    label_mapping[old_label_int] = new_label
                    new_label += 1
                # If this fusion daughter is also a mother in a simple edge, propagate the label.
                if old_label_int in edges:
                    label_mapping[int(edges[old_label_int])] = label_mapping[old_label_int]

            # Simple edge => mother and daughter share the same label (same tracklet).
            elif old_label_int in edges:
                if old_label_int not in label_mapping:
                    label_mapping[old_label_int] = new_label
                # Propagate the same label to the daughter (continue tracklet).
                label_mapping[int(edges[old_label_int])] = label_mapping[old_label_int]

            # Lone detection or start of new track.
            elif old_label_int not in label_mapping:
                label_mapping[old_label_int] = new_label
                new_label += 1

    # Do we have everyone mapped?
    assert len(label_mapping) == positions.shape[0], "Some labels were not mapped!"
    assert sorted(label_mapping.keys()) == sorted(set(positions[:, 0].astype(int))), "Some labels were not mapped!"

    return label_mapping


def relabel_positions(label_mapping: dict[int, int], positions: np.ndarray) -> np.ndarray:
    """
    Relabel positions to match EpiCure requirements.

    Args:
        label_mapping (dict[int, int]): A dictionary mapping TrackMate labels to EpiCure labels.
        positions (np.ndarray): The array of positions to be relabeled.

    Returns:
        np.ndarray: The relabeled positions.
    """
    new_positions = np.zeros_like(positions)
    for i in range(positions.shape[0]):
        old_label = int(positions[i, 0])
        new_label = label_mapping[old_label]
        new_positions[i] = positions[i]
        new_positions[i, 0] = new_label
    return new_positions


def relabel_tracks(label_mapping: dict[int, int], tracks: dict[int, list[int]]) -> dict[int, list[int]]:
    """
    Relabel tracks to match EpiCure requirements.

    Args:
        label_mapping (dict[int, int]): A dictionary mapping TrackMate labels to EpiCure labels.
        tracks (dict[int, list[int]]): The dictionary of tracks to be relabeled.

    Returns:
        dict[int, list[int]]: The relabeled tracks.
    """
    new_tracks = {}
    for daughter_old, mothers_old in tracks.items():
        daughter_new = label_mapping[daughter_old]
        mothers_new = [label_mapping[mother_old] for mother_old in mothers_old]
        # Ignore entries for which the daughter label is identical to the mother(s) label.
        if daughter_new not in mothers_new:
            new_tracks[daughter_new] = mothers_new
    return new_tracks


def relabel_segmentation(label_mapping: dict[int, int], segmentation: np.ndarray) -> np.ndarray:
    """
    Relabel segmentation to match EpiCure requirements.

    Args:
        label_mapping (dict[int, int]): A dictionary mapping TrackMate labels to EpiCure labels.
        segmentation (np.ndarray): The segmentation array to be relabeled.

    Returns:
        np.ndarray: The relabeled segmentation.
    """
    new_seg = np.zeros_like(segmentation)
    for old_label, new_label in label_mapping.items():
        new_seg[segmentation == old_label] = new_label
    return new_seg


def _parse_Model_tag(
    xml_path: Path,
    metadata: dict[str, Union[int, float, str]],
    segmentation: np.ndarray,
) -> tuple[np.ndarray, dict[int, list[int]]]:
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
        dict[int, list[int]]: A dictionary containing the tracks data.
    """
    with open(xml_path, "rb") as f:
        it = ET.iterparse(f, events=["start", "end"])
        _, root = next(it)  # Saving the root of the tree for later cleaning.

        units: dict[str, str] = {}
        positions: np.ndarray = np.empty((0, 4), dtype=np.float32)
        tracks: dict[int, list[int]] = {}
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
                _parse_all_tracks(it, tracks)
                root.clear()

            if element.tag == "Model" and event == "end":
                root.clear()
                break  # We are not interested in the following data.

    return positions, tracks


if __name__ == "__main__":
    tm_file = "test_data/FakeTracks_with_fusions.xml"
    np.set_printoptions(suppress=True, floatmode="maxprec_equal")

    img_data_tag = _get_ImageData_tag(Path(tm_file))
    metadata = _get_metadata(img_data_tag)
    seg_shape = (int(metadata["nframes"]), int(metadata["height"]), int(metadata["width"]))
    segmentation = np.zeros(seg_shape, dtype=np.uint16)
    positions, tracks = _parse_Model_tag(Path(tm_file), metadata, segmentation)
    # print(positions)
    label_mapping = _build_label_mapping(positions, tracks)
    positions = relabel_positions(label_mapping, positions)
    tracks = relabel_tracks(label_mapping, tracks)
    segmentation = relabel_segmentation(label_mapping, segmentation)
    print(label_mapping)
    # print(metadata)
    # print(positions.shape)
    # print(positions[0:10])

    print(tracks)
