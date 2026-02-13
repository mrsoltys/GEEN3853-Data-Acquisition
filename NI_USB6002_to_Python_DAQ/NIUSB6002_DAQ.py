"""
NI USB-6002 single-channel live plot + optional CSV save (no Jupyter needed)

Run:
  python ni_usb6002_live_plot.py

Stop:
  Ctrl+C  (then it will optionally save to CSV)
"""

import time
from collections import deque

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType


# -----------------------
# SETTINGS (edit these)
# -----------------------
DEVICE = "Dev1"          # NI MAX shows this (often "Dev1")
CHANNEL = "ai0"          # ai0 ... ai7 on USB-6002
PHYS_CHAN = f"{DEVICE}/{CHANNEL}"

FS_HZ = 1000.0           # sample rate (Hz)
CHUNK_SAMPLES = 200      # read this many samples each loop
PLOT_WINDOW_S = 5.0      # show last N seconds on the plot

MIN_V = -10.0
MAX_V = 10.0

# Choose ONE terminal configuration
# TERM_CFG = TerminalConfiguration.RSE
TERM_CFG = TerminalConfiguration.DIFFERENTIAL

SAVE_CSV_ON_EXIT = True
CSV_PATH = "ni_usb6002_live_capture.csv"


def main():
    # Rolling buffers for live display
    maxlen = int(FS_HZ * PLOT_WINDOW_S)
    t_buf = deque(maxlen=maxlen)
    y_buf = deque(maxlen=maxlen)

    # Full log buffers for saving
    t_log = []
    y_log = []

    # Plot setup (works well in Spyder / normal Python)
    plt.ion()
    fig, ax = plt.subplots()
    (line,) = ax.plot([], [], lw=1)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title(f"Live: {PHYS_CHAN} @ {FS_HZ:g} Hz")
    ax.grid(True)

    t0 = time.perf_counter()
    sample_index = 0

    with nidaqmx.Task() as task:
        # Configure AI channel
        task.ai_channels.add_ai_voltage_chan(
            PHYS_CHAN,
            min_val=MIN_V,
            max_val=MAX_V,
            terminal_config=TERM_CFG,
        )

        # Configure timing (continuous)
        task.timing.cfg_samp_clk_timing(
            rate=FS_HZ,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=CHUNK_SAMPLES,
        )

        # Start task
        task.start()
        print("Streaming... press Ctrl+C to stop.")

        try:
            while True:
                # Read a chunk (single channel -> list length CHUNK_SAMPLES)
                y_chunk = task.read(
                    number_of_samples_per_channel=CHUNK_SAMPLES,
                    timeout=2.0,
                )
                y_chunk = np.asarray(y_chunk, dtype=float)

                # Generate time stamps based on sample count
                i = np.arange(sample_index, sample_index + CHUNK_SAMPLES)
                t_chunk = i / FS_HZ
                sample_index += CHUNK_SAMPLES

                # Append to rolling buffers
                t_buf.extend(t_chunk)
                y_buf.extend(y_chunk)

                # Append to full log buffers
                t_log.extend(t_chunk.tolist())
                y_log.extend(y_chunk.tolist())

                # Update plot (last PLOT_WINDOW_S seconds)
                line.set_data(np.fromiter(t_buf, float), np.fromiter(y_buf, float))
                ax.set_xlim(max(0.0, t_chunk[-1] - PLOT_WINDOW_S), t_chunk[-1])

                # Auto-scale Y softly based on current window
                y_arr = np.fromiter(y_buf, float)
                if y_arr.size:
                    y_min = float(np.min(y_arr))
                    y_max = float(np.max(y_arr))
                    if y_min == y_max:
                        y_min -= 0.5
                        y_max += 0.5
                    pad = 0.05 * (y_max - y_min)
                    ax.set_ylim(y_min - pad, y_max + pad)

                fig.canvas.draw_idle()
                plt.pause(0.001)  # yields to GUI event loop (important)

        except KeyboardInterrupt:
            print("\nStopped.")

        finally:
            # Stop task cleanly
            try:
                task.stop()
            except Exception:
                pass

    # Optional CSV save
    if SAVE_CSV_ON_EXIT and len(t_log) > 0:
        df = pd.DataFrame({"t_s": t_log, "V": y_log})
        df.to_csv(CSV_PATH, index=False)
        print(f"Saved {len(df)} samples to: {CSV_PATH}")

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
