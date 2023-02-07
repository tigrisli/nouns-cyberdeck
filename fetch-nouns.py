import requests
import base64
import cv2
import numpy as np
from PIL import Image
import traceback
from waveshare_epd import epd2in13b_V3

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

# Fetch the seed data from the Nouns subgraph API
response = requests.post(url, json={'query': query})
if response.status_code == 200:
    result = response.json()
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, response.text))

# Parse the JSON response to get the seed data
data = response.json()

# Get the seed data of the first bid in the first auction
seed = data["data"]["auctions"][0]["bids"][0]["noun"]["seed"]

# Build the SVG image using the `getNoun` function from the previous code example
noun = getNoun(seed=seed)

# Convert the seed data to a base64 encoded SVG string
b64 = base64.b64encode(noun["image"].encode()).decode()

# The final base64 encoded SVG string
image_data = f"data:image/svg+xml;base64,{b64}"

# Load the image data into a NumPy array
img = cv2.imdecode(np.frombuffer(base64.b64decode(image_data.split(',')[1]), np.uint8), cv2.IMREAD_UNCHANGED)

# Resize the image to 122x122
img = cv2.resize(img, (122, 122), interpolation = cv2.INTER_CUBIC)

# Save the resized image to a file
cv2.imwrite("resized_image.bmp", img)

# Initialize the display
epd = epd2in13b_V3.EPD()
epd.init()

# Load the resized image
noun_image = Image.open("resized_image.bmp")

# Create an image with the information
image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
image.paste(noun_image)
draw = ImageDraw.Draw(image)

# Display the resized image on the Waveshare 2in13b e-ink display
epd.display(epd.getbuffer(noun_image))
epd.sleep()
