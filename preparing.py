from settings import COUNT_OF_PLAY_FUNCTIONS
from os import mkdir

games_dictionary = dict()

try:
    mkdir("static/game_links")
except FileExistsError:
    pass

for n in range(1, COUNT_OF_PLAY_FUNCTIONS + 1):
    try:
        games_dictionary[n] = mkdir(f"static/game_links/{n}")
    except FileExistsError:
        games_dictionary[n] = None
