File: README.txt
This is the README file for the video analyzer tool, developed for IBM's Parallel Dipole Line magnetic trap system. This tool is a gui-based tool for manual and automatic extraction of oscillation parameters from video, based on the idea that a bright object can be detected against a dark background over a series of frames, resulting in a motion-tracking capability.

Installation/Dependencies
The code is currently in the form of python scripts, run from the command line in the format > python main.py path/to/video/file <options>
The code depends on Python 2.7 and the following python modules:
OpenCV version 3.0.1
Numpy
Scipy
Matplotlib
ArgParse
Tkinter

Installation of OpenCV is not straightforward and highly machine dependent. It is strongly recommended to use virtual environments when installing OpenCV. Check out this website for tutorials and instructions: www.pyimagesearch.com

Operating the Program
The video analyzer tool requires a set of parameters that the user inputs, notably crop bounds, inspection line, framerate, length calibration, and a smoothing filter window size. The main script prompts the user for these parameters and tries to gather some of them automatically. Upon launching the script, the user will see the results of the automatic inspection line and crop bounds routine. The inspection line is a line across the frame that represents the expected path of motion for the object being tracked. The crop bounds help the program discard irrelevant information that could get in the way of the motion tracking algorithms. The user has the option to either accept the computer's attempt or input the parameters manually. To enable manual adjustment, press N on the keyboard. There will be a screen displaying the current crop bounds of the video. Toggle between lines using SPACE and move the lines using the ASWD keys (A for left, S for down, W for up, and D for right). Try to include only the area encompassed by the path of the object. When satisfied, press ENTER. The next screen is the manual inspection line selector. Select two points on the path of the object. A good method is to use the middle of the left and right edges of the object. The user then has the opportunity to continue or repeat the process again. Next is the length calibration, which can also be included manually at the command line. Select two points, whose distance apart is known. Examples include the length of the object or ticks on a ruler also in the frame. When prompted, input the actual distance in mm. The frames are then read and analyzed by the program. The results are first displayed as a live tracker of the video. The program will continue when finished, but the user can also press Y to continue to the oscillation extraction phase. The program will then display a plot of the position of the object as a function of time, with a fitted damped simple harmonic oscillation function overlain. Upon closing this window, the program saves the figure and the data to the same directory as the video file.