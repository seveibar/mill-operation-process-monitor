#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cstdlib>
#include <cmath>
#include <map>
#include <vector>
#include <string>
#include <utility>
#include "gnuplot-iostream.h"


//Function Prototypes
void initialization( std::ifstream& in_str, std::string& curCommand, double& xPos, double& yPos, double& zPos,
										std::vector<double>& XYZ, std::map< double, std::vector<double> >& timeXYZRecord, 
										double& feedRate, std::string& measurementUnits, double& time );

void movementGCode( std::ifstream& in_str, std::string& curCommand, double& xPos, double& yPos, double& zPos, 
										std::vector<double>& XYZ, std::map< double, std::vector<double> >& timeXYZRecord, 
										double const& feedRate, double& time );

void output( std::map< double, std::vector<double> >const& timeXYZRecord, double const& feedRate, std::string const& measurementUnits );


//This code assumes that this follows the provided sample code format
int main(int argc, char* argv[]){
	std::string curCommand;					//Used for parsing the G-Code
	double xPos;							//Current X-Position
	double yPos;							//Current Y-Position
	double zPos;							//Current Z-Position
	double time;							//Current time
	std::vector<double> XYZ;				//Vector for inserting into XYZ time record
	std::map< double, std::vector<double> > timeXYZRecord;	//Stores the position as time goes on
	double feedRate;						//The feed rate for the CNC
	std::string measurementUnits;			//Measurements for the commands
	
	//Checks if the input file actually opened
	std::ifstream in_str(argv[1]);
	if (!in_str.good()) {
		std::cerr << "Can't open " << argv[1] << " to read.\n";
		exit(1);
	}
	
	//Initializes the values to the specified quantity in the input file
	initialization( in_str, curCommand, xPos, yPos, zPos, XYZ, timeXYZRecord, feedRate, measurementUnits, time );
	
	while(in_str >> curCommand){
		if( curCommand == ";" ){	//Goes through the file to the next commandin the case of a comment
			while(curCommand != "G01" && curCommand != "G4" && curCommand != "G04"){ 
				in_str >> curCommand; 
			}
		}
		movementGCode( in_str, curCommand, xPos, yPos, zPos, XYZ, timeXYZRecord, feedRate, time );
	}
	
	output(timeXYZRecord, feedRate, measurementUnits );
	
}


void initialization( std::ifstream& in_str, std::string& curCommand, double& xPos, double& yPos, double& zPos,
										std::vector<double>& XYZ, std::map< double, std::vector<double> >& timeXYZRecord, 
										double& feedRate, std::string& measurementUnits, double& time ){

	in_str >> curCommand;	//This is for going through the initial point setup aka the G90 line
	for( int i = 0; i < 3; ++i ){
		in_str >> curCommand;
		if( curCommand.at(0) == 'X' ){
			xPos = atof( curCommand.substr( curCommand.find('X') + 1 ).c_str() );
		}
		else if( curCommand.at(0) == 'Y' ){
			yPos = atof( curCommand.substr( curCommand.find('Y') + 1 ).c_str() );
		}
		else{
			zPos = atof( curCommand.substr( curCommand.find('Z') + 1 ).c_str() );
		}
	}
	XYZ.push_back(xPos);
	XYZ.push_back(yPos);
	XYZ.push_back(zPos);
	time = 0.0;
	timeXYZRecord[time] = XYZ;		//Initial XYZ position
	
	in_str >> curCommand;		//Measurement Unit command aka G20 or G21
	if( curCommand == "G20" ){
		measurementUnits = "Inches";
	}
	else{
		measurementUnits = "Millimeters";
	}
	
	in_str >> curCommand; //This is for going past the G91 line
	
	//This is for getting the feed rate
	in_str >> curCommand;
	in_str >> curCommand;
	feedRate = atof( curCommand.substr( curCommand.find('F') + 1 ).c_str() );

}


void movementGCode( std::ifstream& in_str, std::string& curCommand, double& xPos, double& yPos, double& zPos, 
										std::vector<double>& XYZ, std::map< double, std::vector<double> >& timeXYZRecord, 
										double const& feedRate, double& time ){	
	//Movement G-Code
	if( curCommand == "G01" ){
		double oldXPos = xPos;
		double oldYPos = yPos;
		double oldZPos = zPos;
		
		
		std::string movementCode;				//Used for parsing for simultaneous X & Y movements
		std::getline(in_str, movementCode);		
		std::istringstream iss(movementCode);
		
		while( iss >> curCommand ){			//Gets to the actual movement
			if( curCommand.at(0) == 'X' ){	//If the movement is in the X axis
				xPos += atof( curCommand.substr( curCommand.find('X') + 1 ).c_str() );	//Gets the X position
				XYZ[0] = xPos;
			}
			else if( curCommand.at(0) == 'Y' ){//If the movement is in the Y axis
				yPos += atof( curCommand.substr( curCommand.find('Y') + 1 ).c_str() ); //Gets the Y position
				XYZ[1] = yPos;
			}
			else{ //If the movement is in the Z axis
				zPos += atof( curCommand.substr( curCommand.find('Z') + 1 ).c_str() );	//Gets the Z position
				XYZ[2] = zPos;
			}
		}
		
		//Calculates the distance using pythagorean theorem
		double disXSquare = fabs(xPos - oldXPos) * fabs(xPos - oldXPos);
		double disYSquare = fabs(yPos - oldYPos) * fabs(yPos - oldYPos);
		double disZSquare = fabs(zPos - oldZPos) * fabs(zPos - oldZPos);
		double totalDistance = sqrt(disXSquare + disYSquare + disZSquare );
		time += totalDistance / feedRate;		//Time of movement = distance/feed rate
		
		timeXYZRecord[time] = XYZ;		//Inserting in the recent movement
	}
	//Pause G-Code
	else if( curCommand == "G4" || curCommand == "G04" ){
		in_str >> curCommand;
		time += atof( curCommand.substr( curCommand.find('P') + 1 ).c_str() );	//Adds the time from the pause
		timeXYZRecord[time] = XYZ;		//Inserting the position after the pause
	}
	//Not sure about other cases, if there are any
	else{
		
	}
	
}

void output( std::map< double, std::vector<double> >const& timeXYZRecord, double const& feedRate, std::string const& measurementUnits ){
	//Opens stuff for output for GNUplot
	Gnuplot gp;
	std::ofstream xWave("X-Wave.dat");
	std::ofstream yWave("Y-Wave.dat");
	
	//Displays the values
	std::cout << "Feed Rate: " << feedRate << std::endl;
	std::cout << "Measurement Units: " << measurementUnits << std::endl;
	
	//Outputs the time-position data to cout
	std::cout << std::endl << std::endl << "Time Values:" << std::endl;
	std::map< double, std::vector<double> >::const_iterator it = timeXYZRecord.begin();
	for( ; it != timeXYZRecord.end(); ++it ){
		std::cout << "Time: " << std::setfill(' ') << std::setw(6) << std::left << it->first
		<< "\t X-Position: " << std::setfill(' ') << std::setw(6) << std::left << it->second[0] 
		<< "\t Y-Position: " << std::setfill(' ') << std::setw(6) << std::left << it->second[1] 
		<< "\t Z-Position: " << std::setfill(' ') << std::setw(6) << std::left << it->second[2] 
		<< std::endl;
		
		//Stores the time vs X and time vs Y position values into files for GNUplot to use
		xWave << it->first << ' ' << it->second[0] << std::endl;
		yWave << it->first << ' ' << it->second[1] << std::endl;
	}
	
	xWave.close();
	yWave.close();
	
	gp 	<< "set term png\n" 
		<< "set xlabel 'Time (seconds)'\n"
		<< "set ylabel 'Displacement from Origin'\n"
		<< "set autoscale\n"
		<< "set output \"X-Waveform.png\"\n"
		<< "plot \"X-Wave.dat\" using 1:2 title 'X-Position' with lines\n"
		<< "set output \"Y-Waveform.png\"\n"
		<< "plot \"Y-Wave.dat\" using 1:2 title 'Y-Position' with lines\n"
		<< "set output \"X_Y-Waveform.png\"\n"
		<< "plot \"X-Wave.dat\" using 1:2 title 'X-Position' with lines, \\\n"
		<< "\"Y-Wave.dat\" using 1:2 title 'Y-Position' with lines\n";

}
