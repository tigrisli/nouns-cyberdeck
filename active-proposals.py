import sys
import os
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import requests
import logging
from waveshare_epd import epd2in13b_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import time
from datetime import datetime, timedelta

def getCountdownCopy(proposal, currentBlock, activeLocale):
    endBlock = int(proposal["endBlock"])
    startBlock = int(proposal["startBlock"])
    blockDuration = endBlock - startBlock
    totalDuration = blockDuration * AVERAGE_BLOCK_TIME_IN_SECS

    remainingDuration = totalDuration - (currentBlock - startBlock) * AVERAGE_BLOCK_TIME_IN_SECS
    if remainingDuration < 0:
        return "0s"

    remainingDays = int(remainingDuration / 86400)
    remainingDuration -= remainingDays * 86400

    remainingHours = int(remainingDuration / 3600)
    remainingDuration -= remainingHours * 3600

    remainingMinutes = int(remainingDuration / 60)
    remainingDuration -= remainingMinutes * 60

    remainingSeconds = int(remainingDuration)

    if remainingDays > 0:
        return str(remainingDays) + "d " + str(remainingHours) + "h " + str(remainingMinutes) + "m"
    elif remainingHours > 0:
        return str(remainingHours) + "h " + str(remainingMinutes) + "m " + str(remainingSeconds) + "s"
    elif remainingMinutes > 0:
        return str(remainingMinutes) + "m " + str(remainingSeconds) + "s"
    else:
        return str(remainingSeconds) + "s"



# Send GraphQL query to retrieve information
query = """
{
  proposals(orderBy: startBlock, orderDirection: desc) {
    id
    proposer {
      id
    }
    status
    title
    startBlock
    endBlock
    createdTimestamp
  }
}
"""

url = "https://api.thegraph.com/subgraphs/name/nounsdao/nouns-subgraph"

response = requests.post(url, json={'query': query})

if response.status_code == 200:
    result = response.json()
else:
    raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, response.text))


# Initialize display
epd = epd2in13b_V3.EPD()
epd.init()

# Load background image
background_image = Image.open("Proposal-glasses.bmp")
background_red_image = Image.open("Proposals-BG-RED.bmp")

# Create image
black_image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
black_image.paste(background_image)

red_image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
red_image.paste(background_red_image)

draw_black = ImageDraw.Draw(black_image)
draw_red = ImageDraw.Draw(red_image)

# Draw information on image
font = ImageFont.truetype('./fonts/LondrinaSolid-Regular.ttf', 16)

title_text = "ACTIVE PROPS"
draw_black.text((5, 3), title_text, font=font, fill=255)


y = 30
AVERAGE_BLOCK_TIME_IN_SECS = 15
timestamp = time.time()

for proposal in result["data"]["proposals"]:
    if proposal["status"] == "ACTIVE":
        id_text = proposal["id"]
        title_text = proposal["title"]
        endBlock = int(proposal["endBlock"])
        currentBlock = int(result["data"]["proposals"][0]["startBlock"])
        createdTimestamp = int(proposal["createdTimestamp"])

        active_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        countdown = getCountdownCopy(proposal, currentBlock, active_local)
        #if countdown == "0s":
            #continue  # skip proposal if countdown has reached 0

        createdDate = datetime.fromtimestamp(createdTimestamp)
        endTimestamp = createdTimestamp + AVERAGE_BLOCK_TIME_IN_SECS * (endBlock - currentBlock)
        # endDate before voting period starts
        endDate = datetime.fromtimestamp(endTimestamp)
        
        print(f"Proposal ID: {id_text}")
        print(f"Title: {title_text}")
        print(f"Countdown: {countdown}")
        print(" ")
        
        # Calculate the remaining time
        #remainingTime = (endTimestamp - timestamp)

        #if remainingTime < 0:
        #    remainingTime = 0

        # Format the remaining time as a string
        #remainingTime_text = str(timedelta(seconds=remainingTime)).split(".")[0]


        draw_black.text((100, y), countdown, font=font, fill=0)    

        draw_black.text((5, y), id_text, font=font, fill=0)

        # If the title overflows, go to the next line
        if draw_red.textsize(title_text, font=font)[0] > epd.width - (-20):
            words = title_text.split()
            line = ''
            for word in words:
                if draw_red.textsize(line + word, font=font)[0] <= epd.width - (-20):
                    line += word + ' '
                else:
                    draw_red.text((38, y), line, font=font, fill=0)
                    y += 15
                    line = word + ' '
            draw_red.text((38, y), line, font=font, fill=0)
        else:
            draw_red.text((38, y), title_text, font=font, fill=0)

        y += 25


# Display image on the e-ink display
epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
epd.sleep()
