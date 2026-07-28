"""
Sekil 4 - RF Guvenlik Katmani: Yetkisiz Cihaz Tespiti (OUI Tabanli)
============================================================
SahaPilot'un RF guvenlik katmani, cevredeki kablosuz cihazlarin
MAC adreslerinin ilk 3 baytina (OUI - Organizationally Unique
Identifier) bakarak "bilinen/yetkili" mi yoksa "yabanci" mi
oldugunu ayirt eder.

Yanlis alarmi azaltmak icin tek bir taramada yabanci OUI gorulmesi
yeterli sayilmaz; ardisik ARDISIK_ESIK kadar taramada ust uste
gorulmesi istenir (CFAR mantigindaki "ardisik dogrulama" fikrine
benzer bir yaklasim).
============================================================
"""
import random
import matplotlib.pyplot as plt

N = 60                       # toplam tarama sayisi
BILINEN_OUI = ["A4:C1:38", "3C:71:BF", "B8:27:EB"]
YETKISIZ_OUI = "DE:AD:BE"
ARDISIK_ESIK = 3
T_YABANCI_BASLAR = 30         # bu taramadan sonra yabanci cihaz belirebilir
P_YABANCI = 0.85              # t>30 sonrasi yabanci OUI gorulme olasiligi


def taramalari_uret(seed=7):
    random.seed(seed)
    olcumler = []   # her tarama icin (oui, rssi) listesi
    for t in range(N):
        oui_listesi = []
        # bilinen cihazlar her zaman gorunur
        for oui in BILINEN_OUI:
            rssi = random.uniform(-80, -40)
            oui_listesi.append((oui, rssi))
        # yabanci cihaz, t>30'dan sonra belirli bir olasilikla gorunur
        if t > T_YABANCI_BASLAR and random.random() < P_YABANCI:
            ilerleme = (t - T_YABANCI_BASLAR) / (N - T_YABANCI_BASLAR)
            rssi = -92 + ilerleme * (92 - 55)   # yaklastikca sinyal guclenir
            oui_listesi.append((YETKISIZ_OUI, rssi))
        olcumler.append(oui_listesi)
    return olcumler


def tespit_algoritmasi(olcumler):
    """Ardisik ARDISIK_ESIK taramada yetkisiz OUI gorulursen tespit say."""
    ardisik_sayac = 0
    kesin_tespit_t = None
    tespit_gecmisi = []
    yanlis_alarm = 0

    for t, oui_listesi in enumerate(olcumler):
        yabanci_var = any(oui == YETKISIZ_OUI for oui, _ in oui_listesi)
        if yabanci_var:
            ardisik_sayac += 1
        else:
            ardisik_sayac = 0

        tespit_edildi = ardisik_sayac >= ARDISIK_ESIK
        tespit_gecmisi.append(tespit_edildi)

        if tespit_edildi and kesin_tespit_t is None:
            kesin_tespit_t = t
        if tespit_edildi and t <= T_YABANCI_BASLAR:
            yanlis_alarm += 1

    return kesin_tespit_t, tespit_gecmisi, yanlis_alarm


def uret_ve_ciz(dosya_adi="sekil4_rf_guvenlik_tespiti.png"):
    olcumler = taramalari_uret()
    kesin_tespit_t, gecmis, yanlis_alarm = tespit_algoritmasi(olcumler)

    zaman = []
    rssi_yabanci = []
    for t, oui_listesi in enumerate(olcumler):
        for oui, rssi in oui_listesi:
            if oui == YETKISIZ_OUI:
                zaman.append(t)
                rssi_yabanci.append(rssi)

    zaman_bilinen = []
    rssi_bilinen = []
    for t, oui_listesi in enumerate(olcumler):
        for oui, rssi in oui_listesi:
            if oui != YETKISIZ_OUI:
                zaman_bilinen.append(t)
                rssi_bilinen.append(rssi)

    plt.figure(figsize=(9, 4.5))
    plt.scatter(zaman_bilinen, rssi_bilinen, s=14, color="tab:green",
                label="Known OUI (authorized device)")
    plt.scatter(zaman, rssi_yabanci, s=18, color="tab:red",
                label="Unknown OUI (potential threat)")
    plt.axvline(T_YABANCI_BASLAR, color="gray", linestyle="--", linewidth=1,
                label="Unauthorized device may enter field (t=30)")
    if kesin_tespit_t is not None:
        plt.axvline(kesin_tespit_t, color="tab:blue", linewidth=2,
                    label=f"Detection confirmed (3 consecutive matches, t={kesin_tespit_t})")
        plt.annotate("Detection confirmed",
                     xy=(kesin_tespit_t, -58),
                     xytext=(kesin_tespit_t + 3, -58),
                     fontsize=9)

    plt.xlabel("Scan step (t)")
    plt.ylabel("RSSI (dBm)")
    plt.title("Figure 4 - RF Security: Unauthorized Device Detection")
    plt.legend(loc="upper left", fontsize=8)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(dosya_adi, dpi=140)
    print("Kaydedildi:", dosya_adi)
    print("Kesin tespit taramasi:", kesin_tespit_t)
    print("Yanlis alarm sayisi (t<=30 icinde):", yanlis_alarm)


if __name__ == "__main__":
    uret_ve_ciz()
