"""
CSC111 Final Project - Phase 3: UI Design and Implementation - Parsing API Results

Description
===============================

This Python module contains the code required to run a movie server API
and collect information such as rent, trailer and poster links for a
given movie, along with the IMDb rating.

Copyright and Usage Information
===============================

This file is provided solely for the TA's and Computer Science Professors
at the University of Toronto St. George campus. All forms of distribution
of this code, whether as given or with any changes, are expressly prohibited.

This file is Copyright (c) 2023 Guransh Singh, Nauhar Kapur, Shahbaz Nanda,
and Raunak Madan.
"""
# Importing libraries
import json
import requests
import python_ta


def run_api(search_title: str, api_key: str = "", api_host: str = "") -> list[str]:
    """Run the movie API and return the corresponding rent, trailer and poster links for the given title,
    along with the IMDb rating.

    Preconditions:
        - search_title != ""
        - api_key == "" or api_key is a valid API key
        - api_host == "" or api_host is a valid API host server
        """
    # Running API query
    url = "https://streaming-availability.p.rapidapi.com/v2/search/title"
    querystring = {"title": search_title, "country": "us", "show_type": "movie", "output_language": "en"}
    if api_key == "":
        key = "6a537661b7mshff9369efe0cc380p15d036jsn2812fda7b6bf"
    else:
        key = api_key
    if api_host == "":
        host = "streaming-availability.p.rapidapi.com"
    else:
        host = api_host
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    response = requests.request("GET", url, headers=headers, params=querystring)

    # Parsing data into dictionaries
    data = json.loads(response.text)
    formatted_data = json.dumps(data, indent=4)
    data_dict = json.loads(formatted_data)

    # Finding movie title match
    all_titles = [i["title"] for i in data_dict["result"]]
    best_match_title = find_best_title(search_title, all_titles)

    # Returning link info
    links = find_info_from_title(data_dict["result"], best_match_title)
    return links


def parse_string(given_string: str) -> str:
    """Return a lowercase version of the given string, without punctuation or
    special characters - with some exceptions."""
    new_string = ""
    exceptions = {" ", "&"}
    for i in given_string:
        if i.isalnum() or i in exceptions:
            new_string += i.lower()
    return new_string


def get_comparison_score(original_title: str, test_title: str) -> float:
    """Return a comparison score of the given strings."""
    original_words = [parse_string(i) for i in original_title.split()]
    test_words = [parse_string(i) for i in test_title.split()]
    score_numerator = len([x for x in original_words if x in test_words])
    score_denominator_addition = len(test_words) - score_numerator
    score = score_numerator / (len(original_words) + score_denominator_addition)
    return score


def tie_breaker(original_title: str, equal_titles: list[str]) -> str:
    """Return the title with the highest likelihood of matching the original title.

    Preconditions:
        - isinstance(original_title, str)
        - isinstance(equal_titles, list)
        - all(isinstance(x, str) for x in equal_titles)"""
    ignore_words = {"and", "the", "or", "&"}
    original_words = [parse_string(i) for i in original_title.split()]
    best_match_score = 0
    best_title = ""
    for title in equal_titles:
        important_match_count = 0
        words = [parse_string(i) for i in title]
        for word in words:
            if word not in ignore_words and word in original_words:
                important_match_count += 1
        if important_match_count >= best_match_score:
            best_match_score = important_match_count
            best_title = title
    return best_title


def find_best_title(original_title: str, test_titles: list[str]) -> str:
    """Return the title with the highest comparison score, accounting for ties.

    Preconditions:
        - isinstance(original_title, str)
        - isinstance(test_titles, list)
        - all(isinstance(x, str) for x in test_titles)
    """
    score_summary = []
    for title in test_titles:
        score = get_comparison_score(original_title, title)
        score_summary.append((title, score))
    score_summary.sort(key=lambda x: x[1], reverse=True)
    ties = [score_summary[0][0]]
    best_score = score_summary[0][1]
    i = 1
    while i < len(score_summary) and score_summary[i][1] == best_score:
        ties.append(score_summary[i][0])
        i += 1
    return tie_breaker(original_title, ties)


def find_info_from_title(results: list[dict], search_title: str) -> list[str]:
    """Return the associated rent, trailer and poster links for the given title,
    along with the IMDb rating.

    Preconditions:
        - isinstance(search_title, str)
        - all(isinstance(x, dict) for x in results)
    """
    # Program variables
    rent_link = ""
    trailer_link = ""
    poster_link = ""
    imdb_rating = ""

    for i in results:

        # Checking for title match
        if i["title"] == search_title:

            # Getting rent_link
            try:
                purchase_options = i["streamingInfo"]["us"]["prime"]
                rent_link = purchase_options[0]["link"]
            except KeyError:
                try:
                    purchase_options = i["streamingInfo"]["us"]["apple"]
                    rent_link = purchase_options[0]["link"]
                except KeyError:
                    try:
                        purchase_options = i["streamingInfo"]["us"]["hbo"]
                        rent_link = purchase_options[0]["link"]
                    except KeyError:
                        try:
                            purchase_options = i["streamingInfo"]["us"]["hulu"]
                            rent_link = purchase_options[0]["link"]
                        except KeyError:
                            pass

            # Getting movie trailer link
            try:
                trailer_link = i["youtubeTrailerVideoLink"]
            except KeyError:
                pass

            # Getting movie poster link
            try:
                poster_link = i["posterURLs"]["original"]
            except KeyError:
                pass

            # Getting imdb rating
            try:
                imdb_rating = str(i["imdbRating"]) + "%"
            except KeyError:
                pass

    return [rent_link, trailer_link, poster_link, imdb_rating]


# Testing code
if __name__ == "__main__":
    python_ta.check_all(config={
        'extra-imports': ["json", "requests"],
        'allowed-io': [],
        'max-line-length': 120
    })

    # links = run_api("Mission)*(@# Impossibl^#e Ghost Protocol()@#*")
    # print(f"Rent Link: {links[0]}")
    # print(f"Trailer Link: {links[1]}")
    # print(f"Poster Link: {links[2]}")
    # print(f"IMDb Rating: {links[3]}")
