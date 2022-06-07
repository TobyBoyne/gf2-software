"""Test the scanner module."""

import pytest
import string

from names import Names
from scanner import Scanner

# A string containing all ASCII characters that are considered whitespace.
# [‘ ‘, ‘\t’, ‘\v’, ‘\n’, ‘\r’, ‘\f’]
WHITESPACES = string.whitespace


@pytest.fixture
def names():
    """Return a new Names instance"""
    return Names()


def new_file(tmpdir, file_contents):
    """Return a file path to a mock file"""
    p = tmpdir.mkdir("sub").join("example.txt")
    p.write(file_contents)
    return p


def test_file_errors(names):
    """Test that FileNotFoundError is raised if the file does not exist."""
    with pytest.raises(FileNotFoundError):
        Scanner("definitely_not_a_file.txt", names)


generate_test_files = ["DEVICE A: AND 1 INPUTS;", "CONNECT B -> C"]


@pytest.mark.parametrize("file_contents", generate_test_files)
def test_write_new_file(file_contents, tmpdir):
    """Test if the scanner correctly create a temporary file."""
    new_file(tmpdir, file_contents)


names_test_files = [(WHITESPACES + "DEVICE", "DEVICE"), ("G1 -> G2", "G1"), ("->", "")]


@pytest.mark.parametrize("file_contents,expected_name", names_test_files)
def test_scanner_get_names(file_contents, expected_name, tmpdir, names):
    """Test if the scanner reads the alphanumeric strings correctly."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, names)
    scanner._get_next_non_whitespace()
    assert scanner._get_name() == expected_name


number_test_files = [("2 INPUTS", 2), ("10,", 10)]


@pytest.mark.parametrize("file_contents,expected_numbers", number_test_files)
def test_scanner_get_number(file_contents, expected_numbers, tmpdir, names):
    """Test if the scanner reads the number strings correctly."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, names)
    scanner._get_next_non_whitespace()
    assert scanner._get_number() == expected_numbers


symbol_test_files = [("DEVICE", 5, 0), ("MONITOR", 5, 2), ("CLK1:", 7, 4), (";", 1, None)]


@pytest.mark.parametrize("file_contents, expected_type, expected_id", symbol_test_files)
def test_scanner_get_symbol(file_contents, expected_type, expected_id, tmpdir, names):
    """Test if the scanner captures the correct symbol."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, names)
    symbol = scanner.get_symbol()
    assert symbol.id == expected_id
    assert symbol.type == expected_type
