import pytest
from self_code_adk.agent import get_my_application_code, find_git_repo


@pytest.mark.parametrize("dir,expected_files_number", [("self_code_adk", 3)])
def test_autodiscover(dir, expected_files_number):
    files, errors = get_my_application_code(dir)
    assert expected_files_number == len(files)
    assert 0 == len(errors)

@pytest.mark.parametrize("dir,expected_name", [("self_code_adk", "self-code-adk")])
def test_find_git_repo(dir, expected_name):
    repo_path = find_git_repo(dir)
    assert expected_name == repo_path.split("/")[-1]

def test_find_git_repo_non_exiting_path():
    with pytest.raises(Exception):
        find_git_repo("/no/such/path")
