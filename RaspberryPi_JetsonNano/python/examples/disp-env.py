#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
import json
import datetime
import traceback
import argparse

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
from PIL import Image,ImageDraw,ImageFont
from subprocess import PIPE

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='show temperature, humidity and air pressure.')
parser.add_argument('-i', '--image', action='store_true', help='save image.jpg')
args = parser.parse_args()

try:

    epd = epd2in7.EPD()
    command1 = subprocess.run(['ssh', 'rp3', '/home/pi/.cargo/bin/measure_home_env_fs', '--dryrun'], text=True, stdout=PIPE)
    command2 = subprocess.run(['ssh', 'rp4', '/home/tamanishi/.cargo/bin/measure_air_quality'], text=True, stdout=PIPE)

    # print(command1.stdout)
    # print(command2.stdout)

    parsed1 = json.loads(command1.stdout)
    parsed2 = json.loads(command2.stdout)

    dt = datetime.datetime.strptime(parsed1['ti'], '%Y/%m/%d %H:%M:%S')
    strdt = dt.strftime('%a.%b.%-d %-I:%M%p')

    epd.init()
    fontL = ImageFont.truetype('NotoSansMono-Regular.ttf', 32)
    fontM = ImageFont.truetype('NotoSansMono-Regular.ttf', 26)
    fontS = ImageFont.truetype('NotoSansMono-Light.ttf', 18)
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    # Temperature
    draw.text((28, 0), u'T' , font = fontL, fill = 0)
    draw.text((28 + 52, 0), str(parsed1['te']), font = fontL, fill = 0)
    draw.text((28 + 152, 6), u'\'C', font = fontM, fill = 0)

    # Humidity
    draw.text((28, 32), u'H', font = fontL, fill = 0)
    draw.text((28 + 52, 32), str(parsed1['h']), font = fontL, fill = 0)
    draw.text((28 + 152, 32 + 6), u'%', font = fontM, fill = 0)

    # Pressure
    draw.text((28, 64), u'P', font = fontL, fill = 0)
    draw.text((28 + 52, 64), '{:>4}'.format(parsed1['p']), font = fontL, fill = 0)
    draw.text((28 + 152, 64 + 6), u'hPa', font = fontM, fill = 0)

    # CO2
    draw.text((28, 96), u'C', font = fontL, fill = 0)
    draw.text((28 + 52, 96), '{:>4}'.format(parsed2['co2']), font = fontL, fill = 0)
    draw.text((28 + 152, 96 + 6), u'ppm', font = fontM, fill = 0)

    # DateTime
    draw.text((60, 145), strdt, font = fontS, fill = 0)

    epd.display(epd.getbuffer(Himage))
   
    if args.image:
        Himage.save(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'image.jpg'))

    epd.sleep()
        
except IOError as e:
    logging.info(e)
    print(traceback.format_exc())
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()
