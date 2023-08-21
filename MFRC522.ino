/*
 * ----------------------------------------------------------------------------
 * This is a MFRC522 library example; see https://github.com/miguelbalboa/rfid
 * for further details and other examples.
 * 
 * NOTE: The library file MFRC522.h has a lot of useful info. Please read it.
 * 
 * Released into the public domain.
 * ----------------------------------------------------------------------------
 * Example sketch/program which will try the most used default keys listed in 
 * https://code.google.com/p/mfcuk/wiki/MifareClassicDefaultKeys to dump the
 * block 0 of a MIFARE RFID card using a RFID-RC522 reader.
 * 
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 *
 */
#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         9           // Configurable, see typical pin layout above
#define SS_PIN          10          // Configurable, see typical pin layout above
#define buzzer          6

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

unsigned long mfrc522Timeout;
boolean buzzerflag;

void setup(){
  Serial.begin(9600); 
  pinMode(buzzer,OUTPUT);
while (!Serial);            // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
    SPI.begin();                // Init SPI bus
    mfrc522.PCD_Init();         // Init MFRC522 card
}


void loop(){

if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial() && millis() - mfrc522Timeout >= 1300){
  mfrc522Timeout = millis();
  buzzerflag = true;
  analogWrite (buzzer, 80);
  for (uint8_t i=0; i<mfrc522.uid.size; i++){
    Serial.print(mfrc522.uid.uidByte[i], HEX);
    Serial.print(" ");
  }
   Serial.println("");
}
  if(buzzerflag &&  millis() - mfrc522Timeout >= 200){
  mfrc522Timeout = millis();
  analogWrite (buzzer, 0);
  buzzerflag = false;
  }
 
}
