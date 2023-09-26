"""
CSC111 Final Project - Phase 2: Data Parsing - Creating a Network Graph

Description
===============================

This Python module parses a CSV file and populates a ReviewNetwork
specified in movie_classes.py.

Copyright and Usage Information
===============================

This file is provided solely for the TA's and Computer Science Professors
at the University of Toronto St. George campus. All forms of distribution
of this code, whether as given or with any changes, are expressly prohibited.

This file is Copyright (c) 2023 Guransh Singh, Nauhar Kapur, Shahbaz Nanda,
and Raunak Madan.
"""
# Importing libraries
import csv
import python_ta
import movie_classes


def create_review_network(csv_file: str) -> movie_classes.ReviewNetwork:
    """Create a review network by parsing the provided CSV file."""
    # Creating network
    review_network = movie_classes.ReviewNetwork()

    # Reading file
    with open(csv_file) as file:
        header = True
        reader = csv.reader(file)

        for row in reader:
            if header:
                header = False
            else:
                # Typecasting
                user_id = int(row[1])
                rating_score = float(row[2])
                movie_title = row[3]
                movie_genres = row[4].split('-')

                # Creating user object
                if not review_network.user_exists(user_id):
                    new_user = movie_classes.User(user_id)
                    review_network.add_user(new_user)
                else:
                    new_user = review_network.users[user_id]

                # Creating movie object
                if not review_network.movie_exists(movie_title):
                    new_movie = movie_classes.Movie(movie_title, movie_genres)
                    review_network.add_movie(new_movie)
                else:
                    new_movie = review_network.movies[movie_title]

                # Creating rating
                new_rating = movie_classes.Rating(new_user, new_movie, rating_score)

                # Updating user and movie to include new rating
                new_user.add_movie_rated(new_movie, new_rating)
                new_movie.add_user(new_user)

    # Returning fully parsed network
    return review_network


# Testing code
if __name__ == "__main__":
    python_ta.check_all(config={
        'extra-imports': ["csv", "movie_classes"],
        'allowed-io': ["create_review_network"],
        'max-line-length': 120
    })

    # review_network = create_review_network("CSC111 Final Data.csv")
    # test_movie = review_network.movies["Terminator Salvation"]
    # test_user = review_network.users[7]
    # users = test_movie.users_rated_by
