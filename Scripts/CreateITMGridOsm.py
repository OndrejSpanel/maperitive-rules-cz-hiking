# this code is based on the code at http://www.technion.ac.il/~zvikabh/software/ITM/isr84lib.cpp
# it creates OSM file with horizontal and vertical "ways" (lines) according to ITM.
# you have the permission to do what ever you want with this code...
#
# 2013/03/08 Harel Mazor

from maperipy import *
from maperipy.osm import *
import math


#=================================================
# Defines
#=================================================
# Grid creation boundries - in meters
iGridStartN = 350000
iGridEndN = 810000
iGridStartE = 100000
iGridEndE = 300000
iGridStep = 1000

sFileName = 'IsraelHiking\ITMGrid.osm'

# WGS84 Data
WGS84_a = 6378137.0					# Equatorial earth radius
WGS84_b = 6356752.3142				# Polar earth radius
WGS84_f = 0.00335281066474748	  	# (a-b)/a Flatenning = 1/298.257223563
WGS84_esq = 0.006694380004260807	# esq = 1-(b*b)/(a*a) Eccentricity Squared
WGS84_e = 0.0818191909289062 		# sqrt(esq) Eccentricity
# GRS80 Data
GRS80_a = 6378137.0					# Equatorial earth radius
GRS80_b = 6356752.3141				# Polar earth radius
GRS80_f = 0.0033528106811823		# (a-b)/a Flatenning = 1/298.257222101
GRS80_esq = 0.00669438002290272		# esq = 1-(b*b)/(a*a) Eccentricity Squared
GRS80_e = 0.0818191910428276		# sqrt(esq) Eccentricity
# deltas to WGS84
GRS80_dX = -48
GRS80_dY = 55
GRS80_dZ = 52

#ITM Grid data
Grid_lon0 = 0.61443473225468920			# lon0 = central meridian in radians 35.12'16.261"
Grid_lat0 = 0.55386965463774187			# lat0 = central latitude in radians 31.44'03.817"
Grid_k0 = 1.0000067						# k0 = scale factor
Grid_false_easting = 219529.584			 
Grid_false_northing = 2885516.9488		# = 3512424.3388-626907.390
										# MAPI says the false northing is 626907.390, and in another place
										# that the meridional arc at the central latitude is 3512424.3388

#=================================================
# Defines End
#=================================================										


#=================================================
# Israel New Grid (ITM) to WGS84 conversion
#=================================================
def ITM2WGS84(N, E) :
	# 1. Local Grid (ITM) -> GRS80
	(lat80,lon80) = ITMGrid2GRS80LatLon(N,E)

	# 2. Molodensky GRS80->WGS84
	(lat84,lon84) = MolodenskyGRS80ToWGS84(lat80,lon80)

	# final results converted to degrees
	lat = lat84*180/math.pi
	lon = lon84*180/math.pi
	return (lat, lon)
	
#=====================================
# ITM Grid to Lat/Lon GRS80 conversion
#=====================================
def ITMGrid2GRS80LatLon(N, E) :
	#================
	# GRID -> Lat/Lon
	#================

	y = N + Grid_false_northing
	x = E - Grid_false_easting
	M = y / Grid_k0

	a = GRS80_a
	b = GRS80_b
	e = GRS80_e
	esq = GRS80_esq

	mu = M / (a*(1 - e*e/4 - 3*(e**4)/64 - 5*(e**6)/256))
	
	ee = math.sqrt(1-esq)
	e1 = (1-ee)/(1+ee)
	j1 = 3*e1/2 - 27*e1**3/32
	j2 = 21*e1**2/16 - 55*e1**4/32
	j3 = 151*e1**3/96
	j4 = 1097*e1**4/512

	# Footprint Latitude
	fp =  mu + j1*math.sin(2*mu) + j2*math.sin(4*mu) + j3*math.sin(6*mu) + j4*math.sin(8*mu)

	eg = (e*a/b)
	C1 = (eg*math.cos(fp))**2
	T1 = math.tan(fp)**2
	R1 = a*(1-e**2) / (1-(e*math.sin(fp))*(e*math.sin(fp))**1.5)
	N1 = a / math.sqrt(1-((e*math.sin(fp))**2))
	D = x / (N1*Grid_k0)

	Q1 = N1*math.tan(fp)/R1
	Q2 = D*D/2
	Q3 = (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*eg**4)*(D**4)/24
	Q4 = (61 + 90*T1 + 298*C1 + 45*T1**2 - 3*C1**2 - 252*eg**4)*(D**6)/720
	# result lat
	lat = fp - Q1*(Q2-Q3+Q4)

	Q5 = D
	Q6 = (1 + 2*T1 + C1)*(D**3)/6
	Q7 = (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*eg**4 + 24*T1**2)*(D**5)/120
	# result lon
	lon = Grid_lon0 + (Q5 - Q6 + Q7)/math.cos(fp)
	
	return (lat,lon)

#===========================================================================
# Abridged Molodensky transformation between GRS80 and WGS84 coordinates set
#===========================================================================
def MolodenskyGRS80ToWGS84(ilat, ilon) :
	slat = math.sin(ilat)
	clat = math.cos(ilat)
	slon = math.sin(ilon)
	clon = math.cos(ilon)

	df = WGS84_f - GRS80_f
	da = WGS84_a - GRS80_a
	adb = 1.0 / (1.0 - GRS80_f)
	rn = GRS80_a / math.sqrt(1 - GRS80_esq * slat**2)
	rm = GRS80_a * (1 - GRS80_esq) / ((1 - GRS80_esq * slat**2)**1.5)

	dlat = (-GRS80_dX*slat*clon - GRS80_dY*slat*slon + GRS80_dZ*clat + da*rn*GRS80_esq*slat*clat/GRS80_a + df*(rm*adb + rn/adb)*slat*clat) / (rm);

	# result lat (radians)
	olat = ilat+dlat;

	dlon = (-GRS80_dX*slon + GRS80_dY*clon) / ((rn)*clat);
	# result lon (radians)
	olon = ilon+dlon;
	
	return (olat, olon)


#======================================================
# Main script - creates osm file with ITM grid data
# this part will create a matrix of nodes according to
# 	the given step, start and end point in ITM coordinates.
#	once this matrix of nodes is written to the file we will add
# 	ways between every line in this matrix
#======================================================	

osmFile = open(sFileName, 'w')
iId = 0
# writing osm header
osmFile.write('<?xml version="1.0" encoding="utf-8"?>' + "\n")
osmFile.write('<osm version="0.5" generator="CreateITMGridOsm.py">' + "\n")

# Adding all the junction nodes
for iN in range(iGridStartN, iGridEndN, iGridStep) :
	for iE in range(iGridStartE, iGridEndE, iGridStep) :
		(dbLat,dbLon) = ITM2WGS84(iN, iE)
		osmFile.write('  <node id="' + str(iId) + '" visible="true" lat="' + str(dbLat) + '" lon="' + str(dbLon) + '" />' + "\n")
		iId = iId + 1

iMaxNodesId = iId
		
# Adding horizontal lines
for iN in range(iGridStartN, iGridEndN, iGridStep) :
	osmFile.write('  <way id="' + str(iId) + '" visible="true">' + "\n")
	iId = iId + 1
	for iE in range(iGridStartE, iGridEndE, iGridStep) :
		iNodeId = ((iE - iGridStartE) + (iN - iGridStartN) * (iGridEndE - iGridStartE)/ iGridStep) / iGridStep
		osmFile.write('    <nd ref="' + str(iNodeId) + '" />' + "\n")
	if ((iN / 1000) % 10 == 0) :
		osmFile.write('    <tag k="itm_main" v="10"/>' + "\n")
	elif ((iN / 1000)% 5 == 0) :
		osmFile.write('    <tag k="itm_main" v="5"/>' + "\n")
	else :
		osmFile.write('    <tag k="itm_main" v="1"/>' + "\n")
	osmFile.write('    <tag k="itm_coord" v="' +  str(iN / 1000) + '"/>' + "\n")
	osmFile.write('  </way>' + "\n")
	
# Adding vertical lines
for iE in range(iGridStartE, iGridEndE, iGridStep) :
	osmFile.write('  <way id="' + str(iId) + '" visible="true">' + "\n")
	iId = iId + 1
	for iN in range(iGridStartN, iGridEndN, iGridStep) :
		iNodeId = ((iE - iGridStartE) + (iN - iGridStartN) * (iGridEndE - iGridStartE)/ iGridStep) / iGridStep
		osmFile.write('    <nd ref="' + str(iNodeId) + '" />' + "\n")
	if ((iE / 1000) % 10 == 0) :
		osmFile.write('    <tag k="itm_main" v="10"/>' + "\n")
	elif ((iE / 1000)% 5 == 0) :
		osmFile.write('    <tag k="itm_main" v="5"/>' + "\n")
	else :
		osmFile.write('    <tag k="itm_main" v="1"/>' + "\n")
	osmFile.write('    <tag k="itm_coord" v="' +  str(iE / 1000) + '"/>' + "\n")
	osmFile.write('  </way>' + "\n")

# Adding n x n ways to render text on them
iLabelStep = 5
for iE in range(iGridStartE, iGridEndE, iGridStep * iLabelStep) :
	for iN in range(iGridStartN, iGridEndN, iGridStep * iLabelStep) :
		osmFile.write('  <way id="' + str(iId) + '" visible="true">' + "\n")
		iId = iId + 1
		for iNodeIndex in range(0,iLabelStep + 1,1) :
			iNodeId = ((iE - iGridStartE) + (iN + iNodeIndex * iGridStep - iGridStartN) * (iGridEndE - iGridStartE)/ iGridStep) / iGridStep
			osmFile.write('    <nd ref="' + str(iNodeId) + '" />' + "\n")
		osmFile.write('    <tag k="itm_coord_label" v="' + str(iE / 1000) + '"/>' + "\n")
		osmFile.write('  </way>' + "\n")
		
		osmFile.write('  <way id="' + str(iId) + '" visible="true">' + "\n")
		iId = iId + 1
		for iNodeIndex in range(0,iLabelStep + 1,1) :
			iNodeId = ((iE + iNodeIndex * iGridStep - iGridStartE) + (iN - iGridStartN) * (iGridEndE - iGridStartE)/ iGridStep) / iGridStep
			osmFile.write('    <nd ref="' + str(iNodeId) + '" />' + "\n")
		osmFile.write('    <tag k="itm_coord_label" v="' + str(iN / 1000) + '"/>' + "\n")
		osmFile.write('  </way>' + "\n")
	
	
# writing osm fotter
osmFile.write('</osm>')
osmFile.close()

# done! load this file as a part of the setup script