#==============================================================================================================================#
#                        >>> Copyright (C) Telit Communications S.p.A. Italy All Rights Reserved.  <<<
#
#
#
#@brief
#
#
#@details
#
#@author
#Alessio Quieti


#!/usr/bin/env python
import time
import serial
import re
import os
from curses import ascii
response= ""

xml_26250 = 0
xml_26251 = 0
xml_26242 = 0
write_permission = 0
 
############# string utilities #########
def find_word(text,search):
    result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
    if len(result)>0:
        return True
    else:
        return False

############# SEND AT COMMAND ###########
def send_at_command(at_command):
    response = ""
    send_cmd = at_command
    send= ser.write(send_cmd)
    
    global xml_26250
    global xml_26251
    global xml_26242
    global write_permission
        
    time.sleep(1)
    print(str(send_cmd.decode()))
    response = ser.readline().decode('utf-8',errors='ignore')

    while(response != ''):
           
        if("26250") in response:
           
            xml_26250 = 1
            
        if("26251") in response:
            xml_26251 = 1
        
        if("26242") in response:
            xml_26242 = 1
   
        if(">>>") in response:
            write_permission = 1

        if(len(response) > 0):
        
            response = ser.readline().decode('utf-8',errors='ignore')
            if(response != '\r\n'):
                print(str(response))

############### write file ###############
def write_file(object_file):
    global write_permission
    ser.flushInput()

    file = "/home/pi/Desktop/Bravo Project/object_%s.xml"%object_file
    filename = "object_%s.xml"%object_file
    f = open(file,"rb")
    
    file_size = os.path.getsize(file)
    
    chunk = 20
    division = 0
    rest = 0
    division = file_size // chunk
    
    rest = file_size - (chunk*division)
    
    print("Division %d"%division)
    print("Resto %d"%rest)
    
    cmd_to_send = ("AT#M2MWRITE=/XML/"+filename+","+str(file_size)+"\r\n")
    
    send_at_command((cmd_to_send.encode('utf-8')))
    
    time.sleep(1)
    i=1
    
    ser.flushInput()
    while(i<=division):
        
        contenuto_file = f.read(chunk)
        ser.write(contenuto_file)
        i = i+1
        time.sleep(0.05)
      
    if(rest>0):
        contenuto_file = f.read(rest)
        ser.write(contenuto_file)
        time.sleep(0.05)
    f.close()     

############### CONFIGURATION ###############
def configuration(object_xml):
    
    print("configuration CALLED")
        
    time.sleep(1)
    
    if(object_xml == "xml_26250"):
        
        print("Missing file object_26250.xml...writing") 
        write_file("26250")
        print("file object_26250.xml - Wrote")
        ser.write(b'\r\n')
        ser.close()
        time.sleep(1)
        
    if(object_xml == "xml_26242"):
        
        ser.open()
        print("Missing file object_26242.xml...writing")
        write_file("26242")
        print("file object_26242.xml - Wrote")
        ser.write(b'\r\n')
        ser.close()
        time.sleep(1)
        
    if(object_xml == "xml_26251"):
        
        ser.open()
        print("Missing file object_26251.xml...writing")
        write_file("26251")
        print("file object_26251.xml - Wrote")
        ser.write(b'\r\n')
        ser.close()
        time.sleep(1)

    time.sleep(1)
    
    print("Complete")
            
baudrate_in = 115200

ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate = baudrate_in,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
        rtscts = True
)


def settings():
    if ser.isOpen():
        ser.flushInput()
    else:
        print("Cannot open Serial Port")

    time.sleep(3)
    print("Module's Configuration started...")
    send_at_command(b'AT#M2MLIST=/XML/\r\n')

    while(xml_26250 != 1 or xml_26251 != 1 or xml_26242 != 1):
        if(xml_26250 == 0):
            configuration("xml_26250")
            
        if(xml_26251 == 0):
            configuration("xml_26251")
          
        if (xml_26242 == 0):
            configuration("xml_26242")
            


    print("COMPLETE!!!") 