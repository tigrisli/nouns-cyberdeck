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
import pytz
from web3 import Web3
from datetime import datetime, timedelta

def getCountdownCopy(remainingDuration):

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

url = "https://api.goldsky.com/api/public/project_cldf2o9pqagp43svvbk5u3kmo/subgraphs/nouns/0.1.0/gn"

response = requests.post(url, json={'query': query})

if response.status_code == 200:
    result = response.json()
    print(result)
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
AVERAGE_BLOCK_TIME_IN_SECS = 12
timestamp = time.time()

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/a06aeb12512443dbb06c0e86dea5bc08"))

# Get the current block number
current_block = w3.eth.blockNumber

def getCountdown(proposal, currentBlock):
    now = datetime.now(pytz.UTC)

    
    startBlock = proposal.get('startBlock')
    endBlock = proposal.get('endBlock')
    timestamp = int(now.timestamp() * 1000)
    print(f"Proposal: {proposal['id']}")
    start_date = now + timedelta(seconds=AVERAGE_BLOCK_TIME_IN_SECS * (startBlock - currentBlock))
    startDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_date.timestamp()))
    print(f"Starts: {startDate}")
    end_date = now + timedelta(seconds=AVERAGE_BLOCK_TIME_IN_SECS * (endBlock - currentBlock))
    endDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_date.timestamp()))
    print(f"Ends: {endDate}")
    if start_date < now and end_date > now:
        time_remaining = end_date - now
        print(f"Time Remainig {time_remaining}")
        
        return startDate,endDate,time_remaining.total_seconds()
    else:
        return startDate,endDate,0


for proposal in result["data"]["proposals"]:
    if proposal["status"] == "ACTIVE":
        id_text = proposal["id"]
        title_text = proposal["title"]
        
        print(f"Title: {title_text}")
        proposal['startBlock'] = int(proposal['startBlock'])
        proposal['endBlock'] = int(proposal['endBlock'])
        startDate,endDate,countdown = getCountdown(proposal,current_block)
        if countdown == 0:
            continue
        print(" ")
        countdown = getCountdownCopy(countdown)
        
        #endDate_text = endDate.strftime("%d/%m/%Y %H:%M")
        draw_black.text((5, y), "End#", font=font, fill=0)
        draw_black.text((38, y), countdown, font=font, fill=0)
        y = y + 15
        draw_black.text((5,y),id_text,font=font,fill=0)
        
        
        
        # Calculate the remaining time
        #remainingTime = (endTimestamp - timestamp)

        #if remainingTime < 0:
        #    remainingTime = 0

        # Format the remaining time as a string
        #remainingTime_text = str(timedelta(seconds=remainingTime)).split(".")[0]


        #draw_black.text((120, y), countdown, font=font, fill=0)    

        #draw_black.text((5, y), id_text, font=font, fill=0)

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
