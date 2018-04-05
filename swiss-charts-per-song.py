import pandas as pd
import csv

print("loading data")
with open("swiss_single_charts.csv", "r", encoding="utf-8") as file:
    dataframe = pd.read_csv(file)

print("fetching unique songs")
unique_songs = dataframe.artist_and_song.unique()
print("Found {} unique songs".format(len(unique_songs)))

song_entries = []
for i, song in enumerate(unique_songs):
    if i % 100 == 0:
        print("processing song {}...".format(i))
    artist_and_song = song
    occurrences = dataframe[dataframe.artist_and_song == artist_and_song]
    first_entry = occurrences.iloc[0]
    title = first_entry.song
    artist = first_entry.artist
    publisher = first_entry.publisher
    year_entered = occurrences.inquiry_year.min()
    year_exited = occurrences.inquiry_year.max()
    best_placement = occurrences.chart_placement.min()
    weeks_at_best_placement = occurrences[occurrences.chart_placement == best_placement].shape[0]
    weeks_at_place_1 = occurrences[occurrences.chart_placement == 1].shape[0]
    prev_week_val_counts = occurrences.previous_week.value_counts()
    if "++" in prev_week_val_counts.index:
        num_reentries = prev_week_val_counts["++"]
    else:
        num_reentries = 0

    mean_placement = occurrences.chart_placement.mean()
    median_placement = occurrences.chart_placement.median()
    total_weeks_in_charts = occurrences.week_in_charts.max()
    weeks_in_top_10 = occurrences[occurrences.chart_placement <= 10].shape[0]
    crawler_rejected = "yes" if "yes" in occurrences.crawler_rejected.unique() else "no"
    song_entries.append({
        "artist_and_song": artist_and_song,
        "artist": artist,
        "song": title,
        "best_placement": best_placement,
        "weeks_at_best_placement": weeks_at_best_placement,
        "weeks_at_place_1": weeks_at_place_1,
        "weeks_in_top_10": weeks_in_top_10,
        "total_weeks_in_charts": total_weeks_in_charts,
        "mean_placement": mean_placement,
        "median_placement": median_placement,
        "num_reentries": num_reentries,
        "year_entered": year_entered,
        "year_exited": year_exited,
        "publisher": publisher,
        "crawler_rejected": crawler_rejected
    })

print("writing data to file")
with open("swiss_single_charts_per_song.csv", "w", encoding="utf-8") as output_file:
        keys = song_entries[0].keys()
        dict_writer = csv.DictWriter(output_file, keys, delimiter=',', lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(song_entries)

print("done")