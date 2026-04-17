/* 
 * ESP32 Edge ML Demonstration for Predictive Maintenance 
 * This code demonstrates integrating the generated pure C Random Forest 
 * without any external AI framework libraries.
 */

#include <Arduino.h>

// Proper C-linkage and exact signature from m2cgen (4-class output)
extern "C" {
    void score(double * input, double * output);
}

// Set up our 4 testing scenarios based on true historical data variations
const int NUM_SCENARIOS = 4;
double scenarios[4][4] = {
  // {RMS, Kurtosis, Spectral Entropy, Peak Freq}
  {0.076, 2.756, 3.307, 1066.4}, // Scenario 0: Normal Baseline behavior
  {0.138, 2.934, 4.214, 3375.0}, // Scenario 1: Ball Defect signature
  {0.293, 5.245, 4.598, 3585.9}, // Scenario 2: Inner Race Fault signature
  {0.646, 7.999, 4.065, 3445.3}  // Scenario 3: Outer Race Fault signature
};

String class_names[4] = {
  "Ball Defect",            // Class 0 (Alphabetical)
  "Inner Race Fault",       // Class 1
  "Normal System Baseline", // Class 2
  "Outer Race Fault"        // Class 3
};

int current_scenario = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\n[SYS] Initializing ESP32 Predictive Maintenance Subsystem...");
  Serial.println("[SYS] Starting Sensor Telemetry Stream (Simulated)...\n");
}

void loop() {
  Serial.print("==================================================\n");
  Serial.print(">> Fetching next 1024-window telemetry chunk (Scenario ");
  Serial.print(current_scenario); 
  Serial.println(")...\n");
  
  double dummy_features[4];
  for(int i=0; i<4; i++){
      dummy_features[i] = scenarios[current_scenario][i];
  }

  // The Random Forest outputs an array of votes for the 4 classes
  double class_outputs[4] = {0.0, 0.0, 0.0, 0.0};

  Serial.print("   Features: RMS="); Serial.print(dummy_features[0], 3);
  Serial.print(" | Kurt="); Serial.println(dummy_features[1], 1);
  Serial.print("             Entropy="); Serial.print(dummy_features[2], 2);
  Serial.print(" | Pk Freq="); Serial.println(dummy_features[3], 1);

  // Inference: Run the pure C Random Forest!
  unsigned long start_time = micros();
  score(dummy_features, class_outputs);
  unsigned long end_time = micros();

  // Find the class index with the highest score (Argmax)
  int predicted_class = 0;
  double max_score = class_outputs[0];
  for(int i = 1; i < 4; i++) {
      if(class_outputs[i] > max_score) {
          max_score = class_outputs[i];
          predicted_class = i;
      }
  }
  
  Serial.print("\n   [PREDICTION ID] "); Serial.println(predicted_class);
  Serial.print("   [PREDICTION LABEL] "); Serial.println(class_names[predicted_class]);
  Serial.print("   [INFERENCE TIME] "); Serial.print(end_time - start_time); Serial.println(" uS\n");

  if (predicted_class == 2) {
      Serial.println("   [STATUS] ✅ SYSTEM NOMINAL.");
  } else {
      Serial.print("   [CRITICAL ALERT] 🚨 ");
      Serial.print(class_names[predicted_class]); 
      Serial.println(" DETECTED. Immediate inspection advised.");
  }
  Serial.println();

  // Move to next scenario, loop back to start if at the end
  current_scenario++;
  if(current_scenario >= NUM_SCENARIOS) {
      current_scenario = 0;
  }

  delay(4000); // Wait 4 seconds so you can watch to the serial monitor output
}

/* 
 * -------------------------------------------------------------
 * NOTE: In Wokwi or Arduino IDE, you would literally PASTE the 
 * ENTIRE contents of models/random_forest_export.c right here!
 * -------------------------------------------------------------
 */
