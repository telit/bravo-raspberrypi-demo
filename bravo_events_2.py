#==============================================================================================================================#
#                        >>> Copyright (C) Telit Communications S.p.A. Italy All Rights Reserved.  <<<
#
#
#
#@brief
#The file contains the main user entry point and all the functions to use the module with the Bravo Board
#
#
#@details
# -The first point is the calling to settings file to store in the module the correct xml files to use in the LWM2M portal
# -The Network connection provides a network registration
# -echo_demo function opens a PDP context, sends a sample string to an echo server and prints out the returned string
# -lwm2m_demo function open a lwm2m connection enabling the lwm2m client on the module, reads data from the BOSH sensors on the Bravo board and write them in the LWM2M portal
#
#
#@author
#Alessio Quieti

#!/usr/bin/env python
import time
import serial
import asyncio
import functools
import re

#from settings import *

response= ""

APN = "web.omnitel.it"


#--------------Global Variables-----------------------
lwm2m = 0

temp  = 0
press = 0
hum   = 0 
airQ  = 0

battery = 0


#Create event object
event = asyncio.Event()
def set_event(event):
    event.set()
    
async def waiter_event(event):
    await event.wait()
    
############# string utilities #########
def find_word(text,search):
    result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
    if len(result)>0:
        return True
    else:
        return False


############# URC MESSAGES #############

def urc_messages_lwm2m():
    ser.flushInput()
    response = ""
    while(find_word(response,"REGISTERED") == False):
        response = ser.readline().decode('utf-8',errors='ignore')
        print("Waiting registration...")
        time.sleep(1)

############# SEND AT COMMAND ###########
def send_at_command(at_command):
    global event
    response = ""
    send_cmd = at_command
    send= ser.write(send_cmd)
    time.sleep(1)
    print(str(send_cmd.decode()))
    response = ser.readline().decode('utf-8',errors='ignore')

    while(response != ''):
        
        if("ACTIVE") in response:
            global lwm2m
            lwm2m = 1
            print("Inside %d" %lwm2m )
        
        if("#BSENS:") in response:
            sensors_val = response.split(",")
            global temp
            global press
            global hum
            global airQ
            temp = float(str(sensors_val[1]))
            press = float(str(sensors_val[2]))
            hum = float(str(sensors_val[3]))
            airQ = int(str(sensors_val[4]))
            print("Inside %s" %str(temp))
            print(press)
            print(hum)
            print(airQ)
            
        if(len(response) > 0):
        
            response = ser.readline().decode('utf-8',errors='ignore')
            if(response != '\r\n'):
                print(str(response))
    event.set()            
                
############# SEND AT COMMAND ###########
def send_at_regards(at_command):
    response = ""
    send_cmd = at_command
    send= ser.write(send_cmd)
    time.sleep(1)
    response = ser.readline().decode('utf-8',errors='ignore')            
    if(response != '\r\n'):
        print(str(response))
        
############### echo demo  ###############
def echo_demo():
    print("ECHO DEMO CALLED")
    send_at_command(b'AT#SGACT=1,1\r\n')
    if(str(response.find("ERROR"))!= -1):
        send_at_command(b'AT#SD=1,0,10510,modules.telit.com\r\n')
        while(str(response.find("CONNECT"))== 0):
            time.sleep(1)
            
        if(str(response.find("CONNECT"))== 0 or str(response.find("ERROR")) != 0 ):
            greatings = ("Hello from Bravo Board !! ")
            send_at_regards(greatings.encode('utf-8'))
            time.sleep(5)
            send_at_regards(b'+++')
            time.sleep(5)
            send_at_command(b'AT#SH=1\r\n')
            send_at_command(b'AT#SGACT=1,0\r\n')
                    
    else:
        {
            print("SGACT ERROR...Application exit")
            
        }    
        
############### LWM2M DEMO ###############        
async def lwm2m_demo():
    send_at_command(b'AT#LWM2MENA?\r\n')
    print("outside %d" %lwm2m)
   
    if (lwm2m): 
        print("LWM2M Client Enabled.. ")
    else:
        send_at_command(b'AT#LWM2MENA=1\r\n')
        urc_messages_lwm2m()
     
    time.sleep(1)
    
    send_at_command(b'AT#LWM2MNEWINST=0,26251,0\r\n')
    
    time.sleep(1)
    
    while(1):
        
        send_at_command(b'AT#BSENS=1\r\n')
           
        print(temp)
        print(press)
        print(hum)
        print(airQ)
        
        cmd_to_send_temp  =("AT#LWM2MSET=1,26251,0,1,0,%s\r\n" %temp)
        cmd_to_send_press =("AT#LWM2MSET=1,26251,0,2,0,%s\r\n" %press)
        cmd_to_send_hum   =("AT#LWM2MSET=1,26251,0,3,0,%s\r\n" %hum)
        cmd_to_send_airQ  =("AT#LWM2MSET=0,26251,0,4,0,%s\r\n" %airQ)
        
        print(cmd_to_send_temp)
        print(cmd_to_send_press)
        print(cmd_to_send_hum)
        print(cmd_to_send_airQ)
        
        send_at_command((cmd_to_send_temp.encode('utf-8')))
        time.sleep(1)
        send_at_command((cmd_to_send_press.encode('utf-8')))
        time.sleep(1)
        send_at_command((cmd_to_send_hum.encode('utf-8')))
        time.sleep(1)
        send_at_command((cmd_to_send_airQ.encode('utf-8')))
        time.sleep(1)
        
        time.sleep(10)

    
############### NETWORK CONNECTION ###############
async def network_connection():    
    print("NETWORK CONNECTION CALLED")
    reg_status = 0
        
    send_at_command(b'AT+CPIN?\r\n')
    await waiter_task
    
    if(str(response.find("READY"))!= -1):
        
        send_at_command(b'AT+CREG?\r\n')
        
        if(str(response.find("1"))!= -1 or str(response.find("5"))!= -1):
            reg_status = 1
        else:
            counter = 0
            while(reg_status != 1 or reg_status !=5):
                
                print("Module is not registered...retrying")
                
                time.sleep(2)  
                counter = counter +1
                if(counter==10):
                    
                    print("Network error, application end")
                    return
        
        
        print("Module registered:  " +str(reg_status))
        send_at_command(b'AT+WS46=30\r\n')
        time.sleep(1)
        send_at_command(b'AT#WS46?\r\n')
        
        while(str(response.find("ERROR"))== 0):
            send_at_command(b'AT#WS46?')
            time.sleep(1)
            
        if(str(response.find("2"))== -1):
            send_at_command(b'AT#WS46=2\r\n')
            send_at_command(b'AT#REBOOT')
        else:
            cmd_to_send=("AT+CGDCONT=1,\"IPV4V6\",\"%s\"\r\n" %APN)
            time.sleep(1)
            cmd_to_send=("AT+CGDCONT=1,\"IPV4V6\",\"%s\"\r\n" %APN)
            time.sleep(1)
            send_at_command((cmd_to_send.encode('utf-8')))
            send_at_command(b'AT+COPS?\r\n')
            time.sleep(1)
            send_at_command(b'AT+CGATT=0\r\n')
            time.sleep(3)
            send_at_command(b'AT+CGATT=1\r\n')
            time.sleep(1)           
        
    else:
        print("ERROR - Insert SIM")
        return
    

print("########## Welcome to Bravo Board Project ##########")
time.sleep(2)
baudrate_in = 115200
print("Opening Serial Port..@"+ str(baudrate_in))

ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate = baudrate_in,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)    


    
async def main():
    
    if ser.isOpen():
        print("Serial Port Opened ")
        ser.flushInput()
    print("Creating task")


    send_at_command(b'AT\r\n')
    await asyncio.wait(waiter_event)
#     
#     
#     time.sleep(1)
#     print("Settings function Calling...")
#     #settings()
    network_connection()
#     #echo_demo()   
#     lwm2m_demo()


asyncio.run(main())

