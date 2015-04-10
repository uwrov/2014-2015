// Motor layout, top view. Motors 1 and 2 point towards the back. Motors 3 and 4
// point towards the front. Motors 5 and 6 point up.
// 
//      Front
//  1           2
//   /---------\
//  /|         |\
//   |    5    |
//   |         |
//   |         |
//   |         |
//   |    6    |
//  \|         |/
//   \---------/
//  4           3

const int NUM_MOTORS = 6;
const int NUM_SENSORS = 6;

const int DELAY_COUNTER = 5; // delay each loop (ms)


// motor constants
const int MOTOR_FT_LT = 0;
const int MOTOR_FT_RT = 1;
const int MOTOR_BK_RT = 2;
const int MOTOR_BK_LT = 3;
const int MOTOR_FT_UP = 4;
const int MOTOR_BK_DN = 5;


// direction constants
const int READ_BACKWARD = 2;
const int READ_FORWARD = 3;

const int BACKWARD = 0;
const int FORWARD = 1;



// *** PACKET HEADERS ***

// headers for incoming data
const int HEADER_KEY_IN_1 = 17;
const int HEADER_KEY_IN_2 = 151;


// headers for outgoing data
const int HEADER_KEY_OUT_1 = 74;
const int HEADER_KEY_OUT_2 = 225;


const int HEADER_KEY_PNEUMATICS = 100; // toggle pneumatic state
const int HEADER_KEY_LIGHT = 101; // switching LED state
const int HEADER_KEY_PING = 102; // returning ping
const int HEADER_KEY_HOLD_ON = 103; // hold heading
const int HEADER_KEY_HOLD_OFF = 104; // cancel hold



// *** PORT CONSTANTS ***

const int LED_PIN = 13;
const int PNEUMATIC_PIN = 1; // pneumatics port

const int MOTOR_DIR_PORTS[NUM_MOTORS] = {1, 2, 3, 4, 5, 6};
const int MOTOR_POW_PORTS[NUM_MOTORS] = {7, 8, 9, 10, 11, 12};

const int SENSOR_PORTS[NUM_SENSORS] = {0, 1, 2, 3, 4, 5};



// misc constants

const int ACCELERATION = 8; // how fast motors change speed
const int SENSOR_ITERATION = 100000000;



// states
int desiredCompass = 0;
bool hold = false;

int ledState = LOW;
int pneumaticState = LOW;

int currentPower[NUM_MOTORS] = {0, 0, 0, 0, 0, 0}; // current motor power
int motorPower[NUM_MOTORS] = {0, 0, 0, 0, 0, 0}; // desired motor power


// Counter for sensor iteration
int sensorLoopCounter = 0;



// Initialize serial and output ports
void setup() {
    Serial.begin(9600);
    for (int i = 0; i < NUM_MOTORS; i++) {
        pinMode(MOTOR_DIR_PORTS[i], OUTPUT);
        pinMode(MOTOR_POW_PORTS[i], OUTPUT);
    }
    pinMode(PNEUMATIC_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
}


void loop() {
    // read and turn MOTORS from Serial port
    while (Serial.available() >= 5) {
        readSerial();
    }

    motorControl();
    sendSensorData();

    delay(DELAY_COUNTER);
}


void readSerial() {
    if (Serial.read() == HEADER_KEY_IN_1 && Serial.read() == HEADER_KEY_IN_2) {
        int specialKey = Serial.read();

        if (specialKey == HEADER_KEY_PING) {
            Serial.write(HEADER_KEY_OUT_1);
            Serial.write(HEADER_KEY_OUT_2);
            Serial.write(HEADER_KEY_PING);
            Serial.write(Serial.read());
            Serial.read();
        }
        else if (specialKey == HEADER_KEY_LIGHT) {
            // if the LED is off turn it on and vice-versa:
            ledState = !ledState;
            // set the LED with the ledState of the variable:
            digitalWrite(LED_PIN, ledState);
        } else if (specialKey == HEADER_KEY_PNEUMATICS) {
            // if the Pneumatics claw is off turn it on and vice-versa:
            pneumaticState = !pneumaticState;
            // set the Pneumatics claw with the ledState of the variable:
            digitalWrite(PNEUMATIC_PIN, pneumaticState);
        } else if (specialKey == HEADER_KEY_HOLD_ON) {
            // todo
            desiredCompass = readCompass();
            hold = true;
        } else if (specialKey == HEADER_KEY_HOLD_OFF) {
            hold = false;
        } else {
            readMotorValues();
        }
    }
}


void readMotorValues() {
    int motorNum = Serial.read();
    int motorP = Serial.read();
    int motorD = Serial.read();

    if (motorD == READ_FORWARD || motorD == READ_BACKWARD) {
        // stores the read motorP and motorD as the targetted
        // motor power [-255, 255]
        if (motorD == READ_BACKWARD) {
            motorPower[motorNum] = -1 * motorP;
        }
        else if (motorD == READ_FORWARD) {
            motorPower[motorNum] = motorP;
        }
    }
}


// adjust motor power and direction to desired values
void motorControl() {
    for (int i = 0; i < NUM_MOTORS; i++) {
        // updates motor power to be midpoint btw current power and targeted power
        currentPower[i] += (motorPower[i] - currentPower[i]) / ACCELERATION;

        if (hold) {
            adjustAngle();
        }

        // convert back to motor readable output
        int motorD = FORWARD;
        int motorP = currentPower[i];
        if (motorP < 0) {
            motorD = BACKWARD;
            motorP *= -1;
        }

        analogWrite(MOTOR_POW_PORTS[i], motorP);
        digitalWrite(MOTOR_DIR_PORTS[i], motorD);
    }
}


void sendSensorData() {
    // every SENSOR_ITERATION iteration, reads and sends sensor reading
    if (++sensorLoopCounter == SENSOR_ITERATION) {
        sensorLoopCounter = 0;

        for (int i = 0; i < NUM_SENSORS; i++) {
            int sensorValue = analogRead(SENSOR_PORTS[i]);
            Serial.write(HEADER_KEY_OUT_1);
            Serial.write(HEADER_KEY_OUT_2);
            Serial.write(i);
            Serial.write(sensorValue);
        }
    }
}


// stability control through reading of compass and adjusting motor powers based on the different in
// angle ans compared to previous
void adjustAngle() {
    int newCompass = readCompass();
    int diffAngle = (desiredCompass - newCompass + 256) % 256;
    int a = max(2, 3);

    if (diffAngle < 128) rotateLeft(diffAngle);
    else rotateLeft(diffAngle - 256);
}


// reads compass value, return a value between 0 and 255 (counter-clockwise increase, 0 north)
int readCompass() {
    return 0;
}


// rotates left a certain amount
void rotateLeft(int amount) {
    currentPower[MOTOR_FT_LT] += amount / 4;
    currentPower[MOTOR_FT_RT] -= amount / 4;
    currentPower[MOTOR_BK_RT] += amount / 4;
    currentPower[MOTOR_BK_LT] -= amount / 4;
    
    int max_ft = max(currentPower[MOTOR_FT_LT], currentPower[MOTOR_FT_RT]);
    int max_bk = max(currentPower[MOTOR_BK_RT], currentPower[MOTOR_BK_LT]);
    float scale = (float)max(max_ft, max_bk) / 255;

    currentPower[MOTOR_FT_LT] = (int)((float)currentPower[MOTOR_FT_LT] * scale);
    currentPower[MOTOR_FT_RT] = (int)((float)currentPower[MOTOR_FT_RT] * scale);
    currentPower[MOTOR_BK_RT] = (int)((float)currentPower[MOTOR_BK_RT] * scale);
    currentPower[MOTOR_BK_LT] = (int)((float)currentPower[MOTOR_BK_LT] * scale);
}









