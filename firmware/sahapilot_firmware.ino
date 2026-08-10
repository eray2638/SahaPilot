/*
SahaPilot - ESP32 Firmware (v0.3 - PR2 + PR3 birlestirilmis)
Bu dosya, main branch PR#2 ile PR#3'un fikirlerini birlestirir.
PR#2: timeout = hata. PR#3: timeout = belirsiz, echo stuck-HIGH = hata.
Bu surum PR#3'un ayrimini esas alir, ama temkinlilik icin:
1) MESAFE_MIN_CM/MAX_CM menzil kontrolu korunur (PR#2'den).
2) Uzun sureli timeout (15 ardisik) yine de fail-safe olarak durdurur.
3) Cizgi kaybi esigi 10 (PR#2'nin temkinli degeri).
*/

const int IR_SOL_PIN = 34;
const int IR_ORTA_PIN = 35;
const int IR_SAG_PIN = 32;

const int ULTRASONIK_TRIG_PIN = 5;
const int ULTRASONIK_ECHO_PIN = 18;

const int MOTOR_SOL_ILERI = 12;
const int MOTOR_SOL_GERI = 13;
const int MOTOR_SAG_ILERI = 14;
const int MOTOR_SAG_GERI = 27;

const float KP = 4.0;
const float KD = 2.0;
const float ESIK_ENGEL_CM = 15.0;

const float MESAFE_MIN_CM = 2.0;
const float MESAFE_MAX_CM = 400.0;

const float MESAFE_MENZIL_DISI = -1.0;
const float MESAFE_SENSOR_ARIZASI = -2.0;

const int MAX_ARDISIK_ECHO_ARIZASI = 3;
const int MAX_ARDISIK_MENZIL_DISI = 15;
const int MAX_ARDISIK_CIZGI_KAYBI = 10;

float onceki_hata = 0.0;
unsigned long onceki_zaman_ms = 0;
int ardisik_echo_arizasi = 0;
int ardisik_menzil_disi = 0;
int ardisik_cizgi_kaybi = 0;

void setup() {
  Serial.begin(115200);
  pinMode(IR_SOL_PIN, INPUT);
  pinMode(IR_ORTA_PIN, INPUT);
  pinMode(IR_SAG_PIN, INPUT);
  pinMode(ULTRASONIK_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIK_ECHO_PIN, INPUT);
  pinMode(MOTOR_SOL_ILERI, OUTPUT);
  pinMode(MOTOR_SOL_GERI, OUTPUT);
  pinMode(MOTOR_SAG_ILERI, OUTPUT);
  pinMode(MOTOR_SAG_GERI, OUTPUT);
  onceki_zaman_ms = millis();
}

float hata_hesapla(bool &cizgi_var) {
  bool sol = digitalRead(IR_SOL_PIN) == HIGH;
  bool orta = digitalRead(IR_ORTA_PIN) == HIGH;
  bool sag = digitalRead(IR_SAG_PIN) == HIGH;
  cizgi_var = sol || orta || sag;
  if (orta) return 0.0;
  if (sol) return -1.0;
  if (sag) return 1.0;
  return 0.0;
}

float mesafe_olc_cm() {
  if (digitalRead(ULTRASONIK_ECHO_PIN) == HIGH) return MESAFE_SENSOR_ARIZASI;
  digitalWrite(ULTRASONIK_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIK_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIK_TRIG_PIN, LOW);
  long sure_us = pulseIn(ULTRASONIK_ECHO_PIN, HIGH, 30000);
  if (sure_us == 0) return MESAFE_MENZIL_DISI;
  float mesafe = sure_us * 0.0343 / 2.0;
  if (mesafe < MESAFE_MIN_CM || mesafe > MESAFE_MAX_CM) return MESAFE_MENZIL_DISI;
  return mesafe;
}

void motorlari_sur(float pd_cikti) {
  int taban_hiz = 150;
  int fark = constrain((int)(pd_cikti * 20), -100, 100);
  int sol_hiz = constrain(taban_hiz - fark, 0, 255);
  int sag_hiz = constrain(taban_hiz + fark, 0, 255);
  analogWrite(MOTOR_SOL_ILERI, sol_hiz);
  analogWrite(MOTOR_SAG_ILERI, sag_hiz);
  digitalWrite(MOTOR_SOL_GERI, LOW);
  digitalWrite(MOTOR_SAG_GERI, LOW);
}

void dur() {
  analogWrite(MOTOR_SOL_ILERI, 0);
  analogWrite(MOTOR_SAG_ILERI, 0);
  digitalWrite(MOTOR_SOL_GERI, LOW);
  digitalWrite(MOTOR_SAG_GERI, LOW);
  onceki_hata = 0.0;
}

void loop() {
  unsigned long simdi_ms = millis();
  float dt = (simdi_ms - onceki_zaman_ms) / 1000.0;
  if (dt <= 0) dt = 0.001;
  float mesafe = mesafe_olc_cm();
  if (mesafe == MESAFE_SENSOR_ARIZASI) {
    ardisik_echo_arizasi++;
    ardisik_menzil_disi = 0;
    Serial.print("[HATA] Echo hatti takili kaldi, ardisik: ");
    Serial.println(ardisik_echo_arizasi);
  } else if (mesafe == MESAFE_MENZIL_DISI) {
    ardisik_echo_arizasi = 0;
    ardisik_menzil_disi++;
  } else {
    ardisik_echo_arizasi = 0;
    ardisik_menzil_disi = 0;
  }
  
  bool cizgi_var = false;
  float hata = hata_hesapla(cizgi_var);
  if (cizgi_var) {
    ardisik_cizgi_kaybi = 0;
  } else {
    ardisik_cizgi_kaybi++;
  }
  
  bool echo_arizali = ardisik_echo_arizasi >= MAX_ARDISIK_ECHO_ARIZASI;
  bool uzun_menzil_disi = ardisik_menzil_disi >= MAX_ARDISIK_MENZIL_DISI;
  bool cizgi_kayip = ardisik_cizgi_kaybi >= MAX_ARDISIK_CIZGI_KAYBI;
  bool engel_yakin = (mesafe >= 0.0) && (mesafe < ESIK_ENGEL_CM);
  
  if (echo_arizali || uzun_menzil_disi || cizgi_kayip || engel_yakin) {
    if (echo_arizali) Serial.println("[KRITIK] Ultrasonik sensor arizali -> arac durduruldu");
    if (uzun_menzil_disi) Serial.println("[KRITIK] Uzun sureli gecerli olcum yok -> arac durduruldu");
    if (cizgi_kayip) Serial.println("[KRITIK] Cizgi bulunamiyor -> arac durduruldu");
    dur();
  } else {
    float hata_hizi = (hata - onceki_hata) / dt;
    float pd_cikti = KP * hata + KD * hata_hizi;
    motorlari_sur(pd_cikti);
    onceki_hata = hata;
  }
  
  onceki_zaman_ms = simdi_ms;
  delay(20);
}

/*
YAPILACAKLAR:
1. Pin numaralarini gercek devre semasina gore guncelle.
2. IR sensor esiklerini gercek zeminde kalibre et.
3. engelden_kac() mantigini burada da uygula.
4. RF guvenlik katmani icin WiFi.scanNetworks() ile OUI eslestirmesi yaz.
   WiFi bilgileri gizli_ayarlar.h icinde tutulmali, bu dosyaya gomulmemeli.
      MAC/OUI eslestirmesinin sinirlari icin SECURITY.md'ye bakiniz.
      5. Seri port uzerinden telemetri yayinlayip davranisi karsilastir.
      6. MAX_ARDISIK_MENZIL_DISI (=15) degeri elle secildi, gercek testte ayarlanmali.
      */
