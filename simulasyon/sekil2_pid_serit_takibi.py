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
    y = np.zeros(adim)
    yv = np.zeros(adim)   # yanal hiz (y')

    for i in range(1, adim):
        r  = referans(x[i - 1])
        rv = referans_turev(x[i - 1])
        hata      = r - y[i - 1]
        hata_hizi = rv - yv[i - 1]
        ivme = Kp * hata + Kd * hata_hizi
        yv[i] = yv[i - 1] + ivme * dx
        y[i]  = y[i - 1] + yv[i - 1] * dx

    return x, y


def uret_ve_ciz(dosya_adi="sekil2_pid_serit_takibi.png"):
    x, y_iyi  = simule_et(Kp=4.0, Kd=2.0)
    _, y_zayif = simule_et(Kp=0.5, Kd=0.05)
    r = referans(x)

    plt.figure(figsize=(9, 4.5))
    plt.plot(x, r, "k--", linewidth=1.2, label="Reference line")
    plt.plot(x, y_iyi, linewidth=2.0, label="PD control (Kp=4, Kd=2)")
    plt.plot(x, y_zayif, linewidth=1.4, label="Weakly-tuned control (Kp=0.5, Kd=0.05)")
    plt.xlabel("Forward distance (m)")
    plt.ylabel("Lateral position (m)")
    plt.title("Figure 2 - PD-Controlled Line Tracking")
    plt.legend(loc="upper right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(dosya_adi, dpi=140)
    print("Kaydedildi:", dosya_adi)


if __name__ == "__main__":
    uret_ve_ciz()
