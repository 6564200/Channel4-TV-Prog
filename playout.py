#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import glob, os
import sys, shutil
import datetime
from subprocess import Popen, PIPE, call
from threading import Thread
import logging
import fnmatch
import asyncio
import json
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep
from datetime import datetime, timedelta

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print(sys.version)
logging.basicConfig(filename="playout.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b %H:%M:%S')

async def check(file):
  proc = Popen("ffprobe -v error -show_format " + file, shell=True, stdout=PIPE, stderr=PIPE)
  proc.wait()
  da = proc.communicate()
  if len(da[0]) > 0:
    rez = -1
    logging.error(str(da[1][:-2])[2:])
  else:
    rez = 1
  return rez

def duration(file):
  proc = Popen("ffprobe -v error -show_streams " + "\"" + file + "\"", shell=True, stdout=PIPE, stderr=PIPE)
  proc.wait()
  da = proc.communicate()
  if len(da[0]) > 0:
    z = str(da[0])
    p = str(da[0])[(str(da[0]).find("duration=") + 9):]
    p = p[:p.find("r")-1]
    fps = str(da[0])[(str(da[0]).find("nb_frames=") + 10):]
    fps = fps[:fps.find("r")-1]
    rez = float(p[:8])
  else:
    rez = -1
  return rez

def sendEmail(self):
        fromaddr = '*********@gmail.com'
        toaddr = "*****@telecom.ru"
        mypass = "*******"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "PlayOUT ТК 4 КАНАЛ г. Екатеринбург"
        body = "PlayOUT 2021"
        msg.attach(MIMEText(body, 'plain'))

        xls_filename = "pla.xlsx"
        with open(xls_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {xls_filename}",)
        msg.attach(part)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

            server.ehlo()
            server.login(fromaddr, mypass)

            server.send_message(msg)

            server.close()

            print('Email sent!')
        except:
            print('Something went wrong...')

class PlayOutThread(Thread):
    def __init__(self, cmd, DUR):
        Thread.__init__(self)
        self._cmd = cmd
        self._DUR = DUR
    def run(self):
            cmd = self._cmd
            DUR = self._DUR
            #player = OMXPlayer(cmd, dbus_name='org.mpris.MediaPlayer2.omxplayer1', args=["-b", "--aspect-mode",  "stretch"])
            #player.set_aspect_mode('stretch')
            #player.play()
            sleep(DUR+1.3)
            player.quit()


def main():
  if len(sys.argv) < 2:
      print("Argument is empty")
      print("Enter path as an argument")
      sys.exit()

  logging.info("BEGIN")
  root = sys.argv[1]
  jsonf = sys.argv[2]
  fjson = open(sys.argv[2])
  schedule = json.load(fjson)

  pattern = '*.[mM][pP][44]'
  file_ext = '.mp4'
  ff_cmd = '-c:a copy -vcodec copy -y'

  logging.info("BEGIN")
  e = k = 0
  player1 = OMXPlayer("/home/pi/playout/Logo4.mp4", dbus_name='org.mpris.MediaPlayer2.omxplayer0', args=["-b"])
  player2 = OMXPlayer("/home/pi/playout/Logo4.mp4", dbus_name='org.mpris.MediaPlayer2.omxplayer1', args=["-b"])
  while True:
    for prog in schedule["program"]:

      if prog["source"].find('.mp4') > 5:
            DUR = duration(prog["source"])
            cmd = prog["source"]
      elif prog["source"].find('41.stream') > 5:
            DUR = prog["dur"]
            cmd = prog["stream"]
      elif prog["source"].find('04.stream') > 5:
            DUR = prog["dur"]
            cmd = prog["stream"]

      #thplay = PlayOutThread(cmd,DUR)

      if DUR > 3:
            logging.info("PLAY " + cmd)
            if (k % 2 == 0):
               player1 = OMXPlayer(cmd, dbus_name='org.mpris.MediaPlayer2.omxplayer1', args=["-b", "--aspect-mode",  "stretch"])
               player2.quit()
            else:
               player2 = OMXPlayer(cmd, dbus_name='org.mpris.MediaPlayer2.omxplayer2', args=["-b", "--aspect-mode",  "stretch"])
               player1.quit()
            sleep(DUR-0.1)
            k += 1
      else:
            #print("---------------ERROR")
            e += 1
            logging.error(cmd)
    logging.info("TOTAL PLAY " + str(k) + " ERROR " + str(e))


if __name__ == "__main__":
    asyncio.run(main())
