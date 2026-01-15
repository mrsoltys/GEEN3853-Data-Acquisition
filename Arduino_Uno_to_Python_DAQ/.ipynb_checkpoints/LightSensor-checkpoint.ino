// Arduino Uno: stream A0 over Serial as CSV lines
const int pin = A0;
const unsigned long dt_ms = 20; // 50 Hz

unsigned long last = 0;

void setup() {
  Serial.begin(115200);
  // Optional: wait a moment so Python can connect after reset
  delay(500);
  Serial.println("ms,raw,volts"); // header line (nice for CSV)
}

void loop() {
  unsigned long now = millis();
  if (now - last >= dt_ms) {
    last = now;

    int raw = analogRead(pin);              // 0..1023
    float volts = raw * (5.0 / 1023.0);     // Uno ADC ref ~5V (approx)

    Serial.print(now);
    Serial.print(",");
    Serial.print(raw);
    Serial.print(",");
    Serial.println(volts, 4);
  }
}