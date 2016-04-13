from sys import argv
import sys
from pprint import pprint
import math
import matplotlib.pyplot as plt

def _initialization( curCommandInt, time, xPos, yPos, zPos, commandList, timeXYZRecord):
	measurementUnits = ''
	for i in range(1,4):
		curCommandInt = i
		if( (commandList[curCommandInt])[0] == 'X' ):
			xPos = float( (commandList[curCommandInt])[1:] )
		elif( (commandList[curCommandInt])[0] == 'Y' ):
			yPos = float( (commandList[curCommandInt])[1:] )
		else:
			zPos = float( (commandList[curCommandInt])[1:] )
	timeXYZRecord[time] = [ xPos, yPos, zPos ]
	
	curCommandInt += 1
	if( (commandList[curCommandInt]) == 'G20' ):
		measurementUnits = "Inches"
	else:
		measurementUnits = "Millimeters"
	
	for i in range(0,3):
		curCommandInt+=1
	feedRateNumber = float(commandList[curCommandInt][1:]) / 60.0
	curCommandInt += 1
	return ( curCommandInt, xPos, yPos, zPos, feedRateNumber, measurementUnits )

def _movementGCode( curCommandInt, time, xPos, yPos, zPos, feedRate, commandList, timeXYZRecord):
	oldXPos = xPos
	oldYPos = yPos
	oldZPos = zPos
	if( commandList[curCommandInt] == "G01" ):		#Movement G-Code
		curCommandInt+=1
		while( (commandList[curCommandInt])[0] == 'X' or (commandList[curCommandInt])[0] == 'Y' or (commandList[curCommandInt])[0] == 'Z' ): #Calculates the new position
			if( (commandList[curCommandInt])[0] == 'X' ):	#If the movement is in the X axis
				xPos += float((((commandList)[curCommandInt])[1:]))	#Gets the X position
			elif( (commandList[curCommandInt])[0] == 'Y' ):	#If the movement is in the Y axis
				yPos += float((((commandList)[curCommandInt])[1:]))	#Gets the Y position
			else:	#If the movement is in the Z axis
				zPos += float((((commandList)[curCommandInt])[1:]))	#Gets the Z position
			curCommandInt += 1
			
		#Calculates the distance using pythagorean theorem
		disXSquare = float(xPos - oldXPos) * float(xPos - oldXPos)
		disYSquare = float(yPos - oldYPos) * float(yPos - oldYPos)
		disZSquare = float(zPos - oldZPos) * float(zPos - oldZPos)
		totalDistance = float(math.sqrt( disXSquare + disYSquare + disZSquare ))
		#Calculates the time taken to make the movement
		time += (totalDistance / feedRate ) 		#Time of movement = distance/feed rate
	
	elif(  commandList[curCommandInt] == "G4" or commandList[curCommandInt] == "G04" ):
		curCommandInt += 1
		time += float((((commandList)[curCommandInt])[1:]))	#Adds the time from the pause
		curCommandInt += 1
	timeXYZRecord[time] = [ xPos, yPos, zPos]		#Inserting in the recent movement/pause
	
	return ( curCommandInt, time, xPos, yPos, zPos )

def parse(filename, output_file=None, graph=False):
	#Values of the machine data at the most recent instruction
	curCommandInt = 0
	xPos = 0.0
	yPos = 0.0
	zPos = 0.0
	time = 0.0
	timeXYZRecord = {}
	
	feedRate = 0.0
	measurementUnits = ''
	commandList = []
	
	#Stores all the commands and stuff into a list.......very inefficient
	with open(filename,'r') as f:
		for line in f:
			for command in line.split():
				commandList.append( command )
				
	curCommandInt, xPos, yPos, zPos, feedRateNumber, measurementUnits = _initialization( curCommandInt, time, xPos, yPos, zPos, commandList, timeXYZRecord)
	
	while( curCommandInt < len( commandList ) ):
		if( commandList[curCommandInt] == ';' ): #Goes through the file to the next commandin the case of a comment
			while( curCommandInt < len( commandList ) ):
				if( commandList[curCommandInt] == "G01" or commandList[curCommandInt] == "G4" or commandList[curCommandInt] == "G04" ):
					break
				curCommandInt += 1
		if( curCommandInt >= len( commandList ) ):
			break
		curCommandInt, time, xPos, yPos, zPos = _movementGCode( curCommandInt, time, xPos, yPos, zPos, feedRateNumber, commandList, timeXYZRecord)
	
	#pprint( timeXYZRecord )	#Prints out the dictionary
	
	timeList = []
	xValueList = []
	yValueList = []
	
	for key in sorted(timeXYZRecord.iterkeys()):
		timeList.append( key )
		xValueList.append( timeXYZRecord[key][0] )
		yValueList.append( timeXYZRecord[key][1] )

	if graph:
		#Plotting the data
		plt.figure(1)
		plt.subplot(211)
		plt.plot( timeList, xValueList )
		plt.ylabel('Distance from Origin' )
		plt.xlabel('Time' )
		plt.title('X-Waveform')
		plt.subplot(212)
		plt.plot( timeList, yValueList )
		plt.ylabel('Distance from Origin')
		plt.xlabel('Time' )
		plt.title('Y-Waveform')
		plt.show()
	if output_file:
		import json
		positions = []
		for t,x,y in zip(timeList, xValueList, yValueList):
			positions.append({
				"time": t,
				"x": x,
				"y": y
			})
		json.dump({
			'positions': sorted(positions, key=lambda x: x['time'])
		}, open(output_file, 'w'))
	return xValueList,yValueList, timeList

if __name__ == "__main__":
	if len(argv) != 2 and len(argv) != 3 :
		print("USAGE: gcode-parser.py <input gcode> [output_file.json]")
		sys.exit(1)

	#Used for opening the file passed in as an argument
	script, filename = argv[:2]

	output_file = len(argv) == 3 and argv[2] or None

	parse(filename, output_file=output_file, graph=(output_file is None))
