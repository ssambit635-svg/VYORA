from types import SimpleNamespace

from app.ml.model_runner import evaluation_status_for_model, incompatible_input_message


def test_png_checkpoint_rejects_geotiff_contract():
    runner = SimpleNamespace(
        is_ai_inference=True,
        input_representation="grayscale_B_PNG_duplicated",
    )
    message = incompatible_input_message(runner, "geotiff-vv-vh")
    assert message is not None
    assert "not separate VV/VH bands" in message
    assert incompatible_input_message(runner, "single-channel-preview-duplicated", "input.png") is None
    jpeg_message = incompatible_input_message(runner, "single-channel-preview-duplicated", "input.jpg")
    assert jpeg_message is not None
    assert "expects a PNG tile" in jpeg_message
    demo_message = incompatible_input_message(
        runner, "single-channel-preview-duplicated", "agriculture.png", is_synthetic_demo=True
    )
    assert demo_message is not None
    assert "synthetic gallery is not a paired training example" in demo_message


def test_dual_pol_checkpoint_rejects_single_channel_preview():
    runner = SimpleNamespace(is_ai_inference=True, input_representation="VV_VH_pair")
    message = incompatible_input_message(runner, "single-channel-preview-duplicated")
    assert message is not None
    assert "distinct VV and VH" in message
    assert incompatible_input_message(runner, "geotiff-vv-vh") is None


def test_development_runner_keeps_previews_available():
    runner = SimpleNamespace(is_ai_inference=False, input_representation="VV_VH_pair")
    assert incompatible_input_message(runner, "single-channel-preview-duplicated") is None


def test_evaluation_status_is_checkpoint_specific():
    assert evaluation_status_for_model("dev-heuristic-v0", False) == "not_evaluated"
    assert evaluation_status_for_model("another-checkpoint", True) == "not_evaluated_for_this_checkpoint"
    assert evaluation_status_for_model(
        "resunet-paired-png-prototype-v0.2-b-to-a", True
    ) == "documented_200_tile_subset_geographic_independence_unverified"
