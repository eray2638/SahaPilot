"""Unit tests for ``simulasyon/sekil2_pid_serit_takibi.py``.

Checks the sinusoidal reference model, its analytic derivative, and that the
double-integrator PD simulation actually tracks the reference better when
well-tuned (Kp=4, Kd=2) than when weakly tuned.
"""
import numpy as np

import sekil2_pid_serit_takibi as pid


class TestReferans:
    def test_sifirda_sifir(self):
        assert pid.referans(0.0) == 0.0

    def test_ceyrek_periyotta_genlige_ulasir(self):
        assert np.isclose(pid.referans(6.0, genlik=2.0, periyot=24.0), 2.0)

    def test_periyodiktir(self):
        assert np.isclose(pid.referans(5.0), pid.referans(5.0 + 24.0))

    def test_genlik_sinirlari_icinde_kalir(self):
        x = np.linspace(0, 60, 500)
        assert np.max(np.abs(pid.referans(x))) <= 2.0 + 1e-9

    def test_dizi_girdisi_ayni_sekli_dondurur(self):
        x = np.linspace(0, 10, 17)
        assert pid.referans(x).shape == x.shape


class TestReferansTurev:
    def test_sifirda_maksimum_egim(self):
        beklenen = 2.0 * (2 * np.pi / 24.0)
        assert np.isclose(pid.referans_turev(0.0), beklenen)

    def test_ceyrek_periyotta_egim_sifir(self):
        assert np.isclose(pid.referans_turev(6.0), 0.0)

    def test_sayisal_turevle_uyusur(self):
        x = np.linspace(0, 24, 50)
        h = 1e-6
        sayisal = (pid.referans(x + h) - pid.referans(x - h)) / (2 * h)
        assert np.allclose(pid.referans_turev(x), sayisal, atol=1e-5)


class TestSimuleEt:
    def test_cikti_boyutlari(self):
        x, y = pid.simule_et(Kp=4.0, Kd=2.0, x_son=10.0, dx=0.02)
        adim = int(10.0 / 0.02)
        assert x.shape == y.shape == (adim,)
        assert x[0] == 0.0 and np.isclose(x[-1], 10.0)

    def test_sifir_baslangic_kosulu(self):
        _, y = pid.simule_et(Kp=4.0, Kd=2.0, x_son=5.0)
        assert y[0] == 0.0

    def test_kazanc_sifirsa_arac_hic_hareket_etmez(self):
        _, y = pid.simule_et(Kp=0.0, Kd=0.0, x_son=5.0)
        assert np.allclose(y, 0.0)

    def test_iyi_ayarli_kontrolcu_seridi_takip_eder(self):
        x, y = pid.simule_et(Kp=4.0, Kd=2.0)
        r = pid.referans(x)
        yerlesmis = x > 10.0
        assert np.max(np.abs(y[yerlesmis] - r[yerlesmis])) < 0.5

    def test_iyi_ayar_zayif_ayardan_daha_az_hata_yapar(self):
        x, y_iyi = pid.simule_et(Kp=4.0, Kd=2.0)
        _, y_zayif = pid.simule_et(Kp=0.5, Kd=0.05)
        r = pid.referans(x)
        assert np.mean(np.abs(y_iyi - r)) < np.mean(np.abs(y_zayif - r))

    def test_cozum_sinirli_kalir(self):
        _, y = pid.simule_et(Kp=4.0, Kd=2.0)
        assert np.all(np.isfinite(y))
        assert np.max(np.abs(y)) < 10.0


class TestUretVeCiz:
    def test_figur_dosyasi_olusturulur(self, tmp_path, capsys):
        dosya = tmp_path / "sekil2.png"
        pid.uret_ve_ciz(str(dosya))
        assert dosya.exists() and dosya.stat().st_size > 0
        assert str(dosya) in capsys.readouterr().out
