# SahaPilot Yol Haritasi

## Faz 1 - Simulasyon dogrulama (TAMAMLANDI)

- PD vs bang-bang kontrol karsilastirmasi
- RF guvenlik (OUI + ardisik tarama dogrulamasi) mantigi
- Navigasyon carpisma hatasi bulundu ve duzeltildi (200 senaryo, 0 carpisma)
- Butun simulasyon modulleri pytest ile otomatik test altina alindi (84 test, %99 kapsama, mutasyon testiyle dogrulanmis)

## Faz 2 - Fiziksel prototip (SIRADA)

- Bilesenlerin tedariki (bkz. docs/MALIYET.md)
- Sasi montaji, motor/sensor kablolamasi
- IR sensor esik kalibrasyonu (gercek zeminde)

## Faz 3 - Firmware entegrasyonu (kismen tamamlandi)

- [TAMAMLANDI] Ariza-toleransli navigasyon mantigi: ultrasonik sensor arizasi (echo takili kalma) ile menzil-disi olcum ayri ayri ele alindi, cizgi kaybinda guvenli durma eklendi; C++ test harness'i ile 11 assertion dogrulandi, gercek ESP32'de (esp32:esp32@3.3.11) sifir uyariyla derlendi
- [SIRADA] firmware/sahapilot_firmware.ino'daki pin numaralarini gercek devre semasina gore guncelle
- [SIRADA] Simulasyondaki PD parametrelerini gercek motor tepkisine gore yeniden ayarla
- [SIRADA] RF guvenlik dugumunde WiFi.scanNetworks() ile OUI eslestirmesini uygula (su an yalnizca simulasyonda dogrulanmis)

## Faz 4 - Saha testi ve dokumantasyon

- Gercek ortamda test, simulasyon varsayimlariyla karsilastirma
- Video demo + kisa teknik rapor (yuksek lisans basvurusu / CV icin)
