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

T_SON = 15.0
DT    = 0.002
U_SABIT = 1.2     # bang-bang icin sabit kuvvet buyuklugu
KP = 4.0
KD = 2.0


def simule_et(strateji):
    adim = int(T_SON / DT)
    t = np.linspace(0, T_SON, adim)
    e  = np.zeros(adim)   # hata (referans - konum)
    ev = np.zeros(adim)   # hata hizi
    e[0] = 1.0

    for i in range(1, adim):
        if strateji == "bangbang":
            u = U_SABIT if e[i - 1] > 0 else -U_SABIT
        elif strateji == "p":
            u = KP * e[i - 1]
        elif strateji == "pd":
            u = KP * e[i - 1] + KD * ev[i - 1]
        else:
            raise ValueError("bilinmeyen strateji")

        # y'' = u  ->  e'' = -u  (hata azaltma yonunde ivme)
        ev[i] = ev[i - 1] - u * DT
        e[i]  = e[i - 1] + ev[i - 1] * DT

    return t, e


def uret_ve_ciz(dosya_adi="sekil3_kontrol_karsilastirma.png"):
    t, e_bb = simule_et("bangbang")
    _, e_p  = simule_et("p")
    _, e_pd = simule_et("pd")

    plt.figure(figsize=(9, 4.5))
    plt.plot(t, e_bb, linewidth=1.2, label="Bang-bang (surekli salinir)")
    plt.plot(t, e_p,  linewidth=1.2, label="Sadece P (sonmeyen salinim)")
    plt.plot(t, e_pd, linewidth=2.0, label="PD (t~2s'de yatisir)")
    plt.axhline(0, color="gray", linewidth=0.8)
    plt.xlabel("Zaman (s)")
    plt.ylabel("Yanal hata e(t)")
    plt.title("Sekil 3 - Bang-Bang / P / PD Kontrol Karsilastirmasi")
    plt.legend(loc="upper right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(dosya_adi, dpi=140)
    print("Kaydedildi:", dosya_adi)


if __name__ == "__main__":
    uret_ve_ciz()
