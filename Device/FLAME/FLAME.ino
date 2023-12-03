const int flame_sensor = 26;
const int led_red = 25;
const int led_green = 33;

int x;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(flame_sensor, INPUT);
  pinMode(led_red, OUTPUT);
  pinMode(led_green, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  x = Serial.println(digitalRead(flame_sensor));
  delay(500);
  if(x == 0){
    Serial.println("NO FLAME");
    digitalWrite(led_red, LOW);
    digitalWrite(led_green, HIGH);
  }
  if(x == 1){
    digitalWrite(led_red, HIGH);
    digitalWrite(led_green, LOW);
  }
}
