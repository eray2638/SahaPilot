/*
  ============================================================
  SahaPilot - ESP32 Firmware Iskeleti (v0.1 - baslangic noktasi)
  ============================================================
  Bu dosya, Python simulasyonunda (simulasyon/sekil2_pid_serit_takibi.py
  ve simulasyon/sekil3_kontrol_karsilastirma.py) dogrulanan PD kontrol
  mantigini gercek ESP32 donanimina tasimanin ilk adimidir.

  ONEMLI: Bu bir ISKELET'tir, gercek donanimla test edilmeden
  dogrudan bir robota yuklenmemelidir. Pin numaralari ve esik
  degerleri, gercek devre kurulunca kalibre edilmelidir.

  Donanim varsayimi:
    - 3 adet IR cizgi sensoru (sol, orta, sag)
    - 1 adet HC-SR04 ultrasonik mesafe sensoru
    - L298N motor surucu ile 2 adet DC motor (diferansiyel surus)

  Neden Python simulasyonundaki gibi PD kullaniyoruz, bang-bang degil:
  sekil3_kontrol_karsilastirma.py sonuclarina gore, bang-bang/sadece-P
  kontrol surekli salinim yapip hic yatismiyor; PD (orantisal + turevsel)
  ~2 saniyede referansa yaklasiyor. Firmware'de de ayni prensip uygulanir.
  ============================================================
*/

// ---------------- PIN TANIMLARI (kalibre edilecek) ----------------
const int IR_SOL_PIN   = 34;
const int IR_ORTA_PIN  = 35;
const int IR_SAG_PIN    = 32;

const int ULTRASONIK_TRIG_PIN = 5;
const int ULTRASONIK_ECHO_PIN = 18;

const int MOTOR_SOL_ILERI  = 12;
const int MOTOR_SOL_GERI    = 13;
const int MOTOR_SAG_ILERI  = 14;
const int MOTOR_SAG_GERI    = 27;

// ---------------- KONTROL PARAMETRELERI ----------------
// Python simulasyonunda dogrulanan degerler (Kp=4, Kd=2) baslangic
// noktasidir; gercek motorlarin tepkisine gore yeniden ayarlanmalidir.
const float KP = 4.0;
const float KD = 2.0;
const float ESIK_ENGEL_CM = 15.0;   // bu mesafenin altinda engelden kac

// Guvenli-tarafta-kal (fail-safe) esikleri: sensor arizasi veya cizgi
// kaybi durumunda arac korumasiz ilerlemeye devam etmemelidir.
const int MAX_ARDISIK_ECHO_ARIZASI = 3;  // ust uste takili echo hatti -> dur
const int MAX_ARDISIK_CIZGI_KAYBI = 5;   // ust uste cizgisiz kare -> dur

// mesafe_olc_cm() donus kodlari: negatif degerler gecerli olcum degildir.
const float MESAFE_MENZIL_DISI = -1.0;   // echo yok: menzilde engel yok
const float MESAFE_SENSOR_ARIZASI = -2.0;  // echo hatti tetiklemeden HIGH

// ---------------- DURUM DEGISKENLERI ----------------
float onceki_hata = 0.0;
unsigned long onceki_zaman_ms = 0;
int ardisik_echo_arizasi = 0;
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

// IR sensorlerden yanal hatayi hesapla.
// Donusum mantigi Python'daki ir_oku() fonksiyonuyla ayni fikir:
// sol sensor cizgiyi goruyorsa hata negatif (sola kaymisiz demek,
// saga donmemiz gerekir), sag sensor goruyorsa hata pozitif.
// cizgi_var: cikis parametresi, sensorlerden hicbiri cizgi gormediyse false.
float hata_hesapla(bool &cizgi_var) {
  bool sol  = digitalRead(IR_SOL_PIN)  == HIGH;
  bool orta = digitalRead(IR_ORTA_PIN) == HIGH;
  bool sag  = digitalRead(IR_SAG_PIN)  == HIGH;

  cizgi_var = sol || orta || sag;

  if (orta) return 0.0;
  if (sol)  return -1.0;
  if (sag)  return  1.0;
  return 0.0;
}

// HC-SR04 ultrasonik sensorden mesafe olcumu (cm cinsinden).
float mesafe_olc_cm() {
  // Bosta echo hatti LOW olmalidir. Tetikleme oncesi HIGH ise sensor
  // veya kablolama arizali demektir (kopuk GND, bozuk modul); bu durumda
  // pulseIn zaten anlamsiz bir deger dondurur.
  if (digitalRead(ULTRASONIK_ECHO_PIN) == HIGH) return MESAFE_SENSOR_ARIZASI;

  digitalWrite(ULTRASONIK_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIK_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIK_TRIG_PIN, LOW);

  long sure_us = pulseIn(ULTRASONIK_ECHO_PIN, HIGH, 30000);  // 30ms timeout
  // Yanit yok = onumuzde ~5 m icinde yansitici yuzey yok. Bunu sayisal
  // bir mesafe (eski hali: 999.0) olarak dondurmek gecerli bir olcumle
  // karistirilmasina yol aciyordu; ayri bir donus kodu kullaniyoruz.
  if (sure_us == 0) return MESAFE_MENZIL_DISI;
  return sure_us * 0.0343 / 2.0;
}

// Diferansiyel surus: PD ciktisina gore sol/sag motor hizini ayarla.
void motorlari_sur(float pd_cikti) {
  // pd_cikti pozitifse hata sagda demekti -> saga don (sol motor hizlan,
  // sag motor yavasla). Gercek motor hiz araligina gore olceklenmeli.
  int taban_hiz = 150;          // 0-255 PWM araligi, kalibre edilecek
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
  onceki_hata = 0.0;   // duruslardan sonra turev sicramasini engelle
}

void loop() {
  unsigned long simdi_ms = millis();
  float dt = (simdi_ms - onceki_zaman_ms) / 1000.0;
  if (dt <= 0) dt = 0.001;   // sifira bolme koruma

  float mesafe = mesafe_olc_cm();

  if (mesafe == MESAFE_SENSOR_ARIZASI) {
    ardisik_echo_arizasi++;
  } else {
    ardisik_echo_arizasi = 0;
  }

  bool cizgi_var = false;
  float hata = hata_hesapla(cizgi_var);
  if (cizgi_var) {
    ardisik_cizgi_kaybi = 0;
  } else {
    ardisik_cizgi_kaybi++;
  }

  bool sensor_arizali = ardisik_echo_arizasi >= MAX_ARDISIK_ECHO_ARIZASI;
  bool cizgi_kayip = ardisik_cizgi_kaybi >= MAX_ARDISIK_CIZGI_KAYBI;
  bool engel_yakin = (mesafe >= 0.0) && (mesafe < ESIK_ENGEL_CM);

  if (sensor_arizali || cizgi_kayip || engel_yakin) {
    // Guvenlik onceligi: engel yakinsa, ultrasonik sensor arizali gorunuyorsa
    // ya da cizgi kaybedildiyse dur. Cizgi kaybinda korumasiz "duz devam et"
    // davranisi otonom bir aracta kabul edilemez.
    // (Python simulasyonundaki engelden_kac() mantigi burada
    // gelistirilecek - simdilik basit "dur" davranisi.)
    dur();
  } else {
    float hata_hizi = (hata - onceki_hata) / dt;
    float pd_cikti = KP * hata + KD * hata_hizi;

    motorlari_sur(pd_cikti);

    onceki_hata = hata;
  }

  onceki_zaman_ms = simdi_ms;
  delay(20);   // ~50 Hz kontrol dongusu
}

/*
  YAPILACAKLAR (bu iskeletten gercek prototipe gecis):
  1. Pin numaralarini gercek devre semasina gore guncelle.
  2. IR sensor esiklerini (dijital HIGH/LOW yerine analogRead ile
     analog esikleme) gercek zeminde kalibre et.
  3. engelden_kac() mantigini (Python'daki gibi sola/saga kacinma)
     burada da uygula, sadece "dur" ile yetinme.
  4. RF guvenlik katmani icin ikinci bir ESP32 dugumde
     WiFi.scanNetworks() ile OUI eslestirmesi yaz (simulasyon/
     sekil4_rf_guvenlik.py'deki ardisik dogrulama mantigiyla ayni).
     DIKKAT: WiFi SSID/sifresi ve telemetri anahtarlari bu dosyaya
     GOMULMEMELIDIR. Surum kontrolune girmeyen (.gitignore'da olan)
     ayri bir gizli_ayarlar.h dosyasindan okunmalidir. Ayrica MAC/OUI
     eslestirmesi kolayca taklit edilebilir; ayrintili tehdit modeli
     ve sinirlar icin SECURITY.md'ye bakiniz.
  5. Seri port uzerinden telemetri (hata, PD ciktisi, mesafe)
     yayinlayip gercek/simulasyon davranisini karsilastir.
*/
