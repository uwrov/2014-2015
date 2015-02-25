// Motor ports (D for direction and P for power)
// Motor keys (first compare 1 then 2)
int motors = 6;
int motorPortsD[motors] = {0, 1, 2, 3, 4, 5};
int motorPortsP[motors] = {6, 7, 8, 9, 10, 11};
String keyIn1 = 17;
String keyIn2 = 151;

// Sensor ports and every sensor iteration to send
// sensor value
// Sensor key values to be sent
int sensorIteration = 1;
int sensors = 6;
int sensorPorts[sensors] = {0, 1, 2, 3, 4, 5};
String keyOut1 = 74;
String keyOut2 = 225;

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
      analogWrite(motorPortsP[motorNum], motorP);
      digitalWrite(motorPortsD[motorNum], motorD - 1);
    }
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
}

