# File: scaler.py
# This file does stuff
#
#

# Import module
from PIL import Image
from PIL import ImageFilter
import random
import math
import time
import os

def main():
 
    # Set Scales
    scale = 8
    blur_scale = 10

    # Get list of input files
    image_names = ls("input")

    # Scale and then save each image
    for image_name in image_names:
        # Scale image
        image = scale_image("input/" + image_name, scale, blur_scale)

        # Save image
        image.save("output/" + image_name)


def ls(path):
    """
    This function takes in a path and returns a list
    of its output not including hidden files
    """
    # Initialize list
    file_list = []

    # Loop though every file
    for file in os.listdir(path):
        if not file.startswith('.'):
            file_list.append(file)

    # Return list
    return file_list


def scale_image(image_name, scale, blur_scale):
    """
    This function takes in an image name
    and returns a scaled up version of that image
    that has been smoothed without adding new colors
    """
   
    # Open image, load pixels in var, get width and height, and get set of colors
    orginal_image = Image.open(image_name)
    orginal_width = orginal_image.width
    orginal_height = orginal_image.height
    orginal_colors = get_set_of_colors(orginal_image)
   
    # Calculate new height and width
    scaled_width = orginal_width * scale
    scaled_height = orginal_height * scale

    # Check if only one color and just scale up linearly if so
    if (len(orginal_colors) == 1):
        scaled_image = orginal_image.resize((scaled_width, scaled_height), resample=Image.LINEAR)
        return scaled_image

    # Create normalized color dictionaries
    normal_color_dict = create_normalized_color_dict(orginal_colors)
    
    # Create grid of surrounding colors
    color_grid = initialize_color_grid(orginal_width+1, orginal_height+1)

    # Create color grid
    color_grid = create_color_grid(color_grid, orginal_image, orginal_width, orginal_height)
    
    # Resize new image, apply filter, and load pixels in var
    scaled_image = orginal_image.resize((scaled_width, scaled_height), resample=Image.LANCZOS)
    scaled_image = scaled_image.filter(ImageFilter.GaussianBlur(blur_scale))
    scaled_pixels = scaled_image.load()
   

    # Loop though every pixel in new image
    for y in range(scaled_height):
        for x in range(scaled_width):
            
            # Get color of current pixel
            current_color = scaled_pixels[x,y]
            nearest_o_x = int(round(x/scale))
            nearest_o_y = int(round(y/scale))
            
            # Get possible colors from color grid
            possible_colors = color_grid[nearest_o_x][nearest_o_y]

            # Set pixel to most similar color
            scaled_pixels[x,y] = get_most_similiar_color(current_color, possible_colors, normal_color_dict)

    # Return image            
    return scaled_image



def initialize_color_grid(width, height):
    """
    This function takes in a width and height and returns a grid
    of empty sets accessible as list[x][y]
    """

    # Initialize var
    grid = list()

    # Loop though every x
    for x in range(width):
        # Reset col
        col = list()

        # Add every y to the row
        for y in range(height):
            col.append(set())

        # Add col to grid
        grid.append(col)

    return grid



def create_normalized_color_dict(set_of_colors):
    """
    This function takes in a set of colors and returns
    a dict of normalized colors assessable by the string of
    their original color
    """

    # Initialize
    normal_color_dict = {}

    # Create dict of normalized colors
    for color in set_of_colors:
        normalized_color = normalize(color)
        normal_color_dict[str(color)] = normalized_color

    # Return
    return normal_color_dict



def create_color_grid(color_grid, image, width, height):
    """
    This function is a boiler plate which creates a grid of colors by calling all
    the edge cases and overflows
    """

    pixels = image.load()

    # Top edge case
    color_grid = color_grid_generator(color_grid, pixels, range(width), {0}, range(-1,1), range(0,1))
      
    # Left edge case
    color_grid = color_grid_generator(color_grid, pixels, {0}, range(height), range(0,1), range(-1,1))

    # Bottom edge case
    color_grid = color_grid_generator(color_grid, pixels, range(width), {height-1}, range(-1,1), range(-1,0))

    # Right edge case
    color_grid = color_grid_generator(color_grid, pixels, {width-1}, range(height), range(0,1), range(-1,1))
   
    # Inside
    color_grid = color_grid_generator(color_grid, pixels, range(1, width-1), range(1, height-1), range(-1,1), range(-1,1))
    
    # Bottom overflow
    for x in range(width):
        color_grid[x][height] = color_grid[x][height-1]

    # Right overflow
    for y in range(height):
        color_grid[width][y] = color_grid[width-1][y]

    # Bottom Right corner overflow
    color_grid[width][height] = color_grid[width][height-1]

    # Return color grid
    return color_grid

def color_grid_generator(color_grid, pixels, x_range, y_range, dx_range, dy_range):
    """
    This function takes in a color grid, pixels, and ranges and creates
    a color grid of the possible colors in the ranges given
    """

    # Loop though all x and ys
    for y in y_range:
        for x in x_range:

            # Initialize color set
            color_set = set()

            # Get square of colors around original pixel
            for dy in dy_range:
                for dx in dx_range:
                    color_set.add(pixels[x+dx, y+dy])

            # Add set to set
            color_grid[x][y] = color_set

    return color_grid
    

def get_set_of_colors(image):
    
    # Initialize color set
    color_set = set()

    # Load pixels of image
    px = image.load()

    # Loop though every pixel and add its color to set
    for y in range(image.height):
        for x in range(image.width):
            color_set.add(px[x,y])

    # Return color set
    return color_set
    
def get_most_similiar_color(base_color, color_set, normal_color_dict):
  
    # Check if set only has one color and return that color if so
    if len(color_set) == 1:
        return next(iter(color_set))

    # Initialize variables
    best_score = -2

    # Normalize base color
    normal_base_color = normalize(base_color)

    for color in color_set:
        # Normalize color in set
        normal_color = normal_color_dict[str(color)]
       
        # Get cosine similarly score
        score = cosineSim(normal_base_color, normal_color)
        
        # Check is best score so far
        if score > best_score:
            best_score = score
            best_color = color

    # Return color with best score
    return best_color


def normalize(color):
    
    # Initialize vars
    sum_of_squares = 0 

    # Create sum of squares var
    for i in range(len(color)):
        sum_of_squares += color[i] * color[i]

    # Square root sum of squares to get magnitude
    magnitude = math.sqrt(sum_of_squares)

    # Create normalized color
    normalized_color = []
    for i in range(len(color)):
       normalized_color.append(color[i] / magnitude)
    
    # Return tuple of normalized color
    return tuple(normalized_color)


def cosineSim(color_1, color_2):

    # Compute dot product
    dot_product = 0
    for i in range(len(color_1)):
        dot_product += color_1[i] * color_2[i] 
    
    # Return dot product
    return dot_product



# Boilerplate
if __name__ == "__main__":
    main()
