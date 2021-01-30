# File: scaler.py
# This file does stuff
#
#

# Import module
from PIL import Image
from PIL import ImageFilter
import random
import math


def main():
    # Scale image
    scale_image("test.png")


def scale_image(image_name):
   
    # Open image, load pixels in var, and get width and height
    orginal_image = Image.open(image_name)
    orginal_pixels = orginal_image.load()
    orginal_width = orginal_image.width
    orginal_height = orginal_image.height
   
    # Get set of all original colors
    orginal_colors = get_set_of_colors(orginal_image)

    # Initialize
    normal_color_dict = {}

    # Create dict of normalized colors
    for color in orginal_colors:
        normalized_color = normalize(color)
        normal_color_dict[str(color)] = normalized_color

    # Set Scales
    scale = 8
    blur_scale = 10

    # Calculate new height and width
    scaled_width = orginal_width * scale
    scaled_height = orginal_height * scale


    # Resize new image, apply filter, and load pixels in var
    scaled_image = orginal_image.resize((scaled_width, scaled_height), resample=Image.LANCZOS)
    scaled_image = scaled_image.filter(ImageFilter.GaussianBlur(blur_scale))
    scaled_pixels = scaled_image.load()
    
            
    # Loop though every pixel in new image
    for y in range(2*scale,scaled_height-2*scale):
        for x in range(2*scale,scaled_width-2*scale):
            
            # Get color of current pixel
            current_color = scaled_pixels[x,y]
            orginal_x = int(round(x/scale))
            orginal_y = int(round(y/scale))

            # Create color set
            color_set = set()

            # Get square of colors around original pixel
            for dy in range(-1,1):
                for dx in range(-1,1):
                    color_set.add(orginal_pixels[orginal_x+dx, orginal_y+dy])
           
            # Set pixel to most similar color
            scaled_pixels[x,y] = get_most_similiar_color(current_color, color_set, normal_color_dict)
            #scaled_pixels[x,y] = current_color

    # Save image            
    scaled_image.save("output/" + image_name)


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
    
    # Initialize variables
    best_score = -1

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