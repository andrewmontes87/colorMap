#!/usr/bin/python

from colour import Color
import csv
import xml.etree.ElementTree as ET
import sys
import re

statesByAbbrev = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}

provincesByAbbrev = {"ON": "Ontario", "QC": "Quebec", "NS": "Nova Scotia", "NB": "New Brunswick", "MB":"Manitoba", "BC":"British Columbia", "PE":"Prince Edward Island", "SK":"Saskatchewan", "AB":"Alberta", "NL":"Newfoundland and Labrador", "NT":"Northwest Territories", "YT":"Yukon", "NU":"Nunavut"}

def getColors(numberNeeded, userColors):
	"""
	takes the number needed and returns a list of hex color values
	"""
	if(numberNeeded % 2 == 0):
		numberNeeded += 2
	else:
		numberNeeded += 1

	if userColors:
		firstColor = Color(userColors[0])
		lastColor = Color(userColors[-1])
		if len(userColors) == 3:
			middleColor = Color(userColors[1])
		else:
			middleColor = False

	else:
		firstColor  = Color("#F4EB37")
		middleColor = Color("#FFA500")
		lastColor   = Color("#8B0000")

	if middleColor:
		colors1 = list( firstColor.range_to(middleColor, (numberNeeded / 2)))
		colors2 = list(middleColor.range_to(lastColor,   (numberNeeded / 2)))
	else:
		colors1 = list(firstColor.range_to(lastColor, numberNeeded))
		colors2 = []

	allColors = []
	for color in colors1:
		allColors.append(color.hex)
	for color in colors2[1:]:
		allColors.append(color.hex)
	return allColors

def matchValuesToColors(values, colors):
	"""
	takes a list of values and a list of colors
	returns a dictionary of color matches {Value: Color}
	"""
	colorMatches = {}
	i = 0
	while i < len(values):
		colorMatches[values[i]] = colors[i]
		i += 1
	return colorMatches

def getStateValuesDict(inputCSV):
	# create a dictionary of {State: Value}
	stateValueDict = {}

	# all {Name: Abbreviation} pairs for US and Canada in one dict
	statesByName = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "Ontario": "ON", "Quebec":"QC", "Nova Scotia": "NS", "New Brunswick":"NB", "Manitoba":"MB", "British Columbia":"BC", "Prince Edward Island":"PE", "Saskatchewan":"SK", "Alberta":"AB", "Newfoundland and Labrador":"NL", "Northwest Territories":"NT", "Yukon":"YT", "Nunavut":"NU"}

	with open(inputCSV) as myCSV:
		for line in myCSV:
			line = re.sub(' ', '', line)
			line = re.sub('[^0-9a-zA-Z.,]', '', line)
			line = line.split(',')
			if len(line[0]) > 2:
				stateValueDict[statesByName[line[0]]] = float(line[1])
			else:
				stateValueDict[line[0]] = float(line[1])
				
	myCSV.close()

	return stateValueDict

def colorStates(colorDict, stateValueDict, outFile, needUSMap, needCanMap):
	"""
	takes the {Value: Color} and {State: Value} dicts
	and colors in the map
	"""
	# check to see if it's US, Canada, or both
	# loop through the states in the map and assign corresponding values from the dictionaries

	# US map
	if (needUSMap == True)  and (needCanMap == False):
		tree = ET.parse('USMap.svg')
		root = tree.getroot()
		for child in root:
			try:
				if child.attrib['id'] == "outlines":
					for state in child:
						try:
							# find the state's value
							stateValue = stateValueDict[state.attrib["id"]]
							# find the corresponding color
							stateColor = colorDict[stateValue]
							# write that color to the shape's space on the map
							state.attrib["fill"] = stateColor
						except KeyError:
							continue
			except KeyError:
				continue

	# Canadian map
	elif (needUSMap == False) and (needCanMap == True):
		tree = ET.parse('CanadaMap.svg')
		root = tree.getroot()
		for child in root:
			if child.attrib['id'] == 'Canada':
				for province in child:
					try:
						provValue = stateValueDict[province.attrib['id']]
						provColor = colorDict[provValue]
						province.attrib["fill"] = provColor
					except KeyError:
						continue

	# US + Canada map
	elif (needUSMap == True) and (needCanMap == True):
		tree = ET.parse('USCanadaMap.svg')
		root = tree.getroot()
		for child in root:
			if child.attrib['id'] == "US-CAN":
				for country in child:
					for state in country:
						try:
							stateValue = stateValueDict[state.attrib['id']]
							stateColor = colorDict[stateValue]
							state.attrib["fill"] = stateColor
						except KeyError:
							continue

	# write the new XML to the output file
	output = ET.tostring(root)
	f = open(outFile, 'w')
	f.write(output)
	f.close()

def getInputFile(argv):
	"""
	if a CSV has been specified, use that
	otherwise, prompt the user to enter a filename
	"""
	inputCSV = False
	for arg in argv:
		if re.search('\.csv$', arg):
			inputCSV = arg
	if not inputCSV:
		inputCSV = raw_input("enter a CSV to open: ")
	return inputCSV

def getOutputFile(argv):
	"""
	if an SVG has been specified, we'll write to that
	otherwise, we'll use a default
	"""
	outputCSV = "newMap.svg"
	for arg in argv:
		if re.search('\.svg$', arg):
			outputCSV = arg
	return outputCSV

def getInputColors(argv):
	colors = []
	namedColors = ['springgreen', 'salmon', 'midnightblue', 'mediumseagreen', 'thistle', 'lightslategray', 'khaki', 'lightgray', 'coral', 'darkgray', 'silver', 'steelblue', 'lavenderblush', 'lightpink', 'white', 'darkolivegreen', 'lightcyan', 'lightblue', 'turquoise', 'lightgreen', 'lightgoldenrod', 'darkmagenta', 'blue', 'darkslategray', 'wheat', 'palegreen', 'ivory', 'cornsilk', 'darkslateblue', 'blueviolet', 'purple', 'powderblue', 'pink', 'darkorange', 'orange', 'papayawhip', 'peru', 'seashell', 'aliceblue', 'lemonchiffon', 'goldenrod', 'skyblue', 'maroon', 'navy', 'violet', 'burlywood', 'crimson', 'beige', 'lightsteelblue', 'tomato', 'chartreuse', 'royalblue', 'gray', 'darkgoldenrod', 'darkorchid', 'deeppink', 'honeydew', 'orangered', 'forestgreen', 'darkturquoise', 'firebrick', 'greenyellow', 'indianred', 'olivedrab', 'darkblue', 'peachpuff', 'lime', 'mintcream', 'cyan', 'limegreen', 'hotpink', 'mediumslateblue', 'moccasin', 'darkkhaki', 'deepskyblue', 'magenta', 'yellowgreen', 'lawngreen', 'slateblue', 'mediumspringgreen', 'snow', 'red', 'orchid', 'indigo', 'mistyrose', 'chocolate', 'navajowhite', 'cornflowerblue', 'lightgoldenrodyellow', 'gainsboro', 'mediumblue', 'mediumorchid', 'linen', 'aquamarine', 'palevioletred', 'mediumvioletred', 'lightyellow', 'violetred', 'darksalmon', 'olive', 'lavender', 'slategray', 'ghostwhite', 'seagreen', 'brown', 'antiquewhite', 'darkcyan', 'darkseagreen', 'lightsalmon', 'mediumaquamarine', 'lightseagreen', 'gold', 'darkred', 'bisque', 'darkgreen', 'azure', 'dimgray', 'black', 'dodgerblue', 'oldlace', 'lightskyblue', 'mediumpurple', 'sandybrown', 'tan', 'yellow', 'floralwhite', 'lightslateblue', 'cadetblue', 'plum', 'blanchedalmond', 'sienna', 'palegoldenrod', 'darkviolet', 'green', 'whitesmoke', 'mediumturquoise', 'saddlebrown', 'lightcoral', 'rosybrown', 'paleturquoise']

	for arg in sys.argv:
		if re.search("^\#[0-9a-f].....$", arg):
			colors.append(arg)
		if arg.lower() in namedColors:
			colors.append(arg)
	if len(colors) > 1:
		return colors[0:3]
	else:
		return False

def isAmerica(potentialStates):
	USstates = ['WA', 'WI', 'WV', 'FL', 'WY', 'NH', 'NJ', 'NM', 'NC', 'ND', 'NE', 'NY', 'RI', 'NV', 'CO', 'CA', 'GA', 'CT', 'OK', 'OH', 'KS', 'SC', 'KY', 'OR', 'SD', 'DE', 'DC', 'HI', 'TX', 'LA', 'TN', 'PA', 'VA', 'AK', 'AL', 'AR', 'VT', 'IL', 'IN', 'IA', 'AZ', 'ID', 'ME', 'MD', 'MA', 'UT', 'MO', 'MN', 'MI', 'MT', 'MS']
	for place in potentialStates:
		if place in USstates:
			return True
	return False

def isCanada(potentialProvinces):
	canadianProvinces = ["ON", "QC", "NS", "NB", "MB", "BC", "PE", "SK", "AB", "NL", "NT", "YT", "NU"]
	for place in potentialProvinces:
		if place in canadianProvinces:
			return True
	return False

# get the CSV to open
inputCSV = getInputFile(sys.argv)

stateValueDict = getStateValuesDict(inputCSV)

print stateValueDict

allStates = stateValueDict.keys()
allValues = stateValueDict.values()

# determine whether we need a US map, a Canadian map, or both
needUSMap  = isAmerica(allStates)
needCanMap = isCanada(allStates)

# get the unique values in our CSV
uniqValues = list(set(allValues))
uniqValues.sort()

# figure out how many colors we need
# if they choose to "increment" 
# then we'll get as many color values as there are ints between min and max
# otherwise, we'll only get as many color values as there 
#    are UNIQUE values in the CSV
if "-increment" in sys.argv or "-truncate" in sys.argv:
	colorsNeeded = (max(allValues) - min(allValues)) + 1
else:
	colorsNeeded = len(uniqValues)

# see if the user has a color palette in mind
userColors = getInputColors(sys.argv)

# get the color palette
ourColors = getColors(colorsNeeded, userColors)

# get the color dictionary
if "-increment" in sys.argv:
	valueRange = range(min(allValues), max(allValues) + 1)
	colorDict = matchValuesToColors(valueRange, ourColors)
else:
	colorDict = matchValuesToColors(uniqValues, ourColors)

outputCSV = getOutputFile(sys.argv)

colorStates(colorDict, stateValueDict, outputCSV, needUSMap, needCanMap)