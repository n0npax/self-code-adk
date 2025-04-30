import pytest
import sys
import os
import tempfile
from unittest.mock import patch
from self_code_adk.agent import (
    get_my_application_code,
    find_git_repo,
    autodiscover_possible_root_dir,
    SelfCodeAgent,
)


@pytest.mark.parametrize("dir,expected_name", [("self_code_adk", "self-code-adk")])
def test_find_git_repo(dir, expected_name):
    repo_path = find_git_repo(dir)
    assert expected_name == repo_path.split("/")[-1]


def test_find_git_repo_non_exiting_path():
    with pytest.raises(Exception):
        find_git_repo("/no/such/path")


@pytest.mark.skipif(sys.platform != "darwin", reason="runs only on MacOS")
def test_get_my_application_code_permission_denied_mac():
    # Test with non-existent directory
    _, errors = get_my_application_code(
        "/private/etc", only_py_files=False, max_files=200
    )
    assert "sudoers" in errors
    assert "Permission denied" in errors["sudoers"]


@pytest.mark.skipif(sys.platform != "linux", reason="runs only on linux")
def test_get_my_application_code_permission_denied_linux():
    # Test with non-existent directory
    _, errors = get_my_application_code("/etc", only_py_files=False, max_files=200)
    assert "shadow" in errors
    assert "Permission denied" in errors["shadow"]

def test_get_my_application_code_unicode_Error():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, f"file.py"), "wb") as f:
            f.write(b"An incomplete multi-byte sequence")
            f.write(b'\xc3') # breaks utf-8

        files, errors = get_my_application_code(tmpdir)
        assert len(files) == 0 
        assert len(errors) > 0
        assert "Could not decode file as UTF-8 " in errors["file.py"]


def test_get_my_application_code_error_handling():
    # Test with non-existent directory
    files, errors = get_my_application_code("/non/existent/dir")
    assert len(files) == 0
    assert "/non/existent/dir" in errors
    assert "specified root directory is not directory" in errors["/non/existent/dir"]


def test_get_my_application_code_max_files():
    # Create a temporary directory with multiple files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 5 files
        for i in range(5):
            with open(os.path.join(tmpdir, f"file{i}.py"), "w") as f:
                f.write(f"# Test file {i}")

        # Test with max_files=2
        files, errors = get_my_application_code(tmpdir, max_files=2)
        assert (
            len(files) <= 3
        )  # Should only read up to 3 files (max_files=2 plus initial count)
        assert len(errors) > 0  # Should have errors for the remaining files


def test_get_my_application_code_only_py_files():
    # Create a temporary directory with mixed file types
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create python and non-python files
        with open(os.path.join(tmpdir, "test.py"), "w") as f:
            f.write("# Python file")
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("Text file")

        # Test with only_py_files=True
        files, errors = get_my_application_code(tmpdir, only_py_files=True)
        assert len(files) == 1
        assert len(errors) == 0
        assert "test.py" in next(iter(files.keys()))

        # Test with only_py_files=False
        files, errors = get_my_application_code(tmpdir, only_py_files=False)
        assert len(files) == 2
        assert len(errors) == 0


def test_autodiscover_possible_root_dir():
    # Create a simpler test that doesn't rely on mocking
    # Instead, verify the function returns at least one value (current working directory)
    roots = autodiscover_possible_root_dir()
    assert len(roots) >= 1
    assert os.getcwd() in roots


def test_self_code_agent():
    # Test agent creation
    agent = SelfCodeAgent("test-model")
    assert agent.name == "self_code_adk"
    assert agent.model == "test-model"
    assert len(agent.tools) == 2
