import paho.mqtt.client as client
import paho.mqtt.publish as publish
import re
import threading
from collections import namedtuple
import Database_MK4 as database

server_address = 'localhost'
port = 1883

def on_connect(client, userdata, flags, rc):
    '''callback when connected'''
    print("Connected with broker")
    client.subscribe("#")
    client.publish("default", payload='logger is Ready')

def on_message(client, userdata, message):
    '''callback when receive message'''
    content = str(message.payload)
    print(content)

def messageFilter(content):
    content.strip()
    mac = re.match(r'\w+:\w+:\w+:\w+:\w+:\w+', content)

    if mac:
        print (mac)
        print (content)
        device_ID = mac
        content = content.split(":")[6].strip()
        
        if re.match("Data", content):
            data_string = content.split(":")[7].strip()
            location = content.topic     
            data_string = re.finditer(r'\d+:\d+', data_string)

            for pair in data_string:
                pin = pair.group().split(":")[0]
                data = pair.group().split(":")[1]

                database.UpdateSensorData(device_ID, location, pin, data)
       
        if re.match("Request setup", content):
            device_topics = database.CheckTopic(device_ID)
            device_output = database.CheckOutput(device_ID)
            device_sensor = database.CheckSensor(device_ID)
            publish.single(device_ID, payload='Add Topic:' + device_topics)
            publish.single(device_ID, payload='Set Pin Mode:' + device_output + ",OUTPUT")
            publish.single(device_ID, payload='Set Pin Mode:' + device_sensor + ",INPUT")
            
task_num = 0
def ReadTask():
    global task_num
    with open('C:/Users/Cille/Desktop/Tasks.txt', 'r') as task_file:
        for line in task_file.readlines():
            trigger = line.split('=')[0]
            action = line.split('=')[1]
            trigger_plus = []
            trigger_minus = []
            action_plus = []
            action_minus = []
            timing_plus = []
            timing_minus = []

            def SetTrigger(triggers):
                # supported format
                # case_1: location.temperature>20
                # case_2: location.door(open)
                # case_3: time.day_of_week (monday,tuesday,wednesday, etc...)
                # case_4: time.23:34 (24 hour clock)
                # case_5: time.4-11 (month-day)
                # case_6: time.start(10:40) (start at hour-minute, 24 hour clock)
                # case_7: time.start(Monday) (start at day of week)
                # case_8: time.start(10-20) (start at month-day)
                # case_9: time.end(12:45) (end at hour-minute, 24 hour clock)
                # case_10: time.end(Tuesday) (end at day of week)
                # case_11: time.end(5-6) (end at month-day )
                # case_12: time.every.10.seconds/minutes/hours/days/weeks (can be any nature number)
                # case_13: time.random 

                case_1 = re.findall(r"\+?\-?\s*\w+\.\w+[\>|\<]\d+", trigger)
                if len(case_1) > 0:
                    for i in range(len(case_1)):            
                        condition = re.search(r"(\w+)\.(\w+)([\>|\<])(\d+)", case_1[i])
                        condition_list = ["case_1", condition.group(1), condition.group(2), condition.group(3), condition.group(4)]
                        if re.match(r"[^\-]", case_1[i]):
                            trigger_plus.append(condition_list)   
                        if re.search(r"\-", case_1[i]):
                            trigger_minus.append(condition_list)          

                # case_2: location.door(open)
                case_2 = re.findall(r"\+?\-?\s*\w+\.\w+\(\w+\)\s*", trigger)
                if len(case_2) > 0:
                    for i in range(len(case_2)):
                        condition = re.search(r"(\w+)\.(\w+)\((\w+)\)", case_2[i])
                        condition_list = ["case_2", condition.group(1), condition.group(2), condition.group(3)]
                        if re.match(r"[^\-]", case_2[i]):
                            trigger_plus.append(condition_list)
                        if re.match(r"\-", case_2[i]):
                            trigger_minus.append(condition_list)

                # case_3: time.day_of_week (monday,tue,wed, etc...)
                case_3 = re.findall(r"""\+?\-?\s*time\.
                                    (Mon(day?)?|Tue(sday?)?|Wed(nesday?)?|Thu(rsday?)?|Fri(day?)?|Sat(urday?)?|Sun(day?)?)""",
                                    trigger, flags = re.IGNORECASE)
                if len(case_3) > 0:
                    for i in range(len(case_3)):
                        condition = re.search(r"""time\.
                                            (Mon(day?)?|Tue(sday?)?|Wed(nesday?)?|Thu(rsday?)?|Fri(day?)?|Sat(urday?)?|Sun(day?)?)""",
                                            case_3[i], flags = re.IGNORECASE)
                        condition_list = ["case_3", condition.group(1)]                   
                        if re.match(r"[^\-]", case_3[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_3[i]):
                            timing_minus.append(condition_list)
                
                # case_4: time.23:34 (24 hour clock)
                case_4 = re.findall(r"\+?\-?\s*time\.\d{1,2}:\d{1,2}", trigger, flags = re.IGNORECASE)
                if len(case_4) > 0:
                    for i in range(len(case_4)):
                        condition = re.search(r"time\.(\d{1,2}):(\d{1,2})", case_4[i], flags = re.IGNORECASE)
                        condition_list = ["case_4", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_4[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_4[i]):
                            timing_minus.append(condition_list)

                # case_5: time.4-11 (month-day)
                case_5 = re.findall(r"\+?\-?\s*time.\d{1,2}-\d{1,2}", trigger, flags = re.IGNORECASE)
                if len(case_5) > 0:
                    for i in range(len(case_5)):
                        condition = re.search(r"time.(\d{1,2})-(\d{1,2})", case_5[i], flags = re.IGNORECASE)
                        condition_list = ["case_5", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_5[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_5[i]):
                            timing_minus.append(condition_list)

                # case_6: time.start(10:40) (start at hour-minute, 24 hour clock)
                case_6 = re.findall(r"\+?\-?\s*time.start\(\d{1,2}:\d{1,2}\)", trigger, flags = re.IGNORECASE)
                if len(case_6) > 0:
                    for i in range(len(case_6)):
                        condition = re.search(r"time.start\((\d{1,2}):(\d{1,2})\)", case_6[i], flags = re.IGNORECASE)
                        condition_list = ["case_6", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_6[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_6[i]):
                            timing_minus.append(condition_list)
                
                # case_7: time.start(Monday) (start at day of week)
                case_7 = re.findall(r"\+?\-?\s*time\.start\(\w+\)",trigger, flags = re.IGNORECASE)
                if len(case_7) > 0:
                    for i in range(len(case_7)):
                        condition = re.search(r"time\.start\(Mon(day?)|Tue(sday?)|Wed(nesday?)|Thu(rsday?)|Fri(day?)|Sat(urday?)|Sun(day?)\)",
                                                case_7[i], flags = re.IGNORECASE)
                        condition_list = ["case_7", condition.group(1)]              
                        if re.match(r"[^\-]", case_7[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_6[i]):
                            timing_minus.append(condition_list)
                
                # case_8: time.start(10-20) (start at month-day)
                case_8 = re.findall(r"\+?\-?\s*time.start\(\d{1,2}-\d{1,2}\)", trigger, flags = re.IGNORECASE)
                if len(case_8) > 0:
                    for i in range(len(case_8)):
                        condition = re.search(r"time.start\((\d{1,2})-(\d{1,2})\)", case_8[i], flags = re.IGNORECASE)
                        condition_list = ["case_8", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_8[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_8[i]):
                            timing_minus.append(condition_list)
                
                # case_9: time_end(12:45) (end at hour-minute, 24 hour clock)
                case_9 = re.findall(r"\+?\-?\s*time.end\(\d{1,2}:\d{1,2}\)", trigger, flags = re.IGNORECASE)
                if len(case_9) > 0:
                    for i in range(len(case_9)):
                        condition = re.search(r"time.end\((\d{1,2}):(\d{1,2})\)", case_9[i], flags = re.IGNORECASE)
                        condition_list = ["case_9", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_9[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_9[i]):
                            timing_minus.append(condition_list)
                
                # case_10: time_end(Tuesday) (end at day of week)
                case_10 = re.findall(r"""\+?\-?\s*time\.end\(\w+\)""",
                                    trigger, flags = re.IGNORECASE)
                if len(case_10) > 0:
                    for i in range(len(case_10)):
                        condition = re.search(r"""\+?\-?\s*time\.end\((Mon(day?)|Tue(sday?)|Wed(nesday?)|Thu(rsday?)|Fri(day?)|Sat(urday?)|Sun(day?))\)""",
                                            case_10[i], flags = re.IGNORECASE)
                        condition_list = ["case_10", condition.group(1)]              
                        if re.match(r"[^\-]", case_10[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_10[i]):
                            timing_minus.append(condition_list)
                
                # case_11: time.end(5-6) (end at month-day )
                case_11 = re.findall(r"\+?\-?\s*time.end\(\d{1,2}-\d{1,2}\)", trigger, flags = re.IGNORECASE)
                if len(case_11) > 0:
                    for i in range(len(case_11)):
                        condition = re.search(r"time.end\((\d{1,2})-(\d{1,2})\)", case_11[i], flags = re.IGNORECASE)
                        condition_list = ["case_11", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_11[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_11[i]):
                            timing_minus.append(condition_list)
                
                # case_12: time.every.10.seconds/minutes/hours/days/weeks (can be any nature number)
                case_12 = re.findall(r"\+?\-?\s*time.every.\d+.seconds|minutes|hours|days|weeks",trigger, flags = re.IGNORECASE)
                if len(case_12) > 0:
                    for i in range(len(case_12)):
                        condition = re.search(r"time.every.(\d+).(seconds|minutes|hours|days|weeks)", case_12[i], flags = re.IGNORECASE)
                        condition_list = ["case_12", condition.group(1), condition.group(2)]              
                        if re.match(r"[^\-]", case_12[i]):
                            timing_plus.append(condition_list)
                        if re.match(r"\-", case_12[i]):
                            timing_minus.append(condition_list)

                # case_13: random
                case_13 = re.findall(r"time\.random", trigger, flags = re.IGNORECASE)
                if len(case_13) > 0:
                    condition_list = ["case_13", "random"]
                    timing_plus.append(condition_list)
                
     
            def SetAction(action):
                case_1 = re.findall(r"\+?\-?\s*\w+\.\w+\(\w+\)", action)
                if len(case_1) > 0:
                    for i in range(len(case_1)):
                        condition = re.search(r"(\w+)\.(\w+)\((\w+)\)", case_1[i])
                        condition_list = [condition.group(1), condition.group(2), condition.group(3)]
                        if re.match(r"[^\-]", case_1[i]):
                            action_plus.append(condition_list)
                        if re.match(r"\-", case_1[i]):
                            action_minus.append(condition_list)
            
            SetTrigger(trigger)
            SetAction(action)
            
            if (len(trigger_plus) > 0) or (len(timing_plus) > 0):
                 task_num += 1
            
            else:
                print("task syntax is not supported")
            
            task_ID = "task_" + str(task_num)
            
            globals()[task_ID] = type("trigger", (object,),
                                dict(trigger_plus = trigger_plus,
                                    trigger_minus = trigger_minus,
                                    action_plus = action_plus,
                                    action_minus = action_minus,
                                    timing_plus = timing_plus,
                                    timing_minus = timing_minus))

ReadTask()


for i in range(task_num):
    task_ID = "trigger_" + str(i+1)
    print(task_ID)
    print("trigger_plus:")
    print(globals()[task_ID].trigger_plus)
    print("trigger_minus:")
    print(globals()[task_ID].trigger_minus)
    print("action_plus:")
    print(globals()[task_ID].action_plus)
    print("action_minus:")
    print(globals()[task_ID].action_minus)