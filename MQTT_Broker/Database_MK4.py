import sqlite3
import os
import time
import threading
from collections import namedtuple
import re

database = 'database.db'

def CreateDeviceList():
#Create a device list contains all the information of a device
    con = sqlite3.connect(database)
    cur = con.cursor()

    try:
        SQL = ('''CREATE TABLE IF NOT EXISTS device_list 
            (Device_ID TEXT PRIMARY KEY,
            Device_name TEXT,
            Location TEXT,
            Input_pin TEXT,
            Output_pin TEXT,
            Topics TEXT,
            Status TEXT
            );''')
        cur.execute(SQL)        
        con.commit()
        con.close()
        return True

    except:
        print ('Creating Device list table failed')
        return False

def CreateDevice(ID):
#Create a device in the main device list
    con = sqlite3.connect(database)
    cur = con.cursor()
    
    try:
        cur.execute('''INSERT INTO device_list (Device_ID) \
            VALUES (?, ?, ?)''', (ID))

        con.commit()
        con.close()
        return True
    
    except:
        print ('Duplicated Device ID, Creating Device failed')
        return False


def CheckOutput(pin):
#check the output pin of the device, return the output device
    pin = str(pin)
    outputDevice = {}

    #outputDevice format is pin_number : Type
    with open('C:/Users/Cille/Desktop/OutputDevice.txt', 'r') as file:
        for line in file.readlines():
             outputDevice[line.split('=')[0].strip()] = line.split('=')[1].strip()
    
    if pin in outputDevice:
        print (outputDevice[pin])
        type = outputDevice[pin]
        return type
    else:
        print ('ERROR: Undefined Device Type')
        return False
    
    
def CheckSensor(pin):
#check the function of the device, return the function of device    
    pin = str(pin)
    DeviceFunction = {}
    
    #DeviceFormat format is ID : Function
    with open('C:/Users/Cille/Desktop/DeviceFunction.txt', 'r') as file:
        for line in file.readlines():
            DeviceFunction[line.split('=')[0].strip()] = line.split('=')[1].strip()
    
    if pin in DeviceFunction:
        print (DeviceFunction[pin])
        function = DeviceFunction[pin]
        return function
    else:
        print ('ERROR: Undefined Device function')
    return False

def SelectDevice(ID):
#show all the information of a device, device ID required
    con = sqlite3.connect(database)
    cur = con.cursor()

    try:
        #select and print out all the information of the device

        device = cur.execute('''SELECT 
                Device_ID, Type, Function, Location, Device_name, Status 
                FROM device_list WHERE Device_ID = ?''',
                [(ID)])

        for row in device:
            print ('Device_ID = ', row[0])
            print ('Type = ', row[1])
            print ('Function = ', row[2])
            print ('Location = ', row[3])
            print ('Device name = ', row[4])
            print ('Status = ', row[5])
    
        con.commit()
        con.close()
        return True
    
    except:
        print ('Device_ID doesn\'t exist')
        return False


def DeleteDevice(ID):
#delete the device from the device list, device ID required
    con = sqlite3.connect(database)
    cur = con.cursor()
    try:
        cur.execute("DELETE from device_list WHERE Device_ID = ?", [(ID)])
        con.commit()
        con.close()
        print ('Delete successed')
        return True

    except:
        print('Can\'t delete the device')
        return False

def CreateSensorLocation(location):
#Create a location table contains the sensor data within it
    con = sqlite3.connect(database)
    cur = con.cursor()

    try:
        #first add some basic information
        SQL = '''CREATE TABLE IF NOT EXISTS %s
            (Device_ID TEXT PRIMARY KEY,
            Function TEXT,
            Status TEXT
            );'''%location
        cur.execute(SQL)
        location = '\'%s\''%location

        #add every function in the DeviceFunction to the location table
        with open('C:/Users/Cille/Desktop/DeviceFunction.txt', 'r') as file:
            for line in file.readlines():
                DeviceFunction = line.split('=')[1].strip()
                DeviceFunction = '\'%s\''%DeviceFunction
                SQL = 'ALTER TABLE %s ADD COLUMN %s TEXT'\
                    %(location, DeviceFunction)
                cur.execute(SQL)

        con.commit()
        con.close()
        return True

    except:
        print ('Creating Location table failed')
        return False

def DeleteSensorLocation(location):
#delete the location table
    con = sqlite3.connect(database)
    cur = con.cursor()

    try:
        location = '\'%s\''%location
        SQL = 'DROP TABLE %s'%location
        cur.execute(SQL)
        con.commit()
        con.close()
        return True
    
    except:
        print('Can\'t delete the table')
        return False

def AddDataType(location, data_type):
#add one type of data like temperature into a location 
    try:
        #add a new column into the table
        con = sqlite3.connect(database)
        cur = con.cursor()
        location = '\'%s\''%location
        data_type = '\'%s\''%data_type
        SQL = 'ALTER TABLE %s ADD COLUMN %s TEXT' %(location, data_type)
        cur.execute(SQL)
        con.commit()
        con.close()
        return True
    
    except:
        print ('Can\'t add the data type')
        return False

def CheckTopic(ID):
#return the subscribed topics of the device    
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()
        topics = cur.execute('''SELECT Topics 
                FROM device_list WHERE Device_ID = ?''',
                [(ID)])
        con.close()
        return topics
    except:
        print("Device ID doesn't exist")
        return False
     
def InsertSensorLocation(ID, location):
#add a sensor to a location    
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()
        DeviceFunction = '\'%s\''%CheckSensor(ID)
        ID = '\'%s\''%ID
        location = '\'%s\''%location
        SQL = 'INSERT INTO %s (Device_ID, Function) \
            VALUES (%s, %s)'%(location, ID, DeviceFunction)
        cur.execute(SQL)
        con.commit()
        con.close()
        return True
    
    except:
        print ('Can\'t add the sensor to that location')
        return False

def UpdateSensorData(ID, location, pin, data):
#update the measurement data into the location table
    con = sqlite3.connect(database)
    cur = con.cursor()

    data_type = CheckSensor(pin)
    location = '\'%s\''%location
    data_type = '\'%s\''%data_type
    data = '\'%s\''%data
    ID = '\'%s\''%ID

    try:
        SQL = 'UPDATE %s SET %s = %s WHERE device_ID = %s'\
                %(location, data_type, data, ID)
        cur.execute(SQL)
        con.commit()
        con.close()
        return True
    
    except:
        print('Can\'t update data')
        return False

# CreateDeviceList()
# CreateDevice(ID)
# SelectDevice('S-02-1156')
# CreateSensorLocation('kitchen')
# AddDataType('kitchen', 'something')
# InsertSensorLocation('S-03-17', 'kitchen')
# UpdateSensorData('S-03-17', 'kitchen', '86')
# DeleteSensorLocation('kitchen')
