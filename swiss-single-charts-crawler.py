from bs4 import BeautifulSoup
from bs4 import NavigableString
from time import sleep
import urllib.request
import re
import csv

BASE_URL = "https://hitparade.ch/showcharttext.asp?week="
CRAWL_DELAY_S = 1


def fetch_week_dom(week):
    with urllib.request.urlopen(BASE_URL + str(week)) as response:
        html = response.read()
        return BeautifulSoup(html, "html.parser")


# with open("week2566.html", "r", encoding="utf-8") as demofile:
#    dom = BeautifulSoup(demofile, "html.parser")


def collect_tags(tag, collected_tags=None, br_counter=0):
    if collected_tags is None:
        collected_tags = []
    next_tag = tag.next_sibling
    collected_tags.append(next_tag)
    if str(next_tag) == "<br/>":
        br_counter += 1
    elif not str(next_tag) == "\n":
        br_counter = 0

    if br_counter >= 2:
        return collected_tags
    else:
        return collect_tags(next_tag, collected_tags, br_counter)


def clean_tags(collected_tags):
    tags = []
    for tag in collected_tags:
        if isinstance(tag, NavigableString) and not str(tag) == "\n":
            clean_tag = str(tag)
            clean_tag = clean_tag.replace("\n", " ")
            clean_tag = clean_tag.strip()
            clean_tag = re.sub(" +", " ", clean_tag)
            tags.append(clean_tag)
    return tags


def parse_entry(entry_string):
    # parse chart placement
    dot_location = entry_string.find(".")
    chart_placement = int(entry_string[:dot_location])
    remainder = entry_string[dot_location + 1:]

    # parse previous week's placement
    ob = remainder.find("(")
    cb = remainder.find(")")
    prev_week = convert_num(remainder[ob + 1:cb])
    remainder = remainder[cb + 1:].strip()

    # parse publisher, bail early if brackets mismatch
    ob, cb = rfind_bracket_indices(remainder)
    if ob is None or cb is None:
        return bail_from_parsing(chart_placement=chart_placement,
                                 prev_week=prev_week,
                                 artist_and_song=remainder)
    publisher = remainder[ob + 1:cb]
    remainder = remainder[:ob].strip()

    # parse week in charts, bail early if brackets mismatch
    ob, cb = rfind_bracket_indices(remainder)
    if ob is None or cb is None:
        return bail_from_parsing(chart_placement=chart_placement,
                                 prev_week=prev_week,
                                 publisher=publisher,
                                 artist_and_song=remainder)
    week_in_charts = parse_week_in_charts(remainder[ob + 1:cb])

    # parse artist and song
    artist_and_song = remainder[:ob].strip()
    artist_song_tuple = split_artist_and_song(artist_and_song)
    if artist_song_tuple is None:
        return bail_from_parsing(chart_placement=chart_placement,
                                 prev_week=prev_week,
                                 publisher=publisher,
                                 week_in_charts=week_in_charts,
                                 artist_and_song=artist_and_song)
    else:
        artist = artist_song_tuple[0]
        song = artist_song_tuple[1]

    # return parsed data
    return {'chart_placement': chart_placement,
            'previous_week': prev_week,
            'publisher': publisher,
            'week_in_charts': week_in_charts,
            'artist_and_song': artist_and_song,
            'artist': artist,
            'song': song,
            'crawler_rejected': "no"}


def bail_from_parsing(chart_placement=0, prev_week="", publisher="", week_in_charts=0, artist_and_song="", artist="",
                      song=""):
    return {'chart_placement': chart_placement,
            'previous_week': prev_week,
            'publisher': publisher,
            'week_in_charts': week_in_charts,
            'artist_and_song': artist_and_song,
            'artist': artist,
            'song': song,
            'crawler_rejected': "yes"}


def rfind_bracket_indices(string):
    cb_index = -1
    parity = 0
    for i in range(len(string) - 1, -1, -1):
        if cb_index < 0 and string[i] == ")":
            cb_index = i
        if string[i] == ")":
            parity += 1
        if string[i] == "(":
            parity -= 1
        if string[i] == "(" and parity == 0 and cb_index >= 0:
            ob_index = i
            return ob_index, cb_index
    return None, None


def convert_num(num_string):
    try:
        num = int(num_string)
        return num
    except ValueError:
        return num_string


def parse_week_in_charts(string):
    dot_location = string.find(".")
    return int(string[:dot_location])


def split_artist_and_song(artist_song_string):
    parts = artist_song_string.split(" - ")
    if len(parts) != 2:
        return None
    else:
        return parts[0].strip(), parts[1].strip()


def get_inquiry_date_dict(dom):
    h2s = dom.find("h2")
    assert len(h2s) == 1
    datestring = h2s.contents[0].strip()
    date_parts = datestring.split(".")
    assert len(date_parts) == 3
    return {"year": int(date_parts[2]), "month": int(date_parts[1]), "day": int(date_parts[0])}


def compose_entry_dict(entry_string, absolute_week, inquiry_date_dict):
    entry_dict = {}
    basic_entry_dict = parse_entry(entry_string)
    entry_dict["absolute_week"] = absolute_week
    entry_dict["inquiry_year"] = inquiry_date_dict["year"]
    entry_dict["inquiry_month"] = inquiry_date_dict["month"]
    entry_dict["inquiry_day"] = inquiry_date_dict["day"]
    entry_dict["chart_placement"] = basic_entry_dict["chart_placement"]
    entry_dict["previous_week"] = basic_entry_dict["previous_week"]
    entry_dict["artist_and_song"] = basic_entry_dict["artist_and_song"]
    entry_dict["artist"] = basic_entry_dict["artist"]
    entry_dict["song"] = basic_entry_dict["song"]
    entry_dict["publisher"] = basic_entry_dict["publisher"]
    entry_dict["week_in_charts"] = basic_entry_dict["week_in_charts"]
    entry_dict["crawler_rejected"] = basic_entry_dict["crawler_rejected"]
    return entry_dict


def entries_to_entry_dict(clean_entry_strings, absolute_week, inquiry_date_dict):
    entries = []
    for entry_string in clean_entry_strings:
        entries.append(compose_entry_dict(entry_string, absolute_week, inquiry_date_dict))
    return entries


def append_one_week(dom, absolute_week, entries):
    start_tag = find_singles_start_tag(dom.findAll("b"))
    assert (start_tag is not None) and (str(start_tag.contents[0]).strip() == "Singles")

    collected_tags = collect_tags(start_tag)
    clean_entries = clean_tags(collected_tags)

    one_week = entries_to_entry_dict(clean_entries, absolute_week, get_inquiry_date_dict(dom))
    for entry in one_week:
        entries.append(entry)


def find_singles_start_tag(b_tags):
    for b_tag in b_tags:
        if str(b_tag.contents[0]).strip() == "Singles":
            return b_tag
    return None


def write_to_file(entries, filename, append=True):
    file_modifier = "a" if append else "w"
    with open(filename, file_modifier, encoding="utf-8") as output_file:
        keys = entries[0].keys()
        dict_writer = csv.DictWriter(output_file, keys, delimiter=',', lineterminator='\n')
        if not append:
            dict_writer.writeheader()
        dict_writer.writerows(entries)


def bulk_download(start_week, end_week, out_filename, temp_filename=None, temp_out_frequency=0, append=True):
    entries = []
    for absolute_week in range(start_week, end_week + 1):
        print("Crawling week {}".format(absolute_week))
        dom = fetch_week_dom(absolute_week)
        append_one_week(dom, absolute_week, entries)
        if temp_out_frequency != 0 and out_filename is not None and absolute_week % temp_out_frequency == 0:
            write_to_file(entries, (temp_filename + "_weeks_{}-{}.csv".format(start_week, absolute_week)), append=False)
        sleep(CRAWL_DELAY_S)
    write_to_file(entries, (out_filename + ".csv"), append=True)


# bulk_download(1, 2566, "swiss_single_charts", "partial_swiss_single_charts", 200, append=True)
bulk_download(2560, 2566, "last_test", append=True)
