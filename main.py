import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import requests
import logging
from waveshare_epd import epd2in13_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback


# Send the GraphQL query to retrieve the information
query = """
{
  nouns {
    id
    seed {
      background
      body
      accessory
      head
      glasses
    }
    owner {
      id
    }
  }
}
"""

url = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"

response = requests.post(url, json={'query': query})

if response.status_code == 200:
    result = response.json()
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, response.text))


# Initialize the display
epd = epd2in13_V3.EPD()
epd.init()

# Load background image
background_image = Image.open("./images/Nouns602.bmp")

# Create an image with the information
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
image.paste(background_image)
draw = ImageDraw.Draw(image)

# Draw the information on the image
font = ImageFont.truetype('./fonts/LondrinaSolid-Regular.ttf', 16)

text = result["data"]["nouns"][0]["id"]
draw.text((10, 10), text, font=font, fill=255)

text = result["data"]["nouns"][0]["owner"]["id"]
draw.text((10, 30), text, font=font, fill=255)

# Display the image on the e-ink display
epd.display(epd.getbuffer(image))

# Close the display
epd.sleep()
