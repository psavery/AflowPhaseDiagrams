#!/usr/bin/env python
"""Generate a fake AFLOW phase diagram data file.

The number of phases should be specified as an argument.

There will be four columns in the AFLOW phase diagram data:
temperature, pressure, phase_name, and energy.

In the data file, temperature and pressure will both be increasing
with the pressure varying first and the temperature varying second.

Usage:
    $ <script> <num_phases>

Output:
    fake_diagram_with_<num_phases>_phases.out

"""

import sys


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


# The second argument is the number of phases
if len(sys.argv) != 2:
    sys.exit('Usage: <script> <num_phases>')

num_phases = int(sys.argv[1])

# Create the grid conditions
temp_min = 0.0
press_min = 0.0

temp_max = 3000.0
press_max = 100.0

temp_interval = 10.0
press_interval = 1.0

# Figure out the number of points. We just need estimates.
temp_num_points = int((temp_max - temp_min) / temp_interval)
press_num_points = int((press_max - press_min) / press_interval)

total_num_points = temp_num_points * press_num_points

points_per_phase = total_num_points / num_phases

# Generate the fake phase names
phase_names = []
for i in range(num_phases):
    phase_names.append('test' + str(i + 1))

# Set up the counters
phase_index = 0

temp_current = 0.0
press_current = 0.0

point_counter = 0

tol = 1.e-5

# Start with the header
out_str = '#  T(K)        P(GPa)                   '
out_str += 'PhaseName             G(eV/atom)\n'
while temp_current < temp_max or isclose(temp_current, temp_max, tol):

    while press_current < press_max or isclose(press_current, press_max, tol):

        # Check if we need to change the phase name
        # Don't change the phase name if we are on the last phase
        if point_counter > points_per_phase and phase_index != num_phases - 1:
            phase_index += 1
            point_counter = 0

        out_str += str(temp_current) + '     '
        out_str += str(press_current) + '     '
        out_str += phase_names[phase_index] + '     '
        out_str += str(-1.00000) + '\n'

        point_counter += 1

        press_current += press_interval

    # Reset the current pressure
    press_current = press_min

    temp_current += temp_interval

output_file_name = 'fake_diagram_with_' + str(num_phases) + '_phases.out'
with open(output_file_name, 'w') as wf:
    wf.write(out_str)
