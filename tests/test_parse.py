import pytest
import errorlog
from devices import Devices
from monitors import Monitors
from names import Names
from network import Network
from scanner import Scanner
from parse import Parser


@pytest.fixture(scope="module")
def names():
    """Return a new Names instance."""
    return Names()


@pytest.fixture(scope="module")
def devices(names):
    """Return a Devices instance."""
    return Devices(names)


@pytest.fixture(scope="module")
def network(names, devices):
    """Return a Network instance."""
    return Network(names, devices)


@pytest.fixture(scope="module")
def monitors(names, devices, network):
    """Return a new Monitors instance."""
    return Monitors(names, devices, network)


def new_file(tmpdir, file_contents):
    """Return a file path to a mock file used in testing"""
    p = tmpdir.mkdir("sub").join("example.txt")
    p.write(file_contents)
    return p


devicename_test_files_1 = ["DEVICE", "CONNECT", "MONITOR", "INPUTS"]


@pytest.mark.parametrize("file_contents", devicename_test_files_1)
def test_parse_raises_semantic_errors_1(file_contents, tmpdir, names,
                                        devices, network, monitors):
    """Test if the parser correctly raises a ProtectedKeywordError."""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, names)
    parse = Parser(names, devices, network, monitors, scanner)
    parse.next_symbol()
    with pytest.raises(errorlog.ProtectedKeywordError):
        parse.devicename()


devicename_test_files_2 = [",NOR", ":G1:", "0SW", "\t;CLK1"]


@pytest.mark.parametrize("file_contents", devicename_test_files_2)
def test_parse_raises_syntax_errors_1(file_contents, tmpdir, names,
                                      devices, network, monitors):
    """Test if the parser correctly raises a NameSyntaxError.

    Error occurs when a name does not start at a letter"""
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, names)
    parse = Parser(names, devices, network, monitors, scanner)
    parse.next_symbol()
    with pytest.raises(errorlog.NameSyntaxError):
        parse.devicename()


inputname_test_files = ["G1,I1", "G2:I2", "G3;I3", "G4 I4"]


@pytest.mark.parametrize("file_contents", inputname_test_files)
def test_parse_raises_syntax_errors_2(file_contents, tmpdir, names,
                                      devices, network, monitors):
    """Test if the parser correctly raises a PunctuationError.

    Occurs when an input does not start with a dot. """
    path = new_file(tmpdir, file_contents)
    scanner = Scanner(path, names)
    parse = Parser(names, devices, network, monitors, scanner)
    parse.next_symbol()
    with pytest.raises(errorlog.PunctuationError):
        parse.inputname()
