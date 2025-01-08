#include <Wire.h>
#include <WiFi.h>
#include <NewPing.h>
#include <WiFiUdp.h>
#include <SparkFunBME280.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
//#include <Time.h>
//#include <TimeLib.h>
#include <NTPClient.h>
#define SOUND_SPEED 0.034
#define MAX_DISTANCE 200

// se definen los pines para el sensor 1 
#define TRIGGER_sensor_1  5
#define ECHO_sensor_1     18

// se definen los pines para el sensor 2 
#define TRIGGER_sensor_2  16
#define ECHO_sensor_2     17

const char* ssid = "DIGIFIBRA-hPb3";
const char* password =  "";
long tiempo1, tiempo2;
float distancia1, distancia2, humedad, temperatura;
// Configura el servidor NTP
const char* ntpServer = "pool.ntp.org";  // Servidor NTP
const long  utcOffsetInSeconds = 3600;   // Hora estándar de España (UTC+1)

NewPing sensor_1(TRIGGER_sensor_1, ECHO_sensor_1, MAX_DISTANCE);
NewPing sensor_2(TRIGGER_sensor_2, ECHO_sensor_2, MAX_DISTANCE);

// Crear objetos
BME280 bme; // Instancia del sensor BME280
Servo myServo;
WiFiClient wifi;
WiFiUDP udp;  // Crear objeto UDP para la comunicación NTP
NTPClient timeClient(udp, ntpServer, utcOffsetInSeconds);  // Crear cliente NTP

// Variables
float distanciaMinCont = 28;
float distanciaMin = 5;
int contd =0;

int targetHour = 12;
int targetMinute = 03;



void setup()
{
  Serial.begin(230400);

  // Wifi Setup
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
    Serial.write(12);
  }
  Serial.println("Connected to the WiFi network");
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address set: ");
  Serial.println(WiFi.localIP()); //print LAN IP
  
    myServo.attach(23,500,2500); // Pin donde está conectado el ServoRecpmotor
  // Iniciar el cliente NTP
    timeClient.begin();
    timeClient.update();  // Actualizar la hora desde el servidor NTP

    // Inicializar el BME280
    Wire.begin();
  if (bme.beginI2C() == false) //Begin communication over I2C
  {
    Serial.println("El sensor No RESPONDE, por favor verificar la conexión.");
    while(1); //Bucle Infinito
  }
    Serial.println("BME280 encontrado.");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Actualizar la hora
    timeClient.update();
     int currentHour = timeClient.getHours();
    int currentMinute = timeClient.getMinutes();
    // Leer temperatura
    temperatura = bme.readTempC();
    distancia1 = sensor_1.ping_cm();
    delay(1000);
    distancia2 = sensor_2.ping_cm();
  //  delay(2000);
    humedad = bme.readFloatHumidity();
    
      // Controlar el ServoRecpmotor!

    if (currentHour == targetHour && currentMinute == targetMinute) {
     
          if(distancia2 >= distanciaMin){
             myServo.write(180);  // Mover el ServoRecp a 180 ggrados  configurar para servir recipiente
             delay(1000);
              }
             else{
              contd = contd+1;
              myServo.write(0);  // Mover el ServoRecp a 0 ggrados  configurar para cerrar
              delay(30000);
              }
        if(contd >=2){
      //    targetMinute =targetMinute+2;
           contd=0;
          }
    }
    else{
        myServo.write(0);  // Mover el ServoRecp a 0 ggrados  configurar para cerrar
        }
    
    Serial.print("Temperatura: ");
    Serial.print(temperatura);
    Serial.print(" °C, Distancia Cont: ");
    Serial.print(sensor_1.ping_cm());
    Serial.println(" cm, Distancia Recip: ");
    Serial.print(sensor_2.ping_cm());
    Serial.println(" cm");
  

    
    StaticJsonDocument<200> doc;
    doc["sensor_id"] = "s1";
    doc["temperatura"] = temperatura;
    doc["humedad"] = humedad;
    doc["distancia1"] = distancia1;
    doc["distancia2"] = distancia2;
    doc["contador"] = contd;

    String json_string;
  
    serializeJson(doc, json_string);

    Serial.print(json_string);

    HTTPClient http;
  
    http.begin("http://192.168.1.135:5000/sensor_values"); 
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(json_string);
    
  if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error on sending POST Request: ");
      Serial.println(httpResponseCode);
    }
    
  http.end();
  
  } else {
    Serial.println("Error in WiFi connection");
  }
    
    delay(1000); // Esperar un segundo antes de la siguiente lectura
}
