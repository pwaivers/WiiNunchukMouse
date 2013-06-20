/*
 * WiiChuckDemo -- 
 *
 * 2008 Tod E. Kurt, http://thingm.com/
 *
 */

#include <Wire.h>
#include "nunchuck_funcs.h"

int loop_cnt=0;

byte joyx,joyy,accx,accy,accz,zbut,cbut;
int ledPin = 13;


void setup()
{
    Serial.begin(19200);
    
    Serial.print("Initializing WiiNunchuk connection...\n");
    nunchuck_setpowerpins();
    nunchuck_init(); // send the initilization handshake
    
    
    Serial.print("WiiChuckDemo ready!\n");
}

void loop()
{
    if( loop_cnt > 10 ) { // every 100 msecs get new data
        loop_cnt = 0;

        nunchuck_get_data();

        joyx = nunchuck_joyx(); // ranges from approx 23 - 222
        joyy = nunchuck_joyy(); // ranges from approx 31 - 223
        accx  = nunchuck_accelx(); // ranges from approx 70 - 182
        accy  = nunchuck_accely(); // ranges from approx 65 - 173
        accz  = nunchuck_accelz(); // ranges unknown
        zbut = nunchuck_zbutton();
        cbut = nunchuck_cbutton(); 
            
          Serial.print(""); Serial.print((byte)joyx,DEC);
          Serial.print(" "); Serial.print((byte)joyy,DEC);
          Serial.print(" "); Serial.print((byte)accx,DEC);
          Serial.print(" "); Serial.print((byte)accy,DEC);
          Serial.print(" "); Serial.print((byte)accz,DEC);
          Serial.print(" "); Serial.print((byte)zbut,DEC);
          Serial.print(" "); Serial.println((byte)cbut,DEC);
    }
    loop_cnt++;
    delay(1);
}

