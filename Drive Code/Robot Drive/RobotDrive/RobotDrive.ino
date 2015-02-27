#define motors 6
#define sensors 6
#define delayCounter 5

// Motor ports (D for direction and P for power)
// Motor keys (first compare 1 then 2)
int motorPortsD[motors] = {
    0, 1, 2, 3, 4, 5
};
int motorPortsP[motors] = {
    6, 7, 8, 9, 10, 11
};
int motorPower[motors] = {
    0, 0, 0, 0, 0
}; // from -256 to 256 (- being backward)
int currentPower = 0;
int changeRate = 8;
int keyIn1 = 17; // 1st key for reading motor data
int keyIn2 = 151; // 2nd key for reading motor data

// Sensor ports and every sensor iteration to send
// sensor value
// Sensor key values to be sent
int sensorIteration = 1;
int sensorPorts[sensors] = {
    0, 1, 2, 3, 4, 5
};
int keyOut1 = 74; // 1st key for sending sensor data
int keyOut2 = 225; // 2nd key for sending sensor data

// Counter for sensor iteration
int counter = 0;

// Initialize serial and output ports
void setup() {
    Serial.begin(9600);
    for (int i = 0; i < motors; i++) {
        pinMode(motorPortsD[i], OUTPUT);
        pinMode(motorPortsP[i], OUTPUT);
    }
}

void loop() {
    // read and turn motors from Serial port
    while (Serial.available() >= 5) {
        if (Serial.read() == keyIn1 && Serial.read() == keyIn2) {
            int motorNum = Serial.read();
            int motorP = Serial.read();
            int motorD = Serial.read();
            if (motorD > 0 && motorD < 3) {
                // stores the read motorP and motorD as the targetted
                // motor power (btw -256 and 256)
                if (motorD == 1) {
                    motorPower[motorNum] = -1 * motorP;
                } else if (motorD == 2) {
                    motorPower[motorNum] = motorP;
                }
            }
        }
    }
    for (int i = 0; i < motors; i++) {
        // updates motor power to be midpoint btw current power and 
        // targeted power
        currentPower += (motorPower[i] - currentPower) / changeRate;
        // convert back to motor readable output
        int motorD = 1;
        int motorP = currentPower;
        if (currentPower < 0) {
            motorD = 0;
            motorP = -1 * currentPower;
        }
        analogWrite(motorPortsP[i], motorP);
        digitalWrite(motorPortsD[i], motorD);
    } 
    counter++;
    // every sensorIteration iteration, reads and sends sensor
    // reading
    if (counter == sensorIteration) {
        counter = 0;
        for (int i = 0; i < sensors; i++) {
            int sensorValue = analogRead(sensorPorts[i]);
            Serial.write(keyOut1);
            Serial.write(keyOut2);
            Serial.write(i);
            Serial.write(sensorValue);
        }
    }
    delay(delayCounter);
}
