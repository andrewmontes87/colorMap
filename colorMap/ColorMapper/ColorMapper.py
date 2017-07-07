#!/usr/bin/python

from colour import Color
import xml.etree.ElementTree as ET
import csv
# import sys
import re


class ColorMapper:
    '''
    ColorMapper class
    '''

    def __init__(self, args):

        # lists
        with open('assets/States.csv', 'rU') as f:
            self.states = dict((row[0], row[1]) for row in csv.reader(f))

        with open('assets/Provinces.csv', 'rU') as f:
            self.provinces = dict((row[0], row[1]) for row in csv.reader(f))

        with open('assets/Colors.csv', 'rU') as f:
            self.namedColors = [row for row in csv.reader(f)]

        # paths
        self.inputCSV = args.inputCSV
        self.outputSVG = 'output/' + args.outputSVG
        # options
        self.INCREMENT = args.increment
        self.TRUNCATE = args.truncate
        self.COLORS = args.colors
        # start the circus
        self.startJobs()

    def getColors(self, numberNeeded, userColors):
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
            colors1 = list( firstColor.range_to(middleColor, int(numberNeeded / 2)))
            colors2 = list(middleColor.range_to(lastColor,   int(numberNeeded / 2)))
        else:
            colors1 = list(firstColor.range_to(lastColor, int(numberNeeded)))
            colors2 = []

        allColors = []
        for color in colors1:
            allColors.append(color.hex)
        for color in colors2[1:]:
            allColors.append(color.hex)
        return allColors

    def matchValuesToColors(self, values, colors):
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

    def getStateValuesDict(self, inputCSV):
        # create a dictionary of {State: Value}
        stateValueDict = {}

        # all {Name: Abbreviation} pairs for US and Canada in one dict
        self.statesByName = {v: k for k, v in self.states.iteritems()}
        self.provincesByName = {v: k for k, v in self.provinces.iteritems()}
        mergedStateProvinceNames = dict(self.statesByName, **self.provincesByName)

        with open(inputCSV, 'rU') as myCSV:
            reader = csv.reader(myCSV)
            inputs = [(row[0], row[1])for row in reader if len(row)>1 ]
            for items in inputs:
                key, value = items
                value = re.sub(' ', '', value)
                value = re.sub('[^0-9a-zA-Z.,]', '', value)
                if key in self.states.keys() or key in self.provinces.keys():
                    stateValueDict[key] = float(value)
                elif key in self.states.values() or key in self.provinces.values():
                    stateValueDict[mergedStateProvinceNames[key]] = float(value)

        # with open(inputCSV) as myCSV:
        #     for line in myCSV:
        #         # clear whitespace
        #         line = re.sub(' ', '', line)
        #         # clear special characters
        #         line = re.sub('[^0-9a-zA-Z.,]', '', line)
        #         # split on the comma
        #         line = line.split(',')
        #         # only proceed if it's a state or province name or abbreviation
        #         if line[0] in self.statesByName.keys() or line[0] in self.statesByName.values():
        #             if len(line[0]) > 2:
        #                 stateValueDict[self.statesByName[line[0]]] = float(line[1])
        #             else:
        #                 stateValueDict[line[0]] = float(line[1])
        myCSV.close()

        return stateValueDict

    def colorStates(self, colorDict, stateValueDict, outFile, needUSMap, needCanMap):
        """
        takes the {Value: Color} and {State: Value} dicts
        and colors in the map
        """
        # check to see if it's US, Canada, or both
        # loop through the states in the map and assign corresponding values from the dictionaries

        # US map
        if (needUSMap == True)  and (needCanMap == False):
            tree = ET.parse('assets/USMap.svg')
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
            tree = ET.parse('assets/CanadaMap.svg')
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
            tree = ET.parse('assets/USCanadaMap.svg')
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

    def getInputColors(self, colors):
        if colors:
            for item in colors:
                if re.search("^\#[0-9a-f].....$", item):
                    colors.append(item)
                if item.lower() in self.namedColors:
                    colors.append(item)
            if len(colors) > 1:
                return colors[0:3]
            else:
                return False

    def isAmerica(self, potentialStates):
        for place in potentialStates:
            if place in self.states.keys() or place in self.states.values():
                return True
        return False

    def isCanada(self, potentialProvinces):
        for place in potentialProvinces:
            if place in self.provinces.keys() or place in self.provinces.values():
                return True
        return False

    def startJobs(self):
        # get the CSV to open
        stateValueDict = self.getStateValuesDict(self.inputCSV)

        allStates = stateValueDict.keys()
        allValues = stateValueDict.values()

        # determine whether we need a US map, a Canadian map, or both
        needUSMap  = self.isAmerica(allStates)
        needCanMap = self.isCanada(allStates)

        # get the unique values in our CSV
        uniqValues = list(set(allValues))
        uniqValues.sort()

        # figure out how many colors we need
        # if they choose to "increment" 
        # then we'll get as many color values as there are ints between min and max
        # otherwise, we'll only get as many color values as there 
        #    are UNIQUE values in the CSV
        if self.INCREMENT or self.TRUNCATE:
            colorsNeeded = (max(allValues) - min(allValues)) + 1
        else:
            colorsNeeded = len(uniqValues)

        # see if the user has a color palette in mind
        userColors = self.getInputColors(self.COLORS)

        # get the color palette
        ourColors = self.getColors(colorsNeeded, userColors)

        # get the color dictionary
        if self.INCREMENT:
            valueRange = range(int(min(allValues)), int(max(allValues)) + 1)
            colorDict = self.matchValuesToColors(valueRange, ourColors)
        else:
            colorDict = self.matchValuesToColors(uniqValues, ourColors)

        self.colorStates(colorDict, stateValueDict, self.outputSVG, needUSMap, needCanMap)