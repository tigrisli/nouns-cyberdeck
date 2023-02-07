import requests
import logging
from waveshare_epd import epd2in13b_V3
import time
import base64
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import traceback

import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)


url = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"

# Fetch the image seed data from the Nouns Subgraph API without the background
response = requests.get(url, params={
    "query": "query { noun(id: 1) { seed { body accessory head glasses } } }"
})

if response.status_code == 200:
    result = response.json()
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, response.text))


# Parse the JSON response
data = response.json()

# Get the image seed data without the background
seed = data["data"]["noun"]["seed"]

# Convert the seed data to a base64 encoded SVG string without the background
svg = ... # The code to convert the seed to an SVG string without the background
b64 = base64.b64encode(svg.encode()).decode()

# The final base64 encoded SVG string without the background
image_data = f"data:image/svg+xml;base64,{b64}"

# Load the image data into a NumPy array
img = cv2.imdecode(np.frombuffer(base64.b64decode(image_data.split(',')[1]), np.uint8), cv2.IMREAD_UNCHANGED)

# Resize the image to 122x122
img = cv2.resize(img, (122, 122), interpolation = cv2.INTER_CUBIC)

# Save the resized image to a file
cv2.imwrite("resized_image.bmp", img)

# Display the resized image on the Waveshare 2in13v3 e-ink display
... # The code to display the image on the e-ink display

# Initialize the display
epd = epd2in13_V3.EPD()
epd.init()


# Load background image
noun_image = Image.open("resized_image.bmp")

# Create an image with the information
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
image.paste(noun_image)
draw = ImageDraw.Draw(image)

# Display the image on the e-ink display
epd.display(epd.getbuffer(image))

# Close the display
epd.sleep()