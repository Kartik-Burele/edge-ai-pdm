/*
 * ESP32 Edge ML Demonstration for Predictive Maintenance
 * This code demonstrates integrating the generated pure C Random Forest
 * without any external AI framework libraries.
 */

#include <Arduino.h>

// Proper C-linkage and exact signature from m2cgen (4-class output)
extern "C" {
void score(double *input, double *output);
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
  Serial.println(
      "\n[SYS] Initializing ESP32 Predictive Maintenance Subsystem...");
  Serial.println("[SYS] Starting Sensor Telemetry Stream (Simulated)...\n");
}

void loop() {
  Serial.print("==================================================\n");
  Serial.print(">> Fetching next 1024-window telemetry chunk (Scenario ");
  Serial.print(current_scenario);
  Serial.println(")...\n");

  double dummy_features[4];
  for (int i = 0; i < 4; i++) {
    dummy_features[i] = scenarios[current_scenario][i];
  }

  // The Random Forest outputs an array of votes for the 4 classes
  double class_outputs[4] = {0.0, 0.0, 0.0, 0.0};

  Serial.print("   Features: RMS=");
  Serial.print(dummy_features[0], 3);
  Serial.print(" | Kurt=");
  Serial.println(dummy_features[1], 1);
  Serial.print("             Entropy=");
  Serial.print(dummy_features[2], 2);
  Serial.print(" | Pk Freq=");
  Serial.println(dummy_features[3], 1);

  // Inference: Run the pure C Random Forest!
  unsigned long start_time = micros();
  score(dummy_features, class_outputs);
  unsigned long end_time = micros();

  // Find the class index with the highest score (Argmax)
  int predicted_class = 0;
  double max_score = class_outputs[0];
  for (int i = 1; i < 4; i++) {
    if (class_outputs[i] > max_score) {
      max_score = class_outputs[i];
      predicted_class = i;
    }
  }

  Serial.print("\n   [PREDICTION ID] ");
  Serial.println(predicted_class);
  Serial.print("   [PREDICTION LABEL] ");
  Serial.println(class_names[predicted_class]);
  Serial.print("   [INFERENCE TIME] ");
  Serial.print(end_time - start_time);
  Serial.println(" uS\n");

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
  if (current_scenario >= NUM_SCENARIOS) {
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

#include <string.h>
void add_vectors(double *v1, double *v2, int size, double *result) {
  for (int i = 0; i < size; ++i)
    result[i] = v1[i] + v2[i];
}
void mul_vector_number(double *v1, double num, int size, double *result) {
  for (int i = 0; i < size; ++i)
    result[i] = v1[i] * num;
}
void score(double *input, double *output) {
  double var0[4];
  double var1[4];
  double var2[4];
  double var3[4];
  double var4[4];
  double var5[4];
  double var6[4];
  double var7[4];
  double var8[4];
  double var9[4];
  double var10[4];
  double var11[4];
  double var12[4];
  double var13[4];
  double var14[4];
  double var15[4];
  double var16[4];
  double var17[4];
  double var18[4];
  double var19[4];
  double var20[4];
  double var21[4];
  double var22[4];
  double var23[4];
  double var24[4];
  double var25[4];
  double var26[4];
  double var27[4];
  double var28[4];
  double var29[4];
  double var30[4];
  double var31[4];
  double var32[4];
  double var33[4];
  double var34[4];
  double var35[4];
  double var36[4];
  double var37[4];
  double var38[4];
  double var39[4];
  double var40[4];
  double var41[4];
  double var42[4];
  double var43[4];
  double var44[4];
  double var45[4];
  double var46[4];
  double var47[4];
  double var48[4];
  double var49[4];
  double var50[4];
  if (input[3] <= 1195.3125) {
    memcpy(var50, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4210221618413925) {
      if (input[0] <= 0.22094938904047012) {
        memcpy(var50, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var50, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var50, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  double var51[4];
  if (input[3] <= 1195.3125) {
    memcpy(var51, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[2] <= 4.238826036453247) {
      if (input[0] <= 0.41583168506622314) {
        if (input[3] <= 3509.765625) {
          if (input[0] <= 0.23191485553979874) {
            memcpy(var51, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var51, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          }
        } else {
          memcpy(var51, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var51, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    } else {
      if (input[0] <= 0.21509575843811035) {
        memcpy(var51, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[1] <= 6.99263596534729) {
          memcpy(var51, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var51, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var50, var51, 4, var49);
  double var52[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var52, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.536648273468018) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var52, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var52, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var52, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var49, var52, 4, var48);
  double var53[4];
  if (input[2] <= 3.874841809272766) {
    if (input[0] <= 0.1117170862853527) {
      memcpy(var53, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[1] <= 4.939361214637756) {
        memcpy(var53, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var53, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  } else {
    if (input[2] <= 4.277889251708984) {
      if (input[0] <= 0.4132176637649536) {
        if (input[0] <= 0.22390717267990112) {
          memcpy(var53, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var53, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var53, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    } else {
      if (input[2] <= 4.370277643203735) {
        if (input[0] <= 0.21295758336782455) {
          memcpy(var53, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          if (input[1] <= 6.937062740325928) {
            memcpy(var53, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var53, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
          }
        }
      } else {
        memcpy(var53, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var48, var53, 4, var47);
  double var54[4];
  if (input[3] <= 1822.265625) {
    memcpy(var54, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.536648273468018) {
      if (input[1] <= 4.384668231010437) {
        memcpy(var54, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var54, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var54, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var47, var54, 4, var46);
  double var55[4];
  if (input[3] <= 1195.3125) {
    memcpy(var55, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4186412990093231) {
      if (input[0] <= 0.22094938904047012) {
        memcpy(var55, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var55, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var55, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var46, var55, 4, var45);
  double var56[4];
  if (input[0] <= 0.10255303233861923) {
    memcpy(var56, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41671085357666016) {
      if (input[1] <= 4.142840027809143) {
        memcpy(var56, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var56, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var56, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var45, var56, 4, var44);
  double var57[4];
  if (input[0] <= 0.10255303233861923) {
    memcpy(var57, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.6335954666137695) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var57, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var57, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var57, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var44, var57, 4, var43);
  double var58[4];
  if (input[0] <= 0.10303445160388947) {
    memcpy(var58, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.6335954666137695) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var58, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var58, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var58, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var43, var58, 4, var42);
  double var59[4];
  if (input[3] <= 1195.3125) {
    memcpy(var59, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.649531602859497) {
      if (input[0] <= 0.22251413017511368) {
        memcpy(var59, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var59, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var59, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var42, var59, 4, var41);
  double var60[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var60, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[2] <= 4.228182554244995) {
      if (input[1] <= 6.354802131652832) {
        if (input[1] <= 4.207178592681885) {
          memcpy(var60, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var60, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var60, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    } else {
      if (input[1] <= 4.142840027809143) {
        memcpy(var60, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[0] <= 0.44317667186260223) {
          memcpy(var60, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var60, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var41, var60, 4, var40);
  double var61[4];
  if (input[3] <= 1195.3125) {
    memcpy(var61, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[0] <= 0.2221481129527092) {
        memcpy(var61, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var61, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var61, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var40, var61, 4, var39);
  double var62[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var62, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 4.381275296211243) {
      memcpy(var62, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[0] <= 0.4210221618413925) {
        memcpy(var62, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var62, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var39, var62, 4, var38);
  double var63[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var63, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var63, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var63, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var63, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var38, var63, 4, var37);
  double var64[4];
  if (input[3] <= 1195.3125) {
    memcpy(var64, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 4.167100787162781) {
      memcpy(var64, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[1] <= 6.476781606674194) {
        memcpy(var64, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var64, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var37, var64, 4, var36);
  double var65[4];
  if (input[2] <= 3.8078489303588867) {
    if (input[3] <= 1968.75) {
      memcpy(var65, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[0] <= 0.3583456054329872) {
        memcpy(var65, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var65, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  } else {
    if (input[2] <= 4.315748453140259) {
      if (input[3] <= 3052.734375) {
        if (input[0] <= 0.4143981486558914) {
          if (input[2] <= 4.042057991027832) {
            memcpy(var65, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var65, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          }
        } else {
          memcpy(var65, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      } else {
        if (input[0] <= 0.2222730666399002) {
          memcpy(var65, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          if (input[1] <= 6.386324167251587) {
            memcpy(var65, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var65, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
          }
        }
      }
    } else {
      if (input[0] <= 0.20987921208143234) {
        memcpy(var65, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[3] <= 2847.65625) {
          if (input[0] <= 0.44026871025562286) {
            memcpy(var65, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var65, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
          }
        } else {
          if (input[1] <= 7.043588161468506) {
            memcpy(var65, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var65, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
          }
        }
      }
    }
  }
  add_vectors(var36, var65, 4, var35);
  double var66[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var66, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.2196473479270935) {
      memcpy(var66, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[0] <= 0.41905577480793) {
        memcpy(var66, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var66, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var35, var66, 4, var34);
  double var67[4];
  if (input[2] <= 3.8078489303588867) {
    if (input[3] <= 1968.75) {
      memcpy(var67, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[2] <= 3.7174404859542847) {
        if (input[0] <= 0.37236247956752777) {
          memcpy(var67, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var67, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var67, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  } else {
    if (input[1] <= 6.692112445831299) {
      if (input[2] <= 4.251574993133545) {
        if (input[0] <= 0.09715001657605171) {
          memcpy(var67, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
        } else {
          if (input[3] <= 3509.765625) {
            if (input[3] <= 3046.875) {
              memcpy(var67, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
            } else {
              memcpy(var67, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
            }
          } else {
            memcpy(var67, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          }
        }
      } else {
        if (input[3] <= 3486.328125) {
          if (input[3] <= 3052.734375) {
            memcpy(var67, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var67, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
          }
        } else {
          memcpy(var67, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      }
    } else {
      memcpy(var67, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var34, var67, 4, var33);
  double var68[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var68, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.2221481129527092) {
      memcpy(var68, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[1] <= 6.476781606674194) {
        memcpy(var68, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var68, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var33, var68, 4, var32);
  double var69[4];
  if (input[0] <= 0.10374125465750694) {
    memcpy(var69, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4221183806657791) {
      if (input[0] <= 0.2221481129527092) {
        memcpy(var69, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var69, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var69, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var32, var69, 4, var31);
  double var70[4];
  if (input[3] <= 1195.3125) {
    memcpy(var70, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var70, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var70, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var70, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var31, var70, 4, var30);
  double var71[4];
  if (input[3] <= 1822.265625) {
    memcpy(var71, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 4.142840027809143) {
      memcpy(var71, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[2] <= 4.207640886306763) {
        if (input[3] <= 3521.484375) {
          memcpy(var71, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        } else {
          memcpy(var71, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        if (input[3] <= 2847.65625) {
          if (input[3] <= 2818.359375) {
            memcpy(var71, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var71, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
          }
        } else {
          if (input[0] <= 0.43359309434890747) {
            memcpy(var71, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var71, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
          }
        }
      }
    }
  }
  add_vectors(var30, var71, 4, var29);
  double var72[4];
  if (input[2] <= 3.824163794517517) {
    if (input[1] <= 5.414724826812744) {
      if (input[0] <= 0.11324875056743622) {
        memcpy(var72, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var72, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var72, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  } else {
    if (input[1] <= 6.6138410568237305) {
      if (input[0] <= 0.21720662713050842) {
        if (input[3] <= 2144.53125) {
          memcpy(var72, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var72, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var72, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var72, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var29, var72, 4, var28);
  double var73[4];
  if (input[3] <= 1195.3125) {
    memcpy(var73, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[2] <= 4.258835554122925) {
        if (input[3] <= 3486.328125) {
          if (input[1] <= 4.378700017929077) {
            memcpy(var73, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
          } else {
            memcpy(var73, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
          }
        } else {
          memcpy(var73, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        if (input[0] <= 0.21368156373500824) {
          memcpy(var73, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var73, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      }
    } else {
      memcpy(var73, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var28, var73, 4, var27);
  double var74[4];
  if (input[3] <= 1933.59375) {
    memcpy(var74, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.685906648635864) {
      if (input[0] <= 0.22173581272363663) {
        memcpy(var74, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var74, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var74, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var27, var74, 4, var26);
  double var75[4];
  if (input[0] <= 0.10377496853470802) {
    memcpy(var75, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4167770445346832) {
      if (input[0] <= 0.22094938904047012) {
        memcpy(var75, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var75, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var75, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var26, var75, 4, var25);
  double var76[4];
  if (input[3] <= 1921.875) {
    memcpy(var76, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[0] <= 0.22094938904047012) {
        memcpy(var76, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var76, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var76, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var25, var76, 4, var24);
  double var77[4];
  if (input[3] <= 1839.84375) {
    memcpy(var77, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.556402683258057) {
      if (input[0] <= 0.22173581272363663) {
        memcpy(var77, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var77, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var77, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var24, var77, 4, var23);
  double var78[4];
  if (input[3] <= 1886.71875) {
    memcpy(var78, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[2] <= 4.258503198623657) {
      if (input[0] <= 0.4128194600343704) {
        if (input[0] <= 0.22710450738668442) {
          memcpy(var78, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var78, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var78, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    } else {
      if (input[0] <= 0.21368156373500824) {
        memcpy(var78, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[0] <= 0.4388899505138397) {
          memcpy(var78, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var78, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var23, var78, 4, var22);
  double var79[4];
  if (input[0] <= 0.10255303233861923) {
    memcpy(var79, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41874343156814575) {
      if (input[0] <= 0.21911073476076126) {
        memcpy(var79, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var79, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var79, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var22, var79, 4, var21);
  double var80[4];
  if (input[0] <= 0.10374125465750694) {
    memcpy(var80, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[0] <= 0.22125814855098724) {
        memcpy(var80, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var80, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var80, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var21, var80, 4, var20);
  double var81[4];
  if (input[3] <= 1195.3125) {
    memcpy(var81, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.536648273468018) {
      if (input[0] <= 0.2196473479270935) {
        memcpy(var81, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var81, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var81, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var20, var81, 4, var19);
  double var82[4];
  if (input[3] <= 1195.3125) {
    memcpy(var82, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4210221618413925) {
      if (input[1] <= 4.387324929237366) {
        memcpy(var82, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var82, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var82, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var19, var82, 4, var18);
  double var83[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var83, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[2] <= 4.258963108062744) {
      if (input[0] <= 0.22710450738668442) {
        memcpy(var83, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[0] <= 0.4128194600343704) {
          memcpy(var83, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var83, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    } else {
      if (input[1] <= 3.96382737159729) {
        memcpy(var83, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[1] <= 7.2770771980285645) {
          memcpy(var83, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var83, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var18, var83, 4, var17);
  double var84[4];
  if (input[2] <= 3.872505784034729) {
    if (input[0] <= 0.11027558520436287) {
      memcpy(var84, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[3] <= 3416.015625) {
        memcpy(var84, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      } else {
        if (input[3] <= 3439.453125) {
          memcpy(var84, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var84, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  } else {
    if (input[1] <= 4.347151160240173) {
      memcpy(var84, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[0] <= 0.4186772406101227) {
        memcpy(var84, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var84, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var17, var84, 4, var16);
  double var85[4];
  if (input[2] <= 3.811757206916809) {
    if (input[1] <= 5.358620643615723) {
      if (input[3] <= 2250.0) {
        memcpy(var85, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var85, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var85, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  } else {
    if (input[1] <= 4.176964163780212) {
      if (input[3] <= 2144.53125) {
        memcpy(var85, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var85, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      if (input[1] <= 6.6138410568237305) {
        memcpy(var85, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var85, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var16, var85, 4, var15);
  double var86[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var86, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 4.347151160240173) {
      memcpy(var86, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[1] <= 6.685906648635864) {
        memcpy(var86, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var86, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var15, var86, 4, var14);
  double var87[4];
  if (input[3] <= 1839.84375) {
    memcpy(var87, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.6138410568237305) {
      if (input[3] <= 3486.328125) {
        if (input[0] <= 0.22277607768774033) {
          memcpy(var87, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var87, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var87, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var87, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var14, var87, 4, var13);
  double var88[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var88, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4167770445346832) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var88, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var88, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var88, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var13, var88, 4, var12);
  double var89[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var89, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.21720662713050842) {
      memcpy(var89, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[2] <= 4.237983703613281) {
        if (input[0] <= 0.40777069330215454) {
          memcpy(var89, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var89, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      } else {
        if (input[0] <= 0.43165743350982666) {
          memcpy(var89, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var89, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var12, var89, 4, var11);
  double var90[4];
  if (input[2] <= 3.824163794517517) {
    if (input[1] <= 5.358620643615723) {
      if (input[0] <= 0.11356979236006737) {
        memcpy(var90, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var90, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var90, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  } else {
    if (input[0] <= 0.4210221618413925) {
      if (input[1] <= 4.347151160240173) {
        if (input[0] <= 0.09635253995656967) {
          memcpy(var90, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var90, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var90, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var90, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var11, var90, 4, var10);
  double var91[4];
  if (input[0] <= 0.10398825630545616) {
    memcpy(var91, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.41905577480793) {
      if (input[0] <= 0.22094938904047012) {
        memcpy(var91, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var91, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var91, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var10, var91, 4, var9);
  double var92[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var92, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.22030945867300034) {
      memcpy(var92, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[2] <= 4.210436582565308) {
        if (input[0] <= 0.40911702811717987) {
          memcpy(var92, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var92, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      } else {
        if (input[0] <= 0.43572212755680084) {
          memcpy(var92, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var92, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var9, var92, 4, var8);
  double var93[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var93, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.556402683258057) {
      if (input[0] <= 0.2196473479270935) {
        memcpy(var93, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var93, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var93, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var8, var93, 4, var7);
  double var94[4];
  if (input[0] <= 0.10398825630545616) {
    memcpy(var94, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.22094938904047012) {
      memcpy(var94, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
    } else {
      if (input[1] <= 6.4353601932525635) {
        memcpy(var94, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var94, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    }
  }
  add_vectors(var7, var94, 4, var6);
  double var95[4];
  if (input[3] <= 1195.3125) {
    memcpy(var95, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[0] <= 0.4167770445346832) {
      if (input[0] <= 0.2221481129527092) {
        memcpy(var95, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var95, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var95, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var6, var95, 4, var5);
  double var96[4];
  if (input[3] <= 1195.3125) {
    memcpy(var96, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.575878143310547) {
      if (input[1] <= 4.167100787162781) {
        memcpy(var96, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var96, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var96, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var5, var96, 4, var4);
  double var97[4];
  if (input[0] <= 0.10374125465750694) {
    memcpy(var97, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.6335954666137695) {
      if (input[0] <= 0.22094938904047012) {
        memcpy(var97, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var97, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var97, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var4, var97, 4, var3);
  double var98[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var98, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[1] <= 6.6335954666137695) {
      if (input[1] <= 4.347151160240173) {
        memcpy(var98, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        memcpy(var98, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
      }
    } else {
      memcpy(var98, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
    }
  }
  add_vectors(var3, var98, 4, var2);
  double var99[4];
  if (input[0] <= 0.10325983539223671) {
    memcpy(var99, (double[]){0.0, 0.0, 1.0, 0.0}, 4 * sizeof(double));
  } else {
    if (input[2] <= 4.249755144119263) {
      if (input[0] <= 0.4128194600343704) {
        if (input[3] <= 3509.765625) {
          memcpy(var99, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var99, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        }
      } else {
        memcpy(var99, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
      }
    } else {
      if (input[0] <= 0.21368156373500824) {
        memcpy(var99, (double[]){1.0, 0.0, 0.0, 0.0}, 4 * sizeof(double));
      } else {
        if (input[0] <= 0.4339361637830734) {
          memcpy(var99, (double[]){0.0, 1.0, 0.0, 0.0}, 4 * sizeof(double));
        } else {
          memcpy(var99, (double[]){0.0, 0.0, 0.0, 1.0}, 4 * sizeof(double));
        }
      }
    }
  }
  add_vectors(var2, var99, 4, var1);
  mul_vector_number(var1, 0.02, 4, var0);
  memcpy(output, var0, 4 * sizeof(double));
}
