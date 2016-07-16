"""
Tome - a collection of Python dictionaries and some helpful code to use with them.
"""

import copy
import collections

# General Helper Functions
################################################################################################################################
def flip_key_val(x, smart=True, container=list):
    """
    Flip key value pairs of a dictionary with optional 'smart flip' for handling new non-unique keys.

    Smart flip (default: smart=True) turns the new non-unique keyed pairs into a single pair where the new value is a
    contianer (list, set, etc., default: container=list) of the old keys.

    When smart flip is not used the last key value pair returned by iteritems will be used.
    """
    if smart:
        y = {}
        # Loop thru key val pairs
        for k, v in x.iteritems():
            # if key already exists in result
            if v in y:
                # if value is not container
                if not isinstance(y[v], container):
                    # turn current value into container
                    y[v] = container(y[v]) if container is not dict else container([(0, y[v])])
                    # append new value to current value
                    if container is list:
                        y[v].append(k)
                    elif container is set:
                        y[v].update(k)
                    elif container is tuple:
                        y[v] = y[v] + (k,)
                    elif container is dict:
                        y[v].update({len(y[v]): k})
            else:
                y[v] = k
        return y
    else:
        # Nice dictionary comprehension for 'dump' flip
        return {v : k for k, v in x.iteritems()}

# Custom classes
################################################################################################################################
class D(collections.MutableMapping):
    """
    Make a dictionary like object that operates on an attribute called data instead of the typical __dict__.

    Reference credit and thanks
    @aaron-hall (http://stackoverflow.com/a/21368848/2087463) & @jochen-ritzel (http://stackoverflow.com/a/3387975/2087463)

    """
    def __init__(self, *args, **kwargs):
        """Use an object's data attribute as a dictionary"""
        try:
            self.data.update(*args, **kwargs)
        except AttributeError:
            self.data = dict(*args, **kwargs)

    def __setitem__(self, key, value):
        self.data[key] = value
    def __getitem__(self, key):
        return self.data[key]
    def __delitem__(self, key):
        del self.data[key]
    def __iter__(self):
        return iter(self.data)
    def __len__(self):
        return len(self.data)

    def __str__(self):
        """Print the 'dictionary'."""
        return str(self.data)

    def __repr__(self):
        """Create reproducible string, so that eval(x.__repr__()) == x."""
        return 'D({!r})'.format(self.data)

class Tome(D):
    """
    The tome class, which provides extra dictionary functionality.
    """

    # order in wich attibutes are access when printing this class
    print_order = ['name', 'description', 'date', 'authority', 'reference', 'living', 'derived', 'source', 'data']

    # Alias some general helper functions
    flip = flip_key_val

    def __init__(self, data=None, name='Tome', description='A tome of information.', authority='', reference='', living=False, derived=False, source=None, date=None):
        """Add new properties to regular dictionary initialization."""
        # The 'real' dictionary
        self.data = data
        # Nice info about the data
        self.name = name
        self.description = description
        self.date = date
        # Organization that sets the definition
        self.authority = authority
        # URL of reference data
        self.reference = reference
        # Defines whether this reference is 'living' (changes) or 'fixed' (does not change).
        self.living = living
        # Defines whether this data was generated or derived from another Tome source
        self.derived = derived
        self.source = source

    def copy(self, deep=True):
        return copy.deepcopy(self) if deep else copy.copy(self)

    def __str__(self):
        """Pretty print this Tome."""
        return '\n'.join(['{:11} : {}'.format(k, v) for k, v in [(a, self.__dict__[a]) for a in self.print_order if self.__dict__[a]]])

    def __repr__(self):
        """
        Create reproducible string, so that eval(x.__repr__()) == x.
        """
        return 'Tome({})'.format(', '.join('{!s}={!r}'.format(k, v) for k, v in self.__dict__.iteritems()))
