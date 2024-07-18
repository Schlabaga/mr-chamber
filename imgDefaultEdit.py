from PIL import Image
from PIL import ImageOps


def crop_image(dessus_path, dessous_name, crosshair_folder= ""):
    # Load the image
    image = Image.open(dessus_path)

    # Convert the image to RGBA if not already to ensure transparency support
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Calculate the new dimensions after cropping
    new_width = image.width - 9  # 9 pixels from left and 9 pixels from right
    new_height = image.height - 9  # 9 pixels from top and 9 pixels from bottom

    # Define the region to be cropped
    box = (9, 9, new_width, new_height)

    # Crop the image
    image = image.crop(box)

    # Add transparent pixels to the left and right sides
    image = ImageOps.expand(image, border=(9, 0, 9, 0), fill=(0, 0, 0, 0))

    # Add transparent pixels to the top and bottom sides
    image = ImageOps.expand(image, border=(0, 9, 0, 9), fill=(0, 0, 0, 0))

    # Save the new image
    
    output_path = f"{crosshair_folder}/{dessous_name}.png"
    
    image.save(output_path)
    # Close the original image
    image.close()
    return output_path

def supperpose_image_preview(image_dessus_path, image_dessous_path):
    # Load the images
    image1 = Image.open(image_dessous_path)
    image2 = Image.open(image_dessus_path)

    # Convert the images to RGBA if not already to ensure transparency support
    if image1.mode != 'RGBA':
        image1 = image1.convert('RGBA')
    if image2.mode != 'RGBA':
        image2 = image2.convert('RGBA')

    # Calculate the position to superimpose the images
    x = (320 - 128) // 2
    y = (215 - 128) // 2
    position = (x, y)

    # Resize image1 to 128x128
    # image1 = image1.resize((128, 128))

    # Superimpose the images
    image1.paste(image2, position, image2)

    # Save the new image
    output_path = image_dessus_path.replace("blank.png", "preview.png")
    image1.save(f"{output_path}")

    # Close the original images
    image1.close()
    image2.close
    
    return output_path


