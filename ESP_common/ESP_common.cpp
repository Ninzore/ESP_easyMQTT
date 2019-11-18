#include <FS.h>
#include <ESP8266WiFi.h>
#include <ESP_common.h>

//class FileSys begin

void FileSys::ReadFile(String file) {
  File Doc = SPIFFS.open(file, "r");
 
  while(Doc.peek() != -1) {
    String text = Doc.readStringUntil('\n');
    Serial.println(text);
  }
}

//Read the Wifi SSID and password from Wifi.txt
//Wifi.txt is in the format below
//SSID = UserSSID
//password = UserPassword

String FileSys::getSSID() {
  //open the /Wifi.txt file to get the ssid and password
  File WifiInfo = SPIFFS.open("/WifiInfo.txt", "r");

  //get the SSID
  WifiInfo.seek(7,SeekSet); //move the cursor to the UserSSID
  String ssid = WifiInfo.readStringUntil('\n');
  Serial.print("SSID = ");
  Serial.println(ssid);
  
  WifiInfo.close();
  return ssid;
}

String FileSys::getPassword() {
  //get the password
  File WifiInfo = SPIFFS.open("/WifiInfo.txt", "r");
  WifiInfo.readStringUntil('\n');
  WifiInfo.seek(11,SeekCur); //move the cursor to the UserPassword
  String password = WifiInfo.readStringUntil('\n');
  Serial.print("password = ");
  Serial.println(password);

  WifiInfo.close();
  return password;
}

void FileSys::UpdateWifi(String ssid, String password) {
  //Store the Wifi SSID and password in WifiInfo.txt

    //creat new or clear all text in Wifi.txt
    File Wifi_txt = SPIFFS.open("/WifiInfo.txt", "w");
    //Write the SSID and password in default format
    Wifi_txt.print("SSID = ");
    Wifi_txt.println(ssid);
    Wifi_txt.print("Password = ");
    Wifi_txt.print(password);
    Wifi_txt.close();
}

String FileSys::getMqttServer() {
  //get MQTT Server address
  File MqttInfo = SPIFFS.open("/MqttInfo.txt", "r");
  String mqtt_server = MqttInfo.readStringUntil('\n');
  Serial.print("MQTT Server = ");
  Serial.println(mqtt_server);

  MqttInfo.close();
  return mqtt_server;
}

void FileSys::UpdateMqttServer(String mqtt_server) {
  File MqttInfo = SPIFFS.open("/MqttInfo.txt", "w");
  MqttInfo.print(mqtt_server);
  MqttInfo.close();
}