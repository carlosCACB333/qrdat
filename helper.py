import os
import sys


def get_path(path):
    try:
        route_main = sys.__MEIPASS
    except:
        route_main = os.path.abspath(".")
    return os.path.join(route_main, path)
