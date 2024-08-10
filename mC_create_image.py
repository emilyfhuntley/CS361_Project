import os
import time
from PIL import Image, ImageDraw, ImageFont

# Paths for communication
POEM_FILE = "poem.txt"  # The file that will contain the poem
IMAGE_OUTPUT_FILE = "image_path.txt"  # The file to write the image path

def load_image(image_path):
    """Load an image from the specified path."""
    return Image.open(image_path)

def adjust_font_size(draw, lines, font, max_width):
    """Adjust the font size to fit the longest line within the max width."""
    font_size = font.size
    longest_line_width = max(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] for line in lines)
    
    while longest_line_width > max_width and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype("Antro_Vectra_Bolder.otf", font_size)
        longest_line_width = max(draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0] for line in lines)

    return font

def calculate_total_text_height(draw, lines, font, line_spacing, paragraph_spacing):
    """Calculate the total height of the text using the bounding box."""
    total_height = 0
    for line in lines:
        line_height = draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
        total_height += line_height
        
        # Add spacing after each line
        total_height += line_spacing

        # If the line is blank, add paragraph spacing
        if line == "":
            total_height += paragraph_spacing
            
    return total_height

def crop_image(image, total_text_height):
    """Crop the image to 110% of the text height or a minimum of 500px."""
    crop_height = int(total_text_height * 1.1)
    if crop_height < 500:
        crop_height = 500

    return image.crop((0, 0, image.width, crop_height)), crop_height

def draw_text(draw, lines, font, y_start, image_width, text_color):
    """Draw the text on the image."""
    line_spacing = 10  # Space between lines
    paragraph_spacing = 20  # Space between paragraphs

    y_offset = y_start
    x_start = image_width * 0.25 / 2

    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        draw.text((x_start, y_offset), line, fill=text_color, font=font)

        # Add the height of the current line and line spacing
        y_offset += line_bbox[3] - line_bbox[1] + line_spacing  

        # Check for blank lines to add paragraph spacing
        if line == "":  # Assuming a blank line denotes a paragraph break
            y_offset += paragraph_spacing

def create_image_from_poem(poem):
    """Create an image from the given poem."""
    image = load_image("parchment.jpg")
    text_color = (0, 0, 0)
    font = ImageFont.truetype("Antro_Vectra_Bolder.otf", 150)
    draw = ImageDraw.Draw(image)
    
    lines = poem.split("\n")
    max_width = int(image.width * 0.75)

    line_spacing = 10  # Space between lines
    paragraph_spacing = 20  # Space between paragraphs

    font = adjust_font_size(draw, lines, font, max_width)
    total_text_height = calculate_total_text_height(draw, lines, font, line_spacing, paragraph_spacing)

    image, crop_height = crop_image(image, total_text_height)
    draw = ImageDraw.Draw(image)
    y_start = (crop_height - total_text_height) / 2
    draw_text(draw, lines, font, y_start, image.width, text_color)

    # Save the modified image
    output_image_path = "output.jpg"
    image.save(output_image_path)

    return output_image_path

def run_image_creator_service():
    """Run the image creator service, listening for new poems."""
    print("Image creator service starting...\n")

    print("Image creator service listening...\n")
    last_poem = ""
    while True:
        time.sleep(1)

        # Read the poem from the file
        if os.path.exists(POEM_FILE):
            with open(POEM_FILE, "r+") as file:
                poem = file.read().strip()

                if len(poem) > 0:
                    print("New poem detected...\n")
                    print(poem)
                    image_path = create_image_from_poem(poem)
                    file.truncate(0)

                    # Write the image path to the output file
                    with open(IMAGE_OUTPUT_FILE, "w") as file:
                        file.write(image_path)

                    print(f"\nImage created and saved at: {image_path}\n")
                    print("--------------------------------------")
                    print("Image creator service listening...\n")
                    

if __name__ == "__main__":
    run_image_creator_service()
