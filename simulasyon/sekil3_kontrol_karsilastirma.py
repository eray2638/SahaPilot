"""
Sekil 3 - Kontrol Yontemi Karsilastirmasi (Bang-Bang / P / PD)
============================================================
Ayni baslangic hatasindan (e(0) = 1) yola cikan uc farkli kontrol
stratejisinin zaman icinde hatayi nasil sifira (ya da sifira yakin
bir degere) getirdigini karsilastirir.

- Bang-bang : sadece hatanin isaretine bakar, sabit kuvvetle iter
              (u = +U ya da -U). Surekli salinim yapar, hic yatismaz.
- P (orantisal)  : u = -Kp * e. Hatayla orantili tepki verir ama
              sondurme (damping) olmadigi icin salinim devam eder.
- PD (orantisal-turevsel): u = -Kp*e - Kd*e'. Turev terimi salinimi
              sondurur, hata hizla sifira yaklasir.

Model yine y'' = u seklinde basit bir cift entegratordur.
============================================================
"""
import numpy as np
import matplotlib.pyplot as plt

from saha_ortak import pd_kontrol, cift_entegrator, grafik_kaydet

T_SON = 15.0
DT    = 0.002
U_SABIT = 1.2     # bang-bang icin sabit kuvvet buyuklugu
KP = 4.0
KD = 2.0


def simule_et(strateji):
    adim = int(T_SON / DT)
    t = np.linspace(0, T_SON, adim)

    def ivme(i, e_onceki, ev_onceki):
        if strateji == "bangbang":
            u = U_SABIT if e_onceki > 0 else -U_SABIT
        elif strateji == "p":
            u = KP * e_onceki
        elif strateji == "pd":
            u = pd_kontrol(e_onceki, ev_onceki, KP, KD)
        else:
            raise ValueError("bilinmeyen strateji")
        # y'' = u  ->  e'' = -u  (hata azaltma yonunde ivme)
        return -u

    # e (hata) baslangic degeri 1.0; hiz 0.
    e, _ = cift_entegrator(ivme, adim, DT, y0=1.0)
    return t, e


def uret_ve_ciz(dosya_adi="sekil3_kontrol_karsilastirma.png"):
    t, e_bb = simule_et("bangbang")
    _, e_p  = simule_et("p")
    _, e_pd = simule_et("pd")

    plt.figure(figsize=(9, 4.5))
    plt.plot(t, e_bb, linewidth=1.2, label="Bang-bang (sustained oscillation)")
    plt.plot(t, e_p,  linewidth=1.2, label="Proportional only (undamped oscillation)")
    plt.plot(t, e_pd, linewidth=2.0, label="PD (settles by t~2s)")
    plt.axhline(0, color="gray", linewidth=0.8)
    grafik_kaydet(dosya_adi,
                  "Time (s)", "Lateral error e(t)",
                  "Figure 3 - Bang-Bang / P / PD Control Comparison")


if __name__ == "__main__":
    uret_ve_ciz()
