"""This module is the start up module in the TRISTAN-Model-Fitting application. 
It defines the GUI and the logic providing the application's functionality.

   The TRISTAN-Model-Fitting application allows the user to:
        1. Load a CSV file of concentration/time data.  In addition to a column of time data, this
            file must contain at least 2 columns of concentration data for two organs.  There is no
            upper limit on the number of organs for which concentration data may be 
        2. Select a Region Of Interest (ROI) and display a plot of its concentration against
            time.
        3. The user can then select a model they would like to fit to the ROI data.
        4. Depending on the model selected the user can then select an Arterial Input Function(AIF)
            and/or a Venal Input Function (VIF) and display a plot of its concentration against time
            on the same axes as the ROI.
        5. After step 4 is performed, the selected model is used to create a time/concentration series
           based on default values for the models input parameters.  This data series is also plotted 
           on the above axes.
        6. The default model parameters are displayed on the form and the user may vary them
           and observe the effect on the curve generated in step 5.
        7. By pressing the Fit Model button, the model is fitted to the ROI data and the resulting
           values of the parameters are displayed on the screen.
        8. """
   
import sys
import csv
import os.path
import numpy as np
import pyautogui
import logging

from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog,  QApplication, QPushButton, \
     QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel, QDoubleSpinBox, \
     QMessageBox, QFileDialog, QCheckBox, QLineEdit, QSizePolicy, QSpacerItem, QGridLayout

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
import styleSheet

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
DEFAULT_VALUE_Vp = 10.0
DEFAULT_VALUE_Vh = 75.0
DEFAULT_VALUE_Ve = 23.0
DEFAULT_VALUE_Vb = 2.0
DEFAULT_VALUE_Ktrans = 0.10
DEFAULT_VALUE_Fp = 0.0001
DEFAULT_VALUE_Kce = 0.025
DEFAULT_VALUE_Kbc = 0.003
DEFAULT_VALUE_Kbh = 0.00075
DEFAULT_VALUE_Khe = 0.01875
DEFAULT_VALUE_Fa = 40.0 #Arterial Flow Fraction
LABEL_PARAMETER_Vp = 'Plasma Volume Fraction,\n Vp'
LABEL_PARAMETER_Vh = 'Hepatocyte volume fraction,\n Vh'
LABEL_PARAMETER_Vb = 'Intrahepatic bile duct volume fraction,\n Vb'
LABEL_PARAMETER_Kce = 'Hepatocellular Uptake Rate, \n Kce (mL/100mL/min)'
LABEL_PARAMETER_Ve = 'Extracellular Vol Fraction,\n Ve'
LABEL_PARAMETER_Fp = 'Total Plasma Inflow, \n Fp (mL/min/mL)'
LABEL_PARAMETER_Ktrans = 'Transfer Rate Constant, \n Ktrans (1/min)'
LABEL_PARAMETER_Kbh = 'Biliary Efflux Rate, \n Kbh (mL/min/mL)'
LABEL_PARAMETER_Khe = 'Hepatocyte uptake rate, \n Khe (mL/min/mL)'

# Fp: Total plasma inflow (mL/min/mL) <0:0.01> (0.0001)
# fa: Arterial flow fraction <0:1> (0.4)
# khe: Hepatocyte uptake rate (mL/min/mL) <0:0.1> (0.01875)
# kbh: Biliary efflux rate (mL/min/mL) <0:0.01> (0.00075)
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

class ModelFittingApp(QDialog):
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
        self.setWindowIcon(QIcon('TRISTAN LOGO.jpg'))
        width, height = self.getScreenResolution()
        self.setGeometry(width*0.05, height*0.25, width*0.9, height*0.5)
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint |  QtCore.Qt.WindowCloseButtonHint)
        
        self.applyStyleSheet()
       
        #Setup the layouts, the containers for widgets
        verticalLayoutLeft, verticalLayoutMiddle, verticalLayoutRight = self.setupLayouts()
        
        #Add widgets to the left-hand side vertical layout
        self.setupLeftVerticalLayout(verticalLayoutLeft)

        #Set up the graph to plot concentration data on
        # the middle vertical layout
        self.setupPlotArea(verticalLayoutMiddle)
        
        #Create a group box and place it in the right-handside vertical layout
        #Also add a label to hold the TRISTAN Logo
        self.setupRightVerticalLayout(verticalLayoutRight)

        logger.info("GUI created successfully.")

    def setupLayouts(self):
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

    def setupLeftVerticalLayout(self, layout):
        """
        Creates widgets and places them on the left-handside vertical layout. 
        """
        #Create Load Data File Button
        self.btnLoadDisplayData = QPushButton('Load and display data.')
        self.btnLoadDisplayData.setToolTip('Open file dialog box to select the data file')
        self.btnLoadDisplayData.setShortcut("Ctrl+L")
        self.btnLoadDisplayData.setAutoDefault(False)
        self.btnLoadDisplayData.resize(self.btnLoadDisplayData.minimumSizeHint())
        #Method loadDataFile is executed in the clicked event of this button
        self.btnLoadDisplayData.clicked.connect(self.loadDataFile)

        #Create label to display the name of the loaded data file
        self.lblDataFileName = QLabel('')
        
        #Add a vertical spacer to the top of vertical layout to ensure
        #the top of the Load Data button is level with the MATPLOTLIB toolbar 
        #in the central vertical layout.
        verticalSpacer = QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout.addItem(verticalSpacer)
        #Add Load data file button to the top of the vertical layout
        layout.addWidget(self.btnLoadDisplayData)
        layout.addWidget(self.lblDataFileName)
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
        self.setupModelGroupBox(layout, verticalSpacer)
        
        self.btnSaveReport = QPushButton('Save Report in PDF Format')
        self.btnSaveReport.hide()
        self.btnSaveReport.setToolTip('Insert an image of the graph opposite and associated data in a PDF file')
        layout.addWidget(self.btnSaveReport, QtCore.Qt.AlignTop)
        self.btnSaveReport.clicked.connect(self.savePDFReport)
        
        self.btnExit = QPushButton('Exit')
        layout.addWidget(self.btnExit)
        self.btnExit.clicked.connect(self.exitApp)
        layout.addStretch()

    def setupModelGroupBox(self, layout, verticalSpacer):
        """Creates a group box to hold widgets associated with the 
        selection of a model and for inputing/displaying that model's
        parameter data."""
        self.groupBoxModel = QGroupBox('Model Fitting')
        self.groupBoxModel.setAlignment(QtCore.Qt.AlignHCenter)
        #The group box is hidden until a ROI is selected.
        self.groupBoxModel.hide()
        layout.addWidget(self.groupBoxModel)
        layout.addItem(verticalSpacer)
        
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
        self.cmbModels.addItems(TracerKineticModels.getListModels())
        self.cmbModels.setCurrentIndex(0) #Display "Select a Model"
        self.cmbModels.currentIndexChanged.connect(self.displayModelImage)
        self.cmbModels.currentIndexChanged.connect(self.configureGUIForEachModel)
        self.cmbModels.currentIndexChanged.connect(lambda: self.clearOptimisedParamaterList('cmbModels')) 
        self.cmbModels.activated.connect(lambda:  self.plot('cmbModels'))

        #Create dropdown lists for selection of AIF & VIF
        self.lblAIF = QLabel("Arterial Input Function:")
        self.cmbAIF = QComboBox()
        self.cmbAIF.setToolTip('Select Arterial Input Function')
        self.lblVIF = QLabel("Venal Input Function:")
        self.cmbVIF = QComboBox()
       
        self.cmbVIF.setToolTip('Select Venal Input Function')
        #When a ROI is selected plot its concentration data on the graph.
        self.cmbROI.activated.connect(lambda:  self.plot('cmbROI'))
        #When a ROI is selected, then make the Model groupbox and the widgets
        #contains visible.
        self.cmbROI.currentIndexChanged.connect(self.displayModelFittingGroupBox)
        #When an AIF is selected plot its concentration data on the graph.
        self.cmbAIF.activated.connect(lambda: self.plot('cmbAIF'))
        #When an AIF is selected display the Fit Model and Save plot CVS buttons.
        self.cmbAIF.currentIndexChanged.connect(self.displayFitModelSaveCSVButtons)
        self.cmbVIF.currentIndexChanged.connect(self.displayArterialFlowFactorSpinBox)
        #When a VIF is selected plot its concentration data on the graph.
        self.cmbVIF.activated.connect(lambda: self.plot('cmbVIF'))
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
        self.btnReset.clicked.connect(self.initialiseParameterSpinBoxes)
        #If parameters reset to their default values, replot the concentration and model data
        self.btnReset.clicked.connect(lambda: self.plot('Reset Button'))
        modelHorizontalLayoutReset.addWidget(self.cboxDelay)
        modelHorizontalLayoutReset.addWidget(self.cboxConstaint)
        modelHorizontalLayoutReset.addWidget(self.btnReset)
        
        #Create spinboxes and their labels
        #Label text set in function configureGUIForEachModel when the model is selected
        self.lblArterialFlowFactor = QLabel("Arterial Flow Fraction:") 
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
        self.spinBoxArterialFlowFactor.setMinimumSize(self.spinBoxArterialFlowFactor.minimumSizeHint())
        self.spinBoxArterialFlowFactor.resize(self.spinBoxArterialFlowFactor.sizeHint())

        self.spinBoxParameter1 = QDoubleSpinBox()
        self.spinBoxParameter1.setMinimumSize(self.spinBoxParameter1.minimumSizeHint())
        self.spinBoxParameter1.resize(self.spinBoxParameter1.sizeHint())

        self.spinBoxParameter2 = QDoubleSpinBox()
        self.spinBoxParameter2.resize(self.spinBoxParameter2.sizeHint())

        self.spinBoxParameter3 = QDoubleSpinBox()
        self.spinBoxParameter3.resize(self.spinBoxParameter3.sizeHint())

        self.spinBoxParameter4 = QDoubleSpinBox()
        self.spinBoxParameter4.resize(self.spinBoxParameter4.sizeHint())

        self.lblArterialFlowFactor.hide()
        self.spinBoxArterialFlowFactor.hide()
        self.spinBoxParameter1.hide()
        self.spinBoxParameter2.hide()
        self.spinBoxParameter3.hide()
        self.spinBoxParameter4.hide()

        #If a parameter value is changed, replot the concentration and model data
        self.spinBoxArterialFlowFactor.valueChanged.connect(lambda: self.plot('spinBoxArterialFlowFactor')) 
        self.spinBoxParameter1.valueChanged.connect(lambda: self.plot('spinBoxParameter1')) 
        self.spinBoxParameter2.valueChanged.connect(lambda: self.plot('spinBoxParameter2')) 
        self.spinBoxParameter3.valueChanged.connect(lambda: self.plot('spinBoxParameter3'))
        self.spinBoxParameter4.valueChanged.connect(lambda: self.plot('spinBoxParameter4'))
        #Set a global boolean variable, _boolCurveFittingDone to false to indicate that 
        #the value of a model parameter has been changed manually rather than by curve fitting
        self.spinBoxArterialFlowFactor.valueChanged.connect(self.setCurveFittingNotDoneBoolean) 
        self.spinBoxParameter1.valueChanged.connect(self.setCurveFittingNotDoneBoolean) 
        self.spinBoxParameter2.valueChanged.connect(self.setCurveFittingNotDoneBoolean) 
        self.spinBoxParameter3.valueChanged.connect(self.setCurveFittingNotDoneBoolean)
        self.spinBoxParameter4.valueChanged.connect(self.setCurveFittingNotDoneBoolean)
        
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
        self.btnFitModel.clicked.connect(self.runCurveFit)
        
        self.btnSaveCSV = QPushButton('Save plot data to CSV file')
        self.btnSaveCSV.setToolTip('Save the data plotted on the graph to a CSV file')
        self.btnSaveCSV.hide()
        modelHorizontalLayout9.addWidget(self.btnSaveCSV)
        self.btnSaveCSV.clicked.connect(self.saveCSVFile)

    def displayModelFittingGroupBox(self):
        """Shows the model fitting group box if a ROI is selected. 
        Otherwise hides the model fitting group box. """
        try:
            ROI = str(self.cmbROI.currentText())
            if ROI != 'Please Select':
                self.groupBoxModel.show()
                self.btnSaveReport.show()
                logger.info("Function displayModelFittingGroupBox called. Model group box and Save Report button shown when ROI = {}".format(ROI))
            else:
                self.groupBoxModel.hide()
                self.cmbAIF.setCurrentIndex(0)
                self.cmbModels.setCurrentIndex(0)
                self.btnSaveReport.hide()
                logger.info("Function displayModelFittingGroupBox called. Model group box and Save Report button hidden.")
        except Exception as e:
            print('Error in function displayModelFittingGroupBox: ' + str(e)) 
            logger.error('Error in function displayModelFittingGroupBox: ' + str(e))

    def setupPlotArea(self, layout):
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

    def setupRightVerticalLayout(self, layout):
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
        self.lblAFFName = QLabel("")
        self.lblAFFValue = QLabel("")
        self.lblAFFConfInt = QLabel("")
        self.lblAFFConfInt.setAlignment(QtCore.Qt.AlignCenter)
        
        gridLayoutResults.addWidget(self.lblHeaderLeft, 1, 1)
        gridLayoutResults.addWidget(self.lblHeaderMiddle, 1, 3)
        gridLayoutResults.addWidget(self.lblHeaderRight, 1, 5)
        gridLayoutResults.addWidget(self.lblParam1Name, 2, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam1Value, 2, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam1ConfInt, 2, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam2Name, 3, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam2Value, 3, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam2ConfInt, 3, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam3Name, 4, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam3Value, 4, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblParam3ConfInt, 4, 5, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblAFFName, 5, 1, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblAFFValue, 5, 3, QtCore.Qt.AlignTop)
        gridLayoutResults.addWidget(self.lblAFFConfInt, 5, 5, QtCore.Qt.AlignTop)

        #Create horizontal layout box to hold TRISTAN & University of Leeds Logos
        horizontalLogoLayout = QHBoxLayout()
        #Add horizontal layout to bottom of the vertical layout
        layout.addLayout(horizontalLogoLayout)
        #Display TRISTAN & University of Leeds Logos in labels
        lblTRISTAN_Logo = QLabel(self)
        lblUoL_Logo = QLabel(self)
        pixmapTRISTAN = QPixmap('logo-tristan.png')
        lblTRISTAN_Logo.setPixmap(pixmapTRISTAN)
        pixmapUoL = QPixmap('uni-leeds-logo.jpg')
        lblUoL_Logo.setPixmap(pixmapUoL)
        #Add labels displaying logos to the horizontal layout, 
        #Tristan on the LHS, UoL on the RHS
        horizontalLogoLayout.addWidget(lblTRISTAN_Logo)
        horizontalLogoLayout.addWidget(lblUoL_Logo)

    def applyStyleSheet(self):
        """Modifies the appearance of the GUI using CSS instructions"""
        try:
            self.setStyleSheet(styleSheet.TRISTAN_GREY)
        except Exception as e:
            print('Error in function applyStyleSheet: ' + str(e))
            logger.error('Error in function applyStyleSheet: ' + str(e))

    def displayModelImage(self):
        """This method takes the name of the model from the drop-down list 
            on the left-hand side of the GUI and displays the corresponding
            image depicting the model and the full name of the model at the
            top of the right-hand side of the GUI."""
        try:
            logger.info('Function displayModelImage called.')
            shortModelName = str(self.cmbModels.currentText())
        
            if shortModelName != 'Select a model':
                modelImageName = TracerKineticModels.getModelImageName(shortModelName)
                pixmapModelImage = QPixmap(modelImageName)
                #Increase the size of the model image
                pMapWidth = pixmapModelImage.width() * 1.35
                pMapHeight = pixmapModelImage.height() * 1.35
                pixmapModelImage = pixmapModelImage.scaled(pMapWidth, pMapHeight, 
                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.lblModelImage.setPixmap(pixmapModelImage)

                longModelName = TracerKineticModels.getLongModelName(shortModelName)
                self.lblModelName.setText(longModelName)
            else:
                self.lblModelImage.clear()
                self.lblModelName.setText('')

        except Exception as e:
            print('Error in function displayModelImage: ' + str(e)) 
            logger.error('Error in function displayModelImage: ' + str(e))  

    def setCurveFittingNotDoneBoolean(self):
        """Sets global boolean _boolCurveFittingDone to false if the 
        plot of the model curve is changed by manually changing the values of 
        model input parameters rather than by running curve fitting."""
        global _boolCurveFittingDone
        _boolCurveFittingDone=False

    def displayOptimumParamaterValuesOnGUI(self):
        """Displays the optimum parameter values resulting from curve fitting 
        with their confidence limits on the right-hand side of the GUI. These
        values are stored in the global list _optimisedParamaterList
        
        Where appropriate decimal fractions are converted to %"""
        try:
            logger.info('Function displayOptimumParamaterValuesOnGUI called.')

            self.lblParam1Name.setText(self.labelParameter1.text())
            parameterValue = round(_optimisedParamaterList[0][0], 3)
            lowerLimit = round(_optimisedParamaterList[0][1], 3)
            upperLimit = round(_optimisedParamaterList[0][2], 3)
            
            if self.spinBoxParameter1.suffix() == '%':
                #convert from decimal fraction to %
                suffix = '%'
                parameterValue = parameterValue * 100.0
                lowerLimit = lowerLimit * 100.0
                upperLimit = upperLimit * 100.0
                
                #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                #with the % equivalent
                _optimisedParamaterList[0][0] = round(parameterValue, 3)
                _optimisedParamaterList[0][1] = round(lowerLimit, 3)
                _optimisedParamaterList[0][2] = round(upperLimit, 3)
            else:
                suffix = ''
            
            self.lblParam1Value.setText(str(parameterValue) + suffix)
            confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
            self.lblParam1ConfInt.setText(confidenceStr) 

            self.lblParam2Name.setText(self.labelParameter2.text())
            parameterValue = round(_optimisedParamaterList[1][0], 3)
            lowerLimit = round(_optimisedParamaterList[1][1], 3)
            upperLimit = round(_optimisedParamaterList[1][2], 3)
            if self.spinBoxParameter2.suffix() == '%':
                suffix = '%'
                parameterValue = parameterValue * 100.0
                lowerLimit = lowerLimit * 100.0
                upperLimit = upperLimit * 100.0
                #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                #with the % equivalent
                _optimisedParamaterList[1][0] = round(parameterValue,3)
                _optimisedParamaterList[1][1] = round(lowerLimit,3)
                _optimisedParamaterList[1][2] = round(upperLimit,3)
            else:
                suffix = ''
            
            self.lblParam2Value.setText(str(parameterValue) + suffix)
            confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
            self.lblParam2ConfInt.setText(confidenceStr) 

            if self.spinBoxParameter3.isHidden() == False:
                self.lblParam3Name.setText(self.labelParameter3.text())
                parameterValue = round(_optimisedParamaterList[2][0], 3)
                lowerLimit = round(_optimisedParamaterList[2][1], 3)
                upperLimit = round(_optimisedParamaterList[2][2], 3)
                nextIndex = 3
                if self.spinBoxParameter3.suffix() == '%':
                    suffix = '%'
                    parameterValue = parameterValue * 100.0
                    lowerLimit = lowerLimit * 100.0
                    upperLimit = upperLimit * 100.0
                    #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                    #with the % equivalent
                    _optimisedParamaterList[2][0] = round(parameterValue, 3)
                    _optimisedParamaterList[2][1] = round(lowerLimit, 3)
                    _optimisedParamaterList[2][2] = round(upperLimit, 3)
                else:
                    suffix = ''
                
                self.lblParam3Value.setText(str(parameterValue) + suffix)
                confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
                self.lblParam3ConfInt.setText(confidenceStr)
            else:
                nextIndex = 2
                
            if self.spinBoxArterialFlowFactor.isHidden() == False:
                self.lblAFFName.setText(self.lblArterialFlowFactor.text())
                parameterValue = _optimisedParamaterList[nextIndex][0]
                lowerLimit = _optimisedParamaterList[nextIndex][1]
                upperLimit = _optimisedParamaterList[nextIndex][2]
                suffix = '%'
                parameterValue = round(parameterValue * 100.0, 3)
                lowerLimit = round(lowerLimit * 100.0, 3)
                upperLimit = round(upperLimit * 100.0, 3)
                #For display in the PDF report, overwrite decimal volume fraction values in  _optimisedParamaterList
                #with the % equivalent
                _optimisedParamaterList[nextIndex][0] = parameterValue
                _optimisedParamaterList[nextIndex][1] = lowerLimit
                _optimisedParamaterList[nextIndex][2] = upperLimit
               
                self.lblAFFValue.setText(str(parameterValue) + suffix)
                confidenceStr = '[{}     {}]'.format(lowerLimit, upperLimit)
                self.lblAFFConfInt.setText(confidenceStr)


        except Exception as e:
            print('Error in function displayOptimumParamaterValuesOnGUI: ' + str(e))
            logger.error('Error in function displayOptimumParamaterValuesOnGUI: ' + str(e))

    def clearOptimumParamaterValuesOnGUI(self):
        """Clears the contents of the labels on the right handside of the GUI.
        That is the parameter values and their confidence limits resulting 
        from curve fitting. """
        try:
            logger.info('Function clearOptimumParamaterValuesOnGUI called.')
            self.lblParam1Name.clear()
            self.lblParam1Value.clear()
            self.lblParam1ConfInt.clear()
            self.lblParam2Name.clear()
            self.lblParam2Value.clear()
            self.lblParam2ConfInt.clear()
            self.lblParam3Name.clear()
            self.lblParam3Value.clear()
            self.lblParam3ConfInt.clear()
            self.lblAFFName.clear()
            self.lblAFFValue.clear()
            self.lblAFFConfInt.clear()
            
        except Exception as e:
            print('Error in function clearOptimumParamaterValuesOnGUI: ' + str(e))
            logger.error('Error in function clearOptimumParamaterValuesOnGUI: ' + str(e))
    
    def saveCSVFile(self):
        """Saves in CSV format the data in the plot on the GUI """ 
        try:
            logger.info('Function saveCSVFile called.')
            modelName = str(self.cmbModels.currentText())
            modelName.replace(" ", "-")
            #Ask the user to specify the path & name of the CSV file. The name of the model is suggested as a default file name.
            CSVFileName, _ = QFileDialog.getSaveFileName(self, caption="Enter CSV file name", directory=DEFAULT_PLOT_DATA_FILE_PATH_NAME, filter="*.csv")
           
           #Check that the user did not press Cancel on the create file dialog
            if CSVFileName:
                logger.info('Function saveCSVFile - csv file name = ' + CSVFileName)
            
                ROI = str(self.cmbROI.currentText())
                AIF = str(self.cmbAIF.currentText())
                with open(CSVFileName, 'w',  newline='') as csvfile:
                    writeCSV = csv.writer(csvfile,  delimiter=',')
                    #write header row
                    writeCSV.writerow(['Time', ROI, AIF, modelName + ' model'])
                    for i, time in enumerate(_concentrationData['Time']):
                         writeCSV.writerow([time, _concentrationData[ROI][i], _concentrationData[AIF][i], _listModel[i]])
                    csvfile.close()

        except csv.Error:
            print('CSV Writer error in function saveCSVFile: file %s, line %d: %s' % (CSVFileName, WriteCSV.line_num, csv.Error))
            logger.error('CSV Writer error in function saveCSVFile: file %s, line %d: %s' % (CSVFileName, WriteCSV.line_num, csv.Error))
        except IOError as IOe:
            print ('IOError in function saveCSVFile: cannot open file ' + CSVFileName + ' or read its data: ' + str(IOe))
            logger.error ('IOError in function saveCSVFile: cannot open file ' + CSVFileName + ' or read its data; ' + str(IOe))
        except RuntimeError as re:
            print('Runtime error in function saveCSVFile: ' + str(re))
            logger.error('Runtime error in function saveCSVFile: ' + str(re))
        except Exception as e:
            print('Error in function saveCSVFile: ' + str(e) + ' at line in CSV file ', WriteCSV.line_num)
            logger.error('Error in function saveCSVFile: ' + str(e) + ' at line in CSV file ', WriteCSV.line_num)

    def clearOptimisedParamaterList(self, callingControl):
        """Clears results of curve fitting from the GUI and from the global list
        _optimisedParamaterList """
        try:
            logger.info('clearOptimisedParamaterList called from ' + callingControl)
            _optimisedParamaterList.clear()
            self.clearOptimumParamaterValuesOnGUI()
        except Exception as e:
            print('Error in function clearOptimisedParamaterList: ' + str(e)) 
            logger.error('Error in function clearOptimisedParamaterList: ' + str(e))

    def displayArterialFlowFactorSpinBox(self):
        if str(self.cmbVIF.currentText()) == 'Please Select':
            self.lblArterialFlowFactor.hide()
            self.spinBoxArterialFlowFactor.hide()
        else:
            self.lblArterialFlowFactor.show()
            self.spinBoxArterialFlowFactor.show()

    def displayFitModelSaveCSVButtons(self):
        """Displays the Fit Model and Save CSV buttons if both a ROI & AIF 
        are selected.  Otherwise hides them."""
        try:
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            if ROI != 'Please Select' and AIF != 'Please Select':
                self.btnFitModel.show()
                self.btnSaveCSV.show()
                logger.info("Function displayFitModelSaveCSVButtons called. Fit Model button shown when ROI = {} and AIF = {}".format(ROI, AIF))
            else:
                self.btnFitModel.hide()
                self.btnSaveCSV.hide()
                logger.info("Function displayFitModelSaveCSVButtons called. Fit Model button hidden.")
        except Exception as e:
            print('Error in function displayFitModelSaveCSVButtons: ' + str(e))
            logger.error('Error in function displayFitModelSaveCSVButtons: ' + str(e))

    def buildParameterArray(self):
        """Forms a 1D array of model input parameters.  Volume fractions are converted 
            from percentages to decimal fractions.
            
            Returns
            -------
                A list of model input parameter values.
            """
        try:
            logger.info('Function buildParameterArray called.')
            initialParametersArray = []
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

            #Only add the Arterial Flow Factor if a VIF has been selected
            #and the Arterial Flow Factor spinbox is therefore visible.
            if self.spinBoxArterialFlowFactor.isHidden() == False:
                arterialFlowFactor = self.spinBoxArterialFlowFactor.value()/100
                initialParametersArray.append(arterialFlowFactor)

            return initialParametersArray
        except Exception as e:
            print('Error in function buildParameterArray ' + str(e))
            logger.error('Error in function buildParameterArray '  + str(e))

    def blockSpinBoxSignals(self, boolBlockSignal):
        """Blocks signals from spinboxes that fire events.  
           Thus allowing spinbox values to be set programmatically 
           without causing a method connected to one of their events to be executed."""
        logger.info('Function blockSpinBoxSignals called.')
        self.spinBoxArterialFlowFactor.blockSignals(boolBlockSignal)
        self.spinBoxParameter1.blockSignals(boolBlockSignal)
        self.spinBoxParameter2.blockSignals(boolBlockSignal)
        self.spinBoxParameter3.blockSignals(boolBlockSignal)

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
            self.blockSpinBoxSignals(True)
        
            if self.spinBoxParameter1.suffix() == '%':
                self.spinBoxParameter1.setValue(optimumParams[0]* 100) #Convert Volume fraction to %
            else:
                self.spinBoxParameter1.setValue(optimumParams[0])
            if self.spinBoxParameter2.suffix() == '%':
                self.spinBoxParameter2.setValue(optimumParams[1]* 100) #Convert Volume fraction to %
            else:
                self.spinBoxParameter2.setValue(optimumParams[1])
            if self.spinBoxParameter3.isHidden() == False:
                nextIndex = 3
                if self.spinBoxParameter3.suffix() == '%':
                    self.spinBoxParameter3.setValue(optimumParams[2]* 100) #Convert Volume fraction to %
                else:
                    self.spinBoxParameter3.setValue(optimumParams[2])
            else:
                nextIndex = 2

            if self.spinBoxArterialFlowFactor.isHidden() == False:
                self.spinBoxArterialFlowFactor.setValue(optimumParams[nextIndex]* 100) #Convert decimal fraction to %
            
            self.blockSpinBoxSignals(False)
        except Exception as e:
            print('Error in function setParameterSpinBoxesWithOptimumValues ' + str(e))
            logger.error('Error in function setParameterSpinBoxesWithOptimumValues '  + str(e))

    def calculate95ConfidenceLimits(self, numDataPoints, numParams, optimumParams, paramCovarianceMatrix):
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
            logger.info('Function calculate95ConfidenceLimits called: numDataPoints ={}, numParams={}, optimumParams={}, paramCovarianceMatrix={}'
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
                _optimisedParamaterList[counter].append(numParams)
                _optimisedParamaterList[counter].append(round((numParams - sigma*tval), 5))
                _optimisedParamaterList[counter].append(round((numParams + sigma*tval), 5))
                i+=1
            logger.info('In calculate95ConfidenceLimits, _optimisedParamaterList = {}'.format(_optimisedParamaterList))
        except Exception as e:
            print('Error in function calculate95ConfidenceLimits ' + str(e))
            logger.error('Error in function calculate95ConfidenceLimits '  + str(e))  

    def runCurveFit(self):
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
            initialParametersArray = self.buildParameterArray()

            #Get name of region of interest, arterial and venal input functions
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())

            #Get arrays of data corresponding to the above 3 regions 
            #and the time over which the measurements were made.
            arrayTimes = np.array(_concentrationData['Time'], dtype='float')
            arrayROIConcs = np.array(_concentrationData[ROI], dtype='float')
            arrayAIFConcs = np.array(_concentrationData[AIF], dtype='float')

            if VIF != 'Please Select':
                boolDualInput = True
                arrayVIFConcs = np.array(_concentrationData[VIF], dtype='float')
            else:
                #Create empty dummy array to act as place holder in  
                #TracerKineticModels.curveFit function call 
                arrayVIFConcs = []
                boolDualInput = False
            
            if self.cboxConstaint.isChecked():
                addConstraint = True
            else:
                addConstraint = False

            #Get the name of the model to be fitted to the ROI curve
            modelName = str(self.cmbModels.currentText())
            #Call curve fitting routine
            logger.info('TracerKineticModels.curveFit called with model {}, parameters {} and Constraint = {}'.format(modelName, initialParametersArray, addConstraint))
            optimumParams, paramCovarianceMatrix = TracerKineticModels.curveFit(modelName, arrayTimes, 
                 arrayAIFConcs, arrayVIFConcs, arrayROIConcs, initialParametersArray, addConstraint, boolDualInput)
       
            _boolCurveFittingDone = True 
            logger.info('TracerKineticModels.curveFit returned optimum parameters {} with confidence levels {}'.format(optimumParams, paramCovarianceMatrix))
            
            #Display results of curve fitting  
            #(optimum model parameter values) on GUI.
            self.setParameterSpinBoxesWithOptimumValues(optimumParams)

            #Plot the best curve on the graph
            self.plot('runCurveFit')

            #Determine 95% confidence limits.
            numDataPoints = arrayROIConcs.size
            numParams = len(initialParametersArray)
            self.calculate95ConfidenceLimits(numDataPoints, numParams, 
                                    optimumParams, paramCovarianceMatrix)
            
            self.displayOptimumParamaterValuesOnGUI()
            
        except ValueError as ve:
            print ('Value Error: runCurveFit with model ' + modelName + ': '+ str(ve))
            logger.error('Value Error: runCurveFit with model ' + modelName + ': '+ str(ve))
        except Exception as e:
            print('Error in function runCurveFit with model ' + modelName + ': ' + str(e))
            logger.error('Error in function runCurveFit with model ' + modelName + ': ' + str(e))
    
    def savePDFReport(self):
        """Creates and saves a report of the plot on the GUI."""
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
                modelName = str(self.cmbModels.currentText())
                
                #Save a png of the concentration/time plot for display 
                #in the PDF report.
                self.figure.savefig(fname=IMAGE_NAME, dpi=150)  #dpi=150 so as to get a clear image in the PDF report
                
                parameter1 = self.spinBoxParameter1.value()
                parameter2 = self.spinBoxParameter2.value()
                parameter3 = self.spinBoxParameter3.value()
                arterialFlowFractionValue = self.spinBoxArterialFlowFactor.value()
                
##                def createAndSavePDFReport(self, fileName, _dataFileName, modelName, imageName, 
#                               parameter1Text, parameter1Value,
#                               parameter2Text, parameter2Value,
#                               parameter3Text = None, parameter3Value = None, confidenceLimitsArray =[], _boolCurveFittingDone=True)
                
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                if modelName ==  'One Compartment':
                    pdf.createAndSavePDFReport(reportFileName, _dataFileName, modelName, IMAGE_NAME, LABEL_PARAMETER_Vp, parameter1, LABEL_PARAMETER_Fp, parameter2, None, None, _optimisedParamaterList, _boolCurveFittingDone)
                elif modelName ==  'Extended Tofts':
                    pdf.createAndSavePDFReport(reportFileName, _dataFileName, modelName, IMAGE_NAME, LABEL_PARAMETER_Vp, parameter1, LABEL_PARAMETER_Ve, parameter2, LABEL_PARAMETER_Ktrans, parameter3, _optimisedParamaterList, _boolCurveFittingDone)
                elif modelName == 'High-Flow Gadoxetate':
                    pdf.createAndSavePDFReport(reportFileName, _dataFileName, modelName, IMAGE_NAME, LABEL_PARAMETER_Kce, parameter1, LABEL_PARAMETER_Ve, parameter2, LABEL_PARAMETER_Kbc, parameter3, _optimisedParamaterList, _boolCurveFittingDone)
                QApplication.restoreOverrideCursor()

                #Delete image file
                os.remove(IMAGE_NAME)
                logger.info('PDF Report created called ' + reportFileName)
        except Exception as e:
            print('Error in function savePDFReport: ' + str(e))
            logger.error('Error in function savePDFReport: ' + str(e))
       
    def loadDataFile(self):
        """Loads the contents of a CSV file containing time and concentration data
        into a dictionary of lists. The key is the name of the organ or 'time' and 
        the corresponding value is a list of concentrations 
        (or times when the key is 'time')
        
        The following validation is applied to the data file:
            -The CSV file must contain at least 3 columns of data separated by commas.
            -The first row of the CSV file must be a header row with column names.
            -The first column in the CSV file must contain time data."""
        global _concentrationData
        global _dataFileName

        #clear the global dictionary of previous data
        _concentrationData.clear()
        
        self.hideAllControlsOnGUI()
        
        try:
            #get the data file in csv format
            #filter parameter set so that the user can only open a csv file
            _dataFileName, _ = QFileDialog.getOpenFileName(parent=self, caption="Select csv file", filter="*.csv")
            if os.path.exists(_dataFileName):
                with open(_dataFileName, newline='') as csvfile:
                    line = csvfile.readline()
                    if line.count(',') < (MIN_NUM_COLUMNS_CSV_FILE - 1):
                        QMessageBox().warning(self, "CSV data file", "The CSV file must contain at least 3 columns of data separated by commas.  The first column must contain time data.", QMessageBox.Ok)
                        raise RuntimeError('The CSV file must contain at least 3 columns of data separated by commas.')
                    
                    #go back to top of the file
                    csvfile.seek(0)
                    
                    #Check for a header row in the CSV file
                    sniffer = csv.Sniffer()
                    has_header = csv.Sniffer().has_header(csvfile.read(16384))
                    if has_header == False:
                        QMessageBox().warning(self, "CSV data file", "The first row of the CSV file must be a header row with column names", QMessageBox.Ok)
                        raise RuntimeError('The CSV file must have a header row')
                    
                    #go back to top of the file
                    csvfile.seek(0)
                    readCSV = csv.reader(csvfile, delimiter=',')
                    #Get column header labels
                    headers = next(readCSV, None)  # returns the headers or `None` if the input is empty
                    if headers:
                        firstColumnHeader = headers[0].strip().lower()
                        if firstColumnHeader != "time":
                            QMessageBox().warning(self, "CSV data file", "The first column must contain time data.", QMessageBox.Ok)
                            raise RuntimeError('The first column in the CSV file must contain time data.')    

                    logger.info('CSV data file {} loaded'.format(_dataFileName))
                    
                    #Extract data filename from the full data file path
                    _dataFileName = os.path.basename(_dataFileName)
                    self.lblDataFileName.setText('File ' + _dataFileName + ' loaded')

                    #Column headers form the keys in the dictionary called _concentrationData
                    for header in headers:
                        _concentrationData[header.title()]=[]
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
                                    _concentrationData[key].append(int(row[colNum]))
                                else:
                                    _concentrationData[key].append(float(row[colNum]))
                                colNum+=1           
                csvfile.close()

                self.configureGUIAfterLoadingData()
                #clear the plot in case it is showing data from a previous data file
                self.figure.clear()

        except csv.Error:
            print('CSV Reader error in function loadDataFile: file %s, line %d: %s' % (_dataFileName, readCSV.line_num, csv.Error))
            logger.error('CSV Reader error in function loadDataFile: file %s, line %d: %s' % (_dataFileName, readCSV.line_num, csv.Error))
        except IOError:
            print ('IOError in function loadDataFile: cannot open file' + _dataFileName + ' or read its data')
            logger.error ('IOError in function loadDataFile: cannot open file' + _dataFileName + ' or read its data')
        except RuntimeError as re:
            print('Runtime error in function loadDataFile: ' + str(re))
            logger.error('Runtime error in function loadDataFile: ' + str(re))
        except Exception as e:
            print('Error in function loadDataFile: ' + str(e) + ' at line in CSV file ', readCSV.line_num)
            logger.error('Error in function loadDataFile: ' + str(e) + ' at line in CSV file ', readCSV.line_num)

    def hideAllControlsOnGUI(self):
        """Hides/clears all the widgets on left-hand side of the application 
        except for the Load & Display Data and Exit buttons.  
        It is called before a data file is loaded in case the Cancel button on the dialog
        is clicked.  This prevents the scenario where buttons are displayed but there is no
        data loaded to process when they are clicked."""

        logger.info('Function hideAllControlsOnGUI called')
        #Clear label displaying name of the datafile
        self.lblDataFileName.setText('')

        self.lblROI.hide()
        self.cmbROI.hide()
        self.groupBoxModel.hide()
        self.btnFitModel.hide()
        self.btnSaveCSV.hide()

    def configureGUIAfterLoadingData(self):
        """After successfully loading a datafile, this method loads a list of
        organs into ROI, AIF & VIF drop-down lists and displays 
        the ROI drop-down list."""
        try:
            #Data file loaded OK, so set up the GUI
            #Reset and enable dropdown list of models
            self.cmbROI.clear()
            self.cmbAIF.clear()
            self.cmbVIF.clear()
            
            #Create a list of organs for which concentrations are
            #provided in the data input file.  See loadDataFile method.
            organArray = []
            organArray = self.returnListOrgans()
            
            self.cmbROI.addItems(organArray)
            self.cmbAIF.addItems(organArray)
            self.cmbVIF.addItems(organArray)
            self.lblROI.show()
            self.cmbROI.show()

            logger.info('Function configureGUIAfterLoadingData called and the following organ list loaded: {}'.format(organArray))
        except RuntimeError as re:
            print('runtime error in function configureGUIAfterLoadingData: ' + str(re) )
            logger.error('runtime error in function configureGUIAfterLoadingData: ' + str(re) )
        except Exception as e:
            print('Error in function configureGUIAfterLoadingData: ' + str(e) )
            logger.error('Error in function configureGUIAfterLoadingData: ' + str(e))
        
    def returnListOrgans(self):
        """Builds a list of organs from the headers in the CSV data file. 
        The CSV data file comprises columns of concentration data for a
        set of organs.  Each column of concentration data is labeled by
        header giving the name of organ.
        
        Returns
        -------
            A list of organs for which there is concentration data.
        """
        try:
            logger.info('Function returnListOrgans called')
            organList =[]
            organList.append('Please Select') #First item at the top of the drop-down list
            for key in _concentrationData:
                if key.lower() != 'time' and key.lower() != 'model':  
                    organList.append(str(key))       
            return organList
        except RuntimeError as re:
            print('runtime error in function returnListOrgans' + str(re))
            logger.error('runtime error in function returnListOrgans' + str(re))
        except Exception as e:
            print('Error in function returnListOrgans: ' + str(e))
            logger.error('Error in function returnListOrgans: ' + str(e))
    
    def initialiseParameterSpinBoxes(self):
        """Reset model parameter spinboxes with typical initial values for each model"""
        try:
            #Remove suffixes from all spinboxes 
            self.spinBoxParameter1.setSuffix('')
            self.spinBoxParameter2.setSuffix('')
            self.spinBoxParameter3.setSuffix('')
            self.spinBoxParameter4.setSuffix('')
            self.spinBoxParameter1.setEnabled(True)

            #Block signals from spinboxes, so that setting initial values
            #does not trigger an event.
            self.blockSpinBoxSignals(True)
            self.spinBoxArterialFlowFactor.setValue(DEFAULT_VALUE_Fa)
            
            modelName = str(self.cmbModels.currentText())
            logger.info('Function initialiseParameterSpinBoxes called when model = ' + modelName)
            if modelName == '2-2CFM':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setRange(0, 100)
                self.spinBoxParameter1.setSingleStep(0.1)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter1.setSuffix('%')

                self.spinBoxParameter2.setDecimals(4)
                self.spinBoxParameter2.setRange(0, 0.01)
                self.spinBoxParameter2.setSingleStep(0.0001)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Fp)

                self.spinBoxParameter3.setDecimals(5)
                self.spinBoxParameter3.setRange(0.0, 0.1)
                self.spinBoxParameter3.setSingleStep(0.00001)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Khe)
                
                self.spinBoxParameter4.setDecimals(5)
                self.spinBoxParameter4.setRange(0.0, 0.1)
                self.spinBoxParameter4.setSingleStep(0.00001)
                self.spinBoxParameter4.setValue(DEFAULT_VALUE_Kbh)
                
            elif modelName == 'HF2-2CFM':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setRange(0, 100)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter1.setSuffix('%')
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Khe)
                self.spinBoxParameter2.setRange(0, 0.1)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbh)
                self.spinBoxParameter3.setRange(0, 0.1)
            elif modelName == 'HF1-2CFM':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter1.setSuffix('%')
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Khe)
                self.spinBoxParameter2.setRange(0, 0.1)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbh)
                self.spinBoxParameter3.setRange(0, 0.1)
            elif modelName == 'HF1-2CFM-FixVe':
                self.spinBoxParameter1.setDecimals(2)
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter1.setEnabled(False)
                self.spinBoxParameter1.setSuffix('%')
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Khe)
                self.spinBoxParameter2.setRange(0, 0.1)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbh)
                self.spinBoxParameter3.setRange(0, 0.1)
            #Models no longer used
            #elif modelName ==  'Extended Tofts':
            #    self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
            #    self.spinBoxParameter1.setSuffix('%')
            #    self.spinBoxParameter2.setValue(DEFAULT_VALUE_Fp)
            #    self.spinBoxParameter3.setValue(DEFAULT_VALUE_Ktrans)
            #elif modelName == 'High-Flow Gadoxetate':
            #    self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
            #    self.spinBoxParameter1.setSuffix('%')
            #    self.spinBoxParameter2.setValue(DEFAULT_VALUE_Kce)
            #    self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbc)
            #elif modelName ==  'One Compartment':
            #    self.spinBoxParameter1.setValue(DEFAULT_VALUE_Vp)
            #    self.spinBoxParameter1.setSuffix('%')
            #    self.spinBoxParameter2.setValue(DEFAULT_VALUE_Fp)

            self.blockSpinBoxSignals(False)
        except Exception as e:
            print('Error in function initialiseParameterSpinBoxes: ' + str(e) )
            logger.error('Error in function initialiseParameterSpinBoxes: ' + str(e) )

    def configureGUIForEachModel(self):
        """When a model is selected, this method configures the appearance of the GUI
        accordingly.  For example, spinboxes for the input of model parameter values are
        given an appropriate label."""
        try:
            modelName = str(self.cmbModels.currentText())
            logger.info('Function configureGUIForEachModel called when model = ' + modelName)
            
            #self.cboxDelay.show()
            self.cboxConstaint.show()
            self.cboxConstaint.setChecked(False)
            self.btnReset.show()
            self.btnSaveReport.show()
            #Remove results of curve fitting of the previous model
            self.clearOptimumParamaterValuesOnGUI() 
            self.initialiseParameterSpinBoxes() #Typical initial values for each model
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
            elif modelName == 'HF1-2CFM':
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
            elif modelName == 'HF1-2CFM-FixVe':
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
            elif modelName ==  'Extended Tofts':
                self.labelParameter1.setText(LABEL_PARAMETER_Vp)
                self.labelParameter1.show()
                self.labelParameter2.setText(LABEL_PARAMETER_Ve)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_Ktrans)
                self.labelParameter3.show()
            elif modelName == 'High-Flow Gadoxetate':
                self.labelParameter1.setText(LABEL_PARAMETER_Ve)
                self.labelParameter1.show()
                self.labelParameter2.setText(LABEL_PARAMETER_Kce)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_Kbc)
                self.labelParameter3.show()
            elif modelName ==  'One Compartment':
                self.labelParameter1.setText(LABEL_PARAMETER_Vp)
                self.labelParameter1.show()
                self.labelParameter2.setText(LABEL_PARAMETER_Fp)
                self.labelParameter2.show()
                
                #Hide this spinbox & label as this model does not have a third parameter
                self.spinBoxParameter3.hide() 
                self.labelParameter3.hide()
                self.labelParameter3.clear()
            else:  #No model is selected
                self.lblAIF.hide()
                self.cmbAIF.hide()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.cboxDelay.hide()
                self.cboxConstaint.hide()
                self.btnReset.hide()
                self.spinBoxParameter3.hide()
                self.spinBoxParameter1.hide()
                self.spinBoxParameter2.hide()
                self.spinBoxParameter3.hide()
                self.labelParameter1.hide()
                self.labelParameter2.hide()
                self.labelParameter3.hide()
                self.labelParameter1.clear()
                self.labelParameter2.clear()
                self.labelParameter3.clear()
                
                self.cmbAIF.setCurrentIndex(0)
                self.btnFitModel.hide()
                self.btnSaveReport.hide()
                self.btnSaveCSV.hide()
        except Exception as e:
            print('Error in function configureGUIForEachModel: ' + str(e) )
            logger.error('Error in function configureGUIForEachModel: ' + str(e) )
            
    def getScreenResolution(self):
        """Determines the screen resolution of the device running this software.
        
        Returns
        -------
            Returns the width & height of the device screen in pixels.
        """
        try:
            width, height = pyautogui.size()
            logger.info('Function getScreenResolution called. Screen width = {}, height = {}.'.format(width, height))
            return width, height
        except Exception as e:
            print('Error in function getScreenResolution: ' + str(e) )
            logger.error('Error in function getScreenResolution: ' + str(e) )
        
    def determineTextSize(self):
        """Determines the optimum size for the title & labels on the 
           matplotlib graph from the screen resolution.
           
           Returns
           -------
              tick label size, xy axis label size & title size
           """
        try:
            logger.info('Function determineTextSize called.')
            width, _ = self.getScreenResolution()
            
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
            print('Error in function determineTextSize: ' + str(e) )
            logger.error('Error in function determineTextSize: ' + str(e) )
    
    def plot(self, nameCallingFunction):
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

            self.figure.clear()
            
            # create an axis
            ax = self.figure.add_subplot(111)

            #Get the optimum label size for the screen resolution.
            tickLabelSize, xyAxisLabelSize, titleSize = self.determineTextSize()
            
            #Set size of the x,y axis tick labels
            ax.tick_params(axis='both', which='major', labelsize=tickLabelSize)

            #Get the name of the model 
            modelName = str(self.cmbModels.currentText())
            
            arrayTimes = np.array(_concentrationData['Time'], dtype='float')
            ROI = str(self.cmbROI.currentText())
            if ROI != 'Please Select':
                arrayROIConcs = np.array(_concentrationData[ROI], dtype='float')
                ax.plot(arrayTimes, arrayROIConcs, 'b.-', label= ROI)

            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())

            logger.info('Function plot called from ' + nameCallingFunction + ' when ROI={}, AIF={} and VIF={}'.format(ROI, AIF, VIF))

            if AIF != 'Please Select':
                arrayAIFConcs = np.array(_concentrationData[AIF], dtype='float')
                ax.plot(arrayTimes, arrayAIFConcs, 'r.-', label= AIF)
                parameterArray = self.buildParameterArray()

                if VIF == 'Please Select':
                    boolDualInput = False
                    arrayVIFConcs = []
                else:
                    boolDualInput = True
                    arrayVIFConcs = np.array(_concentrationData[VIF], dtype='float')
                    ax.plot(arrayTimes, arrayVIFConcs, 'k.-', label= VIF)
                    
                logger.info('TracerKineticModels.modelSelector called when model ={} and parameter array = {}'. format(modelName, parameterArray))        
                _listModel = TracerKineticModels.modelSelector(modelName, arrayTimes, 
                        arrayAIFConcs, parameterArray, boolDualInput, arrayVIFConcs)
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
                print('Error in function plot when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
                logger.error('Error in function plot when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
    
    def exitApp(self):
        """Closes the Model Fitting application."""
        logger.info("Application closed using the Exit button.")
        sys.exit(0)  
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ModelFittingApp()
    main.show()
    sys.exit(app.exec_())
