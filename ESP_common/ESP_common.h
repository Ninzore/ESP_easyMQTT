#ifndef EspCommon_h
#define EspCommon_h

 //access the ESP8266 file system
class FileSys {
  public:
    void ReadFile(String file);
    String getSSID();
    void UpdateWifi(String ssid, String password); //Store the Wifi SSID and password
    String getPassword();
    String getMqttServer();
    void UpdateMqttServer(String mqtt_server);
};

#endif