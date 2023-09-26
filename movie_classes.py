"""
CSC111 Final Project - Phase 2: Data Parsing - Creating Relevant Classes

Description
===============================

This Python module contains the classes that will be used for file
processing later on in data_parsing.py.

Copyright and Usage Information
===============================

This file is provided solely for the TA's and Computer Science Professors
at the University of Toronto St. George campus. All forms of distribution
of this code, whether as given or with any changes, are expressly prohibited.

This file is Copyright (c) 2023 Guransh Singh, Nauhar Kapur, Shahbaz Nanda,
and Raunak Madan.
"""
# Importing libraries
from __future__ import annotations
import python_ta


class Movie:
    """
    Represents a movie in the movie review network

    Instance Attributes:
    - title: title of the movie
    - genre: genre(s) of the movie
    - users_rated_by: the users that rated this movie

    Representation Invariants:
    # title is empty if and only if genre is empty
    - (self.title != '') == (self.genre != [])
    - all(self in user.movies_rated for user in self.users_rated_by)
    """
    title: str
    genre: list[str]
    users_rated_by: set[User]

    def __init__(self, title: str, genre: list[str]) -> None:
        """Initialize the Movie object with the given parameters."""
        self.title = title
        self.genre = genre
        self.users_rated_by = set()

    def add_user(self, user: User) -> None:
        """
        Add the given user to the users_rated_by set.

        Preconditions:
        - user not in self.users_rated_by
        - self in user.movies_rated
        """
        self.users_rated_by.add(user)


class Rating:
    """
    Represents a rating that 'user' gave to 'movie'.

    Instance Attributes:
    - user: the User object that gave this review
    - movie: the Movie object that this review is intented for
    - rating: the rating, on a scale of 0.0 to 5.0, for the movie

    Representation Invariants:
    - 0.0 <= self.rating <= 5.0
    - self in self.user.movies_rated.values()
    """
    user: User
    movie: Movie
    rating: float

    def __init__(self, user: User, movie: Movie, rating: float) -> None:
        """
        Initialize the Rating object with the given parameters.

        Preconditions:
        - 0.0 <= rating <= 5.0
        - user is a valid User object
        - movie is a valid Movie object
        """
        self.user = user
        self.movie = movie
        self.rating = rating


class User:
    """
    Represents each individual user and reviews they have written

    Instance Attributes:
    - user_id: a unique id number for the user
    - movies_rated: collection of movies and corresponding ratings that the user gives for each movie

    Representation Invariants:
    - all(movie is self.movies_rated[movie].movie for movie in self.movies_rated)
    - all(rating.user is self for rating in self.movies_rated.values())
    """
    user_id: int
    movies_rated: dict[Movie, Rating]

    def __init__(self, user_id: int) -> None:
        """
        Initialize the User class with the given id.
        """
        self.user_id = user_id
        self.movies_rated = {}

    def add_movie_rated(self, movie: Movie, rating: Rating) -> None:
        """
        Add this movie rating to the movies_rated dictionary.

        Preconditions:
        - movie not in self.movies_rated
        """
        self.movies_rated[movie] = rating


class ReviewNetwork:
    """
    Graph structure representing a network of users and movies

    Instance Attributes:
    - movies: collection of movies in the current review system
    - users: collection of users who have joined the given review system

    Representation Invariants:
    - all(name == self.movies[name].title for name in self.movies)
    - all(id == self.users[id].user_id for id in self.users)
    """
    movies: dict[str, Movie]
    users: dict[int, User]

    def __init__(self) -> None:
        """
        Initialize a new movie review network.
        """
        self.movies = {}
        self.users = {}

    def user_exists(self, user_id: int) -> bool:
        """Return whether the user with the given id exists in this network."""
        return user_id in self.users

    def add_user(self, user: User) -> None:
        """
        Add a new user to the given movie review network.

        Do nothing if user already exists in the network's users attribute
        """
        if user.user_id not in self.users:
            self.users[user.user_id] = user

    def movie_exists(self, title: str) -> bool:
        """Return whether the movie with the given title exists in this network."""
        return title in self.movies

    def add_movie(self, movie: Movie) -> None:
        """
        Add a new movie to the review network.

        Do nothing if movie.title is already a key in the network's movies attribute
        """
        if movie.title not in self.movies:
            self.movies[movie.title] = movie

    def get_movie_titles(self) -> set[str]:
        """Return a set of the movie titles of the movies in the current ReviewNetwork"""
        return set(self.movies.keys())


# Testing code
if __name__ == "__main__":
    python_ta.check_all(config={
        'extra-imports': ["annotations"],
        'allowed-io': [],
        'max-line-length': 120
    })
