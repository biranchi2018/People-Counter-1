There are two different methods of using this program. The first is to run it on video footage which you can do from the terminal. To do so use the following command:

python motion_detector.py --video [file path to video]

To run the algorithm to a camera that is attached to the machine that you're running it on just run the program in the IDE or:

python motion_detector.py


You can change the position of the boundary by changing the variable line_point1 and line_point2 at the top.

For different camera positions you may want to change the minimum size and the number of dilations and erosions.