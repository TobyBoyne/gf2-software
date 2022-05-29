from names import Names
import pytest


@pytest.fixture
def n():
    """Return a new Names instance."""
    return Names()


@pytest.fixture
def name_list():
    """Return a list of names."""
    return ["Toby", "Thomas", "Ieronymos", "TikTok", "Johnny", "\n   \t  "]


@pytest.fixture
def names_added(name_list):
    """Return an istance after passing a list of names"""
    #["Toby"=0, "Thomas"=1, "Ieronymos"=2, "TikTok"=3, "Johnny"=4]
    names = Names()
    names.lookup(name_list)
    return names


@pytest.fixture
def initial_errors():
    """Return a number that represents the number initial errors."""
    return 3


@pytest.fixture
def errors_added(names_added, initial_errors):
    """Pass the counted errors to the instance."""
    names_added.unique_error_codes(initial_errors)
    return names_added


def test_unique_errors_raises_error(names_added):
    """Test to check that unique_error_code raises a TypeError 
    upon inputing a non-integer argument"""
    
    with pytest.raises(TypeError):
        names_added.unique_error_codes("some str")
    with pytest.raises(TypeError):
        names_added.unique_error_codes(1.4)

    
@pytest.mark.parametrize(
    "errors, expected", [(4, range(0, 4)), (5, range(0, 5))]
)
def test_error_count(names_added, errors, expected):
    """Assert that errors are correctly counted."""
    assert names_added.unique_error_codes(errors) == expected


@pytest.mark.parametrize(
    "new_errors, expected", [(4, range(3, 7)), (5, range(3, 8))]
)
def test_added_error_count(errors_added, new_errors, expected):
    """Test that the errors add correctly."""
    assert errors_added.unique_error_codes(new_errors) == expected


# "Toby", "Thomas", "Ieronymos", "TikTok", "Johnny", "\n   \t  "
@pytest.mark.parametrize(
    "name, expected_id",
    [
        ("Toby", 0),
        ("Thomas", 1),
        ("Ieronymos", 2),
        ("TikTok", 3),
        ("Johnny", 4),
        ("Amber", None),
    ],
)
def test_query(names_added, n, name, expected_id):
    """Test query function on empty instance and names_added instance"""
    assert names_added.query(name) == expected_id
    assert n.query(name) == None


@pytest.mark.parametrize(
    "names_list, expected_ids", 
    [
     (["Toby", "TikTok", "Ieronymos", "Amber"], 
      [0, 3, 2, 5])]
    )
def test_lookup(names_added, names_list, expected_ids):
    """Input: list containing string names --> Output: list of unique ids. 
    Amber is now assigned an id"""
    assert names_added.lookup(names_list) == expected_ids


@pytest.mark.parametrize(
    "_id, expected_name",
    [
        (0, "Toby"),
        (1, "Thomas"),
        (2, "Ieronymos"),
        (3, "TikTok"),
        (4, "Johnny"),
        (5, None),
    ],
)
def test_get_name_string(names_added, n, _id, expected_name):
    """Test if get_name_string."""
    assert names_added.get_name_string(_id) == expected_name
    assert n.get_name_string(_id) == None


def test_get_name_string_negative_input(names_added, n):
    """Test that Assertion error is raised if negative ids are input (EBNF syntax)"""
    with pytest.raises(AssertionError):
        names_added.get_name_string(-5)
    with pytest.raises(AssertionError):
        n.get_name_string(-1)




