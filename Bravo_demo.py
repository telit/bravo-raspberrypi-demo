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
# -The first executed step is accessing settings file to store in the module the correct xml files, which will be used in the LWM2M portal
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
import re
import RPi.GPIO as GPIO
import time
import threading
import settings as sett

channel = 19 #Use this GPIO to monitor the status of the modem ON/OFF
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(channel,GPIO.OUT)
GPIO.output(channel,GPIO.LOW)

response= ""

APN = ""

baudrate_in = 115200 #for serial Port

#--------------Global Variables-----------------------
g_lwm2m = 0
g_temp  = 0
g_press = 0
g_hum   = 0 
g_airQ  = 0
g_battery = 0
# ------------Async Utilities-------------    
global g_event
global g_waiter_task 

g_event = asyncio.Event()

async def waiter(g_event):
    await g_event.wait()
  
############# Serial Port Opening #########
ser = serial.Serial(
        port='/dev/ttyS0',
        baudrate = baudrate_in,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

############# string utilities #########
def find_word(text,search):
    result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
    if len(result)>0:
        return True
    else:
        return False

############# gpio_check function #########
def gpio_check():
    channel_is_on = GPIO.input(channel)

    if not channel_is_on:
        print("Module is Power Off")
        print("Please Power On the module before start")
        return -1
    else:
        print("Module is Power ON")
        return 0
       
    time.sleep(1) 
############# URC MESSAGES #############
def urc_messages_lwm2m():
    global g_event
    i = 1
    ser.flushInput()
    response = ""
    while(find_word(response,"REGISTERED") is False):
        response = ser.readline().decode('utf-8',errors='ignore')
        print("Waiting registration...from %d seconds"%i)
        i = i+1
        time.sleep(1)
        print(response)
        lwm2m_demo()
        #if(i == 10 or i ==20 or i == 30 or i ==40 or i ==50): lwm2m_demo()

############# SEND AT COMMAND ###########
def send_at_command(at_command,g_event):
    response = ""
    send_cmd = at_command
    send= ser.write(send_cmd)
    time.sleep(1)
    print(str(send_cmd.decode()))
    response = ser.readline().decode('utf-8',errors='ignore')
    
    while(response != ''):        
        if("ACTIVE") in response:
            global g_lwm2m
            g_lwm2m = 1
        
        if("#BSENS:") in response:
            sensors_val = response.split(",")
            global g_temp
            global g_press
            global g_hum
            global g_airQ
            g_temp = float(str(sensors_val[1]))
            g_hum = float(str(sensors_val[2]))
            g_press = float(str(sensors_val[3]))
            g_airQ = int(str(sensors_val[4]))
            
        if(len(response) > 0):
        
            response = ser.readline().decode('utf-8',errors='ignore')
            if(response != '\r\n'):
                print(str(response))
                g_event.set()
                
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
def echo_demo(g_event):
    print("ECHO DEMO CALLED")
    send_at_command(b'AT#SGACT=1,1\r\n',g_event)
   
    if(str(response.find("ERROR"))!= -1):
        send_at_command(b'AT#SD=1,0,10510,modules.telit.com\r\n',g_event)
        while(str(response.find("CONNECT"))== 0):
            time.sleep(1)
            
        if(str(response.find("CONNECT"))== 0 or str(response.find("ERROR")) != 0 ):
            greatings = ("Hello from Bravo Board !! ")
            send_at_regards(greatings.encode('utf-8'))
            time.sleep(5)
            send_at_regards(b'+++')
            time.sleep(5)
            send_at_command(b'AT#SH=1\r\n',g_event)
            send_at_command(b'AT#SGACT=1,0\r\n',g_event)
                    
    else:
        {
            print("SGACT ERROR...Application exit")
            
        }    
        
############### LWM2M DEMO ###############        
def lwm2m_demo():
    global g_lwm2m
    global g_event
    
    send_at_command(b'AT#LWM2MENA?\r\n',g_event)
 
   
    if (g_lwm2m): 
        print("LWM2M Client Enabled.. ")
    else:
        send_at_command(b'AT#LWM2MENA=1\r\n',g_event)
        urc_messages_lwm2m()
        
    time.sleep(1)
    i=1
    while(i<=10):
        
        send_at_command(b'AT#BSENS=1\r\n',g_event)
           
        print("temperature: %s" %g_temp)
        print("pressure: %s" %g_press)
        print("humidity: %s" %g_hum)
        print("airQuality: %s" %g_airQ)
        
        cmd_to_send_temp  =("AT#LWM2MSET=1,26251,0,1,0,%s\r\n" %g_temp)
        cmd_to_send_press =("AT#LWM2MSET=1,26251,0,2,0,%s\r\n" %g_press)
        cmd_to_send_hum   =("AT#LWM2MSET=1,26251,0,3,0,%s\r\n" %g_hum)
        cmd_to_send_airQ  =("AT#LWM2MSET=0,26251,0,4,0,%s\r\n" %g_airQ)
            
        send_at_command((cmd_to_send_temp.encode('utf-8')),g_event)
        time.sleep(1)
        send_at_command((cmd_to_send_press.encode('utf-8')),g_event)
        time.sleep(1)
        send_at_command((cmd_to_send_hum.encode('utf-8')),g_event)
        time.sleep(1)
        send_at_command((cmd_to_send_airQ.encode('utf-8')),g_event)
        time.sleep(1)
        
        time.sleep(5)
        i=i+1
    
    print("Application completed")
    send_at_command(b'AT#LWM2MENA=0\r\n',g_event)
    return
############### NETWORK CONNECTION ###############
def network_connection():
    global g_event
       
    print("NETWORK CONNECTION CALLED")
    reg_status = 0
        
    send_at_command(b'AT+CPIN?\r\n',g_event)
  
    if(str(response.find("READY"))!= -1):
        
        send_at_command(b'AT+CREG?\r\n',g_event)
        
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
        send_at_command(b'AT+WS46=30\r\n',g_event)
        time.sleep(1)
        send_at_command(b'AT#WS46?\r\n',g_event)
        
        while(str(response.find("ERROR"))== 0):
            send_at_command(b'AT#WS46?',g_event)
            time.sleep(1)
            
        if(str(response.find("2"))== -1):
            send_at_command(b'AT#WS46=2\r\n',g_event)
            send_at_command(b'AT#REBOOT',event)
            cmd_to_send=("AT+CGDCONT=1,\"IPV4V6\",\"%s\"\r\n" %APN)
            time.sleep(1)
            cmd_to_send=("AT+CGDCONT=1,\"IPV4V6\",\"%s\"\r\n" %APN)
            time.sleep(1)
            send_at_command((cmd_to_send.encode('utf-8')),g_event)
            send_at_command(b'AT+COPS?\r\n',g_event)
            time.sleep(1)
            send_at_command(b'AT+CGATT=0\r\n',g_event)
            time.sleep(3)
            send_at_command(b'AT+CGATT=1\r\n',g_event)
            time.sleep(1)           
        
    else:
        print("ERROR - Insert SIM")
        return
        
       
async def main():
    
    print("########## Welcome to Bravo Board Project ##########\r\n")

    global g_event
    global g_waiter_task
    
    #GPIO CHECK
    ret = 0
    ret = gpio_check()
    if ret is -1:
        return
    
    #Serial port open 
    if ser.isOpen():
        print("Serial Port Opened @"+ str(baudrate_in))
        ser.flushInput()
    time.sleep(2)    

    #Create a Task to wait until 'even' is set
    g_waiter_task = asyncio.create_task(waiter(g_event))
    
    send_at_command(b'AT\r\n',g_event)
    await g_waiter_task
   
    print("Settings function Calling...")
    sett.settings()
    #network_connection()
    #echo_demo()
    lwm2m_demo()
    return
    
    
   
        
if __name__ == '__main__':  
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())