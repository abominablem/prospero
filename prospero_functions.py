# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 17:15:26 2021

@author: marcu
"""
import re
import enchant
import config
from PIL import Image
import os
import sys
sys.path.append("D:\\Users\\Marcus\\Documents\\R Documents\\Coding\\Python\\Packages")
from mh_logging import Logging, log_class
from global_vars import LOG_LEVEL
log_class = log_class(LOG_LEVEL)
import shutil
import eyed3
import unidecode

log = Logging()

class Functions:
    """
    Provides a variety of generic functions for use in Prospero modules
    """
    def __init__(self, parent):
        self.pr = parent.pr

    def null_function(self, *args, **kwargs):
        return

    @log_class
    def true_titlecase(self, string):
        if type(string) != str:
            return([self.true_titlecase(entry) for entry in string])

        articles = ["a", "an", "and", "of", "the", "is", "to", "via", "for"]
        string = string.lower()
        words = string.split(" ")
        words_capitalised = [words[0].capitalize()] + [word if word in articles
                                                       else word.capitalize()
                                                       for word in words[1:]]
        return " ".join(words_capitalised)

    @log_class
    def filename_from_parts(self, parts, headers):
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

    @log_class
    def filename_from_dict(self, parts_dict):
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
            filename = "%s - %s" % (composer, album)
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

    @log_class
    def suggest_value(self, filename, field):
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
            return self.youtube_url_from_filename(filename, do_word_check = True).strip()
        elif field == "album":
            return self.album_from_filename(filename).strip()
        elif field == "year":
            return self.year_from_filename(filename).strip()
        else:
            return ""

    #return the mapped value of the first regex expr that matches the filename
        for regex_expr in regex_dict.keys():
            if re.search(regex_expr, filename, re.IGNORECASE):
                return str(regex_dict[regex_expr]).strip()
        return ""

    @log_class
    def year_from_filename(self, filename):
        #Match 4 digit number in between some kind of brackets, starting with
        #1 or 2. Always take the last match
        try:
            return re.findall("[\[\(\{]([12]\d{3})[\]\)\}]", filename)[-1]
        except IndexError:
            return ""

    @log_class
    def album_from_filename(self, filename):
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

    @log_class
    def construct_album_regex(self, cd):
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

    @log_class
    def parse_tags_from_filename(self, filename):
        """
        Given a filename in an expected format (post-naming tab), suggests
        suitable metadata tags
        """
        tag_dict = {
            "Composer": None, "Album": None, "#": None, "Track": None,
            "Performers": None, "Year": None, "Genre": None, "URL": None
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

    @log_class
    def youtube_url_from_filename(self, filename, do_word_check = False):

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

    @log_class
    def pad_image_with_transparency(
            self, image, pixels, keep_size = False):
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

    @log_class
    def rename_file(self, old_directory, old_name, new_directory,
                    new_name):
        """
        Move and rename the specified file. Works across drives.
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

    def point_is_inside_widget(self, x, y, widget):
        widget.update()
        x_min = widget.winfo_rootx()
        x_max = x_min + widget.winfo_width()
        y_min = widget.winfo_rooty()
        y_max = y_min + widget.winfo_height()

        return x_min <= x <= x_max and y_min <= y <= y_max

    @log_class
    def tag_file(self, directory, filename, tags):
        """
        Given a filename, adds ID3v2 tags to it based on the provided
        dictionary.

        Valid values for the dictionary are:
            Composer, Album, Track, Number OR #, Performer(s), Genre, Year, URL
        """
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

        if not tags.get("performer(s)", "") in [None, ""]:
            audiofile.tag.artist = tags["performer(s)"]

        if not tags.get("genre", "") in [None, ""]:
            audiofile.tag.genre = tags["genre"]

        if not tags.get("url", "") in [None, ""]:
            audiofile.tag.artist_url = tags["url"]

        if not tags.get("number", "") in [None, ""]:
            audiofile.tag.track_num = int(tags["number"])

        if not tags.get("year", "") in [None, ""]:
            audiofile.tag.recording_date = eyed3.core.Date(int(tags["year"]))

        audiofile.tag.save()
        del audiofile
        return

    @log_class
    def add_keyword_pattern(self, values_dict):
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
            pd = config.keyword_dict.add_keyword_pattern(**kwargs)
            if not pd == 'Pattern exists in dictionary, skipping.':
                log.log_trace(config.keyword_dict,
                              "add_keyword_pattern",
                              trace = {},
                              add = f"Added pattern {pd} to dictionary.")
        #Add Composer + Album = Genre + Year
        if valid_values(["composer", "album", "genre"]):
            kwargs = {"Composer": (values_dict["composer"], "key"),
                      "Album": (values_dict["album"], "key"),
                      "Genre": (values_dict["genre"], "value"),
                      "Year": (values_dict["year"], "value")
                      }
            pd = config.keyword_dict.add_keyword_pattern(**kwargs)
            if not pd == 'Pattern exists in dictionary, skipping.':
                log.log_trace(config.keyword_dict,
                              "add_keyword_pattern",
                              trace = {},
                              add = f"Added pattern {pd} to dictionary.")

        #Add Composer + Track = Genre + Year
        if (valid_values(["composer", "track", "genre"])
            and invalid_values(["album"])):
            kwargs = {"Composer": (values_dict["composer"], "key"),
                      "Track": (values_dict["track"], "key"),
                      "Genre": (values_dict["genre"], "value"),
                      "Year": (values_dict["year"], "value")
                      }
            pd = config.keyword_dict.add_keyword_pattern(**kwargs)
            if not pd == 'Pattern exists in dictionary, skipping.':
                log.log_trace(config.keyword_dict,
                              "add_keyword_pattern",
                              trace = {},
                              add = f"Added pattern {pd} to dictionary.")

    @log_class
    def match_filename_pattern(self, filename):
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
        for d in config.filename_patterns_dict.regex_dict.values():
            if re.match(d["match_pattern"], filename, re.IGNORECASE):
                captures = re.search(d["parse_pattern"], filename,
                                     re.IGNORECASE).groupdict()
            else:
                continue

            if type(captures) != dict:
                continue

            for k in captures:
                try:
                    if d["rematch_values"][k]:
                        new_v = self.suggest_value(captures[k], k)
                        if new_v != "":
                            captures[k] = new_v
                except KeyError:
                    continue
            return captures
        return {}

    @log_class
    def timecode_to_seconds(self, timecode):
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
        timecode = timecode.replace(".", ":")
        parts = timecode.split(":")
        mult = 1
        seconds = 0
        while len(parts)>0:
            seconds += int(parts[-1])*mult
            mult = mult*60
            parts = parts[:-1]
        return seconds

    @log_class
    def clean_track_string(self, track, iterate = True):
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
                double_cleaned = self.clean_track_string(track,iterate = False)
                track = double_cleaned
        return track

    @log_class
    def get_values_dict(self, treeview, iid, columns):
        item_dict = treeview.item(iid)
        values_dict = {columns[0]: item_dict['text']}
        for i, v in enumerate(item_dict['values']):
            values_dict[columns[i+1]] = v

        return values_dict

    @log_class
    def autocomplete(self, text, options, out = "list"):
        """
        Autocomplete a string from a defined set of options. Either return the
        first match (out = "string"), or a list of all possible matches
        (out = "list").
        """
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
            if re.match(pattern, str(opt)):
                if out == "string":
                    return str(opt)
                elif out == "list":
                    matches.append(str(opt))
        return matches

    @log_class
    def remove_diacritics(self, text):
        return unidecode.unidecode(text)

    @log_class
    def get_tags(self, directory, filename):
        """
        Return a dictionary of ID3v2 tags for a specific file.
        """
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