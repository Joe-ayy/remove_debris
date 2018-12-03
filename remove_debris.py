#!/usr/bin/env python

from gimpfu import *
import sys
import time
import os
import re

#sys.stdout = open('C:\\Users\\100062393\\Documents\\remove_debris_testing.txt', 'w')


# Create a class to handle the data of the trajectory file
class HandleTrajectoryData:
    # Create a list to hold the x and y coordinates pulled from the file
    position_data = []

    # The pixel to meter ratio is 1 pixel = 0.05 meters or 20 pixels = 1 meter
    m2p = 20

    def __init__(self, path):
        # Open the trajectory file via its full path
        file = open(path, 'r')

        # Read the first 14 lines, with the 15th line being the first data entry in the .ply file
        line = file.readline()

        for i in range(0, 14):
            line = file.readline()

        # Loop through the trajectory file until the eof has been reached
        while not line.isspace():
            temp_data = line.split(' ')

            # The temp_data list has 8 components, they are as follows:
            # data_list[0] = float x, data_list[1] = float y
            # data_list[2] = float z, data_list[3] = float roll
            # data_list[4] = float pitch, data_list[5] = float yaw
            # data_list[6] = float time, data_list[7] = float scm

            try:
                x_val = float(temp_data[0])
                y_val = float(temp_data[1])
            except ValueError:
                break

            # Save the data to the position_data list
            self.position_data.append([x_val, y_val])

            # Read the next line in the file
            line = file.readline()

        # Close the file
        file.close()

    def convert_to_pixels(self):
        for i in range(0, len(self.position_data)):
            self.position_data[i][0] = int(round(self.position_data[i][0] * self.m2p))
            self.position_data[i][1] = int(round(self.position_data[i][1] * self.m2p))

    def add_offsets(self, x_offset, y_offset):
        for i in range(0, len(self.position_data)):
            self.position_data[i][0] = self.position_data[i][0] + x_offset
            self.position_data[i][1] = self.position_data[i][1] + y_offset

    def paint_path(self, draw, brush_size, step_size, initial_time, brush_color="white"):
        temp_brush = "b1"  # Brush name
        og_foreground = pdb.gimp_context_get_foreground()  # Saves the original foreground palette color
        pdb.gimp_context_set_foreground(brush_color)  # Sets the foreground palette color to the brush color
        temp_brush = pdb.gimp_brush_new(temp_brush)  # Creates a new brush
        pdb.gimp_brush_set_shape(temp_brush, 0)  # Sets the new brush to a circle
        pdb.gimp_brush_set_radius(temp_brush, 1000)  # Sets the radius of the brush in pixels
        pdb.gimp_brush_set_hardness(temp_brush, 100)  # Sets the hardness of the brush
        pdb.gimp_context_set_opacity(100)  # Sets the opacity of the brush
        pdb.gimp_context_set_brush(temp_brush)  # Sets the brush to the active brush
        pdb.gimp_context_set_brush_size(brush_size)  # Sets the brush size to the desired size

        # Iterate over each point retrieved and converted from the trajectory file to "clean" the dirty map
        for i in range(0, len(self.position_data), step_size):
            # Update a progress bar to show how much longer it will take
            percent_done = float(i) / float(len(self.position_data))
            pdb.gimp_progress_update(percent_done)
            elapsed_time = time.time() - initial_time
            progress_text = "Time elapsed: " + '{0:.2f}'.format(
                elapsed_time) + "s\t" + "Percent completed: " + '{0:.2f}'.format(percent_done * 100) + "%"
            pdb.gimp_progress_set_text(progress_text)

            center = [self.position_data[i][0], self.position_data[i][1]]  # Center of brush
            pdb.gimp_pencil(draw, 2, center)  # Paint in the drawable using the center points

        # When done using the pencil, reset the value for the foreground color previously set
        pdb.gimp_context_set_foreground(og_foreground)
        pdb.gimp_brush_delete(temp_brush)  # Delete the brush


class FilePathHandler:
    info_file_path = ""
    trajectory_file_path = ""

    def __init__(self, path):  # The path needs to be to the directory that contains the desired files
        info_file = ""
        trajectory_file = ""

        # Iterate over the files in the directory to find the .info and .ply files
        for file in os.listdir(path):
            info_match_found = re.match(r'.*?.info', file)
            trajectory_match_found = re.match(r'.*?.ply', file)

            # Check and see if any of the two files are found for each iteration
            # If one of them is found, assign them the proper file name
            if info_match_found:
                info_file = file
            elif trajectory_match_found:
                trajectory_file = file

        # Create and assign the path to each file
        if info_file == "":
            self.info_file_path = ""
        else:
            self.info_file_path = path + '/' + info_file
        if trajectory_file == "":
            self.trajectory_file_path = ""
        else:
            self.trajectory_file_path = path + '/' + trajectory_file


# Get the path to the directory that contains the trajectory and offset files
def get_dir_path(image_path):
    # Specify the delimiters of the path in order to retrieve the directory path
    delimiter1 = image_path.find("\\Documents\\")
    delimiter2 = image_path.find('\\', delimiter1 + 11)
    dir_path = image_path[:delimiter2]
    dir_path = dir_path.replace('\\', '/')

    # Testing
    print(dir_path)

    # Return the path to the needed directory
    return dir_path


def get_offsets(offset_file):
    # Open the file for reading and read the first (1 + 4) => 5 lines to skip over header information
    file = open(offset_file, 'r')
    line = file.readline()

    for i in range(0, 5):
        line = file.readline()

    # Locate the x and y position based on the first instance of the : (colon) character
    x_start = line.find(":")
    y_start = line.find(' ', x_start + 2)
    y_end = line.find('\n', y_start + 1)

    # Set the values of the offset
    x_offset = int(line[x_start + 2: y_start])
    y_offset = int(line[y_start + 1: y_end])

    # Testing
    print("X offset: ", x_offset)
    print("Y offset: ", y_offset)

    # Return the offset values
    return x_offset, y_offset


def run_script(timg, tdrw, b_size, step_size, b_color):
    # Measure the amount of time that has elapsed while the program is running
	init_time = time.time()

	# Get the image and drawable to allow the plugin to modify the dirty map
	img = gimp.image_list()[0]
	drw = pdb.gimp_image_get_active_drawable(img)
	
	# Convert the image to gray-scale as a precaution
	if pdb.gimp_drawable_is_rgb(drw) == True:
		pdb.gimp_image_convert_grayscale(img)
	
	#pdb.gimp_image_convert_rgb(img)
    # Get the path to the file that is currently being worked on
	file_path = pdb.gimp_image_get_filename(gimp.image_list()[0])

    # Get the path to the directory we need to pull files from
	working_dir_path = get_dir_path(file_path)

    # Get the full file paths for the .info (offset) and .ply (trajectory) files
	file_paths = FilePathHandler(working_dir_path)

    # Specify the full file paths for .info and .ply files
	full_offset_file_path = file_paths.info_file_path
	full_trajectory_file_path = file_paths.trajectory_file_path

    # Get the offset values
	x_pix_offset, y_pix_offset = get_offsets(full_offset_file_path)

    # Load in the trajectory file
	walk_path_data = HandleTrajectoryData(full_trajectory_file_path)

    # Convert the trajectory data from meters to pixels (note: data must be rounded from float to int)
	walk_path_data.convert_to_pixels()

    # Add the offsets to the trajectory data
	walk_path_data.add_offsets(x_pix_offset, y_pix_offset)

	# Dictate the brush size
    #b_size = 14

    # Flip the image before painting the path
	pdb.gimp_image_flip(img, 1)

	# Paint the path
	walk_path_data.paint_path(drw, b_size, step_size, init_time, b_color)

	# Flip the image back after painting the path
	pdb.gimp_image_flip(img, 1)
	
	return


register(
    "remove_debris",
    "Remove debris, streaks, and bad data points from the map while retaining the integrity of the store layout.",
    "This plugin runs automatically upon execution.",
    "Joey Harrison & Jair Pedroza",
    "J.H. & J.P.",
    "11/18",
    "<Image>/Tools/Transform Tools/_Remove Debris",
    "RGB*, GRAY*",
    [
        (PF_INT, "b_size", "Enter the brush size (no less than 10): ", 12),
        (PF_INT, "step_size", "Enter the step size (how much to divide the number of passes by): ", 1),
        (PF_STRING, "b_color", "Enter the brush color: ", "white")
    ],
    [],
    run_script)

main()
