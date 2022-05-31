"""Test the scanner module.
Each test requires a new scanner and file, so fixtures are not used."""
import pytest
import string

from names import Names
from scanner import Scanner

# A string containing all ASCII characters that are considered whitespace.
# [‘ ‘, ‘\t’, ‘\v’, ‘\n’, ‘\r’, ‘\f’]
WHITESPACES = string.whitespace


def new_file(tmpdir, file_contents):
    """Return a file path to a mock file"""
    p = tmpdir.mkdir("sub").join("example.txt")
    p.write(file_contents)
    return p


error_test_files = [("DEVICE A: AND ! INPUTS;", ValueError), ("CONNECT B - C", ValueError)]


@pytest.mark.parametrize("file_contents,error_type", error_test_files)
def test_scanner_raises_errors(file_contents, error_type, tmpdir):
    """Test if the scanner correctly raises an error."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, Names())
    with pytest.raises(error_type):
        # scan the file, expecting an error of given type
        scanner.advance()


names_test_files = [(WHITESPACES + "DEVICE", "DEVICE"), ("G1 -> G2", "G1"), ("->", "")]


@pytest.mark.parametrize("file_contents,expected_name", names_test_files)
def test_scanner_get_names(file_contents, expected_name, tmpdir):
    """Test if the scanner reads the alphanumeric strings correctly."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, Names())
    scanner.get_next_non_whitespace()
    assert scanner.get_name() == expected_name


number_test_files = [("2 INPUTS", 2)]


@pytest.mark.parametrize("file_contents,expected_numbers", number_test_files)
def test_scanner_get_number(file_contents, expected_numbers, tmpdir):
    """Test if the scanner reads the number strings correctly."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, Names())
    scanner.get_next_non_whitespace()
    assert scanner.get_number() == expected_numbers


symbol_test_files = [("DEVICE", 5, 0), ("MONITOR", 5, 2), ("CLK1:", 7, 4), (";", 1, None)]


@pytest.mark.parametrize("file_contents, expected_type, expected_id", symbol_test_files)
def test_scanner_get_symbol(file_contents, expected_type, expected_id, tmpdir):
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, Names())
    symbol = scanner.get_symbol()
    assert symbol.id == expected_id
    assert symbol.type == expected_type
