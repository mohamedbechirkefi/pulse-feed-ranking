# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""Exploratory toolchain smoke test (M0). It checks only that the locked environment imports; it tests no research code."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_package_imports():
    import pulse

    assert pulse.__version__ == "0.0.0"


def test_seeded_rng_is_deterministic():
    a = np.random.default_rng(np.random.SeedSequence(20261124)).random(5)
    b = np.random.default_rng(np.random.SeedSequence(20261124)).random(5)
    assert np.array_equal(a, b)
