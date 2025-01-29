import os
import tempfile
from pathlib import Path
import pytest
from snapcode.cli import (
    get_excluded_patterns,
    is_text_file,
    should_include_file,
    create_code_snapshot,
)


@pytest.fixture
def temp_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create test files
        (project_dir / "test.py").write_text("print('hello')")
        (project_dir / "test.txt").write_text("hello")
        (project_dir / ".git").mkdir()
        (project_dir / ".git" / "config").write_text("git config")
        (project_dir / "binary_file").write_bytes(b"\x00\x01\x02")

        yield project_dir
        # Cleanup happens automatically when context manager exits
        # but we can add explicit cleanup here if needed


@pytest.fixture(autouse=True)
def cleanup_snapshots():
    # Setup - runs before each test
    yield
    # Cleanup - runs after each test
    cwd = Path.cwd()
    for file in cwd.glob("*_snapshot.txt"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Warning: Could not delete {file}: {e}")


def test_get_excluded_patterns():
    patterns = get_excluded_patterns()
    assert ".git" in patterns
    assert ".venv" in patterns
    assert "__pycache__" in patterns


def test_is_text_file(temp_project):
    assert is_text_file(temp_project / "test.py")
    assert is_text_file(temp_project / "test.txt")
    assert not is_text_file(temp_project / "binary_file")
    assert not is_text_file(temp_project / "nonexistent_file")


def test_should_include_file(temp_project):
    excluded_patterns = get_excluded_patterns()

    assert should_include_file(temp_project / "test.py", excluded_patterns)
    assert should_include_file(temp_project / "test.txt", excluded_patterns)
    assert not should_include_file(temp_project / ".git" / "config", excluded_patterns)
    assert not should_include_file(temp_project / "binary_file", excluded_patterns)


def test_create_code_snapshot(temp_project):
    # Create snapshot
    create_code_snapshot(temp_project)

    # Check if snapshot file was created with correct name
    snapshot_file = temp_project / f"{temp_project.name}_snapshot.txt"
    assert snapshot_file.exists()

    # Check content
    content = snapshot_file.read_text()
    assert "test.py" in content
    assert "test.txt" in content
    assert "print('hello')" in content
    assert "hello" in content
    assert ".git/config" not in content


def test_create_code_snapshot_custom_output(temp_project):
    output_file = "custom_snapshot.txt"
    create_code_snapshot(temp_project, output_file)

    snapshot_file = temp_project / output_file
    assert snapshot_file.exists()

    content = snapshot_file.read_text()
    assert "test.py" in content
    assert "test.txt" in content


def test_create_code_snapshot_with_unreadable_file(temp_project):
    # Create an unreadable file
    unreadable_file = temp_project / "unreadable.txt"
    unreadable_file.write_text("test")
    os.chmod(unreadable_file, 0o000)

    try:
        # Should not raise an exception
        create_code_snapshot(temp_project)
    finally:
        # Cleanup: make file readable again so it can be deleted
        os.chmod(unreadable_file, 0o644)
