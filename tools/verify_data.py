import scipy.io
import os

# Define paths relative to the project root
RAW_DATA_PATH = "data/raw/cwru"
EXPECTED_FILES = ["b007_0_1797.mat", "ir_0_1797.mat", "nbd_0_1797.mat", "or007_0_1797@6.mat"]

def verify_handshake():
    print("🚀 Initializing Phase 2: Link Verification...")
    
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Error: Directory '{RAW_DATA_PATH}' not found.")
        return

    for file_name in EXPECTED_FILES:
        file_path = os.path.join(RAW_DATA_PATH, file_name)
        if os.path.exists(file_path):
            try:
                # Load the .mat file (The Handshake)
                mat_data = scipy.io.loadmat(file_path)
                
                # Filter out metadata to find the vibration data keys
                data_keys = [k for k in mat_data.keys() if not k.startswith('__')]
                
                print(f"✅ Linked: {file_name}")
                print(f"   Internal Keys: {data_keys}")
                
            except Exception as e:
                print(f"❌ Error reading {file_name}: {e}")
        else:
            print(f"⚠️ Warning: Missing {file_name}. Ensure it is downloaded to {RAW_DATA_PATH}.")

if __name__ == "__main__":
    verify_handshake()