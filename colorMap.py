from colour import Color
import csv
import xml.etree.ElementTree as ET
import sys
import re

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

	# myYellow = Color("#F4EB37")
	# myOrange = Color("#FFA500")
	# myRed    = Color("#8B0000")
	# colors1 = list(myYellow.range_to(myOrange, (numberNeeded / 2)))
	# colors2 = list(myOrange.range_to(myRed, (numberNeeded / 2)))

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

def stateValuesDict(inputCSV):
	# create a dictionary of {State: Value}
	stateValueDict = {}

	# ourCSV = raw_input("Enter the file to open: ")

	myFile = open(inputCSV, 'rb')
	rows = csv.reader(myFile, delimiter=',')
	for row in rows:
		stateValueDict[row[0]] = int(row[1])

	myFile.close()

	return stateValueDict

def getAllValues(inputCSV):
	# this will hold the set of all of our limits
	allValues = []

	# open the CSV and read out all of the speed limits
	myFile = open(inputCSV, 'rb')
	rows = csv.reader(myFile, delimiter=',')
	for row in rows:
		allValues.append(int(row[1]))

	myFile.close()

	return allValues

def getAllStates(inputCSV):
	allStates = []
	myFile = open(inputCSV, 'rb')
	rows = csv.reader(myFile, delimiter=',')
	for row in rows:
		allStates.append(row[0])
	myFile.close()
	return allStates

def colorStates(colorDict, stateValueDict, outFile):
	"""
	takes the {Value: Color} and {State: Value} dicts
	and colors in the map
	"""
	# open and parse the map XML
	tree = ET.parse('USMap.svg')
	root = tree.getroot()

	# iterate through the states
	for child in root:
		if child.tag == "{http://www.w3.org/2000/svg}g":
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
	for arg in sys.argv:
		if re.search("^\#[0-9a-f].....$", arg):
			colors.append(arg)
	if len(colors) > 1:
		return colors[0:3]
	else:
		return False

# get the CSV to open
inputCSV = getInputFile(sys.argv)

# get a list of all states
allStates = getAllStates(inputCSV)

# get a list of all values associated with the states
allValues = getAllValues(inputCSV)

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

# get the {State: Speed} dictionary
stateValueDict = stateValuesDict(inputCSV)

outputCSV = getOutputFile(sys.argv)

colorStates(colorDict, stateValueDict, outputCSV)

