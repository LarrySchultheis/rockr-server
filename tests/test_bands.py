from rockr.db.models import bands as bnds


def test_get_bands():
    bands = bnds.get_bands()
    assert bands is not None
    assert len(bands) > 0
    assert "band_name" in bands[0]
    assert "genre" in bands[0]
    assert "members" in bands[0]
    assert isinstance(bands[0]["band_name"], str)
    assert isinstance(bands[0]["genre"], str)
    assert isinstance(bands[0]["members"], int)
    