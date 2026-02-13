# NI USB-6002 → Python DAQ (Spyder)

This folder contains simple Python scripts for:

-   ✅ Live time-domain plotting\
-   ✅ Live time + FFT plotting\
-   ✅ Optional CSV export\

These scripts are designed to run in **Spyder** using **Anaconda**.

------------------------------------------------------------------------
# 🚀 Workflow

## 1️⃣ Launch Spyder

1.  Open **Anaconda Navigator**
2.  Launch **Spyder**

------------------------------------------------------------------------

## 2️⃣ Configure Spyder Plot Settings (IMPORTANT)

To enable real-time updating plots:

1.  Go to\
    **Tools → Preferences**
2.  Select\
    **IPython Console**
3.  Click the **Plotting** tab
4.  Set:

```{=html}
<!-- -->
```
    Backend: Automatic

⚠️ Do NOT use **Inline**.\
Inline plots will not update in real time.

Click **Apply → OK**.

------------------------------------------------------------------------

## 3️⃣ Open the Script

You can either:

-   Download the script from GitHub and open it in Spyder\
-   Or copy/paste the script directly into a new `.py` file

------------------------------------------------------------------------

## 4️⃣ Edit Settings (Top of Script)

At the top of the file, verify:

``` python
DEVICE = "Dev1"
CHANNEL = "ai0"
```

### 🔎 Checking Your Device Name

The scripts default to:

    Dev1

If your device has a different name:

1.  Open **NI MAX (NI Measurement & Automation Explorer)**
2.  Expand **Devices and Interfaces**
3.  Check the name assigned to your USB-6002
4.  Update the script accordingly:

``` python
DEVICE = "YourDeviceName"
```

You may also adjust:

``` python
FS_HZ = 1000.0
PLOT_WINDOW_S = 5.0
```

Terminal configuration defaults to:

``` python
TERM_CFG = TerminalConfiguration.RSE
# TERM_CFG = TerminalConfiguration.DIFF
```

Uncomment `DIFF` if using differential wiring.

------------------------------------------------------------------------

## 5️⃣ Run the Script

Click the green **Run ▶ button** in Spyder.

A new plotting window will open (this is expected behavior).

You should see:

-   Live time-domain plot
-   (Optional script) Live FFT plot

------------------------------------------------------------------------

## 🛑 Stopping the Script

Press:

    Ctrl + C

in the console.

If enabled, data will automatically save to:

    ni_usb6002_live_capture.csv

------------------------------------------------------------------------

# 📊 Running for N Samples Instead of Continuous

By default, the scripts use:

``` python
AcquisitionType.CONTINUOUS
```

To run for a fixed number of samples:

### Replace this:

``` python
sample_mode=AcquisitionType.CONTINUOUS
```

### With this:

``` python
sample_mode=AcquisitionType.FINITE,
samps_per_chan=TOTAL_SAMPLES
```

Then remove the `while True:` loop and instead read once:

``` python
y_data = task.read(number_of_samples_per_channel=TOTAL_SAMPLES)
```

This converts the script from:

-   🔄 Continuous streaming\
    to\
-   📦 Single batch acquisition

------------------------------------------------------------------------

# ⚙️ Recommended Typical Settings

  Application                           FS_HZ           Window    FMAX_HZ
  ------------------------------------- --------------- --------- --------------
  Low-frequency sensors (temp, light)   10--100 Hz      5--10 s   5--20 Hz
  Mechanical vibration                  1000--5000 Hz   2--5 s    200--1000 Hz
  Audio-like signals                    ≥ 8000 Hz       1--3 s    4000 Hz

Remember:

Fmax = Fs / 2 (Nyquist limit)

------------------------------------------------------------------------

# 🔌 Wiring Reminder

Default configuration:

RSE (Referenced Single Ended)

Wire signal to: AIx

Wire ground to: AI GND

If using differential mode:

Uncomment:

``` python
TERM_CFG = TerminalConfiguration.DIFF
```

and wire to:

AIx+ and AIx-

------------------------------------------------------------------------

# 🧾 Requirements

-   Anaconda (Python 3.9+ recommended)
-   Spyder
-   NI-DAQmx driver installed
-   `nidaqmx` Python package installed

Install nidaqmx via:

    pip install nidaqmx

or inside Anaconda prompt:

    conda install -c ni nidaqmx
