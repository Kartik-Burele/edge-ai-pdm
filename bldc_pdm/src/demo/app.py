import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import os
from sklearn.preprocessing import StandardScaler

# Ensure the Streamlit page is fully styled and responsive
st.set_page_config(
    page_title="BLDC Edge-AI Digital Twin",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Compute paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLDC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

PROCESSED_DATA_PATH = os.path.join(BLDC_DIR, "data", "processed", "features.csv")
TFLITE_MODEL_PATH = os.path.join(BLDC_DIR, "models", "edge_model.tflite")

# Inject highly premium dark-mode styling with glassmorphism and glowing neon accents
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Outfit:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0d0f19 0%, #151a30 100%);
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header & Branding */
    .title-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #00f2fe;
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        margin-bottom: 0.1rem;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
    }
    
    /* Neon Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 242, 254, 0.6);
        box-shadow: 0 8px 32px 0 rgba(0, 242, 254, 0.15);
    }
    
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-unit {
        font-size: 0.9rem;
        color: #00f2fe;
        margin-left: 0.3rem;
    }
    
    /* Glowing Beacon Status */
    .beacon-container {
        display: flex;
        align-items: center;
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 12px;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .beacon {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        margin-right: 12px;
        display: inline-block;
    }
    .beacon.nominal {
        background-color: #00f2fe;
        box-shadow: 0 0 15px #00f2fe, 0 0 30px #00f2fe;
        animation: pulse-cyan 1.5s infinite;
    }
    .beacon.warning {
        background-color: #ff9f43;
        box-shadow: 0 0 15px #ff9f43, 0 0 30px #ff9f43;
        animation: pulse-orange 1.5s infinite;
    }
    .beacon.critical {
        background-color: #ff4757;
        box-shadow: 0 0 15px #ff4757, 0 0 30px #ff4757;
        animation: pulse-red 1.5s infinite;
    }
    
    @keyframes pulse-cyan {
        0% { transform: scale(0.9); opacity: 0.6; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.6; }
    }
    @keyframes pulse-orange {
        0% { transform: scale(0.9); opacity: 0.6; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.6; }
    }
    @keyframes pulse-red {
        0% { transform: scale(0.9); opacity: 0.6; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.6; }
    }
</style>
""", unsafe_allow_html=True)

# Load TFLite Model
@st.cache_resource
def load_tflite_model():
    if not os.path.exists(TFLITE_MODEL_PATH):
        return None
    interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
    interpreter.allocate_tensors()
    return interpreter

# Load features.csv
@st.cache_data
def load_telemetry_data():
    if os.path.exists(PROCESSED_DATA_PATH):
        return pd.read_csv(PROCESSED_DATA_PATH)
    return pd.DataFrame()

interpreter = load_tflite_model()
df = load_telemetry_data()

# Header Branding
st.markdown('<div class="title-text">⚡ BLDC MOTOR DIGITAL TWIN</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Edge-AI Predictive Maintenance Monitor &bull; VNIT Evaluation Phase</div>', unsafe_allow_html=True)

if df.empty:
    st.error("❌ Processed features not found. Please run the preprocessing pipeline first.")
    st.stop()

if interpreter is None:
    st.error("❌ Quantized TFLite edge model not found. Please run the TFLite training script first.")
    st.stop()

# Initialize history session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar panel
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h2 style='font-family: Orbitron, sans-serif; color: #00f2fe; font-size: 1.3rem;'>CONTROL STATION</h2>
</div>
""", unsafe_allow_html=True)

simulate_btn = st.sidebar.button("⚡ FETCH TELEMETRY WINDOW", use_container_width=True)
selected_class_filter = st.sidebar.selectbox("Filter Source State", ["All States", "Healthy", "Mechanical Damage", "Electrical Damage", "Mech_Elec_Damage"])

# Filter dataframe based on state if requested
if selected_class_filter != "All States":
    filtered_df = df[df['condition'] == selected_class_filter]
else:
    filtered_df = df

if filtered_df.empty:
    st.sidebar.warning(f"No records found for {selected_class_filter}")
    filtered_df = df

# Set up class label mapping consistent with training
target_labels = {
    0: "Healthy", 
    1: "Mechanical Damage", 
    2: "Electrical Damage", 
    3: "Mech_Elec_Damage"
}

# Main Layout
col_telemetry, col_edge, col_status = st.columns([1, 1, 2])

if simulate_btn:
    with st.spinner("Decoding high-frequency telemetry window..."):
        time.sleep(0.3)  # Emulate real-world FFT computation delay
        
        # Pull a random sample from the filtered dataframe
        sample = filtered_df.sample(1).iloc[0]
        
        # Fit standard scaler parameters to normalize input (same as training pipeline)
        feature_cols = [
            "rms_current", 
            "kurtosis_current", 
            "mean_speed", 
            "std_speed", 
            "spectral_entropy_current", 
            "peak_frequency_current"
        ]
        
        input_data = np.array([[sample[col] for col in feature_cols]], dtype=np.float32)
        
        scaler = StandardScaler()
        scaler.fit(df[feature_cols])
        input_scaled = scaler.transform(input_data).astype(np.float32)
        
        # Run TFLite inference
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        interpreter.set_tensor(input_details[0]['index'], input_scaled)
        
        start_time = time.time()
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        end_time = time.time()
        
        pred_class_idx = int(np.argmax(output_data[0]))
        confidence = float(output_data[0][pred_class_idx])
        latency_ms = (end_time - start_time) * 1000
        
        # Apply strict behavioral rule: thresholding (<0.75 flags Uncertain)
        if confidence < 0.75:
            final_prediction = "Uncertain"
            alert_level = "WARNING"
            beacon_class = "warning"
        else:
            final_prediction = target_labels.get(pred_class_idx, "Unknown")
            if final_prediction == "Healthy":
                alert_level = "NOMINAL"
                beacon_class = "nominal"
            else:
                alert_level = "CRITICAL"
                beacon_class = "critical"
                
        # Append to telemetry trend history
        st.session_state.history.append({
            "RMS Current (A)": float(sample['rms_current']),
            "Rotational Speed (RPM)": float(sample['mean_speed']),
            "Current Entropy": float(sample['spectral_entropy_current']),
            "Speed Ripple (Std)": float(sample['std_speed'])
        })
        if len(st.session_state.history) > 40:
            st.session_state.history.pop(0)
            
        # Telemetry Display Column
        with col_telemetry:
            st.markdown('<h3 style="font-family: Orbitron; font-size: 1.1rem; border-bottom: 2px solid rgba(0,242,254,0.2); padding-bottom: 0.5rem; color:#00f2fe;">🛰️ Telemetry Frame</h3>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">RMS Current</div>
                <div class="metric-value">{sample['rms_current']:.3f}<span class="metric-unit">A</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Mean Rotor Speed</div>
                <div class="metric-value">{sample['mean_speed']:.1f}<span class="metric-unit">RPM</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Current Kurtosis</div>
                <div class="metric-value">{sample['kurtosis_current']:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Current Entropy</div>
                <div class="metric-value">{sample['spectral_entropy_current']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Edge Inference Column
        with col_edge:
            st.markdown('<h3 style="font-family: Orbitron; font-size: 1.1rem; border-bottom: 2px solid rgba(0,242,254,0.2); padding-bottom: 0.5rem; color:#00f2fe;">🧠 Edge Processor</h3>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="border-color: rgba(162, 89, 255, 0.3);">
                <div class="metric-label" style="color: #a259ff;">Inference Core</div>
                <div class="metric-value" style="font-size: 1.5rem; color: #a259ff;">TFLite INT8</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Edge Latency</div>
                <div class="metric-value">{latency_ms:.3f}<span class="metric-unit">ms</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Confidence Score</div>
                <div class="metric-value">{(confidence*100):.1f}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Calculated Ripple</div>
                <div class="metric-value">{sample['std_speed']:.1f}<span class="metric-unit">RPM</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        # Diagnostic & Decision Twin Column
        with col_status:
            st.markdown('<h3 style="font-family: Orbitron; font-size: 1.1rem; border-bottom: 2px solid rgba(0,242,254,0.2); padding-bottom: 0.5rem; color:#00f2fe;">🚨 Diagnostic Twin Status</h3>', unsafe_allow_html=True)
            
            # Glowing beacon status box
            st.markdown(f"""
            <div class="beacon-container">
                <div class="beacon {beacon_class}"></div>
                <div style="font-family: Orbitron; font-weight:700; font-size: 1.2rem; color: #ffffff;">SYSTEM STATUS: {alert_level}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            if final_prediction == "Healthy":
                st.success("✅ MOTOR NOMINAL")
                st.info("BLDC running under perfect balance and clean current inputs. Magnet flux densities are healthy.")
            elif final_prediction == "Uncertain":
                st.warning("⚠️ UNCERTAIN CLASSIFICATION")
                st.info("The classification confidence score is below the 75% threshold. Postponing automatic trigger to prevent false alerts. Maintaining active continuous telemetry inspection.")
            elif final_prediction == "Mechanical Damage":
                st.error("🚨 ALERT: MECHANICAL DAMAGE DETECTED")
                st.markdown("**Fault Type**: Mechanical asymmetry (Ziptie simulator load).")
                st.markdown("**Action Plan**: Check shaft load, coupling alignment, and rotor physical structure immediately.")
            elif final_prediction == "Electrical Damage":
                st.error("🚨 ALERT: ELECTRICAL DAMAGE DETECTED")
                st.markdown("**Fault Type**: Stator/Phase imbalance or degraded magnets.")
                st.markdown("**Action Plan**: Perform windings electrical diagnostic and monitor current inputs immediately.")
            elif final_prediction == "Mech_Elec_Damage":
                st.error("🚨 CRITICAL: MULTI-FAULT STATE DETECTED")
                st.markdown("**Fault Type**: Combined Mechanical asymmetry and Degraded Magnets.")
                st.markdown("**Action Plan**: High priority stator inspection and mechanical shaft balance check required immediately.")
                
        # Trend and probability charts
        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📈 Telemetry Trend (Recent Windows)")
            history_df = pd.DataFrame(st.session_state.history)
            st.line_chart(history_df[["RMS Current (A)", "Current Entropy"]])
            
        with col_chart2:
            st.subheader("📊 Softmax Probability Distribution")
            prob_df = pd.DataFrame({
                "Condition": list(target_labels.values()),
                "Probability": output_data[0]
            })
            st.bar_chart(prob_df.set_index("Condition"))

else:
    # Initial guidance view
    st.info("👈 Click '⚡ FETCH TELEMETRY WINDOW' in the control panel to stream real-time BLDC motor frame inferencing.")
    
    # Render static indicators of model parameters
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-label">Input Shape</div>
            <div class="metric-value" style="color: #00f2fe;">6 Features</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-label">Output Classes</div>
            <div class="metric-value" style="color: #00f2fe;">4 States</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-label">Model Size</div>
            <div class="metric-value" style="color: #00f2fe;">3.08 KB</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("M.Tech in Applied AI and Communications VNIT | Edge AI Predictive Maintenance Project for BLDC Motors (Kartik Burele)")
