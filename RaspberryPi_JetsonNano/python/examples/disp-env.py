#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
import json
import datetime

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
from PIL import Image,ImageDraw,ImageFont
from subprocess import PIPE

logging.basicConfig(level=logging.DEBUG)

try:

    epd = epd2in7.EPD()
    command = subprocess.run(['ssh', 'rp3', '/home/pi/src/measure_home_env_fs/target/debug/measure_home_env_fs', '--dryrun'], text=True, stdout=PIPE)

    parsed = json.loads(command.stdout)

    dt = datetime.datetime.strptime(parsed['ti'], '%Y/%m/%d %H:%M:%S')
    strdt = dt.strftime('%a.%b.%-d %-I:%M%p')

    epd.init()
    fontL = ImageFont.truetype('NotoSansMono-Regular.ttf', 42)
    fontM = ImageFont.truetype('NotoSansMono-Regular.ttf', 30)
    fontS = ImageFont.truetype('NotoSansMono-Light.ttf', 18)
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((15, 0), u'T ' + str(parsed['te']) , font = fontL, fill = 0)
    draw.text((15 + 160, 12), u'C', font = fontM, fill = 0)
    draw.text((15, 40), u'H ' + str(parsed['h']) , font = fontL, fill = 0)
    draw.text((15 + 160, 40 + 12), u'%', font = fontM, fill = 0)
    draw.text((15, 80), u'P ' + str(parsed['p']) , font = fontL, fill = 0)
    draw.text((15 + 160, 80 + 12), u'hPa', font = fontM, fill = 0)
    draw.text((60, 145), strdt, font = fontS, fill = 0)
    epd.display(epd.getbuffer(Himage))

    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7.epdconfig.module_exit()
    exit()
