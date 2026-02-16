"""
NI USB-6002 single-channel live plot (Spyder)

Stop with Ctrl+C
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import deque

import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType


# -----------------------
# SETTINGS
# -----------------------
DEVICE = "Dev1"
CHANNEL = "ai0"
PHYS_CHAN = f"{DEVICE}/{CHANNEL}"

FS_HZ = 1000.0
CHUNK_SAMPLES = 200
PLOT_WINDOW_S = 5.0

MIN_V = 0.0
MAX_V = 5.0

TERM_CFG = TerminalConfiguration.RSE
# TERM_CFG = TerminalConfiguration.DIFF

SAVE_CSV_ON_EXIT = True
CSV_PATH = "ni_usb6002_live_capture.csv"

# -----------------------
# Buffers
# -----------------------
maxlen = int(FS_HZ * PLOT_WINDOW_S)
t_buf = deque(maxlen=maxlen)
y_buf = deque(maxlen=maxlen)

t_log = []
y_log = []

# -----------------------
# Plot setup
# -----------------------
plt.ion()
fig, ax = plt.subplots()
(line,) = ax.plot([], [], lw=1)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_title(f"Live: {PHYS_CHAN} @ {FS_HZ:g} Hz")
ax.set_ylim(MIN_V, MAX_V)
ax.grid(True)

plt.show(block=False)

# -----------------------
# DAQ Loop
# -----------------------
sample_index = 0

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(
        PHYS_CHAN,
        min_val=MIN_V,
        max_val=MAX_V,
        terminal_config=TERM_CFG,
    )

    task.timing.cfg_samp_clk_timing(
        rate=FS_HZ,
        sample_mode=AcquisitionType.CONTINUOUS,
        samps_per_chan=CHUNK_SAMPLES,
    )

    task.start()
    print("Streaming... press Ctrl+C to stop.")

    try:
        while True:
            y_chunk = task.read(
                number_of_samples_per_channel=CHUNK_SAMPLES,
                timeout=2.0,
            )
            y_chunk = np.asarray(y_chunk, dtype=float)

            i = np.arange(sample_index, sample_index + CHUNK_SAMPLES)
            t_chunk = i / FS_HZ
            sample_index += CHUNK_SAMPLES

            t_buf.extend(t_chunk)
            y_buf.extend(y_chunk)

            t_log.extend(t_chunk.tolist())
            y_log.extend(y_chunk.tolist())

            # Update plot
            t_arr = np.fromiter(t_buf, float)
            y_arr = np.fromiter(y_buf, float)

            line.set_data(t_arr, y_arr)
            ax.set_xlim(max(0.0, t_chunk[-1] - PLOT_WINDOW_S), t_chunk[-1])

            fig.canvas.draw_idle()
            plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        try:
            task.stop()
        except Exception:
            pass

# -----------------------
# Save CSV
# -----------------------
if SAVE_CSV_ON_EXIT and len(t_log) > 0:
    df = pd.DataFrame({"t_s": t_log, "V": y_log})
    df.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(df)} samples to: {CSV_PATH}")

plt.ioff()
plt.show()