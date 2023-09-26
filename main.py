"""
CSC111 Final Project - Phase 3: UI Design and Implementation - Menu Scene Class

Description
===============================

This Python module contains the MenuScene class, which visualizes and
displays an interactive input screen for the user to enter his/her
watch history and respective movie ratings.

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
from typing import Optional
import webbrowser
import sys
import random
import tkinter as tk
import python_ta
import pygame
from result_scene import ResultScene
import data_parsing
import graph_traversal

# Getting the screen resolution
ROOT = tk.Tk()
SCREEN_WIDTH = ROOT.winfo_screenwidth() - 100
SCREEN_HEIGHT = ROOT.winfo_screenheight() - 150

# Initializing pygame
DIMENSIONS = pygame.init()

# Defining ratio sizes
ASPECT_RATIO = 1.5
POSTER_RATIO = SCREEN_WIDTH * 0.07
DEFAULT_IMAGE_SIZE = (POSTER_RATIO, POSTER_RATIO * ASPECT_RATIO)

# Defining colors
BLUE = pygame.Color('dodgerblue')
GOLDEN = pygame.Color('darkgoldenrod')
RED = pygame.Color('crimson')
WHITE = pygame.Color('ghostwhite')

# Getting network from data_parsing
REVIEW_NETWORK = data_parsing.create_review_network('CSC111 Final Data.csv')

# Starting pygame clock
CLOCK = pygame.time.Clock()


class DropDown:
    """
    Class representing an interactive drop-down menu.

    Instance Attributes:
    - color_menu: default color(s) of the menu
    - color_option: color(s) for each drop-down option of the menu
    - rect: rectangle representing one slot in the drop-down menu
    - font: text font for all text inside the drop-down menu
    - main: main title/label of the drop-down menu
    - options: list of possible options presented by the drop-down menu
    - draw_menu: bool to determine whether to draw the expanded drop-down menu
    - menu_active: bool to determine whether the user's mouse is hovering over the drop-down menu
    - active_option: int to represent the index of the rectangle in the drop-down menu that the user is accessing

    Representation Invariants:
    - len(self.color_menu) >= 2
    - len(self.color_option) >= 2
    - len(self.options) > 0
    - self.main != ''
    - self.active_option < len(self.options)
    """
    color_menu: list[pygame.color.Color] | tuple[int]
    color_option: list[pygame.color.Color] | tuple[int]
    rect: pygame.Rect
    font: pygame.font.Font
    main: str
    options: list[str]
    draw_menu: bool
    menu_active: bool
    active_option: int

    def __init__(self, color_menu: list[pygame.color.Color] | tuple[int], dims: list[int | float],
                 font: pygame.font.Font, labels: list[str]) -> None:
        """
        Instantiate a DropDown Menu with the given paramaters.

        Preconditions:
        - len(dims) == 4
        - len(labels) >= 2
        - len(color_menu) >= 2
        - labels[0] != ''
        """
        self.color_menu = color_menu
        self.color_option = color_menu
        self.rect = pygame.Rect(dims[0], dims[1], dims[2], dims[3])
        self.font = font
        self.main = labels[0]
        self.options = labels[1:]
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf: pygame.Surface) -> None:
        """Draw the given drop-down menu on the pygame surface given by surf.

        The main title/label of the drop-down menu is always displayed on the pygame surface, and the
        possible options are displayed if self.draw_menu is True (i.e. if the user clicks on the drop-down menu when
        the menu is compressed)."""

        # display the main title/label of the drop-down menu on surf
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, True, WHITE)
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        # display the expanded drop-down menu on surf if self.draw_menu is True
        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, True, WHITE)
                surf.blit(msg, msg.get_rect(center=rect.center))

    def update(self, event_list: list[pygame.event.Event], scene: MenuScene) -> int:
        """
        Keep track of user interactions and handle all events in event_list relating to the drop-down menu.
        Update the drop-down menu's attributes and/or the attributes of scene as necessary.
        """

        # get the user's mouse position and determine if it collides with the drop-down menu
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        # checking if the user's mouse collides with any of the option boxes of the drop-down menu
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        # check hover
        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        # looping through user events/interactions with the drop-down menu
        for event in event_list:

            # checking for mouse clicks on the drop-down menu
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu

                # adding drop-down menu options to movie title text boxes of scene if expanded menu is drawn
                # and a text box of scene is selected.
                elif self.draw_menu and self.active_option >= 0:
                    for i in range(len(scene.user_texts)):
                        if scene.textbox_index is not None:
                            scene.user_texts[scene.textbox_index] = self.options[self.active_option]
                            break
                        elif scene.user_texts[i] == '':
                            scene.user_texts[i] = self.options[self.active_option]
                            self.draw_menu = not self.draw_menu
                            break

        return -1


class MenuScene:
    """
    Class representing the initial Menu Scnene which displays upon running the application.

    Includes functionality for entering movie titles/ratings and displaying current popular movies.

    Instance Attributes:
    - active: Whether the user has made a meaningful interaction with the current MenuScene.
    - textbox_index: index corresponding to the rectangle (text box) that was clicked by the user's mouse.
    - ratingbox_index: index corresponding to the rectangle (rating box) that was clicked by the user's mouse.
    - posters_dict: dictionary mapping movie titles of popular movies to corresponding trailer links.
    - chosen_posters: list of movie posters chosen randomly from posters_list to be displayed on a pygame window.
    - user_text_rects: list of rectangles that highlight the text boxes for inputting movie titles.
    - rating_rects: list of rectangles that highlight the text boxs for inputting movie ratings.
    - user_texts: list of strings which represent the user's input into the movie title text boxes.
    - rating_texts: list of strings which represent the user's input into the movie rating text boxes.
    - screen: Pygame Surface for displaying the contents of the current MenuScene.
    - screen_w: width of the Pygame Surface represented by the screen attribute.
    - screen_h: height of the Pygame Surface represented by the screen attribute.
    - dropdown: DropDown menu for displaying possible movies to choose from if the user cannot think of any movies
                to rate.
    - movies: set of all known movies in the movie review network. Used to check the validity of the user's input
    - submit_permitted: bool representing whether the user can proceed to the result scene with movie
            recommendations.
    - user_submissions: dictionary mapping user's movie title input to corresponding movie rating input

    Representation Invariants:
    - not(self.textbox_index is not None and self.ratingbox_index is not None)
    - len(self.movies) > 0
    - len(self.user_texts) == len(self.user_text_rects)
    - len(self.rating_texts) == len(self.rating_rects)
    - len(self.user_texts) == len(self.rating_texts)
    - len(self.posters_dict) > 0
    """
    active: bool
    textbox_index: Optional[int]
    ratingbox_index: Optional[int]
    posters_dict: dict[str]
    chosen_posters: list[tuple]
    user_text_rects: list[pygame.Rect]
    rating_rects: list[pygame.Rect]
    submit_rect: pygame.Rect
    user_texts: list[str]
    rating_texts: list[str]
    screen: pygame.Surface
    screen_w: int | float
    screen_h: int | float
    dropdown: DropDown
    movies: set[str]
    submit_permitted: Optional[bool]
    user_submissions: dict[str, float]

    def __init__(self, movie_set: set[str]) -> None:
        """
        Initialize a new MenuScene with default attributes and with movie_set as a set of all known movies in the review
        network.
        """
        # initializing instance attributes
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_w = SCREEN_WIDTH
        self.screen_h = SCREEN_HEIGHT
        self.active = False
        self.textbox_index = None
        self.ratingbox_index = None
        self.movies = movie_set
        self.posters_dict = {
            "12 Angry Men": r"https://www.imdb.com/title/tt0050083/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=1a264172"
                            r"-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=AY29H1PCPTHZXTRCGVQV&pf_rd_s=center-1"
                            r"&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_5",
            "The Dark Knight": r"https://www.imdb.com/title/tt0468569/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=1a264172"
                               r"-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=AY29H1PCPTHZXTRCGVQV&pf_rd_s=center-1"
                               r"&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_3",
            "The Godfather": r"https://www.imdb.com/title/tt0068646/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=1a264172"
                             r"-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=AY29H1PCPTHZXTRCGVQV&pf_rd_s=center-1"
                             r"&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_2",
            "The Shawshank Redemption": r"https://www.imdb.com/title/tt0111161/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p"
                                        r"=1a264172-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=AY29H1PCPTHZXTRCGVQV"
                                        r"&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_1",
            "Schindler's List": r"https://www.imdb.com/title/tt0108052/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=1a264172"
                                r"-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=4GCPMC1MJNZQEQHH50KH&pf_rd_s=center-1"
                                r"&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_6",
            "The Godfather Part 2": r"https://www.imdb.com/title/tt0071562/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p"
                                    r"=1a264172-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=4GCPMC1MJNZQEQHH50KH"
                                    r"&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_4",
            "Pulp Fiction": r"https://www.imdb.com/title/tt0110912/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=1a264172"
                            r"-ae11-42e4-8ef7-7fed1973bb8f&pf_rd_r=4GCPMC1MJNZQEQHH50KH&pf_rd_s=center-1"
                            r"&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_8",
            "The Bourne Supremacy": r"https://www.imdb.com/title/tt0372183/?ref_=nv_sr_srsg_0",
            "Mission Impossible": r"https://www.imdb.com/title/tt0117060/?ref_=nv_sr_srsg_0",
            "Titanic": r"https://www.imdb.com/title/tt0120338/?ref_=nv_sr_srsg_0"}

        self.chosen_posters = []
        self.user_text_rects = []
        self.rating_rects = []

        # initializing variables for scaling UI components to the MenuScene's Pygame screen size
        text_box_scale_width = SCREEN_WIDTH * 0.03
        text_box_scale_height = SCREEN_HEIGHT * 0.15
        gap = SCREEN_HEIGHT * 0.125
        text_box_height_ratio = SCREEN_HEIGHT * 0.05
        text_box_width_ratio = SCREEN_WIDTH * 0.25

        rating_box_scale_width = SCREEN_WIDTH * 0.5
        rating_box_width_ratio = SCREEN_WIDTH * 0.04

        # creating movie title text boxes and movie rating text boxes
        for j in range(5):
            self.user_text_rects.append(pygame.Rect(text_box_scale_width, gap * (j + 1) + text_box_scale_height,
                                                    text_box_width_ratio, text_box_height_ratio))
        for j in range(5):
            self.rating_rects.append(pygame.Rect(rating_box_scale_width, gap * (j + 1) + text_box_scale_height,
                                                 rating_box_width_ratio, text_box_height_ratio))

        self.submit_rect = pygame.Rect(self.user_text_rects[0].x + 0.1 * self.screen_w,
                                       0.9 * self.screen_h, 0.21 * self.screen_w, 0.05 * self.screen_h)

        # creating a list of empty strings (representing no text input to the MenuScene)
        self.user_texts = [''] * len(self.user_text_rects)
        self.rating_texts = [''] * len(self.rating_rects)

        # choosing random movie posters to be featured on the current MenuScene
        for _ in range(4):
            random_title = random.choice(list(self.posters_dict.keys()))
            random_image = pygame.transform.scale(pygame.image.load(f'Posters/{random_title}.png'), DEFAULT_IMAGE_SIZE)
            self.chosen_posters.append((random_title, (random_image, self.posters_dict[random_title])))
            self.posters_dict.pop(random_title)

        good_size_movies = []

        # collecting potential movies from the review network to add to the scene's drop down menu
        for movie in REVIEW_NETWORK.movies:
            text_width = pygame.font.SysFont('trebuchetms', 20).size(movie)[0]
            if text_width <= 400:
                good_size_movies.append(movie)

        # creating a dropdown menu with random movie selection options from good_size_movies
        self.dropdown = DropDown(
            [BLUE, GOLDEN],
            [SCREEN_WIDTH * 0.35, 3, SCREEN_WIDTH * 0.35, SCREEN_HEIGHT * 0.07],
            pygame.font.SysFont('trebuchetms', 20),
            ["Some Movie Selections"] + random.choices(good_size_movies, k=10))

        # initializing more instance attributes
        self.submit_permitted = None
        self.user_submissions = {}
        pygame.key.set_repeat(300, 100)

    def _event_action(self, event: pygame.event.Event) -> None:
        """
        Helper method for MenuScene.handle_event.
        """

        # checking if the user presses a key after clicking on a text box or rating box
        if event.type == pygame.KEYDOWN and self.active:
            pygame.key.get_repeat()

            # checking if backspace was pressed and removing text as necessary
            if event.key == pygame.K_BACKSPACE:
                if self.textbox_index is not None:
                    self.user_texts[self.textbox_index] = self.user_texts[self.textbox_index][:-1]
                elif self.ratingbox_index is not None:
                    self.rating_texts[self.ratingbox_index] = self.rating_texts[self.ratingbox_index][:-1]

            # checking if a movie rating box was accessed and adding text to the corresponding box
            elif self.ratingbox_index is not None:
                if (pygame.key.name(event.key).isdigit() or event.unicode == '.') and \
                        len(self.rating_texts[self.ratingbox_index]) < 3:
                    self.rating_texts[self.ratingbox_index] += event.unicode

            # adding text to the movie title text boxes
            elif self.textbox_index is not None and event.key != pygame.K_RETURN:
                self.user_texts[self.textbox_index] += event.unicode

            # changing the textbox focus if the user presses the enter key
            if event.key == pygame.K_RETURN:
                if self.textbox_index is not None:
                    self.textbox_index, self.ratingbox_index = None, self.textbox_index
                    event.key = 0
                elif event.key is not None and self.ratingbox_index is not None:
                    if self.ratingbox_index < 4:
                        self.ratingbox_index, self.textbox_index = None, self.ratingbox_index + 1

    def handle_event(self) -> None:
        """
        Check for user interaction with the current MenuScene, and update the current MenuScene attributes to
        keep track of the user's interactions.
        """

        # getting a list of user events/interactions with the current MenuScene
        event_list = pygame.event.get()

        poster_coord_width = SCREEN_WIDTH * 0.8
        poster_coord_height = SCREEN_HEIGHT * 0.13
        poster_gap = SCREEN_HEIGHT * 0.215

        # checking for interactions with the drop-down menu and updating its attributes as necessary
        self.dropdown.update(event_list, self)

        # looping through user events/interactions with the MenuScene
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # checking for mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.chosen_posters[0][1][0].get_rect(
                        topleft=(poster_coord_width, poster_coord_height)).collidepoint(event.pos):
                    webbrowser.open(self.chosen_posters[0][1][1])
                elif self.chosen_posters[1][1][0].get_rect(
                        topleft=(poster_coord_width, poster_coord_height + poster_gap)).collidepoint(event.pos):
                    webbrowser.open(self.chosen_posters[1][1][1])
                elif self.chosen_posters[2][1][0].get_rect(
                        topleft=(poster_coord_width, poster_coord_height + 2 * poster_gap)).collidepoint(event.pos):
                    webbrowser.open(self.chosen_posters[2][1][1])
                elif self.chosen_posters[3][1][0].get_rect(
                        topleft=(poster_coord_width, poster_coord_height + 3 * poster_gap)).collidepoint(event.pos):
                    webbrowser.open(self.chosen_posters[3][1][1])

                elif not self.dropdown.draw_menu:
                    self.textbox_index = None
                    self.ratingbox_index = None

                # checking if the user clicks on the 'GO' button
                if self.submit_rect.collidepoint(event.pos):
                    part_a = [self.user_texts[r] in self.movies for r in range(len(self.user_texts))]
                    part_b = [is_valid_rating(self.rating_texts[n]) for n in range(len(self.user_texts))]
                    if any(part_a[g] and part_b[g] for g in range(len(self.user_texts))):
                        self.submit_permitted = True
                    else:
                        self.submit_permitted = False

                # checking if the user clicks on any of the movie title text boxes
                for j in range(len(self.user_text_rects)):
                    if self.user_text_rects[j].collidepoint(event.pos):
                        self.textbox_index = j
                        self.ratingbox_index = None
                        self.active = True

                # checking if the user clicks on any of the movie rating text boxes
                for j in range(len(self.rating_rects)):
                    if self.rating_rects[j].collidepoint(event.pos):
                        self.ratingbox_index = j
                        self.textbox_index = None
                        self.active = True

            # helper method to check for KEYDOWN events
            self._event_action(event)

    def _help_draw(self) -> None:
        """
        Helper method for MenuScene.draw.
        """

        # Program variables
        poster_coord_width = SCREEN_WIDTH * 0.8
        poster_coord_height = SCREEN_HEIGHT * 0.13
        poster_gap = SCREEN_HEIGHT * 0.215
        base_font = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.017))
        invalid_movie_surface = base_font.render('Movie not found. Please enter a different movie.', True, RED)
        invalid_rate_surface = base_font.render('Invalid rating.', True, RED)
        invalid_rate_surface_2 = base_font.render('Ratings must be from 0.0 to 5.0 inclusive.', True, RED)

        # displaying movie poster images
        for j in range(len(self.chosen_posters)):
            rect = self.chosen_posters[j][1][0].get_rect(topleft=(poster_coord_width,
                                                                  poster_coord_height + (poster_gap * j)))
            self.screen.blit(self.chosen_posters[j][1][0], rect)

        # displaying user's movie title input and adjusting text box size
        for j in range(len(self.user_texts)):
            text_surface = base_font.render(self.user_texts[j], True, (255, 255, 255))
            if self.rating_rects[j].x - (self.user_text_rects[j].x + text_surface.get_width()) <= 50:
                self.user_texts[j] = self.user_texts[j][:-1]
                text_surface = base_font.render(self.user_texts[j], True, (255, 255, 255))
            self.screen.blit(text_surface, (self.user_text_rects[j].x + 5, self.user_text_rects[j].y + 5))
            self.user_text_rects[j].w = max(text_surface.get_width() + 10, 150)

        # displaying warning text if user enters invalid movie title input
        for j in range(len(self.user_texts)):
            if self.user_texts[j] not in self.movies and self.user_texts[j] != '' and self.textbox_index != j:
                self.screen.blit(invalid_movie_surface,
                                 (1 / 30 * self.screen.get_width(),
                                  0.33 * self.screen.get_height() + j * SCREEN_HEIGHT * 0.125))

        # displaying user's movie rating input
        for j in range(len(self.rating_texts)):
            text_surface = base_font.render(self.rating_texts[j], True, (255, 255, 255))
            self.screen.blit(text_surface, (self.rating_rects[j].x + SCREEN_WIDTH * 0.01,
                                            self.rating_rects[j].y + SCREEN_HEIGHT * 0.01))

        # displaying warning text if user enters an invalid movie rating
        for j in range(len(self.rating_texts)):
            if not is_valid_rating(self.rating_texts[j]) and self.ratingbox_index != j and self.rating_texts[j] != '':
                self.screen.blit(invalid_rate_surface, invalid_rate_surface.get_rect(
                    center=(self.rating_rects[j].centerx,
                            self.rating_rects[j].centery + 0.045 * self.screen_h)))
                self.screen.blit(invalid_rate_surface_2, invalid_rate_surface.get_rect(
                    center=(self.rating_rects[j].centerx,
                            self.rating_rects[j].centery + 0.08 * self.screen_h)))

    def draw(self) -> Optional[bool]:
        """
        Draw the scene's contents on the given screen using Pygame.
        """

        # filling the current MenuScene's Pygame screen with a black background
        self.screen.fill((0, 0, 0))

        # initializing fonts and rectagles
        base_font = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.017))

        title_outline_rect = pygame.Rect(0, 0, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.077)
        movies_outline_rect = pygame.Rect(SCREEN_WIDTH * 0.7, 0, SCREEN_WIDTH * 0.3, SCREEN_HEIGHT * 0.077)

        # displaying error message if user tries to receive recommendations with invalid input
        if not self.submit_permitted and self.submit_permitted is not None:
            invalid_submit_surface = base_font.render(
                'Invalid input. Please fill out at least one row with a valid movie title and rating to proceed.',
                True, RED)
            self.screen.blit(invalid_submit_surface, invalid_submit_surface.get_rect(center=(
                self.submit_rect.centerx + 0.13 * SCREEN_WIDTH,
                self.submit_rect.centery + 0.05 * self.screen.get_height())))

        # If user entered valid input, collect it in order to find the best movie recommendations
        elif self.submit_permitted:
            for j in range(len(self.user_texts)):
                if self.user_texts[j] in self.movies and is_valid_rating(self.rating_texts[j]):
                    self.user_submissions[self.user_texts[j]] = float(self.rating_texts[j])
            return True

        # drawing text box and rating box rectangles
        for i in range(len(self.user_text_rects)):
            if i == self.textbox_index:
                pygame.draw.rect(self.screen, BLUE, self.user_text_rects[i], 2)
                pygame.draw.rect(self.screen, GOLDEN, self.rating_rects[i], 2)
            elif i == self.ratingbox_index:
                pygame.draw.rect(self.screen, BLUE, self.rating_rects[i], 2)
                pygame.draw.rect(self.screen, GOLDEN, self.user_text_rects[i], 2)
            else:
                pygame.draw.rect(self.screen, GOLDEN, self.user_text_rects[i], 2)
                pygame.draw.rect(self.screen, GOLDEN, self.rating_rects[i], 2)

        # drawing title outline rectangles
        pygame.draw.rect(self.screen, BLUE, title_outline_rect, 3)
        pygame.draw.rect(self.screen, GOLDEN, movies_outline_rect, 3)
        pygame.draw.rect(self.screen, BLUE, self.submit_rect)

        # rendering title/header texts using various fonts
        title_surface = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.025)).render('FlickFindr', True, GOLDEN)
        sidebar_title_surface = pygame.font.SysFont('trebuchetms',
                                                    int(SCREEN_WIDTH * 0.02)).render('Today\'s Hit Flicks:', True, BLUE)
        instructions_surface1 = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.017)).render(
            'Submit up to 5 movie ratings and press \'GO\'', True,
            GOLDEN)
        instructions_surface2 = pygame.font.SysFont('trebuchetms',
                                                    int(SCREEN_WIDTH * 0.017))\
            .render('to receive movie recommendations!', True, GOLDEN)
        moviebox_label = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.017)).render('Movie Title', True, BLUE)
        ratingbox_label = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.017)).render('Rating (0.0 to 5.0)',
                                                                                               True, BLUE)
        submit_label = pygame.font.SysFont('trebuchetms', int(SCREEN_WIDTH * 0.017)).render('GO!', True, WHITE)

        # displaying text on the pygame window
        self.screen.blit(title_surface,
                         (title_outline_rect.x + (1 / 30 * self.screen.get_width()), title_outline_rect.y + 5))
        self.screen.blit(sidebar_title_surface, sidebar_title_surface.get_rect(center=movies_outline_rect.center))
        self.screen.blit(instructions_surface1, (title_outline_rect.x + (1 / 30 * self.screen.get_width()),
                                                 SCREEN_HEIGHT * 0.1))
        self.screen.blit(instructions_surface2, (title_outline_rect.x + (1 / 30 * self.screen.get_width()),
                                                 SCREEN_HEIGHT * 0.15))
        self.screen.blit(moviebox_label, (self.user_text_rects[0].x, self.user_text_rects[0].y - SCREEN_HEIGHT * 0.08))
        self.screen.blit(ratingbox_label, ratingbox_label.get_rect(topleft=(
            self.rating_rects[0].x, self.rating_rects[0].y - SCREEN_HEIGHT * 0.08)))
        self.screen.blit(submit_label, submit_label.get_rect(center=(self.submit_rect.centerx,
                                                                     self.submit_rect.centery)))

        # calling a helper method to display remaining UI components on Pygame screen
        self._help_draw()

        # drawing the most updated version of the Drop-Down menu
        self.dropdown.draw(self.screen)

        return None


def is_valid_rating(rating: str) -> bool:
    """
    Return whether rating represents a valid movie rating from 0.0 to 5.0 inclusive.

    Preconditions:
    - 0 <= len(rating) <= 3
    """
    if len(rating) == 0:
        return False
    if len(rating) == 1:
        if rating == '.' or (rating.isnumeric() and float(rating) > 5.0):
            return False
    elif len(rating) == 2:
        if rating.count('.') <= 1 and float(rating) > 5.0:
            return False
        elif rating == '..':
            return False
    else:
        if rating[:2].isnumeric() and float(rating[:2]) > 5.0:
            return False
        if rating.count('.') <= 1 and float(rating) > 5.0:
            return False
        elif rating.count('.') >= 2:
            return False

    return True


if __name__ == '__main__':
    python_ta.check_all(config={
        'extra-imports': ["annotations", "Optional", "result_scene", "webbrowser", "pygame", "sys", "random",
                          "data_parsing", "graph_traversal", "tkinter"],
        'allowed-io': [],
        'disable': ["too-many-instance-attributes", "too-many-branches", "too-many-nested-blocks"],
        'generated-members': ['pygame.*'],
        'max-line-length': 120
    })

    user_scene = MenuScene(REVIEW_NETWORK.get_movie_titles())
    while True:
        if isinstance(user_scene, MenuScene):
            user_scene.handle_event()
            if user_scene.draw():
                top_movies = graph_traversal.run_search_on_all(user_scene.user_submissions)
                top_movie_titles = [x[0].title for x in top_movies]
                user_scene = ResultScene(top_movie_titles)

        elif isinstance(user_scene, ResultScene):
            user_scene.draw()
            user_scene.handle_event()

        pygame.display.flip()
        CLOCK.tick(60)
