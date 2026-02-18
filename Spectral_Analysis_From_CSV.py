
# ---- FFT settings ----
remove_dc = True
use_hann_window = True

min_freq = 0.5        # <-- ignore frequencies below this (Hz)
n_peaks = 5           # <-- how many peaks to report

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
amp[0] = amp[0] / 2.0  # DC correction

# ---- Ignore low frequencies ----
mask = (freq >= min_freq) & (freq <= fs/2)

freq_plot = freq[mask]
amp_plot = amp[mask]

# ---- Plot ----
plt.figure()
plt.plot(freq_plot, amp_plot)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (V)')
plt.title('Single-sided amplitude spectrum (filtered)')
plt.grid(True)
plt.show()

# ---- Find top peaks ----
if len(freq_plot) > 3:
    idx_sorted = np.argsort(amp_plot)[::-1]  # descending order
    top_idx = idx_sorted[:n_peaks]

    print(f"\nTop {n_peaks} frequency peaks (above {min_freq} Hz):")
    for i in top_idx:
        print(f"  {freq_plot[i]:8.3f} Hz   amplitude ~ {amp_plot[i]:.4g} V")
