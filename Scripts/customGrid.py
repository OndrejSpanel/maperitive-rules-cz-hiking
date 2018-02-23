# Places a simple rectangular grid based on the current map view (or geometry bounds).

# Author: Igor Brejc
# License: public domain

from maperipy import *

import math

# A helper Python method for ranging with float values
def xfrange(start, stop, step):
    while start < stop:
        yield start
        start += step
  	
# Create a custom map layer...
layer = Map.add_custom_layer()

# Symbol for the grid
symbol = LineSymbol("grid", Srid.Wgs84LonLat)
# Add the symbol to our new layer
layer.add_symbol(symbol)

# Set some styling
symbol.style.pen_width = 2
symbol.style.pen_color = Color("red")
symbol.style.pen_opacity = 0.5

# We are using geometry bounds, but you could set something different yourself.
grid_box = Map.geo_bounds

avg_x = (grid_box.max_x + grid_box.min_x) * 0.5
avg_y = (grid_box.max_y + grid_box.min_y) * 0.5

# Meridian length is always the same - 
meridian = 20003930.0
equator = 40075160
parallel = math.cos(math.radians(avg_y)) * equator

grid_distance = 1000.0

print avg_x, avg_y

grid_step_x = grid_distance / parallel * 360
grid_step_y = grid_distance / meridian * 180

print grid_step_x, grid_step_y

if (grid_box.delta_x < grid_step_x * 100) & (grid_box.delta_y < grid_step_y * 100):
	# The grid step (in our case it's one second of a degree)


	# Draw horizontal lines
	for y in xfrange (grid_box.min_y, grid_box.max_y, grid_step_y):
		linestring = LineString([Point(grid_box.min_x, y), Point(grid_box.max_x, y)])
		symbol.add(linestring)

	# Draw vertical lines
	for x in xfrange (grid_box.min_x, grid_box.max_x, grid_step_x):
		linestring = LineString([Point(x, grid_box.min_y), Point(x, grid_box.max_y)])
		symbol.add(linestring)