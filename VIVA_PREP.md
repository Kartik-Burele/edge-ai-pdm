# Edge AI Predictive Maintenance - Viva Preparation Guide
*Evaluator Persona: PhD in AI / Industry Expert in Embedded Machine Learning*

This document contains highly targeted, realistic viva questions an evaluator will ask to test your depth of knowledge on the engineering decisions made in this specific project.

---

## Section 1: Data & Signal Processing

**Q1: You mentioned using a 1024-sample window for your sensor data. Why exactly 1024? Why not 500 or 5000?**

**Answer:** A window size of 1024 is optimal because the Fast Fourier Transform (FFT) algorithm operates most efficiently on arrays that are powers of 2 (e.g., 256, 512, 1024). A 1024-sample window strikes the right balance between having enough temporal resolution to capture low-frequency mechanical faults, while remaining small enough to be processed rapidly within the limited RAM of an ESP32 microcontroller without causing memory overflow.

**Q2: You extracted features like RMS, Kurtosis, and Spectral Entropy instead of feeding the raw vibration data directly into the neural network. Why?**

**Answer:** Feeding raw high-frequency vibration waveforms directly into a model requires a deep, computationally heavy architecture (like a 1D-CNN or LSTM), which is unsuitable for a resource-constrained ESP32. By using domain-specific signal processing (FFT) to extract statistical features, we drastically reduce the data payload size (from an array of 1024 floats to just 4 distinct features, under 1KB). This allows us to use ultra-lightweight models (like a tiny TFLite NN or Random Forest) that achieve high accuracy while consuming less than 50KB of flash memory.

**Q3: Why is Kurtosis specifically a good feature for bearing fault detection?**

**Answer:** Kurtosis measures the "tailedness" or the presence of sharp spikes in a signal distribution. In a healthy motor, the vibration is mostly smooth and normally distributed (Kurtosis ~ 3.0). When a bearing defect occurs (like a crack in the outer race), the rolling elements hit the crack, generating periodic high-impact spikes. Kurtosis is highly sensitive to these impacts, making it one of the most reliable statistical indicators of early-stage bearing degradation.

---

## Section 2: Model Architecture & Edge Constraints

**Q4: Your evaluation metrics show 100% accuracy. As an AI researcher, 100% usually indicates data leakage or overfitting. How do you defend this result?**

**Answer:** 100% accuracy on real-world raw data is indeed suspicious. However, in our system, we are not classifying raw noise; we are classifying highly engineered frequency-domain features (Spectral Entropy, Peak Frequency) from the controlled CWRU dataset. These specific features transform the complex vibration data into clusters that are almost perfectly linearly separable. Therefore, the models are not memorizing the noise (overfitting); they are correctly identifying extremely distinct mechanical physics signatures. In a real factory environment with varying machine loads, we expect this accuracy to drop, which is exactly why we implemented the `< 0.75` confidence thresholding safety net.

**Q5: You deployed two different models: a TensorFlow Lite Neural Network and a Pure C Random Forest. What is the engineering trade-off between these two?**

**Answer:** The trade-off is strictly **Memory Footprint vs. Execution Speed**. 
* The **TFLite model** uses INT8 quantization, compressing the network weights so it only consumes about **2.7 KB** of memory, making it ideal for the tightest storage constraints. However, running inference requires the TFLite interpreter overhead (~0.010 ms).
* The **Pure C Random Forest** compiles directly into raw machine instructions. It executes twice as fast (~0.005 ms) because there is no interpreter overhead, but hardcoding every branch of the decision trees requires significantly more flash memory (**~43 KB**). 

**Q6: What is INT8 Quantization, and does it reduce your model's accuracy?**

**Answer:** INT8 Quantization is a technique that converts the standard 32-bit floating-point weights and activations of the neural network into 8-bit integers. This reduces the model size by a factor of 4x and speeds up inference because microcontrollers perform integer math much faster than floating-point math. While quantization can sometimes lead to a slight drop in accuracy due to loss of precision, our feature set is distinct enough that the model maintained its high performance even at 8-bit precision.

---

## Section 3: System Design & Real-World Viability

**Q7: Why process the data on the "Edge" (the ESP32) at all? Why not just send the raw sensor data via Wi-Fi to a cloud server like AWS and run a massive, highly accurate model there?**

**Answer:** There are three critical reasons for Edge AI in industrial environments:
1. **Latency:** Cloud transmission introduces network latency. Edge inference (taking less than 2 milliseconds) ensures immediate localized triggering of safety shut-offs before catastrophic failure occurs.
2. **Bandwidth Costs:** Streaming high-frequency raw vibration data (e.g., 10,000+ samples per second) continuously from hundreds of factory motors would overwhelm industrial networks and incur massive cloud ingress costs.
3. **Reliability:** Factory network connections can drop. Edge AI ensures the machine is continuously protected even if the Wi-Fi or cloud server goes offline.

**Q8: I see your code implements a rule where if the confidence score is below 0.75, it outputs "Uncertain" instead of raising an alarm. Why is this necessary?**

**Answer:** In an industrial setting, the cost of a "False Positive" is incredibly high. If the model falsely predicts a fault, it will trigger an unnecessary shutdown of the manufacturing line, costing thousands of dollars in lost production time. By setting a strict 75% confidence threshold, we force the system to require a high degree of certainty. If it is "Uncertain," it continues to monitor subsequent windows to establish a reliable trend before alerting technicians.

**Q9: If you had 6 more months to work on this, how would you migrate from this simulated CWRU data phase to a physical factory floor deployment?**

**Answer:** The next immediate step is Hardware-in-the-Loop integration. I would physically wire an ADXL345 3-axis accelerometer to the ESP32 via I2C or SPI and attach it to a real induction motor rig. I would port the Python `preprocess.py` (FFT and Kurtosis extraction) directly into C++ on the ESP32. We would then run the motor under healthy conditions, introduce physical imbalance (e.g., adding uneven weights to the rotor), and validate that the C-transpiled model correctly classifies the state changes in real-time.

**Q10: Why did you choose the CWRU dataset for this project?**

**Answer:** The Case Western Reserve University (CWRU) bearing dataset is the gold standard for bearing fault research because it provides high-frequency vibration data under controlled experimental conditions, specifically capturing the precise signatures of inner race, outer race, and ball defects. Since our goal was to demonstrate cutting-edge Edge AI techniques on limited hardware, using this standardized, publicly available dataset allowed us to validate our complex signal processing and quantization algorithms against a proven benchmark before attempting deployment on real-world, noisy industrial machinery.


**Q11: How to defend the 100% accuracy?**

**Answer:** As you can see, our Edge AI model achieved 100% accuracy across all fault categories. While 100% is rare in real-world messy data, it is expected here because we applied a robust signal processing pipeline (FFT and windowing) before feeding it to the model. By converting the raw time-series vibrations into frequency-domain statistical features like Spectral Entropy and Kurtosis, the boundaries between a healthy motor and a faulty bearing become highly separable. Furthermore, we achieved this 100% accuracy using an INT8 Quantized Neural Network that takes up less than 3 kilobytes of memory, proving that you do not need heavy cloud computing to achieve perfect diagnostic performance.


