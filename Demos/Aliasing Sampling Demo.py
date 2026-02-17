import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import subprocess

# =========================
# KNOBS
# =========================
f0 = 440.0               # True sine frequency (Hz)
duration_s = 2         # seconds to generate/play

fs_play = 44100          # High-rate playback/sample grid for plotting + audio
fs_sample = 1000          # Sampling rate to test (try: 800, 801, 880, 1000, 2000)

plot_window_ms = 40      # plot window (10–50 ms)
A = 0.9                  # amplitude (<1)

wav_true = "tone_true.wav"
wav_linear = "tone_linear.wav"
wav_alias = "tone_alias.wav"
# =========================

print("True frequency f0:", f0, "Hz")
print("Sampling rate fs_sample:", fs_sample, "Hz")
print("Playback rate fs_play:", fs_play, "Hz")
print("Nyquist =", fs_sample / 2, "Hz")

# ------------------------------------------------------------
# 1) "True" tone at high playback rate
# ------------------------------------------------------------
t_play = np.arange(int(duration_s * fs_play)) / fs_play
x_true = (A * np.sin(2 * np.pi * f0 * t_play)).astype(np.float32)

# ------------------------------------------------------------
# 2) Sample the true tone at fs_sample (include endpoint)
# ------------------------------------------------------------
t_s = np.arange(int(duration_s * fs_sample) + 1) / fs_sample
x_s = (A * np.sin(2 * np.pi * f0 * t_s)).astype(np.float32)

# ------------------------------------------------------------
# 3) Linear reconstruction back onto high-rate grid (connect dots)
# ------------------------------------------------------------
x_linear = np.interp(t_play, t_s, x_s).astype(np.float32)

# ------------------------------------------------------------
# 4) Predict alias frequency
#    Alias frequency is the folded frequency that best matches the samples.
# ------------------------------------------------------------
k = int(np.round(f0 / fs_sample))
f_alias = abs(f0 - k * fs_sample)
if f_alias > fs_sample / 2:
    f_alias = fs_sample - f_alias

print("\nPredicted alias frequency ≈", f_alias, "Hz")

# ------------------------------------------------------------
# 5) Build an "alias sine" that matches the sampled points
#    We'll pick a phase (and sign) that best matches x_s.
#    (This is not "resampling"; it's a best-fit sine at the predicted alias frequency.)
# ------------------------------------------------------------
omega = 2 * np.pi * f_alias

# Solve least-squares for x_s ≈ a*sin(ωt) + b*cos(ωt)
S = np.sin(omega * t_s)
C = np.cos(omega * t_s)
M = np.column_stack([S, C])
coef, _, _, _ = np.linalg.lstsq(M, x_s, rcond=None)
a, b = coef

# Convert a*sin + b*cos to amplitude+phase form: R*sin(ωt + phi)
R = np.sqrt(a*a + b*b)
phi = np.arctan2(b, a)

# Create alias sine at high playback rate (use fitted amplitude R, phase phi)
x_alias = (R * np.sin(omega * t_play + phi)).astype(np.float32)

# ------------------------------------------------------------
# 6) PLOT FIRST: True sine, Linear reconstruction, Alias sine + sample points
# ------------------------------------------------------------
N_plot = int((plot_window_ms / 1000) * fs_play)
t_win = t_play[:N_plot]
x_true_win = x_true[:N_plot]
x_linear_win = x_linear[:N_plot]
x_alias_win = x_alias[:N_plot]

# Sample points inside plot window
N_samp_win = int((plot_window_ms / 1000) * fs_sample) + 1
t_s_win = t_s[:N_samp_win]
x_s_win = x_s[:N_samp_win]

t_win_ms = t_win * 1000
t_s_ms = t_s_win * 1000

plt.figure(figsize=(11, 6))
plt.plot(t_win_ms, x_true_win, linewidth=2, label=f"Actual signal: {f0:.1f} Hz sine")
plt.scatter(t_s_ms, x_s_win, s=55, label="Sample points")
plt.plot(t_win_ms, x_linear_win, linewidth=2, linestyle="--", label="Linear reconstruction (connect-the-dots)")
plt.plot(t_win_ms, x_alias_win, linewidth=2, linestyle=":", label=f"Predicted aliased sine: {f_alias:.1f} Hz")

plt.title(f"Sampling {f0:.1f} Hz at fs = {fs_sample} Hz (Nyquist = {fs_sample/2:.1f} Hz)")
plt.xlabel("Time (ms)")
plt.ylabel("Amplitude")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 7) WRITE WAVs and PLAY: True → Linear → Alias
# ------------------------------------------------------------
sf.write(wav_true, x_true, fs_play)
sf.write(wav_linear, x_linear, fs_play)
sf.write(wav_alias, x_alias, fs_play)

print("\nPlaying TRUE tone (clean)...")
subprocess.run(["afplay", wav_true], check=True)

print("Playing LINEAR reconstruction tone (peaky/polygon-ish at low fs)...")
subprocess.run(["afplay", wav_linear], check=True)

print("Playing ALIAS sine tone (predicted pitch)...")
subprocess.run(["afplay", wav_alias], check=True)

print("\nFiles written:")
print(" -", wav_true)
print(" -", wav_linear)
print(" -", wav_alias)
print("\nAlias fit details:")
print("  fitted amplitude R =", float(R))
print("  fitted phase phi (rad) =", float(phi))
