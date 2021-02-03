# -*- coding: utf-8 -*-
##------- из архива текстовые файлы программы передач в формат XML для сайта 4 канала 2019 год
##------- программа +2 недели от создания архива


import xml.etree.cElementTree as ET
import os
import sys
import chardet
import rarfile
import pysftp
from datetime import datetime, timedelta


TVPrograms = ET.Element("TVPrograms")

def date_time_rar(Rfile): ## дата упаковки файла 
    ##print(Rfile.namelist()[5])
    Yaer = Rfile.getinfo(Rfile.namelist()[1]).date_time[0]
    Month = Rfile.getinfo(Rfile.namelist()[1]).date_time[1]
    Day = Rfile.getinfo(Rfile.namelist()[1]).date_time[2]
    datetime_Rfile = datetime.strptime(str(Day)+"/"+str(Month)+"/"+str(Yaer)+" 10:00:00", '%d/%m/%Y %H:%M:%S')
    #print(Fore.GREEN)
    print("Date add file in rarfile: " + datetime_Rfile.strftime("%d-%m-%Y"))
    #print(Fore.WHITE)
    return(datetime_Rfile)


def create_tree(txt, we, now):
    
    week = now.isoweekday() ## день недели даты архива
    tl = txt.splitlines() ## на множество строк
    del tl[0]
    td = timedelta(days=we-week+8) ## понедельник ... вс следующей недели
    d_date = now + td
    print("Create XML element <TVDay><Date> " + d_date.strftime("%d-%m-%Y"))

    TVDay = ET.SubElement(TVPrograms, "TVDay")
    ET.SubElement(TVDay, "Date").text = d_date.strftime("%d-%m-%Y")
    TVList = ET.SubElement(TVDay, "TVList")

    for line in tl:
        if line != '':
            TVProgram = ET.SubElement(TVList, "TVProgram")
            ET.SubElement(TVProgram, "Time").text = line[:5]
            ET.SubElement(TVProgram, "ProgramName").text = line[6:-4]
            ET.SubElement(TVProgram, "ProgramAge").text = line[-3:]
   
    return ET.ElementTree(TVPrograms)
    
def sendSFTP():
    #print(Fore.GREEN)
    print("Send to site channel4.ru")
    #print(Fore.RED)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    try:
        srv = pysftp.Connection(host="193.107.237.33", username="****", password="****", cnopts=cnopts)
        srv.put("p_p" + (datetime.now()).strftime('%m_%d_%Y') + ".xml", 'app/web/uploads/programa_peredach.xml')
        srv.close()
    except:
        #print(Fore.RED)
        print("Couldn't connect to new.channel4.ru")
        #print(Fore.WHITE)
        return False
    return True

def main():
  if len(sys.argv) < 2:
      #print(Fore.RED)
      print("NO Argument! RAR file!")
      #print(Fore.WHITE)
      #raw_input("Press Enter to continue...")
      sys.exit()
  print("Process UnRAR ...")    
  rar = sys.argv[1]
  print(rar)
  we = 0
  zf = rarfile.RarFile(rar)
  dt_rar = date_time_rar(zf)
  count = 0
  for name in zf.namelist():
      if name.find('4K') > -1:
          #print(name)
          txtfile = zf.open(name, 'r')
          text = txtfile.read()
          enc = chardet.detect(text).get("encoding")
          if enc and enc.lower() != "utf-8":
              text = text.decode(enc)
              #text = text.encode("utf-8")
          tree = create_tree(text, we, dt_rar)
          #print(text)
          we += 1
          count += 1
          
  print("Find " + str(count) + " files.")          
  if count == 0:
        #print(Fore.RED)
        print("ERROR format text file")
        #raw_input("Press Enter to continue...")
        exit(0)
        sys.exit
        
  #print(Fore.YELLOW)        
  print("Process completed")
  #print(Fore.WHITE)
  tree.write("p_p" + (datetime.now()).strftime('%m_%d_%Y') + ".xml", encoding="utf-8")
  if sendSFTP():
    #print(Fore.YELLOW)
    print("Completed")
    #print(Fore.WHITE)
  else:
    #print(Fore.RED)
    print("Error! No send SFTP")
    #print(Fore.WHITE)
  #raw_input("Press Enter to continue...")
  sys.exit
  
              
if __name__ == "__main__":
    
    #init(convert=True)
    #print(Fore.YELLOW)
    main()
