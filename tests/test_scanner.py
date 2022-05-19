"""Test the scanner module.
Each test requires a new scanner and file, so fixtures are not used."""
import pytest

from names import Names
from scanner import Scanner


def new_file(tmpdir, file_contents):
    """Return a file path to a mock file"""
    p = tmpdir.mkdir("sub").join("example.txt")
    p.write(file_contents)
    return p


test_files = [("DEVICE A: AND ! INPUTS;", ValueError), ("CONNECT B - C", ValueError)]


@pytest.mark.parametrize("file_contents,error_type", test_files)
def test_scanner_raises_errors(file_contents, error_type, tmpdir):
    """Test if the scanner correctly raises an error."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, Names())
    with pytest.raises(error_type):
        # scan the file, expecting an error of given type
        scanner.advance()
