from pathlib import Path

from ml.src.train import _safe_artifact_reference


def test_manifest_metadata_uses_repo_relative_reference_for_repo_files(tmp_path):
    repository_file = Path(__file__).resolve().parents[2] / "ml/configs/train_default.json"
    assert _safe_artifact_reference(repository_file) == "ml/configs/train_default.json"


def test_external_manifest_metadata_does_not_store_absolute_path():
    for external_file in ("/tmp/user-private-dataset/tiles.json", r"C:\\Users\\private\\tiles.json"):
        result = _safe_artifact_reference(external_file)
        assert result == "external:tiles.json"
        assert "/tmp/" not in result
        assert "user-private-dataset" not in result
        assert "Users" not in result
