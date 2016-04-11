from sys import argv
from pprint import pprint
import math
import matplotlib.pyplot as plt

def initialization( curCommandInt, time, xPos, yPos, zPos ):
	#Finds the initial xyz coordinates
	curCommandInt = 1
	for i in range(1,3):
		curCommandInt += 1 
		if( (commandList[curCommandInt])[0] == 'X' ):
			xPos = float( (commandList[curCommandInt])[1:] )
		elif( (commandList[curCommandInt])[0] == 'Y' ):
			yPos = float( (commandList[curCommandInt])[1:] )
		else:
			zPos = float( (commandList[curCommandInt])[1:] )
	
	#Stores the initial xyz coordinates into a list
	XYZ.append( xPos )
	XYZ.append( yPos )
	XYZ.append( zPos )
	#Stores the xyz coordinates into a dictionary that has a key of the time
	timeXYZRecord[time] = XYZ
	#Returns the feed rate and the measurement units
	curCommandInt += 1
	if( (commandList[curCommandInt]) == 'G20' ):
		measurementUnits = "Inches"
	else:
		measurementUnits = "Millimeters"
	for i in range(1,4):
		curCommandInt+=1
	feedRateNumber = float((((commandList)[curCommandInt])[1:]))
	curCommandInt+=1
	return (feedRateNumber, measurementUnits, curCommandInt, xPos, yPos, zPos )

def movementGCode( curCommandInt, time, xPos, yPos, zPos, feedRate ):
	oldXPos = xPos
	oldYPos = yPos
	oldZPos = zPos
	if( commandList[curCommandInt] == "G01" ):		#Movement G-Code
		timeXYZRecord[time] = [ oldXPos, oldYPos, oldZPos ]
		curCommandInt+=1
		while( (commandList[curCommandInt])[0] == 'X' or (commandList[curCommandInt])[0] == 'Y' or (commandList[curCommandInt])[0] == 'Z' ): #Calculates the new position
			if( (commandList[curCommandInt])[0] == 'X' ):	#If the movement is in the X axis
				xPos += float((((commandList)[curCommandInt])[1:]))	#Gets the X position
				XYZ[0] = xPos;
			elif( (commandList[curCommandInt])[0] == 'Y' ):	#If the movement is in the Y axis
				yPos += float((((commandList)[curCommandInt])[1:]))	#Gets the Y position
				XYZ[1] = xPos;
			else:	#If the movement is in the Z axis
				zPos += float((((commandList)[curCommandInt])[1:]))	#Gets the Z position
				XYZ[2] = xPos;
			curCommandInt += 1
		#Calculates the distance using pythagorean theorem
		disXSquare = float(xPos - oldXPos) * float(xPos - oldXPos)
		disYSquare = float(yPos - oldYPos) * float(yPos - oldYPos)
		disZSquare = float(zPos - oldZPos) * float(zPos - oldZPos)
		totalDistance = float(math.sqrt( disXSquare + disYSquare + disZSquare ))
		#Calculates the time taken to make the movement
		time += totalDistance / feedRate		#Time of movement = distance/feed rate
		timeXYZRecord[time] = XYZ		#Inserting in the recent movement
		
		#Pause G-Code
	elif(  commandList[curCommandInt] == "G4" or commandList[curCommandInt] == "G04" ):
		curCommandInt+=1
		time += float((((commandList)[curCommandInt])[1:]))	#Adds the time from the pause
		timeXYZRecord[time] = [ oldXPos, oldYPos, oldZPos ]		#Inserting the position after the pause
		curCommandInt += 1
	return ( curCommandInt, xPos, yPos, zPos, time )

#Values of the machine data at the most recent instruction
curCommandInt = 0
xPos = 0.0
yPos = 0.0
zPos = 0.0
time = 0.0

#Various data structures to hold the xyz values and the commands
commandList = list() #Used for holding all of the commands in the file
XYZ = list() #Used for holding the "current" coordinates of the machine
timeXYZRecord = dict() #Used for holding the xyz values at time t

#Values for the feed rate
feedRate = 0.0
measurementUnits = ''

#Used for opening the file passed in as an argument
script, filename = argv 

#Stores all the commands and stuff into a list.......very inefficient
with open(filename,'r') as f:
	for line in f:
		for command in line.split():
			commandList.append( command )

#Initializing the values
feedRate, measurementUnits, curCommandInt, xPos, yPos, zPos = initialization( curCommandInt, time, xPos, yPos, zPos )
while( curCommandInt < len( commandList ) ):
	if( commandList[curCommandInt] == ';' ): #Goes through the file to the next commandin the case of a comment
		while( curCommandInt < len( commandList ) ):
			if( commandList[curCommandInt] == "G01" or commandList[curCommandInt] == "G4" or commandList[curCommandInt] == "G04" ):
				break
			curCommandInt += 1
	if( curCommandInt >= len( commandList ) ):
		break
	curCommandInt, xPos, yPos, zPos, time = movementGCode( curCommandInt, time, xPos, yPos, zPos, feedRate )


pprint( timeXYZRecord )

#Used for plotting the data
xValueList = list()
yValueList = list()
timeList = list()

for key in sorted(timeXYZRecord.iterkeys()):
	timeList.append( key )
	xValueList.append( timeXYZRecord[key][0] )
	yValueList.append( timeXYZRecord[key][1] )

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
