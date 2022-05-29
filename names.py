"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.names = []
        self.error_code_count = 0  # how many error codes have been declared

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """

        #if name_string in self.names:
        #    return self.names.index(name_string)
        #else:
        #    return None

        #check if name is string
        if isinstance(name_string,str):
            if name_string in self.names:
                return self.names.index(name_string) #return id of name
            else:
                #assuming only positive numbers as defined in EBFL
                #raise IndexError('name_string not in the list')
                return None
        else:
            #raise TypeError('Only strings allowed')
            return None

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        ids = []
        for name in name_string_list:
            #check in name is string and does not exist spaces only
            if isinstance(name,str) and not name.isspace():
                if name not in self.names:
                    self.names.append(name) #append name in list
                    ids.append(len(self.names)-1) #append id of the new name
                else:
                    ids.append(self.names.index(name)) #append id of existing name
        return ids

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        #if isinstance(name_id, float): name_id = int(name_id)
        #check if id is integer
        if isinstance(name_id,int) and name_id >=0:
            name_id = int(name_id)
            if name_id in range(len(self.names)):
                return self.names[name_id] #return name corresponding to id
            else:
                return None

        elif name_id < 0:
            raise AssertionError('Negative-integers are not allowed!')

"""
def name_list():
    return ["Toby", "Thomas", "Ieronymos", "TikTok", "Bob", "\n   \t  "]

def names_added(name_list):
    names = Names()
    ids = names.lookup(name_list())
    print(ids)
    return names
"""


#name = Names()
#z=name.get_name_string('andreas')
#print(z) #none
#er = name.unique_error_codes(3)
#er = name.unique_error_codes(2)
#print(er)
#ids = name.lookup(["Toby", "Thomas", "Ieronymos", "TikTok", "Bob", "\n   \t  ",1])
#print(ids)#
#x = name.get_name_string(3)
#print(x)
#z = name.lookup(["Tiktok",2,3,'Bob'])
#print(z)
#i = name.query("Thomas")
#print(i) # 1
