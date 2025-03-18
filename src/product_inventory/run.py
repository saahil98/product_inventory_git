# code to test the file locations are working correctly 
import os
import PIL.Image

def fetch_image():
    image_path = os.path.join(os.path.dirname(__file__), 'data', 'image.jpg')
    image = PIL.Image.open(image_path)
    return image.format

print(fetch_image())