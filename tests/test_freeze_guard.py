# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""The run guard accepts the frozen confirmatory configs and refuses any changed artifact.
No test here executes a simulation of a confirmatory config."""
from __future__ import annotations

import json
import shutil

import pytest

from pulse import cli
from pulse.manifest import REPO_ROOT
from pulse.runner import ProtocolNotFrozen, execute, load_experiment, protocol_frozen

EXPS = ("EXP-001", "EXP-002", "EXP-003", "EXP-004")
FROZEN = (REPO_ROOT / "research" / "freeze.json").exists()


def copy_repo(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(REPO_ROOT / "research", root / "research")
    shutil.copytree(REPO_ROOT / "experiments", root / "experiments")
    (root / "data").mkdir()
    shutil.copy(REPO_ROOT / "data" / "manifest.json", root / "data" / "manifest.json")
    return root


@pytest.mark.parametrize("name", EXPS)
def test_live_repository_guard_state(name):
    exp = load_experiment(REPO_ROOT / "experiments" / f"{name}.json")
    ok, why = protocol_frozen(name, REPO_ROOT, exp)
    if FROZEN:
        assert ok, why  # the frozen configs are accepted
    else:
        assert not ok and "DRAFT" in why


@pytest.mark.skipif(not FROZEN, reason="no freeze record yet")
@pytest.mark.parametrize("name", EXPS)
def test_changed_artifacts_are_refused(tmp_path, name):
    root = copy_repo(tmp_path)
    exp = load_experiment(root / "experiments" / f"{name}.json")
    assert protocol_frozen(name, root, exp)[0]

    changed = json.loads(json.dumps(exp))
    changed["seeds"]["count"] = 19
    ok, why = protocol_frozen(name, root, changed)
    assert not ok and "differs from the frozen config" in why
    with pytest.raises(ProtocolNotFrozen):
        execute(changed, root=root, out_dir=tmp_path / "out")
    assert not (tmp_path / "out").exists()

    for rel in (f"experiments/{name}.json", "research/protocol.md", "data/manifest.json",
                f"research/experiments/{name}/protocol.md"):
        r2 = copy_repo(tmp_path / rel.replace("/", "_"))
        f = r2 / rel
        f.write_bytes(f.read_bytes() + b"\n")
        ok, why = protocol_frozen(name, r2, exp)
        assert not ok, rel


@pytest.mark.skipif(not FROZEN, reason="no freeze record yet")
def test_cli_refuses_changed_config(tmp_path):
    exp = json.loads((REPO_ROOT / "experiments" / "EXP-001.json").read_text())
    exp["base"]["like_midpoint"] = 0.5
    p = tmp_path / "EXP-001.json"
    p.write_text(json.dumps(exp))
    assert cli.main(["run", "--config", str(p), "--out", str(tmp_path / "o")]) == 3
    assert not (tmp_path / "o").exists()


def test_unfrozen_copy_is_refused(tmp_path):
    root = copy_repo(tmp_path)
    proto = root / "research" / "protocol.md"
    proto.write_text("**Status: DRAFT**\n" + proto.read_text())
    exp = load_experiment(root / "experiments" / "EXP-001.json")
    assert not protocol_frozen("EXP-001", root, exp)[0]
    with pytest.raises(ProtocolNotFrozen):
        execute(exp, root=root, out_dir=tmp_path / "c")
    assert not (tmp_path / "c").exists()
