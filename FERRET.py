"""This module is the start up module in the TRISTAN-Model-Fitting application. 
It defines the GUI and the logic providing the application's functionality. 
The GUI was built using PyQT5.

How to Use.
-----------
   The TRISTAN-Model-Fitting application allows the user to analyse 
   organ time/concentration data by fitting a model to the 
   Region Of Interest (ROI) time/concentration curve. 
   The TRISTAN-Model-Fitting application provides the following functionality:
        1. Load an XML configuration file that describes the models to be fitted
            to the concentration/time data.
        2. Then load a CSV file of concentration/time or MR Signal/time data.  
            The first column must contain time data in seconds. 
            remaining columns of data must contain concentration in 
			millimoles (mM) or MR signal data for individual organs 
            at the time points in the time column. 
			There must be at least 2 columns of concentration data.  
			There is no upper limit on the number of columns of concentration data.
			Each time a CSV file is loaded, the screen is reset to its initial state.
        3. Select a Region Of Interest (ROI) and display a plot of its concentration against
            time.
        4. The user can then select a model they would like to fit to the ROI data.  
            When a model is selected, a schematic representation of it may be
           displayed on the right-hand side of the screen if an image is available.
           An image file will have to be stored in the images 
           folder in the root folder containing the application 
           source code and its name defined in the XML configuration file.
        5. Depending on the model selected the user can then select an Arterial Input Function(AIF)
            and/or a Venous Input Function (VIF) and display a plot(s) of its/their concentration 
            against time on the same axes as the ROI.
        6. After step 4 is performed, the selected model is used 
           to create a time/concentration series
           based on default values for the models input parameters.  
          data series is also plotted on the above axes.
        7. The default model parameters are displayed on the form 
           and the user may vary them and observe the effect on 
           the curve generated in step 5.
        8. Clicking the 'Reset' button resets the model 
           input parameters to their default values.
        9. By clicking the 'Fit Model' button, the model is 
           fitted to the ROI data and the resulting values 
           of the model input parameters are displayed on 
           the screen together with their 95% confidence limits.
        10. By clicking the 'Save plot data to CSV file' button the data plotted on the screen is saved
            to a CSV file - one column for each plot and a column for time.
            A file dialog box is displayed allowing the user to select a location 
            and enter a file name.
        11. By clicking the 'Save Report in PDF Format', 
            current state of the model fitting session
            is saved in PDF format.  This includes a image 
            of the plot, name of the model, name of the 
            data file and the values of the model input parameters. 
            If curve fitting has been carried 
            out and the values of the model input parameters 
            have not been manually adjusted, then the report 
            will contain the 95% confidence limits of the 
            model input parameter values arrived at by curve fitting.
        12. While this application is running, events & function 
            calls with data where appropriate 
            are logged to a file called TRISTAN.log, 
            stored at the same location as the 
            source code or executable. This file can be used as a debugging aid. 
            When a new instance of the application is started, 
            TRISTAN.log from the last session will be deleted
            and a new log file started.
        13. Clicking the 'Start Batch Processing' button applies model fitting
            to the MR signal/time data in all the files in the folder containing
            the data file selected in step 2.  For each file, a PDF report is created
            as in step 11. Also, a Microsoft Excel spread sheet summarising all
            the results is generated.
        14. Clicking the 'Exit' button closes the application.

Application Module Structure.
---------------------------
The modelFittingGUI.py class module is the start up module 
in the TRISTAN-Model-Fitting application. 
It defines the GUI and the logic providing the application's functionality.
The GUI was built using PyQT5.

The XMLReader.py class module uses the xml.etree.ElementTree package to parse
the XML configuration file that describes all the models to be made available
for curve fitting.  It also contains functions that query the XML tree using
XPath notation and return data.

The styleSheet.py module contains style instructions using CSS 
notation for each control/widget.

The Tools.py module contains a library of mathematical functions 
used to solve the equations in the models in ModelFunctionsHelper.py.

Objects of the following 2 classes are created in modelFittingGUI.py 
and provide services to this class:
    1. The PDFWrite.py class module creates and saves a report 
    of a model fitting session in a PDF file.
    2. The ExcelWriter.py class module uses the openpyxl package 
    to create an Excel spreadsheet and write a summary of the 
    results from the batch processing of data files.

The ModelFunctions.py class module contains functions that use 
tracer kinetic models to calculate the variation of concentration
with time according to several tracer kinetic models. 

The ModelFunctionsHelper module coordinates the calling of model 
functions in ModelFunctions.py by functions in ModelFittingGUI.py

GUI Structure
--------------
The GUI is based on the QWidget class.
The GUI contains a single form.  Controls are arranged in two 
vertical columns on this form using Vertical Layout widgets.
Consequently, a horizontal layout control in placed on this form. 
Within this horizontal layout are placed 2 vertical layout controls.

The left-hand side vertical layout holds controls pertaining to the input and 
selection of data and the selection of a model to analyse the data. The results
of curve fitting, optimum parameter values and their confidence limits
are displayed next to their parameter input values.

The right-hand side vertical layout holds controls for the display of a schematic 
representation of the chosen model and a canvas widget for the 
graphical display of the data.

The appearance of the GUI is controlled by the CSS commands in styleSheet.py

Reading Data into the Application.
----------------------------------
The function LoadConfigFile loads and parses the contents of the 
XML file that describes the models to be used for curve fitting.  
If parsing is successful, the XML tree is stored in memory 
and used to build a list of models for display in a combo box on the GUI,
and the 'Load Data File' button is made visible.
See the README file for a detailed description of the XML configuration file.

Clicking the 'Load Data File' button executes the LoadDataFile function.
The function LoadDataFile loads the contents of a CSV file
containing time and MR signal data into a dictionary of lists.
The key is the name of the organ or 'time' and the 
corresponding value is a list of MR signals for that organ
(or times when the key is 'time').  
The header label of each column of data is taken as a key.  
        
The following validation is applied to the data file:
    -The CSV file must contain at least 3 columns of data separated by commas.
    -The first column in the CSV file must contain time data.
    -The header of the time column must contain the word 'time'.

A list of keys is created and displayed in drop down lists to provide a means 
of selecting the Region of Interest (ROI), Arterial Input Function (AIF) and
the Venous Input Function (VIF).

As the time data is read, it is divided by 60 in order to convert it into minutes.
        """
__author__ = "Steve Shillitoe, https://www.imagingbiomarkers.org/stephen-shillitoe"
__version__ = "1.0"
__date__ = "Date: 2018/12/12"

import sys
import csv
import os
#Add folders CoreModules & Models to the Module Search Path. 
#path[0] is the current working directory
sys.path.append(os.path.join(sys.path[0],'CoreModules'))
sys.path.append(os.path.join(sys.path[0],'Models'))
import numpy as np
import pyautogui
import logging
from typing import List
import datetime

from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QPushButton, QDoubleSpinBox,\
     QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel,  \
     QMessageBox, QFileDialog, QCheckBox, QLineEdit, QSizePolicy, QSpacerItem, \
     QGridLayout, QWidget, QStatusBar, QProgressBar, QFrame

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from scipy.stats.distributions import  t

import ModelFunctionsHelper

#Import CSS file
import StyleSheet

#Import PDF report writer class
from PDFWriter import PDF

from ExcelWriter import ExcelWriter

from XMLReader import XMLReader
 
########################################
##              CONSTANTS             ##
########################################
WINDOW_TITLE = 'FERRET - Model-fitting of dynamic contrast-enhanced MRI'
REPORT_TITLE = 'FERRET - Model-fitting of dynamic contrast-enhanced MRI'
IMAGE_NAME = 'model.png'
DEFAULT_REPORT_FILE_PATH_NAME = 'report.pdf'
DEFAULT_PLOT_DATA_FILE_PATH_NAME = 'plot.csv'
LOG_FILE_NAME = "TRISTAN.log"
MIN_NUM_COLUMNS_CSV_FILE = 3

#Image Files
TRISTAN_LOGO = 'images\\TRISTAN LOGO.jpg'
LARGE_TRISTAN_LOGO ='images\\logo-tristan.png'
UNI_OF_LEEDS_LOGO ='images\\uni-leeds-logo.jpg'
FERRET_LOGO = 'images\\FERRET_LOGO.png'
IMAGE_FOLDER = 'images\\'
#######################################

#Create and configure the logger
#First delete the previous log file if there is one
if os.path.exists(LOG_FILE_NAME):
   os.remove(LOG_FILE_NAME) 
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=LOG_FILE_NAME, 
                    level=logging.INFO, 
                    format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class NavigationToolbar(NavigationToolbar):
    """
    Removes unwanted default buttons in the Navigation Toolbar by creating
    a subclass of the NavigationToolbar class from from 
    matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    that only defines the desired buttons
    """
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]


# User-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class NoModelFunctionDefined(Error):
   """Raised when the name of the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass

class NoModuleDefined(Error):
   """Raised when the name of the module containing the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass

class NoModelInletTypeDefined(Error):
   """Raised when the inlet type of the model is not returned
    from the XML configuration file."""
   pass

class ModelFittingApp(QWidget):   
    """This class defines the TRISTAN Model Fitting software 
       based on QWidget class that provides the GUI.
       This includes seting up the GUI and defining the methods 
       that are executed when events associated with widgets on
       the GUI are executed."""
     
    def __init__(self, parent=None):
        """Creates the GUI. Controls on the GUI are placed onto 2 vertical
           layout panals placed on a horizontal layout panal.
           The appearance of the widgets is determined by CSS 
           commands in the module styleSheet.py. 
           
           The left-handside vertical layout panal holds widgets for the 
           input of data & the selection of the model to fit to the data.
           Optimum parameter data and their confidence limits resulting
           from the model fit are also displayed.
           
           The right-handside vertical layout panal holds the graph 
           displaying the time/concentration data and the fitted model.
           Above this graph is displayed a schematic representation of the
           model.
           
           This method coordinates the calling of methods that set up the 
           widgets on the 2 vertical layout panals."""

        super(ModelFittingApp, self).__init__(parent)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(FERRET_LOGO))
        width, height = self.GetScreenResolution()
        self.setGeometry(0, 0, width, height*0.95)
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint |  
                            QtCore.Qt.WindowCloseButtonHint)
        
        # Store path to time/concentration data files for use 
        # in batch processing.
        self.dataFileDirectory = ""
        
        # Name of current loaded data file
        self.dataFileName = ''
        self.yAxisLabel = ''

        # Boolean variable indicating that the last 
        # change to the model parameters was caused
        #  by curve fitting.
        self.isCurveFittingDone = False

        # Dictionary to store signal data from the data input file
        self.signalData={} 
        
        # List to store concentrations calculated by the models
        self.listModel = [] 
        
        # Stores optimum parameters from Curve fitting
        self.optimisedParamaterList = [] 
        
        # XML reader object to process XML configuration file
        self.objXMLReader = XMLReader() 
        
        self.ApplyStyleSheet()
       
        # Setup the layouts, the containers for widgets
        verticalLayoutLeft, verticalLayoutRight = self.SetUpLayouts() 
        
        # Add widgets to the left-hand side vertical layout
        self.SetUpLeftVerticalLayout(verticalLayoutLeft)

        # Set up the graph to plot concentration data on
        #  the right-hand side vertical layout
        self.SetUpPlotArea(verticalLayoutRight)
        print(os.getcwd())
        
        logger.info("GUI created successfully.")

    def SetUpLayouts(self):
        """Places a horizontal layout on the window
           and places 2 vertical layouts on the horizontal layout.
           
           Returns the 2 vertical layouts to be used by other methods
           that place widgets on them.
           
           Returns
           -------
                Two vertical layouts that have been added to a 
                horizontal layout.
           """

        horizontalLayout = QHBoxLayout()
        verticalLayoutLeft = QVBoxLayout()
        verticalLayoutRight = QVBoxLayout()
        
        self.setLayout(horizontalLayout)
        horizontalLayout.addLayout(verticalLayoutLeft, 9)
        horizontalLayout.addLayout(verticalLayoutRight, 10)
        return verticalLayoutLeft,  verticalLayoutRight  

    def SetUpLeftVerticalLayout(self, layout):
        """
        Creates widgets and places them on the left-handside vertical layout. 

        Inputs
        ------
        layout - holds a reference to the left handside vertical layout widget
        """
        # Create Load Configuration XML file Button
        self.btnLoadConfigFile = QPushButton('Load Model Library')
        self.btnLoadConfigFile.setToolTip(
            'Opens file dialog box to select the model library file')
        self.btnLoadConfigFile.setShortcut("Ctrl+C")
        self.btnLoadConfigFile.setAutoDefault(False)
        self.btnLoadConfigFile.clicked.connect(self.LoadConfigFile)

        # Create Load Data File Button
        self.btnLoadDataFile = QPushButton('Load Data File')
        self.btnLoadDataFile.hide()
        self.btnLoadDataFile.setToolTip('Opens file dialog box to select the data file')
        self.btnLoadDataFile.setShortcut("Ctrl+L")
        self.btnLoadDataFile.setAutoDefault(False)
        self.btnLoadDataFile.resize(self.btnLoadDataFile.minimumSizeHint())
        self.btnLoadDataFile.clicked.connect(self.LoadDataFile)
        
        verticalSpacer = QSpacerItem(10, 60, QSizePolicy.Minimum, 
                          QSizePolicy.Minimum)
        #layout.addItem(verticalSpacer)
        layout.addWidget(self.btnLoadConfigFile)
        layout.addWidget(self.btnLoadDataFile)
        #layout.addItem(verticalSpacer)

        # Create dropdown list & label for selection of ROI
        self.lblROI = QLabel("Region of Interest:")
        self.lblROI.setAlignment(QtCore.Qt.AlignRight)
        self.cmbROI = QComboBox()
        self.cmbROI.setToolTip('Select Region of Interest')
        self.lblROI.hide()
        self.cmbROI.hide()
        
        # Below Load Data button add ROI list.  It is placed in a 
        # horizontal layout together with its label, so they are
        # aligned in the same row.
        ROI_HorizontalLayout = QHBoxLayout()
        ROI_HorizontalLayout.insertStretch (0, 2)
        ROI_HorizontalLayout.addWidget(self.lblROI)
        ROI_HorizontalLayout.addWidget(self.cmbROI)
        layout.addLayout(ROI_HorizontalLayout)
        
        # Create a group box to group together widgets associated with
        # the model selected. 
        self.SetUpModelGroupBox(layout)
        
        self.btnSaveReport = QPushButton('Save Report in PDF Format')
        self.btnSaveReport.hide()
        self.btnSaveReport.setToolTip(
        'Insert an image of the graph opposite and associated data in a PDF file')
        layout.addWidget(self.btnSaveReport, QtCore.Qt.AlignTop)
        self.btnSaveReport.clicked.connect(self.CreatePDFReport)

        self.SetUpBatchProcessingGroupBox(layout)
        
        layout.addStretch(1)
        self.btnExit = QPushButton('Exit')
        layout.addWidget(self.btnExit)
        self.statusbar = QStatusBar()
        layout.addWidget(self.statusbar)
        self.btnExit.clicked.connect(self.ExitApp)
        
    def SetUpModelGroupBox(self, layout):
        """Creates a group box to hold widgets associated with the 
        selection of a model and for inputing/displaying that model's
        parameter data."""
        self.groupBoxModel = QGroupBox('Model Fitting')
        self.groupBoxModel.setAlignment(QtCore.Qt.AlignHCenter)
        # The group box is hidden until a ROI is selected.
        self.groupBoxModel.hide()
        layout.addWidget(self.groupBoxModel)
        
        # Create horizontal layouts, one row of widgets to 
        # each horizontal layout. Then add them to a vertical layout, 
        # then add the vertical layout to the group box
        modelHorizontalLayoutModelList = QHBoxLayout()
        modelHorizontalLayoutAIF = QHBoxLayout()
        modelHorizontalLayoutVIF = QHBoxLayout()
        modelHorizontalLayoutReset = QHBoxLayout()
        grid = QGridLayout()
        modelHorizontalLayoutFitModelBtn = QHBoxLayout()
        modelHorizontalLayoutSaveCSVBtn = QHBoxLayout()
        modelVerticalLayout = QVBoxLayout()
        modelVerticalLayout.setAlignment(QtCore.Qt.AlignTop) 
        modelVerticalLayout.addLayout(modelHorizontalLayoutModelList)
        modelVerticalLayout.addLayout(modelHorizontalLayoutAIF)
        modelVerticalLayout.addLayout(modelHorizontalLayoutVIF)
        modelVerticalLayout.addLayout(modelHorizontalLayoutReset)
        modelVerticalLayout.addLayout(grid)
        modelVerticalLayout.addLayout(modelHorizontalLayoutFitModelBtn)
        modelVerticalLayout.addLayout(modelHorizontalLayoutSaveCSVBtn)
        self.groupBoxModel.setLayout(modelVerticalLayout)
        
        # Create dropdown list to hold names of models
        self.modelLabel = QLabel("Model:")
        self.modelLabel.setAlignment(QtCore.Qt.AlignRight)
        self.cmbModels = QComboBox()
        self.cmbModels.setToolTip('Select a model to fit to the data')
        #Display first item in list, the string "Select a Model"
        self.cmbModels.setCurrentIndex(0) 
        self.cmbModels.currentIndexChanged.connect(self.UncheckFixParameterCheckBoxes)
        self.cmbModels.currentIndexChanged.connect(self.DisplayModelImage)
        self.cmbModels.currentIndexChanged.connect(self.ConfigureGUIForEachModel)
        self.cmbModels.currentIndexChanged.connect(lambda: self.clearOptimisedParamaterList('cmbModels')) 
        self.cmbModels.currentIndexChanged.connect(self.display_FitModel_SaveCSV_SaveReport_Buttons)
        self.cmbModels.activated.connect(lambda:  self.plotMRSignals('cmbModels'))

        # Create dropdown lists for selection of AIF & VIF
        self.lblAIF = QLabel('Arterial Input Function:')
        self.cmbAIF = QComboBox()
        self.cmbAIF.setToolTip('Select Arterial Input Function')
        self.lblVIF = QLabel("Venous Input Function:")
        self.cmbVIF = QComboBox()
        self.cmbVIF.setToolTip('Select Venous Input Function')

        # When a ROI is selected: 
        # plot its concentration data on the graph.
        self.cmbROI.activated.connect(lambda:  self.plotMRSignals('cmbROI'))
        # then make the Model groupbox and the widgets it contains visible.
        self.cmbROI.activated.connect(self.DisplayModelFittingGroupBox)
        # When an AIF is selected plot its concentration data on the graph.
        self.cmbAIF.activated.connect(lambda: self.plotMRSignals('cmbAIF'))
        # When an AIF is selected display the Fit Model and Save plot CVS buttons.
        self.cmbAIF.currentIndexChanged.connect(self.display_FitModel_SaveCSV_SaveReport_Buttons)
        self.cmbVIF.currentIndexChanged.connect(self.display_FitModel_SaveCSV_SaveReport_Buttons)
        # When a VIF is selected plot its concentration data on the graph.
        self.cmbVIF.activated.connect(lambda: self.plotMRSignals('cmbVIF'))
        self.lblAIF.hide()
        self.cmbAIF.hide()
        self.lblVIF.hide()
        self.cmbVIF.hide()
        self.cmbROI.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbAIF.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbVIF.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        # Add combo boxes and their labels to the horizontal layouts
        modelHorizontalLayoutModelList.insertStretch (0, 2)
        modelHorizontalLayoutModelList.addWidget(self.modelLabel)
        modelHorizontalLayoutModelList.addWidget(self.cmbModels)
        modelHorizontalLayoutAIF.insertStretch (0, 2)
        modelHorizontalLayoutAIF.addWidget(self.lblAIF)
        modelHorizontalLayoutAIF.addWidget(self.cmbAIF)
        modelHorizontalLayoutVIF.insertStretch (0, 2)
        modelHorizontalLayoutVIF.addWidget(self.lblVIF)
        modelHorizontalLayoutVIF.addWidget(self.cmbVIF)
        
        self.cboxDelay = QCheckBox('Delay', self)
        self.cboxConstaint = QCheckBox('Constraint', self)
        self.cboxDelay.hide()
        self.cboxConstaint.hide()
        self.btnReset = QPushButton('Reset')
        self.btnReset.setToolTip('Reset parameters to their default values.')
        self.btnReset.hide()
        self.btnReset.clicked.connect(self.InitialiseParameterSpinBoxes)
        self.btnReset.clicked.connect(self.OptimumParameterChanged)
        # If parameters reset to their default values, 
        # replot the concentration and model data
        self.btnReset.clicked.connect(lambda: self.plotMRSignals('Reset Button'))
        modelHorizontalLayoutReset.addWidget(self.cboxDelay)
        modelHorizontalLayoutReset.addWidget(self.cboxConstaint)
        modelHorizontalLayoutReset.addWidget(self.btnReset)
        
        self.lblPhysParams = QLabel("Model Parameters")
        self.lblConfInt = QLabel("95% Confidence Interval")
        self.lblFix = QLabel("Fix")
        self.lblPhysParams.hide()
        self.lblFix.hide()
        self.lblConfInt.hide()
        self.lblPhysParams.setAlignment(QtCore.Qt.AlignLeft)
        self.lblConfInt.setAlignment(QtCore.Qt.AlignRight)
        self.lblFix.setAlignment(QtCore.Qt.AlignLeft)

        # Create model parameter spinboxes and their labels
        # Label text set when the model is selected
        self.labelParameter1 = QLabel("") 
        self.labelParameter1.hide()
        self.ckbParameter1 = QCheckBox("")
        self.ckbParameter1.hide()
        self.lblParam1ConfInt = QLabel("")
        self.lblParam1ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        
        self.labelParameter2 = QLabel("")
        self.ckbParameter2 = QCheckBox("")
        self.ckbParameter2.hide()
        self.lblParam2ConfInt = QLabel("")
        self.lblParam2ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        
        self.labelParameter3 = QLabel("")
        self.ckbParameter3 = QCheckBox("")
        self.ckbParameter3.hide()
        self.lblParam3ConfInt = QLabel("")
        self.lblParam3ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        
        self.labelParameter4 = QLabel("")
        self.ckbParameter4 = QCheckBox("")
        self.ckbParameter4.hide()
        self.lblParam4ConfInt = QLabel("")
        self.lblParam4ConfInt.setAlignment(QtCore.Qt.AlignCenter)

        self.labelParameter5 = QLabel("")
        self.ckbParameter5 = QCheckBox("")
        self.ckbParameter5.hide()
        self.lblParam5ConfInt = QLabel("")
        self.lblParam5ConfInt.setAlignment(QtCore.Qt.AlignCenter)

        self.labelParameter1.setWordWrap(True)
        self.labelParameter2.setWordWrap(True)
        self.labelParameter3.setWordWrap(True)
        self.labelParameter4.setWordWrap(True)
        self.labelParameter5.setWordWrap(True)
        
        self.spinBoxParameter1 = QDoubleSpinBox()
        self.spinBoxParameter2 = QDoubleSpinBox()
        self.spinBoxParameter3 = QDoubleSpinBox()
        self.spinBoxParameter4 = QDoubleSpinBox()
        self.spinBoxParameter5 = QDoubleSpinBox()
        
        self.spinBoxParameter1.hide()
        self.spinBoxParameter2.hide()
        self.spinBoxParameter3.hide()
        self.spinBoxParameter4.hide()
        self.spinBoxParameter5.hide()

        # If a parameter value is changed, replot the concentration and model data
        self.spinBoxParameter1.valueChanged.connect(lambda: self.plotMRSignals('spinBoxParameter1')) 
        self.spinBoxParameter2.valueChanged.connect(lambda: self.plotMRSignals('spinBoxParameter2')) 
        self.spinBoxParameter3.valueChanged.connect(lambda: self.plotMRSignals('spinBoxParameter3')) 
        self.spinBoxParameter4.valueChanged.connect(lambda: self.plotMRSignals('spinBoxParameter4'))
        self.spinBoxParameter5.valueChanged.connect(lambda: self.plotMRSignals('spinBoxParameter5'))
        # Set boolean variable, self.isCurveFittingDone to false to 
        # indicate that the value of a model parameter
        # has been changed manually rather than by curve fitting
        self.spinBoxParameter1.valueChanged.connect(self.OptimumParameterChanged) 
        self.spinBoxParameter2.valueChanged.connect(self.OptimumParameterChanged) 
        self.spinBoxParameter3.valueChanged.connect(self.OptimumParameterChanged) 
        self.spinBoxParameter4.valueChanged.connect(self.OptimumParameterChanged)
        self.spinBoxParameter5.valueChanged.connect(self.OptimumParameterChanged)

        grid.addWidget(self.lblPhysParams, 0, 0, 1, 2, alignment=QtCore.Qt.AlignLeft)
        grid.addWidget(self.lblFix, 0, 3)
        grid.addWidget(self.lblConfInt, 0, 4)

        grid.addWidget(self.labelParameter1, 1, 0, 1, 2)
        grid.addWidget(self.spinBoxParameter1, 1, 2)
        grid.addWidget(self.ckbParameter1, 1, 3)
        grid.addWidget(self.lblParam1ConfInt, 1, 4, alignment=QtCore.Qt.AlignCenter)
       
        grid.addWidget(self.labelParameter2, 2, 0, 1, 2)
        grid.addWidget(self.spinBoxParameter2, 2, 2)
        grid.addWidget(self.ckbParameter2, 2, 3)
        grid.addWidget(self.lblParam2ConfInt, 2, 4, alignment=QtCore.Qt.AlignCenter)

        grid.addWidget(self.labelParameter3, 3, 0, 1, 2)
        grid.addWidget(self.spinBoxParameter3, 3, 2)
        grid.addWidget(self.ckbParameter3, 3, 3)
        grid.addWidget(self.lblParam3ConfInt, 3, 4, alignment=QtCore.Qt.AlignCenter)

        grid.addWidget(self.labelParameter4, 4, 0, 1, 2)
        grid.addWidget(self.spinBoxParameter4, 4, 2)
        grid.addWidget(self.ckbParameter4, 4, 3)
        grid.addWidget(self.lblParam4ConfInt, 4, 4, alignment=QtCore.Qt.AlignCenter)

        grid.addWidget(self.labelParameter5, 7, 0, 1, 2)
        grid.addWidget(self.spinBoxParameter5, 7, 2)
        grid.addWidget(self.ckbParameter5, 7, 3)
        grid.addWidget(self.lblParam5ConfInt, 7, 4)

        self.btnFitModel = QPushButton('Fit Model')
        self.btnFitModel.setToolTip('Use non-linear least squares to fit the selected model to the data')
        self.btnFitModel.hide()
        modelHorizontalLayoutFitModelBtn.addWidget(self.btnFitModel)
        self.btnFitModel.clicked.connect(self.CurveFit)
        
        self.btnSaveCSV = QPushButton('Save plot data to CSV file')
        self.btnSaveCSV.setToolTip('Save the data plotted on the graph to a CSV file')
        self.btnSaveCSV.hide()
        modelHorizontalLayoutSaveCSVBtn.addWidget(self.btnSaveCSV)
        self.btnSaveCSV.clicked.connect(self.SaveCSVFile)


    def SetUpBatchProcessingGroupBox(self, layout):
        """Creates a group box to hold widgets associated with batch
        processing functionality.
        
        Inputs
        ------
        layout - holds a reference to the left handside vertical layout widget
        
        """
        self.groupBoxBatchProcessing = QGroupBox('Batch Processing')
        self.groupBoxBatchProcessing.setAlignment(QtCore.Qt.AlignHCenter)
        self.groupBoxBatchProcessing.hide()
        layout.addWidget(self.groupBoxBatchProcessing)

        verticalLayout = QVBoxLayout()
        self.groupBoxBatchProcessing.setLayout(verticalLayout)

        self.btnBatchProc = QPushButton('Start Batch Processing')
        self.btnBatchProc.setToolTip('Processes all the CSV data files in the selected directory')
        self.btnBatchProc.clicked.connect(self.BatchProcessAllCSVDataFiles) 
        verticalLayout.addWidget(self.btnBatchProc)

        self.lblBatchProcessing = QLabel("")
        self.lblBatchProcessing.setWordWrap(True)
        verticalLayout.addWidget(self.lblBatchProcessing)
        self.pbar = QProgressBar(self)
        verticalLayout.addWidget(self.pbar)
        self.pbar.hide()

    def DisplayModelFittingGroupBox(self):
        """Shows the model fitting group box if a ROI is selected. 
        Otherwise hides the model fitting group box. """
        try:
            ROI = str(self.cmbROI.currentText())
            if ROI != 'Please Select':
                # A ROI has been selected
                self.groupBoxModel.show()
                self.btnSaveReport.show()
                logger.info("Function DisplayModelFittingGroupBox called. Model group box and Save Report button shown when ROI = {}".format(ROI))
            else:
                self.groupBoxModel.hide()
                self.cmbAIF.setCurrentIndex(0)
                self.cmbModels.setCurrentIndex(0)
                self.btnSaveReport.hide()
                logger.info("Function DisplayModelFittingGroupBox called. Model group box and Save Report button hidden.")
        except Exception as e:
            print('Error in function DisplayModelFittingGroupBox: ' + str(e)) 
            logger.error('Error in function DisplayModelFittingGroupBox: ' + str(e))

    def SetUpPlotArea(self, layout):
        """Adds widgets for the display of the graph onto the 
        right-hand side vertical layout.
        
        Inputs
        ------
        layout - holds a pointer to the right-hand side vertical layout widget
        """
        layout.setAlignment(QtCore.Qt.AlignTop)

        # lblModelImage is used to display a schematic
        # representation of the model.
        self.lblModelImage = QLabel('') 
        self.lblModelImage.setAlignment(QtCore.Qt.AlignCenter )
        self.lblModelImage.setMargin(2)
                                        
        self.lblModelName = QLabel('')
        self.lblModelName.setAlignment(QtCore.Qt.AlignCenter)
        self.lblModelName.setMargin(2)
        self.lblModelName.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.lblModelName.setWordWrap(True)

        self.figure = plt.figure(figsize=(5, 8), dpi=100) 
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter 
        # to its __init__ function
        self.canvas = FigureCanvas(self.figure)
        # this is the Navigation widget
        # it takes the Canvas widget as a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Display TRISTAN & University of Leeds Logos in labels
        self.lblFERRET_Logo = QLabel(self)
        self.lblTRISTAN_Logo = QLabel(self)
        self.lblUoL_Logo = QLabel(self)
        self.lblTRISTAN_Logo.setAlignment(QtCore.Qt.AlignHCenter)
        self.lblUoL_Logo.setAlignment(QtCore.Qt.AlignHCenter)

        pixmapFERRET = QPixmap(FERRET_LOGO)
        pMapWidth = pixmapFERRET.width() 
        pMapHeight = pixmapFERRET.height() 
        pixmapFERRET = pixmapFERRET.scaled(pMapWidth, pMapHeight, 
                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.lblFERRET_Logo.setPixmap(pixmapFERRET) 

        pixmapTRISTAN = QPixmap(LARGE_TRISTAN_LOGO)
        pMapWidth = pixmapTRISTAN.width() * 0.5
        pMapHeight = pixmapTRISTAN.height() * 0.5
        pixmapTRISTAN = pixmapTRISTAN.scaled(pMapWidth, pMapHeight, 
                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.lblTRISTAN_Logo.setPixmap(pixmapTRISTAN)

        pixmapUoL = QPixmap(UNI_OF_LEEDS_LOGO)
        pMapWidth = pixmapUoL.width() * 0.75
        pMapHeight = pixmapUoL.height() * 0.75
        pixmapUoL = pixmapUoL.scaled(pMapWidth, pMapHeight, 
                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.lblUoL_Logo.setPixmap(pixmapUoL)
       
        layout.addWidget(self.lblModelImage)
        layout.addWidget(self.lblModelName)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        # Create horizontal layout box to hold TRISTAN & University of Leeds Logos
        horizontalLogoLayout = QHBoxLayout()
        horizontalLogoLayout.setAlignment(QtCore.Qt.AlignRight)
        # Add horizontal layout to bottom of the vertical layout
        layout.addLayout(horizontalLogoLayout)
        # Add labels displaying logos to the horizontal layout, 
        # Tristan on the LHS, UoL on the RHS
        horizontalLogoLayout.addWidget(self.lblFERRET_Logo)
        horizontalLogoLayout.addWidget(self.lblTRISTAN_Logo)
        horizontalLogoLayout.addWidget(self.lblUoL_Logo)

    def ApplyStyleSheet(self):
        """Modifies the appearance of the GUI using CSS instructions"""
        try:
            self.setStyleSheet(StyleSheet.TRISTAN_GREY)
            logger.info('Style Sheet applied.')
        except Exception as e:
            print('Error in function ApplyStyleSheet: ' + str(e))
            logger.error('Error in function ApplyStyleSheet: ' + str(e))

    def DisplayModelImage(self):
        """This method takes the name of the model from the 
            drop-down list on the left-hand side of the GUI 
            and displays the corresponding image depicting 
            the model and the full name of the model at the
            top of the right-hand side of the GUI.
            
            Both the name of the image file and the full name
            of the model are retrieved from the XML configuration
            file.

            If no image is defined for the model in the XML configuration
            file, then the string 'No image available for this model' is 
            displayed on the GUI.
            """
        try:
            logger.info('Function DisplayModelImage called.')
            shortModelName = str(self.cmbModels.currentText())
        
            if shortModelName != 'Select a model':
                # A model has been selected
                imageName = self.objXMLReader.getImageName(shortModelName)
                if imageName:
                    imagePath = IMAGE_FOLDER + imageName
                    pixmapModelImage = QPixmap(imagePath)
                    # Increase the size of the model image
                    pMapWidth = pixmapModelImage.width() * 1.15
                    pMapHeight = pixmapModelImage.height() * 1.15
                    pixmapModelImage = pixmapModelImage.scaled(pMapWidth, pMapHeight, 
                          QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    self.lblModelImage.setPixmap(pixmapModelImage)
                    logger.info('Image {} displayed.'.format(imageName))
                    longModelName = self.objXMLReader.getLongModelName(shortModelName)
                    self.lblModelName.setText(longModelName)
                else:
                    logger.info('Function DisplayModelImage - No image available for this model')
                    self.lblModelImage.clear()
                    self.lblModelName.setText('No image available for this model')
            else:
                self.lblModelImage.clear()
                self.lblModelName.setText('')

        except Exception as e:
            print('Error in function DisplayModelImage: ' + str(e)) 
            logger.error('Error in function DisplayModelImage: ' + str(e))  

    def OptimumParameterChanged(self):
        """Sets boolean self.isCurveFittingDone to false if the 
        plot of the model curve is changed by manually changing the values of 
        model input parameters rather than by running curve fitting.
        
        Also, clears the labels that display the optimum value of each 
        parameter and its confidence inteval."""

        self.isCurveFittingDone=False
        self.clearOptimisedParamaterList('Function-OptimumParameterChanged')

    def CurveFitSetConfIntLabel(self, paramNumber):
        """Called by the CurveFitProcessOptimumParameters function,
        this function populates the label that displays the 
        upper and lower confidence limits for each calculated 
        optimum parameter value.

        Where necessary decimal fractions are converted to % and the
        corresponding value in the global list self.optimisedParamaterList
        is updated, which is also the source of this data.

        Upto 5 model input parameters can be displayed on the GUI.  
        For each parameter there is a spinbox displaying its value,
        a checkbox to indicate if this parameter should have its 
        value remain fixed during curve fitting and a label to display
        the upper and lower 95% confidence limits of the parameter value
        determined during curve fitting.
        Checking the checkbox, fixes the parameter's value during
        curve fitting.

        This trio of widgets follows a set naming convention.
        spinBoxParameter1, ckbParameter1 and lblParam1 refer
        to the first parameter; spinBoxParameter2, 
        ckbParameter2 and lblParam2 refer to the second parameter
        and so on. This set naming convention allows objects 
        corresponding to this trio of widgets for a given parameter
        to be created using the getattr function. 

        Inputs
        ------
        paramNumber - Ordinal number of the parameter, takes values 1-5
        """
        logger.info('Function CurveFitSetConfIntLabel called ' +
                   'with paramNumber={}'.format(paramNumber))
        try:
            objSpinBox = getattr(self, 'spinBoxParameter' + str(paramNumber))
            objCheckBox = getattr(self, 'ckbParameter' + str(paramNumber))
            objLabel = getattr(self, 'lblParam' + str(paramNumber) + 'ConfInt')
            index = paramNumber - 1
            parameterValue = self.optimisedParamaterList[index][0]
            lowerLimit = self.optimisedParamaterList[index][1]
            upperLimit = self.optimisedParamaterList[index][2]
            if objSpinBox.suffix() == '%':
                # Convert decimal fraction to a percentage
                parameterValue = parameterValue * 100.0
                if not objCheckBox.isChecked():
                    lowerLimit = lowerLimit * 100.0
                    upperLimit = upperLimit * 100.0
        
            parameterValue = round(parameterValue, 3)
            if not objCheckBox.isChecked():
                lowerLimit = round(lowerLimit, 2)
                upperLimit = round(upperLimit, 2)
            # For display in the PDF report, 
            # overwrite decimal volume fraction values 
            # in  self.optimisedParamaterList with the % equivalent
            self.optimisedParamaterList[index][0] = parameterValue
            self.optimisedParamaterList[index][1] = lowerLimit
            self.optimisedParamaterList[index][2] = upperLimit
           
            if not objCheckBox.isChecked():
                # Display 95% confidence limits on the GUI
                confidenceStr = '[{}  {}]'.format(lowerLimit, upperLimit)
                objLabel.setText(confidenceStr)

        except Exception as e:
            print('Error in function CurveFitSetConfIntLabel with paramNumber={} index={}'.format(paramNumber, index) + str(e))
            logger.error('Error in function CurveFitSetConfIntLabel with paramNumber={} index={}'.format(paramNumber, index) + str(e))


    def CurveFitProcessOptimumParameters(self):
        """Displays the confidence limits for the optimum 
           parameter values resulting from curve fitting 
           on the right-hand side of the GUI."""
        try:
            logger.info('Function CurveFitProcessOptimumParameters called.')
            self.lblConfInt.show()
            self.lblFix.show()
            self.lblPhysParams.show()
            modelName = str(self.cmbModels.currentText())
            numParams = self.objXMLReader.getNumberOfParameters(modelName)
            if numParams >= 1:
                self.CurveFitSetConfIntLabel(1)
            if numParams >= 2:
                self.CurveFitSetConfIntLabel(2)
            if numParams >= 3:
                self.CurveFitSetConfIntLabel(3)
            if numParams >= 4:
                self.CurveFitSetConfIntLabel(4)
            if numParams >= 5:
                self.CurveFitSetConfIntLabel(5)
            
        except Exception as e:
            print('Error in function CurveFitProcessOptimumParameters: ' + str(e))
            logger.error('Error in function CurveFitProcessOptimumParameters: ' + str(e))

    def ClearOptimumParamaterConfLimitsOnGUI(self):
        """Clears the contents of the labels on the left 
        handside of the GUI that display parameter value
        confidence limits resulting from curve fitting. """
        try:
            logger.info('Function ClearOptimumParamaterConfLimitsOnGUI called.')
            
            self.lblParam1ConfInt.clear()
            self.lblParam2ConfInt.clear()
            self.lblParam3ConfInt.clear()
            self.lblParam4ConfInt.clear()
            self.lblParam5ConfInt.clear()
        except Exception as e:
            print('Error in function ClearOptimumParamaterConfLimitsOnGUI: ' + str(e))
            logger.error('Error in function ClearOptimumParamaterConfLimitsOnGUI: ' + str(e))
    

    def SaveCSVFile(self, fileName=""):
        """Saves in CSV format the data in the plot on the GUI """ 
        try:
            logger.info('Function SaveCSVFile called.')
            modelName = str(self.cmbModels.currentText())
            modelName.replace(" ", "-")

            if not fileName:
                # Ask the user to specify the path & name of the CSV file. The name of the model is suggested as a default file name.
                CSVFileName, _ = QFileDialog.getSaveFileName(self, caption="Enter CSV file name", directory=DEFAULT_PLOT_DATA_FILE_PATH_NAME, filter="*.csv")
            else:
               CSVFileName = fileName

           # Check that the user did not press Cancel on the
           # create file dialog
            if CSVFileName:
                logger.info('Function SaveCSVFile - csv file name = ' + 
                            CSVFileName)
            
                ROI = str(self.cmbROI.currentText())
                AIF = str(self.cmbAIF.currentText())
                if self.cmbVIF.isVisible():
                    VIF = str(self.cmbVIF.currentText())
                    mustIncludeVIF = True
                else:
                    mustIncludeVIF = False

                # If CSVFileName already exists, delete it
                if os.path.exists(CSVFileName):
                    os.remove(CSVFileName)

                with open(CSVFileName, 'w',  newline='') as csvfile:
                    writeCSV = csv.writer(csvfile,  delimiter=',')
                    if mustIncludeVIF:
                        # write header row
                        writeCSV.writerow(['Time (min)', ROI, AIF, VIF, modelName + ' model'])
                        # Write rows of data
                        for i, time in enumerate(self.signalData['time']):
                            writeCSV.writerow([time, self.signalData[ROI][i], self.signalData[AIF][i], self.signalData[VIF][i], self.listModel[i]])
                    else:
                        # write header row
                        writeCSV.writerow(['Time (min)', ROI, AIF, modelName + ' model'])
                        # Write rows of data
                        for i, time in enumerate(self.signalData['time']):
                            writeCSV.writerow([time, self.signalData[ROI][i], self.signalData[AIF][i], self.listModel[i]])
                    csvfile.close()

        except csv.Error:
            print('CSV Writer error in function SaveCSVFile: file %s, line %d: %s' % (CSVFileName, WriteCSV.line_num, csv.Error))
            logger.error('CSV Writer error in function SaveCSVFile: file %s, line %d: %s' % (CSVFileName, WriteCSV.line_num, csv.Error))
        except IOError as IOe:
            print ('IOError in function SaveCSVFile: cannot open file ' + CSVFileName + ' or read its data: ' + str(IOe))
            logger.error ('IOError in function SaveCSVFile: cannot open file ' + CSVFileName + ' or read its data; ' + str(IOe))
        except RuntimeError as re:
            print('Runtime error in function SaveCSVFile: ' + str(re))
            logger.error('Runtime error in function SaveCSVFile: ' + str(re))
        except Exception as e:
            print('Error in function SaveCSVFile: ' + str(e) + ' at line in CSV file ', WriteCSV.line_num)
            logger.error('Error in function SaveCSVFile: ' + str(e) + ' at line in CSV file ', WriteCSV.line_num)

    def clearOptimisedParamaterList(self, callingControl: str):
        """Clears results of curve fitting from the GUI 
        and from the global list self.optimisedParamaterList """
        try:
            logger.info('clearOptimisedParamaterList called from ' + callingControl)
            self.optimisedParamaterList.clear()
            self.ClearOptimumParamaterConfLimitsOnGUI()
        except Exception as e:
            print('Error in function clearOptimisedParamaterList: ' + str(e)) 
            logger.error('Error in function clearOptimisedParamaterList: ' + str(e))

    def display_FitModel_SaveCSV_SaveReport_Buttons(self):
        """Displays the Fit Model, Save CSV and Save PFD Report
       buttons if both a ROI & AIF are selected.  
       Otherwise hides them."""
        try:
            # Hide buttons then display them if appropriate
            self.btnFitModel.hide()
            self.btnSaveCSV.hide()
            self.btnSaveReport.hide()
            self.groupBoxBatchProcessing.hide()
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())
            modelName = str(self.cmbModels.currentText())
            modelInletType = self.objXMLReader.getModelInletType(modelName)
            logger.info("Function display_FitModel_SaveCSV_SaveReport_Buttons called. Model is " + modelName)
            if modelInletType == 'single':
                if ROI != 'Please Select' and AIF != 'Please Select':
                    self.btnFitModel.show()
                    self.btnSaveCSV.show()
                    self.btnSaveReport.show()
                    self.groupBoxBatchProcessing.show() 
                    logger.info("Function display_FitModel_SaveCSV_SaveReport_Buttons called when ROI = {} and AIF = {}".format(ROI, AIF))
            elif modelInletType == 'dual':
                if ROI != 'Please Select' and AIF != 'Please Select' and VIF != 'Please Select' :
                    self.btnFitModel.show()
                    self.btnSaveCSV.show()
                    self.btnSaveReport.show()
                    self.groupBoxBatchProcessing.show() 
                    logger.info("Function display_FitModel_SaveCSV_SaveReport_Buttons called when ROI = {}, AIF = {} & VIF ={}".format(ROI, AIF, VIF)) 
        
        except Exception as e:
            print('Error in function display_FitModel_SaveCSV_SaveReport_Buttons: ' + str(e))
            logger.error('Error in function display_FitModel_SaveCSV_SaveReport_Buttons: ' + str(e))


    def GetSpinBoxValue(self, paramNumber, initialParametersArray):
        """
        Gets the value in a parameter spinbox. 
        Converts a % to a decimal fraction if necessary. 
        This value is then appended to the array, initialParametersArray.
        """
        logger.info('Function GetSpinBoxValue called when paramNumber={} and initialParametersArray={}.'
                    .format(paramNumber,initialParametersArray))
        try:
            objSpinBox = getattr(self, 'spinBoxParameter' + str(paramNumber))
            parameter = objSpinBox.value()
            if objSpinBox.suffix() == '%':
                # This is a volume fraction so convert % to a decimal fraction
                parameter = parameter/100.0
            initialParametersArray.append(parameter)

        except Exception as e:
            print('Error in function GetSpinBoxValue: ' + str(e))
            logger.error('Error in function GetSpinBoxValue: ' + str(e))
    
    def BuildParameterArray(self) -> List[float]:
        """Forms a 1D array of model input parameters
        for input to the modle function.  
            
            Returns
            -------
                A list of model input parameter values.
            """
        try:
            logger.info('Function BuildParameterArray called.')
            initialParametersArray = []

            modelName = str(self.cmbModels.currentText())
            numParams = self.objXMLReader.getNumberOfParameters(modelName)

            if numParams >= 1:
                self.GetSpinBoxValue(1, initialParametersArray)
            if numParams >= 2:
                self.GetSpinBoxValue(2, initialParametersArray)
            if numParams >= 3:
                self.GetSpinBoxValue(3, initialParametersArray)
            if numParams >= 4:
                self.GetSpinBoxValue(4, initialParametersArray)
            if numParams >= 5:
                self.GetSpinBoxValue(5, initialParametersArray)

            return initialParametersArray
        except Exception as e:
            print('Error in function BuildParameterArray ' + str(e))
            logger.error('Error in function BuildParameterArray '  + str(e))


    def SetParameterSpinBoxValue(self, paramNumber, parameterList):
        """
        Sets the value of an individual parameter spinbox.  If necessary
        converts a decimal fraction to a %.
        """
        logger.info('Function SetParameterSpinBoxValue called.')
        try:
            objSpinBox = getattr(self, 'spinBoxParameter' + 
                                 str(paramNumber))
            objSpinBox.blockSignals(True)
            index = paramNumber - 1
            if objSpinBox.suffix() == '%':
                objSpinBox.setValue(parameterList[index] * 100) 
            else:
                objSpinBox.setValue(parameterList[index])
            objSpinBox.blockSignals(False)

        except Exception as e:
            print('Error in function SetParameterSpinBoxValue ' + str(e))
            logger.error('Error in function SetParameterSpinBoxValue '  + str(e))


    def SetParameterSpinBoxValues(self, parameterList):
        """Sets the value displayed in the model parameter spinboxes 
           to the calculated optimum model parameter values.
        
        Input Parameters
        ----------------
            parameterList - Array of optimum model input parameter values.
        """
        try:
            logger.info('Function SetParameterSpinBoxValues called with parameterList = {}'.format(parameterList))
           
            modelName = str(self.cmbModels.currentText())
            numParams = self.objXMLReader.getNumberOfParameters(modelName)

            if numParams >= 1:
                self.SetParameterSpinBoxValue(1, parameterList)
            if numParams >= 2:
                self.SetParameterSpinBoxValue(2, parameterList)
            if numParams >= 3:
                self.SetParameterSpinBoxValue(3, parameterList)
            if numParams >= 4:
                self.SetParameterSpinBoxValue(4, parameterList)
            if numParams >= 5:
                self.SetParameterSpinBoxValue(5, parameterList)
            
        except Exception as e:
            print('Error in function SetParameterSpinBoxValues ' + str(e))
            logger.error('Error in function SetParameterSpinBoxValues '  + str(e))


    def CurveFitCalculate95ConfidenceLimits(self, numDataPoints: int, 
                                            numParams: int, 
                                            optimumParams, 
                                            paramCovarianceMatrix):
        """Calculates the 95% confidence limits of optimum 
        parameter values resulting from curve fitting. 
        Results are stored in global self.optimisedParamaterList 
        that is used in the creation of the PDF report
        and to display results on the GUI.
        
        Input Parameters
        ----------------
        numDataPoints -  Number of data points to which the model is fitted.
                Taken as the number of elements in the array of ROI data.
        numParams - Number of model input parameters.
        optimumParams - Array of optimum model input parameter values 
                        resulting from curve fitting.
        paramCovarianceMatrix - The estimated covariance of 
                the values in optimumParams calculated during 
                curve fitting.
        """
        try:
            logger.info('Function CurveFitCalculate95ConfidenceLimits called: numDataPoints ={}, numParams={}, optimumParams={}, paramCovarianceMatrix={}'
                        .format(numDataPoints, numParams, optimumParams, paramCovarianceMatrix))
            alpha = 0.05 # 95% confidence interval = 100*(1-alpha)
            originalOptimumParams = optimumParams.copy()
            originalNumParams = numParams

            # Check for fixed parameters.
            # Removed fixed parameters from the optimum parameter list
            # as they should not be included in the calculation of
            # confidence limits
            for paramNumber in range(1, len(optimumParams)+ 1):
                # Make parameter checkbox
                objCheckBox = getattr(self, 'ckbParameter' + str(paramNumber))
                if objCheckBox.isChecked():
                    numParams -=1
                    del optimumParams[paramNumber - (originalNumParams - numParams)]
                    
            numDegsOfFreedom = max(0, numDataPoints - numParams) 
        
            # student-t value for the degrees of freedom and the confidence level
            tval = t.ppf(1.0-alpha/2., numDegsOfFreedom)
        
            # Remove results of previous curve fitting
            self.optimisedParamaterList.clear()
            # self.optimisedParamaterList is a list of lists. 
            # Add an empty list for each parameter to hold its value 
            # and confidence limits
            for i in range(numParams):
                self.optimisedParamaterList.append([])
           
            for counter, numParams, var in zip(range(numDataPoints), optimumParams, np.diag(paramCovarianceMatrix)):
                # Calculate 95% confidence interval for each parameter 
                # allowed to vary and add these to a list
                sigma = var**0.5
                lower = numParams - sigma*tval
                upper = numParams + sigma*tval
                self.optimisedParamaterList[counter].append(numParams)
                self.optimisedParamaterList[counter].append(lower)
                self.optimisedParamaterList[counter].append(upper)
                logger.info('Just added value {}, lower {}, upper {} to self.optimisedParamaterList at position{}'
                            .format(numParams, lower, upper, counter))
            
            # Now insert fixed parameters into _optimisedParameterList
            # if there are any.
            for index in range(originalNumParams):
                objCheckBox = getattr(self, 'ckbParameter' + str(index + 1))
                if objCheckBox.isVisible() and objCheckBox.isChecked():
                    # Add the fixed optimum parameter value to a list
                    fixedParamValue = originalOptimumParams[index]
                    lower = ''
                    upper = ''
                    tempList = [fixedParamValue, lower, upper]
                    # Now add this list to the list of lists 
                    self.optimisedParamaterList.insert(index, tempList)
                    logger.info('Just added temp list {} to self.optimisedParamaterList at position{}'
                            .format(tempList, index))
            
            logger.info('Leaving CurveFitCalculate95ConfidenceLimits, self.optimisedParamaterList = {}'.format(self.optimisedParamaterList))
        except RuntimeError as rte:
            print('Runtime Error in function CurveFitCalculate95ConfidenceLimits ' + str(rte))
            logger.error('Runtime Error in function CurveFitCalculate95ConfidenceLimits '  + str(rte))  
        except Exception as e:
            print('Error in function CurveFitCalculate95ConfidenceLimits ' + str(e))
            logger.error('Error in function CurveFitCalculate95ConfidenceLimits '  + str(e))  
    

    def CurveFitGetParameterData(self, modelName, paramNumber):
        """
        Returns a tuple containing all data associated with a parameter
        as required by lmfit curve fitting; namely,
        (parameter name, parameter value, fix parameter value (True/False),
        minimum value, maximum value, expression, step size)

        expression & step size are set to None.

        Input Parameters
        ----------------
        modelName  - Short name of the selected model.
        paramNumber - Number, 1-5, of the parameter.
        """

        logger.info('Function CurveFitGetParameterData called with modelName={} and paramNumber={}.'
                        .format(modelName, paramNumber))
        try:
            paramShortName =self.objXMLReader.getParameterShortName(modelName, paramNumber)
            isPercentage, _ =self.objXMLReader.getParameterLabel(modelName, paramNumber)
            upper = self.objXMLReader.getUpperParameterConstraint(modelName, paramNumber)
            lower = self.objXMLReader.getLowerParameterConstraint(modelName, paramNumber)
            objSpinBox = getattr(self, 'spinBoxParameter' + str(paramNumber))
            value = objSpinBox.value()
            
            if isPercentage:
                value = value/100
            
            vary = True    
            objCheckBox = getattr(self, 'ckbParameter' + str(paramNumber))
            if objCheckBox.isChecked():
                vary = False
            
            tempTuple = (paramShortName, value, vary, lower, upper, None, None)
            
            return tempTuple
        except Exception as e:
            print('Error in function CurveFitGetParameterData: ' + str(e) )
            logger.error('Error in function CurveFitGetParameterData: ' + str(e) )


    def CurveFitCollateParameterData(self)-> List[float]:
        """Forms a 1D array of model input parameters to 
        be used as input to curve fitting.  
            
            Returns
            -------
                A list of model input parameter values 
                for curve fitting.
            """
        try:
            logger.info('Function CurveFitCollateParameterData called.')
            parameterDataList = []

            modelName = str(self.cmbModels.currentText())
            numParams = self.objXMLReader.getNumberOfParameters(modelName)

            if numParams >= 1:
                parameterDataList.append(
                    self.CurveFitGetParameterData(modelName, 1))
            if numParams >= 2:
                parameterDataList.append(
                    self.CurveFitGetParameterData(modelName, 2))
            if numParams >= 3:
                parameterDataList.append(
                    self.CurveFitGetParameterData(modelName, 3))
            if numParams >= 4:
                parameterDataList.append(
                    self.CurveFitGetParameterData(modelName, 4))
            if numParams >= 5:
                parameterDataList.append(
                    self.CurveFitGetParameterData(modelName, 5))

            return parameterDataList
        except Exception as e:
            print('Error in function CurveFitCollateParameterData ' + str(e))
            logger.error('Error in function CurveFitCollateParameterData '  + str(e))

    def CurveFit(self):
        """Performs curve fitting to fit AIF (and VIF) data 
        to the ROI curve.  Then displays the optimum model 
        input parameters on the GUI and calls 
        the plot function to display the line of best fit 
        on the graph on the GUI
        when these parameter values are input to the selected model.
        Also, takes results from curve fitting (optimal parameter values) 
        and determines their 95% confidence limits which are 
        stored in the global list self.optimisedParamaterList.
        """
        try:
            # Form inputs to the curve fitting function
            paramList = self.CurveFitCollateParameterData()
            constantsString = self.objXMLReader.getStringOfConstants()
            
            # Get name of region of interest, arterial and venal input functions
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())

            # Get arrays of data corresponding to the above 3 regions 
            # and the time over which the measurements were made.
            arrayTimes = np.array(self.signalData['time'], 
                                  dtype='float')
            array_ROI_MR_Signals = np.array(self.signalData[ROI], 
                                     dtype='float')
            array_AIF_MR_Signals = np.array(self.signalData[AIF], 
                                     dtype='float')

            if VIF != 'Please Select':
                array_VIF_MR_Signals = np.array(self.signalData[VIF], 
                                         dtype='float')
            else:
                # Create empty dummy array to act as place holder in  
                # ModelFunctionsHelper.CurveFit function call 
                array_VIF_MR_Signals = []
            
            # Get the name of the model to be fitted to the ROI curve
            modelName = str(self.cmbModels.currentText())
            moduleName = self.objXMLReader.getModuleName(modelName)
            if moduleName is None:
                raise NoModuleDefined
            functionName = self.objXMLReader.getFunctionName(modelName)
            if functionName is None:
                raise NoModelFunctionDefined

            inletType = self.objXMLReader.getModelInletType(modelName)
            if inletType is None:
                raise NoModelInletTypeDefined

            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            optimumParamsDict, paramCovarianceMatrix = \
                ModelFunctionsHelper.CurveFit(
                functionName, moduleName, paramList, arrayTimes, 
                array_AIF_MR_Signals, array_VIF_MR_Signals, array_ROI_MR_Signals,
                inletType, constantsString)
            
            self.isCurveFittingDone = True 
            QApplication.restoreOverrideCursor()
            logger.info('ModelFunctionsHelper.CurveFit returned optimum parameters {}'
                        .format(optimumParamsDict))
            
            # Display results of curve fitting  
            # (optimum model parameter values) on GUI.
            optimumParamsList = list(optimumParamsDict.values())
            self.ClearOptimumParamaterConfLimitsOnGUI()
            self.SetParameterSpinBoxValues(optimumParamsList)

            # Plot the best curve on the graph
            self.plotMRSignals('CurveFit')

            # Determine 95% confidence limits.
            numDataPoints = array_ROI_MR_Signals.size
            numParams = len(optimumParamsList)
            if paramCovarianceMatrix.size:
                self.CurveFitCalculate95ConfidenceLimits(numDataPoints, numParams, 
                                    optimumParamsList, paramCovarianceMatrix)
                self.CurveFitProcessOptimumParameters()
        
        except NoModelInletTypeDefined:
            warningString = 'Cannot procede because no inlet type ' + \
                'is defined for this model in the configuration file.'
            print(warningString)
            logger.info('CurveFit - ' + warningString)
            QMessageBox().critical( self,  "Curve Fitting", warningString, QMessageBox.Ok)
        except NoModelFunctionDefined:
            warningString = 'Cannot procede because no function ' + \
                'is defined for this model in the configuration file.'
            print(warningString)
            logger.info('CurveFit - ' + warningString)
            QMessageBox().critical( self,  "Curve Fitting", warningString, QMessageBox.Ok)
        except NoModuleDefined:
            warningString = 'Cannot procede because no module ' + \
                'is defined for this model function in the configuration file.'
            print(warningString)
            logger.info('CurveFit - ' + warningString)
            QMessageBox().critical( self,  "Curve Fitting", warningString, QMessageBox.Ok)
        except ValueError as ve:
            print ('Value Error: CurveFit with model ' + modelName + ': '+ str(ve))
            logger.error('Value Error: CurveFit with model ' + modelName + ': '+ str(ve))
        except Exception as e:
            print('Error in function CurveFit with model ' + modelName + ': ' + str(e))
            logger.error('Error in function CurveFit with model ' + modelName + ': ' + str(e))
    

    def GetValuesForEachParameter(self, paramNumber, 
                    confidenceLimitsArray, parameterDictionary):
        """Called by the function, BuildParameterDictionary, for each
        parameter spinbox, this function builds a list containing the
        spinbox value and the upper and lower confidence limits (if
        curve fitting has just been done). This list is then added
        to the dictionary, parameterDictionary as the value with the
        full parameter name as the key.  
        
         Inputs
         ------
         paramNumber - Ordinal number of the parameter on the GUI, which number
                    from 1 (top) to 5 (bottom).
         confidenceLimitsArray - An array of upper and lower confidence limits
                    for the optimum value of each model parameter obtained
                    after curve fitting.  
        """
        try:
            logger.info('Function GetValuesForEachParameter called when paramNumber={}.'
                        .format(paramNumber))
            parameterList = []
            index = paramNumber - 1
            objLabel = getattr(self, 'labelParameter' + str(paramNumber))
            objSpinBox = getattr(self, 'spinBoxParameter' + str(paramNumber))
            if confidenceLimitsArray != None:
                # curve fitting has just been done
                parameterList.append(confidenceLimitsArray[index][0]) # Parameter Value
                parameterList.append(confidenceLimitsArray[index][1]) # Lower Limit
                parameterList.append(confidenceLimitsArray[index][2]) # Upper Limit
            else:
                # Curve fitting has not just been done
                parameterList.append(round(objSpinBox.value(), 2))
                parameterList.append('N/A')
                parameterList.append('N/A')
            
            parameterDictionary[objLabel.text()] = parameterList

        except Exception as e:
            print('Error in function GetValuesForEachParameter with model: ' + str(e))
            logger.error('Error in function GetValuesForEachParameter with model: ' + str(e))

    def BuildParameterDictionary(self, confidenceLimitsArray = None):
        """Builds a dictionary of values and their confidence limits 
        (if curve fitting is performed) for each model input parameter 
        (dictionary key). This dictionary is used to build a 
        parameter values table used to create the PDF report.  
        It orders the input parameters in the same 
       vertical order as the parameters on the GUI, top to bottom.
       
       Inputs
       ------
       confidenceLimitsArray - An array of upper and lower confidence limits
                    for the optimum value of each model parameter obtained
                    after curve fitting.  If curve fitting has not just
                    been performed then the default value of None is passed
                    into this function. 
       """
        try:
            logger.info('BuildParameterDictionary called with confidence limits array = {}'
                        .format(confidenceLimitsArray))
            parameterDictionary = {}
            modelName = str(self.cmbModels.currentText())
            numParams = self.objXMLReader.getNumberOfParameters(modelName)

            if numParams >= 1:
                self.GetValuesForEachParameter(1,
                    confidenceLimitsArray, parameterDictionary)
            if numParams >= 2:
                self.GetValuesForEachParameter(2,
                    confidenceLimitsArray, parameterDictionary)
            if numParams >= 3:
                self.GetValuesForEachParameter(3,
                    confidenceLimitsArray, parameterDictionary)
            if numParams >= 4:
                self.GetValuesForEachParameter(4,
                    confidenceLimitsArray, parameterDictionary)
            if numParams >= 5:
                self.GetValuesForEachParameter(5,
                    confidenceLimitsArray, parameterDictionary)
           
            return parameterDictionary
    
        except Exception as e:
            print('Error in function BuildParameterDictionary: ' + str(e))
            logger.error('Error in function BuildParameterDictionary: ' + str(e))


    def CreatePDFReport(self, reportFileName=""):
        """Creates and saves a report of model fitting in PDF format. 
        It includes the name of the model, the current values
        of its input parameters and a copy of the current plot.
        
        Input Parameter:
        ****************
            reportFileName - file path and name of the PDF file 
            in which the report will be saved.
            Used during batch processing.

        Return:
        -------
            parameterDict - A dictionary of parameter short name:value pairs
                used during batch processing to create the overall results
                summary, in an Excel spreadsheet, from all the data input files.
        """
        try:
            pdf = PDF(REPORT_TITLE, FERRET_LOGO) 
            
            if not reportFileName:
                # Ask the user to specify the path & name of PDF report. 
                # A default report name is suggested, 
                # see the Constant declarations at the top of this file
                reportFileName, _ = QFileDialog.getSaveFileName(self, caption="Enter PDF file name", 
                                                                directory=DEFAULT_REPORT_FILE_PATH_NAME, 
                                                                filter="*.pdf")

            if reportFileName:
                # If the user has entered the name of a new file, 
                # then we will have to add the .pdf extension
                # If the user has decided to overwrite an existing file, 
                # then will not have to add the .pdf extension
                name, ext = os.path.splitext(reportFileName)
                if ext != '.pdf':
                    # Need to add .pdf extension to reportFileName
                    reportFileName = reportFileName + '.pdf'
                if os.path.exists(reportFileName):
                    # delete existing copy of PDF called reportFileName
                    os.remove(reportFileName) 
                    
                shortModelName = self.cmbModels.currentText()
                longModelName = self.objXMLReader.getLongModelName(shortModelName)

                # Save a png of the concentration/time plot for display 
                # in the PDF report.
                self.figure.savefig(fname=IMAGE_NAME, dpi=150)  # dpi=150 so as to get a clear image in the PDF report
                
                if self.isCurveFittingDone:
                    parameterDict = self.BuildParameterDictionary(self.optimisedParamaterList)
                else:
                    parameterDict = self.BuildParameterDictionary()
                             
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))

                pdf.CreateAndSavePDFReport(reportFileName, self.dataFileName, 
                       longModelName, IMAGE_NAME, parameterDict)
                
                QApplication.restoreOverrideCursor()

                # Delete image file
                os.remove(IMAGE_NAME)
                logger.info('PDF Report created called ' + reportFileName)
                return parameterDict
        except Exception as e:
            print('Error in function CreatePDFReport: ' + str(e))
            logger.error('Error in function CreatePDFReport: ' + str(e))


    def PopulateModelListCombo(self):
        """
        Builds a list of model short names from data in the 
        XML configuration file and adds this list to the 
        cmbModels combo box for display on the GUI.
        """
        try:
            logger.info('Function PopulateModelListCombo called.')
            # Clear the list of models, ready to accept 
            # a new list of models from the XML configuration
            # file just loaded
            self.cmbModels.clear()

            tempList = self.objXMLReader.getListModelShortNames()
            self.cmbModels.blockSignals(True)
            self.cmbModels.addItems(tempList)
            self.cmbModels.blockSignals(False)

        except Exception as e:
            print('Error in function PopulateModelListCombo: ' + str(e))
            logger.error('Error in function PopulateModelListCombo: ' + str(e))


    def LoadConfigFile(self):
        """Loads the contents of an XML file containing model(s) 
        configuration data.  If the XML file parses successfully,
        display the 'Load Data File' button and build the list 
        of model short names."""
        
        try:
            # Clear the existing plot
            self.figure.clear()
            self.figure.set_visible(False)
            self.canvas.draw()
        
            self.HideAllControlsOnGUI()

            #  Get the configuration file in XML format.
            # The filter parameter is set so that the 
            # user can only open an XML file.
            defaultPath = "config\\"
            fullFilePath, _ = QFileDialog.getOpenFileName(parent=self, 
                caption="Select configuration file", 
                directory=defaultPath,
                filter="*.xml")

            if os.path.exists(fullFilePath):
                self.objXMLReader.parseConfigFile(fullFilePath)
                
                if self.objXMLReader.hasXMLFileParsedOK:
                    logger.info('Config file {} loaded'.format(fullFilePath))
                    
                    folderName, configFileName = \
                        os.path.split(fullFilePath)
                    self.statusbar.showMessage('Configuration file ' + configFileName + ' loaded')
                    self.btnLoadDataFile.show()
                    self.PopulateModelListCombo()
                    self.yAxisLabel = self.objXMLReader.getYAxisLabel()
                else:
                    self.btnLoadDataFile.hide()
                    self.HideAllControlsOnGUI()
                    QMessageBox().warning(self, "XML configuration file", "Error reading XML file ", QMessageBox.Ok)
            
        except IOError as ioe:
            print ('IOError in function LoadConfigFile:' + str(ioe))
            logger.error ('IOError in function LoadConfigFile: cannot open file' 
                   + str(ioe))
        except RuntimeError as re:
            print('Runtime error in function LoadConfigFile: ' + str(re))
            logger.error('Runtime error in function LoadConfigFile: ' 
                         + str(re))
        except Exception as e:
            print('Error in function LoadConfigFile: ' + str(e))
            logger.error('Error in function LoadConfigFile: ' + str(e))           


    def LoadDataFile(self):
        """
        Loads the contents of a CSV file containing time 
        and MR signal data into a dictionary of lists. 
        The key is the name of the organ or the word 'time'  
        and the corresponding value is a list of MR signals
        for that organ (or times when the key is 'time').
        
        The following validation is applied to the data file:
            -The CSV file must contain at least 3 columns of data 
                separated by commas.
            -The first column in the CSV file must contain time data.
            -The header of the time column must contain the word 'time'.
        """
        
        # clear the dictionary of previous data
        self.signalData.clear()
        
        self.HideAllControlsOnGUI()
        
        try:
            # Get the data file in csv format.
            # Filter parameter set so that the user can only
            # open a csv file.
            dataFileFolder = self.objXMLReader.getDataFileFolder()
            fullFilePath, _ = QFileDialog.getOpenFileName(parent=self, 
                                                     caption="Select csv file", 
                                                     directory=dataFileFolder,
                                                     filter="*.csv")
            if os.path.exists(fullFilePath):
                with open(fullFilePath, newline='') as csvfile:
                    line = csvfile.readline()
                    if line.count(',') < (MIN_NUM_COLUMNS_CSV_FILE - 1):
                        QMessageBox().warning(self, 
                          "CSV data file", 
                          "The CSV file must contain at least 3 columns of data separated by commas.  The first column must contain time data.", 
                          QMessageBox.Ok)
                        raise RuntimeError('The CSV file must contain at least 3 columns of data separated by commas.')
                    
                    # Go back to top of the file
                    csvfile.seek(0)
                    readCSV = csv.reader(csvfile, delimiter=',')
                    # Get column header labels
                    # Returns the headers or `None` if the input is empty
                    headers = next(readCSV, None)  
                    if headers:
                        firstColumnHeader = headers[0].strip().lower()
                        if 'time' not in firstColumnHeader:
                            QMessageBox().warning(self, 
                               "CSV data file", 
                               "The first column must contain time data.", 
                               QMessageBox.Ok)
                            raise RuntimeError('The first column in the CSV file must contain time data.')    

                    logger.info('CSV data file {} loaded'.format(fullFilePath))
                    
                    folderName = os.path.basename(os.path.dirname(fullFilePath))
                    self.dataFileDirectory, self.dataFileName = os.path.split(fullFilePath)
                    self.statusbar.showMessage('File ' + self.dataFileName + ' loaded')
                    self.lblBatchProcessing.setText("Batch process all CSV data files in folder: " + folderName)
                    
                    # Column headers form the keys in the dictionary 
                    # called self.signalData
                    for header in headers:
                        if 'time' in header.lower():
                            header ='time'
                        self.signalData[header.title().lower()]=[]
                    # Also add a 'model' key to hold a list of concentrations generated by a model
                    self.signalData['model'] = []

                    # Each key in the dictionary is paired 
                    # with a list of corresponding concentrations 
                    # (except the Time key that is paired 
                    # with a list of times)
                    for row in readCSV:
                        colNum=0
                        for key in self.signalData:
                            # Iterate over columns in the selected row
                            if key != 'model':
                                if colNum == 0: 
                                    # time column
                                    self.signalData['time'].append(float(row[colNum])/60.0)
                                else:
                                    self.signalData[key].append(float(row[colNum]))
                                colNum+=1           
                csvfile.close()

                self.NormaliseSignalData()
                self.ConfigureGUIAfterLoadingData()
                
        except csv.Error:
            print('CSV Reader error in function LoadDataFile: file {}, line {}: error={}'.format(self.dataFileName, readCSV.line_num, csv.Error))
            logger.error('CSV Reader error in function LoadDataFile: file {}, line {}: error ={}'.format(self.dataFileName, readCSV.line_num, csv.Error))
        except IOError:
            print ('IOError in function LoadDataFile: cannot open file' + self.dataFileName + ' or read its data')
            logger.error ('IOError in function LoadDataFile: cannot open file' + self.dataFileName + ' or read its data')
        except RuntimeError as re:
            print('Runtime error in function LoadDataFile: ' + str(re))
            logger.error('Runtime error in function LoadDataFile: ' + str(re))
        except Exception as e:
            print('Error in function LoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            logger.error('Error in function LoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            QMessageBox().warning(self, "CSV data file", "Error reading CSV file at line {} - {}".format(readCSV.line_num, e), QMessageBox.Ok)


    def NormaliseSignalData(self):
        """
        This function normalises the MR signal data by dividing
        each data point by the average of the initial baseline
        scans done before the perfusion agent is added to the 
        bloodstream.
        """
        try:
            # Get the number of baseline scans is defined 
            # in the xml configuration file
            numBaseLineScans = self.objXMLReader.getNumBaselineScans()

            for key, signalList in self.signalData.items():
                if key == 'model' or key == 'time':
                    # data from a model is already normalised
                    continue
                
                # Calculate mean baseline for the current 
                # list of signals
                signalBaseline = \
                    sum(signalList[0:numBaseLineScans])/numBaseLineScans

                # Divide each value in the list by the baseline
                signalList[:] = [signal/signalBaseline 
                                 for signal in signalList]
                self.signalData[key] = signalList

        except Exception as e:
            print('Error in function NormaliseSignalData: ' + str(e))
            logger.error('Error in function NormaliseSignalData: ' + str(e))


    def HideAllControlsOnGUI(self):
        """
        Hides/clears all the widgets on left-hand side of the application 
        except for the Load & Display Data and Exit buttons.  
        It is called before a data file is loaded in case the 
        Cancel button on the dialog is clicked.  
        This prevents the scenario where buttons are displayed 
        but there is no data loaded to process when they are clicked.
        """
        logger.info('Function HideAllControlsOnGUI called')
        self.statusbar.clearMessage()
        self.pbar.reset()
        self.lblROI.hide()
        self.cmbROI.hide()
        self.groupBoxModel.hide()
        self.btnSaveReport.hide()
        self.btnFitModel.hide()
        self.btnSaveCSV.hide()
        self.groupBoxBatchProcessing.hide()
        

    def ConfigureGUIAfterLoadingData(self):
        """
        After successfully loading a datafile, 
        this method loads a list of organs into ROI, 
        AIF & VIF drop-down lists and displays 
        the ROI drop-down list.  
        It also clears the Matplotlib graph.
        """
        try:
            # Reset and show the dropdown list of organs
            self.cmbROI.clear()
            self.cmbAIF.clear()
            self.cmbVIF.clear()
            
            # Create a list of organs for which concentrations are
            # provided in the data input file.  See LoadDataFile method.
            organArray = []
            organArray = self.GetListOrgans()
            
            self.cmbROI.addItems(organArray)
            self.cmbAIF.addItems(organArray)
            self.cmbVIF.addItems(organArray)
            self.lblROI.show()
            self.cmbROI.show()

            # Clear the existing plot
            self.figure.clear()
            self.figure.set_visible(False)
            self.canvas.draw()

            logger.info('Function ConfigureGUIAfterLoadingData called and the following organ list loaded: {}'.format(organArray))
        except RuntimeError as re:
            print('runtime error in function ConfigureGUIAfterLoadingData: ' + str(re) )
            logger.error('runtime error in function ConfigureGUIAfterLoadingData: ' + str(re) )
        except Exception as e:
            print('Error in function ConfigureGUIAfterLoadingData: ' + str(e) )
            logger.error('Error in function ConfigureGUIAfterLoadingData: ' + str(e))
     
            
    def GetListOrgans(self):
        """Builds a list of organs from the headers in the CSV data file. 
        The CSV data file comprises columns of concentration data for a
        set of organs.  Each column of concentration data is labeled with
        a header giving the name of organ.
        
        Returns
        -------
            A list of organs for which there is concentration data.
        """
        try:
            logger.info('Function GetListOrgans called')
            organList =[]
            organList.append('Please Select') #First item at the top of the drop-down list
            for key in self.signalData:
                if key.lower() != 'time' and key.lower() != 'model':  
                    organList.append(str(key))
                    
            return organList

        except RuntimeError as re:
            print('runtime error in function GetListOrgans' + str(re))
            logger.error('runtime error in function GetListOrgans' + str(re))
        except Exception as e:
            print('Error in function GetListOrgans: ' + str(e))
            logger.error('Error in function GetListOrgans: ' + str(e))
    

    def UncheckFixParameterCheckBoxes(self):
        """Uncheckes all the fix parameter checkboxes."""
        logger.info('Function UncheckFixParameterCheckBoxes called')
        self.ckbParameter1.blockSignals(True)
        self.ckbParameter2.blockSignals(True)
        self.ckbParameter2.blockSignals(True)
        self.ckbParameter3.blockSignals(True)
        self.ckbParameter5.blockSignals(True)

        self.ckbParameter1.setChecked(False)
        self.ckbParameter2.setChecked(False)
        self.ckbParameter2.setChecked(False)
        self.ckbParameter3.setChecked(False)
        self.ckbParameter5.setChecked(False)
        
        self.ckbParameter1.blockSignals(False)
        self.ckbParameter2.blockSignals(False)
        self.ckbParameter2.blockSignals(False)
        self.ckbParameter3.blockSignals(False)
        self.ckbParameter5.blockSignals(False)


    def populateParameterLabelAndSpinBox(self, modelName, paramNumber):
        """
        When a model is selected, this function is called.  
        Each model may have upto 5 parameters.  Parameter labels,
        parameter spinboxes and fix parameter checkboxes already exist
        on the form but are hidden. The naming convention of these
        widgets follows a fixed pattern. For the parameter label, this
        is 'labelParameter' followed by a suffix 1, 2, 3, 4 or 5.
        For the parameter spinbox, this is 'spinBoxParameter' 
        followed by a suffix 1, 2, 3, 4 or 5.  For the checkbox
        that indicates if a parameter should be constrainted during
        curve fitting this is 'ckbParameter' followed by a 
        suffix 1, 2, 3, 4 or 5.

        This functions creates and configures the parameter label,
        spinbox and checkbox for a given parameter according to the
        data in the xml configuration file.

        Input Parameters
        ----------------
        modelName  - Short name of the selected model.
        paramNumber - Number, 1-5, of the parameter.
        """
        
        try:
            logger.info('Function populateParameterLabelAndSpinBox called with modelName={}, paramNumber={}'
                        .format(modelName, paramNumber))
            isPercentage, paramName =self.objXMLReader.getParameterLabel(modelName, paramNumber)
            precision = self.objXMLReader.getParameterPrecision(modelName, paramNumber)
            upper = self.objXMLReader.getMaxParameterDisplayValue(modelName, paramNumber)
            lower = self.objXMLReader.getMinParameterDisplayValue(modelName, paramNumber)
            step = self.objXMLReader.getParameterStep(modelName, paramNumber)
            default = self.objXMLReader.getParameterDefault(modelName, paramNumber)
        
            objLabel = getattr(self, 'labelParameter' + str(paramNumber))
            objLabel.setText(paramName)
            objLabel.show()
            
            objSpinBox = getattr(self, 'spinBoxParameter' + str(paramNumber))
            objSpinBox.blockSignals(True)
            objSpinBox.setDecimals(precision)
            objSpinBox.setRange(lower, upper)
            objSpinBox.setSingleStep(step)
            objSpinBox.setValue(default)
            if isPercentage:
                objSpinBox.setSuffix('%')
            else:
                objSpinBox.setSuffix('')
            objSpinBox.blockSignals(False)
            objSpinBox.show()

            objCheckBox = getattr(self, 'ckbParameter' + str(paramNumber))
            objCheckBox.setChecked(False)
            objCheckBox.show()

        except Exception as e:
            print('Error in function populateParameterLabelAndSpinBox: ' + str(e) )
            logger.error('Error in function populateParameterLabelAndSpinBox: ' + str(e) )


    def SetParameterSpinBoxToDefault(self, modelName, paramNumber):
        """Resets the value of a parameter spinbox to the default
        stored in the XML configuration file. 
        
        Input Parameters
        ----------------
        modelName  - Short name of the selected model.
        paramNumber - Number, 1-5, of the parameter.
        """
        try:
            logger.info(
                'SetParameterSpinBoxToDefault called with paramNumber=' 
                + str(paramNumber))
            default = self.objXMLReader.getParameterDefault(modelName, paramNumber)
        
            objSpinBox = getattr(self, 'spinBoxParameter' + str(paramNumber))
            objSpinBox.blockSignals(True)
            objSpinBox.setValue(default)
            objSpinBox.blockSignals(False)
            
        except Exception as e:
            print('Error in function populateParameterLabelAndSpinBox: ' + str(e) )
            logger.error('Error in function populateParameterLabelAndSpinBox: ' + str(e) )


    def InitialiseParameterSpinBoxes(self):
        """
        Initialises all the parameter spinbox vales 
        for the selected model by coordinating the 
        calling of the function SetParameterSpinBoxToDefault 
        for each parameter spinbox. """
        try:
            modelName = str(self.cmbModels.currentText())
            logger.info(
                'Function InitialiseParameterSpinBoxes called when model = ' 
                + modelName)

            numParams = self.objXMLReader.getNumberOfParameters(modelName)
            if numParams >= 1:
                self.SetParameterSpinBoxToDefault(modelName, 1)
            if numParams >= 2:
                self.SetParameterSpinBoxToDefault(modelName, 2)
            if numParams >= 3:
                self.SetParameterSpinBoxToDefault(modelName, 3)
            if numParams >= 4:
                self.SetParameterSpinBoxToDefault(modelName, 4)
            if numParams >= 5:
                self.SetParameterSpinBoxToDefault(modelName, 5)

        except Exception as e:
            print('Error in function InitialiseParameterSpinBoxes: ' + str(e) )
            logger.error('Error in function InitialiseParameterSpinBoxes: ' + str(e) )


    def SetUpParameterLabelsAndSpinBoxes(self):
        """Coordinates the calling of function
       populateParameterLabelAndSpinBox to set up and show the 
       parameter spinboxes for each model"""
        logger.info('Function SetUpParameterLabelsAndSpinBoxes called. ')
        try:
            modelName = str(self.cmbModels.currentText())
            numParams = self.objXMLReader.getNumberOfParameters(modelName)
            if numParams >= 1:
                self.populateParameterLabelAndSpinBox(modelName, 1)
            if numParams >= 2:
                self.populateParameterLabelAndSpinBox(modelName, 2)
            if numParams >= 3:
                self.populateParameterLabelAndSpinBox(modelName, 3)
            if numParams >= 4:
                self.populateParameterLabelAndSpinBox(modelName, 4)
            if numParams >= 5:
                self.populateParameterLabelAndSpinBox(modelName, 5)

        except Exception as e:
            print('Error in function SetUpParameterLabelsAndSpinBoxes: ' + str(e) )
            logger.error('Error in function SetUpParameterLabelsAndSpinBoxes: ' + str(e) )


    def ClearAndHideParameterLabelsSpinBoxesAndCheckBoxes(self):
        self.spinBoxParameter1.hide()
        self.spinBoxParameter2.hide()
        self.spinBoxParameter3.hide()
        self.spinBoxParameter4.hide()
        self.spinBoxParameter5.hide()
        self.spinBoxParameter1.clear()
        self.spinBoxParameter2.clear()
        self.spinBoxParameter3.clear()
        self.spinBoxParameter4.clear()
        self.spinBoxParameter5.clear()
        self.labelParameter1.clear()
        self.labelParameter2.clear()
        self.labelParameter3.clear()
        self.labelParameter4.clear()
        self.labelParameter5.clear()
        self.ckbParameter1.hide()
        self.ckbParameter2.hide()
        self.ckbParameter3.hide()
        self.ckbParameter4.hide()
        self.ckbParameter5.hide()
        self.ckbParameter1.setChecked(False)
        self.ckbParameter2.setChecked(False)
        self.ckbParameter3.setChecked(False)
        self.ckbParameter4.setChecked(False)
        self.ckbParameter5.setChecked(False)


    def ConfigureGUIForEachModel(self):
        """When a model is selected, this method configures 
        the appearance of the GUI accordingly.  
        For example, spinboxes for the input of model parameter 
        values are given an appropriate label."""
        try:
            modelName = str(self.cmbModels.currentText())
            logger.info('Function ConfigureGUIForEachModel called when model = ' + modelName)   
            #self.cboxDelay.show()
            #self.cboxConstaint.show()
            #self.cboxConstaint.setChecked(False)
            self.btnReset.show()
            self.btnSaveReport.show()
            self.pbar.reset()
            self.ClearAndHideParameterLabelsSpinBoxesAndCheckBoxes()
            
            ##Configure parameter spinboxes and their labels for each model
            if modelName == 'Select a model':
                self.lblAIF.hide()
                self.cmbAIF.hide()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.cboxDelay.hide()
                self.cboxConstaint.hide()
                self.btnReset.hide()
                self.cmbAIF.setCurrentIndex(0)
                self.cmbVIF.setCurrentIndex(0)
                self.btnFitModel.hide()
                self.btnSaveReport.hide()
                self.btnSaveCSV.hide()
                self.groupBoxBatchProcessing.hide()
                self.lblConfInt.hide()
                self.lblFix.hide()
                self.lblPhysParams.hide()
            else:
                self.SetUpParameterLabelsAndSpinBoxes()
                self.lblConfInt.show()
                self.lblFix.show()
                self.lblPhysParams.show()
                self.lblAIF.show() #Common to all models
                self.cmbAIF.show() #Common to all models
                inletType = self.objXMLReader.getModelInletType(modelName)
                if inletType == 'single':
                    self.lblVIF.hide()
                    self.cmbVIF.hide()
                    self.cmbVIF.setCurrentIndex(0)
                elif inletType == 'dual':
                    self.lblVIF.show()
                    self.cmbVIF.show()

        except Exception as e:
            print('Error in function ConfigureGUIForEachModel: ' + str(e) )
            logger.error('Error in function ConfigureGUIForEachModel: ' + str(e) )
           
            
    def GetScreenResolution(self):
        """Determines the screen resolution of the device 
        running this software.
        
        Returns
        -------
            Returns the width & height of the device screen in pixels.
        """
        try:
            width, height = pyautogui.size()
            logger.info('Function GetScreenResolution called. Screen width = {}, height = {}.'.format(width, height))
            return width, height
        except Exception as e:
            print('Error in function GetScreenResolution: ' + str(e) )
            logger.error('Error in function GetScreenResolution: ' + str(e) )
        

    def DetermineTextSize(self):
        """Determines the optimum size for the title & labels on the 
           matplotlib graph from the screen resolution.
           
           Returns
           -------
              tick label size, xy axis label size & title size
           """
        try:
            logger.info('Function DetermineTextSize called.')
            width, _ = self.GetScreenResolution()
            
            if width == 1920: #Desktop
                tickLabelSize = 12
                xyAxisLabelSize = 14
                titleSize = 20
            elif width == 2560: #Laptop
                tickLabelSize = 16
                xyAxisLabelSize = 18
                titleSize = 24
            else:
                tickLabelSize = 12
                xyAxisLabelSize = 14
                titleSize = 20

            return tickLabelSize, xyAxisLabelSize, titleSize
        except Exception as e:
            print('Error in function DetermineTextSize: ' + str(e) )
            logger.error('Error in function DetermineTextSize: ' + str(e) )
    

    def plotModelCurve(self, modelName, 
                       inletType,
                       arrayTimes, 
                       array_AIF_MR_Signals, 
                       array_VIF_MR_Signals, objSubPlot):
        """
        This function calls the function that calculates the 
        MR signal/time curve using the selected model and then
        plots this curve on the matplotlib plot.

        Inputs
        ------
        modelName - short name of the select model
        inletType - inlet type of the model, single or dual
        arrayTimes - array of time points over which the
                MR signal data is recorded.
        array_AIF_MR_Signals - array of AIF MR signal data over
                the time period stored in arrayTimes.
        array_VIF_MR_Signals - array of VIF MR signal data over
                the time period stored in arrayTimes.
        objSubPlot - object pointing to the matplotlib plot.
        """
        try:
            parameterArray = self.BuildParameterArray()
            constantsString = self.objXMLReader.getStringOfConstants()
            modelFunctionName = self.objXMLReader.getFunctionName(modelName)
            moduleName = self.objXMLReader.getModuleName(modelName)

            logger.info('ModelFunctionsHelper.ModelSelector called when model={}, function ={} & parameter array = {}'. format(modelName, modelFunctionName, parameterArray))        
            
            self.listModel = ModelFunctionsHelper.ModelSelector(
                        modelFunctionName, moduleName,
                        inletType, arrayTimes, array_AIF_MR_Signals, 
                        parameterArray, constantsString,
                        array_VIF_MR_Signals)
            
            arrayModel =  np.array(self.listModel, dtype='float')
            objSubPlot.plot(arrayTimes, arrayModel, 'g--', label= modelName + ' model')
            
        except Exception as e:
                print('Error in function plotModelCurve ' + str(e) )
                logger.error('Error in function plotModelCurve ' + str(e) )
    

    def setUpPlot(self):
        """
        This function draws the matplotlib plot on the GUI
        for the display of the MR signal/time curves.
        """
        try:
            logger.info('Function setUpPlot called.')
            self.figure.clear()
            self.figure.set_visible(True)
        
            objSubPlot = self.figure.add_subplot(111)

            # Get the optimum label size for the screen resolution.
            tickLabelSize, xyAxisLabelSize, titleSize = \
                self.DetermineTextSize()

            # Set size of the x,y axis tick labels
            objSubPlot.tick_params(axis='both', 
                                   which='major', 
                                   labelsize=tickLabelSize)

            objSubPlot.set_xlabel('Time (mins)', fontsize=xyAxisLabelSize)
            objSubPlot.set_ylabel(self.yAxisLabel, fontsize=xyAxisLabelSize)
            objSubPlot.set_title('Time Curves', fontsize=titleSize, pad=25)
            objSubPlot.grid()

            return objSubPlot

        except Exception as e:
                print('Error in function setUpPlot: ' + str(e))
                logger.error('Error in function setUpPlot: ' + str(e))


    def setUpLegendBox(self, objPlot):
        """
        This function draws the legend box holding the key
        to the MR signal/time curves on the plot.
        """
        logger.info('Function setUpLegendBox called.')
        chartBox = objPlot.get_position()
        objPlot.set_position([chartBox.x0*1.1, chartBox.y0, 
                              chartBox.width*0.9, chartBox.height])
        objPlot.legend(loc='upper center', 
                       bbox_to_anchor=(0.9, 1.0), 
                       shadow=True, ncol=1, fontsize='x-large')


    def plotMRSignals(self, nameCallingFunction: str):
        """If a Region of Interest has been selected, 
        this function plots the normalised signal against time curves 
        for the ROI, AIF, VIF.  
        Also, plots the normalised signal/time curve predicted by the 
        selected model.
        
        Input Parameter
        ----------------
        nameCallingFunction - Name of the function or widget from whose event 
        this function is called. This information is used in logging and error
        handling.
        """
        try:
            boolAIFSelected = False
            boolVIFSelected = False

            objPlot = self.setUpPlot()

            # Get the names of the regions 
            # selected from the drop down lists.
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            VIF = 'Not Selected'
            VIF = str(self.cmbVIF.currentText())

            logger.info('Function plot called from ' +
                        nameCallingFunction + 
                        ' when ROI={}, AIF={} and VIF={}'.format(ROI, AIF, VIF))

            arrayTimes = np.array(self.signalData['time'], dtype='float')
            
            if AIF != 'Please Select':
                array_AIF_MR_Signals = np.array(self.signalData[AIF], dtype='float')
                objPlot.plot(arrayTimes, array_AIF_MR_Signals, 'r.-', label= AIF)
                boolAIFSelected = True

            array_VIF_MR_Signals = []
            if VIF != 'Please Select':
                array_VIF_MR_Signals = np.array(self.signalData[VIF], dtype='float')
                objPlot.plot(arrayTimes, array_VIF_MR_Signals, 'k.-', label= VIF)
                boolVIFSelected = True
                    
            # Plot concentration curve from the model
            modelName = str(self.cmbModels.currentText())
            if modelName != 'Select a model':
                inletType = self.objXMLReader.getModelInletType(modelName)
                if (inletType == 'dual') and \
                    (boolAIFSelected and boolVIFSelected) \
                    or \
                    (inletType == 'single') and boolAIFSelected:
                    self.plotModelCurve(modelName, inletType,
                                        arrayTimes, 
                                        array_AIF_MR_Signals, 
                                       array_VIF_MR_Signals, objPlot)

            if ROI != 'Please Select':
                array_ROI_MR_Signals = np.array(self.signalData[ROI], dtype='float')
                objPlot.plot(arrayTimes, array_ROI_MR_Signals, 'b.-', label= ROI)
                
                self.setUpLegendBox(objPlot)
                
                # Refresh canvas
                self.canvas.draw()
            else:
                # Draw a blank graph on the canvas
                self.canvas.draw

        except Exception as e:
                print('Error in function plotMRSignals when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
                logger.error('Error in function plotMRSignals when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
    

    def ExitApp(self):
        """Closes the Model Fitting application."""
        logger.info("Application closed using the Exit button.")
        sys.exit(0)  


    def toggleEnabled(self, boolEnabled=False):
        """Used to disable all the controls on the form 
        during batch processing and to enable them again 
        when batch processing is complete."""
        self.btnExit.setEnabled(boolEnabled)
        self.btnLoadDataFile.setEnabled(boolEnabled)
        self.cmbROI.setEnabled(boolEnabled)
        self.cmbAIF.setEnabled(boolEnabled)
        self.cmbVIF.setEnabled(boolEnabled)
        self.btnSaveReport.setEnabled(boolEnabled)
        self.btnExit.setEnabled(boolEnabled)
        self.cmbModels.setEnabled(boolEnabled)
        self.btnReset.setEnabled(boolEnabled)
        self.btnFitModel.setEnabled(boolEnabled)
        self.btnSaveCSV.setEnabled(boolEnabled)
        self.spinBoxParameter1.setEnabled(boolEnabled)
        self.spinBoxParameter2.setEnabled(boolEnabled) 
        self.spinBoxParameter3.setEnabled(boolEnabled) 
        self.spinBoxParameter4.setEnabled(boolEnabled) 
        self.spinBoxParameter5.setEnabled(boolEnabled)
        self.btnBatchProc.setEnabled(boolEnabled)
        self.ckbParameter1.setEnabled(boolEnabled)
        self.ckbParameter2.setEnabled(boolEnabled)
        self.ckbParameter2.setEnabled(boolEnabled)
        self.ckbParameter3.setEnabled(boolEnabled)
        self.ckbParameter5.setEnabled(boolEnabled)
        

    def BatchProcessAllCSVDataFiles(self):
        """
       When a CSV data file is selected, the path to its folder is saved.
       This function processes all the CSV data files in that folder by 
       performing curve fitting using the selected model. 
       
       The results for each data file are written to an Excel spreadsheet.  
       If a CSV file cannot be read then its name is also recorded in the 
       Excel spreadsheet together with the reason why it could not be read.
       
       As each data file is processed, a PDF report with a plot of the 
       time/concentration curves is generated and stored in a sub-folder 
       in the folder where the data files are held.  Likewise, a CSV file
       holding the time and concentration data (including the model curve)
       in the is created in another sub-folder in the folder where the 
       data files are held."""
        try:
            
            logger.info('Function BatchProcessAllCSVDataFiles called.')
            
            # Create a list of csv files in the selected directory
            csvDataFiles = [file 
                            for file in os.listdir(self.dataFileDirectory) 
                            if file.lower().endswith('.csv')]

            numCSVFiles = len(csvDataFiles)

            self.lblBatchProcessing.clear()
            self.lblBatchProcessing.setText('{}: {} csv files.'
                                       .format(self.dataFileDirectory, str(numCSVFiles)))

            # Make nested folders to hold CSV files 
            # of plot data and PDF reports
            csvPlotDataFolder = self.dataFileDirectory + '/CSVPlotDataFiles'
            pdfReportFolder = self.dataFileDirectory + '/PDFReports'
            if not os.path.exists(csvPlotDataFolder):
                os.makedirs(csvPlotDataFolder)
                logger.info('BatchProcessAllCSVDataFiles: {} created.'.format(csvPlotDataFolder))
            if not os.path.exists(pdfReportFolder):
                os.makedirs(pdfReportFolder)
                logger.info('BatchProcessAllCSVDataFiles: {} created.'.format(pdfReportFolder))
            
            # Set up progress bar
            self.pbar.show()
            self.pbar.setMaximum(numCSVFiles)
            self.pbar.setValue(0)
        
            boolUseParameterDefaultValues = True
            # If the user has changed one or more parameter values
            # ask if they still wish to use the parameter default valuesSet
            # or the values they have selected.
            if self.BatchProcessingHaveParamsChanged():
                buttonReply = QMessageBox.question(self, 'Parameter values changed.', 
                       "As initial values, do you wish to use to use the new parameter values (Yes) or the default values (No)?", QMessageBox.Yes | QMessageBox.No, 
                       QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    logger.info('BatchProcessAllCSVDataFiles: Using new parameter values')
                    boolUseParameterDefaultValues = False
                    #Store new parameter values
                    initialParameterArray = self.BuildParameterArray()
                else:
                    logger.info('BatchProcessAllCSVDataFiles: Using default parameter values')

            self.toggleEnabled(False)
            QApplication.processEvents()
            # Counter to show progress of batch processing in 
            # progress bar.
            count = 0  

            modelName = str(self.cmbModels.currentText())

            # Create the Excel spreadsheet to record the results
            objSpreadSheet, boolExcelFileCreatedOK = self.BatchProcessingCreateBatchSummaryExcelSpreadSheet(self.dataFileDirectory)
            
            if boolExcelFileCreatedOK:
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                for file in csvDataFiles:
                    if boolUseParameterDefaultValues:
                        self.InitialiseParameterSpinBoxes() #Reset default values
                    else:
                        # Reset parameters to values selected by the user before
                        # the start of batch processing
                        self.SetParameterSpinBoxValues(initialParameterArray)

                    # Set class instance property dataFileName 
                    # to name of file in current iteration 
                    #  this variable used to write datafile 
                    #  in the PDF report
                    self.dataFileName = str(file) 
                    self.statusbar.showMessage('File ' + self.dataFileName + ' loaded.')
                    count +=1
                    self.lblBatchProcessing.setText("Processing {}".format(self.dataFileName))
                    # Load current file
                    fileLoadedOK, failureReason = self.BatchProcessingLoadDataFile(self.dataFileDirectory + '/' + self.dataFileName)
                    if not fileLoadedOK:
                        objSpreadSheet.recordSkippedFiles(self.dataFileName, failureReason)
                        self.pbar.setValue(count)
                        continue  # Skip this iteration if problems loading file
                
                    self.plotMRSignals('BatchProcessAllCSVDataFiles') #Plot data                
                    self.CurveFit() # Fit curve to model 
                    self.SaveCSVFile(csvPlotDataFolder + '/plot' + file) #Save plot data to CSV file               
                    parameterDict = self.CreatePDFReport(pdfReportFolder + '/' + os.path.splitext(file)[0]) #Save PDF Report                
                    self.BatchProcessWriteOptimumParamsToSummary(objSpreadSheet, 
                               self.dataFileName,  modelName, parameterDict)
                    self.pbar.setValue(count)
                    QApplication.processEvents()

                self.lblBatchProcessing.setText("Batch processing complete.")
                QApplication.restoreOverrideCursor()
                self.toggleEnabled(True)
                objSpreadSheet.saveSpreadSheet()

        except Exception as e:
            print('Error in function BatchProcessAllCSVDataFiles: ' + str(e) )
            logger.error('Error in function BatchProcessAllCSVDataFiles: ' + str(e) )
            QApplication.restoreOverrideCursor()
            self.toggleEnabled(True)     


    def BatchProcessingCreateBatchSummaryExcelSpreadSheet(self, 
                                                pathToFolder):
        """Creates an Excel spreadsheet to hold a summary of model 
        fitting a batch of data files
        
        Input
        -----
           pathToFolder - location of the folder holding the 
                MR signal data
        
        """ 
        try:
            boolExcelFileCreatedOK = True
            logger.info('Function BatchProcessingCreateBatchSummaryExcelSpreadSheet called.')

            #Ask the user to specify the path & name of the Excel spreadsheet file. 
            ExcelFileName, _ = QFileDialog.getSaveFileName(self, caption="Batch Summary Excel file name", 
                           directory=pathToFolder + "//BatchSummary", filter="*.xlsx")

           #Check that the user did not press Cancel on the create file dialog
            if not ExcelFileName:
                ExcelFileName = pathToFolder + "//BatchSummary.xlsx"
           
            logger.info('Function BatchProcessingCreateBatchSummaryExcelSpreadSheet - Excel file name = ' + ExcelFileName)

            #If ExcelFileName already exists, delete it
            if os.path.exists(ExcelFileName):
                os.remove(ExcelFileName)
            
            #Create spreadsheet object
            spreadSheet = ExcelWriter(ExcelFileName, FERRET_LOGO)
            
            return spreadSheet, boolExcelFileCreatedOK

        except OSError as ose:
            logger.error (ExcelFileName + 'is open. It must be closed. Error =' + str(ose))
            QMessageBox.warning(self, 'Spreadsheet open in Excel', 
                       "Close the batch summary spreadsheet and try again", 
                       QMessageBox.Ok, 
                       QMessageBox.Ok)
            self.toggleEnabled(True)
            boolExcelFileCreatedOK = False
            return None, boolExcelFileCreatedOK
        except RuntimeError as re:
            print('Runtime error in function BatchProcessingCreateBatchSummaryExcelSpreadSheet: ' + str(re))
            logger.error('Runtime error in function BatchProcessingCreateBatchSummaryExcelSpreadSheet: ' + str(re))
            self.toggleEnabled(True)
            boolExcelFileCreatedOK = False
            return None, boolExcelFileCreatedOK
        except Exception as e:
            print('Error in function BatchProcessingCreateBatchSummaryExcelSpreadSheet: ' + str(e))
            logger.error('Error in function BatchProcessingCreateBatchSummaryExcelSpreadSheet: ' + str(e))    
            self.toggleEnabled(True)
            boolExcelFileCreatedOK = False
            return None, boolExcelFileCreatedOK


    def BatchProcessWriteOptimumParamsToSummary(self, 
                                                objExcelFile, 
                                                fileName, 
                                                modelName, 
                                                paramDict):
        """During batch processing of data files, writes 
        the optimum parameter values resulting from  
       curve fitting to Excel spreadsheet.
       
       Inputs
       -----
       objExcelFile - object instanciated from the XMLReader class
       fileName - Name of the MR Signal data file currently being
            batch processed.
       modelName - Name of the model being used for curve fitting.
       paramDict - Dictionary of optimum parameter values determined
            by the curve fitting process
       """
        try:
            for paramName, paramList in paramDict.items(): 
                paramName.replace('\n', '')
                paramName.replace(',', '')
                paramName = "'" + paramName + "'"
                value = str(round(paramList[0],3))
                lower = paramList[1]
                upper = paramList[2]
                objExcelFile.recordParameterValues(fileName, modelName, paramName, value, lower, upper)
                
        except Exception as e:
            print('Error in function BatchProcessWriteOptimumParamsToSummary: ' + str(e))
            logger.error('Error in function BatchProcessWriteOptimumParamsToSummary: ' + str(e))
            self.toggleEnabled(True)      


    def BatchProcessingLoadDataFile(self, fullFilePath):
        """ 
        Loads the contents of a CSV file containing time and concentration data
        into a dictionary of lists. The key is the name of the organ or 'time' and 
        the corresponding value is a list of concentrations 
        (or times when the key is 'time')
        
        The following validation is applied to the data file:
            -The CSV file must contain at least 3 columns of data separated by commas.
            -The first column in the CSV file must contain time data.
            -The header of the time column must contain the word 'time'.
       
        Input Parameters:
        ******************
            fullFilePath - Full file path to a CSV file containing 
                            time/concentration data    
        """
      
        # clear the dictionary of previous data
        self.signalData.clear()

        boolFileFormatOK = True
        boolDataOK = True
        failureReason = ""
        
        try:
            if os.path.exists(fullFilePath):
                with open(fullFilePath, newline='') as csvfile:
                    line = csvfile.readline()
                    if line.count(',') < (MIN_NUM_COLUMNS_CSV_FILE - 1):
                        boolFileFormatOK = False
                        failureReason = "At least 3 columns of data are expected"
                        errorStr = 'Batch Processing: CSV file {} must acontain at least 3 columns of data separated by commas.'.format(fullFilePath)
                        logger.info(errorStr)
                        
                    # Go back to top of the file
                    csvfile.seek(0)
                    readCSV = csv.reader(csvfile, delimiter=',')
                    # Get column header labels
                    headers = next(readCSV, None)  # returns the headers or `None` if the input is empty
                    if headers:
                        join = ""
                        firstColumnHeader = headers[0].strip().lower()
                        if 'time' not in firstColumnHeader:
                            boolFileFormatOK = False
                            if len(failureReason) > 0:
                                join = " and "
                            failureReason = failureReason + join + \
                           "First column must contain time data, with the word 'time' as a header"
                            errorStr = 'Batch Processing: The first column in {} must contain time data.'.format(fullFilePath)
                            logger.info(errorStr)
                      
                        boolDataOK, dataFailureReason = self.BatchProcessingCheckAllInputDataPresent(headers)
                        if not boolDataOK:
                            if len(failureReason) > 0:
                                join = " and "
                            failureReason = failureReason + join + dataFailureReason
                            boolFileFormatOK = False

                    if boolFileFormatOK:
                        # Column headers form the keys in the dictionary called self.signalData
                        for header in headers:
                            if 'time' in header:
                                header ='time'
                            self.signalData[header.title().lower()]=[]
                        # Also add a 'model' key to hold a list of concentrations generated by a model
                        self.signalData['model'] = []

                        # Each key in the dictionary is paired with a 
                        # list of corresponding concentrations 
                        # (except the Time key that is paired with a list of times)
                        for row in readCSV:
                            colNum=0
                            for key in self.signalData:
                                # Iterate over columns in the selected row
                                if key != 'model':
                                    if colNum == 0: 
                                        # time column
                                        self.signalData['time'].append(float(row[colNum])/60.0)
                                    else:
                                        self.signalData[key].append(float(row[colNum]))
                                    colNum+=1           
                        logger.info('Batch Processing: CSV data file {} loaded OK'.format(fullFilePath))
            self.NormaliseSignalData()
            return boolFileFormatOK, failureReason
        
        except csv.Error:
            boolFileFormatOK = False
            print('CSV Reader error in function BatchProcessingLoadDataFile: file {}, line {}: error={}'.format(self.dataFileName, readCSV.line_num, csv.Error))
            logger.error('CSV Reader error in function BatchProcessingLoadDataFile: file {}, line {}: error ={}'.format(self.dataFileName, readCSV.line_num, csv.Error))
        except IOError:
            boolFileFormatOK = False
            print ('IOError in function BatchProcessingLoadDataFile: cannot open file' + self.dataFileName + ' or read its data')
            logger.error ('IOError in function BatchProcessingLoadDataFile: cannot open file' + self.dataFileName + ' or read its data')
        except RuntimeError as re:
            boolFileFormatOK = False
            print('Runtime error in function BatchProcessingLoadDataFile: ' + str(re))
            logger.error('Runtime error in function BatchProcessingLoadDataFile: ' + str(re))
        except Exception as e:
            boolFileFormatOK = False
            print('Error in function BatchProcessingLoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            logger.error('Error in function BatchProcessingLoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            failureReason = "Error reading CSV file at line {} - {}".format(readCSV.line_num, e)
        finally:
            self.toggleEnabled(True)
            return boolFileFormatOK, failureReason 

    def BatchProcessingCheckAllInputDataPresent(self, headers):
        """This function checks that the current data file contains
        data for the ROI, AIF and, if appropriate, the VIF.
        
        If data is missing, it returns false and a string indicating 
        what data is missing.

        Input
        -----
        headers - A list of the column headers in the MR signal
            CSV data file
        """
        boolDataOK = True
        join = ""
        failureReason = ""
        try:
            lowerCaseHeaders = [header.strip().lower() for header in headers]

            # Check ROI data is in the current data file
            ROI = str(self.cmbROI.currentText().strip().lower())
            if ROI not in (lowerCaseHeaders):
                boolDataOK = False
                failureReason = ROI + " data missing"
            
            # Check AIF data is in the current data file
            AIF = str(self.cmbAIF.currentText().strip().lower())
            if AIF not in (lowerCaseHeaders):
                boolDataOK = False
                if len(failureReason) > 0:
                    join = " and "
                failureReason = failureReason + join + AIF + " data missing"

            if self.cmbVIF.isVisible():
                # Check VIF data is in the current data file
                VIF = str(self.cmbVIF.currentText().strip().lower())
                if VIF not in (lowerCaseHeaders):
                    boolDataOK = False
                    if len(failureReason) > 0:
                        join = " and "
                    failureReason = failureReason + join + VIF + " data missing"
            
            return boolDataOK, failureReason

        except Exception as e:
            boolDataOK = False
            print('Error in function BatchProcessingCheckAllInputDataPresent: ' + str(e))
            logger.error('Error in function BatchProcessingCheckAllInputDataPresent: ' + str(e))
            failureReason = failureReason + " " + str(e)
            return boolDataOK, failureReason
            self.toggleEnabled(True)

    def BatchProcessingHaveParamsChanged(self) -> bool:
        """Returns True if the user has changed one or more  
        parameter spinbox values from the defaults"""
        try:
            boolParameterChanged = False
            modelName = str(self.cmbModels.currentText())
            logger.info('Function BatchProcessingHaveParamsChanged called when model = ' + modelName)

            if self.spinBoxParameter1.isVisible():
                if (self.spinBoxParameter1.value() != 
                   self.objXMLReader.getParameterDefault(modelName, 1)):
                    boolParameterChanged = True
           
            if self.spinBoxParameter2.isVisible():
                if (self.spinBoxParameter2.value() != 
                   self.objXMLReader.getParameterDefault(modelName, 2)):
                    boolParameterChanged = True
                    
            if self.spinBoxParameter3.isVisible() :
                if (self.spinBoxParameter3.value() != 
                   self.objXMLReader.getParameterDefault(modelName,3)):
                    boolParameterChanged = True  
                    
            if self.spinBoxParameter4.isVisible():
                if (self.spinBoxParameter4.value() != 
                   self.objXMLReader.getParameterDefault(modelName, 4)):
                    boolParameterChanged = True

            if self.spinBoxParameter5.isVisible():
                if (self.spinBoxParameter5.value() != 
                   self.objXMLReader.getParameterDefault(modelName, 5)):
                    boolParameterChanged = True
            
            return boolParameterChanged    
        except Exception as e:
            print('Error in function BatchProcessingHaveParamsChanged: ' + str(e) )
            logger.error('Error in function BatchProcessingHaveParamsChanged: ' + str(e) )
            self.toggleEnabled(True)
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ModelFittingApp()
    main.show()
    sys.exit(app.exec_())
