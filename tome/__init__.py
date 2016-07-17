"""
Tome - a collection of Python dictionaries and some helpful code to use with them.
"""

import copy
import json
import pickle
import pprint
import collections

from fuzzywuzzy import process

# Various Initialization
################################################################################################################################
pp = pprint.PrettyPrinter(indent=1)

# General Helper Functions
################################################################################################################################
def flip_key_val(x=None, smart=True, container=list):
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

def regex_search(x=None, pattern='', where='both'):
    """
    Search thru keys, values, or both via regex match.
    """
    # Create precompiled regex if need be
    pattern_re = re.compile(pattern) if isinstance(pattern, str) or isinstance(pattern, unicode) else pattern

    # Search thru the items and return matches
    if where is 'keys':
        result = {k: x[k] for k in x.iterkeys() if pattern_re.match(str(k))}
    elif where is 'values':
        result = {k: x[k] for k, v in x.iteritems() if pattern_re.match(str(v))}
    elif where is 'both':
        result = {k: x[k] for k, v in x.iteritems() if pattern_re.match(str(k)) or pattern_re.match(str(v))}

    return result

def fuzzy_search(x=None, query='', where='both', score_cutoff=50, limit=10):
    """
    Search thru keys, values, or both via fuzzy string comparison.
    """

    if where is 'keys':
        matches = process.extractBests(query, x.keys(), score_cutoff=score_cutoff, limit=limit)
        results = {k : x[k] for k, score in matches}
    elif where is 'values':
        matches = process.extractBests(query, x, score_cutoff=score_cutoff, limit=limit)
        results = {k : v for v, score, k in matches}
    elif where is 'both':
        key_matches = process.extractBests(query, x.keys(), score_cutoff=score_cutoff, limit=limit)
        key_results = {k : x[k] for k, score in key_matches}
        val_matches = process.extractBests(query, x, score_cutoff=score_cutoff, limit=limit)
        val_results = {k : v for v, score, k in val_matches}
        # Combine results
        results = key_results.copy()
        results.update(val_results)

    return results

def fuzzy_matches(x=None, query='', where='both', score_cutoff=50, limit=10):
    """
    Get the internal matches used in fuzzy search. Exposses the scores of each match.
    If item is a 2 tuple match is on a key, if the item is a 3 tuple match is on a value.
    """

    if where is 'keys':
        matches = process.extractBests(query, x.keys(), score_cutoff=score_cutoff, limit=limit)
    elif where is 'values':
        matches = process.extractBests(query, x, score_cutoff=score_cutoff, limit=limit)
    elif where is 'both':
        key_matches = process.extractBests(query, x.keys(), score_cutoff=score_cutoff, limit=limit)
        val_matches = process.extractBests(query, x, score_cutoff=score_cutoff, limit=limit)
        # Combine results
        results = key_matches + val_matches

    return results

# Custom classes
################################################################################################################################
class DataDict(collections.MutableMapping):
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

class Tome(DataDict):
    """
    The tome class, which provides extra dictionary functionality.
    """

    # order in wich attibutes are access when printing this class
    print_order = ['name', 'description', 'key', 'value', 'date', 'authority', 'reference', 'living', 'derived', 'source']
    header_order = ['name', 'description', 'date', 'authority', 'reference', 'living', 'derived', 'source']

    # Alias some of the general dictionary helper functions as class methods
    flip = flip_key_val
    regex_search = regex_search
    fuzzy_search = fuzzy_search
    fuzzy_matches = fuzzy_matches

    def __init__(self, data=None, name='Tome', description='A container of information.', key='', value='', authority='', reference='', living=False, derived=False, source=None, date=None):
        """Add new properties to regular dictionary initialization."""
        # The 'real' dictionary
        self.data = data
        # Nice info about the data
        self.name = name
        self.description = description
        self.date = date
        self.key = key
        self.value = value
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

    def astype(self, new_type=lambda x: x):
        """Convert values to a different type"""
        converted_self = self.copy()
        converted_self.data = {k : new_type(v) for k, v in converted_self.data.iteritems()}
        return converted_self

    def to_tuples(self):
        """Convert dictionary to tuples."""
        return [x for x in self.data.iteritems()]

    def to_lists(self):
        """Convert dictionary to lists."""
        return [list(x) for x in self.data.iteritems()]

    def to_pickle(self, fp=None, data_only=False):
        """Convert tome to pickle. Use data_only=True to convert just the data."""
        if fp:
            if isinstance(fp, str) or isinstance(fp, unicode):
                with open(fp, 'w') as f:
                    pickle.dump(f, self.data) if data_only else json.dumps(self.__dict__)
            else:
                pickle.dump(fp, self.data) if data_only else json.dumps(self.__dict__)
        else:
            return pickle.dumps(self.data) if data_only else json.dumps(self.__dict__)

    def to_json(self, fp=None, data_only=False, indent=4):
        """Convert tome to json. Use data_only=True to convert just the data."""
        if fp:
            if isinstance(fp, str) or isinstance(fp, unicode):
                with open(fp, 'w') as f:
                    json.dump(f, self.data, indent=indent) if data_only else json.dump(self.__dict__, indent=indent)
            else:
                json.dump(fp, self.data, indent=indent) if data_only else json.dump(self.__dict__, indent=indent)
        else:
            return json.dumps(self.data, indent=indent) if data_only else json.dumps(self.__dict__, indent=indent)

    def to_csv(self, fp=None, data_only=False, csv_formater='{},{}', header_formater='{}: {}'):
        """
        Convert tome to csv. Tome metadata is placed in first row header.
        Use data_only=True to convert just the data. Control separators with csv_formator and header_formater
        """
        csv = '' if data_only else ', '.join([header_formater.format(a, self.__dict__[a]) for a in self.header_order if self.__dict__[a]]) + '\n'
        csv += csv_formater.format(self.key, self.value) + '\n'
        csv += '\n'.join([csv_formater.format(k, v) for k, v in self.data.iteritems()])
        if fp:
            if isinstance(fp, str) or isinstance(fp, unicode):
                with open(fp, 'w') as f:
                    f.write(csv)
            else:
               fp.write(csv)
        else:
            return csv

    def to_tsv(self, fp=None, data_only=False, csv_formater='{}\t{}', header_formater='{}: {}'):
        """Convenience call to csv with tab delimiter."""
        return self.to_csv(fp=fp, data_only=data_only, csv_formater=csv_formater, header_formater=header_formater)

    def to_text(self, fp=None, data_only=False, csv_formater='{}: {}', header_formater='{}: {}'):
        """Convenience call to csv with colon delimiter."""
        return self.to_csv(fp=fp, data_only=data_only, csv_formater=csv_formater, header_formater=header_formater)

    def to_html(self, fp=None, data_only=False, header_formater='{}: {}'):
        """Convert tome to html table. Use data_only=True to convert just the data."""
        html = '<table>\n'
        html += '' if data_only else '\t<caption>' + ', '.join([header_formater.format(a, self.__dict__[a]) for a in self.header_order if self.__dict__[a]]) + '</caption>\n'
        html += '\t<thead>\n\t\t<tr><th>{}</th><th>{}</th></tr>\n\t</thead>\n'.format(self.key, self.value)
        html += '\t<tbody>\n' + '\n'.join(['\t\t<tr><td>{}</td><td>{}</td></tr>'.format(k, v) for k, v in self.data.iteritems()]) + '\n\t</tbody>\n'
        html += '</table>\n'
        if fp:
            if isinstance(fp, str) or isinstance(fp, unicode):
                with open(fp, 'w') as f:
                    f.write(html)
            else:
               fp.write(html)
        else:
            return html

    def __str__(self):
        """Pretty print this Tome."""
        s = '\n'.join(['{:11} : {}'.format(k, v) for k, v in [(a, self.__dict__[a]) for a in self.print_order if self.__dict__[a]]])
        s += '\n' + pp.pformat(self.data)
        return s

    def __repr__(self):
        """
        Create reproducible string, so that eval(x.__repr__()) == x.
        """
        return 'Tome({})'.format(', '.join('{!s}={!r}'.format(k, v) for k, v in self.__dict__.iteritems()))
