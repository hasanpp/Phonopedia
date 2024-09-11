from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import io

def crop_image(image, target_ratio=(1, 1)):
    img = Image.open(image)

    # Get the dimensions of the image
    img_width, img_height = img.size

    # Calculate the target dimensions based on the target ratio
    target_width = img_width
    target_height = int(img_width * target_ratio[1] / target_ratio[0])

    if target_height > img_height:
        target_height = img_height
        target_width = int(img_height * target_ratio[0] / target_ratio[1])

    # Calculate coordinates for cropping
    left = (img_width - target_width) / 2
    top = (img_height - target_height) / 2
    right = (img_width + target_width) / 2
    bottom = (img_height + target_height) / 2

    # Crop the image
    img = img.crop((left, top, right, bottom))

    # Save the cropped image to a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')

    # Return the cropped image as an InMemoryUploadedFile
    return InMemoryUploadedFile(img_io, None, image.name, 'image/png', img_io.tell(), None)
