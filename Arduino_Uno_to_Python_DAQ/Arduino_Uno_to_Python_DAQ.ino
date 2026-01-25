/*
  Arduino Uno DAQ (A0) — command-triggered CSV streaming

  Command:
    START,<rate_hz>,<n_samples>

  Output:
    READY
    arduino_us,raw
    <micros>,<0..1023>
    ...
    DONE

  Notes:
  - This sketch is optimized for simplicity and robustness using ASCII CSV.
  - For much higher rates, consider: higher baud or binary packets.
  
*/

const int ADC_PIN = A0;

unsigned long sample_interval_us = 2000; // default 500 Hz
unsigned long n_samples = 0;

bool running = false;
unsigned long last_us = 0;
unsigned long sent = 0;

void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.println("READY");
    /*
    NOTE: Serial speed will limit data transfer rates. Higher baud rates may
    introduce data corruption depending on USB cable, drivers, and host system.

    Best practice: use the lowest baud rate that reliably supports the desired
    sample rate.

    At 115200 baud:
      - Raw throughput ≈ 115,200 bits/sec ≈ 11,520 bytes/sec (10 bits/byte)
      - Each CSV line is at most ~17 bytes: "us,raw\r\n"
      - Maximum theoretical rate ≈ 11,520 / 17 ≈ 677 samples/sec

    In practice, stable rates are typically somewhat lower.
  */

}

void loop() {
  // --- Listen for command ---
  // Command is of form: "Start,Rate[Hz],N Samples"
  if (!running && Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.startsWith("START")) {
      // parse: START,rate,n
      int c1 = cmd.indexOf(',');
      int c2 = cmd.indexOf(',', c1 + 1);
      if (c1 > 0 && c2 > c1) {
        long rate_hz = cmd.substring(c1 + 1, c2).toInt();
        long n = cmd.substring(c2 + 1).toInt();
        if (rate_hz > 0 && n > 0) {
          sample_interval_us = (unsigned long)(1000000L / rate_hz);
          n_samples = (unsigned long)n;
          running = true;
          sent = 0;
          last_us = micros();
          Serial.println("arduino_us,raw");
        }
      }
    }
  }

  // --- Sample loop (hardware paced by micros timing) ---
  if (running) {
    unsigned long now = micros();
    if ((unsigned long)(now - last_us) >= sample_interval_us) {
      int raw = analogRead(ADC_PIN);
      last_us += sample_interval_us; // keeps cadence stable
      Serial.print(now);
      Serial.print(",");
      Serial.println(raw);

      sent++;
      if (sent >= n_samples) {
        running = false;
        Serial.println("DONE");
      }
    }
  }
}


  
    /*
    NOTE ON TEXT VS. BINARY SERIAL TRANSFER

    This sketch sends data as human-readable ASCII (CSV text), which is simple,
    transparent, and ideal for learning and debugging.

    Each sample is transmitted as text, e.g.:
      "us,raw\r\n"  → up to ~17 bytes per sample

    At 115200 baud (~11,520 bytes/sec usable throughput), this limits the
    theoretical maximum sample rate to ~677 samples/sec.

    If data were sent in binary form instead (fixed-size packets), the same
    information could be transmitted in as little as:
      - 4 bytes: uint32 timestamp (microseconds)
      - 2 bytes: uint16 ADC value
      → 6 bytes per sample total

    This would increase the maximum achievable sample rate by roughly
    a factor of 2–3 at the same baud rate.

    Tradeoff:
      - Text (CSV): simple, readable, easy to debug
      - Binary: faster and more efficient, but harder to inspect and parse

    Best practice: use text for learning and moderate data rates; use binary
    only when higher sample rates are required.
  */
  