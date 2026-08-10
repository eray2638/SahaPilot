"""Shared pytest setup for the SahaPilot simulation tests.

The simulation scripts live in ``simulasyon/`` as top-level scripts (no
package), so that directory is put on ``sys.path``.  Matplotlib is forced onto
the headless ``Agg`` backend before any simulation module is imported.
"""
import os
import sys
from pathlib import Path

import matplotlib

os.environ.setdefault("MPLBACKEND", "Agg")
matplotlib.use("Agg", force=True)

SIMULASYON_DIZINI = Path(__file__).resolve().parent.parent / "simulasyon"
if str(SIMULASYON_DIZINI) not in sys.path:
    sys.path.insert(0, str(SIMULASYON_DIZINI))
