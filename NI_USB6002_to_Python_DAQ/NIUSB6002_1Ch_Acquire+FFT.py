"""
NI USB-6002: live time plot + live FFT plot (Spyder)

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

# Frequency plot settings
FFT_REMOVE_DC = True     # subtract mean before FFT (usually helpful)
USE_HANN_WINDOW = True   # reduces leakage

TERM_CFG = TerminalConfiguration.RSE
# TERM_CFG = TerminalConfiguration.DIFF

SAVE_CSV_ON_EXIT = True
CSV_PATH = "ni_usb6002_live_capture.csv"


# -----------------------
# Buffers
# -----------------------
NFFT = int(FS_HZ * PLOT_WINDOW_S)        # FFT uses the rolling window length
if NFFT < 16:
    raise ValueError("PLOT_WINDOW_S too small for FFT / plotting.")

t_buf = deque(maxlen=NFFT)
y_buf = deque(maxlen=NFFT)

t_log = []
y_log = []


# -----------------------
# Plot setup
# -----------------------
plt.ion()
fig, (ax_t, ax_f) = plt.subplots(2, 1, figsize=(9, 6), constrained_layout=True)

# Time-domain line
(line_t,) = ax_t.plot([], [], lw=1)
ax_t.set_title(f"Live: {PHYS_CHAN} @ {FS_HZ:g} Hz")
ax_t.set_xlabel("Time (s)")
ax_t.set_ylabel("Voltage (V)")
ax_t.set_ylim(MIN_V, MAX_V)
ax_t.grid(True)

# Frequency-domain line
(line_f,) = ax_f.plot([], [], lw=1)
ax_f.set_xlabel("Frequency (Hz)")
ax_f.set_ylabel("FFT Magnitude (arb. V)")
ax_f.set_xlim(0.0, FS_HZ / 2.0)
ax_f.grid(True)

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

            # Update buffers + full log
            t_buf.extend(t_chunk)
            y_buf.extend(y_chunk)

            t_log.extend(t_chunk.tolist())
            y_log.extend(y_chunk.tolist())

            # ---- Time plot update ----
            t_arr = np.fromiter(t_buf, float)
            y_arr = np.fromiter(y_buf, float)

            line_t.set_data(t_arr, y_arr)
            if t_arr.size:
                ax_t.set_xlim(max(0.0, t_arr[-1] - PLOT_WINDOW_S), t_arr[-1])

            # ---- FFT update (only if we have a full window) ----
            if y_arr.size == NFFT:
                y_fft = y_arr.copy()

                if FFT_REMOVE_DC:
                    y_fft = y_fft - np.mean(y_fft)

                if USE_HANN_WINDOW:
                    w = np.hanning(NFFT)
                    y_fft = y_fft * w

                Y = np.fft.rfft(y_fft)
                f = np.fft.rfftfreq(NFFT, d=1.0 / FS_HZ)

                mag = np.abs(Y) / NFFT  # simple magnitude scaling

                # Apply f-limit
                fmax = FS_HZ / 2.0
                m = f <= fmax
                line_f.set_data(f[m], mag[m])

                # (Optional) set a fixed-ish y-limit for FFT so it doesn't autoscale jittery
                # Tune this number once you see typical magnitudes:
                ax_f.set_ylim(0.0, max(1e-6, np.max(mag[m]) * 1.2))

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