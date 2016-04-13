It is necessary to have GNUplot installed along with a compiler that supports C++11 and the Boost library.

To compile the code, run something along the lines of 
"g++ -std=c++11 G-Code_Parser.cpp -o main -lboost_iostreams -lboost_system -lboost_filesystem"

Then, run the main executable file with the Gcode file in the same directory with the Gcode file name as a parameter.
For example:
"./main gcode.txt"

This will autogenerate three graphs: X-Position vs Time, Y-Position vs Time, X&Y-Position vs Time. The autogeneration utilizes GNUplot and will save the graphs as png files in the same directory as the executable. The graphs are set to be autoscaled, so some adjustment of the code/gnuplot may be necessary.
