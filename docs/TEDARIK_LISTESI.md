# SahaPilot Prototip Tedarik Listesi (Agustos 2026)

Fiyatlar Robotistan, Cimri.com (fiyat karsilastirma), Trendyol ve Direnc.net uzerinden Agustos 2026'da yapilan aramalarla derlenmistir. Bazi urunler arama sirasinda stokta yoktu ("Tukendi") - siparis oncesi guncel stok/fiyat kontrolu sart. Fiyatlar KDV dahildir.

## Ana bilesenler

| Bilesen | Adet | Birim fiyat (TL) | Toplam (TL) | Kaynak |
|---|---|---|---|---|
| ESP32 DevKit (WROOM-32) | 2 (arac + RF dugumu) | ~450-570 | ~900-1.140 | [Trendyol/Robiduck](https://www.trendyol.com/esp32-wroom-y-s13092) ~466 TL, [Robotistan (cimri.com)](https://www.cimri.com/hobi-elektronigi/en-ucuz-robotistan-esp32-esp-32s-wifi-ve-bluetooth-dual-mode-gelistirme-karti-fiyatlari,1871530375) ~567 TL |
| L298N cift motor surucu karti | 1 | ~100-180 | ~100-180 | [Robotistan](https://www.robotistan.com/l298-cift-motor-surucu-karti-dual-motor-driver-yesil-pcb) |
| HC-SR04 ultrasonik mesafe sensoru | 1 | ~28-56 | ~40 | [Cimri.com](https://www.cimri.com/lazer-metre-uzaklik-olcer/en-ucuz-hc-sr04-ultrasonik-mesafe-sensoru-fiyatlari,50463069) |
| TCRT5000 5 kanal IR serit sensoru | 1 | ~42-80 | ~50 | [Robocombo](https://www.robocombo.com/tcrt5000-5-kanalli-cizgi-izleyen-sensor-modulu) |
| Sasi + 2x DC motor + teker | 1 set | ~186-575 | ~186-575 | [REX 2WD platform](https://www.robotistan.com/2wd-cok-amacli-mobil-robot-platformu) 574,88 TL; [motor+teker seti](https://www.robotistan.com/6v-250-rpm-motor-ve-tekerlek-seti) 93,03 TL/adet - ikisi de arama aninda stokta yoktu |
| 18650 Li-ion pil + tutucu | 1-2 pil + tutucu | ~60-100 + ~50-100 | ~150-250 | [Robotistan](https://www.robotistan.com/18650-li-ion-pil) |
| Jumper kablo + breadboard seti | 1 | ~60-150 | ~100 | [Direnc.net](https://www.direnc.net/560-parca-jumper-kablo-seti-en) 143,52 TL |

**Tahmini toplam: ~1.550-2.350 TL** (eski tahmin olan ~1.340 TL'nin belirgin sekilde uzerinde - 2026 fiyat artisini yansitiyor, ozellikle ESP32 kartlari ikiye katlanmis gorunuyor).

## Ekipman (muhtemelen elde mevcut, tek seferlik)

- Multimetre (kablolama hatalarini bulmak icin sart)
- USB-A to Micro-USB veya USB-C kablo (ESP32 baglantisi icin)
- Lehim makinesi (opsiyonel - breadboard ile baslamak lehimsiz de mumkun)
- Bilgisayarda Arduino IDE kurulu olmasi

## Uyarilar

- REX 2WD platform ve motor-teker seti arama aninda Robotistan'da stokta yoktu; siparis oncesi tekrar kontrol edilmeli veya Direnc.net/Robotsepeti gibi alternatif saticilara bakilmali.
- ESP32 fiyatlari eski tahminin (~200 TL) yaklasik iki katina cikmis durumda - docs/MALIYET.md guncellendi.
