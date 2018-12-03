TRISTAN-Model-Fitting
----------------------
How to use.
------------
   The TRISTAN-Model-Fitting application allows the user to analyse organ time/concentration data
   by fitting a model to the Region Of Interest (ROI) time/concentration curve. 
   This application provides the following functionality:
        1. Load a CSV file of concentration/time data.  The first column must contain time data.
           The remaining columns of data must contain concentration data for individual organs at
           the time points in the time column. 
           There must be at least 2 columns of concentration data.  
           There is no upper limit on the number of columns of concentration data.
           Each time a CSV file is loaded, the screen is reset to its initial state.
        2. Select a Region Of Interest (ROI) and display a plot of its concentration against
            time.
        3. The user can then select a model they would like to fit to the ROI data.  
            When a model is selected, a schematic representation of it is displayed on the 
            right-hand side of the screen.
        4. Depending on the model selected the user can then select an Arterial Input Function(AIF)
            and/or a Venous Input Function (VIF) and display a plot(s) of its/their concentration 
            against time on the same axes as the ROI.
        5. After step 4 is performed, the selected model is used to create a time/concentration series
           based on default values for the models input parameters.  This data series is also plotted 
           on the above axes.
        6. The default model parameters are displayed on the form and the user may vary them
           and observe the effect on the curve generated in step 5.
        7. Clicking the 'Reset' button resets the model input parameters to their default values.
        8. By clicking the 'Fit Model' button, the model is fitted to the ROI data and the resulting
           values of the model input parameters are displayed on the screen together with 
           their 95% confidence limits.
        9. By clicking the 'Save plot data to CSV file' button the data plotted on the screen is saved
            to a CSV file - one column for each plot and a column for time.
            A file dialog box is displayed allowing the user to select a location 
            and enter a file name.
        10. By clicking the 'Save Report in PDF Format', the current state of the model fitting session
            is saved in PDF format.  This includes a image of the plot, name of the model, name of the 
            data file and the values of the model input parameters. If curve fitting has been carried 
            out and the values of the model input parameters have not been manually adjusted, then
            the report will contain the 95% confidence limits of the model input parameter values 
            arrived at by curve fitting.
        11. While this application is running, events & function calls with data where appropriate 
            are logged to a file called TRISTAN.log, stored at the same location as the source code.
            This file will used as a debugging aid. When a new instance of the application is started, 
            TRISTAN.log from the last session will be deleted and a new TRISTAN.log file created.
        12. Clicking the 'Exit' button closes the application.

Setting up your computer to run TRISTAN Model Fitting.
-------------------------------------------------------
	In addition to the 32 bit version of Python 3, to run the TRISTAN model fitting application
	the following Python packages must be installed on your computer:
		numpy
		pyautogui
		PyQt5
		matplotlib
		scipy
		FPDF

	The 4 Python files that comprise this application must be placed in folder together
	with the accompanying an images subfolder containing the 7 graphics (jpg & png) files.
		
Application Module Structure.
---------------------------
The modelFittingGUI.py class module is the start up module in the TRISTAN-Model-Fitting application. 
It defines the GUI and the logic providing the application's functionality.
The GUI was built using PyQT5.

The styleSheet.py module contains style instructions using CSS notation for each control/widget.

The Tools.py module contains a library of mathematical functions used to solve the equations in 
the models in TracerKineticModels.py.

Objects of the following 2 classes are created in modelFittingGUI.py and provide services 
to this class:
The PDFWrite.py class module creates and saves a report of a model fitting session in a PDF file.

The TracerkineticModels.py module contains functions that calculate the variation of concentration
with time according to several tracer kinetic models.   

GUI Structure
--------------
The GUI is based on the QDialog class, which is the base class of dialog windows.
The GUI contains a single form.  Controls are arranged in three verticals on this form.
Consequently, a horizontal layout control in placed on this form. Within this horizontal
layout is placed 3 vertical layout controls.

The left-hand side vertical layout holds controls pertaining to the input and selection of data
and the selection of a model to analyse the data.

The central vertical layout holds a canvas widget for the graphical display of the data.

The right-hand side vertical layout holds controls for the display of a schematic 
representation of the chosen model and the optimum model input parameters resulting
from fitting the curve to the Region of Interest (ROI) concentration/time curve.

The appearance of the GUI is controlled by the CSS commands in styleSheet.py

Reading Data into the Application.
----------------------------------
The function loadDataFile loads the contents of a CSV file containing time and 
concentration data into a dictionary of lists. The key is the name of the organ 
or 'time' and the corresponding value is a list of concentrations for that organ
(or times when the key is 'time').  The header label of each column of data is
taken as a key.  
        
The following validation is applied to the data file:
    -The CSV file must contain at least 3 columns of data separated by commas.
    -The first column in the CSV file must contain time data.
    -The header of the time column must contain the word 'time'.

A list of keys is created and displayed in drop down lists to provide a means 
of selecting the Region of Interest (ROI), Arterial Input Function (AIF) and
the Venous Input Function (VIF).


