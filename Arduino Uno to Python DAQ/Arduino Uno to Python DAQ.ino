/*
  Arduino Uno DAQ: stream analog pin A0 over Serial as CSV lines.

  Output format:
    us,raw
    <micros>,<0..1023>

  Notes:
  - This sketch is optimized for simplicity and robustness using ASCII CSV.
  - For much higher rates, consider: higher baud or binary packets.
*/

const uint8_t  ANALOG_PIN = A0;
const uint16_t RATE_HZ    = 500;                 // target sample rate (Hz)
const uint32_t DT_US      = 1000000UL / RATE_HZ; // sampling interval (microseconds)

uint32_t last_us = 0;

void setup() {
  Serial.begin(115200);
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

  // Optional: brief delay so the host can connect after reset
  delay(500);

  Serial.println("us,raw"); // CSV header
  last_us = micros();       // initialize scheduler reference
}

void loop() {
  const uint32_t now_us = micros();  //Check current time

  // Use signed subtraction to handle micros() rollover safely.
  if ((int32_t)(now_us - last_us) >= (int32_t)DT_US) {
    //Read data first
    const uint16_t raw = analogRead(ANALOG_PIN); // 10-bit ADC: 0..1023

    // Schedule next call. You could also use last_us = now_us, but this 
    // "Catch up" scheduling will try to correct for drift if loop timing slips.
    last_us += DT_US;

    Serial.print(now_us);
    Serial.print(',');
    Serial.println(raw);
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
  }
}