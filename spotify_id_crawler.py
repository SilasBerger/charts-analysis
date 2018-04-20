"""
This script is intended to read-in a data set of type *_charts_per_song.csv, run each title + artist against the
Spotify /v1/search endpoint, retrieve the Spotify-ID of the song if available, and output the same data set with
an additional column containing the Spotify-IDs of all songs in the original data set which are available on Spotify.
"""

"""
General algorithm:

possibleTokenProblem = False
possibleRateProblem = False

load data set file
request Spotify access token
for each entry:
  add entry to list of entries
  search for entry at /v1/search endpoint in Spotify API
  
  if 429 (rate limit reached):
    # make sure not to get stuck in a rate limit problem
    if possibleRateProblem:
      exit("Rate problem encountered")
    possibleRateProblem = True  # rate limit error occurred
    extract Retry-After header field
    wait for (Retry-After + 1) seconds
    
  if token expired:
    # make sure not to get stuck in a rate limit problem
    if possibleTokenProblem:
      exit("Token problem encountered")
    possibleTokenProblem = True  # token error occurred
    request new access token
    retry line
  
  # token and rate seem to be okay
  possibleTokenProblem = False
  possibleRateProblem = False
  
  if exactly 1 result:
    extract id
    add id to entry
  else:
    mark entry as "ambiguous on Spotify"
    
export all entries to CSV
    
"""