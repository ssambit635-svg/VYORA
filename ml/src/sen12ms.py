"""Turn SEN12MS toolbox train/test file lists into a paired-image manifest."""
from __future__ import annotations

import random
import re
from pathlib import Path

from ml.src.data import ManifestError, build_manifest


def _list_lines(path: Path) -> list[str]:
    if not path.is_file():
        raise ManifestError(f"SEN12MS split list not found: {path}")
    return [line.strip().replace("\\", "/") for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def _expand_s1_entries(data_root: Path, list_path: Path) -> list[Path]:
    files: set[Path] = set()
    for entry in _list_lines(list_path):
        candidate = Path(entry)
        candidate = candidate if candidate.is_absolute() else data_root / candidate
        if candidate.is_file():
            if "_s1_" in candidate.as_posix():
                files.add(candidate.resolve())
            elif "_s2_" in candidate.as_posix():
                paired = Path(candidate.as_posix().replace("_s2_", "_s1_"))
                if paired.is_file():
                    files.add(paired.resolve())
                else:
                    raise ManifestError(f"Could not map S2 list entry to S1: {candidate}")
            else:
                raise ManifestError(f"Split-list file must contain an _s1_ or _s2_ identifier: {candidate}")
        elif candidate.is_dir():
            files.update(p.resolve() for p in candidate.rglob("*.tif") if "_s1_" in p.as_posix())
            files.update(p.resolve() for p in candidate.rglob("*.tiff") if "_s1_" in p.as_posix())
        else:
            raise ManifestError(f"Could not find split-list entry under SEN12MS root: {candidate}")
    return sorted(files)


def _scene_group(path: Path) -> str:
    match = re.search(r"ROIs\d+", path.as_posix(), re.IGNORECASE)
    if match:
        return match.group(0)
    return path.name.split("_s1_")[0]


def _paired_rows(
    data_root: Path,
    list_path: Path,
    split: str,
    vv_band: int,
    vh_band: int,
    rgb_bands: tuple[int, int, int],
    optical_scale: float,
    licence_note: str,
) -> list[dict]:
    rows = []
    for s1_path in _expand_s1_entries(data_root, list_path):
        relative_s1 = s1_path.relative_to(data_root)
        s2_path = data_root / Path(relative_s1.as_posix().replace("_s1_", "_s2_"))
        if not s2_path.is_file():
            raise ManifestError(f"Missing matching Sentinel-2 tile for {s1_path}: expected {s2_path}")
        rows.append({
            "tile_id": s1_path.stem,
            "scene_group": _scene_group(s1_path),
            "split": split,
            "sar_path": relative_s1.as_posix(),
            "vv_band": vv_band,
            "vh_band": vh_band,
            "optical_path": s2_path.relative_to(data_root).as_posix(),
            "optical_bands": list(rgb_bands),
            "optical_scale": optical_scale,
            "source": "SEN12MS; exact release and acquisition details must be recorded",
            "licence": licence_note,
        })
    return rows


def create_sen12ms_manifest(
    data_root: str | Path,
    train_list: str | Path,
    test_list: str | Path,
    output_path: str | Path,
    *,
    vv_band: int,
    vh_band: int,
    rgb_bands: tuple[int, int, int],
    optical_scale: float,
    licence_note: str,
    validation_fraction: float = 0.1,
    seed: int = 42,
) -> Path:
    """Pair official lists; reserve whole training ROIs for validation.

    `rgb_bands` are explicit 1-based indexes and must be checked against the
    exact downloaded SEN12MS release. No classification labels are consumed.
    """
    if vv_band < 1 or vh_band < 1 or vv_band == vh_band:
        raise ManifestError("VV/VH indexes must be distinct, positive 1-based band numbers.")
    if len(rgb_bands) != 3 or min(rgb_bands) < 1 or len(set(rgb_bands)) != 3:
        raise ManifestError("RGB indexes must be three distinct positive 1-based band numbers in R,G,B order.")
    if optical_scale <= 0:
        raise ManifestError("optical_scale must be a positive divisor verified from the TIFF metadata.")
    root = Path(data_root).resolve()
    train_path = Path(train_list)
    test_path = Path(test_list)
    train_path = train_path if train_path.is_absolute() else root / train_path
    test_path = test_path if test_path.is_absolute() else root / test_path
    train_rows = _paired_rows(root, train_path, "train", vv_band, vh_band, rgb_bands, optical_scale, licence_note)
    test_rows = _paired_rows(root, test_path, "test", vv_band, vh_band, rgb_bands, optical_scale, licence_note)
    test_groups = {row["scene_group"] for row in test_rows}
    train_groups = {row["scene_group"] for row in train_rows}
    overlap = train_groups & test_groups
    if overlap:
        raise ManifestError(f"Official train/test lists share ROI groups: {sorted(overlap)[:5]}")
    if len(train_groups) < 2:
        raise ManifestError("Need at least two distinct training ROI groups to reserve validation scenes.")
    if not 0 < validation_fraction < 0.5:
        raise ManifestError("validation_fraction must be between 0 and 0.5.")
    groups = sorted(train_groups)
    random.Random(seed).shuffle(groups)
    validation_count = max(1, round(len(groups) * validation_fraction))
    validation_groups = set(groups[:validation_count])
    for row in train_rows:
        if row["scene_group"] in validation_groups:
            row["split"] = "validation"
    return build_manifest(train_rows + test_rows, output_path, root=root)
