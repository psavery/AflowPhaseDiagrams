#!/usr/bin/env python
"""Generate a phase diagram image using AFLOW phase diagram data.

There should be four columns in the AFLOW phase diagram data:
temperature, pressure, phase_name, and energy.

In the data file, temperature and pressure should both be increasing
with the pressure varying first and the temperature varying second.

Usage:
    $ <script> <input_file> [output_file]

"""

from collections import namedtuple

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap

import numpy as np

PhaseDataStruct = namedtuple('PhaseDataStruct',
                             'temperature pressure phase_name energy')

PHASE_COLORS = ['red', 'blue', 'gray', 'brown', 'black', 'purple', 'orange',
                'yellow', 'pink', 'green']


def isclose(a, b, abs_tol=1.e-9):
    """Simple function to determine whether two floats are close.

    Args:
        a (float): the first float.
        b (float): the second float.
        abs_tol (float): the absolute tolerance for determing "close".

    Returns:
        bool: True if the floats are close. False otherwise.

    """
    return abs(a - b) <= abs_tol


# Returns a list of PhaseDataStructs
def extract_phase_data_from_file(filename):
    """Extract phase data from a file.

    Args:
        filename (str): the path to the file containing
                        AFLOW phase data.

    Returns:
        list: A list of PhaseDataStruct objects containing the data.

    """
    with open(filename, 'r') as rf:
        data = []
        for line in rf:
            # Remove comments and skip empty lines
            line = line.split('#')[0].strip()
            if not line:
                continue

            lineSplit = line.split()

            # The line should be at least 4 columns wide
            if len(lineSplit) < 4:
                continue

            data.append(PhaseDataStruct(float(lineSplit[0]),  # Temperature
                                        float(lineSplit[1]),  # Pressure
                                        lineSplit[2],  # Phase name
                                        float(lineSplit[3])))  # Energy

    return data


def generate_phase_diagram(input_file, output_file):
    """Take input phase data and generate a .pdf output phase diagram

    Args:
        input_file (str): The path to the AFLOW phase diagram file.
        output_file (str): The path to write the output pdf image.

    Returns:
        None

    """

    data = extract_phase_data_from_file(input_file)

    if len(data) == 0:
        raise ValueError('No phase data found in ' + input_file)

#    print(data)

    # Get the unique phase names from the data
    phase_names = set()
    for entry in data:
        phase_names.add(entry.phase_name)

    # Convert to list
    phase_names = list(phase_names)

    # Sort them in alphabetical order
    phase_names.sort()

    # Move the 'NO_PHASE_DATA' string to the back
    no_phase_data_str = 'NO_PHASE_DATA'
    if no_phase_data_str in phase_names:
        phase_names.remove(no_phase_data_str)
        phase_names.append(no_phase_data_str)

#    print('phase_names is', phase_names)

    # Make sure we are below the number of max phases
    max_phases = len(PHASE_COLORS)
    if len(phase_names) > max_phases:
        raise ValueError('There is currently a maximum of ' +
                         str(max_phases) + ' phases on a single diagram')

    # Generate the imshow data by creating a 2D array of indices of
    # the phase names
    # We assume here that the data is sorted by varying pressure first and
    # then varying temperature.
    plot_data = []
    ref_index = 0
    cur_index = 0
    tol = 1.e-2

    # We will record these as well in the loop
    min_temperature = 1.e300
    max_temperature = -1.0
    min_pressure = 1.e300
    max_pressure = -1.0

    # Outer loop is varying temperature
    while ref_index < len(data):
        _tmp_list = []
        # Inner loop is varying pressure
        while cur_index < len(data) and isclose(data[ref_index].temperature,
                                                data[cur_index].temperature,
                                                abs_tol=tol):
            # Record the boundaries for pressure
            if data[cur_index].pressure < min_pressure:
                min_pressure = data[cur_index].pressure
            if data[cur_index].pressure > max_pressure:
                max_pressure = data[cur_index].pressure

            # Append the index of the most stable phase
            _tmp_list.append(phase_names.index(data[cur_index].phase_name))
            cur_index += 1

        # Record the boundaries for the temperature
        if data[ref_index].temperature < min_temperature:
            min_temperature = data[ref_index].temperature
        if data[ref_index].temperature > max_temperature:
            max_temperature = data[ref_index].temperature

        plot_data.append(_tmp_list)
        ref_index = cur_index

    # All of the inner lists must be the same size
    num_inner_points = len(plot_data[0])
    for entry in plot_data:
        if len(entry) != num_inner_points:
            raise ValueError('Inner lists (varying pressure) must be '
                             'equal in size!')

    # Turn our data into a numpy array
    # A little manipulation is required to orient the plot correctly...
    plot_data = np.flip(np.array(plot_data).transpose(), 0)

#    print('plot_data is', plot_data)

    # Generate the color map and the legend from it
    cmap = ListedColormap(PHASE_COLORS)
    colors = cmap(np.linspace(0, 1, len(phase_names)))

    # For the legend
    custom_lines = []
    for i, phase_name in enumerate(phase_names):
        custom_lines.append(Line2D([0], [0], color=colors[i], lw=4))

    # Label the axes
    plt.xlabel('Temperature (K)')
    plt.ylabel('Pressure (GPa)')
    plt.legend(custom_lines, phase_names, loc='upper right')
    plt.title('Phase Diagram')

    plt.imshow(plot_data, interpolation='nearest', cmap=cmap,
               extent=[min_temperature, max_temperature,
                       min_pressure, max_pressure],
               aspect='auto')

    plt.draw()
    plt.savefig(output_file, dpi=400)


if __name__ == '__main__':

    import sys

    if len(sys.argv) < 2:
        print('Usage: <script> <input_file> [output_file]')
        sys.exit()

    input_file = sys.argv[1]

    if len(sys.argv) < 3:
        output_file = 'AGL_pT_phase_diagram.pdf'
    else:
        output_file = sys.argv[2]

    generate_phase_diagram(input_file, output_file)
