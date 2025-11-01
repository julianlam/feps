import json
from . import data_for_json_file


def test_data_for_json_file():
    result = data_for_json_file()

    assert isinstance(result, list)

    dumped = json.dumps(result)

    assert isinstance(dumped, str)
