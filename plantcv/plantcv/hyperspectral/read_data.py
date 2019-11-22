# Read in a hyperspectral data cube as an array and parse metadata from the header file

import os
import cv2
import numpy as np
from plantcv.plantcv import params
from plantcv.plantcv import plot_image
from plantcv.plantcv import print_image
from plantcv.plantcv import Spectral_data
from plantcv.plantcv.transform import rescale


def _find_closest(spectral_array, target):
    # A must be sorted
    idx = spectral_array.searchsorted(target)
    idx = np.clip(idx, 1, len(spectral_array) - 1)
    left = spectral_array[idx - 1]
    right = spectral_array[idx]
    idx -= target - left < right - target
    return idx



def read_data(filename):
    """Read hyperspectral image data from file.

        Inputs:
        filename = name of image file

        Returns:
        spectral_array    = image object as numpy array

        :param filename: str
        :return spectral_array: __main__.Spectral_data
        """
    # Store debug mode
    debug = params.debug
    params.debug = None

    # Initialize dictionary
    header_dict = {}

    headername = filename + ".hdr"

    with open(headername, "r") as f:
        # Replace characters for easier parsing
        hdata = f.read()
        hdata = hdata.replace(",\n", ",")
        hdata = hdata.replace("\n,", ",")
        hdata = hdata.replace("{\n", "{")
        hdata = hdata.replace("\n}", "}")
        hdata = hdata.replace(" \n ", "")
        hdata = hdata.replace(";", "")
    hdata = hdata.split("\n")

    # Loop through and create a dictionary from the header file
    for i, string in enumerate(hdata):
        if ' = ' in string:
            header_data = string.split(" = ")
            header_dict.update({header_data[0].rstrip(): header_data[1].rstrip()})
        elif ' : ' in string:
            header_data = string.split(" : ")
            header_dict.update({header_data[0].rstrip(): header_data[1].rstrip()})

    # Reformat wavelengths
    header_dict["wavelength"] = header_dict["wavelength"].replace("{", "")
    header_dict["wavelength"] = header_dict["wavelength"].replace("}", "")
    header_dict["wavelength"] = header_dict["wavelength"].replace(" ", "")
    header_dict["wavelength"] = header_dict["wavelength"].split(",")

    # Create dictionary of wavelengths
    wavelength_dict = {}
    for j, wavelength in enumerate(header_dict["wavelength"]):
        wavelength_dict.update({float(wavelength): float(j)})

    # Replace datatype ID number with the numpy datatype
    dtype_dict = {"1": np.uint8, "2": np.int16, "3": np.int32, "4": np.float32, "5": np.float64, "6": np.complex64,
                  "9": np.complex128, "12": np.uint16, "13": np.uint32, "14": np.uint64, "15": np.uint64}
    header_dict["data type"] = dtype_dict[header_dict["data type"]]

    # Read in the data from the file
    raw_data = np.fromfile(filename, header_dict["data type"], -1)

    # Reshape the raw data into a datacube array
    array_data = raw_data.reshape(int(header_dict["lines"]),
                                  int(header_dict["bands"]),
                                  int(header_dict["samples"])).transpose((0, 2, 1))

    if "default bands" in header_dict:
        header_dict["default bands"] = header_dict["default bands"].replace("{", "")
        header_dict["default bands"] = header_dict["default bands"].replace("}", "")
        default_bands = header_dict["default bands"].split(",")

        pseudo_rgb = cv2.merge((array_data[:, :, int(default_bands[0])],
                                array_data[:, :, int(default_bands[1])],
                                array_data[:, :, int(default_bands[2])]))

    else:
        max_wavelength = max([float(i) for i in wavelength_dict.keys()])
        min_wavelength = min([float(i) for i in wavelength_dict.keys()])
        # Check range of available wavelength
        if max_wavelength >= 635 and min_wavelength <= 490:
            id_red = _find_closest(spectral_array=np.array([float(i) for i in wavelength_dict.keys()]), target=710)
            id_green = _find_closest(spectral_array=np.array([float(i) for i in wavelength_dict.keys()]), target=540)
            id_blue = _find_closest(spectral_array=np.array([float(i) for i in wavelength_dict.keys()]), target=480)

            pseudo_rgb = cv2.merge((array_data[:, :, [id_blue]],
                                    array_data[:, :, [id_green]],
                                    array_data[:, :, [id_red]]))
        else:
            # Otherwise take 3 wavelengths, first, middle and last available wavelength
            id_red = int(header_dict["bands"]) - 1
            id_green = int(id_red / 2)
            pseudo_rgb = cv2.merge((array_data[:, :, [0]],
                                    array_data[:, :, [id_green]],
                                    array_data[:, :, [id_red]]))

    # Gamma correct pseudo_rgb image
    pseudo_rgb = pseudo_rgb ** (1 / 2.2)
    # Scale each of the channels up to 255
    pseudo_rgb = cv2.merge((rescale(pseudo_rgb[:, :, 0]),
                            rescale(pseudo_rgb[:, :, 1]),
                            rescale(pseudo_rgb[:, :, 2])))

    max_wl = float(str(header_dict["wavelength"][-1]).rstrip())
    min_wl = float(str(header_dict["wavelength"][0]).rstrip())

    # Create an instance of the spectral_data class
    spectral_array = Spectral_data(array_data=array_data, max_wavelength=max_wl,
                                   min_wavelength=min_wl, d_type=header_dict["data type"],
                                   wavelength_dict=wavelength_dict, samples=int(header_dict["samples"]),
                                   lines=int(header_dict["lines"]), interleave=header_dict["interleave"],
                                   wavelength_units=header_dict["wavelength units"], array_type="datacube",
                                   pseudo_rgb=pseudo_rgb, filename=filename)

    # Reset debug mode
    params.debug = debug

    if params.debug == "plot":
        # Gamma correct pseudo_rgb image
        plot_image(pseudo_rgb)
    elif params.debug == "print":
        print_image(pseudo_rgb, os.path.join(params.debug_outdir, str(params.device) + "_pseudo_rgb.png"))

    return spectral_array
