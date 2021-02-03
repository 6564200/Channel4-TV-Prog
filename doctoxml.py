# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime
import xml.etree.cElementTree as ET

month = (('января', '1'), ('февраля', '2'), ('марта', '3'), ('апреля', '4'), ('мая', '5'), ('июня', '6'), ('июля', '7'), ('августа', '8'), ('сентября', '9'), ('октября', '10'), ('ноября', '11'), ('декабря', '12'))

def main():

  if len(sys.argv) < 2:
      print("NO Argument! DOC file!")
      sys.exit()
  print("Process DOC to XML ", sys.argv[1])    
  doc_file = sys.argv[1]
  result = os.system('antiword -m cp1251.txt ' + doc_file + ' > ' + doc_file[:-3] + 'txt')
  text = open(doc_file[:-3] + 'txt').readlines()


  print("---------------------------------------------------------")
  tcls = []
  text = [line.rstrip() for line in text]
  for t in text:
          if (len(t.strip().strip(".").strip()) > 1):  ## ----------- убираем пустое и лишнее
              tcls.append(t.strip().strip(".").strip())

  textcls = []
  timeRe = re.compile('\d\d\\.\d\d') #
  dayRe = re.compile('\d\s\w+,\s\d+\s\w+') # 1 Понедельник, 27 января
  ageRe = re.compile('\(\d*\+\)') # (16+) (6+)

## -------------- убираем переносы
  i = 0
  for t in tcls:
    time = timeRe.findall(t)
    age = ageRe.findall(t)
    if (len(time) > 0 and len(age) == 0):
      tcls[i] = tcls[i] + tcls[i+1]
      tcls.pop(i+1)
    elif (len(time) == 0 and len(age) == 0):
      day = re.findall('воскресенье,|суббота,|пятница,|понедельник,|вторник,|среда,|четверг,', str(t).lower())
      if (len(day) == 0):
        tcls[i] = ''
    i += 1

  tcls = [t for t in tcls if t]
    
  tree = ET.Element("TVPrograms")
## -------------------------------- prsing
  for t in tcls:
      day = re.findall('воскресенье,|суббота,|пятница,|понедельник,|вторник,|среда,|четверг,', str(t).lower())

      if (len(day) > 0):  ### ---------------------- разбираем дату
        tma = t[t.find(",")+1:].strip()
        for old, new in month:
          tma = tma.replace(old, new)
        tma = tma + " " + datetime.now().strftime("%Y")
        date = datetime.strptime(tma, "%d %m %Y" ).strftime("%d-%m-%Y")
        print(date)
        
        TVDay = ET.SubElement(tree, "TVDay")
        ET.SubElement(TVDay, "Date").text = datetime.strptime(tma, "%d %m %Y" ).strftime("%d-%m-%Y")
        TVList = ET.SubElement(TVDay, "TVList")
      else:                       ### --------------- разбираем строки
        time = timeRe.findall(t)
        age = ageRe.findall(t)
        prg = str(t)[str(t).find("«"):str(t).rfind("(")]
        #print(t)
        print(time, age, prg)
        
        TVProgram = ET.SubElement(TVList, "TVProgram")
        ET.SubElement(TVProgram, "Time").text = str(time)
        ET.SubElement(TVProgram, "ProgramName").text = str(prg)
        ET.SubElement(TVProgram, "ProgramAge").text = str(age)
        
  root = ET.ElementTree(tree)
  root.write("doc" + (datetime.now()).strftime('%m_%d_%Y') + ".xml", encoding="utf-8")

if __name__ == "__main__":

    main()
