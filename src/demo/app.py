import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import os

st.set_page_config(page_title="Edge-AI PDM Monitor", layout="wide", page_icon="⚙️")

PROCESSED_DATA_PATH = "data/processed/features.csv"
TFLITE_MODEL_PATH = "models/edge_model.tflite"

@st.cache_resource
def load_model():
    interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
    interpreter.allocate_tensors()
    return interpreter

@st.cache_data
def load_data():
    if os.path.exists(PROCESSED_DATA_PATH):
        return pd.read_csv(PROCESSED_DATA_PATH)
    return pd.DataFrame()

interpreter = load_model()
df = load_data()

st.title("⚙️ Edge-AI Predictive Maintenance Dashboard")
st.markdown("Digital Twin Simulation of Edge TFLite Inferencing")

if df.empty:
    st.error("No telemetry data found. Please run the preprocessing script first.")
    st.stop()

if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar
st.sidebar.header("Control Panel")
simulate_btn = st.sidebar.button("Fetch Next Telemetry Window", use_container_width=True)

# Layout
col1, col2, col3 = st.columns([1, 1, 2])
target_labels = {0: "Normal", 1: "Ball Defect", 2: "Inner Race Fault", 3: "Outer Race Fault"}

if simulate_btn:
    with st.spinner("Extracting features from sensor window..."):
        time.sleep(0.5) # Simulate processing time
        
        # Pick a random sample from the dataset to simulate the edge streaming
        sample = df.sample(1).iloc[0]
        
        input_data = np.array([[
            sample["rms_vibration"], 
            sample["kurtosis"], 
            sample["spectral_entropy"], 
            sample["peak_frequency_hz"]
        ]], dtype=np.float32)
        
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaler.fit(df[["rms_vibration", "kurtosis", "spectral_entropy", "peak_frequency_hz"]])
        
        input_data_scaled = scaler.transform(input_data).astype(np.float32)

        # TFLite Inference
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], input_data_scaled)
        
        start_time = time.time()
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        end_time = time.time()
        
        pred_class_idx = int(np.argmax(output_data[0]))
        confidence = float(output_data[0][pred_class_idx])
        
        # Applies Behavioral Rule 
        alert_raised = False
        if confidence < 0.75:
            final_prediction = "Uncertain"
        else:
            final_prediction = target_labels.get(pred_class_idx, "Unknown")
            if final_prediction != "Normal":
                alert_raised = True
                
        inference_time_ms = (end_time - start_time) * 1000
        
        st.session_state.history.append({
            "RMS Vibration": float(sample['rms_vibration']),
            "Kurtosis": float(sample['kurtosis']),
            "Entropy": float(sample['spectral_entropy']),
            "Peak Freq": float(sample['peak_frequency_hz'])
        })
        if len(st.session_state.history) > 50:
            st.session_state.history.pop(0)
        
        with col1:
            st.subheader("Raw Telemetry")
            st.metric("RMS Vibration", f"{sample['rms_vibration']:.3f} g")
            st.metric("Kurtosis", f"{sample['kurtosis']:.1f}")
            st.metric("Entropy", f"{sample['spectral_entropy']:.2f}")
            st.metric("Peak Freq", f"{sample['peak_frequency_hz']:.1f} Hz")
            
        with col2:
            st.subheader("Edge Inference")
            st.metric("Inference Engine", "TensorFlow Lite INT8")
            st.metric("Latency", f"{inference_time_ms:.2f} ms")
            st.metric("Confidence Score", f"{confidence*100:.1f}%")
            
        with col3:
            st.subheader("System Status")
            if final_prediction == "Normal":
                st.success("✅ SYSTEM NOMINAL")
                st.info("No structural faults detected in recent window.")
            elif final_prediction == "Uncertain":
                st.warning("⚠️ UNCERTAIN CLASSIFICATION")
                st.info("Model confidence dropped below threshold. Continuing observation.")
            else:
                st.error(f"🚨 CRITICAL ALERT: {final_prediction}")
                st.markdown(f"**Action Required**: Inspect motor drive-end for {final_prediction.lower()}.")
                
        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📈 Telemetry Trend")
            history_df = pd.DataFrame(st.session_state.history)
            st.line_chart(history_df[["RMS Vibration", "Entropy"]])
            
        with col_chart2:
            st.subheader("📊 Confidence Distribution")
            prob_df = pd.DataFrame({
                "Condition": list(target_labels.values()),
                "Probability": output_data[0]
            })
            st.bar_chart(prob_df.set_index("Condition"))
            
else:
    st.info("👈 Click 'Fetch Next Telemetry Window' to simulate an edge device reading.")
    
st.divider()
st.caption("Developed for M.Tech in Applied AI and Communications VNIT by Kartik Burele | Edge AI Predictive Maintenance Project")
