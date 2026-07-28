# SahaPilot Yol Haritasi

## Faz 1 - Simulasyon dogrulama (TAMAMLANDI)
- PD vs bang-bang kontrol karsilastirmasi
- RF guvenlik (OUI + ardisik tarama dogrulamasi) mantigi
- Navigasyon carpisma hatasi bulundu ve duzeltildi (200 senaryo, 0 carpisma)

## Faz 2 - Fiziksel prototip (SIRADA)
- Bilesenlerin tedariki (bkz. docs/MALIYET.md)
- Sasi montaji, motor/sensor kablolamasi
- IR sensor esik kalibrasyonu (gercek zeminde)

## Faz 3 - Firmware entegrasyonu
- firmware/sahapilot_firmware.ino iskeletini gercek pinlerle kalibre et
- Simulasyondaki PD parametrelerini gercek motor tepkisine gore yeniden ayarla
- RF guvenlik dugumunde WiFi.scanNetworks() ile OUI eslestirmesini uygula

## Faz 4 - Saha testi ve dokumantasyon
- Gercek ortamda test, simulasyon varsayimlariyla karsilastirma
- Video demo + kisa teknik rapor (yuksek lisans basvurusu / CV icin)
