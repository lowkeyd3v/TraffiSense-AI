def test_model_file_exists():
    import os

    assert os.path.exists(
        "ml/model.joblib"
    )