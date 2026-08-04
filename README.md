# SahaPilot

**Low-cost, ESP32-based autonomous ground vehicle (AGV) with an integrated RF security layer, built for small and mid-sized manufacturers.**

Developed for the *15. Otomotivin Geleceği Tasarım Yarışması (OGTY 2026)* — theme: Endüstriyel Mobilite.

> Türkçe özet için bu dosyanın sonundaki "Türkçe Özet" bölümüne bakınız.

---

## 1. Problem

Commercial industrial AGV/AMR systems cost $15,000–$40,000 per unit, require custom infrastructure, and are largely out of reach for small and mid-sized manufacturers (KOBİ) in Turkey. Simple line-following robots exist at lower cost but offer no security layer — anyone can walk up to the vehicle or its operating area undetected.

**SahaPilot's goal:** deliver autonomous material transport at roughly 1/10th the entry cost, on off-the-shelf ESP32 hardware, with a built-in RF-based intrusion detection layer as a differentiator rather than an afterthought.

## 2. System architecture

See `gorseller/Sekil1_Sistem_Mimarisi.jpg`.

The vehicle combines two functional layers on the same low-cost hardware:

- **Navigation layer:** 3-channel IR line-sensor array + forward-facing ultrasonic sensor for line-following and obstacle avoidance.
- **Security layer:** a second ESP32 node continuously scans nearby wireless traffic and flags devices whose MAC-address OUI (Organizationally Unique Identifier — the first 3 bytes of a MAC address, which identify the manufacturer) doesn't match a known allow-list.

## 3. Control methodology (validated in simulation before hardware)

### 3.1 Line following — PID vs bang-bang (`simulasyon/sekil2_pid_serit_takibi.py`, `sekil3_kontrol_karsilastirma.py`)

The lateral dynamics are modeled as a double integrator:

```
y'' = Kp·(r − y) + Kd·(r' − y')
```

where `y` is lateral position, `r` is the reference line position, `Kp` is proportional gain, `Kd` is derivative gain (damping).

- A tuned PD controller (Kp=4, Kd=2) converges to the reference within ~2 seconds of a step disturbance.
- Bang-bang and pure-proportional control sustain persistent oscillation and never settle — this is why the actual firmware uses PD, not simple threshold logic, for the steering correction.

### 3.2 RF security layer — OUI matching with consecutive-scan confirmation (`simulasyon/sekil4_rf_guvenlik.py`)

A single unknown-OUI sighting is not treated as an intrusion (real-world RF scans are noisy — a passer-by's phone can appear once and vanish). The detector requires **3 consecutive scans** with the same unauthorized OUI before raising an alert. In simulation (60 scans, unauthorized device appearing stochastically after scan 30 with RSSI rising from -92 dBm to -55 dBm as it "approaches"):

- Detection fires ~2–3 scans after the intruder first appears.
- Zero false alarms across the pre-intrusion window.

This consecutive-confirmation approach is conceptually the same false-alarm-reduction idea used in CFAR (Constant False Alarm Rate) radar detection, applied here to a much simpler RF/MAC context.

### 3.3 Obstacle avoidance bug fix (`simulasyon/otonom_kodu_duzeltilmis.py`)

An earlier version of the line-following + obstacle-avoidance logic had a real bug, found via randomized testing (not just code review): the ultrasonic "look ahead" check and the line-centering logic used different frames of reference, so the vehicle could sense an obstacle, begin avoiding it, and then get pulled straight back onto it by the line-centering step. This produced ~1,000 collisions across 200 randomized test runs. The fix adds one explicit check — "does my candidate next position collide with an obstacle *in the current row*, regardless of which behavior chose it?" — before committing to a move. Verified fix: 0 collisions across the same 200 test seeds.

## 4. Repository structure

```
SahaPilot/
├── simulasyon/     Python proof-of-concept simulations (control theory, RF detection, bug-fixed navigation logic)
├── firmware/        ESP32 (Arduino/C++) firmware skeleton — hardware implementation in progress
├── gorseller/        Generated figures (Şekil 1–4) referenced in the application document
├── basvuru_belgeleri/  Competition application document (PDF)
└── docs/             Cost breakdown, hardware sourcing, roadmap notes
```

## 4.1 Tests

Unit tests for the simulation modules live in `tests/` (pytest):

```bash
pip install -r requirements-dev.txt
pytest                                              # run the suite
pytest --cov=simulasyon --cov-report=term-missing   # with coverage
```

Coverage is 99% of `simulasyon/` (only the `if __name__ == "__main__"` entry lines are uncovered). `tests/test_otonom_navigasyon.py::TestMainDongusu::test_main_dongusu_carpismasiz` is the regression test for the collision bug in section 3.3 — it replays the same 200 randomized seeds and asserts zero collisions.

## 5. Tech stack

- **Simulation / control validation:** Python, NumPy, Matplotlib
- **Target firmware:** C++ (Arduino framework) on ESP32
- **Application document generation:** Python + ReportLab

## 6. Estimated cost (prototype)

| Component | Est. cost (TRY) |
|---|---|
| ESP32 DevKit v1 | 200 |
| L298N motor driver | 60 |
| 2× geared DC motor + wheel | 220 |
| Chassis + caster wheel | 150 |
| 5-channel IR line sensor | 90 |
| HC-SR04 ultrasonic sensor | 40 |
| Li-ion battery + holder | 260 |
| Wiring / misc | 120 |
| RF security layer (extra ESP32 node) | 200 |
| **Prototype total** | **~1,340** |

Productized unit (enclosure, PCB, labor) estimated at 3,000–4,000 TRY, vs. 15,000–40,000 USD for commercial AGV systems.

## 7. Roadmap

- [x] Control-theory validation in simulation (PD vs bang-bang)
- [x] RF security detection logic validated in simulation
- [x] Navigation bug found and fixed via randomized testing
- [x] Competition application document (OGTY 2026)
- [ ] Physical prototype build (chassis, wiring, sensor calibration)
- [ ] ESP32 firmware implementing the validated control logic
- [ ] Field testing against the simulated assumptions
- [ ] Short technical report / write-up suitable for graduate-school research-experience material

## 8. Author

Eray Özen — Electrical & Electronics Engineering, Gazi University.

## 9. License

MIT (see `LICENSE`).

---

## Türkçe Özet

SahaPilot, küçük ve orta ölçekli üreticilere yönelik, ESP32 tabanlı, düşük maliyetli bir otonom saha lojistiği aracıdır (AGV). Ticari AGV sistemleri 15.000–40.000 USD gibi maliyetlerle geliyor ve KOBİ bütçesine uygun değil; SahaPilot bunu ~1.340 TL prototip / 3.000-4.000 TL ürünleşmiş birim maliyetine indirmeyi hedefliyor. Aracın iki katmanı var: (1) IR şerit sensörleri + ultrasonik sensörle şerit takibi ve engelden kaçınma, (2) çevredeki kablosuz cihazların MAC adresi OUI'sine bakarak yetkisiz cihaz tespiti yapan RF güvenlik katmanı. `simulasyon/` klasöründeki Python dosyaları, donanıma geçmeden önce kontrol mantığını (PID vs bang-bang) ve RF tespit algoritmasını doğrulamak için yazıldı; `otonom_kodu_duzeltilmis.py` dosyası, rastgele test yöntemiyle bulunup düzeltilen gerçek bir çarpışma hatasının belgesidir (1009 çarpışma -> 0 çarpışma, 200 senaryo). Proje, *15. Otomotivin Geleceği Tasarım Yarışması*'na (OGTY 2026) başvuru olarak hazırlandı; sıradaki adım gerçek donanım prototipini kurmak ve firmware'i yazmaktır.
