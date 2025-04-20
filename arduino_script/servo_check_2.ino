#include <TFT_eSPI.h>
#include <SPI.h>
#include <ESP32Servo.h>

TFT_eSPI tft = TFT_eSPI();

// Screen dimensions
const int screenWidth = 240;
const int screenHeight = 320;

// Eye geometry
int spaceBetweenDefault = 20; 
int spaceBetweenCurrent = spaceBetweenDefault;

// Eye left - size and position
int eyeLwidthDefault = 120;      
int eyeLheightDefault = 150;     
int eyeLwidthCurrent = eyeLwidthDefault;
int eyeLheightCurrent = eyeLheightDefault;
byte eyeLborderRadiusDefault = 50;
byte eyeLborderRadiusCurrent = eyeLborderRadiusDefault;

// Eye right - size and position (mirrored to left)
int eyeRwidthDefault = eyeLwidthDefault;
int eyeRheightDefault = eyeLheightDefault;
int eyeRwidthCurrent = eyeRwidthDefault;
int eyeRheightCurrent = eyeRheightDefault;
byte eyeRborderRadiusDefault = 50;
byte eyeRborderRadiusCurrent = eyeRborderRadiusDefault;

// Eye coordinates
int eyeLx = ((screenHeight) - (eyeLwidthDefault + spaceBetweenDefault + eyeRwidthDefault)) / 2;
int eyeLy = (screenWidth - eyeLheightDefault) / 2;
int eyeRx = eyeLx + eyeLwidthDefault + spaceBetweenDefault;
int eyeRy = eyeLy;

// Eyelids (if you want to animate them further)
int eyelidsHeight = eyeLheightDefault / 2;

// Blinking parameters
bool eyesOpen = true;        
unsigned long lastBlinkTime = 0;
const int blinkInterval = 3000;  // Every 3 seconds
const int blinkSpeed = 10;       
int blinkStep = 10;              

// Animation durations
bool isLaughing = false;
unsigned long laughStartTime = 0;
const int laughDuration = 2000; 

bool isSad = false;
unsigned long sadStartTime = 0;
const int sadDuration = 2000;

// Servo motor pins and initialization
Servo motor1;
Servo motor2;

// IMPORTANT: Define the center position as per Python's expectations (pan=65, tilt=105)
const int panCenter = 65;  
const int tiltCenter = 105;

int motor1Pin = 13;  // Pan servo pin
int motor2Pin = 14;  // Tilt servo pin

volatile bool comboRunning = false;
volatile bool cancelCombo = false;

void setup() {
  tft.init();
  tft.setRotation(3); // Orient screen vertically
  tft.fillScreen(TFT_WHITE);
  Serial.begin(115200);  // Start serial communication
  delay(1000); // Allow time for serial port to settle
  
  motor1.attach(motor1Pin);
  motor2.attach(motor2Pin);
  digitalWrite(motor1Pin, LOW);  // Pre-set to known state
  digitalWrite(motor2Pin, LOW); 
  
  // Set servos to center position initially.
  motor1.write(panCenter);
  motor2.write(tiltCenter);

  // Draw initial eyes (neutral expression)
  drawEyes();
}

void loop() {
  static String lastCommand = "blink"; 

  // Check if there is a new serial command from Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    Serial.print("Command received: ");
    Serial.println(command);
    if (command.length() == 0 || command.length() > 50) {
      return;
  }

    if (command.startsWith("move:")) {
      moveServos(command);  // Parse and handle servo movement commands
    } 
    else if (command == "blink" ||
             command == "happy" ||
             command == "sad" ||
             command == "confused" ||
             command == "winkleft" ||
             command == "winkright") {
      lastCommand = command;
    }
    else if (command == "shutdown") {
      motor1.write(65);  // Replace with your pan center
      motor2.write(105); // Replace with your tilt center
      lastCommand = "blink";
      Serial.println("Shutdown complete");
    }
 
    else {
      Serial.println("Invalid command received.");
    }
  }

  // Execute animation based on the last command
  if (lastCommand == "blink") {
    blinking();
  } 
  else if (lastCommand == "happy") {
    laughAnimation();
  } 
  else if (lastCommand == "sad") {
    animateSadEyes();
  } 
  else if (lastCommand == "confused") {
    animateConfusedEyes();
  } 
  else if (lastCommand == "winkleft") {
    winkAnimationLeft();
  } 
  else if (lastCommand == "winkright") {
    winkAnimationRight();
  }
}

// ---------------------
// Servo Movement Adjustments
// ---------------------
void moveServos(String command) {
  // Expected command format: move:angle1,angle2
  if (command.startsWith("move:")) {
    int separatorIndex = command.indexOf(':');
    String anglesPart = command.substring(separatorIndex + 1);
    int commaIndex = anglesPart.indexOf(',');
    if (commaIndex != -1) {
      int angle1 = anglesPart.substring(0, commaIndex).toInt();
      int angle2 = anglesPart.substring(commaIndex + 1).toInt();
      
      // Clamp angles (0-180)
      angle1 = constrain(angle1, 0, 180);
      angle2 = constrain(angle2, 0, 180);
      
      // Adjust so that pan (angle1) barely deviates from center if needed:
      // For left/right, keep within 5-10 degree difference from panCenter.
      if (abs(angle1 - panCenter) > 10) {
        if (angle1 < panCenter) {
          angle1 = panCenter - 5;
        } else {
          angle1 = panCenter + 5;
        }
      }
      
      // For tilt (angle2), let it vary more but ensure center is tiltCenter:
      // (No special constraint applied unless needed.)
      
      motor1.write(angle1);
      motor2.write(angle2);
      
      Serial.print("Servos moved to angles: ");
      Serial.print(angle1);
      Serial.print(", ");
      Serial.println(angle2);
    } else {
      Serial.println("Invalid format. Use move:angle1,angle2");
    }
  } else {
    Serial.println("Unknown command.");
  }
}

// ---------------------
// Expression Animations
// ---------------------

// Blinking logic
void blinking() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastBlinkTime > blinkInterval) {
    blinkStep = 0;            
    eyesOpen = false;         
    lastBlinkTime = currentMillis;
  }
  if (!eyesOpen) {
    animateBlink();
  }
}

// Draw a single eye
void drawEye(int x, int y, int width, int height, int borderRadius) {
  tft.fillRoundRect(x, y, width, height, borderRadius, TFT_BLUE);
}

// Draw both eyes
void drawEyes() {
  tft.fillScreen(TFT_WHITE);
  drawEye(eyeLx, eyeLy, eyeLwidthCurrent, eyeLheightCurrent, eyeLborderRadiusCurrent);
  drawEye(eyeRx, eyeRy, eyeRwidthCurrent, eyeRheightCurrent, eyeRborderRadiusCurrent);
}

// Blinking animation (open and close)
void animateBlink() {
  if (eyesOpen) {
    for (int h = eyeLheightCurrent; h > 0; h -= 48) {
      eyeLheightCurrent = h;
      eyeRheightCurrent = h;
      drawEyes();
      delay(blinkSpeed);
    }
    eyesOpen = false;
    delay(50);
  } else {
    for (int h = 0; h <= eyeLheightDefault; h += 48) {
      eyeLheightCurrent = h;
      eyeRheightCurrent = h;
      drawEyes();
      delay(blinkSpeed);
    }
    eyesOpen = true;
  }
}

// Happy eyes animation
void drawHappyEyes() {
  int offset = (millis() / 100) % 2 == 0 ? 3 : -3;
  tft.fillRect(eyeLx - 5, eyeLy - 5, eyeLwidthDefault + 10, eyeLheightDefault + 10, TFT_WHITE);
  tft.fillRect(eyeRx - 5, eyeRy - 5, eyeRwidthDefault + 10, eyeRheightDefault + 10, TFT_WHITE);
  drawCSmile(eyeLx + eyeLwidthDefault / 2, eyeLy + eyeLheightDefault / 2 + offset, eyeLwidthDefault, eyeLheightDefault / 3, TFT_BLUE);
  drawCSmile(eyeRx + eyeRwidthDefault / 2, eyeRy + eyeRheightDefault / 2 + offset, eyeRwidthDefault, eyeRheightDefault / 3, TFT_BLUE);
}

void laughAnimation() {
  isLaughing = true;
  laughStartTime = millis();
  drawHappyEyes();
}

// Draw a "C" shape for a happy smile
void drawCSmile(int x, int y, int w, int h, uint16_t color) {
  int thickness = 26;
  for (int i = -w / 2; i <= w / 2; i += 3) {
    int arcHeight = h * sqrt(1 - pow(i / (float)(w / 2), 2));
    for (int t = 0; t < thickness; t++) {
      tft.drawPixel(x + i, y + arcHeight - t, color);
    }
  }
}

// Sad eyes animation
void animateSadEyes() {
  int sadnessOffset = (millis() / 300) % 2 == 0 ? 1 : -1;
  int sadEyeLx = eyeLx + 2;
  int sadEyeRx = eyeRx - 2;
  int sadEyeLy = eyeLy + 3 + sadnessOffset;
  int sadEyeRy = eyeRy + 3 + sadnessOffset;
  tft.fillRect(eyeLx - 5, eyeLy - 5, eyeLwidthDefault + 10, eyeLheightDefault + 10, TFT_WHITE);
  tft.fillRect(eyeRx - 5, eyeRy - 5, eyeRwidthDefault + 10, eyeRheightDefault + 10, TFT_WHITE);
  drawSadCurve(sadEyeLx + eyeLwidthDefault / 2, sadEyeLy + eyeLheightDefault / 2, eyeLwidthDefault, eyeLheightDefault / 4, TFT_BLUE);
  drawSadCurve(sadEyeRx + eyeRwidthDefault / 2, sadEyeRy + eyeRheightDefault / 2, eyeRwidthDefault, eyeRheightDefault / 4, TFT_BLUE);
}

void drawSadCurve(int x, int y, int w, int h, uint16_t color) {
  int thickness = 20;
  for (int i = -w / 2; i <= w / 2; i += 3) {
    int arcHeight = h * sqrt(1 - pow(i / (float)(w / 2), 2));
    for (int t = 0; t < thickness; t++) {
      tft.drawPixel(x + i, y - arcHeight + t, color);
    }
  }
}

// Confused eyes animation: alternate between two states
void animateConfusedEyes() {
  drawConfusedEyesLeft();
  delay(500);
  drawConfusedEyesRight();
  delay(500);
}

void drawConfusedEyesLeft() {
  tft.fillRect(eyeLx - 5, eyeLy - 5, eyeLwidthDefault + 10, eyeLheightDefault + 10, TFT_WHITE);
  tft.fillRect(eyeRx - 5, eyeRy - 5, eyeRwidthDefault + 10, eyeRheightDefault + 10, TFT_WHITE);
  drawEye(eyeLx, eyeLy, eyeLwidthCurrent, eyeLheightCurrent, eyeLborderRadiusCurrent);
  int shrunkenHeight = eyeRheightCurrent * 0.6;
  drawEye(eyeRx, eyeRy, eyeRwidthCurrent, shrunkenHeight, eyeRborderRadiusCurrent);
}

void drawConfusedEyesRight() {
  tft.fillRect(eyeLx - 5, eyeLy - 5, eyeLwidthDefault + 10, eyeLheightDefault + 10, TFT_WHITE);
  tft.fillRect(eyeRx - 5, eyeRy - 5, eyeRwidthDefault + 10, eyeRheightDefault + 10, TFT_WHITE);
  int shrunkenHeight = eyeLheightCurrent * 0.6;
  drawEye(eyeLx, eyeLy, eyeLwidthCurrent, shrunkenHeight, eyeLborderRadiusCurrent);
  drawEye(eyeRx, eyeRy, eyeRwidthCurrent, eyeRheightCurrent, eyeRborderRadiusCurrent);
}

// Wink animations
void winkAnimationRight() {
  closeEyeWithLineRight();
  delay(500);
  drawEye(eyeRx, eyeRy, eyeRwidthCurrent, eyeRheightCurrent, eyeRborderRadiusCurrent);
  delay(500);
}

void closeEyeWithLineRight() {
  tft.fillRect(eyeRx - 2, eyeRy - 2, eyeRwidthDefault + 4, eyeRheightDefault + 4, TFT_WHITE);
  int lineThickness = 5;
  int lineY = eyeRy + eyeRheightDefault / 2;
  tft.fillRect(eyeRx, lineY - lineThickness / 2, eyeRwidthDefault, lineThickness, TFT_BLUE);
  drawEye(eyeLx, eyeLy, eyeLwidthDefault, eyeLheightDefault, eyeLborderRadiusDefault);
}

void winkAnimationLeft() {
  closeEyeWithLineLeft();
  delay(500);
  drawEye(eyeLx, eyeLy, eyeLwidthCurrent, eyeLheightCurrent, eyeLborderRadiusCurrent);
  delay(500);
}

void closeEyeWithLineLeft() {
  tft.fillRect(eyeLx - 2, eyeLy - 2, eyeLwidthDefault + 4, eyeLheightDefault + 4, TFT_WHITE);
  int lineThickness = 5;
  int lineY = eyeLy + eyeLheightDefault / 2;
  tft.fillRect(eyeLx, lineY - lineThickness / 2, eyeLwidthDefault, lineThickness, TFT_BLUE);
  drawEye(eyeRx, eyeRy, eyeRwidthDefault, eyeRheightDefault, eyeRborderRadiusDefault);
}

// ---------------------------------------
// The code below remains unchanged unless further integration is needed
// ---------------------------------------
