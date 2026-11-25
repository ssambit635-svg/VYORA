import pytest

from ml.src.evaluate import manifest_input_representation, validate_checkpoint_manifest


def test_png_manifest_contract_uses_declared_grayscale_side():
    rows = [
        {"source": "SEN12MS A/B PNG export; input_side=B", "input_side": "B"},
        {"source": "SEN12MS A/B PNG export; input_side=B", "input_side": "B"},
    ]
    assert manifest_input_representation(rows) == "grayscale_B_PNG_duplicated"
    validate_checkpoint_manifest({"input_representation": "grayscale_B_PNG_duplicated"}, rows)


def test_evaluation_rejects_reversed_or_geotiff_checkpoint_mapping():
    rows = [{"source": "SEN12MS A/B PNG export", "input_side": "B"}]
    with pytest.raises(ValueError, match="Checkpoint expects"):
        validate_checkpoint_manifest({"input_representation": "grayscale_A_PNG_duplicated"}, rows)


def test_geotiff_manifest_requires_dual_pol_checkpoint():
    rows = [{"sar_path": "scene_s1.tif", "vv_band": 1, "vh_band": 2}]
    assert manifest_input_representation(rows) == "VV_VH_pair"
    with pytest.raises(ValueError, match="Checkpoint expects"):
        validate_checkpoint_manifest({"input_representation": "grayscale_B_PNG_duplicated"}, rows)


def test_ambiguous_manifest_is_rejected():
    with pytest.raises(ValueError, match="Cannot infer"):
        manifest_input_representation([{"sar_path": "input.png"}])
