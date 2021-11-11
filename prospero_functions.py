# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 17:15:26 2021

@author: marcu
"""
import tkinter as tk
import re
import enchant
import config
from PIL import Image
from datetime import datetime
import os
import shutil
import eyed3
import unidecode

class Functions:
    """
    Provides a variety of generic functions for use in Prospero modules
    """
    def __init__(self, parent, trace = None):
        self.parent = parent
        self.root = parent.root
        self.pr = parent.pr
        self.class_name = "Functions"
        self._log_trace(self, "__init__", trace)
        return
    
    def distribute_width(self, width, weights, fix_width = None, trace = None):
        self._log_trace(self, "distribute_width", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".distribute_width"}
        
        if fix_width is None:
            fix_width = [True for w in weights]
        
        total_fixed_width = sum(weights[i] if fix_width[i] else 0 
                                for i in range(len(weights)))
        reduced_old_width = sum(weights) - total_fixed_width
        reduced_new_width = width - total_fixed_width
        
        new_widths = [weights[i] if fix_width[i] 
                      else weights[i]*reduced_new_width/reduced_old_width 
                      for i in range(len(weights))]
        
        new_widths = self.round_list(new_widths, trace = inf_trace)
        
        width_diff = sum(new_widths) - width - 1
        new_widths[-1] = new_widths[-1] + width_diff 
        #remove any deviation from the target width due to rounding
        
        return new_widths
    
    def normalise_list(self, data, trace = None):
        self._log_trace(self, "normalise_list", trace)
        return [i/sum(data) for i in data]
    
    def round_list(self, data, precision=0, trace = None):
        self._log_trace(self, "round_list", trace)
        if precision<=0:
            return [int(round(i, precision)) for i in data]
        else:
            return [round(i, precision) for i in data]
    
    def multiply_list(self, data, multiple, trace = None):
        self._log_trace(self, "multiply_list", trace)
        return [i*multiple for i in data]
    
    
    def null_function(self, trace = None, *args, **kwargs):
        return
    
    def true_titlecase(self, string, trace = None):
        self._log_trace(self, "true_titlecase", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".true_titlecase"}
        
        if type(string) != str:
            return([self.true_titlecase(entry, inf_trace) for entry in string])
        
        articles = ["a", "an", "and", "of", "the", "is", "to", "via", "for"]
        string = string.lower()
        words = string.split(" ")
        words_capitalised = [words[0].capitalize()] + [word if word in articles 
                                                       else word.capitalize() 
                                                       for word in words[1:]]
        return " ".join(words_capitalised)
    
    def filename_from_parts(self, parts, headers, trace = None):
        self._log_trace(self, "filename_from_parts", trace)
        
        #parts:
        composer = str(parts[headers.index("Composer")]).strip()
        album = str(parts[headers.index("Album")]).strip()
        number = str(parts[headers.index("#")]).strip()
        track = str(parts[headers.index("Track")]).strip()
        performers = str(parts[headers.index("Performer(s)")]).strip()
        
        parts_pattern = [composer, album, number, track]
        parts_pattern = [part != '' for part in parts_pattern]
        """
        '        #List of cases:
        '        #    1) Surname, Forenames - Track
        '        #    2) Surname, Forenames - Album
        '        #    3) Surname, Forenames - Album - Number. Track
        '        #    4) Surname, Forenames - Album - Track
        '        #    5) Surname, Forenames - Album - Number.
        """  
        if parts_pattern == [True, False, False, True]: #1
            filename = "%s - %s" (composer, track)
        elif parts_pattern == [True, True, False, False]: 
            filename = "%s - %s" (composer, album)
        elif parts_pattern == [True, True, True, True]:
            filename = "%s - %s - %s. %s" % (composer, album, number, track)
        elif parts_pattern == [True, True, False, True]: 
            filename = "%s - %s - %s" % (composer, album, track)
        elif parts_pattern == [True, True, True, False]: 
            filename = "%s - %s - %s." % (composer, album, number)
        else:
            filename = ""
        
        if performers != '' and filename != '':
            filename = filename + " [" + performers + "]"
    
        filename = filename.strip() #remove leading and trailing spaces
        filename = " ".join(filename.split()) #remove duplicate whitespace
        
        return filename

    def filename_from_dict(self, parts_dict, trace = None):
        self._log_trace(self, "filename_from_dict", trace)

        composer = parts_dict.get("Composer", "")
        album = parts_dict.get("Album", "")
        number = parts_dict.get("#", "")
        track = parts_dict.get("Track", "")
        performers = parts_dict.get("Performer(s)", "")

        parts_pattern = [composer, album, number, track]
        parts_pattern = [part != '' for part in parts_pattern]

        if parts_pattern == [True, False, False, True]: #1
            filename = "%s - %s" % (composer, track)
        elif parts_pattern == [True, True, False, False]: 
            filename = "%s - %s" (composer, album)
        elif parts_pattern == [True, True, True, True]:
            filename = "%s - %s - %s. %s" % (composer, album, number, track)
        elif parts_pattern == [True, True, False, True]: 
            filename = "%s - %s - %s" % (composer, album, track)
        elif parts_pattern == [True, True, True, False]: 
            filename = "%s - %s - %s." % (composer, album, number)
        else:
            filename = ""
        
        if performers != '' and filename != '':
            filename = filename + " [" + performers + "]"
    
        filename = filename.strip() #remove leading and trailing spaces
        filename = " ".join(filename.split()) #remove duplicate whitespace
        
        return filename

    def suggest_value(self, filename, field, trace = None):
        self._log_trace(self, "suggest_value", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.class_name + ".suggest_value"}
        
        """
        Given a filename string and specified field, tries to suggest a value 
        for it via dictionaries of regex expressions mapped to values
        """
        field = field.lower()
        if field == "composer":
            regex_dict = config.composers_dict.regex_dict
        elif field == "genre":
            regex_dict = config.genres_dict.regex_dict
        elif field == "number" or field == "#" or field == "numeral":
            regex_dict = config.numerals_dict.regex_dict
        elif field == "url" or field == "artist url":
            return self.youtube_url_from_filename(filename, do_word_check=True, 
                                                  trace = inf_trace).strip()
        elif field == "album":
            return self.album_from_filename(filename, trace = inf_trace).strip()
        elif field == "year":
            return self.year_from_filename(filename, trace = inf_trace).strip()
        else:
            return ""
        
    #return the mapped value of the first regex expr that matches the filename
        for regex_expr in regex_dict.keys():
            if re.search(regex_expr, filename, re.IGNORECASE):
                return str(regex_dict[regex_expr]).strip()
        return ""
    
    def year_from_filename(self, filename, trace = None):
        self._log_trace(self, "year_from_filename", trace)
        
        #Match 4 digit number in between some kind of brackets, starting with
        #1 or 2. Always take the last match
        try:
            return re.findall("[\[\(\{]([12]\d{3})[\]\)\}]", filename)[-1]
        except IndexError:
            return ""


    def album_from_filename(self, filename, trace = None):
        self._log_trace(self, "album_from_filename", trace)
        
        albums_dict = config.albums_dict.regex_dict
        for key in albums_dict.keys():
            match_type = albums_dict[key]["type"]
            
            if match_type == "regex_construct":
                albums_dict[key] = self.construct_album_regex(albums_dict[key])
                
            if re.match(albums_dict[key]["pattern"], filename, re.I):
                match_type = albums_dict[key]["type"]
                if match_type == "string":
                    return albums_dict[key]["value"]
                elif match_type == "regex":
                    result = []
                    for i in range(len(albums_dict[key]["value"])):
                        value = albums_dict[key]["value"][i]
                        parse = albums_dict[key]["parse"][i]
                        if parse:
                            parsed = re.search(value, filename, re.I).group(1)
                            if not parsed is None: result.append(parsed)
                        else:
                            result.append(value)
                    result = " ".join(result)
                    result = " ".join(result.replace("No.", "No. ").split())
                    result = self.true_titlecase(result)
                    return result
        return ""
    
    def construct_album_regex(self, cd, trace = None):
        self._log_trace(self, "construct_album_regex", trace)
        
        if type(cd) != dict: return cd
        if cd["type"] != "regex_construct": return cd
        
        outdict = {"pattern": None, "value": None, 
                   "parse": None, "type": "regex"}
        
        pattern = list(cd["pattern"].values())
        optional = cd["optional"]
        parse = []
        value = []
        regex_parts = []
        
        regex_start = r"^.*\b"
        regex_end = r"\b.*$"
        for i in range(len(pattern)):
            end = r")?\b\s*" if optional[i] else r")\b\s*"
            regex_parts.append(r"\s*\b(?:" + "|".join(pattern[i]) + end)
        
        for i in range(len(pattern)):
            #build the regex which will return the strings used to construct the
            #final value. To do this, make each non-capturing group a capturing
            #group in turn, while keeping all other group non-capturing.
            end = r")?\b\s*" if optional[i] else r")\b\s*"
            match_part = regex_start + "".join(regex_parts[:i])
            match_part += r"\s*\b(" + "|".join(pattern[i]) + end
            match_part += "".join(regex_parts[i+1:]) + regex_end
            value.append(match_part)
            parse.append(True)
            
        outdict["pattern"] = regex_start + "".join(regex_parts) + regex_end
        outdict["value"] = value
        outdict["parse"] = parse
        return outdict
    
    def parse_tags_from_filename(self, filename, trace = None):
        self._log_trace(self, "suggest_tags_from_final_filename", trace)
        
        """
        Given a filename in an expected format (post-naming tab), suggests 
        suitable metadata tags
        """
        tag_dict = {"Composer": None,
                    "Album": None,
                    "#": None,
                    "Track": None,
                    "Performers": None,
                    "Year": None,
                    "Genre": None,
                    "URL": None
                    }
        
        if filename is None or filename == "":
            return tag_dict
        
        if re.search("\[.*\]$", filename) is not None:
            """
            re.search returns the [full; text], and the first and last 
            characters are then trimmed off. "/" is used in the backend to 
            separate multiple distinct artist, even though it appears as "; " 
            in both the file name as we've set it, and the properties/tags 
            window in Windows.
            """
            tag_dict["Performer(s)"] = \
                re.search("\[.*\]$", filename)[0][1:-1].replace( "; ", "/")
                
            filename = filename.replace(
                re.search("\s?\[.*\]$", filename)[0], "")
        
        #split at most 2 times, for album and then track
        filename_parts = filename.split(" - ", 2) 
        
        if re.search("^[a-zA-z\']*, [a-zA-z\']* - ", filename) is not None: 
            tag_dict["Composer"] = \
                " ".join(filename_parts[0].split(", ")[::-1])
        else:
            tag_dict["Composer"] = filename_parts[0]
        
        if re.match("^\d+\.\b", filename_parts[-1]):
            search = re.search("^(\d+)\.\s(.*)$", filename_parts[-1])
            tag_dict["#"] = search.group(1)
            tag_dict["Track"] = search.group(2)
        else:
            tag_dict["Track"] = filename_parts[-1]
            
        tag_dict["Album"] = "%s (%s)" % (filename_parts[1],
                                        tag_dict["Composer"])
        for k in tag_dict:
            if k is None or k == "":
                tag_dict[k] = self.suggest_value(filename, k)
        
        return tag_dict
    
    def youtube_url_from_filename(self, filename, do_word_check = False, 
                                  trace = None):
        self._log_trace(self, "youtube_url_from_filename", trace)
        
        """
        For a given filename, tries to detect if it ends in a valid YouTube 
        video ID. If it does, returns the corresponding URL.
        """
        
        youtube_prefix = "www.youtube.com/watch?v="
        #take the last word in the string since the id will always be 1 word
        youtube_id = filename.split()[-1] 
        
        if len(youtube_id) < 11:
            return ""
        elif len(youtube_id) >= 12:
            #to account for old youtube-dl behaviour, where the filename 
            #format was <video title>-<video id>
            youtube_id = (youtube_id[-11:] if youtube_id[-12] == "-" 
                          else youtube_id)
        
        #test for a valid id format 
        if not re.match("[0-9a-zA-Z_-]{11}", youtube_id): 
            return ""
        
        if re.match("[a-zA-Z]{11}", youtube_id) and do_word_check:
            # test if the string is a dictionary word
            # covers the case that the video name ends in an 11 letter word
            # This has by far the largest performance impact, so is disabled by 
            # default
            if enchant.Dict("en_GB").check(youtube_id): 
                return ""
        
        return youtube_prefix + youtube_id
    
    def pad_image_with_transparency(self, image, pixels, 
                                    keep_size = False, trace = None):
        self._log_trace(self, "pad_image_with_transparency", trace)
        """
        Pad around the outside of an image with the specified transparent 
        pixels on each side. Option to keep the final image the same size 
        as the original, or increase according to padding
        """
        image = image.convert('RGBA')
        width, height = image.size  
        
        if keep_size:
            """height/width of the final image is the same as the original 
            #original image is resized to the original minus the specified 
            padding amount on each side"""
            pad_width, pad_height = width - pixels*2, height - pixels*2
            new_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            image = image.resize((pad_width, pad_height), 
                                 resample=Image.ANTIALIAS)
        else:
            """new height/width is the original plus the specified padding 
            amount on each side"""
            pad_width, pad_height = width + pixels*2, height + pixels*2
            new_image = Image.new('RGBA', (pad_width, pad_height), (0, 0, 0, 0))
            
     
        #paste the original image into the centre
        new_image.paste(image, (pixels, pixels))
        return new_image
    
    def _log_trace(self, parent_class, function, trace, add = ""):
        if self.pr.testing_mode:
            trace = ({"source": None, "widget": None, "parent": None} 
                     if trace is None else trace)
            
            if parent_class is None:
                trace["function"] = function
            if type(parent_class) is str:
                trace["function"] = parent_class + "." + function
            else:
                trace["function"] = (parent_class.__class__.__name__ 
                                     + "." + function)
            
            if trace["source"] == "bound event":
                trace_tuple = (datetime.now(), trace["function"], 
                               trace["widget"], trace["event"])
                prnt = "%s Called %s from widget %s and event %s." % trace_tuple
            elif trace["source"] == "function call":
                trace_tuple = (datetime.now(), trace["function"], 
                               trace["parent"])
                prnt = "%s Called %s from within %s." % trace_tuple
            elif trace["source"] == "initialise class":
                trace_tuple = (datetime.now(), parent_class.__class__.__name__, 
                               trace["parent"])
                prnt = "%s Initialised class %s from within %s." % trace_tuple
            else:
                trace_tuple = (datetime.now(), trace["function"])
                prnt = "%s Called %s without trace." % trace_tuple
                
            prnt += f" {add}"
            print(prnt)
        return

    def rename_file(self, old_directory, old_name, new_directory, 
                    new_name, trace = None):
        self._log_trace(self, "rename_file", trace)
        """
        Renames and moves the specified file. Returns a FileExistsError if the 
        renamed file already exists.
        """
        old_directory = old_directory.replace("/", "\\")
        new_directory = new_directory.replace("/", "\\")
        
        old_path = os.path.join(old_directory, old_name)
        new_path = os.path.join(new_directory, new_name)
        
        try:
            if os.path.exists(new_path):
                raise FileExistsError
            else:
                shutil.move(old_path, new_path)
        except FileNotFoundError:
            raise
        return
    
    def treeview_to_json(self, treeview, trace = None):
        self._log_trace(self, "treeview_to_json", trace)
        """
        Given a treeview, converts the IDs and values to dictionary object, 
        ready for dumping to JSON
        """
        json_dict = {}
        for child in treeview.get_children():
            json_dict[child] = treeview.item(child, 'values')
        return json_dict
        
    def json_to_treeview(self, treeview, json_dict, trace = None):
        self._log_trace(self, "json_to_treeview", trace)
        """
        Given a dictionary of ID keys and mapped value lists, adds the IDs 
        and values to the provided treeview
        """
        if type(json_dict) != dict:
            raise TypeError
            return
        
        for key,value in json_dict.items():
            treeview.insert("", index="end", text = key, iid = key, 
                            values = value)
        return

    def configure_treeview_columns(self, treeview, columns, headers, widths, 
                                   create_columns = False, trace = None):
        self.pr.f._log_trace(self, "_configure_treeview_columns", trace)
        
        column_count = len(columns)
        if column_count > 1 and create_columns:
            treeview['columns'] = columns[1:]
        
        for i in range(column_count):
            column_name = columns[i]
            column_header = headers[i]
            column_width = widths[i]
            
            if create_columns:
                treeview.heading(column_name, text = column_header)
                
            treeview.column(column_name, width = column_width, 
                            minwidth = column_width, stretch = tk.NO)
        return
    
    def point_is_inside_widget(self, x, y, widget, trace = None):
        self.pr.f._log_trace(self, "is_point_inside_widget", trace)
        
        widget.update()
        x_min = widget.winfo_rootx()
        x_max = x_min + widget.winfo_width()
        y_min = widget.winfo_rooty()
        y_max = y_min + widget.winfo_height()
        
        return x_min <= x <= x_max and y_min <= y <= y_max
    
    def common_dictionary_subset_is_identical(self, a, b, trace = None):
        self.pr.f._log_trace(self, "compare_dictionary_subset", trace)

        common_keys = [k for k in a.keys if k in b.keys()]
        
        for k in common_keys:
            if a[k] != b[k]:
                return False
        return True
    
    def tag_file(self, directory, filename, tags, trace = None):
        """
        Given a filename, adds ID3v2 tags to it based on the provided
        dictionary.
        
        Valid values for the dictionary are:
            Composer
            Album
            Track
            Number OR #
            Performer(s)
            Genre
            Year
            URL
        """
        self.pr.f._log_trace(self, "tag_file", trace)
        if filename[-4:] != self.pr.c.file_extension: 
            filename += self.pr.c.file_extension
            
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError
            
        #Load audiofile into memory for tagging
        audiofile = eyed3.load(filepath)
        #initialise tagging if it is not already
        if audiofile.tag is None:
            audiofile.initTag()
        
        #Rebuild tags dict with standardised keys
        init_tags = tags
        std_keys = {"#": "number",
                    "Performer": "performer(s)",
                    "performer": "performer(s)"
                    }
        tags = {std_keys.get(k, k.lower()): init_tags[k] 
                for k in init_tags.keys()}
        
        #Set default values for fields required below
        tags.setdefault("composer", "")
        tags.setdefault("album", "")
        
        #Update tag values for tagging rather than filename building
        c = tags["composer"]
        
        # "Surname, Forenames (more info)" -> "Forenames Surname (more info)"
        if not (c is None or c == ""):
            end = ""
            if re.match(".*\(.*\).*", c):
                end = re.match(".*(?P<end>\(.*\).*)", c).group("end")
                c = c.replace(end, "").strip()
                
            if re.match(".*,.*", c):
                c = c.split(", ")[1] + " " + c.split(", ")[0]
            
            tags["composer"] = c
            
            #append to end of album value if it exists
            if tags["album"] != "":
                tags["album"] = tags["album"] + " (%s)" % c
        
        audiofile.tag.album_artist = tags.get("composer", "")
        audiofile.tag.album = tags.get("album", "")
        audiofile.tag.title = tags.get("track", "")
        audiofile.tag.artist = tags.get("performer(s)", "")
        audiofile.tag.genre = tags.get("genre", "")
        audiofile.tag.artist_url = tags.get("url", "")
        
        if not tags.get("number", "") in [None, ""]:
            audiofile.tag.track_num = int(tags["number"])
            
        if not tags.get("year", "") in [None, ""]:
            audiofile.tag.recording_date = eyed3.core.Date(int(tags["year"]))
        
        audiofile.tag.save()
        del audiofile
        return
    
    def add_keyword_pattern(self, values_dict, trace = None):
        self.pr.f._log_trace(self, "add_keyword_pattern", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + 
                                 ".add_keyword_pattern"}
        values_dict  =  {k.lower(): v for k, v in values_dict.items()}
        if 'number' in values_dict.keys():
            values_dict['#'] = values_dict['number']
            
        def valid_values(fields):
            for field in fields:
                try:
                    if (str(values_dict[field]).strip() == "" or 
                            values_dict[field] is None):
                        return False
                except KeyError:
                    return False
            return True
        
        def invalid_values(fields):
            return not valid_values(fields)
        
        #Add Composer + Album + Number = Track
        if valid_values(["composer", "album", "#", "track"]):
            kwargs = {"Composer": (values_dict["composer"], "key"),
                      "Album": (values_dict["album"], "key"),
                      "Number": (values_dict["#"], "key"),
                      "Track": (values_dict["track"], "value")
                      }
            pd = config.keyword_dict.add_keyword_pattern(**kwargs, 
                                                         trace = inf_trace)
            if not pd == 'Pattern exists in dictionary, skipping.':
                self.pr.f._log_trace(config.keyword_dict, 
                                     "add_keyword_pattern", 
                                     trace = inf_trace,
                                     add = f"Added pattern {pd} to dictionary.")
        #Add Composer + Album = Genre + Year
        if valid_values(["composer", "album", "genre"]):
            kwargs = {"Composer": (values_dict["composer"], "key"),
                      "Album": (values_dict["album"], "key"),
                      "Genre": (values_dict["genre"], "value"),
                      "Year": (values_dict["year"], "value")
                      }
            pd = config.keyword_dict.add_keyword_pattern(**kwargs, 
                                                         trace = inf_trace)
            if not pd == 'Pattern exists in dictionary, skipping.':
                self.pr.f._log_trace(config.keyword_dict, 
                                     "add_keyword_pattern", 
                                     trace = inf_trace,
                                     add = f"Added pattern {pd} to dictionary.")

        #Add Composer + Track = Genre + Year
        if (valid_values(["composer", "track", "genre"]) 
            and invalid_values(["album"])):
            kwargs = {"Composer": (values_dict["composer"], "key"),
                      "Track": (values_dict["track"], "key"),
                      "Genre": (values_dict["genre"], "value"),
                      "Year": (values_dict["year"], "value")
                      }
            pd = config.keyword_dict.add_keyword_pattern(**kwargs, 
                                                         trace = inf_trace)
            if not pd == 'Pattern exists in dictionary, skipping.':
                self.pr.f._log_trace(config.keyword_dict, 
                                     "add_keyword_pattern", 
                                     trace = inf_trace,
                                     add = f"Added pattern {pd} to dictionary.")
                
    def match_filename_pattern(self, filename, trace = None):
        """

        Parameters
        ----------
        filename : str
            String to match pattern to.
        trace : dict, optional
            Trace dictionary for logging. The default is None.

        Returns
        -------
        dict
            Dictionary of matched group names and values.
            
        Uses the config dictionary "filename_patterns_dict" to attempt to match
        filenames to a defined pattern. If it is able to match, it then parses
        the filename and extracts all named capture groups as a dictionary.
        Does not directly support nested capture groups.

        """
        self.pr.f._log_trace(self, "match_filename_pattern", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + 
                                 ".match_filename_pattern"}
        
        for d in config.filename_patterns_dict.regex_dict.values():
            if re.match(d["match_pattern"], filename, re.IGNORECASE):
                captures = re.search(d["parse_pattern"], filename, 
                                     re.IGNORECASE).groupdict()
            else:
                continue
                
            if type(captures) != dict: 
                continue
            
            for k in captures.keys():
                try:
                    if d["rematch_values"][k]:
                        new_v = self.suggest_value(captures[k], k, inf_trace)
                        if new_v != "": 
                            captures[k] = new_v
                except KeyError:
                    continue
            return captures
        return {}

    def timecode_to_seconds(self, timecode, trace = None):
        """

        Parameters
        ----------
        timecode : str
            str in the format XX.XX.XX or XX:XX:XX for digits X, corresponding 
            to hours:minutes:seconds in a timecode.
        trace : dict, optional
            Trace dictionary for logging. The default is None.

        Returns
        -------
        int.
            number of seconds from 00:00:00 to timecode

        """
        self.pr.f._log_trace(self, "match_filename_pattern", trace)
        timecode = timecode.replace(".", ":")
        parts = timecode.split(":")
        mult = 1
        seconds = 0
        while len(parts)>0:
            seconds += int(parts[-1])*mult
            mult = mult*60
            parts = parts[:-1]
        return seconds
    
    def clean_track_string(self, track, iterate = True, trace = None):
        self.pr.f._log_trace(self, "clean_track_string", trace)
        inf_trace = {"source": "function call", 
                     "parent": self.__class__.__name__ + 
                                 ".clean_track_string"}
        
        track = " ".join(track.split())
        track = track.replace(r"\n", "")
        
        if track == "": return track
        
        leading_trailing_chars = ["-",",",".","'","–",":",";"]
        for char in leading_trailing_chars:
            track = track[1:] if track[0] == char else track #Remove leading
            track = track[:-1] if track[-1] == char else track #Remove trailing
        
        if track == "": return track
            
        #remove leading ) if no closing bracket and vice versa
        bracket_map = {"(": ")", ")": "(", 
                       "{": "}", "}": "{", 
                       "[":"]", "]": "["}
        
        for brkt in bracket_map:
            #remove brackets without counter part
            track = (track.replace(brkt, "") 
                     if not bracket_map[brkt] in track else track)
            if track == "": return track
            #remove brackets if they wrap the whole string
            track = (track[1:-1] if track[-1] == brkt 
                     and track[0] == bracket_map[brkt] else track)
        
        track = track.strip()
        
        if track == "": return track
        
        if iterate:
            #keep cleaning until no change occur between cleaning cycles
            double_cleaned = ""
            while double_cleaned != track:
                double_cleaned = self.clean_track_string(track, 
                                                         iterate = False, 
                                                         trace = inf_trace)
                track = double_cleaned
        return track

    def get_values_dict(self, treeview, iid, columns, trace = None):
        self.pr.f._log_trace(self, "clean_track_string", trace)
        
        item_dict = treeview.item(iid)
        values_dict = {columns[0]: item_dict['text']}
        for i, v in enumerate(item_dict['values']):
            values_dict[columns[i+1]] = v
        
        return values_dict
    
    def autocomplete(self, text, options, out = "list", trace = None):
        """
        Autocomplete a string from a defined set of options. Either return the
        first match (out = "string"), or a list of all possible matches
        (out = "list").
        """
        self.pr.f._log_trace(self, "autocomplete", trace)
        
        if not out in ["list", "string"]:
            raise ValueError("Invalid return type specified. out must be one"
                             " of 'list' or 'string'.")
            
        if text == "" or text is None:
            if out == "list":
                return options
            elif out == "string":
                return text
        
        #build the regex pattern
        regex_str = ".*"
        for word in text.split():
            regex_str += r"(?=.*\b[A-Z']*?%s[A-Z']*?\b.*)" % re.escape(word)
        regex_str += ".*"
        
        pattern = re.compile(regex_str, re.IGNORECASE)
        
        matches = []
        for opt in options:
            if re.match(pattern, opt):
                if out == "string":
                    return opt
                elif out == "list":
                    matches.append(opt)
        return matches
    
    def remove_diacritics(self, text, trace = None):
        self.pr.f._log_trace(self, "remove_diacritics", trace)
        return unidecode.unidecode(text)
        
    def get_tags(self, directory, filename, trace = None):
        """
        Return a dictionary of ID3v2 tags for a specific file.
        """
        self.pr.f._log_trace(self, "get_tags", trace)
        
        filepath = os.path.join(directory, filename)
        audiofile = eyed3.load(filepath)
        
        #initialise tagging if it is not already
        if audiofile.tag is None:
            audiofile.initTag()
        
        tag_dict = {
            "Composer": audiofile.tag.album_artist,
            "Album": audiofile.tag.album,
            "#": audiofile.tag.track_num[0],
            "Track": audiofile.tag.title,
            "Performer(s)": audiofile.tag.artist,
            "Year": (audiofile.tag.recording_date.year 
                     if not audiofile.tag.recording_date is None else ""),
            "Genre": audiofile.tag.genre,
            "URL": audiofile.tag.artist_url
            }
        
        for k,v in tag_dict.items():
            if v is None: tag_dict[k] = ""
        
        return tag_dict
    