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


from time import sleep
from datetime import datetime, timedelta
#from openpyxl import Workbook

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart      
from email.mime.text import MIMEText

print(sys.version)
logging.basicConfig(filename="playout.log", level=logging.INFO)

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
    print(str(da[0]).find("duration="))
    p = str(da[0])[(str(da[0]).find("duration=") + 9):]
    p = p[:p.find("r")-1]
    
    print("dur "+p)
    fps = str(da[0])[(str(da[0]).find("nb_frames=") + 10):]
    fps = fps[:fps.find("r")-1]
    print("fps "+fps)
    rez = float(p)
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
            print('Connect smtp.gmail.com')
            server.ehlo()
            server.login(fromaddr, mypass)
            print('Login smtp.gmail.com')
            server.send_message(msg)
            print('Send')
            server.close()

            print('Email sent!')
        except:
            print('Something went wrong...')

class PlayOutThread(Thread):
    def __init__(self, cmd):
        Thread.__init__(self)
        self._cmd = cmd
    def run(self):
            cmd = self._cmd
            proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, encoding='utf-8')
            stdout, stderr = proc.communicate()
            print(stdout)
            #print(stderr)


async def main():
  if len(sys.argv) < 2:
      print("Argument is empty")
      print("Enter path as an argument")
      sys.exit()
      
  logging.info("BEGIN")
  root = sys.argv[1]
  pattern = '*.[mM][pP][44]'
  file_ext = '.mp4'
  ff_cmd = '-c:a copy -vcodec copy -y'

  logging.info("BEGIN")
  e = k = 0
  for folder, subdirs, files in os.walk(root):
      cur_dir = folder.replace('/','\\')
      cur_dir = folder
      print(cur_dir)
      s = ''
      os.chdir( cur_dir )
      logging.info(os.getcwd())
      for filename in files:

          logging.info(filename)          
          if fnmatch.fnmatch(filename, '*.mp4'):
            DUR = duration(filename)
            cmd = "ffplay -hide_banner -t "+ str(DUR) +" -autoexit -i \"" + filename + "\""
          elif fnmatch.fnmatch(filename, '*41.stream'):
            DUR = 10
            cmd = "ffplay -hide_banner -t "+ str(DUR) +" -autoexit -i rtmp://hunterphoto.ru/Channel4/stream "
          elif fnmatch.fnmatch(filename, '*04.stream'):
            DUR = 6
            cmd = "ffplay -hide_banner -t "+ str(DUR) +" -autoexit -i rtmp://hunterphoto.ru/Channel4/stream "
            
          thplay = PlayOutThread(cmd)

          if DUR > 5:
            logging.info("PLAY " + cmd)
            thplay.start()
            #thplay.join()
            #print(thplay.is_alive(), DUR, cmd)
            await asyncio.sleep(DUR-0.1)
            k += 1
          else:
            print("---------------ERROR")
            e += 1
            logging.error(cur_dir+" "+filename+" :")
  logging.info("TOTAL PLAY " + str(k) + " ERROR " + str(e))


if __name__ == "__main__":
    asyncio.run(main())
