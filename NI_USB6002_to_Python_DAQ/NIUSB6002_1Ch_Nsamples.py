"""
NI USB-6002 single-channel capture (Spyder)

This script:
1. Collects N samples at a specified sample rate
2. Saves the data to a timestamped CSV file
3. Plots the data after acquisition
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType


# -----------------------
# SETTINGS
# -----------------------
DEVICE = "Dev1"
CHANNEL = "ai0"
PHYS_CHAN = f"{DEVICE}/{CHANNEL}"

FS_HZ = 500.0          # Sampling frequency (Hz)
N_SAMPLES = 100        # Total number of samples to collect

MIN_V = 0.0
MAX_V = 5.0

TERM_CFG = TerminalConfiguration.RSE
# TERM_CFG = TerminalConfiguration.DIFF


# -----------------------
# ACQUIRE DATA
# -----------------------
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(
        PHYS_CHAN,
        min_val=MIN_V,
        max_val=MAX_V,
        terminal_config=TERM_CFG,
    )

    task.timing.cfg_samp_clk_timing(
        rate=FS_HZ,
        sample_mode=AcquisitionType.FINITE,
        samps_per_chan=N_SAMPLES,
    )

    print(f"Collecting {N_SAMPLES} samples from {PHYS_CHAN} at {FS_HZ} Hz...")

    y = task.read(
        number_of_samples_per_channel=N_SAMPLES,
        timeout=5.0,
    )

print("Acquisition complete.")


# -----------------------
# BUILD TIME ARRAY
# -----------------------
y = np.asarray(y, dtype=float)
t = np.arange(N_SAMPLES) / FS_HZ


# -----------------------
# SAVE CSV
# -----------------------
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
CSV_PATH = f"light_sensor_capture_{timestamp}.csv"

df = pd.DataFrame({
    "t_s": t,
    "V": y,
})

df.to_csv(CSV_PATH, index=False)
print(f"Saved data to: {CSV_PATH}")


# -----------------------
# PLOT DATA
# -----------------------
plt.figure()
plt.plot(t, y)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title(f"{PHYS_CHAN}: {N_SAMPLES} samples at {FS_HZ:g} Hz")
plt.grid(True)
plt.show()