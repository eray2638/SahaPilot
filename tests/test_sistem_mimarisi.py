"""Unit tests for ``simulasyon/sekil1_sistem_mimarisi.py``.

That script draws the architecture diagram at module scope, so it is imported
from inside a temporary working directory (the import writes the PNG next to
the current directory).  The ``box``/``arrow`` helpers are then tested
directly.
"""
import importlib
import os

import matplotlib.pyplot as plt
import pytest
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


@pytest.fixture(scope="module")
def mimari(tmp_path_factory):
    """Imports the script from a temp cwd; yields (modul, cikti_dizini)."""
    dizin = tmp_path_factory.mktemp("sekil1")
    eski = os.getcwd()
    os.chdir(dizin)
    try:
        yield importlib.import_module("sekil1_sistem_mimarisi"), dizin
    finally:
        os.chdir(eski)
        plt.close("all")


def test_import_figur_dosyasini_yazar(mimari):
    _, dizin = mimari
    dosya = dizin / "sekil1_sistem_mimarisi.png"
    assert dosya.exists() and dosya.stat().st_size > 0


def test_box_tek_satir_metin_ekler(mimari):
    modul, _ = mimari
    _, ax = plt.subplots()
    modul.box(ax, 0, 0, 2, 1, "Baslik")
    assert len([p for p in ax.patches if isinstance(p, FancyBboxPatch)]) == 1
    assert [t.get_text() for t in ax.texts] == ["Baslik"]
    plt.close("all")


def test_box_alt_metinle_iki_satir_ekler(mimari):
    modul, _ = mimari
    _, ax = plt.subplots()
    modul.box(ax, 0, 0, 2, 1, "Baslik", subtext="Aciklama")
    assert [t.get_text() for t in ax.texts] == ["Baslik", "Aciklama"]
    assert ax.texts[0].get_position()[1] > ax.texts[1].get_position()[1]
    plt.close("all")


def test_arrow_ok_ekler(mimari):
    modul, _ = mimari
    _, ax = plt.subplots()
    modul.arrow(ax, 0, 0, 1, 1, color="#123456")
    oklar = [p for p in ax.patches if isinstance(p, FancyArrowPatch)]
    assert len(oklar) == 1
    plt.close("all")
