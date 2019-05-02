MR Signal TRISTAN-Model-Fitting
----------------------
How to use.
------------
   The TRISTAN-Model-Fitting application allows the user to 
   analyse organ time/MR signal data by fitting a model 
   to the Region Of Interest (ROI) time/MR signal curve. 
   Changes in the MR signal correspond to changes in the
   concentration of the tracer introduced into the organ.

   This application provides the following functionality:
		1.  Load an XML based configuration file that describes
			the model(s) to be used for curve fitting. This configuration
			file allows the user to access one or more of the models 
			coded in the Python file ModelFunctions.py.  Data in this
			file determines the appearance of the user interface.
        2.	Load a CSV file of MR signal/time data.  
			The first column must contain time data in seconds. 
			The remaining columns of data must contain MR signal data 
			for individual organs at the time points in the time column. 
			There must be at least 2 columns of MR signal data.  
			There is no upper limit on the number of columns 
			of MR signal data.
			Each time a CSV file is loaded, the screen is reset to its initial state.
        3. Select a Region Of Interest (ROI) and display a plot of its MR signal against
            time.
        4. The user can then select a model they would like to fit to the ROI data.  
            When a model is selected, a schematic representation of it is displayed on the 
            right-hand side of the screen.
        5. Depending on the model selected the user can then select an Arterial Input Function(AIF)
            and/or a Venous Input Function (VIF) and display a plot(s) of its/their MR signal 
            against time on the same axes as the ROI.
        6. After step 4 is performed, the selected model is used to create a time/MR signal series
           based on default values for the models input parameters.  This data series is also plotted 
           on the above axes.
        7. The default model parameters are displayed on the form and the user may vary them
           and observe the effect on the curve generated in step 5.
        8. Clicking the 'Reset' button resets the model input parameters to their default values.
        9. By clicking the 'Fit Model' button, the model is fitted to the ROI data and the resulting
           values of the model input parameters are displayed on the screen together with 
           their 95% confidence limits.
        10. By clicking the 'Save plot data to CSV file' button the data plotted on the screen is saved
            to a CSV file - one column for each plot and a column for time.
            A file dialog box is displayed allowing the user to select a location 
            and enter a file name.
        11. By clicking the 'Save Report in PDF Format', the current state of the model fitting session
            is saved in PDF format.  This includes a image of the plot, name of the model, name of the 
            data file and the values of the model input parameters. If curve fitting has been carried 
            out and the values of the model input parameters have not been manually adjusted, then
            the report will contain the 95% confidence limits of the model input parameter values 
            arrived at by curve fitting.
        12. While this application is running, events & function calls with data where appropriate 
            are logged to a file called TRISTAN.log, stored at the same location as the source code.
            This file will used as a debugging aid. When a new instance of the application is started, 
            TRISTAN.log from the last session will be deleted and a new TRISTAN.log file created.
        13. Clicking the 'Start Batch Processing' button causes
		
		14. Clicking the 'Exit' button closes the application.

Setting up your computer to run TRISTAN Model Fitting application.
-------------------------------------------------------
In addition to the 32 bit version of Python 3, to run the TRISTAN model fitting application
the following Python packages must be installed on your computer:
	numpy
	pyautogui
	PyQt5
	matplotlib
	scipy
	FPDF
	openpyxl
	lmfit

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

The TracerkineticModels.py module contains functions that calculate the variation of 
MR signal with time according to several tracer kinetic models.   

GUI Structure
--------------
The GUI is based on the QWidget class. The GUI contains a single form.  
Controls are arranged in two vertical layouts on this form.
Consequently, a horizontal layout control in placed on this form. Within this horizontal
layout are placed 2 vertical layout controls.

The left-hand side vertical layout holds controls pertaining to the input and selection of data
and the selection of a model to analyse the data.  Also, the optimum model input parameters 
(and their 95% confidence limits) resulting from fitting the curve to the Region of Interest 
(ROI) MR signal/time curve are displayed.  

The right-hand side vertical layout holds a canvas widget for the graphical
display of the data.  Above this a schematic representation of the chosen 
model is displayed.

The appearance of the GUI is controlled by the CSS commands in styleSheet.py

Reading Data into the Application.
----------------------------------
The function loadDataFile loads the contents of a CSV file containing time and 
MR signal data into a dictionary of lists. The key is the name of the organ 
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

As the time data is read, it is divided by 60 in order to convert it into minutes

Included in this repository is a sample data input file called Sample_Data.csv

Batch Processing.
-----------------
This application can be used to automatically fit models to MR signal data in
2 or more files in the same folder.  For each data file, a PDF report containing the 
MR signal curve plot and a table of the optimum parameter values and thier 95% 
confidence limits is created in a folder called PDFReports.  

Likewise, for each data file, the time/MR signal data in the plot after curve 
fitting is saved in csv format in a file in a folder called CSVPlotDataFiles.

As each data file is processed, its name, the optimum parameter values and their 
95% confidence limits are written in csv format to the batch summary file. 
The names of any files that fail the validation tests are also recorded in this 
summary csv file together with the reasons for their failure. 

The folders PDFReports and CSVPlotDataFiles are automatically created within the folder 
containg the csv data files.

To initiate batch processing:
	1. Put all the data files you wish to batch process in the same folder.
		Note, all csv files in this folder will be included in the batch 
		processing. However, files will be skipped over which do not meet
		the above criteria.

	2. Load one of these files. 

	3. Select the region of interest for the whole batch.

	4. Select the model for the whole batch.

	5. Select the AIF and VIF (if appropriate) for the whole batch.

	6. Set the initial values of the input parameters or use the defaults.

	7. Click the 'Start Batch Processing' button.  You will be asked to give the
		name and location of the batch summary csv file or you can accept the defaults.
		A progress bar will show the progress batch processing.



