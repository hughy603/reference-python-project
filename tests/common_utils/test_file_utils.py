"""
Unit tests for file_utils module.
"""

import os
from pathlib import Path

import pytest

from enterprise_data_engineering.common_utils.file_utils import (
    ensure_directory_exists,
    get_file_extension,
    list_files_with_extension,
    read_file_content,
    safe_file_write,
)


class TestGetFileExtension:
    """Tests for the get_file_extension function."""

    def test_with_extension(self):
        """Test extracting extension from a file with an extension."""
        assert get_file_extension("data/file.csv") == "csv"
        assert get_file_extension("file.txt") == "txt"
        assert get_file_extension("path/to/file.json") == "json"

    def test_with_multiple_dots(self):
        """Test extracting extension from a file with multiple dots."""
        assert get_file_extension("data/file.tar.gz") == "gz"
        assert get_file_extension("file.name.with.dots.txt") == "txt"

    def test_without_extension(self):
        """Test extracting extension from a file without an extension."""
        assert get_file_extension("data/file") == ""
        assert get_file_extension("no_extension") == ""

    def test_with_path_object(self):
        """Test extracting extension from a Path object."""
        assert get_file_extension(Path("data/file.csv")) == "csv"
        assert get_file_extension(Path("file.txt")) == "txt"
        assert get_file_extension(Path("path/to/file")) == ""


class TestEnsureDirectoryExists:
    """Tests for the ensure_directory_exists function."""

    def test_create_directory(self, tmp_path):
        """Test creating a directory that doesn't exist."""
        test_dir = tmp_path / "test_dir"
        assert not test_dir.exists()

        result = ensure_directory_exists(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir

    def test_create_nested_directory(self, tmp_path):
        """Test creating a nested directory structure."""
        test_dir = tmp_path / "parent" / "child" / "grandchild"
        assert not test_dir.exists()

        result = ensure_directory_exists(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()
        assert (tmp_path / "parent").exists()
        assert (tmp_path / "parent" / "child").exists()
        assert result == test_dir

    def test_existing_directory(self, tmp_path):
        """Test ensuring an existing directory exists."""
        # First create the directory
        test_dir = tmp_path / "existing_dir"
        test_dir.mkdir()
        assert test_dir.exists()

        # Then call the function
        result = ensure_directory_exists(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir

    def test_with_string_path(self, tmp_path):
        """Test ensuring directory exists with a string path."""
        test_dir = str(tmp_path / "string_path_dir")
        assert not os.path.exists(test_dir)

        result = ensure_directory_exists(test_dir)

        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        assert result == Path(test_dir)


class TestListFilesWithExtension:
    """Tests for the list_files_with_extension function."""

    @pytest.fixture
    def test_directory(self, tmp_path):
        """Create a test directory with various files."""
        # Create test files
        (tmp_path / "file1.txt").write_text("test content")
        (tmp_path / "file2.txt").write_text("test content")
        (tmp_path / "file3.csv").write_text("test content")
        (tmp_path / "noextension").write_text("test content")

        # Create a subdirectory with more files
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "subfile1.txt").write_text("test content")
        (subdir / "subfile2.csv").write_text("test content")

        return tmp_path

    def test_find_files_non_recursive(self, test_directory):
        """Test finding files with a specific extension (non-recursive)."""
        # Find .txt files
        txt_files = list_files_with_extension(test_directory, "txt", recursive=False)

        assert len(txt_files) == 2
        assert any(file.name == "file1.txt" for file in txt_files)
        assert any(file.name == "file2.txt" for file in txt_files)
        assert not any("subdir" in str(file) for file in txt_files)

        # Find .csv files
        csv_files = list_files_with_extension(test_directory, "csv", recursive=False)

        assert len(csv_files) == 1
        assert any(file.name == "file3.csv" for file in csv_files)

    def test_find_files_recursive(self, test_directory):
        """Test finding files with a specific extension (recursive)."""
        # Find .txt files recursively
        txt_files = list_files_with_extension(test_directory, "txt", recursive=True)

        assert len(txt_files) == 3
        assert any(file.name == "file1.txt" for file in txt_files)
        assert any(file.name == "file2.txt" for file in txt_files)
        assert any(file.name == "subfile1.txt" for file in txt_files)

        # Find .csv files recursively
        csv_files = list_files_with_extension(test_directory, "csv", recursive=True)

        assert len(csv_files) == 2
        assert any(file.name == "file3.csv" for file in csv_files)
        assert any(file.name == "subfile2.csv" for file in csv_files)

    def test_extension_case_sensitivity(self, test_directory):
        """Test that extension matching is case-insensitive."""
        # Create a file with uppercase extension
        (test_directory / "upper.TXT").write_text("test content")

        # Find .txt files (should find uppercase too)
        txt_files = list_files_with_extension(test_directory, "txt", recursive=False)

        assert len(txt_files) == 3
        assert any(file.name == "upper.TXT" for file in txt_files)

        # Test with uppercase search pattern
        txt_files_upper = list_files_with_extension(test_directory, "TXT", recursive=False)

        assert len(txt_files_upper) == 3

    def test_no_matching_files(self, test_directory):
        """Test finding files when none match the extension."""
        # Look for a non-existent extension
        pdf_files = list_files_with_extension(test_directory, "pdf", recursive=True)

        assert len(pdf_files) == 0
        assert isinstance(pdf_files, list)


class TestSafeFileWrite:
    """Tests for the safe_file_write function."""

    def test_write_to_existing_directory(self, tmp_path):
        """Test writing to a file in an existing directory."""
        file_path = tmp_path / "test_file.txt"
        content = "This is test content"

        safe_file_write(file_path, content)

        assert file_path.exists()
        assert file_path.read_text() == content

    def test_write_with_directory_creation(self, tmp_path):
        """Test writing to a file in a non-existent directory with creation."""
        file_path = tmp_path / "new_dir" / "test_file.txt"
        content = "This is test content"

        safe_file_write(file_path, content, create_dirs=True)

        assert file_path.exists()
        assert file_path.read_text() == content
        assert (tmp_path / "new_dir").exists()
        assert (tmp_path / "new_dir").is_dir()

    def test_write_no_directory_creation(self, tmp_path):
        """Test writing to a file in a non-existent directory without creation."""
        file_path = tmp_path / "another_dir" / "test_file.txt"
        content = "This is test content"

        with pytest.raises(FileNotFoundError):
            safe_file_write(file_path, content, create_dirs=False)

    def test_write_with_custom_encoding(self, tmp_path):
        """Test writing to a file with a custom encoding."""
        file_path = tmp_path / "encoded_file.txt"
        content = "This is test content with special characters: ÄÖÜ"

        safe_file_write(file_path, content, encoding="latin-1")

        # Read with the same encoding to verify
        assert file_path.read_text(encoding="latin-1") == content


class TestReadFileContent:
    """Tests for the read_file_content function."""

    def test_read_existing_file(self, tmp_path):
        """Test reading content from an existing file."""
        file_path = tmp_path / "test_read.txt"
        content = "This is test content for reading"
        file_path.write_text(content)

        result = read_file_content(file_path)

        assert result == content

    def test_read_nonexistent_file(self):
        """Test reading from a non-existent file returns None."""
        result = read_file_content("nonexistent_file.txt")

        assert result is None

    def test_read_nonexistent_file_with_default(self):
        """Test reading from a non-existent file returns the default value."""
        default_content = "Default content"
        result = read_file_content("nonexistent_file.txt", default=default_content)

        assert result == default_content

    def test_read_with_custom_encoding(self, tmp_path):
        """Test reading a file with a custom encoding."""
        file_path = tmp_path / "encoded_read.txt"
        content = "Content with special characters: ÄÖÜ"

        # Write with latin-1 encoding
        file_path.write_text(content, encoding="latin-1")

        # Read with the same encoding
        result = read_file_content(file_path, encoding="latin-1")

        assert result == content
