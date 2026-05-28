/* 
 * ESP32 Edge ML Demonstration for Predictive Maintenance (BLDC Motors)
 * This code demonstrates integrating the generated pure C Random Forest 
 * model without any external AI framework libraries.
 */

#include <Arduino.h>

// Proper C-linkage and exact signature from m2cgen (6 inputs, 4 outputs)
extern "C" {
    void score(double * input, double * output);
}

// Set up our 4 testing scenarios based on true historical data variations
// Features array: {rms_current, kurtosis_current, mean_speed, std_speed, spectral_entropy_current, peak_frequency_current}
const int NUM_SCENARIOS = 4;
double scenarios[4][6] = {
  // Scenario 0: Healthy Motor Nominal State (Confidence: 99.4%)
  {3.258, 2.612, 21466.4, 463.7, 0.474, 0.000},
  // Scenario 1: Mechanical Damage State (Confidence: 96.5%)
  {3.404, 2.578, 22011.2, 522.0, 0.381, 0.000},
  // Scenario 2: Electrical Damage State (Confidence: 100.0%)
  {4.164, 2.458, 23155.1, 545.5, 0.273, 0.000},
  // Scenario 3: Combined Mech & Elec Damage State (Confidence: 100.0%)
  {4.985, 2.513, 22482.9, 509.3, 0.202, 0.000}
};

// Alphabetical ordering of outputs matching m2cgen's internal list:
// Class 0: Electrical Damage
// Class 1: Healthy
// Class 2: Mech_Elec_Damage
// Class 3: Mechanical Damage
String class_names[4] = {
  "Electrical Damage",
  "Healthy",
  "Mech_Elec_Damage",
  "Mechanical Damage"
};

int current_scenario = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\n[SYS] Initializing ESP32 BLDC Predictive Maintenance Subsystem...");
  Serial.println("[SYS] Starting Sensor Telemetry Stream (Simulated)...\n");
}

void loop() {
  Serial.print("==================================================\n");
  Serial.print(">> Fetching next 1024-window telemetry chunk (Scenario ");
  Serial.print(current_scenario); 
  Serial.println(")...\n");
  
  double dummy_features[6];
  for(int i=0; i<6; i++){
      dummy_features[i] = scenarios[current_scenario][i];
  }

  // The Random Forest outputs an array of votes for the 4 classes
  double class_outputs[4] = {0.0, 0.0, 0.0, 0.0};

  Serial.print("   [TELEMETRY RAW] ");
  Serial.print("Current RMS="); Serial.print(dummy_features[0], 3);
  Serial.print(" A | Kurtosis="); Serial.print(dummy_features[1], 2);
  Serial.print(" | Speed Mean="); Serial.print(dummy_features[2], 1);
  Serial.print(" RPM | Speed Ripple="); Serial.println(dummy_features[3], 1);
  Serial.print("                   Current Entropy="); Serial.print(dummy_features[4], 3);
  Serial.print(" | Current Peak Freq="); Serial.print(dummy_features[5], 3); Serial.println(" Hz");

  // Inference: Run the pure C Random Forest model!
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
  
  Serial.println();
  Serial.print("   [PREDICTION ID] "); Serial.println(predicted_class);
  Serial.print("   [PREDICTION LABEL] "); Serial.println(class_names[predicted_class]);
  Serial.print("   [INFERENCE TIME] "); Serial.print(end_time - start_time); Serial.println(" uS\n");

  if (predicted_class == 1) { // Class 1 is "Healthy"
      Serial.println("   [STATUS] ✅ SYSTEM NOMINAL.");
  } else if (predicted_class == 0) { // Electrical Damage
      Serial.println("   [WARNING ALERT] 🚨 ELECTRICAL DAMAGE DETECTED. winding check advised.");
  } else if (predicted_class == 3) { // Mechanical Damage
      Serial.println("   [WARNING ALERT] 🚨 MECHANICAL DAMAGE DETECTED. alignment check advised.");
  } else if (predicted_class == 2) { // Combined Mech_Elec_Damage
      Serial.println("   [CRITICAL SYSTEM FAULT] 🛑 BOTH MECHANICAL & ELECTRICAL DAMAGE DETECTED. Shutdown and immediate maintenance required.");
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
