from data_preproc import get_min_max_cord


def test_get_min_max_coordinates():
    """
    get max latitude, max longitude, min latitude, min longitude from json file
    """
    assert get_min_max_cord("tests/some.json", "Ekb") == (
        60.1935774,
        56.823773,
        60.0073423,
        56.7578451,
    )
