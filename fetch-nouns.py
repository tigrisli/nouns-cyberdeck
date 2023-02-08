import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import requests
import base64
import cv2
import numpy as np
from PIL import Image, ImageDraw
import traceback
from waveshare_epd import epd2in13b_V3
from io import BytesIO

# Set the query to fetch the seed data from the Nouns subgraph API
url = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"
query = '''
query {
  auctions(orderDirection: desc, orderBy: startTime) {
    id
    amount
    startTime
    endTime
    bids(orderDirection: desc,orderBy:amount) {
      id
      amount
      blockNumber
      txIndex
      noun {
        id
        seed {
          background
          body
          accessory
          head
          glasses
        }
      }
    }
  }
}
'''

def build_svg(noun_data, palette, background):
    # Create a string that will hold the svg image
    svg_image = ""

    # Add the opening tag of the svg element
    svg_image += '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'

    # Add the background element
    svg_image += f'<rect width="100" height="100" fill="{palette[background]}"/>'

    # Add the body element
    svg_image += f'<circle cx="50" cy="50" r="35" fill="{palette[noun_data["body"]]}"/>'

    # Add the accessory element
    svg_image += f'<rect x="40" y="40" width="20" height="20" fill="{palette[noun_data["accessory"]]}"/>'

    # Add the head element
    svg_image += f'<circle cx="50" cy="35" r="15" fill="{palette[noun_data["head"]]}"/>'

    # Add the glasses element
    svg_image += f'<rect x="45" y="30" width="10" height="5" fill="{palette[noun_data["glasses"]]}"/>'
    svg_image += f'<rect x="45" y="35" width="10" height="5" fill="{palette[noun_data["glasses"]]}"/>'

    # Close the svg tag
    svg_image += "</svg>"

    return svg_image


def get_noun_data(seed):
    # Retrieve data from noun parts
    noun_data = {
      "body": seed["body"],
      "accessory": seed["accessory"],
      "head": seed["head"],
      "glasses": seed["glasses"]
    }
    palette = seed["palette"]

    return noun_data, palette

def getNoun(seed):
    if "id" in seed:
        id = str(seed["id"])
        name = "Noun {}".format(id)
        description = "Noun {} is a member of the Nouns DAO".format(id)
        parts, background = get_noun_data(seed)
        image = "data:image/svg+xml;base64,{}".format(base64.b64encode(build_svg(parts, seed["palette"], background).encode()).decode())

        noun = {
            "name": name,
            "description": description,
            "image": image
        }
    else:
        return {}

# Fetch the seed data from the Nouns subgraph API
try:
    response = requests.post(url, json={'query': query})
    response.raise_for_status()
    result = response.json()
except Exception as e:
    print(f"Error fetching data from Nouns subgraph API: {e}")
    traceback.print_exc()

# Get the seed data of the first bid in the first auction
seed = result["data"]["auctions"][0]["bids"][0]["noun"]["seed"]

# Build the SVG image using the `getNoun` function from the previous code example
noun = getNoun(seed=seed)

# Convert the seed data to a base64 encoded SVG string
if "image" in noun:
    b64 = base64.b64encode(noun["image"].encode()).decode()
else:
    print(f"Error fetching image")

# The final base64 encoded SVG string
image_data = f"data:image/svg+xml;base64,{b64}"

# Load the image data into a NumPy array
img = np.array(Image.open(BytesIO(base64.b64decode(image_data.split(',')[1].encode()))))

# Resize the image to 122x122
img = cv2.resize(img, (122, 122), interpolation = cv2.INTER_CUBIC)

# Initialize the display
epd = epd2in13b_V3.EPD()
epd.init()

# Load the resized image
noun_image = Image.fromarray(img)

# Create an image with the information
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
image.paste(noun_image)
draw = ImageDraw.Draw(image)

# Display the resized image on the Waveshare 2in13b e-ink display
epd.display(epd.getbuffer(noun_image))
epd.sleep()
