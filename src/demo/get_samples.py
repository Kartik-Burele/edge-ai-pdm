import csv

with open('data/processed/features.csv', 'r') as f:
    reader = csv.DictReader(f)
    samples = {}
    for row in reader:
        c = row['condition']
        if c not in samples:
            samples[c] = row
            
for c, vals in samples.items():
    print(f"// {c}")
    print(f"{{{vals['rms_vibration']}, {vals['kurtosis']}, {vals['spectral_entropy']}, {vals['peak_frequency_hz']}}},")
