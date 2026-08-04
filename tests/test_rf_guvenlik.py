"""Unit tests for ``simulasyon/sekil4_rf_guvenlik.py``.

Focus on ``tespit_algoritmasi`` (the consecutive-scan confirmation logic that
suppresses false alarms) and on the determinism / shape of the synthetic scan
generator, plus a smoke test of the figure generation.
"""
import sekil4_rf_guvenlik as rf

BILINEN = rf.BILINEN_OUI[0]
YETKISIZ = rf.YETKISIZ_OUI


def tarama(*ouiler):
    return [(oui, -60.0) for oui in ouiler]


class TestTespitAlgoritmasi:
    def test_yabanci_cihaz_yoksa_tespit_olmaz(self):
        olcumler = [tarama(BILINEN) for _ in range(10)]
        kesin_t, gecmis, yanlis_alarm = rf.tespit_algoritmasi(olcumler)
        assert kesin_t is None
        assert gecmis == [False] * 10
        assert yanlis_alarm == 0

    def test_bos_olcum_listesi(self):
        assert rf.tespit_algoritmasi([]) == (None, [], 0)

    def test_esik_alti_ardisik_gorulme_tespit_saymaz(self):
        olcumler = [tarama(BILINEN, YETKISIZ)] * (rf.ARDISIK_ESIK - 1)
        kesin_t, gecmis, yanlis_alarm = rf.tespit_algoritmasi(olcumler)
        assert kesin_t is None
        assert not any(gecmis)
        assert yanlis_alarm == 0

    def test_esige_ulasan_ardisik_gorulme_tespit_eder(self):
        olcumler = [tarama(BILINEN, YETKISIZ)] * rf.ARDISIK_ESIK
        kesin_t, gecmis, _ = rf.tespit_algoritmasi(olcumler)
        assert kesin_t == rf.ARDISIK_ESIK - 1
        assert gecmis == [False] * (rf.ARDISIK_ESIK - 1) + [True]

    def test_arada_kesilen_gorulmeler_sayaci_sifirlar(self):
        olcumler = (
            [tarama(BILINEN, YETKISIZ)] * (rf.ARDISIK_ESIK - 1)
            + [tarama(BILINEN)]
            + [tarama(BILINEN, YETKISIZ)] * (rf.ARDISIK_ESIK - 1)
        )
        kesin_t, gecmis, yanlis_alarm = rf.tespit_algoritmasi(olcumler)
        assert kesin_t is None
        assert not any(gecmis)
        assert yanlis_alarm == 0

    def test_kesin_tespit_ilk_tespit_aninda_sabitlenir(self):
        olcumler = [tarama(BILINEN, YETKISIZ)] * (rf.ARDISIK_ESIK + 5)
        kesin_t, gecmis, _ = rf.tespit_algoritmasi(olcumler)
        assert kesin_t == rf.ARDISIK_ESIK - 1
        assert all(gecmis[rf.ARDISIK_ESIK - 1:])

    def test_erken_tespit_yanlis_alarm_olarak_sayilir(self):
        """t <= T_YABANCI_BASLAR icindeki her tespit adimi yanlis alarmdir."""
        adet = rf.T_YABANCI_BASLAR + 1
        olcumler = [tarama(BILINEN, YETKISIZ)] * adet
        kesin_t, _, yanlis_alarm = rf.tespit_algoritmasi(olcumler)
        assert kesin_t == rf.ARDISIK_ESIK - 1
        assert yanlis_alarm == rf.T_YABANCI_BASLAR + 1 - (rf.ARDISIK_ESIK - 1)

    def test_yalnizca_yetkisiz_oui_tetikler(self):
        digerleri = [o for o in rf.BILINEN_OUI]
        olcumler = [tarama(*digerleri)] * (rf.ARDISIK_ESIK + 2)
        assert rf.tespit_algoritmasi(olcumler)[0] is None


class TestTaramalariUret:
    def test_tarama_sayisi_ve_bilinen_cihazlar(self):
        olcumler = rf.taramalari_uret()
        assert len(olcumler) == rf.N
        for oui_listesi in olcumler:
            ouiler = [oui for oui, _ in oui_listesi]
            for bilinen in rf.BILINEN_OUI:
                assert bilinen in ouiler

    def test_yabanci_cihaz_esikten_once_hic_gorunmez(self):
        olcumler = rf.taramalari_uret()
        for t in range(rf.T_YABANCI_BASLAR + 1):
            assert all(oui != rf.YETKISIZ_OUI for oui, _ in olcumler[t])

    def test_yabanci_cihaz_esikten_sonra_gorunur(self):
        olcumler = rf.taramalari_uret()
        sonra = [
            t
            for t in range(rf.T_YABANCI_BASLAR + 1, rf.N)
            if any(oui == rf.YETKISIZ_OUI for oui, _ in olcumler[t])
        ]
        assert sonra

    def test_ayni_seed_ayni_sonucu_verir(self):
        assert rf.taramalari_uret(seed=3) == rf.taramalari_uret(seed=3)

    def test_farkli_seed_farkli_sonuc_verir(self):
        assert rf.taramalari_uret(seed=3) != rf.taramalari_uret(seed=4)

    def test_bilinen_cihaz_rssi_araligi(self):
        for oui_listesi in rf.taramalari_uret():
            for oui, rssi in oui_listesi:
                if oui != rf.YETKISIZ_OUI:
                    assert -80 <= rssi <= -40

    def test_yabanci_cihaz_yaklastikca_sinyal_guclenir(self):
        olcumler = rf.taramalari_uret()
        seri = [
            (t, rssi)
            for t, oui_listesi in enumerate(olcumler)
            for oui, rssi in oui_listesi
            if oui == rf.YETKISIZ_OUI
        ]
        assert len(seri) >= 2
        assert all(a[1] < b[1] for a, b in zip(seri, seri[1:]))
        assert seri[0][1] >= -92


class TestVarsayilanSenaryo:
    def test_yanlis_alarmsiz_ve_esikten_kisa_sure_sonra_tespit(self):
        kesin_t, _, yanlis_alarm = rf.tespit_algoritmasi(rf.taramalari_uret())
        assert yanlis_alarm == 0
        assert kesin_t is not None
        assert rf.T_YABANCI_BASLAR < kesin_t <= rf.T_YABANCI_BASLAR + 5


class TestUretVeCiz:
    def test_figur_dosyasi_olusturulur(self, tmp_path, capsys):
        dosya = tmp_path / "sekil4.png"
        rf.uret_ve_ciz(str(dosya))
        assert dosya.exists() and dosya.stat().st_size > 0
        cikti = capsys.readouterr().out
        assert str(dosya) in cikti
        assert "Yanlis alarm sayisi" in cikti
