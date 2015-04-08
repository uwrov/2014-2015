#define DELAY_COUNTER 5

int pneumaticsPort = 1;
const int KEYPNEUMATICS = 100;

// Special LED packets
const int KEYLIGHT = 101;
const int LEDPIN = 13;
int ledState = LOW;

// Special Ping packets
const int KEYPING = 102;

// Motor ports (D for direction and P for power)
// Motor keys (first compare 1 then 2)
#define MOTORS 6
const int motorPortsD[MOTORS] = {
    1, 2, 3, 4, 5, 6
};
const int motorPortsP[MOTORS] = {
    7, 8, 9, 10, 11, 12
};
int motorPower[MOTORS] = {
    0, 0, 0, 0, 0
};

// from -256 to 256 (- being backward)
int currentPower = 0;
int changeRate = 8;

// 1st key for reading motor data
int keyIn1 = 17;
// 2nd key for reading motor data
int keyIn2 = 151;

// Sensor ports and every sensor iteration to send
// sensor value
// Sensor key values to be sent
#define SENSORS 6
int sensorIteration = 100000000;
const int sensorPorts[SENSORS] = {
    0, 1, 2, 3, 4, 5
};

int keyOut1 = 74;
// 1st key for sending sensor data
int keyOut2 = 225;
// 2nd key for sending sensor data

// Counter for sensor iteration
int counter = 0;
// Initialize serial and output ports

void setup() {
    Serial.begin(9600);
    for (int i = 0; i < MOTORS; i++) {
        pinMode(motorPortsD[i], OUTPUT);
        pinMode(motorPortsP[i], OUTPUT);
    }
    pinMode(pneumaticsPort, OUTPUT);
    pinMode(LEDPIN, OUTPUT);
}

void loop() {
    // read and turn MOTORS from Serial port
    while (Serial.available() >= 5) {
        readSerial();
    }
    motorControl();
    sendSensorData();
}

void readSerial() {
    if (Serial.read() == keyIn1 && Serial.read() == keyIn2) {
        int specialKey = Serial.read();
        if (specialKey == KEYPING) {
            Serial.write(keyOut1);
            Serial.write(keyOut2);
            Serial.write(KEYPING);
            Serial.write(Serial.read());
            Serial.read();
        }
        else if (specialKey == KEYLIGHT) {
            // if the LED is off turn it on and vice-versa:
            ledState = !ledState;
            // set the LED with the ledState of the variable:
            digitalWrite(LEDPIN, ledState);
        } else if (specialKey == KEYPNUEUMATICS) {
            // if the Pneumatics claw is off turn it on and vice-versa:
            ledState = !ledState;
            // set the Pneumatics claw with the ledState of the variable:
            digitalWrite(pneumaticsPort, ledState);
        }
        else {
            readMotorValues();
        }
    }
}

void sendSensorData() {
    counter++;
    // every sensorIteration iteration, reads and sends sensor
    // reading
    if (counter == sensorIteration) {
        counter = 0;
        for (int i = 0; i < SENSORS; i++) {
            int sensorValue = analogRead(sensorPorts[i]);
            Serial.write(keyOut1);
            Serial.write(keyOut2);
            Serial.write(i);
            Serial.write(sensorValue);
        }
    }
    delay(DELAY_COUNTER);
}

void readMotorValues() {
    int motorNum = Serial.read();
    int motorP = Serial.read();
    int motorD = Serial.read();
    if (motorD > 0 && motorD < 3) {
        // stores the read motorP and motorD as the targetted
        // motor power (btw -256 and 256)
        if (motorD == 1) {
            motorPower[motorNum] = -1 * motorP;
        }
        else if (motorD == 2) {
            motorPower[motorNum] = motorP;
        }
    }
}

void motorControl() {
    for (int i = 0; i < MOTORS; i++) {
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
}


