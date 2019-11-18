# ESP_easyMQTT
a easy to use script for ESP8266 to work as a MQTT Client

## Use this script to easily build up a smart system with MQTT
You don't need to understand or write any code, all the things to to is download all dependencies and upload this script to the ESP8266

## How to use
1. When at the first started, it will act as a WiFi AP, connect to the WiFi with SSID = ESP8266, psw = 123456.  A UDP server with port 8888 will automatically begin, you need to send WiFi ssid and paw throuth the UDP channel
they will be stored in the on-board memory
2. The ESP board should have a reboot, and try to connect to the WiFi provided
3. Once online, it listens to port 1883, a MQTT broker is then needed for commands publishment. Use any device you want to as the broker

## Use the following commands to control the ESP
  1. to set one pin to input/output   
  SetPinMode:Pin_number INPUT/OUTPUT
  2. to make one pin to output HIGH or LOW signal   
  PinOutput: Pin_number HIGH/LOW
  3. to PWM a pin, x is the PWM percentage and 0<x<100
  PinOutput: Pin_number PWM x
  4. to subscript a topic
  AddTopic:o topic: topic_name
  5. to subscript a topic
  RemoveTopic: topic_name

the serial port is at 115200 bps, it always output useful informations when states changes
