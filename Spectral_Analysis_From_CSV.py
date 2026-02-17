
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---- Choose your file ----
# Option A: type a filename in the same folder as this notebook
csv_path = 'PUT_YOUR_FILE_HERE.csv'

# Option B: use an absolute path
# csv_path = r'/full/path/to/your/file.csv'

csv_path = Path(csv_path)
assert csv_path.exists(), f'File not found: {csv_path.resolve()}'

df = pd.read_csv(csv_path)
print('Loaded:', csv_path.name)
print('Columns:', list(df.columns))
print(df.head())

# ---- Column mapping ----
# Preferred schema from the aligned DAQ notebooks:
TIME_COL = 'time_s'
SIG_COL  = 'ch0_V'

# If needed, map alternative column names here:
if SIG_COL not in df.columns:
    for alt in ['voltage_V', 'volts', 'V', 'signal']:
        if alt in df.columns:
            print(f"Using '{alt}' as signal column")
            SIG_COL = alt
            break

assert TIME_COL in df.columns, f"Missing time column '{TIME_COL}'. Found: {list(df.columns)}"
assert SIG_COL in df.columns,  f"Missing signal column '{SIG_COL}'. Found: {list(df.columns)}"

# Clean + extract arrays
x_t = df[TIME_COL].to_numpy(dtype=float)
x_v = df[SIG_COL].to_numpy(dtype=float)

# Basic sanity
assert len(x_t) == len(x_v) and len(x_t) > 10

# dt stats
dt = np.diff(x_t)
dt = dt[np.isfinite(dt)]

dt_med = float(np.median(dt))
fs_est = 1.0 / dt_med

jitter = float(np.std(dt) / dt_med) if dt_med > 0 else np.nan

print(f"Estimated sampling rate: {fs_est:.3f} Hz (median dt = {dt_med:.6g} s)")
print(f"Relative jitter (std(dt)/median(dt)): {jitter:.4f}")

# If time is not strictly increasing, sort it
if np.any(dt <= 0):
    print('Time is not strictly increasing — sorting by time.')
    order = np.argsort(x_t)
    x_t = x_t[order]
    x_v = x_v[order]

# %% Cell 8
plt.figure()
plt.plot(x_t, x_v)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title(f'Time domain: {csv_path.name}')
plt.grid(True)
plt.show()

# ---- FFT settings ----
remove_dc = True
use_hann_window = True

# Frequency-axis trustworthiness note:
# - NI USB-6002: time axis is hardware-clocked (very reliable)
# - Arduino: time axis depends on microcontroller timing + serial transport (may have jitter)

# Prepare signal
x = x_v.copy()
if remove_dc:
    x = x - np.mean(x)

N = len(x)
fs = float(fs_est)

if use_hann_window:
    w = np.hanning(N)
    xw = x * w
    coherent_gain = np.mean(w)
else:
    xw = x
    coherent_gain = 1.0

X = np.fft.rfft(xw)
freq = np.fft.rfftfreq(N, d=1/fs)

amp = (2.0 / (N * coherent_gain)) * np.abs(X)
amp[0] = amp[0] / 2.0  # DC

# Plot up to a reasonable max
f_max = min(500.0, fs/2)
mask = freq <= f_max

plt.figure()
plt.plot(freq[mask], amp[mask])
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (V)')
plt.title('Single-sided amplitude spectrum')
plt.grid(True)
plt.show()

# Simple peak-pick (ignores DC)
if len(freq) > 3:
    k0 = 1
    k_peak = k0 + int(np.argmax(amp[k0:]))
    print(f"Peak frequency: {freq[k_peak]:.3f} Hz (amplitude ~ {amp[k_peak]:.3g} V)")

