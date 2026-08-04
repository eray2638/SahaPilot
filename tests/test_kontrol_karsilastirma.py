"""Unit tests for ``simulasyon/sekil3_kontrol_karsilastirma.py``.

Verifies the three control strategies behave as the report claims: PD settles,
while bang-bang and pure-proportional keep oscillating.
"""
import numpy as np
import pytest

import sekil3_kontrol_karsilastirma as kk


def yerlesme_hatasi(e, t, t_baslangic):
    return np.max(np.abs(e[t > t_baslangic]))


class TestSimuleEt:
    @pytest.mark.parametrize("strateji", ["bangbang", "p", "pd"])
    def test_cikti_boyutlari_ve_baslangic_hatasi(self, strateji):
        t, e = kk.simule_et(strateji)
        adim = int(kk.T_SON / kk.DT)
        assert t.shape == e.shape == (adim,)
        assert e[0] == 1.0
        assert np.all(np.isfinite(e))

    def test_bilinmeyen_strateji_hata_verir(self):
        with pytest.raises(ValueError):
            kk.simule_et("bilinmeyen")

    def test_pd_iki_saniyede_yatisir(self):
        t, e = kk.simule_et("pd")
        assert yerlesme_hatasi(e, t, 2.0) < 0.2
        assert yerlesme_hatasi(e, t, 5.0) < 0.01

    def test_bangbang_yatismaz(self):
        t, e = kk.simule_et("bangbang")
        assert yerlesme_hatasi(e, t, 2.0) > 0.1

    def test_orantisal_kontrol_sonumsuz_salinim_yapar(self):
        t, e = kk.simule_et("p")
        assert yerlesme_hatasi(e, t, 2.0) > 0.5

    def test_orantisal_salinim_genligi_korunur(self):
        """Sondurme olmadigi icin genlik zamanla azalmaz."""
        t, e = kk.simule_et("p")
        ilk_yari = np.max(np.abs(e[t < kk.T_SON / 2]))
        son_yari = np.max(np.abs(e[t > kk.T_SON / 2]))
        assert son_yari == pytest.approx(ilk_yari, rel=0.1)

    def test_pd_en_kucuk_ortalama_hataya_sahiptir(self):
        _, e_bb = kk.simule_et("bangbang")
        _, e_p = kk.simule_et("p")
        _, e_pd = kk.simule_et("pd")
        ortalama = lambda e: np.mean(np.abs(e))
        assert ortalama(e_pd) < ortalama(e_bb)
        assert ortalama(e_pd) < ortalama(e_p)

    def test_bangbang_ve_p_isaret_degistirir(self):
        for strateji in ("bangbang", "p"):
            _, e = kk.simule_et(strateji)
            assert np.min(e) < 0 < np.max(e)


class TestUretVeCiz:
    def test_figur_dosyasi_olusturulur(self, tmp_path, capsys):
        dosya = tmp_path / "sekil3.png"
        kk.uret_ve_ciz(str(dosya))
        assert dosya.exists() and dosya.stat().st_size > 0
        assert str(dosya) in capsys.readouterr().out
