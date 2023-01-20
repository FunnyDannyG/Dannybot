# this is where most of the bullshit will be taking place
# anything you need to configure will be located in here

# ----------
# Imports
# ----------
import asyncio
import base64
import io
import json
import os
import random
import re
import sys
import time
import traceback
import typing
import urllib
import urllib.request

import aiohttp
import discord
import furl
import numpy
import PIL
import requests
from cleverwrap import CleverWrap
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# ----------
# Variables
# ----------

#this is the bots prefix
dannybot_prefix = "d2."
# easy to call variable that stores our current working directory
dannybot = os.getcwd()
# debug mode is a setting which makes the bot only respond to commands from the user IDs listed in "devs"
debug_mode = True
# put your user ID here, as well as any other user IDs that you would like to be able to bypass debug mode
devs = [
    343224184110841856,  # Danny
    158418656861093888,  # EzoGaming
]
# logo list for the logo command
logolist = [
    "clan",
    "neon",
    "fluffy",
    "water",
    "smurfs",
    "style",
    "runner",
    "blackbird",
    "fabulous",
    "glow",
    "chrominium",
    "amped",
    "supermarket",
    "crafts",
    "fire",
    "steel",
    "glossy",
    "fifties",
    "retro",
    "beauty",
    "birdy",
    "inferno",
    "winner",
    "uprise",
    "global",
    "silver",
    "minions",
    "magic",
    "fancy",
    "orlando",
    "fortune",
    "swordfire",
    "roman",
    "golden",
    "outline",
    "funtime",
]

# dalle shit
DALLE_API = "https://backend.craiyon.com/generate"
DALLE_FORMAT = "png"

# ----------
# Functions
# ----------

# take a provided gif file and unpack each frame to /cache/ffmpeg
def unpack_gif(file):
    os.system(
        f'ffmpeg -i "{file}" -vf fps=25 -vsync 0 "{dannybot}\\cache\\ffmpeg\\temp%04d.png" -y')
    return

# take each frame in /cache/ffmpeg/out and turn it back into a gif
def repack_gif():
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}\\cache\\ffmpeg\\output\\palette.png -y')
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png" -i "{dannybot}\\cache\\ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return

# take each frame in /cache/ffmpeg/out and turn it back into a gif (jpg variant)
def repack_gif_JPG():
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.jpg" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}\\cache\\ffmpeg\\output\\palette.png -y')
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.jpg" -i "{dannybot}\\cache\\ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return

# clear the ffmpeg and ffmpeg/output folders of any residual files
def cleanup_ffmpeg():
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\{file}')
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg\\output'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\output\\{file}')

# iterate through a folder and count every file
def fileCount(folder):
    return sum([len(files) for r, d, files in os.walk(folder)])
    
# overcomplicated function for parsing and matching data with a list of aliases
def ezogaming_regex(datalist, dataentry):
    # ezogaming if you would like to add comments to this catastrophe, be my guest
    # this may even be rewritten completely by the time you are reading this
    with open(f"{dannybot}\\ezogaming\\{datalist}_char") as f:
        entry = f.readlines()
        entry = [x.rstrip() for x in entry]
    with open(f"{dannybot}\\ezogaming\\{datalist}_checker") as f:
        entryalias = f.readlines()
        entryalias = [x.rstrip() for x in entryalias]
    aru = " ".join(dataentry[:])
    inp = re.sub("[^a-z]", "", aru.lower())
    sort = [0] * len(entry)
    for i in range(0, len(entry)):
        sort[i] = i
    random.shuffle(sort)
    for i2 in range(0, len(entry)):
        inputStripped = inp.strip()
        aliasStripped = re.sub(
            "[^a-z]", "", entryalias[sort[i2]].lower().strip())
        entrystripped = re.sub("[^a-z]", "", entry[sort[i2]].lower().strip())
        if (inputStripped in entrystripped) or inputStripped in aliasStripped:
            break
    sort[i2]
    results = entry[sort[i2]]
    return results

# 1/20/23: FunnyDannyG remembers that python has dictionaries
def undertext(name):
    # character overrides
    # you could also put this in a JSON
    underdict = {
        "danny": "https://cdn.discordapp.com/attachments/560608550850789377/1005989141768585276/dannyportrait1.png",
        "danny-funny": "https://cdn.discordapp.com/attachments/560608550850789377/1005999509496660060/dannyportrait3.png",
        "danny-angry": "https://cdn.discordapp.com/attachments/560608550850789377/1005989142825553971/dannyportrait4.png",
        "danny-pissed": "https://cdn.discordapp.com/attachments/560608550850789377/1005989142083145828/dannyportrait2.png",
        "flashlight": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552733170384926/FFlash.png",
        "ezo": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552733170384926/FFlash.png",
        "ezogaming": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552733170384926/FFlash.png",
        "incine": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552737435992084/FIncine.png",
        "pizzi": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552743626780732/FPizzi.png",
        "cris": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552816397951037/FCris.png",
        "seki": "https://cdn.discordapp.com/attachments/1063552619110477844/1063738177212399658/sekiportrait1.png"
    }
    name = underdict.get(name, name)

    # link overrides
    if name.startswith("https://"):
        name = "custom&url=" + name
    return name

# grab the url of a gif file using the tenor api
def gettenor(url=''):
    apikey = "8FMRE051ZV31"
    gifid = url[url.rindex('-')+1:]
    r = requests.get(
        "https://api.tenor.com/v1/gifs?ids=%s&key=%s&media_filter=minimal" % (gifid, apikey))

    if r.status_code == 200:
        gifs = json.loads(r.content)
    else:
        gifs = None
    return gifs['results'][0]['media'][0]['gif']['url']

# idk how any of the next few functions work
# ezogaming wrote all of them

# go through the last 500 messages sent in the channel a command is ran in and check for images
async def message_history_img_handler(ctx):
    channel = ctx.message.channel
    extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',
                  'gif', 'PNG', 'JPG', 'JPEG', 'GIF', 'BMP', 'WEBP', 'GIF']
    async for msg in channel.history(limit=500):
        if len(msg.attachments) > 0:
            ext = msg.attachments[0].url.split('.')[-1]
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            if 'https://tenor.com/view/' in msg.content:
                a = (str(gettenor(msg.content)))
                return a
            else:
                aa = str(msg.content)
                ext = aa.split('.')[-1]
                if ext in extensions:
                    a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                    a = a.split('?')[0]
                    return a

# go through the last 500 messages sent in the channel a command is ran in and check for audio
async def message_history_audio_handler(ctx):
    channel = ctx.message.channel
    extensions = ['wav', 'ogg', 'mp3', 'flac', 'aiff', 'opus', 'm4a',
                  'oga', 'WAV', 'OGG', 'MP3', 'FLAC', 'AIFF', 'OPUS', 'M4A', 'OGA']
    async for msg in channel.history(limit=500):
        if len(msg.attachments) > 0:
            ext = msg.attachments[0].url.split('.')[-1]
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            aa = str(msg.content)
            ext = aa.split('.')[-1]
            if ext in extensions:
                a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                a = a.split('?')[0]
                return a

# go through the last 500 messages sent in the channel a command is ran in and check for videos
async def message_history_video_handler(ctx):
    channel = ctx.message.channel
    extensions = ['mp4', 'avi', 'mpeg', 'mpg', 'webm', 'mov',
                  'mkv', 'MP4', 'AVI', 'MPEG', 'MPG', 'WEBM', 'MOV', 'MKV']
    async for msg in channel.history(limit=500):
        if len(msg.attachments) > 0:
            ext = msg.attachments[0].url.split('.')[-1]
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            aa = str(msg.content)
            ext = aa.split('.')[-1]
            if ext in extensions:
                a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                a = a.split('?')[0]
                return a

# i honestly don't even know what this is for
async def resolve_args(ctx, args, attachments):
    try:
        if 'http' in args[0]:
            url = args[0]
            kys = args[1:]
            text = ' '.join(kys)
            return [url.split('?')[0], text]
        elif attachments:
            url = attachments[0].url
            text = ' '.join(args)
            return [url.split('?')[0], text]
        else:
            url = await message_history_img_handler(ctx)
            text = ' '.join(args)
            return [url, text]
    except IndexError:
        if attachments:
            url = attachments[0].url
            text = ' '.join(args)
            return [url.split('?')[0], text]
        else:
            url = await message_history_img_handler(ctx)
            text = ' '.join(args)
            return [url, text]

# ok back to FunnyDannyG code :)

# primary function of the meme command
# take an image and put centered and outlined impact font text with a black outline over the top and bottom of the image
def make_meme(Top_Text, Bottom_Text, path):
    # open image in PIL
    img = PIL.Image.open(path)

    # fixed font size calc
    # proportionally scales the font to the size of the image, and make sure it doesn't equal 0
    imageSize = img.size
    fontSize = int(imageSize[1]/5)
    if fontSize  <= 0:
        fontSize = 1

    font = ImageFont.truetype(
        f"{dannybot}\\assets\\impactjpn.otf", fontSize)

    # scale and position the text
    topTextSize = font.getsize(Top_Text)
    bottomTextSize = font.getsize(Bottom_Text)
    topTextPositionX = (imageSize[0]/2) - (topTextSize[0]/2)
    topTextPosition = (topTextPositionX, 0)
    bottomTextPositionX = (imageSize[0]/2) - (bottomTextSize[0]/2)
    bottomTextPositionY = imageSize[1] - bottomTextSize[1]
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY - 10)

    # FIXED THE FUCKING STROKE SIZE
    # idk why i never bothered to calculate stroke size like this
    # it divides the size of both top and bottom text by 75 and uses that as the stroke size
    # also we make sure it doesn't equal 0
    top_outline = int((topTextSize[0]//75))
    bottom_outline = int((bottomTextSize[0]//75))
    if top_outline <= 0:
        top_outline = 1
    if bottom_outline <= 0:
        bottom_outline = 1

    # draw the text
    draw = ImageDraw.Draw(img)
    draw.text(topTextPosition, Top_Text, (255, 255, 255), font=font,
              stroke_width=top_outline, stroke_fill=(0, 0, 0))
    draw.text(bottomTextPosition, Bottom_Text, (255, 255, 255),
              font=font, stroke_width=bottom_outline, stroke_fill=(0, 0, 0))

    # save the resulting image
    img.save(f"{dannybot}\\cache\\meme_out.png")
    return

# gif version
def make_meme_gif(Top_Text, Bottom_Text):

    # iterate through every frame in the ffmpeg folder and edit them
    for frame in os.listdir(f"{dannybot}\\cache\\ffmpeg\\"):
        if '.png' in frame:

            # open image in PIL
            img = PIL.Image.open(f"{dannybot}\\cache\\ffmpeg\\{frame}")

            # fixed font size calc
            # proportionally scales the font to the size of the image, and make sure it doesn't equal 0
            imageSize = img.size
            fontSize = int(imageSize[1]/5)
            if fontSize  <= 0:
                fontSize = 1

            font = ImageFont.truetype(
                f"{dannybot}\\assets\\impactjpn.otf", fontSize)

            # scale and position the text
            topTextSize = font.getsize(Top_Text)
            bottomTextSize = font.getsize(Bottom_Text)
            topTextPositionX = (imageSize[0]/2) - (topTextSize[0]/2)
            topTextPosition = (topTextPositionX, 0)
            bottomTextPositionX = (imageSize[0]/2) - (bottomTextSize[0]/2)
            bottomTextPositionY = imageSize[1] - bottomTextSize[1]
            bottomTextPosition = (bottomTextPositionX, bottomTextPositionY - 10)

            # FIX THE FUCKING STROKE SIZE
            # idk why i never bothered to calculate stroke size like this
            # it divides the size of both top and bottom text by 75 and uses that as the stroke size
            # also we make sure it doesn't equal 0
            top_outline = int((topTextSize[0]//75))
            bottom_outline = int((bottomTextSize[0]//75))
            if top_outline <= 0:
                top_outline = 1
            if bottom_outline <= 0:
                bottom_outline = 1

            # draw the text
            draw = ImageDraw.Draw(img)
            draw.text(topTextPosition, Top_Text, (255, 255, 255), font=font,
                    stroke_width=top_outline, stroke_fill=(0, 0, 0))
            draw.text(bottomTextPosition, Bottom_Text, (255, 255, 255),
                    font=font, stroke_width=bottom_outline, stroke_fill=(0, 0, 0))

            # save the resulting image
            img.save(f"{dannybot}\\cache\\ffmpeg\\output\\{frame}")
            print("frame " + frame + " processed")
    repack_gif()

    return

# dalle shit
# Rotty wrote the following three and I don't feel like reading through it and commenting everything

# communicate with the dalle API and ask it to generate our prompt
async def generate_images(prompt: str) -> str(io.BytesIO):
    async with aiohttp.ClientSession() as session:
        async with session.post(DALLE_API, json={"prompt": prompt}) as response:
            if response.status == 200:
                print("Dalle server is OK")
                response_data = await response.json()
                images = [
                    io.BytesIO(base64.decodebytes(bytes(image, "utf-8")))
                    for image in response_data["images"]
                ]
                return images
            else:
                return None

# generate the images for dalles 3x3 grid
def make_collage_sync(images: str(io.BytesIO), wrap: int) -> io.BytesIO:
    image_arrays = [numpy.array(PIL.Image.open(image)) for image in images]
    image_ct = 1
    for image in images:
        print(str(image_ct) + " image(s) generated out of " + str(image_ct))
        image_ct += 1
        image.seek(0)
    collage_horizontal_arrays = [
        numpy.hstack(image_arrays[i: i + wrap])
        for i in range(0, len(image_arrays), wrap)
    ]
    collage_array = numpy.vstack(collage_horizontal_arrays)
    collage_image = Image.fromarray(collage_array)
    collage = io.BytesIO()
    collage_image.save(collage, format=DALLE_FORMAT)
    print("Attempting to generate 3x3")
    collage.seek(0)
    return collage

# assemble and save the image grid
async def make_collage(images: str(io.BytesIO), wrap: int) -> io.BytesIO:
    images = await asyncio.get_running_loop().run_in_executor(
        None, make_collage_sync, images, wrap
    )
    print("3x3 Generated")
    return images