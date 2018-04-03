from bs4 import BeautifulSoup
from bs4 import NavigableString
import urllib.request
import re
import csv

base_url = "https://hitparade.ch/showcharttext.asp?week="


def fetch_week_dom(week):
    with urllib.request.urlopen(base_url + str(week)) as response:
        html = response.read()
        return BeautifulSoup(html, "html.parser").prettify()


with open("week2566.html", "r", encoding="utf-8") as demofile:
    dom = BeautifulSoup(demofile, "html.parser")


def collect_tags(tag, collected_tags=[], br_counter=0):
    next_tag = tag.next_sibling
    collected_tags.append(next_tag)
    if str(next_tag) == "<br/>":
        br_counter += 1
    elif not str(next_tag) == "\n":
        br_counter = 0

    if br_counter >= 3:
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
    dot_location = entry_string.find(".")
    chart_placement = int(entry_string[:dot_location])
    remainder = entry_string[dot_location+1:]
    ob = remainder.find("(")
    cb = remainder.find(")")
    prev_week = convert_num(remainder[ob+1:cb])
    remainder = remainder[cb+1:].strip()
    ob = remainder.rfind("(")
    cb = remainder.rfind(")")
    publisher = remainder[ob+1:cb]
    remainder = remainder[:ob].strip()
    ob = remainder.rfind("(")
    cb = remainder.rfind(")")
    week_in_charts = parse_week_in_charts(remainder[ob + 1:cb])
    artist_and_song = remainder[:ob].strip()
    artist_song_tuple = split_artist_and_song(artist_and_song)
    if artist_song_tuple is None:
        artist = ""
        song = ""
        rejected_artist_song = artist_and_song
    else:
        artist = artist_song_tuple[0]
        song = artist_song_tuple[1]
        rejected_artist_song = ""
    return {'chart_placement': chart_placement,
            'previous_week': prev_week,
            'publisher': publisher,
            'week_in_charts': week_in_charts,
            'artist': artist,
            'song': song,
            'rejected_artist_and_song': rejected_artist_song}


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


def compose_entry_dict(entry_string, absolute_week):
    entry_dict = {}
    basic_entry_dict = parse_entry(entry_string)
    entry_dict["absolute_week"] = absolute_week
    entry_dict["chart_placement"] = basic_entry_dict["chart_placement"]
    entry_dict["previous_week"] = basic_entry_dict["previous_week"]
    entry_dict["artist"] = basic_entry_dict["artist"]
    entry_dict["song"] = basic_entry_dict["song"]
    entry_dict["publisher"] = basic_entry_dict["publisher"]
    entry_dict["week_in_charts"] = basic_entry_dict["week_in_charts"]
    entry_dict["rejected_artist_and_song"] = basic_entry_dict["rejected_artist_and_song"]
    return entry_dict


def entries_to_entry_dict(clean_entry_strings, absolute_week):
    entries = []
    for entry_string in clean_entry_strings:
        entries.append(compose_entry_dict(entry_string, absolute_week))
    return entries


html_text = dom.prettify()
b_tags = dom.findAll("b")
assert len(b_tags) == 1
start_tag = b_tags[0]
assert len(start_tag.contents) == 1
start_tag_contents = str(start_tag.contents[0]).strip()
assert start_tag_contents == "Singles"

collected_tags = collect_tags(start_tag)
clean_entries = clean_tags(collected_tags)

one_week = entries_to_entry_dict(clean_entries, 2566)

keys = one_week[0].keys()
with open('test.csv', 'w', encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, keys, delimiter=',', lineterminator='\n')
    dict_writer.writeheader()
    dict_writer.writerows(one_week)