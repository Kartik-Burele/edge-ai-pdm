import numpy as np
import matplotlib.pyplot as plt
import os

# Create realistic simulated vibration data for visualization
fs = 12000  # Sampling frequency 12kHz
t = np.linspace(0, 1024/fs, 1024, endpoint=False) # 1024 sample window

# 1. Normal Motor (Base running frequency ~60Hz + smooth noise)
normal_signal = 0.5 * np.sin(2 * np.pi * 60 * t) + np.random.normal(0, 0.1, len(t))

# 2. Bearing Fault (Base 60Hz + high frequency impacts/ringing from bearing defects)
fault_signal = 0.5 * np.sin(2 * np.pi * 60 * t) + np.random.normal(0, 0.2, len(t))
# Add periodic impacts (spikes) simulating rolling elements hitting a crack
impact_freq = 150 # Hz
for i in range(0, 1024, int(fs/impact_freq)):
    if i < 1024:
        fault_signal[i:i+20] += np.exp(-np.linspace(0, 5, min(20, 1024-i))) * 3.0 * np.sin(2 * np.pi * 2000 * t[0:min(20, 1024-i)])

# Perform FFT
def compute_fft(signal, fs):
    n = len(signal)
    fft_vals = np.fft.fft(signal)
    fft_mag = np.abs(fft_vals) * 2.0 / n
    freqs = np.fft.fftfreq(n, 1/fs)
    # Return only positive frequencies
    return freqs[:n//2], fft_mag[:n//2]

freqs_norm, fft_norm = compute_fft(normal_signal, fs)
freqs_fault, fft_fault = compute_fft(fault_signal, fs)

# Plotting
plt.style.use('dark_background')
fig, axs = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle('Signal Processing Pipeline: Time Domain vs. Frequency Domain (FFT)', fontsize=18, fontweight='bold', color='white')

# Normal Time Domain
axs[0, 0].plot(t*1000, normal_signal, color='#00ff00', linewidth=1)
axs[0, 0].set_title('Normal Operation (Time Domain)', fontsize=14)
axs[0, 0].set_xlabel('Time (ms)')
axs[0, 0].set_ylabel('Amplitude (g)')
axs[0, 0].grid(True, alpha=0.2)
axs[0, 0].set_ylim([-4, 4])

# Normal Frequency Domain
axs[0, 1].plot(freqs_norm, fft_norm, color='#00ff00', linewidth=1.5)
axs[0, 1].set_title('Normal Operation (FFT)', fontsize=14)
axs[0, 1].set_xlabel('Frequency (Hz)')
axs[0, 1].set_ylabel('Magnitude')
axs[0, 1].grid(True, alpha=0.2)
axs[0, 1].set_xlim([0, 3000])
axs[0, 1].set_ylim([0, 0.6])

# Fault Time Domain
axs[1, 0].plot(t*1000, fault_signal, color='#ff3333', linewidth=1)
axs[1, 0].set_title('Bearing Fault (Time Domain) - Notice Impacts', fontsize=14)
axs[1, 0].set_xlabel('Time (ms)')
axs[1, 0].set_ylabel('Amplitude (g)')
axs[1, 0].grid(True, alpha=0.2)
axs[1, 0].set_ylim([-4, 4])

# Fault Frequency Domain
axs[1, 1].plot(freqs_fault, fft_fault, color='#ff3333', linewidth=1.5)
axs[1, 1].set_title('Bearing Fault (FFT) - Notice High Frequency Harmonics', fontsize=14)
axs[1, 1].set_xlabel('Frequency (Hz)')
axs[1, 1].set_ylabel('Magnitude')
axs[1, 1].grid(True, alpha=0.2)
axs[1, 1].set_xlim([0, 3000])
axs[1, 1].set_ylim([0, 0.6])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('fft_visualization.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
print("Saved highly-impactful visualization to fft_visualization.png!")
