"""This module is the start up module in the TRISTAN-Model-Fitting application. 
It defines the GUI and the logic providing the application's functionality. 
The GUI was built using PyQT5.

How to Use.
-----------
   The TRISTAN-Model-Fitting application allows the user to analyse organ time/concentration data
   by fitting a model to the Region Of Interest (ROI) time/concentration curve. 
   The TRISTAN-Model-Fitting application provides the following functionality:
        1. Load a CSV file of concentration/time data.  The first column must contain time data 
			in seconds. The remaining columns of data must contain concentration data in 
			millimoles (mM) for individual organs at the time points in the time column. 
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
            are logged to a file called TRISTAN.log, stored at the same location as the 
            source code or executable. This file will used as a debugging aid. 
            When a new instance of the application is started, 
            TRISTAN.log from the last session will be deleted and a new log file started.
        12. Clicking the 'Exit' button closes the application.

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
The function LoadDataFile loads the contents of a CSV file containing time and 
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

As the time data is read, it is divided by 60 in order to convert it into minutes.
        """
__author__ = "Steve Shillitoe, https://www.imagingbiomarkers.org/stephen-shillitoe"
__version__ = "1.0"
__date__ = "Date: 2018/12/12"

import sys
import csv
import os.path
import numpy as np
import pyautogui
import logging
from typing import List

from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QPushButton, QDoubleSpinBox,\
     QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel,  \
     QMessageBox, QFileDialog, QCheckBox, QLineEdit, QSizePolicy, QSpacerItem, \
     QGridLayout, QWidget, QStatusBar, QProgressBar

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from scipy.stats.distributions import  t

class NavigationToolbar(NavigationToolbar):
    """
    Removes unwanted default buttons in the Navigation Toolbar by creating
    a subclass of the NavigationToolbar class from from 
    matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    that only defines the desired buttons
    """
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

#Import module containing model definitions
import TracerKineticModels

#Import CSS file
import StyleSheet

#Import PDF report writer class
from PDFWriter import PDF

#Initialise global dictionary to hold concentration data
_concentrationData={}
#Initialise global list to hold concentrations calculated using the selected model
_listModel = []
#Initialise global string variable to hold the name of the data file.
#Needs to be global for printing in the PDF report
_dataFileName = ''
#Initialise global list that holds results of curve fitting
_optimisedParamaterList = []
#Global boolean that indicates if the curve fitting routine has been just run or not.
#Used by the PDF report writer to determine if displaying confidence limits is appropriate
_boolCurveFittingDone = False

########################################
##              CONSTANTS             ##
########################################
WINDOW_TITLE = 'Model-fitting of dynamic contrast-enhanced MRI'
REPORT_TITLE = 'Model-fitting of dynamic contrast-enhanced MRI'
IMAGE_NAME = 'model.png'
DEFAULT_REPORT_FILE_PATH_NAME = 'report.pdf'
DEFAULT_PLOT_DATA_FILE_PATH_NAME = 'plot.csv'
LOG_FILE_NAME = "TRISTAN.log"
MIN_NUM_COLUMNS_CSV_FILE = 3

#Image Files
TRISTAN_LOGO = 'images\\TRISTAN LOGO.jpg'
LARGE_TRISTAN_LOGO ='images\\logo-tristan.png'
UNI_OF_LEEDS_LOGO ='images\\uni-leeds-logo.jpg'

#Model 1: 2-2CFM
DEFAULT_VALUE_Ve_2_2CFM = 20.0
DEFAULT_VALUE_Fp_2_2CFM = 1.0
DEFAULT_VALUE_Kbh_2_2CFM = 0.017
DEFAULT_VALUE_Khe_2_2CFM = 0.22
#Other models
DEFAULT_VALUE_Ve = 23.0
DEFAULT_VALUE_Kbh = 0.0918
DEFAULT_VALUE_Khe = 2.358
DEFAULT_VALUE_Fp = 0.0001
DEFAULT_VALUE_Vp = 10.0
DEFAULT_VALUE_Vh = 75.0
DEFAULT_VALUE_Vb = 2.0
DEFAULT_VALUE_Ktrans = 0.10
DEFAULT_VALUE_Kce = 0.025
DEFAULT_VALUE_Kbc = 0.003
DEFAULT_VALUE_Fa = 17.0 #Arterial Flow Fraction

LABEL_PARAMETER_Vp = 'Plasma Volume Fraction,\n Vp (%)'
LABEL_PARAMETER_Vh = 'Hepatocyte Volume Fraction,\n Vh (%)'
LABEL_PARAMETER_Vb = 'Intrahepatic Bile Duct Volume Fraction,\n Vb (%)'
LABEL_PARAMETER_Kce = 'Hepatocellular Uptake Rate, \n Kce (mL/100mL/min)'
LABEL_PARAMETER_Ve = 'Extracellular Vol Fraction,\n Ve (%)'
LABEL_PARAMETER_Fp = 'Total Plasma Inflow, \n Fp (mL/min/mL)'
LABEL_PARAMETER_Ktrans = 'Transfer Rate Constant, \n Ktrans (1/min)'
LABEL_PARAMETER_Kbh = 'Biliary Efflux Rate, \n Kbh (mL/min/mL)'
LABEL_PARAMETER_Khe = 'Hepatocyte Uptake Rate, \n Khe (mL/min/mL)'
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

class ModelFittingApp(QWidget):   
    """This class defines the TRISTAN Model Fitting software 
       based on a QDialog window.
       This includes seting up the GUI and defining the methods 
       that are executed when events associated with widgets on
       the GUI are executed."""
    
    def __init__(self, parent=None):
        """Creates the GUI. Controls on the GUI are grouped into 3 vertical
           layout panals placed on a horizontal layout panal.
           The appearance of the widgets is determined by CSS 
           commands in the module styleSheet.py. 
           
           The left-handside vertical layout panal holds widgets for the 
           input of data & the selection of the model to fit to the data.
           
           The middle vertical layout panal holds the graph displaying the
           data and the fitted model.
           
           The right-hand vertical layout panal displays parameter data and
           their confidence limits pertaining to the model fit. 
           
           This method coordinates the calling of methods that set up the 
           widgets on the 3 vertical layout panals."""

        super(ModelFittingApp, self).__init__(parent)
      
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(TRISTAN_LOGO))
        width, height = self.GetScreenResolution()
        self.setGeometry(width*0.05, height*0.05, width*0.9, height*0.9)
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint |  QtCore.Qt.WindowCloseButtonHint)
        self.directory = ""
        self.ApplyStyleSheet()
       
        #Setup the layouts, the containers for widgets
        verticalLayoutLeft, verticalLayoutMiddle, verticalLayoutRight = self.SetUpLayouts()
        
        #Add widgets to the left-hand side vertical layout
        self.SetUpLeftVerticalLayout(verticalLayoutLeft)

        #Set up the graph to plot concentration data on
        # the middle vertical layout
        self.SetUpPlotArea(verticalLayoutMiddle)
        
        #Create a group box and place it in the right-handside vertical layout
        #Also add a label to hold the TRISTAN Logo
        self.SetUpRightVerticalLayout(verticalLayoutRight)

        logger.info("GUI created successfully.")

    def SetUpLayouts(self):
        """Places a horizontal layout on the window
           and places 3 vertical layouts on the horizontal layout.
           
           Returns the 3 vertical layouts to be used by other methods
           that place widgets on them.
           
           Returns
           -------
                Three vertical layouts that have been added to a 
                horizontal layout.
           """

        horizontalLayout = QHBoxLayout()
        verticalLayoutLeft = QVBoxLayout()
        verticalLayoutMiddle = QVBoxLayout()
        verticalLayoutRight = QVBoxLayout()
        
        self.setLayout(horizontalLayout)
        horizontalLayout.addLayout(verticalLayoutLeft,2)
        horizontalLayout.addLayout(verticalLayoutMiddle,3)
        horizontalLayout.addLayout(verticalLayoutRight,2)
        return verticalLayoutLeft, verticalLayoutMiddle, verticalLayoutRight

    def SetUpLeftVerticalLayout(self, layout):
        """
        Creates widgets and places them on the left-handside vertical layout. 
        """
        #Create Load Data File Button
        self.btnLoadDisplayData = QPushButton('Load and display data.')
        self.btnLoadDisplayData.setToolTip('Open file dialog box to select the data file')
        self.btnLoadDisplayData.setShortcut("Ctrl+L")
        self.btnLoadDisplayData.setAutoDefault(False)
        self.btnLoadDisplayData.resize(self.btnLoadDisplayData.minimumSizeHint())
        #Method LoadDataFile is executed in the clicked event of this button
        self.btnLoadDisplayData.clicked.connect(self.LoadDataFile)
        
        #Add a vertical spacer to the top of vertical layout to ensure
        #the top of the Load Data button is level with the MATPLOTLIB toolbar 
        #in the central vertical layout.
        verticalSpacer = QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addItem(verticalSpacer)
        #Add Load data file button to the top of the vertical layout
        layout.addWidget(self.btnLoadDisplayData)
        layout.addItem(verticalSpacer)

        #Create dropdown list for selection of ROI
        self.lblROI = QLabel("Region of Interest:")
        self.lblROI.setAlignment(QtCore.Qt.AlignRight)
        self.cmbROI = QComboBox()
        self.cmbROI.setToolTip('Select Region of Interest')
        self.lblROI.hide()
        self.cmbROI.hide()
        
        #Below Load Data button add ROI list.  It is placed in a 
        #horizontal layout together with its label, so they are
        #aligned in the same row.
        ROI_HorizontalLayout = QHBoxLayout()
        ROI_HorizontalLayout.addWidget(self.lblROI)
        ROI_HorizontalLayout.addWidget(self.cmbROI)
        layout.addLayout(ROI_HorizontalLayout)
        
        #Create a group box to group together widgets associated with
        #the model selected. 
        #It is placed in the left-handside vertical layout
        self.SetUpModelGroupBox(layout, verticalSpacer)
        
        self.btnSaveReport = QPushButton('Save Report in PDF Format')
        self.btnSaveReport.hide()
        self.btnSaveReport.setToolTip('Insert an image of the graph opposite and associated data in a PDF file')
        layout.addWidget(self.btnSaveReport, QtCore.Qt.AlignTop)
        self.btnSaveReport.clicked.connect(self.CreatePDFReport)

        self.SetUpBatchProcessingGroupBox(layout)
        
        layout.addStretch(1)
        self.btnExit = QPushButton('Exit')
        layout.addWidget(self.btnExit)
        self.statusbar = QStatusBar()
        layout.addWidget(self.statusbar)
        self.btnExit.clicked.connect(self.ExitApp)
        

    def SetUpModelGroupBox(self, layout, verticalSpacer):
        """Creates a group box to hold widgets associated with the 
        selection of a model and for inputing/displaying that model's
        parameter data."""
        self.groupBoxModel = QGroupBox('Model Fitting')
        self.groupBoxModel.setAlignment(QtCore.Qt.AlignHCenter)
        #The group box is hidden until a ROI is selected.
        self.groupBoxModel.hide()
        layout.addWidget(self.groupBoxModel)
        #layout.addItem(verticalSpacer)
        
        #Create horizontal layouts, one row of widgets to 
        #each horizontal layout. Then add them to a vertical layout, 
        #then add the vertical layout to the group box
        modelHorizontalLayout2 = QHBoxLayout()
        modelHorizontalLayoutArterialFlowFactor = QHBoxLayout()
        modelHorizontalLayout3 = QHBoxLayout()
        modelHorizontalLayout4 = QHBoxLayout()
        modelHorizontalLayoutReset = QHBoxLayout()
        modelHorizontalLayout5 = QHBoxLayout()
        modelHorizontalLayout6 = QHBoxLayout()
        modelHorizontalLayout7 = QHBoxLayout()
        modelHorizontalLayoutPara4 = QHBoxLayout()
        modelHorizontalLayout8 = QHBoxLayout()
        modelHorizontalLayout9 = QHBoxLayout()
        modelVerticalLayout = QVBoxLayout()
        modelVerticalLayout.setAlignment(QtCore.Qt.AlignTop) 
        modelVerticalLayout.addLayout(modelHorizontalLayout2)
        modelVerticalLayout.addLayout(modelHorizontalLayout3)
        modelVerticalLayout.addLayout(modelHorizontalLayout4)
        modelVerticalLayout.addLayout(modelHorizontalLayoutReset)
        modelVerticalLayout.addLayout(modelHorizontalLayoutArterialFlowFactor)
        modelVerticalLayout.addLayout(modelHorizontalLayout5)
        modelVerticalLayout.addLayout(modelHorizontalLayout6)
        modelVerticalLayout.addLayout(modelHorizontalLayout7)
        modelVerticalLayout.addLayout(modelHorizontalLayoutPara4)
        modelVerticalLayout.addLayout(modelHorizontalLayout8)
        modelVerticalLayout.addLayout(modelHorizontalLayout9)
        self.groupBoxModel.setLayout(modelVerticalLayout)
        
        #Create dropdown list to hold names of models
        self.modelLabel = QLabel("Model:")
        self.modelLabel.setAlignment(QtCore.Qt.AlignRight)
        self.cmbModels = QComboBox()
        self.cmbModels.setToolTip('Select a model to fit to the data')
        #Populate the combo box with names of models in the modelNames list
        #self.cmbModels.addItems(TracerKineticModels.modelNames)
        self.cmbModels.addItems(TracerKineticModels.GetListModels())
        self.cmbModels.setCurrentIndex(0) #Display "Select a Model"
        self.cmbModels.currentIndexChanged.connect(self.DisplayModelImage)
        self.cmbModels.currentIndexChanged.connect(self.ConfigureGUIForEachModel)
        self.cmbModels.currentIndexChanged.connect(lambda: self.ClearOptimisedParamaterList('cmbModels')) 
        self.cmbModels.currentIndexChanged.connect(self.DisplayFitModelSaveCSVButtons)
        self.cmbModels.activated.connect(lambda:  self.PlotConcentrations('cmbModels'))

        #Create dropdown lists for selection of AIF & VIF
        self.lblAIF = QLabel('Arterial Input Function:')
        self.cmbAIF = QComboBox()
        self.cmbAIF.setToolTip('Select Arterial Input Function')
        self.lblVIF = QLabel("Venous Input Function:")
        self.cmbVIF = QComboBox()
       
        self.cmbVIF.setToolTip('Select Venous Input Function')
        #When a ROI is selected plot its concentration data on the graph.
        self.cmbROI.activated.connect(lambda:  self.PlotConcentrations('cmbROI'))
        #When a ROI is selected, then make the Model groupbox and the widgets
        #contains visible.
        self.cmbROI.currentIndexChanged.connect(self.DisplayModelFittingGroupBox)
        #When an AIF is selected plot its concentration data on the graph.
        self.cmbAIF.activated.connect(lambda: self.PlotConcentrations('cmbAIF'))
        #When an AIF is selected display the Fit Model and Save plot CVS buttons.
        self.cmbAIF.currentIndexChanged.connect(self.DisplayFitModelSaveCSVButtons)
        self.cmbVIF.currentIndexChanged.connect(self.DisplayArterialFlowFactorSpinBox)
        self.cmbVIF.currentIndexChanged.connect(self.DisplayFitModelSaveCSVButtons)
        #When a VIF is selected plot its concentration data on the graph.
        self.cmbVIF.activated.connect(lambda: self.PlotConcentrations('cmbVIF'))
        self.lblAIF.hide()
        self.cmbAIF.hide()
        self.lblVIF.hide()
        self.cmbVIF.hide()
        self.cmbROI.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbAIF.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbVIF.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        #Add combo boxes and their labels to the horizontal layouts
        modelHorizontalLayout2.insertStretch (0, 2)
        modelHorizontalLayout2.addWidget(self.modelLabel)
        modelHorizontalLayout2.addWidget(self.cmbModels)
        modelHorizontalLayout3.addWidget(self.lblAIF)
        modelHorizontalLayout3.addWidget(self.cmbAIF)
        modelHorizontalLayout4.addWidget(self.lblVIF)
        modelHorizontalLayout4.addWidget(self.cmbVIF)
        
        self.cboxDelay = QCheckBox('Delay', self)
        self.cboxConstaint = QCheckBox('Constraint', self)
        self.cboxDelay.hide()
        self.cboxConstaint.hide()
        self.btnReset = QPushButton('Reset')
        self.btnReset.setToolTip('Reset parameters to their default values.')
        self.btnReset.hide()
        self.btnReset.clicked.connect(self.InitialiseParameterSpinBoxes)
        #If parameters reset to their default values, replot the concentration and model data
        self.btnReset.clicked.connect(lambda: self.PlotConcentrations('Reset Button'))
        modelHorizontalLayoutReset.addWidget(self.cboxDelay)
        modelHorizontalLayoutReset.addWidget(self.cboxConstaint)
        modelHorizontalLayoutReset.addWidget(self.btnReset)
        
        #Create spinboxes and their labels
        #Label text set in function ConfigureGUIForEachModel when the model is selected
        self.lblArterialFlowFactor = QLabel("Arterial Flow Fraction, \n fa (%):") 
        self.lblArterialFlowFactor.hide()
        self.labelParameter1 = QLabel("")
        self.labelParameter2 = QLabel("")
        self.labelParameter3 = QLabel("")
        self.labelParameter4 = QLabel("")
        self.labelParameter1.setWordWrap(True)
        self.labelParameter2.setWordWrap(True)
        self.labelParameter3.setWordWrap(True)
        self.labelParameter4.setWordWrap(True)

        self.spinBoxArterialFlowFactor = QDoubleSpinBox()
        self.spinBoxArterialFlowFactor.setRange(0, 100)
        self.spinBoxArterialFlowFactor.setDecimals(2)
        self.spinBoxArterialFlowFactor.setSingleStep(0.01)
        self.spinBoxArterialFlowFactor.setValue(DEFAULT_VALUE_Fa)
        self.spinBoxArterialFlowFactor.setSuffix('%')
        self.spinBoxArterialFlowFactor.hide()
        
        self.spinBoxParameter1 = QDoubleSpinBox()
        self.spinBoxParameter2 = QDoubleSpinBox()
        self.spinBoxParameter3 = QDoubleSpinBox()
        self.spinBoxParameter4 = QDoubleSpinBox()
        
        self.spinBoxParameter1.hide()
        self.spinBoxParameter2.hide()
        self.spinBoxParameter3.hide()
        self.spinBoxParameter4.hide()

        #If a parameter value is changed, replot the concentration and model data
        self.spinBoxArterialFlowFactor.valueChanged.connect(lambda: self.PlotConcentrations('spinBoxArterialFlowFactor')) 
        self.spinBoxParameter1.valueChanged.connect(lambda: self.PlotConcentrations('spinBoxParameter1')) 
        self.spinBoxParameter2.valueChanged.connect(lambda: self.PlotConcentrations('spinBoxParameter2')) 
        self.spinBoxParameter3.valueChanged.connect(lambda: self.PlotConcentrations('spinBoxParameter3'))
        self.spinBoxParameter4.valueChanged.connect(lambda: self.PlotConcentrations('spinBoxParameter4'))
        #Set a global boolean variable, _boolCurveFittingDone to false to indicate that 
        #the value of a model parameter has been changed manually rather than by curve fitting
        self.spinBoxArterialFlowFactor.valueChanged.connect(self.SetCurveFittingNotDoneBoolean) 
        self.spinBoxParameter1.valueChanged.connect(self.SetCurveFittingNotDoneBoolean) 
        self.spinBoxParameter2.valueChanged.connect(self.SetCurveFittingNotDoneBoolean) 
        self.spinBoxParameter3.valueChanged.connect(self.SetCurveFittingNotDoneBoolean)
        self.spinBoxParameter4.valueChanged.connect(self.SetCurveFittingNotDoneBoolean)
        
        #Place spin boxes and their labels in horizontal layouts
        modelHorizontalLayoutArterialFlowFactor.addWidget(self.lblArterialFlowFactor)
        modelHorizontalLayoutArterialFlowFactor.addWidget(self.spinBoxArterialFlowFactor)
        modelHorizontalLayout5.addWidget(self.labelParameter1)
        modelHorizontalLayout5.addWidget(self.spinBoxParameter1)
        modelHorizontalLayout6.addWidget(self.labelParameter2)
        modelHorizontalLayout6.addWidget(self.spinBoxParameter2)
        modelHorizontalLayout7.addWidget(self.labelParameter3)
        modelHorizontalLayout7.addWidget(self.spinBoxParameter3)
        modelHorizontalLayoutPara4.addWidget(self.labelParameter4)
        modelHorizontalLayoutPara4.addWidget(self.spinBoxParameter4)
        
        self.btnFitModel = QPushButton('Fit Model')
        self.btnFitModel.setToolTip('Use non-linear least squares to fit the selected model to the data')
        self.btnFitModel.hide()
        modelHorizontalLayout8.addWidget(self.btnFitModel)
        self.btnFitModel.clicked.connect(self.RunCurveFit)
        
        self.btnSaveCSV = QPushButton('Save plot data to CSV file')
        self.btnSaveCSV.setToolTip('Save the data plotted on the graph to a CSV file')
        self.btnSaveCSV.hide()
        modelHorizontalLayout9.addWidget(self.btnSaveCSV)
        self.btnSaveCSV.clicked.connect(self.SaveCSVFile)

    def SetUpBatchProcessingGroupBox(self, layout):
        """Creates a group box to hold widgets associated with batch
        processing functionality."""
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
        """Adds widgets for the display of the graph onto the middle vertical layout."""
        self.figure = plt.figure(figsize=(5, 4), dpi=100)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to its __init__
        self.canvas = FigureCanvas(self.figure)
        
        # this is the Navigation widget
        # it takes the Canvas widget as a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def SetUpRightVerticalLayout(self, layout):
        """Creates and adds widgets to the right hand side vertical layout for the 
        display of the results of curve fitting. """

        #Add a vertical spacer to the top of vertical layout to ensure
        #the top of the group box is level with the MATPLOTLIB toolbar 
        #the central vertical layout.
        verticalSpacer = QSpacerItem(20, 35, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addItem(verticalSpacer)
        layout.addItem(verticalSpacer)

        self.lblModelImage = QLabel(self)
        self.lblModelImage.setAlignment(QtCore.Qt.AlignCenter)
        self.lblModelName = QLabel('')
        self.lblModelName.setAlignment(QtCore.Qt.AlignCenter)
        self.lblModelName.setWordWrap(True)
        layout.addWidget(self.lblModelImage)
        layout.addWidget(self.lblModelName)
        #Create Group Box to contain labels displaying the results of curve fitting
        self.groupBoxResults = QGroupBox('Curve Fitting Results')
        self.groupBoxResults.setAlignment(QtCore.Qt.AlignHCenter)
        layout.addWidget(self.groupBoxResults)
        layout.addStretch()
        #Grid layout to be placed inside the group box
        gridLayoutResults = QGridLayout()
        gridLayoutResults.setAlignment(QtCore.Qt.AlignTop) 
        self.groupBoxResults.setLayout(gridLayoutResults)

        self.lblHeaderLeft = QLabel("Parameter")
        self.lblHeaderMiddle = QLabel("Value")
        self.lblHeaderRight = QLabel("95% Confidence Interval")
        self.lblAFFName = QLabel("")
        self.lblAFFValue = QLabel("")
        self.lblAFFConfInt = QLabel("")
        self.lblAFFConfInt.setAlignment(QtCore.Qt.AlignCenter)
        self.lblParam1Name = QLabel("")
        self.lblParam1Value = QLabel("")
        self.lblParam1ConfInt = QLabel("")
        self.lblParam1ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        self.lblParam2Name = QLabel("")
        self.lblParam2Value = QLabel("")
        self.lblParam2ConfInt = QLabel("")
        self.lblParam2ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        self.lblParam3Name = QLabel("")
        self.lblParam3Value = QLabel("")
        self.lblParam3ConfInt = QLabel("")
        self.lblParam3ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        self.lblParam4Name = QLabel("")
        self.lblParam4Value = QLabel("")
        self.lblParam4ConfInt = QLabel("")
        self.lblParam4ConfInt.setAlignment(QtCore.Qt.AlignCenter)
        
        gridLayoutResults.addWidget(self.lblHeaderLeft, 1, 1)
        gridLayoutResults.addWidget(self.lblHeaderMiddle, 1, 3)
        gridLayoutResults.addWidget(self.lblHeaderRight, 1, 5)
        gridLayoutResults.addWidget(self.lblAFFName, 2, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblAFFValue, 2, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblAFFConfInt, 2, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam1Name, 3, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam1Value, 3, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam1ConfInt, 3, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam2Name, 4, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam2Value, 4, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam2ConfInt, 4, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam3Name, 5, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam3Value, 5, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam3ConfInt, 5, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam4Name, 6, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam4Value, 6, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam4ConfInt, 6, 5, QtCore.Qt.AlignTop)

        #Create horizontal layout box to hold TRISTAN & University of Leeds Logos
        horizontalLogoLayout = QHBoxLayout()
        #Add horizontal layout to bottom of the vertical layout
        layout.addLayout(horizontalLogoLayout)
        #Display TRISTAN & University of Leeds Logos in labels
        self.lblTRISTAN_Logo = QLabel(self)
        self.lblUoL_Logo = QLabel(self)
        self.lblTRISTAN_Logo.setAlignment(QtCore.Qt.AlignHCenter)
        self.lblUoL_Logo.setAlignment(QtCore.Qt.AlignHCenter)

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
        #Add labels displaying logos to the horizontal layout, 
        #Tristan on the LHS, UoL on the RHS
        horizontalLogoLayout.addWidget(self.lblTRISTAN_Logo)
        horizontalLogoLayout.addWidget(self.lblUoL_Logo)

    def ApplyStyleSheet(self):
        """Modifies the appearance of the GUI using CSS instructions"""
        try:
            self.setStyleSheet(StyleSheet.TRISTAN_GREY)
        except Exception as e:
            print('Error in function ApplyStyleSheet: ' + str(e))
            logger.error('Error in function ApplyStyleSheet: ' + str(e))

    def DisplayModelImage(self):
        """This method takes the name of the model from the drop-down list 
            on the left-hand side of the GUI and displays the corresponding
            image depicting the model and the full name of the model at the
            top of the right-hand side of the GUI."""
        try:
            logger.info('Function DisplayModelImage called.')
            shortModelName = str(self.cmbModels.currentText())
        
            if shortModelName != 'Select a model':
                modelImageName = TracerKineticModels.GetModelImageName(shortModelName)
                pixmapModelImage = QPixmap(modelImageName)
                #Increase the size of the model image
                pMapWidth = pixmapModelImage.width() * 1.35
                pMapHeight = pixmapModelImage.height() * 1.35
                pixmapModelImage = pixmapModelImage.scaled(pMapWidth, pMapHeight, 
                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.lblModelImage.setPixmap(pixmapModelImage)

                longModelName = TracerKineticModels.GetLongModelName(shortModelName)
                self.lblModelName.setText(longModelName)
            else:
                self.lblModelImage.clear()
                self.lblModelName.setText('')

        except Exception as e:
            print('Error in function DisplayModelImage: ' + str(e)) 
            logger.error('Error in function DisplayModelImage: ' + str(e))  

    def SetCurveFittingNotDoneBoolean(self):
        """Sets global boolean _boolCurveFittingDone to false if the 
        plot of the model curve is changed by manually changing the values of 
        model input parameters rather than by running curve fitting."""
        global _boolCurveFittingDone
        _boolCurveFittingDone=False

    def DisplayOptimumParamaterValuesOnGUI(self):
        """Displays the optimum parameter values resulting from curve fitting 
        with their confidence limits on the right-hand side of the GUI. These
        values are stored in the global list _optimisedParamaterList
        
        Where appropriate decimal fractions are converted to %"""
        try:
            logger.info('Function DisplayOptimumParamaterValuesOnGUI called.')
            if self.spinBoxArterialFlowFactor.isHidden() == False:
                self.lblAFFName.setText(self.lblArterialFlowFactor.text())
                parameterValue = _optimisedParamaterList[0][0]
                lowerLimit = _optimisedParamaterList[0][1]
                upperLimit = _optimisedParamaterList[0][2]
                suffix = '%'
                parameterValue = round(parameterValue * 100.0, 2)
                lowerLimit = round(lowerLimit * 100.0, 2)
                upperLimit = round(upperLimit * 100.0, 2)
                #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                #with the % equivalent
                _optimisedParamaterList[0][0] = parameterValue
                _optimisedParamaterList[0][1] = lowerLimit
                _optimisedParamaterList[0][2] = upperLimit
               
                self.lblAFFValue.setText(str(parameterValue) + suffix)
                confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
                self.lblAFFConfInt.setText(confidenceStr)
                nextIndex=1
            else:
                nextIndex = 0
            
            self.lblParam1Name.setText(self.labelParameter1.text())
            parameterValue = round(_optimisedParamaterList[nextIndex][0], 3)
            lowerLimit = round(_optimisedParamaterList[nextIndex][1], 3)
            upperLimit = round(_optimisedParamaterList[nextIndex][2], 3)
            
            if self.spinBoxParameter1.suffix() == '%':
                #convert from decimal fraction to %
                suffix = '%'
                parameterValue = round(parameterValue * 100.0, 3)
                lowerLimit = round(lowerLimit * 100.0,3)
                upperLimit = round(upperLimit * 100.0,3)
                
                #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                #with the % equivalent
                _optimisedParamaterList[nextIndex][0] = parameterValue
                _optimisedParamaterList[nextIndex][1] = lowerLimit
                _optimisedParamaterList[nextIndex][2] = upperLimit
            else:
                suffix = ''
            
            nextIndex +=1
            self.lblParam1Value.setText(str(parameterValue) + suffix)
            modelName = str(self.cmbModels.currentText())
            if modelName == 'HF1-2CFM-FixVe':
                confidenceStr = '[N/A     N/A]'
            else:
                confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
            self.lblParam1ConfInt.setText(confidenceStr) 

            self.lblParam2Name.setText(self.labelParameter2.text())
            parameterValue = round(_optimisedParamaterList[nextIndex][0], 3)
            lowerLimit = round(_optimisedParamaterList[nextIndex][1], 3)
            upperLimit = round(_optimisedParamaterList[nextIndex][2], 3)

            if self.spinBoxParameter2.suffix() == '%':
                suffix = '%'
                parameterValue = round(parameterValue * 100.0,3)
                lowerLimit = round(lowerLimit * 100.0,3)
                upperLimit = round(upperLimit * 100.0,3)
                #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                #with the % equivalent
                _optimisedParamaterList[nextIndex][0] = parameterValue
                _optimisedParamaterList[nextIndex][1] = lowerLimit
                _optimisedParamaterList[nextIndex][2] = upperLimit
            else:
                suffix = ''
            
            nextIndex += 1
            self.lblParam2Value.setText(str(parameterValue) + suffix)
            confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
            self.lblParam2ConfInt.setText(confidenceStr) 

            if self.spinBoxParameter3.isHidden() == False:
                self.lblParam3Name.setText(self.labelParameter3.text())
                parameterValue = round(_optimisedParamaterList[nextIndex][0], 3)
                lowerLimit = round(_optimisedParamaterList[nextIndex][1], 3)
                upperLimit = round(_optimisedParamaterList[nextIndex][2], 3)
                nextIndex += 1
                if self.spinBoxParameter3.suffix() == '%':
                    suffix = '%'
                    parameterValue = round(parameterValue * 100.0, 3)
                    lowerLimit = round(lowerLimit * 100.0, 3)
                    upperLimit = round(upperLimit * 100.0, 3)
                    #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                    #with the % equivalent
                    _optimisedParamaterList[nextIndex][0] = parameterValue
                    _optimisedParamaterList[nextIndex][1] = lowerLimit
                    _optimisedParamaterList[nextIndex][2] = upperLimit
                else:
                    suffix = ''
                
                self.lblParam3Value.setText(str(parameterValue) + suffix)
                confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
                self.lblParam3ConfInt.setText(confidenceStr)

            if self.spinBoxParameter4.isHidden() == False:
                self.lblParam4Name.setText(self.labelParameter4.text())
                parameterValue = round(_optimisedParamaterList[nextIndex][0], 3)
                lowerLimit = round(_optimisedParamaterList[nextIndex][1], 3)
                upperLimit = round(_optimisedParamaterList[nextIndex][2], 3)
                nextIndex += 1
                if self.spinBoxParameter4.suffix() == '%':
                    suffix = '%'
                    parameterValue = round(parameterValue * 100.0, 3)
                    lowerLimit = round(lowerLimit * 100.0, 3)
                    upperLimit = round(upperLimit * 100.0, 3)
                    #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                    #with the % equivalent
                    _optimisedParamaterList[nextIndex][0] = parameterValue
                    _optimisedParamaterList[nextIndex][1] = lowerLimit
                    _optimisedParamaterList[nextIndex][2] = upperLimit
                else:
                    suffix = ''
                
                self.lblParam4Value.setText(str(parameterValue) + suffix)
                confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
                self.lblParam4ConfInt.setText(confidenceStr)
            
        except Exception as e:
            print('Error in function DisplayOptimumParamaterValuesOnGUI: ' + str(e))
            logger.error('Error in function DisplayOptimumParamaterValuesOnGUI: ' + str(e))

    def ClearOptimumParamaterValuesOnGUI(self):
        """Clears the contents of the labels on the right handside of the GUI.
        That is the parameter values and their confidence limits resulting 
        from curve fitting. """
        try:
            logger.info('Function ClearOptimumParamaterValuesOnGUI called.')
            self.lblParam1Name.clear()
            self.lblParam1Value.clear()
            self.lblParam1ConfInt.clear()
            self.lblParam2Name.clear()
            self.lblParam2Value.clear()
            self.lblParam2ConfInt.clear()
            self.lblParam3Name.clear()
            self.lblParam3Value.clear()
            self.lblParam3ConfInt.clear()
            self.lblParam4Name.clear()
            self.lblParam4Value.clear()
            self.lblParam4ConfInt.clear()
            self.lblAFFName.clear()
            self.lblAFFValue.clear()
            self.lblAFFConfInt.clear()
            
        except Exception as e:
            print('Error in function ClearOptimumParamaterValuesOnGUI: ' + str(e))
            logger.error('Error in function ClearOptimumParamaterValuesOnGUI: ' + str(e))
    
    def SaveCSVFile(self, fileName=''):
        """Saves in CSV format the data in the plot on the GUI """ 
        try:
            logger.info('Function SaveCSVFile called.')
            modelName = str(self.cmbModels.currentText())
            modelName.replace(" ", "-")

            if fileName == '':
                #Ask the user to specify the path & name of the CSV file. The name of the model is suggested as a default file name.
                CSVFileName, _ = QFileDialog.getSaveFileName(self, caption="Enter CSV file name", directory=DEFAULT_PLOT_DATA_FILE_PATH_NAME, filter="*.csv")
            else:
               CSVFileName = fileName

           #Check that the user did not press Cancel on the create file dialog
            if CSVFileName:
                logger.info('Function SaveCSVFile - csv file name = ' + CSVFileName)
            
                ROI = str(self.cmbROI.currentText())
                AIF = str(self.cmbAIF.currentText())
                if self.cmbVIF.isVisible() == True:
                    VIF = str(self.cmbVIF.currentText())
                    boolIncludeVIF = True
                else:
                    boolIncludeVIF = False

                #If CSVFileName already exists, delete it
                if os.path.exists(CSVFileName):
                    os.remove(CSVFileName)

                with open(CSVFileName, 'w',  newline='') as csvfile:
                    writeCSV = csv.writer(csvfile,  delimiter=',')
                    if boolIncludeVIF:
                        #write header row
                        writeCSV.writerow(['Time (min)', ROI, AIF, VIF, modelName + ' model'])
                        #Write rows of data
                        for i, time in enumerate(_concentrationData['time']):
                            writeCSV.writerow([time, _concentrationData[ROI][i], _concentrationData[AIF][i], _concentrationData[VIF][i], _listModel[i]])
                    else:
                        #write header row
                        writeCSV.writerow(['Time (min)', ROI, AIF, modelName + ' model'])
                        #Write rows of data
                        for i, time in enumerate(_concentrationData['time']):
                            writeCSV.writerow([time, _concentrationData[ROI][i], _concentrationData[AIF][i], _listModel[i]])
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

    def ClearOptimisedParamaterList(self, callingControl: str):
        """Clears results of curve fitting from the GUI and from the global list
        _optimisedParamaterList """
        try:
            logger.info('ClearOptimisedParamaterList called from ' + callingControl)
            _optimisedParamaterList.clear()
            self.ClearOptimumParamaterValuesOnGUI()
        except Exception as e:
            print('Error in function ClearOptimisedParamaterList: ' + str(e)) 
            logger.error('Error in function ClearOptimisedParamaterList: ' + str(e))

    def DisplayArterialFlowFactorSpinBox(self):
        if str(self.cmbVIF.currentText()) == 'Please Select':
            self.lblArterialFlowFactor.hide()
            self.spinBoxArterialFlowFactor.hide()
        else:
            self.lblArterialFlowFactor.show()
            self.spinBoxArterialFlowFactor.show()

    def DisplayFitModelSaveCSVButtons(self):
        """Displays the Fit Model and Save CSV buttons if both a ROI & AIF 
        are selected.  Otherwise hides them."""
        try:
            #Hide buttons then display them if appropriate
            self.btnFitModel.hide()
            self.btnSaveCSV.hide()
            self.groupBoxBatchProcessing.hide()
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())
            modelName = str(self.cmbModels.currentText())
            modelInletType = TracerKineticModels.GetModelInletType(modelName)
            logger.info("Function DisplayFitModelSaveCSVButtons called. Model is " + modelName)
            if modelInletType == 'single':
                if ROI != 'Please Select' and AIF != 'Please Select':
                    self.btnFitModel.show()
                    self.btnSaveCSV.show()
                    self.groupBoxBatchProcessing.show() 
                    logger.info("Function DisplayFitModelSaveCSVButtons called when ROI = {} and AIF = {}".format(ROI, AIF))
            elif modelInletType == 'dual':
                if ROI != 'Please Select' and AIF != 'Please Select' and VIF != 'Please Select' :
                    self.btnFitModel.show()
                    self.btnSaveCSV.show()
                    self.groupBoxBatchProcessing.show() 
                    logger.info("Function DisplayFitModelSaveCSVButtons called when ROI = {}, AIF = {} & VIF ={}".format(ROI, AIF, VIF)) 
        
        except Exception as e:
            print('Error in function DisplayFitModelSaveCSVButtons: ' + str(e))
            logger.error('Error in function DisplayFitModelSaveCSVButtons: ' + str(e))

    def BuildParameterArray(self) -> List[float]:
        """Forms a 1D array of model input parameters.  Volume fractions are converted 
            from percentages to decimal fractions.
            
            Returns
            -------
                A list of model input parameter values.
            """
        try:
            logger.info('Function BuildParameterArray called.')
            initialParametersArray = []

            #Only add the Arterial Flow Factor if a VIF has been selected
            #and the Arterial Flow Factor spinbox is therefore visible.
            if self.spinBoxArterialFlowFactor.isHidden() == False:
                arterialFlowFactor = self.spinBoxArterialFlowFactor.value()/100
                initialParametersArray.append(arterialFlowFactor)

            modelName = str(self.cmbModels.currentText())
            if modelName == 'HF1-2CFM-FixVe':
                #Ve must be fixed at 23%
                parameter1 = 23.00
            else:
                parameter1 = self.spinBoxParameter1.value()
         
            if self.spinBoxParameter1.suffix() == '%':
                #This is a volume fraction so convert % to a decimal fraction
                parameter1 = parameter1/100.0
            initialParametersArray.append(parameter1)
        
            parameter2 = self.spinBoxParameter2.value()
            if self.spinBoxParameter2.suffix() == '%':
                 #This is a volume fraction so convert % to a decimal fraction
                parameter2 = parameter2/100.0
            initialParametersArray.append(parameter2)
        
            if self.spinBoxParameter3.isHidden() == False:
                parameter3 = self.spinBoxParameter3.value()
                if self.spinBoxParameter3.suffix() == '%':
                     #This is a volume fraction so convert % to a decimal fraction
                    parameter3 = parameter3/100.0
                initialParametersArray.append(parameter3)

            if self.spinBoxParameter4.isHidden() == False:
                parameter4 = self.spinBoxParameter4.value()
                if self.spinBoxParameter4.suffix() == '%':
                     #This is a volume fraction so convert % to a decimal fraction
                    parameter4 = parameter4/100.0
                initialParametersArray.append(parameter4)

            return initialParametersArray
        except Exception as e:
            print('Error in function BuildParameterArray ' + str(e))
            logger.error('Error in function BuildParameterArray '  + str(e))

    def BlockSpinBoxSignals(self, boolBlockSignal: bool):
        """Blocks signals from spinboxes that fire events.  
           Thus allowing spinbox values to be set programmatically 
           without causing a method connected to one of their events to be executed."""
        logger.info('Function BlockSpinBoxSignals called.')
        self.spinBoxArterialFlowFactor.blockSignals(boolBlockSignal)
        self.spinBoxParameter1.blockSignals(boolBlockSignal)
        self.spinBoxParameter2.blockSignals(boolBlockSignal)
        self.spinBoxParameter3.blockSignals(boolBlockSignal)
        self.spinBoxParameter4.blockSignals(boolBlockSignal)

    def setParameterSpinBoxesWithOptimumValues(self, optimumParams):
        """Sets the value displayed in the model parameter spinboxes 
           to the calculated optimum model parameter values.
        
        Input Parameters
        ----------------
            optimumParams - Array of optimum model input parameter values.
        """
        try:
            logger.info('Function setParameterSpinBoxesWithOptimumValues called with optimumParams = {}'.format(optimumParams))
            #Block signals from spinboxes, so that setting values
            #returned from curve fitting does not trigger an event. 
            self.BlockSpinBoxSignals(True)
            
            if self.spinBoxArterialFlowFactor.isHidden() == False:
                self.spinBoxArterialFlowFactor.setValue(optimumParams[0]* 100) #Convert decimal fraction to %
                nextIndex = 1
            else:
                nextIndex = 0

            if self.spinBoxParameter1.suffix() == '%':
                self.spinBoxParameter1.setValue(optimumParams[nextIndex]* 100) #Convert Volume fraction to %
            else:
                self.spinBoxParameter1.setValue(optimumParams[nextIndex])
            nextIndex += 1

            if self.spinBoxParameter2.suffix() == '%':
                self.spinBoxParameter2.setValue(optimumParams[nextIndex]* 100) #Convert Volume fraction to %
            else:
                self.spinBoxParameter2.setValue(optimumParams[nextIndex])
            nextIndex += 1

            if self.spinBoxParameter3.isHidden() == False:
                if self.spinBoxParameter3.suffix() == '%':
                    self.spinBoxParameter3.setValue(optimumParams[nextIndex]* 100) #Convert Volume fraction to %
                else:
                    self.spinBoxParameter3.setValue(optimumParams[nextIndex])
                nextIndex += 1

            if self.spinBoxParameter4.isHidden() == False:
                if self.spinBoxParameter4.suffix() == '%':
                    self.spinBoxParameter4.setValue(optimumParams[nextIndex]* 100) #Convert Volume fraction to %
                else:
                    self.spinBoxParameter4.setValue(optimumParams[nextIndex])
       
            self.BlockSpinBoxSignals(False)
        except Exception as e:
            print('Error in function setParameterSpinBoxesWithOptimumValues ' + str(e))
            logger.error('Error in function setParameterSpinBoxesWithOptimumValues '  + str(e))

    def Calculate95ConfidenceLimits(self, numDataPoints: int, numParams: int, 
                                    optimumParams, paramCovarianceMatrix):
        """Calculates the 95% confidence limits of optimum parameter values 
        resulting from curve fitting. Results are stored in 
        global _optimisedParamaterList that is used in the creation of the PDF report
        and to display results on the GUI.
        
        Input Parameters
        ----------------
        numDataPoints -  Number of data points to which the model is fitted.
                Taken as the number of elements in the array of ROI data.
        numParams - Number of model input parameters.
        optimumParams - Array of optimum model input parameter values 
                        resulting from curve fitting.
        paramCovarianceMatrix - The estimated covariance of the values in optimumParams. 
                        calculated during curve fitting.
        """
        try:
            logger.info('Function Calculate95ConfidenceLimits called: numDataPoints ={}, numParams={}, optimumParams={}, paramCovarianceMatrix={}'
                        .format(numDataPoints, numParams, optimumParams, paramCovarianceMatrix))
            alpha = 0.05 #95% confidence interval = 100*(1-alpha)
            degsOfFreedom = max(0, numDataPoints - numParams) #Number of degrees of freedom
        
            #student-t value for the degrees of freedom and the confidence level
            tval = t.ppf(1.0-alpha/2., degsOfFreedom)
        
            #Remove results of previous curve fitting
            _optimisedParamaterList.clear()
            #_optimisedParamaterList is a list of lists. 
            #Add an empty list for each parameter to hold its value and confidence limits
            for i in range(numParams):
                _optimisedParamaterList.append([])
           
            for counter, numParams, var in zip(range(numDataPoints), optimumParams, np.diag(paramCovarianceMatrix)):
                sigma = var**0.5
                _optimisedParamaterList[counter].append(round(numParams,3))
                _optimisedParamaterList[counter].append(round((numParams - sigma*tval), 3))
                _optimisedParamaterList[counter].append(round((numParams + sigma*tval), 3))
                
            logger.info('In Calculate95ConfidenceLimits, _optimisedParamaterList = {}'.format(_optimisedParamaterList))
        except Exception as e:
            print('Error in function Calculate95ConfidenceLimits ' + str(e))
            logger.error('Error in function Calculate95ConfidenceLimits '  + str(e))  

    def RunCurveFit(self):
        """Performs curve fitting to fit AIF (and VIF) data to the ROI curve.
        Then displays the optimum model input parameters on the GUI and calls 
        the plot function to display the line of best fit on the graph on the GUI
        when these parameter values are input to the selected model.
        Also, takes results from curve fitting (optimal parameter values) and 
        determines their 95% confidence limits which are stored in the global list
        _optimisedParamaterList.
        """
        global _boolCurveFittingDone
        try:
            initialParametersArray = self.BuildParameterArray()

            #Get name of region of interest, arterial and venal input functions
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())

            #Get arrays of data corresponding to the above 3 regions 
            #and the time over which the measurements were made.
            arrayTimes = np.array(_concentrationData['time'], dtype='float')
            arrayROIConcs = np.array(_concentrationData[ROI], dtype='float')
            arrayAIFConcs = np.array(_concentrationData[AIF], dtype='float')

            if VIF != 'Please Select':
                arrayVIFConcs = np.array(_concentrationData[VIF], dtype='float')
            else:
                #Create empty dummy array to act as place holder in  
                #TracerKineticModels.CurveFit function call 
                arrayVIFConcs = []
            
            if self.cboxConstaint.isChecked():
                addConstraint = True
            else:
                addConstraint = False

            #Get the name of the model to be fitted to the ROI curve
            modelName = str(self.cmbModels.currentText())
            #Call curve fitting routine
            logger.info('TracerKineticModels.CurveFit called with model {}, parameters {} and Constraint = {}'.format(modelName, initialParametersArray, addConstraint))
            optimumParams, paramCovarianceMatrix = TracerKineticModels.CurveFit(modelName, arrayTimes, 
                 arrayAIFConcs, arrayVIFConcs, arrayROIConcs, initialParametersArray, addConstraint)
            
            _boolCurveFittingDone = True 
            logger.info('TracerKineticModels.CurveFit returned optimum parameters {} with confidence levels {}'.format(optimumParams, paramCovarianceMatrix))
            
            #Display results of curve fitting  
            #(optimum model parameter values) on GUI.
            self.setParameterSpinBoxesWithOptimumValues(optimumParams)

            #Plot the best curve on the graph
            self.PlotConcentrations('RunCurveFit')

            #Determine 95% confidence limits.
            numDataPoints = arrayROIConcs.size
            numParams = len(initialParametersArray)
            self.Calculate95ConfidenceLimits(numDataPoints, numParams, 
                                    optimumParams, paramCovarianceMatrix)
            
            self.DisplayOptimumParamaterValuesOnGUI()
            
        except ValueError as ve:
            print ('Value Error: RunCurveFit with model ' + modelName + ': '+ str(ve))
            logger.error('Value Error: RunCurveFit with model ' + modelName + ': '+ str(ve))
        except Exception as e:
            print('Error in function RunCurveFit with model ' + modelName + ': ' + str(e))
            logger.error('Error in function RunCurveFit with model ' + modelName + ': ' + str(e))
    
    def BuildParameterDictionary(self, confidenceLimitsArray = None):
        """Builds a dictionary of values and their confidence limits 
        (if curve fitting is performed) for each model input parameter (dictionary key)
        This dictionary is used in the creation of a parameter values table in the
        creation of the PDF report.  It orders the input parameters in the same 
       vertical order as the parameters on the GUI, top to bottom."""
        try:
            logger.info('BuildParameterDictionary called with confidence limits array = {}'
                        .format(confidenceLimitsArray))
            parameterDictionary = {}
           
            index = 0
            if self.spinBoxArterialFlowFactor.isHidden() == False:
                parameterList1 = []
                if confidenceLimitsArray != None:
                    parameterList1.append(confidenceLimitsArray[index][0]) #Parameter Value
                    parameterList1.append(confidenceLimitsArray[index][1]) #Lower Limit
                    parameterList1.append(confidenceLimitsArray[index][2]) #Upper Limit
                else:
                    parameterList1.append(round(self.spinBoxArterialFlowFactor.value(), 2))
                    parameterList1.append('N/A')
                    parameterList1.append('N/A')
                
                parameterDictionary[self.lblArterialFlowFactor.text()] = parameterList1
                index +=1

            if self.spinBoxParameter1.isHidden() == False:
                parameterList2=[]
                if confidenceLimitsArray != None:
                    parameterList2.append(confidenceLimitsArray[index][0]) #Parameter Value
                    parameterList2.append(confidenceLimitsArray[index][1]) #Lower Limit
                    parameterList2.append(confidenceLimitsArray[index][2]) #Upper Limit
                else:
                    parameterList2.append(round(self.spinBoxParameter1.value(), 2))
                    parameterList2.append('N/A')
                    parameterList2.append('N/A')
                
                parameterDictionary[self.labelParameter1.text()] = parameterList2
                index +=1

            if self.spinBoxParameter2.isHidden() == False:
                parameterList3 =[]
                if confidenceLimitsArray != None:
                    parameterList3.append(confidenceLimitsArray[index][0]) #Parameter Value
                    parameterList3.append(confidenceLimitsArray[index][1]) #Lower Limit
                    parameterList3.append(confidenceLimitsArray[index][2]) #Upper Limit
                else:
                    parameterList3.append(round(self.spinBoxParameter2.value(), 2))
                    parameterList3.append('N/A')
                    parameterList3.append('N/A')
                
                parameterDictionary[self.labelParameter2.text()] = parameterList3
                index +=1

            if self.spinBoxParameter3.isHidden() == False:
                parameterList4 = []
                if confidenceLimitsArray != None:
                    parameterList4.append(confidenceLimitsArray[index][0]) #Parameter Value
                    parameterList4.append(confidenceLimitsArray[index][1]) #Lower Limit
                    parameterList4.append(confidenceLimitsArray[index][2]) #Upper Limit
                else:
                    parameterList4.append(round(self.spinBoxParameter3.value(), 3))
                    parameterList4.append('N/A')
                    parameterList4.append('N/A')
                
                parameterDictionary[self.labelParameter3.text()] = parameterList4
                index +=1

            if self.spinBoxParameter4.isHidden() == False:
                parameterList5=[]
                if confidenceLimitsArray != None:
                    parameterList5.append(confidenceLimitsArray[index][0]) #Parameter Value
                    parameterList5.append(confidenceLimitsArray[index][1]) #Lower Limit
                    parameterList5.append(confidenceLimitsArray[index][2]) #Upper Limit
                else:
                    parameterList5.append(round(self.spinBoxParameter4.value(), 4))
                    parameterList5.append('N/A')
                    parameterList5.append('N/A')
                
                parameterDictionary[self.labelParameter4.text()] = parameterList5
                #print('parameterDictionary = {}'.format(parameterDictionary))

            return parameterDictionary
    
        except Exception as e:
            print('Error in function BuildParameterDictionary: ' + str(e))
            logger.error('Error in function BuildParameterDictionary: ' + str(e))


    def CreatePDFReport(self):
        """Creates and saves a report of model fitting. It includes the name of the model, 
        the current values of its input parameters and a copy of the current plot."""
        try:
            pdf = PDF(REPORT_TITLE) 
            
            #Ask the user to specify the path & name of PDF report. A default report name is suggested, see the Constant declarations at the top of this file
            reportFileName, _ = QFileDialog.getSaveFileName(self, caption="Enter PDF file name", directory=DEFAULT_REPORT_FILE_PATH_NAME, filter="*.pdf")
        
            if reportFileName:
                #If the user has entered the name of a new file, then we will have to add the .pdf extension
                #If the user has decided to overwrite an existing file, then will not have to add the .pdf extension
                name, ext = os.path.splitext(reportFileName)
                if ext != '.pdf':
                    #Need to add .pdf extension to reportFileName
                    reportFileName = reportFileName + '.pdf'
                if os.path.exists(reportFileName):
                    #delete existing copy of PDF called reportFileName
                    os.remove(reportFileName)   
                shortModelName = str(self.cmbModels.currentText())
                longModelName = TracerKineticModels.GetLongModelName(shortModelName)
                
                #Save a png of the concentration/time plot for display 
                #in the PDF report.
                self.figure.savefig(fname=IMAGE_NAME, dpi=150)  #dpi=150 so as to get a clear image in the PDF report
                
                if _boolCurveFittingDone == True:
                    parameterDict = self.BuildParameterDictionary(_optimisedParamaterList)
                else:
                    parameterDict = self.BuildParameterDictionary()
                             
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))

                pdf.CreateAndSavePDFReport(reportFileName, _dataFileName, 
                       longModelName, IMAGE_NAME, parameterDict)
                
                QApplication.restoreOverrideCursor()

                #Delete image file
                os.remove(IMAGE_NAME)
                logger.info('PDF Report created called ' + reportFileName)
        except Exception as e:
            print('Error in function CreatePDFReport: ' + str(e))
            logger.error('Error in function CreatePDFReport: ' + str(e))
       
    def LoadDataFile(self):
        """Loads the contents of a CSV file containing time and concentration data
        into a dictionary of lists. The key is the name of the organ or 'time' and 
        the corresponding value is a list of concentrations 
        (or times when the key is 'time')
        
        The following validation is applied to the data file:
            -The CSV file must contain at least 3 columns of data separated by commas.
            -The first column in the CSV file must contain time data.
            -The header of the time column must contain the word 'time'."""
        global _concentrationData
        global _dataFileName

        #clear the global dictionary of previous data
        _concentrationData.clear()
        
        self.HideAllControlsOnGUI()
        
        try:
            #get the data file in csv format
            #filter parameter set so that the user can only open a csv file
            fullFilePath, _ = QFileDialog.getOpenFileName(parent=self, caption="Select csv file", filter="*.csv")
            if os.path.exists(fullFilePath):
                with open(fullFilePath, newline='') as csvfile:
                    line = csvfile.readline()
                    if line.count(',') < (MIN_NUM_COLUMNS_CSV_FILE - 1):
                        QMessageBox().warning(self, "CSV data file", "The CSV file must contain at least 3 columns of data separated by commas.  The first column must contain time data.", QMessageBox.Ok)
                        raise RuntimeError('The CSV file must contain at least 3 columns of data separated by commas.')
                    
                    #go back to top of the file
                    csvfile.seek(0)
                    readCSV = csv.reader(csvfile, delimiter=',')
                    #Get column header labels
                    headers = next(readCSV, None)  # returns the headers or `None` if the input is empty
                    if headers:
                        firstColumnHeader = headers[0].strip().lower()
                        if 'time' not in firstColumnHeader:
                            QMessageBox().warning(self, "CSV data file", "The first column must contain time data.", QMessageBox.Ok)
                            raise RuntimeError('The first column in the CSV file must contain time data.')    

                    logger.info('CSV data file {} loaded'.format(_dataFileName))
                    
                    #Extract data filename from the full data file path
                    #_dataFileName = os.path.basename(_dataFileName)
                    folderName = os.path.basename(os.path.dirname(fullFilePath))
                    self.directory, _dataFileName = os.path.split(fullFilePath)
                    self.statusbar.showMessage('File ' + _dataFileName + ' loaded')
                    self.lblBatchProcessing.setText("Batch process all CSV data files in folder: " + folderName)
                    
                    #Column headers form the keys in the dictionary called _concentrationData
                    for header in headers:
                        if 'time' in header:
                            header ='time'
                        _concentrationData[header.title().lower()]=[]
                    #Also add a 'model' key to hold a list of concentrations generated by a model
                    _concentrationData['model'] = []

                    #Each key in the dictionary is paired with a list of 
                    #corresponding concentrations 
                    #(except the Time key that is paired with a list of times)
                    for row in readCSV:
                        colNum=0
                        for key in _concentrationData:
                            #Iterate over columns in the selected row
                            if key != 'model':
                                if colNum == 0: 
                                    #time column
                                    _concentrationData['time'].append(float(row[colNum])/60.0)
                                else:
                                    _concentrationData[key].append(float(row[colNum]))
                                colNum+=1           
                csvfile.close()

                self.ConfigureGUIAfterLoadingData()
                
        except csv.Error:
            print('CSV Reader error in function LoadDataFile: file {}, line {}: error={}'.format(_dataFileName, readCSV.line_num, csv.Error))
            logger.error('CSV Reader error in function LoadDataFile: file {}, line {}: error ={}'.format(_dataFileName, readCSV.line_num, csv.Error))
        except IOError:
            print ('IOError in function LoadDataFile: cannot open file' + _dataFileName + ' or read its data')
            logger.error ('IOError in function LoadDataFile: cannot open file' + _dataFileName + ' or read its data')
        except RuntimeError as re:
            print('Runtime error in function LoadDataFile: ' + str(re))
            logger.error('Runtime error in function LoadDataFile: ' + str(re))
        except Exception as e:
            print('Error in function LoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            logger.error('Error in function LoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            QMessageBox().warning(self, "CSV data file", "Error reading CSV file at line {} - {}".format(readCSV.line_num, e), QMessageBox.Ok)

    def HideAllControlsOnGUI(self):
        """Hides/clears all the widgets on left-hand side of the application 
        except for the Load & Display Data and Exit buttons.  
        It is called before a data file is loaded in case the Cancel button on the dialog
        is clicked.  This prevents the scenario where buttons are displayed but there is no
        data loaded to process when they are clicked."""

        logger.info('Function HideAllControlsOnGUI called')
        #Clear label displaying name of the datafile
        self.statusbar.clearMessage()

        self.lblROI.hide()
        self.cmbROI.hide()
        self.groupBoxModel.hide()
        self.btnFitModel.hide()
        self.btnSaveCSV.hide()
        self.groupBoxBatchProcessing.hide()
        

    def ConfigureGUIAfterLoadingData(self):
        """After successfully loading a datafile, this method loads a list of
        organs into ROI, AIF & VIF drop-down lists and displays 
        the ROI drop-down list.  It also clears the Matplotlib graph."""
        try:
            #Data file loaded OK, so set up the GUI
            #Reset and enable dropdown list of models
            self.cmbROI.clear()
            self.cmbAIF.clear()
            self.cmbVIF.clear()
            
            #Create a list of organs for which concentrations are
            #provided in the data input file.  See LoadDataFile method.
            organArray = []
            organArray = self.GetListOrgans()
            
            self.cmbROI.addItems(organArray)
            self.cmbAIF.addItems(organArray)
            self.cmbVIF.addItems(organArray)
            self.lblROI.show()
            self.cmbROI.show()

            #Clear the existing plot
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
        set of organs.  Each column of concentration data is labeled by
        header giving the name of organ.
        
        Returns
        -------
            A list of organs for which there is concentration data.
        """
        try:
            logger.info('Function GetListOrgans called')
            organList =[]
            organList.append('Please Select') #First item at the top of the drop-down list
            for key in _concentrationData:
                if key.lower() != 'time' and key.lower() != 'model':  
                    organList.append(str(key))       
            return organList
        except RuntimeError as re:
            print('runtime error in function GetListOrgans' + str(re))
            logger.error('runtime error in function GetListOrgans' + str(re))
        except Exception as e:
            print('Error in function GetListOrgans: ' + str(e))
            logger.error('Error in function GetListOrgans: ' + str(e))
    
    def InitialiseParameterSpinBoxes(self):
        """Reset model parameter spinboxes with typical initial values for each model"""
        try:
            #Remove suffixes from the first spinboxes 
            self.spinBoxParameter1.setSuffix('')
            self.spinBoxParameter1.setEnabled(True) #May have been disabled by HF1-2CFM-FixVe model

            #Block signals from spinboxes, so that setting initial values
            #does not trigger an event.
            self.BlockSpinBoxSignals(True)
            self.spinBoxArterialFlowFactor.setValue(DEFAULT_VALUE_Fa)
            
            modelName = str(self.cmbModels.currentText())
            logger.info('Function InitialiseParameterSpinBoxes called when model = ' + modelName)
            if modelName == '2-2CFM':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setRange(0.01, 99.99)
                self.spinBoxParameter1.setSingleStep(0.1)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve_2_2CFM)
                self.spinBoxParameter1.setSuffix('%')

                self.spinBoxParameter2.setDecimals(2)
                self.spinBoxParameter2.setRange(0, 100.0)
                self.spinBoxParameter2.setSingleStep(0.1)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Fp_2_2CFM)

                self.spinBoxParameter3.setDecimals(3)
                self.spinBoxParameter3.setRange(0.0, 100.0)
                self.spinBoxParameter3.setSingleStep(0.1)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Khe_2_2CFM)
                
                self.spinBoxParameter4.setDecimals(4)
                self.spinBoxParameter4.setRange(0.0001, 100.0)
                self.spinBoxParameter4.setSingleStep(0.1)
                self.spinBoxParameter4.setValue(DEFAULT_VALUE_Kbh_2_2CFM)
                
            elif modelName == 'HF2-2CFM':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setRange(0.01, 99.99)
                self.spinBoxParameter1.setSingleStep(0.1)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter1.setSuffix('%')

                self.spinBoxParameter2.setDecimals(3)
                self.spinBoxParameter2.setRange(0.0, 100.0)
                self.spinBoxParameter2.setSingleStep(0.1)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Khe)
                
                self.spinBoxParameter3.setDecimals(4)
                self.spinBoxParameter3.setRange(0.0001, 100.0)
                self.spinBoxParameter3.setSingleStep(0.1)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbh)

            elif modelName == 'HF1-2CFM' or modelName == 'HF1-2CFM-FixVe':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setRange(0.01, 99.99)
                self.spinBoxParameter1.setSingleStep(0.1)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter1.setSuffix('%')

                self.spinBoxParameter2.setDecimals(3)
                self.spinBoxParameter2.setRange(0.0, 100.0)
                self.spinBoxParameter2.setSingleStep(0.1)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Khe)
                
                self.spinBoxParameter3.setDecimals(4)
                self.spinBoxParameter3.setRange(0.0001, 100.0)
                self.spinBoxParameter3.setSingleStep(0.1)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbh)

            self.BlockSpinBoxSignals(False)
        except Exception as e:
            print('Error in function InitialiseParameterSpinBoxes: ' + str(e) )
            logger.error('Error in function InitialiseParameterSpinBoxes: ' + str(e) )

    def ConfigureGUIForEachModel(self):
        """When a model is selected, this method configures the appearance of the GUI
        accordingly.  For example, spinboxes for the input of model parameter values are
        given an appropriate label."""
        try:
            modelName = str(self.cmbModels.currentText())
            logger.info('Function ConfigureGUIForEachModel called when model = ' + modelName)
            
            #self.cboxDelay.show()
            #self.cboxConstaint.show()
            self.cboxConstaint.setChecked(False)
            self.btnReset.show()
            self.btnSaveReport.show()
            #Remove results of curve fitting of the previous model
            self.ClearOptimumParamaterValuesOnGUI() 
            self.InitialiseParameterSpinBoxes() #Typical initial values for each model
            #Show widgets common to all models
            self.lblAIF.show()
            self.cmbAIF.show()
            self.lblVIF.show()
            self.cmbVIF.show()
            self.spinBoxParameter1.show()
            self.spinBoxParameter2.show()
            self.spinBoxParameter3.show()
            
            #Configure parameter spinbox labels for each model
            if modelName == '2-2CFM':
                self.labelParameter1.setText(LABEL_PARAMETER_Ve)
                self.labelParameter1.show()
                self.labelParameter2.setText(LABEL_PARAMETER_Fp)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_Khe)
                self.labelParameter3.show()
                self.labelParameter4.setText(LABEL_PARAMETER_Kbh)
                self.labelParameter4.show()
                self.spinBoxParameter4.show()
            elif modelName == 'HF2-2CFM':
                self.labelParameter1.setText(LABEL_PARAMETER_Ve)
                self.labelParameter1.show()
                self.labelParameter2.setText(LABEL_PARAMETER_Khe)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_Kbh)
                self.labelParameter3.show()
                self.labelParameter4.hide()
                self.spinBoxParameter4.hide()
            elif modelName == 'HF1-2CFM' or modelName == 'HF1-2CFM-FixVe':
                self.labelParameter1.setText(LABEL_PARAMETER_Ve)
                self.labelParameter1.show()
                self.labelParameter2.setText(LABEL_PARAMETER_Khe)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_Kbh)
                self.labelParameter3.show()
                self.labelParameter4.hide()
                self.spinBoxParameter4.hide()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.cmbVIF.setCurrentIndex(0)
            else:  #No model is selected
                self.lblAIF.hide()
                self.cmbAIF.hide()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.cboxDelay.hide()
                self.cboxConstaint.hide()
                self.btnReset.hide()
                self.spinBoxParameter1.hide()
                self.spinBoxParameter2.hide()
                self.spinBoxParameter3.hide()
                self.spinBoxParameter4.hide()
                self.spinBoxArterialFlowFactor.hide()
                self.labelParameter1.clear()
                self.labelParameter2.clear()
                self.labelParameter3.clear()
                self.labelParameter4.clear()
                self.lblArterialFlowFactor.hide()
                
                self.cmbAIF.setCurrentIndex(0)
                self.cmbVIF.setCurrentIndex(0)
                self.btnFitModel.hide()
                self.btnSaveReport.hide()
                self.btnSaveCSV.hide()
                self.groupBoxBatchProcessing.hide()
        except Exception as e:
            print('Error in function ConfigureGUIForEachModel: ' + str(e) )
            logger.error('Error in function ConfigureGUIForEachModel: ' + str(e) )
            
    def GetScreenResolution(self):
        """Determines the screen resolution of the device running this software.
        
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
    
    def PlotConcentrations(self, nameCallingFunction: str):
        """Plots the concentration against time curves for the ROI, AIF, VIF.  
        Also, the concentration/time curve predicted by the selected model.
        
        Input Parameter
        ----------------
        nameCallingFunction - Name of the function or widget from whose event 
        this function is called. This information is used in logging and error
        handling.
        """
        try:
            global _listModel
            boolAIFSelected = False
            boolVIFSelected = False

            self.figure.clear()
            self.figure.set_visible(True)
            
            # create an axis
            ax = self.figure.add_subplot(111)

            #Get the optimum label size for the screen resolution.
            tickLabelSize, xyAxisLabelSize, titleSize = self.DetermineTextSize()
            
            #Set size of the x,y axis tick labels
            ax.tick_params(axis='both', which='major', labelsize=tickLabelSize)

            #Get the name of the model 
            modelName = str(self.cmbModels.currentText())
            
            arrayTimes = np.array(_concentrationData['time'], dtype='float')

            ROI = str(self.cmbROI.currentText())
            if ROI != 'Please Select':
                arrayROIConcs = np.array(_concentrationData[ROI], dtype='float')
                ax.plot(arrayTimes, arrayROIConcs, 'b.-', label= ROI)

            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())

            logger.info('Function plot called from ' + nameCallingFunction + ' when ROI={}, AIF={} and VIF={}'.format(ROI, AIF, VIF))

            if AIF != 'Please Select':
                #Plot AIF curve
                arrayAIFConcs = np.array(_concentrationData[AIF], dtype='float')
                ax.plot(arrayTimes, arrayAIFConcs, 'r.-', label= AIF)
                boolAIFSelected = True

            if VIF != 'Please Select':
                #Plot VIF curve
                arrayVIFConcs = np.array(_concentrationData[VIF], dtype='float')
                ax.plot(arrayTimes, arrayVIFConcs, 'k.-', label= VIF)
                boolVIFSelected = True
                    
            #Plot concentration curve from the model
            if TracerKineticModels.GetModelInletType(modelName) == 'dual':
                if boolAIFSelected and boolVIFSelected:
                    parameterArray = self.BuildParameterArray()
                    logger.info('TracerKineticModels.ModelSelector called when model ={} and parameter array = {}'. format(modelName, parameterArray))        
                    _listModel = TracerKineticModels.ModelSelector(modelName, arrayTimes, 
                       arrayAIFConcs, parameterArray, arrayVIFConcs)
                    arrayModel =  np.array(_listModel, dtype='float')
                    ax.plot(arrayTimes, arrayModel, 'g--', label= modelName + ' model')
            elif TracerKineticModels.GetModelInletType(modelName) == 'single':
                if boolAIFSelected:
                    parameterArray = self.BuildParameterArray()
                    logger.info('TracerKineticModels.ModelSelector called when model ={} and parameter array = {}'. format(modelName, parameterArray))        
                    _listModel = TracerKineticModels.ModelSelector(modelName, arrayTimes, 
                       arrayAIFConcs, parameterArray)
                    arrayModel =  np.array(_listModel, dtype='float')
                    ax.plot(arrayTimes, arrayModel, 'g--', label= modelName + ' model')


            if ROI != 'Please Select':  
                ax.set_xlabel('Time (mins)', fontsize=xyAxisLabelSize)
                ax.set_ylabel('Concentration (mM)', fontsize=xyAxisLabelSize)
                ax.set_title('Tissue Concentrations', fontsize=titleSize, pad=25)
                ax.grid()
                chartBox = ax.get_position()
                ax.set_position([chartBox.x0*1.1, chartBox.y0, chartBox.width*0.9, chartBox.height])
                ax.legend(loc='upper center', bbox_to_anchor=(0.9, 1.0), shadow=True, ncol=1, fontsize='x-large')
                # refresh canvas
                self.canvas.draw()
            else:
                # draw a blank graph on the canvas
                self.canvas.draw()
            
        except Exception as e:
                print('Error in function PlotConcentrations when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
                logger.error('Error in function PlotConcentrations when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
    
    def ExitApp(self):
        """Closes the Model Fitting application."""
        logger.info("Application closed using the Exit button.")
        sys.exit(0)  

    def BatchProcessAllCSVDataFiles(self):
        try:
            logger.info('Function BatchProcessAllCSVDataFiles called.')
            self.pbar.show()
            #Create a list of csv files in the selected directory
            csvFiles = [file for file in os.listdir(self.directory) if file.lower().endswith('.csv')]
            numCSVFiles = len(csvFiles)

            self.lblBatchProcessing.clear()
            self.lblBatchProcessing.setText('{}: {} csv files.'
                                       .format(self.directory, str(numCSVFiles)))

            #Make nested folders to hold plot CSV files and PDF reports
            csvPlotDataFolder = self.directory + '/CSVPlotDataFiles'
            pdfReportFolder = self.directory + '/PDFReports'
            if not os.path.exists(csvPlotDataFolder):
                os.makedirs(csvPlotDataFolder)
                logger.info('BatchProcessAllCSVDataFiles: {} created.'.format(csvPlotDataFolder))
            if not os.path.exists(pdfReportFolder):
                os.makedirs(pdfReportFolder)
                logger.info('BatchProcessAllCSVDataFiles: {} created.'.format(pdfReportFolder))
            
            self.pbar.setMaximum(numCSVFiles)
            self.pbar.setValue(0)
        
            count = 0

            for file in csvFiles:
                count +=1
                self.lblBatchProcessing.clear()
                self.lblBatchProcessing.setText("Processing {}".format(str(file)))
                #Load current file
                if not self.BatchProcessingLoadDataFile(self.directory + '/' + str(file)):
                    continue
                #Plot data
                self.PlotConcentrations('BatchProcessAllCSVDataFiles')
                #Fit curve to model
                self.RunCurveFit()
                #Save plot data to CSV file
                self.SaveCSVFile(str(csvPlotDataFolder + '/plot' + file))
                #Save PDF Report
                #Reset default values
                self.pbar.setValue(count)

            self.lblBatchProcessing.setText("Processing complete.")
            self.pbar.hide()
        except Exception as e:
            print('Error in function BatchProcessAllCSVDataFiles: ' + str(e) )
            logger.error('Error in function BatchProcessAllCSVDataFiles: ' + str(e) )

    def BatchProcessingLoadDataFile(self, fullFilePath):
        """Loads the contents of a CSV file containing time and concentration data
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
        global _concentrationData
        global _dataFileName

        #clear the global dictionary of previous data
        _concentrationData.clear()

        boolFileLoadedOK = True
        
        try:
            if os.path.exists(fullFilePath):
                with open(fullFilePath, newline='') as csvfile:
                    line = csvfile.readline()
                    if line.count(',') < (MIN_NUM_COLUMNS_CSV_FILE - 1):
                        boolFileLoadedOK = False
                        errorStr = 'Batch Processing: CSV file {} must contain at least 3 columns of data separated by commas.'.format(fullFilePath)
                        logger.info(errorStr)
                        raise RuntimeError(errorStr)

                    #go back to top of the file
                    csvfile.seek(0)
                    readCSV = csv.reader(csvfile, delimiter=',')
                    #Get column header labels
                    headers = next(readCSV, None)  # returns the headers or `None` if the input is empty
                    if headers:
                        firstColumnHeader = headers[0].strip().lower()
                        if 'time' not in firstColumnHeader:
                            boolFileLoadedOK = False
                            errorStr = 'Batch Processing: The first column in {} must contain time data.'.format(fullFilePath)
                            logger.info(errorStr)
                            raise RuntimeError(errorStr)    

                    logger.info('Batch Processing: CSV data file {} loaded OK'.format(fullFilePath))
                    
                    #Column headers form the keys in the dictionary called _concentrationData
                    for header in headers:
                        if 'time' in header:
                            header ='time'
                        _concentrationData[header.title().lower()]=[]
                    #Also add a 'model' key to hold a list of concentrations generated by a model
                    _concentrationData['model'] = []

                    #Each key in the dictionary is paired with a list of 
                    #corresponding concentrations 
                    #(except the Time key that is paired with a list of times)
                    for row in readCSV:
                        colNum=0
                        for key in _concentrationData:
                            #Iterate over columns in the selected row
                            if key != 'model':
                                if colNum == 0: 
                                    #time column
                                    _concentrationData['time'].append(float(row[colNum])/60.0)
                                else:
                                    _concentrationData[key].append(float(row[colNum]))
                                colNum+=1           
                csvfile.close()
                
        except csv.Error:
            boolFileLoadedOK = False
            print('CSV Reader error in function LoadDataFile: file {}, line {}: error={}'.format(_dataFileName, readCSV.line_num, csv.Error))
            logger.error('CSV Reader error in function LoadDataFile: file {}, line {}: error ={}'.format(_dataFileName, readCSV.line_num, csv.Error))
        except IOError:
            boolFileLoadedOK = False
            print ('IOError in function LoadDataFile: cannot open file' + _dataFileName + ' or read its data')
            logger.error ('IOError in function LoadDataFile: cannot open file' + _dataFileName + ' or read its data')
        except RuntimeError as re:
            boolFileLoadedOK = False
            print('Runtime error in function LoadDataFile: ' + str(re))
            logger.error('Runtime error in function LoadDataFile: ' + str(re))
        except Exception as e:
            boolFileLoadedOK = False
            print('Error in function LoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            logger.error('Error in function LoadDataFile: ' + str(e) + ' at line {} in the CSV file'.format( readCSV.line_num))
            QMessageBox().warning(self, "CSV data file", "Error reading CSV file at line {} - {}".format(readCSV.line_num, e), QMessageBox.Ok)
        finally:
            return boolFileLoadedOK
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ModelFittingApp()
    main.show()
    sys.exit(app.exec_())
