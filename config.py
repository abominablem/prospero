# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 20:10:38 2021

@author: marcu
"""

import json
from mh_logging import log_class
from global_vars import LOG_LEVEL

class JSONDict:
    """
    This class represents a dictionary based on a .json file.

    Attributes:
    ----------
    logging : Logging
        A class used to log activity in the class

    dict_type : str
        Type of the dictionary. The file name of the read .json file.

    filename : str
        The constructed filename, based on dict_type.

    regex_dict : dict
        The dictionary read from the file at filename.

    config_dict : dict
        Possible additional pointer to regex_dict, depending on dict_type.

    Methods:
    ----------
    dd_value(self, regex, result, override_existing = False, trace = None):
        Given a RegEx pattern and result, tries to create a map between them in
        the regex_dict object. If the map already exists, gives the option to
        change the mapped output.

    delete_value(self, regex_pattern, trace = None):
        Given a regex pattern, remove the corresponding dictionary entry

    dump_values(self, trace = None):
        Writes the current dictionary state to file

    add_regex_pattern_words(self, include_words, exclude_words,
                                result, trace = None):
        Given a list of words to include and words to exclude, adds a regex
        pattern to the dictionary which matches any string including all of the
        former and excluding all of the latter, mapping to the specified result

    add_keyword_pattern(self, trace = None, **kwargs):
        Each input should be a dictionary of (value, role) where role is
        "key"/"value", corresponding to whether the value is a key in the
        pattern matching, or the result of the pattern matching. Value is then
        the string or regex pattern to be used in the pattern matching or the
        result of the pattern matching.

        Allowed parameters are composer, album, number, track, genre, and year.
    """
    @log_class(LOG_LEVEL)
    def __init__(self, dict_type):
        """
        Takes one string parameter. This should correspond to a json file
        sitting in the config folder.
        """
        self.dict_type = dict_type
        self.filename = './config/%s.json' % dict_type

        with open(self.filename, encoding='utf-8') as json_file:
            self.regex_dict = json.load(json_file)

        if self.dict_type == "config":
            self.config_dict = self.regex_dict

    @log_class(LOG_LEVEL)
    def add_value(self, regex, result, override_existing = False):
        """
        Given a RegEx pattern and result, tries to create a map between them in
        the regex_dict object. If the map already exists, gives the option to
        change the mapped output.
        """
        if regex in self.regex_dict.keys():
            if self.regex_dict[regex] != result and not override_existing:
                raise KeyError("The specfied RegEx pattern already exists with"
                               " a different mapped output. Pass the argument "
                               "override_existing = True to update the "
                               "existing entry.")
            if override_existing:
                self.regex_dict[regex] = result
        else:
            self.regex_dict[regex] = result

    @log_class(LOG_LEVEL)
    def delete_value(self, keys):
        """
        Given a list of keys, remove the corresponding dictionary entries
        """
        if not isinstance(keys, list):
            keys = [keys]

        for key in keys:
            try:
                del self.regex_dict[str(key)]
            except KeyError:
                raise KeyError("Invalid key, nothing to delete")

    @log_class(LOG_LEVEL)
    def dump_values(self):
        """
        Writes the current dictionary state to file
        """
        if self.dict_type == "config":
            self.regex_dict = self.config_dict

        with open(self.filename, "w", encoding='utf-8') as json_file:
            json.dump(self.regex_dict, json_file)

    @log_class(LOG_LEVEL)
    def add_regex_pattern_words(self, include_words, exclude_words, result):
        """
        Given a list of words to include and words to exclude, adds a regex
        pattern to the dictionary which matches any string including all of the
        former and excluding all of the latter, mapping to the specified result
        """
        if isinstance(include_words, str):
            include_words = [include_words]

        if isinstance(exclude_words, str):
            exclude_words = [exclude_words]

        #build the regex pattern
        regex_str = ".*"
        for word in include_words:
            regex_str = regex_str + "(?=.*\\b%s\\b.*)" % word
        for word in exclude_words:
            regex_str = regex_str + "(?=^(?:(?!\\b%s\\b.)*$)" % word
        regex_str = regex_str + ".*"

        #add to dictionary
        self.add_value(regex_str, result)

    @log_class(LOG_LEVEL)
    def add_keyword_pattern(self, **kwargs):
        """
        Each input should be a dictionary of (value, role) where role is
        "key"/"value", corresponding to whether the value is a key in the
        pattern matching, or the result of the pattern matching. Value is then
        the string or regex pattern to be used in the pattern matching or the
        result of the pattern matching.

        Allowed parameters are composer, album, number, track, genre, and year.
        """
        if self.dict_type != 'keyword':
            raise Exception('Keyword patterns not supported for this '
                            'dictionary type.')

        pattern_dict = {'key': {}, 'value': {}}
        new_key = str(int(list(self.regex_dict.keys())[-1])+1)

        for key, value in kwargs.items():
            kw_dict = '#' if key.lower() == 'number' else key
            kw_dict = kw_dict.capitalize()
            pattern_dict[value[1].lower()][kw_dict] = str(value[0])

        #do not add if pattern already exists in dictionary
        if pattern_dict in self.regex_dict.values():
            print(f'Pattern {pattern_dict} exists in dictionary, skipping.')
            return 'Pattern exists in dictionary, skipping.'

        self.regex_dict[new_key] = pattern_dict
        return pattern_dict


config = JSONDict('config')
composers_dict = JSONDict('composers')
keyword_dict = JSONDict('keyword')
genres_dict = JSONDict('genres')
numerals_dict = JSONDict('numerals')
albums_dict = JSONDict('albums')
filename_patterns_dict = JSONDict('filename_patterns')

if __name__ == "__main__":
    filt = []
    for key in keyword_dict.regex_dict:
        try:
            if (keyword_dict.regex_dict[key]["key"]["Composer"] == "Scriabin, Alexander"
                and keyword_dict.regex_dict[key]["key"]["Album"] == "24 Preludes"):
                filt.append(key)
        except KeyError:
            continue