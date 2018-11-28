TRISTAN-Model-Fitting
----------------------
The modelFittingGUI.py module is the start up module in the TRISTAN-Model-Fitting application. 
It defines the GUI and the logic providing the application's functionality.
The GUI was built using PyQT5

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

		------------------------------------------------------

