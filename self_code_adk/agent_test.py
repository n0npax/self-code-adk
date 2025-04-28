import pytest
from self_code_adk.agent import get_my_application_code

@pytest.mark.parametrize("dir,expected_files_number", [("self_code_adk", 3)])
def test_autodiscover(dir, expected_files_number):
    files, errors = get_my_application_code(dir)
    assert expected_files_number == len(files)
    assert 0 == len(errors)