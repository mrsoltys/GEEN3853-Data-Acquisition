# Arduino → Python DAQ (Live Plot + CSV Logging)

This repository demonstrates a **simple, transparent data acquisition (DAQ) system** using:

- **Arduino Uno** for sensor sampling
- **Serial communication** to stream data
- **Python (Jupyter Notebook)** for live plotting and CSV export

The goal is not maximum performance, but **clarity, reliability, and good engineering practice**.

---

## Workflow Overview

1. **Arduino**
   - Samples an analog signal on pin `A0`
   - Timestamps each sample using `micros()`
   - Streams data as **human-readable CSV text** over Serial

2. **Python (Jupyter Notebook)**
   - Connects to the Arduino via `pyserial`
   - Reads and parses incoming CSV lines
   - Displays a **live rolling plot**
   - Logs the full dataset to a **CSV file** for later analysis

3. **Analysis**
   - Data can be analyzed, plotted, and processed after acquisition
   - Live plotting is treated as a *view*, not the primary data store

---

## Data Format

Each line sent by the Arduino has the form:

```
us,raw
1234567,512
```

Where:
- `us`  = timestamp from `micros()` (microseconds since reset)
- `raw` = 10-bit ADC reading (`0–1023`)

All values are sent as **ASCII text (CSV)** for transparency and ease of debugging.

---

## Baud Rate and Throughput

Serial communication speed is limited by the **baud rate**.

- This project uses:
  ```cpp
  Serial.begin(115200);
  ```

- At 115200 baud:
  - ≈ 115,200 bits/sec
  - ≈ 11,520 bytes/sec usable throughput (10 bits/byte)

- Each CSV line is at most ~17 bytes:
  ```
  "us,raw\r\n"
  ```

- This limits the **theoretical maximum sample rate** to:
  ```
  11,520 bytes/sec ÷ 17 bytes/sample ≈ 677 samples/sec
  ```

In practice, stable rates are typically somewhat lower.

**Best practice:**  
> Use the *lowest baud rate that reliably supports your desired sample rate.*

---

## Why Use Text (CSV) Instead of Binary?

This project intentionally uses **text-based serial output**:

### Advantages
- Human-readable
- Easy to debug
- Easy to parse in Python
- Ideal for learning and teaching

### Tradeoff
- Text is inefficient compared to binary
- Limits maximum achievable sample rate

Binary streaming can be 2–3× faster at the same baud rate, but adds complexity and is intentionally avoided here.

---

## Timing Resolution on the Arduino Uno

The Arduino Uno uses a **16 MHz microcontroller**.  
As a result:

- `micros()` has a **resolution of 4 µs**
- Timestamps increment in steps of:
  ```
  0, 4, 8, 12, … µs
  ```

This is expected behavior and comes from the hardware timer configuration.

### Important distinctions
- **Resolution:** 4 µs (smallest distinguishable step)
- **Accuracy:** Very good over short durations
- **Drift:** Minimal over typical lab timescales

Seeing repeated timestamps or 4 µs jumps is normal and correct.

---

## Python Architecture (Why It Works in Jupyter)

The notebook separates responsibilities:

- **Background thread**
  - Continuously reads from the serial port
  - Buffers data for plotting
  - Logs all samples for CSV export

- **Main thread**
  - Handles plotting using `matplotlib.animation.FuncAnimation`
  - Updates at ~10–20 frames per second

This separation ensures:
- Reliable data capture
- Responsive plots
- No data loss due to slow plotting

---

## Starting and Stopping Acquisition

Because this system uses:
- a background thread
- a live animation timer

You **must** explicitly stop acquisition.

The notebook includes a **“Stop + Export”** cell that:
- stops the reader thread
- stops the animation
- closes the serial port
- closes the plot
- writes the CSV file

Failing to do this may leave the Jupyter kernel “busy.”

---

## Summary of Key Engineering Ideas

- **DAQ is a pipeline**: sensor → timing → transport → logging → visualization
- **Baud rate limits throughput**
- **Text is slower but clearer than binary**
- **Hardware sets timing resolution**
- **Plotting should never block acquisition**
- **Logging should be lossless; plotting can be decimated**

This system is intentionally simple, robust, and transparent — a foundation you can build on later.

---

## Files in This Repository

- `arduino_daq.ino`  
  Arduino sketch that samples `A0` and streams `us,raw` CSV data

- `LivePlot_and_ExportCSV.ipynb`  
  Jupyter notebook for live plotting and CSV logging

- `README.md`  
  This file

---

## Intended Use

This project is designed for:
- Introductory DAQ systems
- Measurement and data analysis courses
- Demonstrating real-world limits of instrumentation
- Teaching good data handling habits

Not for:
- High-speed oscilloscope replacement
- Maximum-throughput DAQ
- Production-grade logging systems

---

## Acknowledgements

Parts of this Arduino sketch, Jupyter notebook, and documentation were developed
with the assistance of **ChatGPT**, an AI language model created by OpenAI, through
an interactive design and debugging process.

The final code structure, comments, and instructional framing were reviewed and
adapted by the course instructor for clarity, correctness, and pedagogical intent.

ChatGPT: https://chat.openai.com  
OpenAI: https://openai.com
