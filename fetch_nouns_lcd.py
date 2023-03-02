import time
import requests
import traceback
import re
import base64
import json
import cv2
import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
import ST7789
from typing import List, Dict

class NounSeed:
  def __init__(self, background: int, body: int, accessory: int, head: int, glasses: int):
    self.background = background
    self.body = body
    self.accessory = accessory
    self.head = head
    self.glasses = glasses

class EncodedImage:
  def __init__(self, filename: str, data: str):
    self.filename = filename
    self.data = data

class NounData:
  def __init__(self, parts: List[EncodedImage], background: str):
    self.parts = parts
    self.background = background



def get_noun_data(seed: NounSeed) -> NounData:
    global palette
    # load the image data. This is a json file that contains the image data. Make sure you have the image-data.json file in the same directory as this file.
    images = json.load(open("image-data.json"))
    bgcolors = images['bgcolors']
    palette = images['palette']
    bodies = images['images']['bodies']
    accessories = images['images']['accessories']
    heads = images['images']['heads']
    glasses = images['images']['glasses']
    background_index = int(seed.background)
    if background_index >= len(bgcolors):
        raise ValueError(f"Invalid background index: {background_index}")
    background = tuple(bgcolors[background_index]) if bgcolors[background_index] is not None else None
    return NounData(
        parts=[
            bodies[int(seed['body'])],
            accessories[int(seed['accessory'])],
            heads[int(seed['head'])],
            glasses[int(seed['glasses'])]
        ],
        background=background
    )


class IEncoder:
    def encode_image(self, filename: str, image):
        raise NotImplementedError


class Rect:
    def __init__(self, length, color_index):
        self.length = length
        self.color_index = color_index


class LineBounds:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class ImageRow:
    def __init__(self, rects, bounds):
        self.rects = rects
        self.bounds = bounds


ImageRows = Dict[int, ImageRow]

class ImageBounds:
    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class RGBAColor:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


class DecodedImage:
    def __init__(self, palette_index, bounds, rects):
        self.palette_index = palette_index
        self.bounds = bounds
        self.rects = rects


class EncodedImage:
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data


class ImageData:
    def __init__(self, palette, images):
        self.palette = palette
        self.images = images


class PngImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def rgba_at(self, x, y):
        raise NotImplementedError

def decode_image(image):
    data = re.sub(r"^0x", "", image)
    palette_index = int(data[0:2], 16)
    bounds = {
        "top": int(data[2:4], 16),
        "right": int(data[4:6], 16),
        "bottom": int(data[6:8], 16),
        "left": int(data[8:10], 16)
    }
    rects = data[10:]

    if rects:
        rects = [
            (int(rect[0:2], 16), int(rect[2:4], 16))
            for rect in re.findall(r".{1,4}", rects)
        ]
    else:
        rects = []

    return {
        "palette_index": palette_index,
        "bounds": bounds,
        "rects": rects
    }

def get_rect_length(current_x, draw_length, right_bound):
    remaining_pixels_in_line = right_bound - current_x
    return draw_length if draw_length <= remaining_pixels_in_line else remaining_pixels_in_line


def build_svg(parts, palette_colors, bg_color=None):
    if bg_color is not None and not isinstance(bg_color, tuple):
        raise ValueError("bg_color must be a tuple")
    svg_image = Image.new('RGBA', (320, 320), bg_color if bg_color else (0, 0, 0, 0))
    draw = ImageDraw.Draw(svg_image)

    for part in parts:
        decoded_image = decode_image(part["data"])
        bounds = decoded_image["bounds"]
        rects = decoded_image["rects"]

        current_x = bounds["left"]
        current_y = bounds["top"]

        for draw in rects:
            draw_length = draw[0]
            color_index = draw[1]
            hex_color = palette_colors[color_index]

            length = get_rect_length(current_x, draw_length, bounds["right"])
            while length > 0:
                if color_index != 0:
                    draw_rect = (current_x * 10, current_y * 10, (current_x + length) * 10, (current_y + 1) * 10)
                    draw.rectangle(draw_rect, fill=hex_color, outline=None)

                current_x += length
                if current_x == bounds["right"]:
                    current_x = bounds["left"]
                    current_y += 1

                draw_length -= length
                length = get_rect_length(current_x, draw_length, bounds["right"])

    return svg_image


def get_noun(noun_id, seed):
    id = str(noun_id)
    name = f"Noun {id}"
    description = f"Noun {id} is a member of the Nouns DAO"
    
    data_ = get_noun_data(seed)
    parts = data_.parts
    background = data_.background
    image = f"data:image/svg+xml;base64,{base64.b64encode(build_svg(parts, palette, background).encode()).decode()}"

    return {
        "name": name,
        "description": description,
        "image": image
    }



# Set the query to fetch the seed data from the Nouns subgraph API
url = "https://api.goldsky.com/api/public/project_cldf2o9pqagp43svvbk5u3kmo/subgraphs/nouns/0.1.0/gn"
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
try:
    response = requests.post(url, json={'query': query})
    response.raise_for_status()
    result = response.json()
    # save the result to a file
    #with open("result.json", "w") as f:
        #import json
        #json.dump(result, f)
    print(response.json())
        
except Exception as e:
    print(f"Error fetching data from Nouns subgraph API: {e}")
    traceback.print_exc()


noun = result["data"]["auctions"][0]["bids"][0]["noun"]["id"]
# Get the seed data of the first bid in the first auction
seed = result["data"]["auctions"][0]["bids"][0]["noun"]["seed"]

# Get the Noun data
noun_data = get_noun(noun, seed)
image_data = noun_data["image"]
# save image attribute to a file
with open("noun.svg", "wb") as f:
    f.write(base64.b64decode(image_data.split(",")[1].encode()))
    

# convert the svg image to raster image
cairosvg.svg2png(url="noun.svg",write_to="noun.png")
# Load the image data into a NumPy array
img = np.array(cv2.imread("noun.png"))

# Resize the image to 122x122
#img = cv2.resize(img, (8, 8), interpolation = cv2.INTER_CUBIC)

# Initialize the display
display = ST7789.ST7789(
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,
    dc=9,
    backlight=19,
    spi_speed_hz=80_000_000
)

display.begin()


# Load the resized image + rotate 90
noun_image = Image.fromarray(img)
#noun_image = noun_image.transpose(Image.ROTATE_90)

imageblack_h = Image.new('1',(135 , 240),255)
imageblack_draw = ImageDraw.Draw(imageblack_h)
imagered_h = Image.new('1',(135 , 240),255)
imagered_draw = ImageDraw.Draw(imagered_h)
noun_image = noun_image.resize((140,140))
noun_image = noun_image.convert('RGB')
#noun_image = noun_image.transpose(Image.ROTATE_90)
enhancer = ImageEnhance.Contrast(noun_image)
image = enhancer.enhance(2)
imagered_h.paste(noun_image,(-15,0))

# Display the information on the LCD display
display.display(noun_image)
#epd.sleep()



def get_time_remaining(start_time, end_time):
    current_time = int(time.time())
    time_remaining = int(end_time) - current_time
    minutes, seconds = divmod(time_remaining,60)
    hours, minutes = divmod(minutes, 60)
    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_remaining,time_str

font = ImageFont.truetype('./fonts/LondrinaSolid-Regular.ttf', 16)

if "auctions" in result["data"] and len(result["data"]["auctions"]) > 0 and "bids" in result["data"]["auctions"][0] and len(result["data"]["auctions"][0]["bids"]) > 0 and "noun" in result["data"]["auctions"][0]["bids"][0]:
    noun_number = result["data"]["auctions"][0]["bids"][0]["noun"]["id"]
    if len(result["data"]["auctions"][0]["bids"]) > 0:
        current_bid = result["data"]["auctions"][0]["bids"][0]["amount"]
    else:
        current_bid = "0"
else:
    print("Error: Noun data not found")


current_bid = result["data"]["auctions"][0]["bids"][0]["amount"]
current_bid = float(current_bid) / 1000000000000000000 # convert to ETH
bid = f"Bid: {current_bid:.2f}ETH"

start_time = result["data"]["auctions"][0]["startTime"]
end_time = result["data"]["auctions"][0]["endTime"]

imageblack_draw.text((10, 160), "Noun: " + str(noun_number), font=font,  fill=0)
imageblack_draw.text((10, 175), bid, font=font, fill=0)

while True:
    
    # Get the time remaining
    time_remaining, time_str = get_time_remaining(start_time, end_time)
    if time_remaining <= 5:
        break

    # Display the time remaining on the LCD display
    font = ImageFont.truetype('./fonts/LondrinaSolid-Regular.ttf', 16)
    image = Image.new("RGB", (240, 240), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Noun: " + str(noun_number), font=font, fill=(0, 0, 0))
    draw.text((10, 30), bid, font=font, fill=(0, 0, 0))
    draw.text((10, 50), "Time Remaining:", font=font, fill=(0, 0, 0))
    draw.text((10, 70), time_str, font=font, fill=(0, 0, 0))
    display.display(image)
        
    # Wait for 1 second before updating the display again
    time.sleep(1)
    