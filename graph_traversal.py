"""
CSC111 Final Project - Phase 2: Data Parsing - Traversing the Graph

Description
===============================

This Python module traverses a ReviewNetwork and returns the best
movie recommendations to watch, given the user's watch history and
ratings.

Copyright and Usage Information
===============================

This file is provided solely for the TA's and Computer Science Professors
at the University of Toronto St. George campus. All forms of distribution
of this code, whether as given or with any changes, are expressly prohibited.

This file is Copyright (c) 2023 Guransh Singh, Nauhar Kapur, Shahbaz Nanda,
and Raunak Madan.
"""
# Importing libraries
import python_ta
import data_parsing
import movie_classes


# Program constants
REVIEW_NETWORK = data_parsing.create_review_network("CSC111 Final Data.csv")
MOVIE_THRESHOLD = 4.0
SCORE_THRESHOLD = 4.0
GENRE_THRESHOLD = 3.0
ADJUSTMENT_FACTOR = 0.5


# Helper function to run a search on a singular rating
def run_search(title: str, rating: float, accumulator: dict[movie_classes.Movie, list]) -> None:
    """Run a search for good movie recommendations for this review."""
    # Finding 10 closest people
    movie = REVIEW_NETWORK.movies[title]
    user_and_diff = []
    for user in movie.users_rated_by:
        user_rating = user.movies_rated[movie].rating
        user_and_diff.append((user, abs(user_rating - rating)))
    user_and_diff.sort(key=lambda x: x[1])
    top_10_user_ids = [q[0].user_id for q in user_and_diff[:10]]

    # Finding all possible movies
    possible_movies = set()
    for user_id in top_10_user_ids:
        user = REVIEW_NETWORK.users[user_id]
        possible_recs = [w for w in user.movies_rated if user.movies_rated[w].rating >= MOVIE_THRESHOLD]
        possible_movies = possible_movies.union(set(possible_recs))

    if movie in possible_movies:
        possible_movies.remove(movie)

    # Updating accumulator table
    for user_id in top_10_user_ids:
        user = REVIEW_NETWORK.users[user_id]
        for i in user.movies_rated:
            if i == movie or i not in possible_movies:
                continue

            if i in accumulator:
                accumulator[i][0] += 1
                accumulator[i][2] += user.movies_rated[i].rating
            else:
                genre_numerator = len([x for x in movie.genre if x in i.genre])
                genre_denominator_addition = len(i.genre) - genre_numerator
                genre_score = genre_numerator / (len(movie.genre) + genre_denominator_addition)
                genre_score = 1 - genre_score if rating < GENRE_THRESHOLD else genre_score
                accumulator[i] = [1, genre_score, user.movies_rated[i].rating]


# Helper function to run search on all the user's watch history
def run_search_on_all(user_movies: dict[str, float], num_rec: int = 10) -> list[tuple[movie_classes.Movie, float]]:
    """Return the best num_rec recommendations for the user, given their watch history."""
    # Defining accumulator to store search results
    accumulator = {}

    # Running search on all recommendations
    for movie_title in user_movies:
        run_search(movie_title, user_movies[movie_title], accumulator)

    # Computing final scores
    final_scores = []
    for i in accumulator:
        frequency = accumulator[i][0]
        total = accumulator[i][2]
        avg_score = total / frequency
        genre_score = accumulator[i][1]
        new_avg_score = ((avg_score - SCORE_THRESHOLD) * frequency * ADJUSTMENT_FACTOR) + avg_score
        final_score = new_avg_score * genre_score
        final_scores.append((i, final_score))

    # Sorting list and returning top num_rec recommendations
    final_scores.sort(key=lambda x: x[1], reverse=True)
    return final_scores[:num_rec]


# Testing code
if __name__ == "__main__":
    python_ta.check_all(config={
        'extra-imports': ["data_parsing", "movie_classes"],
        'allowed-io': [],
        'max-line-length': 120
    })

    # user_movies_input = {"Mission: Impossible II": 5.0, "The Bourne Identity": 4.5}
    # results = run_search_on_all(user_movies_input, 25)
    # for j in results:
    #     print(f"{j[0].title}: {j[1]}")
