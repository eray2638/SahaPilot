# Security notes — SahaPilot

SahaPilot is currently a simulation + firmware-skeleton project: Python
proof-of-concept scripts under `simulasyon/` and an ESP32 sketch under
`firmware/`. There is no network service, no database, and no user-facing
application in this repository, so classic web-application issues (SQL
injection, CORS misconfiguration, exposed debug endpoints, missing
authorization checks) have no attack surface here yet. This file records the
threat model and the rules that apply as the project moves to hardware
(Phase 3 in `docs/YOL_HARITASI.md`), which is when a real attack surface —
WiFi, RF scanning, telemetry — appears.

## 1. Design limitation: OUI/MAC allow-listing is not authentication

The RF security layer (`simulasyon/sekil4_rf_guvenlik.py`) classifies nearby
devices by comparing the first three bytes of their MAC address (the OUI)
against an allow-list. This is useful as an *intrusion signal*, but it is not
an authentication mechanism, and the documentation should not present it as
one:

- MAC addresses are transmitted in the clear and can be set arbitrarily in
  software on most WiFi/Bluetooth adapters, so an attacker can present an
  allow-listed OUI at will.
- Modern phones and laptops randomize their MAC addresses by default, so a
  legitimate device may look "unknown" and an attacker may look different on
  each scan.
- The consecutive-scan confirmation (3 matches before alerting) reduces false
  alarms, but it also means an attacker who is only briefly in range, or who
  rotates their MAC each scan, will not trigger the alert.

Treat the layer as "an unexpected radio appeared near the vehicle" telemetry,
not as an access-control decision. Anything that must actually be trusted
(e.g. a remote stop command) needs cryptographic authentication, not an OUI
match.

## 2. Fail-safe behaviour in the firmware

An autonomous vehicle must fail closed: when a sensor cannot be trusted, the
correct action is to stop, not to keep driving. Two fail-open paths were
fixed in `firmware/sahapilot_firmware.ino`:

- A missing ultrasonic echo used to be reported as `999.0` cm, i.e. a normal
  "path is clear" distance, so a disconnected or dead sensor read as "no
  obstacle, full speed ahead". Failed measurements now return distinct
  negative status codes, and an echo line that is already HIGH before
  triggering (a wiring/module fault) stops the vehicle after
  `MAX_ARDISIK_ECHO_ARIZASI` consecutive occurrences.
- Losing the line (no IR sensor sees it) used to produce a zero error, which
  made the vehicle drive straight ahead blindly. It now stops after
  `MAX_ARDISIK_CIZGI_KAYBI` consecutive line-less control cycles.

Note that "no echo" cannot be distinguished from "nothing within ~5 m" with a
single HC-SR04, so an unpowered sensor pointed at open space is still
indistinguishable from a clear path. Before field use, add an independent
hardware fail-safe that does not depend on the ultrasonic sensor — e.g. a
bumper limit switch that cuts motor drive — and a hardware emergency stop.

## 3. Rules for the hardware phase

- **No credentials in the repository.** WiFi SSID/password, telemetry
  endpoints, and API keys must live in an untracked `gizli_ayarlar.h`
  (already in `.gitignore`), never inline in the sketch. As of this audit the
  working tree and the full git history contain no credentials — keep it that
  way, because rewriting published firmware history is far harder than not
  committing the secret.
- **Do not expose an unauthenticated control interface.** If telemetry or
  tuning is added over WiFi, do not ship an open HTTP endpoint or an OTA
  update path that anyone in radio range can reach; anything that can move
  the vehicle must be authenticated and, preferably, reachable only on a
  dedicated network.
- **Pin dependencies.** `simulasyon/requirements.txt` pins exact versions so
  a compromised or breaking upstream release is not pulled in silently.

## 4. Reporting

This is a competition/portfolio project without a production deployment. If
you find a security problem, please open a GitHub issue.

---

## Türkçe özet

Bu depo su an bir simulasyon + firmware iskeleti oldugundan web tabanli
guvenlik aciklarinin (SQL enjeksiyonu, CORS, acikta kalan debug ucnoktalari,
eksik yetki kontrolu) hedef alacagi bir yuzey yok. Onemli noktalar:

1. **OUI/MAC beyaz listesi kimlik dogrulama degildir** — MAC adresi taklit
   edilebilir ve modern cihazlar MAC adresini rastgeleleyebilir. Bu katman
   bir "izinsiz giris sinyali"dir, erisim kontrolu karari degildir.
2. **Firmware guvenli tarafta kalmalidir** — ultrasonik sensorden yanit
   gelmemesi artik "yol acik" olarak yorumlanmiyor; cizgi kaybinda arac
   korumasiz duz gitmek yerine duruyor. Saha kullanimindan once ultrasonik
   sensore bagli olmayan bagimsiz bir donanim guvenligi (tampon limit
   svici, acil stop) eklenmelidir.
3. **Sirlar depoya girmez** — WiFi/telemetri bilgileri surum kontrolune
   girmeyen `gizli_ayarlar.h` icinde tutulur; bagimliliklar sabit surumlere
   sabitlenmistir.
