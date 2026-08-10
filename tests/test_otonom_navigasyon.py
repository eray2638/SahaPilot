"""Unit tests for ``simulasyon/otonom_kodu_duzeltilmis.py``.

Covers the sensor models (``ir_oku``, ``ultrasonik_oku``), the two decision
functions (``serit_takip``, ``engelden_kac``), the world generators and the
main loop.  ``test_main_dongusu_carpismasiz`` is the regression test for the
collision bug documented in the module docstring (1009 collisions -> 0).
"""
import random

import pytest

import otonom_kodu_duzeltilmis as nav


class TestIrOku:
    def test_serit_ortada(self):
        assert nav.ir_oku(5, 5) == (False, True, False)

    def test_serit_solda(self):
        assert nav.ir_oku(5, 4) == (True, False, False)

    def test_serit_sagda(self):
        assert nav.ir_oku(5, 6) == (False, False, True)

    def test_serit_menzil_disinda(self):
        assert nav.ir_oku(5, 9) == (False, False, False)


class TestUltrasonikOku:
    def test_engel_yoksa_lookahead_disi_deger(self):
        assert nav.ultrasonik_oku(5, 0, {}) == (nav.LOOKAHEAD + 1, None)

    def test_en_yakin_engeli_bulur(self):
        engeller = {3: {5}, 5: {5}}
        assert nav.ultrasonik_oku(5, 2, engeller) == (1, 3)

    def test_baska_sutundaki_engeli_gormez(self):
        engeller = {3: {7}}
        assert nav.ultrasonik_oku(5, 2, engeller) == (nav.LOOKAHEAD + 1, None)

    def test_o_anki_satiri_kontrol_etmez(self):
        """Sensör bilinçli olarak yalnızca ileriye bakar; satır ``f`` main()
        içindeki son-an kontrolüne bırakılmıştır."""
        engeller = {4: {5}}
        assert nav.ultrasonik_oku(5, 4, engeller) == (nav.LOOKAHEAD + 1, None)

    def test_lookahead_sinirinin_otesini_gormez(self):
        engeller = {0 + nav.LOOKAHEAD + 1: {5}}
        assert nav.ultrasonik_oku(5, 0, engeller) == (nav.LOOKAHEAD + 1, None)

    def test_lookahead_sinirindaki_engeli_gorur(self):
        engeller = {nav.LOOKAHEAD: {5}}
        assert nav.ultrasonik_oku(5, 0, engeller) == (nav.LOOKAHEAD, nav.LOOKAHEAD)


class TestSeritTakip:
    def test_orta_sensor_duz_gider(self):
        assert nav.serit_takip(5, 5) == 5

    def test_sol_sensor_sola_kayar(self):
        assert nav.serit_takip(5, 4) == 4

    def test_sag_sensor_saga_kayar(self):
        assert nav.serit_takip(5, 6) == 6

    @pytest.mark.parametrize("serit_x, beklenen", [(10, 6), (1, 4)])
    def test_serit_kaybedilince_son_yone_arar(self, serit_x, beklenen):
        assert nav.serit_takip(5, serit_x) == beklenen


class TestEngeldenKac:
    def test_tam_merkezde_saga_kayar(self):
        """``yol_uret`` araci tam merkezden baslattigi icin bu esik onemli."""
        merkez = nav.GENISLIK // 2
        assert nav.engelden_kac(merkez, 4, {4: {merkez}}) == merkez + 1

    def test_iki_yan_bos_sag_yariday_sola_kayar(self):
        robot_x = nav.GENISLIK // 2 + 1
        assert nav.engelden_kac(robot_x, 4, {4: {robot_x}}) == robot_x - 1

    def test_iki_yan_bos_sol_yariday_saga_kayar(self):
        robot_x = nav.GENISLIK // 2 - 1
        assert nav.engelden_kac(robot_x, 4, {4: {robot_x}}) == robot_x + 1

    def test_sadece_sol_bos(self):
        assert nav.engelden_kac(5, 4, {4: {5, 6}}) == 4

    def test_sadece_sag_bos(self):
        assert nav.engelden_kac(5, 4, {4: {4, 5}}) == 6

    def test_her_iki_yan_kapali_bekler(self):
        assert nav.engelden_kac(5, 4, {4: {4, 5, 6}}) == 5

    def test_sol_kenarda_saga_kacar(self):
        assert nav.engelden_kac(0, 4, {4: {0}}) == 1

    def test_sag_kenarda_sola_kacar(self):
        son = nav.GENISLIK - 1
        assert nav.engelden_kac(son, 4, {4: {son}}) == son - 1


class TestDunyaUretimi:
    def test_yol_uzunlugu_ve_sinirlari(self):
        random.seed(0)
        yol = nav.yol_uret(nav.ADIM)
        assert len(yol) == nav.ADIM + nav.LOOKAHEAD + 1
        assert all(2 <= x <= nav.GENISLIK - 3 for x in yol)

    def test_yol_adim_basina_en_fazla_bir_hucre_kayar(self):
        random.seed(1)
        yol = nav.yol_uret(nav.ADIM)
        assert all(abs(b - a) <= 1 for a, b in zip(yol, yol[1:]))

    def test_engeller_serit_uzerine_ve_gecerli_araliga_konur(self):
        random.seed(2)
        yol = nav.yol_uret(nav.ADIM)
        engeller = nav.engel_uret(yol, nav.ADIM)
        assert engeller
        for satir, hucreler in engeller.items():
            assert 10 <= satir < nav.ADIM - nav.LOOKAHEAD
            assert yol[satir] in hucreler
            assert all(0 <= h < nav.GENISLIK for h in hucreler)
            assert len(hucreler) <= 2

    def test_engel_satirlari_arasinda_bosluk_var(self):
        random.seed(3)
        yol = nav.yol_uret(nav.ADIM)
        satirlar = sorted(nav.engel_uret(yol, nav.ADIM))
        assert all(8 <= b - a <= 12 for a, b in zip(satirlar, satirlar[1:]))


class TestKareyiCiz:
    def test_robot_engel_ve_serit_isaretlenir(self, capsys):
        yol = [3] * 20
        engeller = {1: {7}}
        nav.kareyi_ciz(3, 0, yol, engeller, "SERIT TAKIP", 2)
        cikti = capsys.readouterr().out
        satirlar = [s for s in cikti.splitlines() if s.startswith("|")]
        assert len(satirlar) == nav.LOOKAHEAD + 1
        assert satirlar[-1][1 + 3] == "O"          # robot alt satirda
        assert satirlar[-2][1 + 7] == "#"          # engel bir ust satirda
        assert satirlar[0][1 + 3] == "."           # serit
        assert "SERIT TAKIP" in cikti and "2 adim" in cikti


class TestMainDongusu:
    @staticmethod
    def _izle(monkeypatch, seed):
        """main()'i çalıştırır ve (satır, robot_x, engeller) izini döndürür."""
        random.seed(seed)
        monkeypatch.setattr(nav.time, "sleep", lambda _s: None)
        iz = []

        def kaydet(robot_x, f, yol, engeller, durum, mesafe):
            iz.append((f, robot_x, engeller))

        monkeypatch.setattr(nav, "kareyi_ciz", kaydet)
        nav.main()
        return iz

    def test_main_dongusu_carpismasiz(self, monkeypatch):
        """Düzeltilmiş sürüm 200 rastgele senaryoda hiç çarpışmamalı."""
        for seed in range(200):
            for f, robot_x, engeller in self._izle(monkeypatch, seed):
                assert robot_x not in engeller.get(f, set()), (
                    f"seed={seed} satir={f} konum={robot_x} engele carpti"
                )

    def test_main_her_adimi_cizer_ve_sinirlarda_kalir(self, monkeypatch):
        iz = self._izle(monkeypatch, 42)
        assert [f for f, _, _ in iz] == list(range(nav.ADIM))
        assert all(0 <= robot_x < nav.GENISLIK for _, robot_x, _ in iz)

    def test_main_adim_basina_en_fazla_bir_hucre_hareket_eder(self, monkeypatch):
        konumlar = [robot_x for _, robot_x, _ in self._izle(monkeypatch, 7)]
        assert all(abs(b - a) <= 1 for a, b in zip(konumlar, konumlar[1:]))

    def test_main_tamamlandi_mesajini_basar(self, monkeypatch, capsys):
        random.seed(11)
        monkeypatch.setattr(nav.time, "sleep", lambda _s: None)
        monkeypatch.setattr(nav, "kareyi_ciz", lambda *a, **k: None)
        nav.main()
        assert "Simulasyon tamamlandi." in capsys.readouterr().out
