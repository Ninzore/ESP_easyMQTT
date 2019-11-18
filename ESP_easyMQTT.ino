#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Thread.h>
#include <ThreadController.h>
#include <FS.h>
#include <WiFiUdp.h>
#include <ESP_common.h>

//Wifi ssid and password
char* ssid;
char* password;

//MQTT server info
const char* MQTT_Server;
const int MQTT_Port = 1883;

// get the device mac address
String mac = WiFi.macAddress();

//create instance
WiFiClient espClient;
PubSubClient client(espClient);
FileSys FileSys;
WiFiUDP Udp;

//create multithreads
Thread Thread_1 = Thread();
Thread Thread_2 = Thread();
Thread Thread_3 = Thread();
ThreadController ticker = ThreadController();

String Topics;
String sensor_pin;
int wifi_retry = 0;
int mqtt_retry = 0;

void SetupWifi()
{
  String ssid_buffer = FileSys.getSSID();
  ssid_buffer.toCharArray(ssid, ssid_buffer.length());
  String password_buffer = FileSys.getPassword();
  password_buffer.toCharArray(password, password_buffer.length());
  
  if (ssid_buffer.length() == 0)
  {
    UdpServer();
  }
  else
  {
    Serial.print("Connecting to ");
    Serial.println(ssid_buffer);
  
    WiFi.begin(ssid, password);
  
    if (WiFi.status() != WL_CONNECTED)
    {
      for (int WifiRetry= 0; WifiRetry <= 10; WifiRetry++)
      {
        delay(500);
        Serial.print(".");
        if (WiFi.status() == WL_CONNECTED)
        {
          Serial.println("");
          Serial.println("WiFi connected");
          Serial.println("IP address: ");
          Serial.println(WiFi.localIP());
          Serial.println(WiFi.macAddress());
          break;
        }
      }
    }
    else
    {
      Serial.println("WiFi connection failed, Start Retry process");
    }
  }
}

void UdpServer()
{
  Serial.println("Start AP configuration");

  const char* ap_ssid = "ESP8266";
  const char* ap_password = "12345678";

  WiFi.softAP(ap_ssid,ap_password);

  int udp_port = 8888;
  Udp.begin(udp_port);
  Serial.printf("Now listening at %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("UDP port is %d\n",udp_port);
}

void udpMessage()
{
  char udp_buffer[UDP_TX_PACKET_MAX_SIZE];
  String message;
  String ssid, password, server;

  Serial.print("Getting message from ");
  Serial.println(Udp.remoteIP().toString().c_str());
  Serial.print("Port ");
  Serial.println(Udp.remotePort());
  message = String(Udp.read(udp_buffer, UDP_TX_PACKET_MAX_SIZE));
  Serial.println(message);
  message.replace(" ", "");

  if (message.startsWith("SSID:"))
  {
    message.replace("SSID:", "");
    ssid = message;
    //Send the reply   
    Udp.beginPacket(Udp.remoteIP(),Udp.remotePort());  
    Udp.write("SSID received");  
    Udp.endPacket();  //end of packet
  }

  if (message.startsWith("password:"))
  {
    message.replace("Password:", "");
    password = message;
    Udp.beginPacket(Udp.remoteIP(),Udp.remotePort());  
    Udp.write("Password received");  
    Udp.endPacket();  //end of packet
  }

  if (message.startsWith("MQTTServer:"))
  {
    message.replace("MQTTServer:", "");
    server = message;
    Udp.beginPacket(Udp.remoteIP(),Udp.remotePort());  
    Udp.write("MQTT server address received");  
    Udp.endPacket();  //end of packet
  }

  if (message.startsWith("UpdateWifi"))
  {
    FileSys.UpdateWifi(ssid, password);
    WiFi.softAPdisconnect(true);
    wifi_retry = 0;
  }
  
  if (message.startsWith("UpdateMqttServer"))
  {
    FileSys.UpdateMqttServer(server);
    mqtt_retry = 0;
  }
}

void callback(char* topic, byte* payload, unsigned int length)
{
  Serial.println("Message arrived:");
  Serial.print("Topic:");
  Serial.println(topic);
  char message[length];
  for (int i=0;i<length;i++) 
  {
    message[i] = payload[i];
  }
  String content = String(message);
  content.remove(length);
  Serial.println(content);
  messageFilter(content);
}

void ConnectMQTT()
{
  String mqtt_buffer = FileSys.getMqttServer();
  MQTT_Server = mqtt_buffer.c_str();
  client.setServer(MQTT_Server, MQTT_Port);
  client.setCallback(callback);
  // Create a client ID
  String clientID = String(random(0xffff),HEX);
  // check connection
  if (client.connect(clientID.c_str()))
  {
    Serial.println("MQTT connected");
    publishRequest("default", "Request topic");
    client.subscribe("default");
    client.subscribe(mac.c_str());
  }
  else
  {
     Serial.println("\nMQTT connection failed");
  }
}

void ReconnectWifi()
{
  if (sizeof(ssid) == 0 || sizeof(password) == 0)
  {
  String ssid_buffer = FileSys.getSSID();
  ssid_buffer.toCharArray(ssid, ssid_buffer.length());
  String password_buffer = FileSys.getPassword();
  password_buffer.toCharArray(password, password_buffer.length());
  }

  WiFi.begin(ssid, password);
  Serial.println("Attempting WiFi reconnection");
  wifi_retry++;

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    ticker.remove(&Thread_2);
    wifi_retry = 0;
  }
}

void ReconnectMQTT()
{
  if (sizeof(MQTT_Server) == 0)
  {
    String mqtt_buffer = FileSys.getMqttServer();
    MQTT_Server = mqtt_buffer.c_str();
  }
  
  Serial.println("Attempting MQTT connection...");
  mqtt_retry++;
  if (client.connected()) 
  {
    Serial.println("MQTT server connected");
    ticker.remove(&Thread_3);
    ConnectMQTT();
  }
}

void publishRequest(String topic, String request)
{
  request = mac + " : " + request;
  client.publish(topic.c_str(), request.c_str());
}

void publishData()
{
  int cursor_start = 0; 
  int cursor_end = 0;
  String data;
  int pin;
  cursor_end = sensor_pin.indexOf(",");
  while (cursor_end != -1)
  {
    pin = sensor_pin.substring(cursor_start, cursor_end).toInt();
    cursor_start = cursor_end+1;
    cursor_end = Topics.indexOf(",",cursor_start);
      if (pin == 2)
      {
        data.concat(pin+":");
        data.concat(analogRead(2)+",");
      }
      else
      {
        data.concat(pin+":");
        data.concat(digitalRead(pin)+",");
      }
  }

  String topic;
  int len = Topics.length();
  cursor_end = Topics.indexOf(",");
  while (cursor_end != -1)
  {
    topic = Topics.substring(cursor_start, cursor_end);
    client.publish(topic.c_str(), data.c_str());
    cursor_start = cursor_end+1;
    cursor_end = Topics.indexOf(",",cursor_start);
  }
  topic = Topics.substring(cursor_start, len);
  Serial.print("Publish data to topic: ");
  Serial.println(topic);
  client.publish(topic.c_str(), data.c_str());
}

void messageFilter(String content)
{
  content.replace(" ", "");
  int cursor_start = 0; 
  int cursor_end;

  if (content.startsWith("SetPinMode:"))
  {
    content.replace("SetPinMode:" , "");
    cursor_end = content.indexOf(",");
    int pin = content.substring(0, cursor_end).toInt();
    
    if (content.endsWith("OUTPUT"))
    {
      pinMode(pin, OUTPUT);
      Serial.print(pin);
      Serial.println(" is now output");
    }

    if (content.endsWith("INPUT"))
    {
      pinMode(pin, INPUT);
      sensor_pin.concat(pin + ",");
      Serial.print(pin);
      Serial.println(" is now input");
    }
  }

  if (content.startsWith("PinOutput:"))
  {
    content.replace("PinOutput:" , "");
    cursor_end = content.indexOf(",");
    int pin = content.substring(0, cursor_end).toInt();
    
    if (content.endsWith("HIGH"))
    {
      digitalWrite(pin, HIGH);
      Serial.print(pin);
      Serial.println(" is HIGH");
    }

    if (content.endsWith("LOW"))
    {
      pinMode(pin, LOW);
      Serial.print(pin);
      Serial.println(" is LOW");
    }

    else 
    {
      content.replace(content.substring(0, cursor_end) + ",", "");
      if (content.startsWith("PWM"))
      {
        content.replace("PWM" , "");
        analogWrite(pin, content.toInt());
        Serial.print(pin);
        Serial.print(" is PWM to ");
        Serial.println(content);
      }
    }
  }

  if (content.startsWith("RemoveTopic:"))
  {
    String topic;
    content.replace("RemoveTopic:" , "");
    int len = content.length();
    cursor_end = content.indexOf(",");

    while (cursor_end != -1)
    {
      topic = content.substring(cursor_start, cursor_end);
      Serial.print("Unsubscribe topic: ");
      Serial.println(topic);
      client.unsubscribe(topic.c_str());
      cursor_start = cursor_end+1;
      cursor_end = content.indexOf(",",cursor_start);
      
      if (Topics.endsWith(topic))
      {
        Topics.replace(","+topic,"");
      }
      else
      {
        Topics.replace(topic+",","");
      }
    }
    topic = content.substring(cursor_start, len);
    client.unsubscribe(topic.c_str());
    Serial.print("Unsubscribe topic: ");
    Serial.println(topic);
  }
  
  if (content.startsWith("AddTopic:"))
  {
    String topic;
    content.replace("AddTopic:" , "");
    int len = content.length();
    cursor_end = content.indexOf(",");

    if (Topics.length() == 0)
    {
      Topics.concat(topic);
    }

    if (Topics.length() != 0)
    {
      Topics.concat(",");
      Topics.concat(topic);
    }

    while (cursor_end != -1)
    {
      topic = content.substring(cursor_start, cursor_end);
      Serial.print("Subscribe to topic: ");
      Serial.println(topic);
      client.subscribe(topic.c_str());
      cursor_start = cursor_end+1;
      cursor_end = content.indexOf(",",cursor_start);
     }
    topic = content.substring(cursor_start, len);
    client.subscribe(topic.c_str());
    Serial.print("Subscribe to topic: ");
    Serial.println(topic);
  }
}

void setup()
{
  Serial.begin(115200);
  SPIFFS.begin();
  SetupWifi();
  ConnectMQTT();
  client.setCallback(callback);

  Thread_1.onRun(publishData);
  Thread_1.setInterval(500);

  Thread_2.onRun(ReconnectWifi);
  Thread_2.setInterval(500);

  Thread_3.onRun(ReconnectMQTT);
  Thread_3.setInterval(500);
}

void loop() 
{
  if (WiFi.status() != WL_CONNECTED)
  {
    if (wifi_retry = 0)
    {
      ticker.add(&Thread_2);       
    }
    if (wifi_retry > 10)
   {
      Serial.println("Can't connect to the WiFi, Please check WiFi setup");
      ticker.remove(&Thread_2);
      UdpServer();
    }
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    if (!client.connected())
    {
      if (mqtt_retry == 0)
      {
        ticker.add(&Thread_3);
      }
      
      if (mqtt_retry > 10)
      {
        Serial.print("MQTT connection failed, Current State = ");
        Serial.println(client.state());
        Serial.println("Please check MQTT setup");        
        ticker.remove(&Thread_3);
        UdpServer();
      }
    }
  }

  if (WiFi.status() == WL_CONNECTED && client.connected())
  {
    client.loop();
    if (Topics.length() != 0 && sensor_pin.length() != 0)
    {
      ticker.add(&Thread_1);
    }
  }

  ticker.run();

  if (Udp.parsePacket())
  {
    udpMessage();
  }
}
