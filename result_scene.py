"""
CSC111 Final Project - Phase 3: UI Design and Implementation - Result Scene Class

Description
===============================

This Python module contains the ResultScene class, which visualizes and
displays an interactive output screen for the user to view his/her movie
recommendations.

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
import io
import sys
import webbrowser
from urllib.request import urlopen
import pygame
import python_ta
import api_parser


# Program constants
DEFAULT_SIZE = (200, 330)
POSTER_LOCATIONS = [(100, 20), (350, 20), (600, 20), (850, 20), (1100, 20), (100, 430), (350, 430), (600, 430),
                    (850, 430), (1100, 430)]


# Defining result scene class
class ResultScene:
    """
    A result scene class to store the Pygame layout for the movie recommendation results.

    Instance Attributes:
    - movie_titles: Stores the movie titles of the movies that will be displayed on screen.
    - trailer_links: Stores a list of strings representing YouTube trailer links for the displayed movies.
    - poster_rects: Stores the pygame Rect objects for the movie posters.
    - rent_rects: Stores the pygame Rect objects for the movie rent buttons.
    - screen: Stores the pygame screen on which all objects and images will be displayed.
    - posters_drawn: Stores whether the various objects, such as movie posters, have been drawn on screen.
    - link_results: Stores a list of lists, where each inner list contains relevant links for each movie on screen.

    Representation Invariants:
    - len(self.movie_titles) == 10
    - all(len(movie_link_result) == 4 for movie_link_result in self.link_results)
    """
    movie_titles: list[str]
    trailer_links: list[str]
    rent_links: list[str]
    poster_rects: list[pygame.Rect]
    rent_rects: list[pygame.Rect]
    screen: pygame.Surface
    posters_drawn: bool
    link_results: list[list[str]]

    def __init__(self, movie_titles: list[str]) -> None:
        """
        Initializer for the result scene class.

        Preconditions:
        - len(movie_titles) == 10
        """
        self.screen = pygame.display.set_mode([1500, 850])
        self.movie_titles = movie_titles
        self.trailer_links = []
        self.poster_rects = []
        self.rent_rects = []
        self.posters_drawn = False
        self.link_results = self.get_links_for_movies()

    def get_links_for_movies(self) -> list[list[str]]:
        """Return the rent, trailer and poster links for the movies contained in self.movie_titles,
        along with the IMDb rating."""
        link_results = []
        for title in self.movie_titles:
            try:
                links = api_parser.run_api(title)
            except KeyError:
                try:
                    links = api_parser.run_api(title, "9b0499a6d0msha5373448155f126p1dbc86jsne6e5da63ee3b")
                except KeyError:
                    try:
                        links = api_parser.run_api(title, "45dfa9c982msh748b72a3ace08f7p1f4c84jsn30c598f9d44e")
                    except KeyError:
                        try:
                            links = api_parser.run_api(title, "eff08fa849msh2a5ea7560fe2dfdp118e8bjsnfa6525831061")
                        except KeyError:
                            links = ["", "", "", ""]
            link_results.append(links)
        return link_results

    def handle_event(self) -> None:
        """
        Check for user interaction with the current ResultScene, and update the current ResultScene attributes to
        respond to the user's interactions.
        """
        # Checking program events
        event_list = pygame.event.get()
        rent_links = [w[0] for w in self.link_results]
        for event in event_list:

            # Checking program exit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Checking mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for poster_rect_index in range(10):
                    if self.poster_rects[poster_rect_index].collidepoint(event.pos):
                        if self.trailer_links[poster_rect_index] == "":
                            continue
                        webbrowser.open(
                            rf"{self.trailer_links[poster_rect_index]}"
                            r"-42e4-8ef7-7fed1973bb8f&pf_rd_r=AY29H1PCPTHZXTRCGVQV&pf_rd_s=center-1&pf_rd_t=15506"
                            r"&pf_rd_i=top&ref_=chttp_tt_5")

                for rent_rect_index in range(10):
                    if self.rent_rects[rent_rect_index].collidepoint(event.pos):
                        if rent_links[rent_rect_index] == "":
                            continue
                        webbrowser.open(
                            rf"{rent_links[rent_rect_index]}"
                            r"-42e4-8ef7-7fed1973bb8f&pf_rd_r=AY29H1PCPTHZXTRCGVQV&pf_rd_s=center-1&pf_rd_t=15506"
                            r"&pf_rd_i=top&ref_=chttp_tt_5")

            # Checking mouse motion
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
                match = False
                for i in range(10):
                    poster_location = POSTER_LOCATIONS[i]
                    poster_x, poster_y = poster_location
                    if poster_x <= x <= poster_x + DEFAULT_SIZE[0] and poster_y <= y <= poster_y + DEFAULT_SIZE[1]:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        pygame.draw.rect(self.screen, (255, 255, 255), (poster_x, poster_y, DEFAULT_SIZE[0],
                                                                        DEFAULT_SIZE[1]),
                                         3, border_radius=1)
                        match = True
                        break
                for poster_location in POSTER_LOCATIONS:
                    rent_x, rent_y = poster_location
                    rent_y += (DEFAULT_SIZE[1] + 10)
                    if rent_x <= x <= rent_x + 70 and rent_y <= y <= rent_y + 30:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                        pygame.draw.rect(self.screen, (255, 255, 255), (rent_x - 3, rent_y - 3, 76, 36),
                                         3, border_radius=1)
                        match = True
                        break

                if not match:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    for i in range(10):
                        poster_location = POSTER_LOCATIONS[i]
                        poster_x, poster_y = poster_location
                        pygame.draw.rect(self.screen, (0, 0, 0), (poster_x, poster_y, DEFAULT_SIZE[0], DEFAULT_SIZE[1]),
                                         3, border_radius=1)
                    for i in range(10):
                        poster_location = POSTER_LOCATIONS[i]
                        rent_x, rent_y = poster_location
                        rent_y += (DEFAULT_SIZE[1] + 10)
                        pygame.draw.rect(self.screen, (0, 0, 0), (rent_x - 3, rent_y - 3, 76, 36),
                                         3, border_radius=1)

    def draw(self) -> None:
        """
        Display movie posters and corresponding trailer/rent links on the current ResultScene's Pygame window,
        given the list of movie data from self.link_results.
        """
        link_font = pygame.font.SysFont('trebuchetms', 25)
        poster_location_index = 0

        # Displaying poster info
        for movie_link_result in self.link_results:
            if self.posters_drawn:
                continue

            # Adding trailer links
            self.trailer_links.append(movie_link_result[1])

            # Fixing url and converting to image
            poster_link = "http" + movie_link_result[2][5:]
            with urlopen(poster_link) as image_str:
                image_str = image_str.read()
            image_file = io.BytesIO(image_str)
            image = pygame.image.load(image_file)

            # Scaling image and drawing on screen
            image = pygame.transform.scale(image, DEFAULT_SIZE)
            image_rect = image.get_rect(topleft=POSTER_LOCATIONS[poster_location_index])
            self.screen.blit(image, image_rect)

            # Adding poster rect object to class attribute
            self.poster_rects.append(image_rect)

            # Creating rent text
            coordinate_x = POSTER_LOCATIONS[poster_location_index][0]
            coordinate_y = POSTER_LOCATIONS[poster_location_index][1] + DEFAULT_SIZE[1] + 10
            rent_rect = pygame.Rect(coordinate_x, coordinate_y, 70, 30)
            rent_surface = link_font.render('Rent', True, pygame.Color('darkgoldenrod'))
            pygame.draw.rect(self.screen, pygame.Color(21, 21, 81), rent_rect)
            self.screen.blit(rent_surface, (rent_rect.x + 5, rent_rect.y + 5))

            # Updating class attribute
            self.rent_rects.append(rent_rect)

            # Creating rating text
            coordinate_x = POSTER_LOCATIONS[poster_location_index][0] + DEFAULT_SIZE[0] - 70
            coordinate_y = POSTER_LOCATIONS[poster_location_index][1] + DEFAULT_SIZE[1] + 10
            rating_rect = pygame.Rect(coordinate_x, coordinate_y, 70, 30)
            rating_surface = link_font.render(movie_link_result[3], True, pygame.Color('darkgoldenrod'))
            pygame.draw.rect(self.screen, pygame.Color(21, 21, 81), rating_rect)
            self.screen.blit(rating_surface, (rating_rect.x + 23, rating_rect.y + 5))

            # Updating loop index
            poster_location_index += 1

        # Updating draw boolean
        self.posters_drawn = True


# Testing code
if __name__ == "__main__":
    python_ta.check_all(config={
        'extra-imports': ["annotations", "io", "sys", "pygame", "webbrowser", "api_parser", "urllib.request"],
        'allowed-io': [],
        'disable': ["too-many-branches", "too-many-nested-blocks"],
        'generated-members': ['pygame.*'],
        'max-line-length': 120
    })

    # titles = ["Mission Impossible - Ghost Protocol", "The Bourne Supremacy", "Fast Five", "The Dark Knight",
    #           "Iron Man 2", "Captain America Civil War", "Mission Impossible - Ghost Protocol",
    #           "The Bourne Supremacy", "Fast Five", "The Dark Knight"]
    # results = ResultScene(titles)
