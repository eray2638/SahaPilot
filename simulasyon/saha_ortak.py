"""
Ortak simulasyon yardimcilari (shared simulation utilities)
============================================================
SahaPilot Python simulasyon betikleri (sekil2 / sekil3 / sekil4)
arasinda birebir tekrar eden kod parcalarini tek yerde toplar:

- pd_kontrol       : PD kontrol yasasi          (Kp*e + Kd*e')
- cift_entegrator  : ikinci-dereceden (double-integrator) sistemin
                     yari-ortuk (semi-implicit) Euler cozumu
- grafik_kaydet    : matplotlib eksen etiketleme + kaydetme kaliplari

Bu modul, ayni klasordeki betiklerin yaninda durur; betikler
`from saha_ortak import ...` seklinde ice aktarir.
============================================================
"""
import numpy as np
import matplotlib.pyplot as plt


def pd_kontrol(hata, hata_hizi, kp, kd):
    """PD kontrol ciktisi: Kp*hata + Kd*hata_hizi.

    Ayni yasa hem serit takibi (sekil2) hem de kontrol
    karsilastirmasindaki (sekil3) PD stratejisinde kullanilir;
    firmware'deki (sahapilot_firmware.ino) hesap da bununla ayni fikirdir.
    """
    return kp * hata + kd * hata_hizi


def cift_entegrator(ivme_fonk, adim, dt, y0=0.0, v0=0.0):
    """y'' = ivme(...) seklindeki ikinci-dereceden sistemi yari-ortuk
    (semi-implicit) Euler ile ayrik zamanda cozer.

    ivme_fonk(i, y_onceki, v_onceki) -> o adimdaki ivme (y'') degerini
    dondurmelidir. Konum (y) ve hiz (v) dizileri dondurulur.

    Guncelleme kalibi (her iki eski betikte de ayni):
        v[i] = v[i-1] + ivme * dt
        y[i] = y[i-1] + v[i-1] * dt
    """
    y = np.zeros(adim)
    v = np.zeros(adim)
    y[0] = y0
    v[0] = v0
    for i in range(1, adim):
        ivme = ivme_fonk(i, y[i - 1], v[i - 1])
        v[i] = v[i - 1] + ivme * dt
        y[i] = y[i - 1] + v[i - 1] * dt
    return y, v


def grafik_kaydet(dosya_adi, xlabel, ylabel, baslik,
                  legend_loc="upper right", legend_fontsize=None, dpi=140):
    """Betiklerde tekrar eden matplotlib son-islem kaliplari:
    eksen etiketleri, baslik, legend, grid, tight_layout, savefig ve
    "Kaydedildi:" bilgi ciktisi."""
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(baslik)
    if legend_fontsize is not None:
        plt.legend(loc=legend_loc, fontsize=legend_fontsize)
    else:
        plt.legend(loc=legend_loc)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(dosya_adi, dpi=dpi)
    print("Kaydedildi:", dosya_adi)
