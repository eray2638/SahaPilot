"""
Sekil 2 - PID ile Serit Takibi Simulasyonu
============================================================
Aracin (SahaPilot) yanal konumunu, sinuzoidal bir referans seride
(r(t)) takip ederken PD kontrolcu ile nasil davrandigini gosterir.

Model: cift entegratorlu (double-integrator) yanal dinamik
    y'' = Kp*(r - y) + Kd*(r' - y')
Burada y  -> aracin yanal konumu
       r  -> takip edilmesi gereken serit konumu (referans)
       Kp -> orantisal kazanc (hataya ne kadar sert tepki verilecegi)
       Kd -> turevsel kazanc (sondirme / titresimi azaltma)

Iyi ayarlanmis (Kp=4, Kd=2) ve zayif ayarlanmis (Kp=0.5, Kd=0.05)
kontrolcu karsilastirilir. Euler integrasyonu ile ayrik zamanda cozulur.
============================================================
"""
import numpy as np
import matplotlib.pyplot as plt

from saha_ortak import pd_kontrol, cift_entegrator, grafik_kaydet

# ---------------- REFERANS SERIT ----------------
def referans(x, genlik=2.0, periyot=24.0):
    """Ilerleme mesafesi x'e gore hafif kivrilan bir serit uretir."""
    return genlik * np.sin(2 * np.pi * x / periyot)


def referans_turev(x, genlik=2.0, periyot=24.0):
    """Serit egiminin x'e gore turevi (kontrolcu icin gerekli)."""
    return genlik * (2 * np.pi / periyot) * np.cos(2 * np.pi * x / periyot)


# ---------------- SIMULASYON ----------------
def simule_et(Kp, Kd, x_son=60.0, dx=0.02):
    """Verilen Kp/Kd ile aracin sinuzoidal seridi takibini simule eder."""
    adim = int(x_son / dx)
    x = np.linspace(0, x_son, adim)

    def ivme(i, y_onceki, v_onceki):
        hata      = referans(x[i - 1]) - y_onceki
        hata_hizi = referans_turev(x[i - 1]) - v_onceki
        return pd_kontrol(hata, hata_hizi, Kp, Kd)

    y, _ = cift_entegrator(ivme, adim, dx)
    return x, y


def uret_ve_ciz(dosya_adi="sekil2_pid_serit_takibi.png"):
    x, y_iyi  = simule_et(Kp=4.0, Kd=2.0)
    _, y_zayif = simule_et(Kp=0.5, Kd=0.05)
    r = referans(x)

    plt.figure(figsize=(9, 4.5))
    plt.plot(x, r, "k--", linewidth=1.2, label="Reference line")
    plt.plot(x, y_iyi, linewidth=2.0, label="PD control (Kp=4, Kd=2)")
    plt.plot(x, y_zayif, linewidth=1.4, label="Weakly-tuned control (Kp=0.5, Kd=0.05)")
    grafik_kaydet(dosya_adi,
                  "Forward distance (m)", "Lateral position (m)",
                  "Figure 2 - PD-Controlled Line Tracking")


if __name__ == "__main__":
    uret_ve_ciz()
