# -*- coding: utf-8 -*-

# Sample showing how to add a custom web map

from maperipy import Map
from maperipy.webmaps import WebMap

Map.clear()

# the first argument is the name of your custom map
# the second is the base URL of the Web map tiles (or multiple URLs if you have them)
Map.add_web_map_custom("local", ["http://192.168.4.54:6789/openstreetmap-carto/tile" ])
