# this is where most of the bullshit will be taking place
# anything you need to configure will be located in here

# ----------
# Imports
# ----------

import asyncio
import base64
import hashlib
import io
import json
import os
import random
import re
import string
import sys
import time
import traceback
import typing
import urllib
import urllib.request
from textwrap import wrap

import aiohttp
import discord
import furl
import numpy
import openai
import PIL
import requests
from cleverwrap import CleverWrap
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from petpetgif import petpet
from PIL import (GifImagePlugin, Image, ImageColor, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps, ImageSequence)
from wand.image import Image as magick

from fifteen import FifteenAPI

load_dotenv()

# ----------
# Variables
# ----------

# dannybot config
dannybot_prefix = "d." #bot prefix
dannybot_token = os.getenv("TOKEN") #token
dannybot_denialRatio = 1000 # chance for dannybot to deny your command input
dannybot = os.getcwd() # easy to call variable that stores our current working directory
cache_clear_onLaunch = False # dannybot will clear his cache on launch if set to true
debug_mode = False # debug mode is a setting which makes the bot only respond to commands from the user IDs listed in "devs"
logs_channel = 971178342550216705 # channel to log command and cleverbot usage
talking_channel = "talk-to-dannybot" # channel to limit cleverbot usage to
# put your user ID here, as well as any other user IDs that you would like to be able to bypass debug mode
devs = [
    343224184110841856,  # FDG
    158418656861093888,  # Ezo
]

#configs for the image manipulation commands
imageLower = 250 # the smallest image width image commands will use. if the image is thinner than this, it will proportionally scale to this size
imageUpper = 1500 # the largest image width image commands will use. if the image is wider than this, it will proportionally scale to this size

# .env
Cleverbot = CleverWrap(os.getenv("CLEVERBOT_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
removebg_key = os.getenv("REMOVEBG_KEY")
tenor_apikey =  os.getenv("TENOR_KEY")

# external paths
KemonoFriendsPath = "E:\\Anime\\Kemono Friends" # put your kemono friends regex files into here
NekoparaPath = "E:\\Anime\\Nekopara" # put your nekopara regex files into here
PicturesPath = "C:\\Users\\weebm\\Pictures" # set this to your pictures folder
VideosPath = "C:\\Users\\weebm\\Videos" # set this to your videos folder
GifsPath = "C:\\Users\\weebm\\Pictures\\GIFS" # set this to your gifs folder

# tool paths
UltimateVocalRemover = f"{dannybot}\\tools\\UltimateVocalRemover\\python inference.py" # set this to the path of your inference.py file in your install of UltimateVocalRemover
Waifu2x = f"{dannybot}\\tools\\waifu2x-caffe\\waifu2x-caffe-cui.exe" # set this to the path of your waifu2x-caffe-cui.exe file in your waifu2x-caffe install
Fluidsynth = f"{dannybot}\\tools\\Fluidsynth\\fluidsynth.exe"  # set this to the path of your fluidsynth.exe file in your install of FluidSynth

# list of accepted files for the bots public database
database_acceptedFiles = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'wav', 'ogg', 'mp3', 'flac', 'aiff', 'opus', 'm4a','oga', 'mp4', 'avi', 'mpeg', 'mpg', 'webm', 'mov','mkv']

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
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.jpg" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" {dannybot}\\cache\\ffmpeg\\output\\palette.png -y')
    os.system(f'ffmpeg -i "{dannybot}\\cache\\ffmpeg\\output\\temp%04d.png.jpg" -i "{dannybot}\\cache\\ffmpeg\\output\\palette.png" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 8M "{dannybot}\\cache\\ffmpeg_out.gif" -y')
    return

# clear the ffmpeg and ffmpeg/output folders of any residual files
def cleanup_ffmpeg():
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\{file}')
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg\\output'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\output\\{file}')
            
def randhex(bits):
    return hashlib.sha256(str(random.getrandbits(bits)).encode('utf-8')).hexdigest()

def clear_cache():
    for file in os.listdir(f'{dannybot}\\cache'):
        if 'git' not in file and '.' in file:
            os.remove(f'{dannybot}\\cache\\{file}')
            print(f"deleted {dannybot}\\cache\\{file}")
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\{file}')
            print(f'deleted{dannybot}\\cache\\ffmpeg\\{file}')
    for file in os.listdir(f'{dannybot}\\cache\\ffmpeg\\output'):
        if '.png' in file:
            os.remove(f'{dannybot}\\cache\\ffmpeg\\output\\{file}')
            print(f'deleted{dannybot}\\cache\\ffmpeg\\{file}')
    return

# iterate through a folder and count every file
def fileCount(folder):
    return sum([len(files) for r, d, files in os.walk(folder)])

# overcomplicated function for parsing and matching data with a list of aliases
def ezogaming_regex(datalist, dataentry):
    # ezogaming if you would like to add comments to this catastrophe, be my guest - FDG
    # this may even be rewritten completely by the time you are reading this - FDG
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

# 1/20/23: FDG remembers that python has dictionaries
def undertext(name):
    # character overrides
    # you could also put this in a JSON - FDG
    name = name.replace('_',"-")
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
        "seki": "https://cdn.discordapp.com/attachments/1063552619110477844/1063738177212399658/sekiportrait1.png",
        "leffrey" : "https://cdn.discordapp.com/attachments/1063552619110477844/1068092769438019584/leffreyportrait1.png",
        "suggagugga" : "https://cdn.discordapp.com/attachments/1063552619110477844/1068248384164614154/mcflurger.png"
    }
    name = underdict.get(name, name)

    # link overrides
    if name.startswith("https://"):
        name = "custom&url=" + name
    return name

# grab the gif url of a tenor id using the tenor api
def gettenor(gifid=None):
    apikey = tenor_apikey
    r = requests.get(
        "https://api.tenor.com/v1/gifs?ids=%s&key=%s&media_filter=minimal" % (gifid, apikey))

    if r.status_code == 200:
        gifs = json.loads(r.content)
    else:
        gifs = None
    return gifs['results'][0]['media'][0]['gif']['url']

# go through the last 500 messages sent in the channel a command is ran in and check for images
async def message_history_img_handler(ctx):
    channel = ctx.message.channel #define shorthand variable for the message channel
    extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'] #define the extensions the command is looking for in attachments
    async for msg in channel.history(limit=500): #check the last 500 messages
        
        # TENOR IS NOT FUN TO HANDLE - FDG
        if 'https://tenor.com/view/' in msg.content: # check if we have a tenor url
            # extract the tenor gif id from the message contents
            for x in re.finditer(r"tenor\.com/view/.*-(\d+)", str(msg.content)): # you can do basically anything with regex - FDG
                tenorid = x.group(1)
            a = (str(gettenor(tenorid))) #get the gif url from tenor API
            return a
           # end tenor bullshit 
            
        if msg.attachments: #check if there are attachments (will return a List or a None depending on if there are attachments)
            ext = msg.attachments[0].url.split('.')[-1].lower() #extract extension from URL of first attachment and temporarily convert it to lowercase to fix case-sensitivity
            if ext in extensions:
                return msg.attachments[0].url #return url of first attachment in message
        else:
                aa = str(msg.content)
                ext = aa.split('.')[-1].lower()  #extract extension from URL and temporarily convert it to lowercase to fix case-sensitivity
                if ext in extensions:
                    a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0] #extract just url from the text, so a message like "Balls! (its here: http://balls.com/balls.png) Balls!" just returns the first url in the message
                    a = a.split('?')[0] #removes ? from the end of a url so it doesnt download a ?width=500 image
                    return a

# go through the last 500 messages sent in the channel a command is ran in and check for audio
# this isn't commented its just the same shit as the above function
async def message_history_audio_handler(ctx):
    channel = ctx.message.channel
    extensions = ['wav', 'ogg', 'mp3', 'flac', 'aiff', 'opus', 'm4a','oga']
    async for msg in channel.history(limit=500):
        if msg.attachments:
            ext = msg.attachments[0].url.split('.')[-1].lower()
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
# this isn't commented its just the same shit as the above function
async def message_history_video_handler(ctx):
    channel = ctx.message.channel
    extensions = ['mp4', 'avi', 'mpeg', 'mpg', 'webm', 'mov','mkv']
    async for msg in channel.history(limit=500):
        if msg.attachments:
            ext = msg.attachments[0].url.split('.')[-1].lower()
            if ext in extensions:
                return msg.attachments[0].url
        if 'http' in msg.content:
            aa = str(msg.content)
            ext = aa.split('.')[-1]
            if ext in extensions:
                a = re.findall("(?=http).*?(?= |\n|$)", msg.content)[0]
                a = a.split('?')[0]
                return a

# i honestly don't even know what this is for - FDG
# danny its a function that extracts url/arguments from a command run - Ezo
# ok asshat - FDG
# update: i figured out how to use this - FDG
async def resolve_args(ctx, args, attachments):
    try:
        if 'http' in args[0]: #see if first in the list of "args" is a URL
            #Case of "d.meme http://balls.com/balls.png balls|balls"
            url = args[0] #first in list of "args" is set as the url
            text = ' '.join(args[1:]) #everything after that is set as the text and combined to a string
            return [url.split('?')[0], text]
        elif attachments: #otherwise check if there are attachments
            #Case of "d.meme balls|balls" with attached file
            url = attachments[0].url
            text = ' '.join(args) #the command text is everything in the args since there is no url as the first arg
            return [url.split('?')[0], text] #get everything leading up to "?width=500"-type shenenigans
        else: #if there are no attachments or a link, run the context handler
            #Case of "d.meme balls|balls" with no attachment
            url = await message_history_img_handler(ctx)
            text = ' '.join(args)
            return [url, text]
    except IndexError: #this happens whem there is no args[0] because the command was simply, say, "d.explode" with no arguments.
        if attachments: #check if there are attachments
            #Case of "d.meme balls|balls" with attached file
            url = attachments[0].url
            text = ' '.join(args)
            return [url.split('?')[0], text] #get everything leading up to "?width=500"-type shenenigans
        else: #if there are no attachments or a link, run the context handler
            #Case of "d.meme balls|balls" with no attachment
            url = await message_history_img_handler(ctx)
            text = ' '.join(args)
            return [url, text]

def deepfry(inputpath, outputpath):
    image = PIL.Image.open(f'{inputpath}').convert('RGB')
    image.save(f'{dannybot}\\cache\\deepfry_in.jpg', quality=15)
    with magick(filename=f'{dannybot}\\cache\\deepfry_in.jpg') as img:
        img.level(0.2, 0.9, gamma=1.1)
        img.level(0.2, 0.9, gamma=1.1)
        img.sharpen(radius=8, sigma=4)
        img.noise("laplacian", attenuate=1.0)
        img.level(0.2, 0.9, gamma=1.1)
        img.sharpen(radius=8, sigma=4)
        img.save(filename=f'{outputpath}')
    return

def imagebounds(path):

    img = PIL.Image.open(path)

    # lower cap
    if img.size[0] < imageLower:
        ratio = (imageLower/float(img.size[0]))
        new_height = int((float(img.size[1])*float(ratio)))
        img = img.resize((imageLower, new_height), Image.Resampling.LANCZOS)
        img.save(path) # save image with new size
        return

    # upper cap
    if img.size[0] > imageUpper:
        ratio = (imageUpper/float(img.size[0]))
        new_height = int((float(img.size[1])*float(ratio)))
        img = img.resize((imageUpper, new_height), Image.Resampling.LANCZOS)
        img.save(path) # save image with new size
        return
    return

# primary function of the meme command
# take an image and put centered and outlined impact font text with a black outline over the top and bottom of the image
# this is stolen from a, like, decade old repo
def make_meme(Top_Text, Bottom_Text, path):
    img = PIL.Image.open(path)

    imagebounds(path)
    img = PIL.Image.open(path) # reopen the image
        
    # scale and position the text
    fontSize = int(img.size[0])
    font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
    topTextSize = font.getsize(Top_Text)
    bottomTextSize = font.getsize(Bottom_Text)
    
    # find the biggest font size that works, and then make sure its at least 1
    while topTextSize[0] > img.size[0]-20 or bottomTextSize[0] > img.size[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
        topTextSize = font.getsize(Top_Text)
        bottomTextSize = font.getsize(Bottom_Text)
    if fontSize  <= 0:
        fontSize = 1
    
    # center and position the text
    topTextPositionX = (img.size[0]/2) - (topTextSize[0]/2)
    topTextPosition = (topTextPositionX, 0)
    bottomTextPositionX = (img.size[0]/2) - (bottomTextSize[0]/2)
    bottomTextPositionY = img.size[1] - bottomTextSize[1]
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY - 10)

    # FIXED THE FUCKING STROKE SIZE - FDG
    # it divides the size of top text by 75 and uses that as the stroke size
    # also we make sure the stroke size is AT LEAST 1
    outline = int((topTextSize[0]//75))
    if outline <= 0:
        outline = 1

    # draw the text
    draw = ImageDraw.Draw(img)
    draw.text(topTextPosition, Top_Text, (255, 255, 255), font=font,
              stroke_width=outline, stroke_fill=(0, 0, 0))
    draw.text(bottomTextPosition, Bottom_Text, (255, 255, 255),
              font=font, stroke_width=outline, stroke_fill=(0, 0, 0))

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
            path = f"{dannybot}\\cache\\ffmpeg\\{frame}"

            imagebounds(path)
            img = PIL.Image.open(path) # reopen the image
                
            # scale and position the text
            fontSize = int(img.size[0])
            font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
            topTextSize = font.getsize(Top_Text)
            bottomTextSize = font.getsize(Bottom_Text)
            
            # find the biggest font size that works, and then make sure its at least 1
            while topTextSize[0] > img.size[0]-20 or bottomTextSize[0] > img.size[0]-20:
                fontSize = fontSize - 1
                font = ImageFont.truetype(f"{dannybot}\\assets\\impactjpn.otf", fontSize)
                topTextSize = font.getsize(Top_Text)
                bottomTextSize = font.getsize(Bottom_Text)
            if fontSize  <= 0:
                fontSize = 1
            
            # center and position the text
            topTextPositionX = (img.size[0]/2) - (topTextSize[0]/2)
            topTextPosition = (topTextPositionX, 0)
            bottomTextPositionX = (img.size[0]/2) - (bottomTextSize[0]/2)
            bottomTextPositionY = img.size[1] - bottomTextSize[1]
            bottomTextPosition = (bottomTextPositionX, bottomTextPositionY - 10)

            # FIXED THE FUCKING STROKE SIZE - FDG
            # it divides the size of top text by 75 and uses that as the stroke size
            # also we make sure the stroke size is AT LEAST 1
            outline = int((topTextSize[0]//75))
            if outline <= 0:
                outline = 1

            # draw the text
            draw = ImageDraw.Draw(img)
            draw.text(topTextPosition, Top_Text, (255, 255, 255), font=font,
                    stroke_width=outline, stroke_fill=(0, 0, 0))
            draw.text(bottomTextPosition, Bottom_Text, (255, 255, 255),
                    font=font, stroke_width=outline, stroke_fill=(0, 0, 0))

            # save the resulting image
            img.save(f"{dannybot}\\cache\\ffmpeg\\output\\{frame}")
    repack_gif()

    return

# dalle shit
# rotty wrote the following three and I don't feel like reading through it and commenting everything - FDG

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