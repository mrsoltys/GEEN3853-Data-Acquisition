import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
import subprocess
#import winsound #windows only

# =========================
# KNOBS (edit these)
# =========================
audio_path = "01 Army Of Me (1).mp3"   # mp3 or wav file

sample_start_s = 45.0                  # <-- WHERE in the song to start (seconds)
seconds_to_use = 12                    # <-- how many seconds to process/play from that start point

bits = 16                               # try: 16, 12, 8, 6, 4, 3
#16 bits is "CD quality". "What's a CD?!"

plot_window_ms = 500                   # snippet length to plot in milliseconds
plot_offset_s = 0.0                    # <-- where to start plotting within the loaded segment (seconds)

out_wav = "output_quantized.wav"       # output file name
# =========================

# -------------------------
# Load ONLY the desired segment (starting at sample_start_s)
# -------------------------
x, fs0 = librosa.load(audio_path, sr=None, mono=True, offset=sample_start_s, duration=seconds_to_use)
x = x.astype(np.float32)

print("Loaded:", audio_path)
print(f"Segment loaded: start={sample_start_s:.2f}s, duration={len(x)/fs0:.2f}s")

if len(x) == 0:
    raise SystemExit("Loaded segment is empty. Try a smaller sample_start_s.")

# Normalize to avoid clipping (keeps comparisons consistent)
peak = np.max(np.abs(x))
if peak > 0:
    x = (0.95 * x / peak).astype(np.float32)

# -------------------------
# Quantize (simulate lower resolution / bit depth)
# -------------------------
if bits >= 16:
    xq = x.copy()
else:
    max_int = (2 ** (bits - 1)) - 1
    xi = np.round(np.clip(x, -1.0, 1.0) * max_int).astype(np.int32)
    xq = (xi / max_int).astype(np.float32)

# -------------------------
# Plot a short snippet: original vs quantized
# (within the loaded segment)
# -------------------------
total_duration_s = len(x) / fs0

# Clamp plot_offset_s so students can't crash it
if plot_offset_s < 0:
    plot_offset_s = 0
if plot_offset_s > total_duration_s:
    plot_offset_s = max(0, total_duration_s - 0.1)

start_i = int(plot_offset_s * fs0)
N = int((plot_window_ms / 1000) * fs0)

seg = x[start_i:start_i + N]
seg_q = xq[start_i:start_i + N]

t_ms = (np.arange(len(seg)) / fs0) * 1000

plt.figure(figsize=(10, 5))
plt.plot(t_ms, seg, label="Original", linewidth=1.5)
plt.step(t_ms, seg_q, where="mid", label=f"Quantized ({bits}-bit)", linewidth=2)

# Draw quantization bins for small bit depths so the "levels" are obvious
if bits <= 6:
    levels = np.linspace(-1, 1, 2**bits)
    for lv in levels:
        plt.axhline(lv, linewidth=0.6, alpha=0.25)

plt.title(f"Snippet from {sample_start_s:.2f}s (showing {plot_window_ms} ms)")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude (normalized)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# -------------------------
# Save ONE output file and play it
# (This will now start at sample_start_s in the original song)
# -------------------------
sf.write(out_wav, xq, fs0)
print(f"\nWrote {out_wav} with simulated resolution = {bits}-bit.")
print(f"Playback is the {seconds_to_use}s segment starting at {sample_start_s}s.")
print("Playing...")
subprocess.run(["afplay", out_wav], check=True)#Mac Only
#winsound.PlaySound(out_wav,winsound.SND_FILENAME) #Windows Only
