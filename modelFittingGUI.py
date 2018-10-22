import sys
import csv
import os.path
import numpy as np
import pyautogui
import logging

from PyQt5.QtGui import QCursor, QIcon, QFont, QPixmap
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog,  QApplication, QPushButton, \
     QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel, QDoubleSpinBox, \
     QMessageBox, QFileDialog, QCheckBox, QLineEdit, QSizePolicy, QGridLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from scipy.stats.distributions import  t

#To remove unwanted default buttons in the Navigation Toolbar
#create a subclass of the NavigationToolbar class 
#(from from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar)
# that only defines the desired buttons
class NavigationToolbar(NavigationToolbar):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

#Import module containing model definitions
import TracerKineticModels
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

########################################
##              CONSTANTS             ##
########################################
WINDOW_TITLE = 'Model-fitting of dynamic contrast-enhanced MRI'
REPORT_TITLE = 'Model-fitting of dynamic contrast-enhanced MRI'
IMAGE_NAME = 'model.png'
MIN_NUM_COLUMNS_CSV_FILE = 3
DEFAULT_VALUE_Vp = 5.0
DEFAULT_VALUE_Ve = 0.02
DEFAULT_VALUE_Ktrans = 0.10
DEFAULT_VALUE_Fp = 1
DEFAULT_VALUE_Kce = 2
DEFAULT_VALUE_Kbc = 0.3
LABEL_PARAMETER_1A = 'Plasma Volume Fraction, \n Vp(%)'
LABEL_PARAMETER_1B = 'Hepatocellular Uptake Rate, \n Kce (mL/100mL/min)'
LABEL_PARAMETER_2A = 'Extracellular Vol Fraction, \n Ve (%)'
LABEL_PARAMETER_2B = 'Plasma Flow Rate, \n Fp (ml/min)'
LABEL_PARAMETER_3A = 'Transfer Rate Constant, \n Ktrans (1/min)'
LABEL_PARAMETER_3B = 'Biliary Efflux Rate, \n Kbc (mL/100mL/min)'
DEFAULT_REPORT_FILE_PATH_NAME = 'report.pdf'
DEFAULT_PLOT_DATA_FILE_PATH_NAME = 'plot.csv'
LOG_FILE_NAME = "ModelFitting.log"
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

    def __init__(self, parent=None):
        """__init__ Creates the user interface. """
        super(ModelFittingApp, self).__init__(parent)
      
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon('TRISTAN LOGO.jpg'))
        width, height = self.getScreenResolution()
        self.setGeometry(width*0.05, height*0.25, width*0.9, height*0.5)
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint |  QtCore.Qt.WindowCloseButtonHint)
        
        self.applyStyleSheet()
       
        #Setup the layouts, the containers for controls
        verticalLayoutLeft, verticalLayoutMiddle, verticalLayoutRight = self.setupLayouts()
        
        #Add controls to the left-hand side vertical layout
        self.setupLeftVerticalLayout(verticalLayoutLeft)

        #Set up the graph to plot concentration data on
        # the middle vertical layout
        self.setupPlotArea(verticalLayoutMiddle)
        
        #Create a group box and place it in the right-handside vertical layout
        #Also add a label to hold the TRISTAN Logo
        self.setupRightVerticalLayout(verticalLayoutRight)

        logger.info("GUI created successfully.")


    def setupLayouts(self):
        #Start with an overall horizontal layout
        #and place 3 vertical layouts within it
        horizontalLayout = QHBoxLayout()
        verticalLayoutLeft = QVBoxLayout()
        verticalLayoutMiddle = QVBoxLayout()
        verticalLayoutRight = QVBoxLayout()
        
        self.setLayout(horizontalLayout)
        horizontalLayout.addLayout(verticalLayoutLeft,2)
        horizontalLayout.addLayout(verticalLayoutMiddle,3)
        horizontalLayout.addLayout(verticalLayoutRight,2)
        return verticalLayoutLeft, verticalLayoutMiddle, verticalLayoutRight

    def setupPlotArea(self, layout):
        self.figure = plt.figure(figsize=(5, 4), dpi=100)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        #Middle layout box holds the graph and associated toolbar
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def setupModelGroupBox(self, layout, verticalSpacer):
        self.groupBoxModel = QGroupBox('Model Fitting')
        #Set alignment of group box label
        self.groupBoxModel.setAlignment(QtCore.Qt.AlignHCenter)
        self.groupBoxModel.hide()
        layout.addWidget(self.groupBoxModel)
        layout.addItem(verticalSpacer)
        
        #Create horizontal layouts, then 
        #add them to a vertical layout, then
        #the vertical layout to the group box
        modelHorizontalLayout2 = QHBoxLayout()
        modelHorizontalLayout3 = QHBoxLayout()
        modelHorizontalLayout4 = QHBoxLayout()
        modelHorizontalLayoutReset = QHBoxLayout()
        modelHorizontalLayout5 = QHBoxLayout()
        modelHorizontalLayout6 = QHBoxLayout()
        modelHorizontalLayout7 = QHBoxLayout()
        modelHorizontalLayout8 = QHBoxLayout()
        modelHorizontalLayout9 = QHBoxLayout()
        modelVerticalLayout = QVBoxLayout()
        modelVerticalLayout.setAlignment(QtCore.Qt.AlignTop) 
        modelVerticalLayout.addLayout(modelHorizontalLayout2)
        modelVerticalLayout.addLayout(modelHorizontalLayout3)
        modelVerticalLayout.addLayout(modelHorizontalLayout4)
        modelVerticalLayout.addLayout(modelHorizontalLayoutReset)
        modelVerticalLayout.addLayout(modelHorizontalLayout5)
        modelVerticalLayout.addLayout(modelHorizontalLayout6)
        modelVerticalLayout.addLayout(modelHorizontalLayout7)
        modelVerticalLayout.addLayout(modelHorizontalLayout8)
        modelVerticalLayout.addLayout(modelHorizontalLayout9)
        self.groupBoxModel.setLayout(modelVerticalLayout)
        
        #Create dropdown list to hold names of models
        self.modelLabel = QLabel("Model:")
        self.modelLabel.setAlignment(QtCore.Qt.AlignRight)
        self.cmbModels = QComboBox()
        #Populate the combo box with names of models in the modelNames list
        self.cmbModels.setToolTip('Select a model to fit to the data')
        self.cmbModels.addItems(TracerKineticModels.modelNames)
        self.cmbModels.setCurrentIndex(0) #Display "Select a Model"
        self.cmbModels.currentIndexChanged.connect(self.configureGUIForEachModel)
        self.cmbModels.currentIndexChanged.connect(lambda: self.clearOptimisedParamaterList('cmbModels')) 
        self.cmbModels.activated.connect(lambda: self.plot('cmbModels'))
        
        #Create dropdown lists for selection of AIF & VIF
        self.lblAIF = QLabel("Arterial Input Function:")
        self.lblAIF.setAlignment(QtCore.Qt.AlignRight)
        self.cmbAIF = QComboBox()
        self.cmbAIF.setToolTip('Select Arterial Input Function')
        self.lblVIF = QLabel("Venal Input Function:")
        self.lblVIF.setAlignment(QtCore.Qt.AlignRight)
        self.cmbVIF = QComboBox()
        self.cmbVIF.setToolTip('Select Venal Input Function')
        self.cmbROI.activated.connect(lambda: self.plot('cmbROI'))
        self.cmbROI.currentIndexChanged.connect(self.displayModelFittingGroupBox)
        self.cmbAIF.activated.connect(lambda: self.plot('cmbAIF'))
        self.cmbAIF.currentIndexChanged.connect(self.displayFitModelSaveCSVButtons)
        self.cmbVIF.activated.connect(lambda: self.plot('cmbVIF'))
        self.lblAIF.hide()
        self.cmbAIF.hide()
        self.lblVIF.hide()
        self.cmbVIF.hide()
        self.cmbROI.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbAIF.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbVIF.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        #Add lists and their labels to the horizontal layouts
        modelHorizontalLayout2.insertStretch (0, 2)
        modelHorizontalLayout2.addWidget(self.modelLabel)
        modelHorizontalLayout2.addWidget(self.cmbModels)
        modelHorizontalLayout3.addWidget(self.lblAIF)
        modelHorizontalLayout3.addWidget(self.cmbAIF)
        modelHorizontalLayout4.addWidget(self.lblVIF)
        modelHorizontalLayout4.addWidget(self.cmbVIF)
        
        self.cboxDelay = QCheckBox('Delay', self)
        self.cboxConstaint = QCheckBox('Constraint', self)
        #self.cboxConstaint.clicked.connect(self.setParameterSpinBoxesToConstraintValue)
        self.cboxDelay.hide()
        self.cboxConstaint.hide()
        self.btnReset = QPushButton('Reset')
        self.btnReset.setToolTip('Reset parameters to their default values.')
        self.btnReset.hide()
        self.btnReset.clicked.connect(self.initialiseParameterSpinBoxes)
        self.btnReset.clicked.connect(lambda: self.plot('Reset Button'))
        modelHorizontalLayoutReset.addWidget(self.cboxDelay)
        modelHorizontalLayoutReset.addWidget(self.cboxConstaint)
        modelHorizontalLayoutReset.addWidget(self.btnReset)
        
        #Create spinboxes and their labels
        #Label text set in function configureGUIForEachModel when the model is selected
        self.labelParameter1 = QLabel("")
        self.labelParameter2 = QLabel("")
        self.labelParameter3 = QLabel("")
        self.labelParameter1.setWordWrap(True)
        self.labelParameter2.setWordWrap(True)
        self.labelParameter3.setWordWrap(True)
        self.spinBoxParameter1 = QDoubleSpinBox()
        self.spinBoxParameter1.setRange(-100, 1000)
        self.spinBoxParameter1.setSingleStep(0.1)
        self.spinBoxParameter1.setMinimumSize(self.spinBoxParameter1.minimumSizeHint())
        self.spinBoxParameter1.resize(self.spinBoxParameter1.sizeHint())
        self.spinBoxParameter2 = QDoubleSpinBox()
        self.spinBoxParameter2.setRange(-100, 1000)
        self.spinBoxParameter2.setSingleStep(0.1)
        self.spinBoxParameter2.resize(self.spinBoxParameter2.sizeHint())
        self.spinBoxParameter3 = QDoubleSpinBox()
        self.spinBoxParameter3.setRange(-100, 1000)
        self.spinBoxParameter3.setSingleStep(0.01)
        self.spinBoxParameter3.resize(self.spinBoxParameter3.sizeHint())
        self.spinBoxParameter1.hide()
        self.spinBoxParameter2.hide()
        self.spinBoxParameter3.hide()
        self.spinBoxParameter1.valueChanged.connect(lambda: self.plot('spinBoxParameter1')) 
        self.spinBoxParameter2.valueChanged.connect(lambda: self.plot('spinBoxParameter2')) 
        self.spinBoxParameter3.valueChanged.connect(lambda: self.plot('spinBoxParameter3'))
        
        #Place spin boxes and their labels in horizontal layouts
        modelHorizontalLayout5.addWidget(self.labelParameter1)
        modelHorizontalLayout5.addWidget(self.spinBoxParameter1)
        modelHorizontalLayout6.addWidget(self.labelParameter2)
        modelHorizontalLayout6.addWidget(self.spinBoxParameter2)
        modelHorizontalLayout7.addWidget(self.labelParameter3)
        modelHorizontalLayout7.addWidget(self.spinBoxParameter3)
        
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

    def setupLeftVerticalLayout(self, layout):
        #Create Load Data File Button
        self.btnLoadDisplayData = QPushButton('Load and display data.')
        self.btnLoadDisplayData.setToolTip('Open file dialog box to select the data file')
        self.btnLoadDisplayData.setShortcut("Ctrl+L")
        self.btnLoadDisplayData.setAutoDefault(False)
        self.btnLoadDisplayData.resize(self.btnLoadDisplayData.minimumSizeHint())
        self.btnLoadDisplayData.clicked.connect(self.loadDataFile)

        #Create label to display the name of the loaded data file
        self.lblDataFileName = QLabel('')
        
        #Add Load data file button to the top of the vertical layout
        verticalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(verticalSpacer)
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
        
        #Below Load Data button add ROI list
        ROI_HorizontalLayout = QHBoxLayout()
        ROI_HorizontalLayout.addWidget(self.lblROI)
        ROI_HorizontalLayout.addWidget(self.cmbROI)
        layout.addLayout(ROI_HorizontalLayout)
        
        #Create a group box, add controls 
        #and place it in the left-handside vertical layout
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

    def setupRightVerticalLayout(self, layout):
        """Creates and adds controls to the right hand side vertical layout for the 
        display of the results of curve fitting. """

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
            self.setStyleSheet(styleSheet.GREY_SCALE)
        except Exception as e:
            print('Error in function applyStyleSheet: ' + str(e))
            logger.error('Error in function applyStyleSheet: ' + str(e))

    

    #def returnErrorString(self):
    #    return 'Error: {}. {}, line: {}'.format(sys.exc_info()[0],
    #                                     sys.exc_info()[1],
    #                                     sys.exc_info()[2].tb_lineno)

    def displayOptimumParamaterValuesOnGUI(self):
        try:
            logger.info('Function displayOptimumParamaterValuesOnGUI called.')
            self.lblParam1Name.setText(self.labelParameter1.text())
            self.lblParam1Value.setText(str(round(_optimisedParamaterList[0][0], 5)))
            confidenceStr = '[{}     {}]'.format(_optimisedParamaterList[0][1], _optimisedParamaterList[0][2])
            self.lblParam1ConfInt.setText(confidenceStr) 
            self.lblParam2Name.setText(self.labelParameter2.text())
            self.lblParam2Value.setText(str(round(_optimisedParamaterList[1][0], 5)))
            confidenceStr = '[{}     {}]'.format(_optimisedParamaterList[1][1], _optimisedParamaterList[1][2])
            self.lblParam2ConfInt.setText(confidenceStr)

            if len(_optimisedParamaterList) == 3:
                self.lblParam3Name.setText(self.labelParameter3.text())
                self.lblParam3Value.setText(str(round(_optimisedParamaterList[2][0], 5)))
                confidenceStr = '[{}     {}]'.format(_optimisedParamaterList[2][1], _optimisedParamaterList[2][2])
                self.lblParam3ConfInt.setText(confidenceStr)
        except Exception as e:
            print('Error in function displayOptimumParamaterValuesOnGUI: ' + str(e))
            logger.error('Error in function displayOptimumParamaterValuesOnGUI: ' + str(e))

    def clearOptimumParamaterValuesOnGUI(self):
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
        except Exception as e:
            print('Error in function clearOptimumParamaterValuesOnGUI: ' + str(e))
            logger.error('Error in function clearOptimumParamaterValuesOnGUI: ' + str(e))
    
    def saveCSVFile(self):
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
        try:
            logger.info('clearOptimisedParamaterList called from ' + callingControl)
            _optimisedParamaterList.clear()
            self.clearOptimumParamaterValuesOnGUI()
        except Exception as e:
            print('Error in function clearOptimisedParamaterList: ' + str(e)) 
            logger.error('Error in function clearOptimisedParamaterList: ' + str(e))

    def displayModelFittingGroupBox(self):
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

    def displayFitModelSaveCSVButtons(self):
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

    def runCurveFit(self):
        try:
            modelName = str(self.cmbModels.currentText())
            initialParametersArray = []
            
            if modelName ==  'One Compartment':
                parameter1 = self.spinBoxParameter1.value()
                initialParametersArray.append(parameter1)
                parameter2 = self.spinBoxParameter2.value()
                initialParametersArray.append(parameter2)
            elif modelName ==  'Extended Tofts':
                parameter1 = self.spinBoxParameter1.value()
                initialParametersArray.append(parameter1)
                parameter2 = self.spinBoxParameter2.value()
                initialParametersArray.append(parameter2)
                parameter3 = self.spinBoxParameter3.value()
                initialParametersArray.append(parameter3)
            elif modelName == 'High-Flow Gadoxetate':
                parameter2 = self.spinBoxParameter1.value()
                initialParametersArray.append(parameter2)
                parameter1 = self.spinBoxParameter2.value()
                initialParametersArray.append(parameter1)
                parameter3 = self.spinBoxParameter3.value()
                initialParametersArray.append(parameter3)
                
            ROI = str(self.cmbROI.currentText())
            AIF = str(self.cmbAIF.currentText())
            arrayTimes = np.array(_concentrationData['Time'], dtype='float')
            arrayROIConcs = np.array(_concentrationData[ROI], dtype='float')
            arrayInputConcs = np.array(_concentrationData[AIF], dtype='float')
            if self.cboxConstaint.isChecked():
                addConstraint = True
            else:
                addConstraint = False

            #Call curve fitting routine
            logger.info('TracerKineticModels.curveFit called with model {}, parameters {} and Constraint = {}'.format(modelName, initialParametersArray, addConstraint))
            optimumParams, paramCovarianceMatrix = TracerKineticModels.curveFit(modelName, arrayTimes, arrayInputConcs, arrayROIConcs, initialParametersArray, addConstraint)
            logger.info('TracerKineticModels.curveFit returned optimum parameters {} with confidence levels {}'.format(optimumParams, paramCovarianceMatrix))
            
            self.spinBoxParameter1.setValue(optimumParams[0])
            self.spinBoxParameter2.setValue(optimumParams[1])
            if optimumParams.size == 3:
                self.spinBoxParameter3.setValue(optimumParams[2])

            numDataPoints = arrayROIConcs.size
            numParams = len(initialParametersArray)
            #logger.info('Function calcParameterConfidenceIntervals called with numDataPoints = {} '
            # ' and numParams= {}'.format(numDataPoints, numParams))
            #self.calcParameterConfidenceIntervals(numDataPoints, numParams, optimumParams, estimatedCovarianceArray)
            
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
            
            logger.info('In calcParameterConfidenceIntervals, _optimisedParamaterList = {}'.format(_optimisedParamaterList))
            self.displayOptimumParamaterValuesOnGUI()
            
        except ValueError as ve:
            print ('Value Error: runCurveFit with model ' + modelName + ': '+ str(ve))
            logger.error('Value Error: runCurveFit with model ' + modelName + ': '+ str(ve))
        except Exception as e:
            print('Error in function runCurveFit with model ' + modelName + ': ' + str(e))
            logger.error('Error in function runCurveFit with model ' + modelName + ': ' + str(e))
    
    def savePDFReport(self):
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
                
                self.figure.savefig(fname=IMAGE_NAME, dpi=150)  #dpi=200 so as to get a clear image in the PDF report
                
                parameter1 = self.spinBoxParameter1.value()
                parameter2 = self.spinBoxParameter2.value()
                parameter3 = self.spinBoxParameter3.value()
                
##                def createAndSavePDFReport(self, fileName, _dataFileName, modelName, imageName, 
#                               parameter1Text, parameter1Value,
#                               parameter2Text, parameter2Value,
#                               parameter3Text = None, parameter3Value = None, covarianceArray =[])
                
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                if modelName ==  'One Compartment':
                    pdf.createAndSavePDFReport(reportFileName, _dataFileName, modelName, IMAGE_NAME, LABEL_PARAMETER_1A, parameter1, LABEL_PARAMETER_2B, parameter2, None, None, _optimisedParamaterList)
                elif modelName ==  'Extended Tofts':
                    pdf.createAndSavePDFReport(reportFileName, _dataFileName, modelName, IMAGE_NAME, LABEL_PARAMETER_1A, parameter1, LABEL_PARAMETER_2A, parameter2, LABEL_PARAMETER_3A, parameter3, _optimisedParamaterList)
                elif modelName == 'High-Flow Gadoxetate':
                    pdf.createAndSavePDFReport(reportFileName, _dataFileName, modelName, IMAGE_NAME, LABEL_PARAMETER_1B, parameter1, LABEL_PARAMETER_2A, parameter2, LABEL_PARAMETER_3B, parameter3, _optimisedParamaterList)
                QApplication.restoreOverrideCursor()

                #Delete image file
                os.remove(IMAGE_NAME)
                logger.info('PDF Report created called ' + reportFileName)
        except Exception as e:
            print('Error in function savePDFReport: ' + str(e))
            logger.error('Error in function savePDFReport: ' + str(e))
       
    def loadDataFile(self):
        global _concentrationData
        global _dataFileName

        #clear the global dictionary of previous data
        _concentrationData.clear()

        #Clear label displaying name of the datafile
        self.lblDataFileName.setText('')
        
        #get the data file in csv format
        #filter parameter set so that the user can only open a csv file
        try:
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

                    #Each key in the dictionary is paired with a list of corresponding concentrations (except for the Time key that is paired with a list of times)
                    for row in readCSV:
                        counter=0
                        for key in _concentrationData:
                            if key != 'model':
                                if counter == 0:
                                    _concentrationData[key].append(int(row[counter]))
                                else:
                                    _concentrationData[key].append(float(row[counter]))
                                counter+=1           
                csvfile.close()

                self.configureGUIAfterLoadingData()
                #plot function called here in case we need to clear a graph showing data from a previous data file
                self.plot('loadDataFile')

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

    def configureGUIAfterLoadingData(self):
        try:
            #Data file loaded OK, so set up the GUI
            #Reset and enable dropdown list of models
            self.cmbROI.clear()
            self.cmbAIF.clear()
            self.cmbVIF.clear()
            
            organArray = []
            organArray = self.returnListOrgans()
            
            self.btnSaveReport.hide()
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
        try:
            logger.info('Function returnListOrgans called')
            organList =[]
            counter=0
            organList.append('Please Select') #First item at the top of the drop-down list
            for key in _concentrationData:
                if counter > 0:  #Ignore the first key because it will be the word 'time'
                    if key != 'model':
                        organList.append(str(key))
                counter+=1        
            return organList
        except RuntimeError as re:
            print('runtime error in function returnListOrgans' + str(re))
            logger.error('runtime error in function returnListOrgans' + str(re))
        except Exception as e:
            print('Error in function returnListOrgans: ' + str(e))
            logger.error('Error in function returnListOrgans: ' + str(e))
    
    def initialiseParameterSpinBoxes(self):
        #Reset model parameter spinboxes with typical initial values for each model
        try:
            self.spinBoxParameter1.blockSignals(True)
            self.spinBoxParameter2.blockSignals(True)
            self.spinBoxParameter3.blockSignals(True)
            
            modelName = str(self.cmbModels.currentText())
            logger.info('Function initialiseParameterSpinBoxes called when model = ' + modelName)
            if modelName ==  'Extended Tofts':
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Vp)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Ktrans)
            elif modelName == 'High-Flow Gadoxetate':
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Ve)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Kce)
                self.spinBoxParameter3.setValue(DEFAULT_VALUE_Kbc)
            elif modelName ==  'One Compartment':
                self.spinBoxParameter1.setValue(DEFAULT_VALUE_Vp)
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Fp)

            self.spinBoxParameter1.blockSignals(False)
            self.spinBoxParameter2.blockSignals(False)
            self.spinBoxParameter3.blockSignals(False)
        except Exception as e:
            print('Error in function initialiseParameterSpinBoxes: ' + str(e) )
            logger.error('Error in function initialiseParameterSpinBoxes: ' + str(e) )

    def setParameterSpinBoxesToConstraintValue(self):
        """Set model parameter spinboxes to the upper bound of the constaint"""
        global oldParameter1 
        global oldParameter2 
        global oldParameter3
        try:
            upperBound = TracerKineticModels.PARAMETER_UPPER_BOUND
     
            if self.cboxConstaint.isChecked():
                logger.info('Function setParameterSpinBoxesToConstraintValue called. Upper Bound = {}'.format(upperBound))
                
                oldParameter1 = self.spinBoxParameter1.value() 
                oldParameter2 = self.spinBoxParameter2.value()
                oldParameter3 = self.spinBoxParameter3.value()

                self.spinBoxParameter1.blockSignals(True)
                self.spinBoxParameter2.blockSignals(True)
                self.spinBoxParameter3.blockSignals(True)

                self.spinBoxParameter1.setValue(upperBound)
                self.spinBoxParameter2.setValue(upperBound)
                self.spinBoxParameter3.setValue(upperBound)

                self.spinBoxParameter1.blockSignals(False)
                self.spinBoxParameter2.blockSignals(False)
                self.spinBoxParameter3.blockSignals(False)
            else:
                logger.info('Function setParameterSpinBoxesToConstraintValue called, parameter spinboxes reset to old values')
                self.spinBoxParameter1.blockSignals(True)
                self.spinBoxParameter2.blockSignals(True)
                self.spinBoxParameter3.blockSignals(True)

                self.spinBoxParameter1.setValue(oldParameter1)
                self.spinBoxParameter2.setValue(oldParameter2)
                self.spinBoxParameter3.setValue(oldParameter3)

                self.spinBoxParameter1.blockSignals(False)
                self.spinBoxParameter2.blockSignals(False)
                self.spinBoxParameter3.blockSignals(False)

        except Exception as e:
            print('Error in function setParameterSpinBoxesToConstraintValue: ' + str(e) )
            logger.error('Error in function setParameterSpinBoxesToConstraintValue: ' + str(e) )

    def configureGUIForEachModel(self):
        try:
            self.cboxDelay.show()
            self.cboxConstaint.show()
            self.cboxConstaint.setChecked(False)
            self.btnReset.show()
            self.initialiseParameterSpinBoxes() #Typical initial values for each model
            self.clearOptimumParamaterValuesOnGUI() #Remove results of curve fitting of the previous model
            modelName = str(self.cmbModels.currentText())
            logger.info('Function configureGUIForEachModel called when model = ' + modelName)
            if modelName ==  'Extended Tofts':
                self.labelParameter1.setText(LABEL_PARAMETER_1A)
                self.labelParameter1.show()
                self.lblAIF.show()
                self.cmbAIF.show()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.spinBoxParameter1.show()
                self.spinBoxParameter2.show()
                self.spinBoxParameter3.show()
                self.labelParameter2.setText(LABEL_PARAMETER_2A)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_3A)
                self.labelParameter3.show()
            elif modelName == 'High-Flow Gadoxetate':
                self.labelParameter1.setText(LABEL_PARAMETER_2A)
                self.labelParameter1.show()
                self.lblAIF.show()
                self.cmbAIF.show()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.spinBoxParameter1.show()
                self.spinBoxParameter2.show()
                self.spinBoxParameter3.show()
                self.labelParameter2.setText(LABEL_PARAMETER_1B)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_3B)
                self.labelParameter3.show()
            elif modelName ==  'One Compartment':
                self.labelParameter1.setText(LABEL_PARAMETER_1A)
                self.labelParameter1.show()
                self.lblAIF.show()
                self.cmbAIF.show()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.spinBoxParameter1.show()
                self.spinBoxParameter2.show()
                self.spinBoxParameter3.hide()
                self.labelParameter2.setText(LABEL_PARAMETER_2B)
                self.labelParameter2.show()
                self.labelParameter3.hide()
                self.labelParameter3.clear()
                self.spinBoxParameter2.setValue(DEFAULT_VALUE_Fp) #Default value
            elif modelName == 'Descriptive':
                self.labelParameter1.setText(LABEL_PARAMETER_1A)
                self.labelParameter1.show()
                self.lblAIF.hide()
                self.cmbAIF.hide()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.spinBoxParameter1.show()
                self.spinBoxParameter2.show()
                self.spinBoxParameter3.show()
                self.labelParameter2.setText(LABEL_PARAMETER_2A)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_3A)
                self.labelParameter3.show()
            elif modelName == 'AIF & VIF':
                self.labelParameter1.setText(LABEL_PARAMETER_1A)
                self.labelParameter1.show()
                self.lblAIF.show()
                self.cmbAIF.show()
                self.lblVIF.show()
                self.cmbVIF.show()
                self.spinBoxParameter1.show()
                self.spinBoxParameter2.show()
                self.spinBoxParameter3.show()
                self.labelParameter2.setText(LABEL_PARAMETER_2A)
                self.labelParameter2.show()
                self.labelParameter3.setText(LABEL_PARAMETER_3A)
                self.labelParameter3.show()
            else:  #No model is selected
                self.lblAIF.hide()
                self.cmbAIF.hide()
                self.lblVIF.hide()
                self.cmbVIF.hide()
                self.cmbAIF.setCurrentIndex(0)
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

                self.btnFitModel.hide()
                self.btnSaveCSV.hide()
        except Exception as e:
            print('Error in function configureGUIForEachModel: ' + str(e) )
            logger.error('Error in function configureGUIForEachModel: ' + str(e) )
            
    def getScreenResolution(self):
        try:
            width, height = pyautogui.size()
            logger.info('Function getScreenResolution called. Screen width = {}, height = {}.'.format(width, height))
            return width, height
        except Exception as e:
            print('Error in function getScreenResolution: ' + str(e) )
            logger.error('Error in function getScreenResolution: ' + str(e) )
        
    def determineTextSize(self):
        """Determines the optimum size for labels on the matplotlib graph from
            the screen resolution"""
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
    
    def plot(self, callingFunction):
        try:
            global _listModel
            #with plt.style.context('ggplot'):
            self.figure.clear()
            
            # create an axis
            ax = self.figure.add_subplot(111)

            #Get the optimum label size for the screen resolution.
            tickLabelSize, xyAxisLabelSize, titleSize = self.determineTextSize()
            
            #Set size of the x,y axis tick labels
            ax.tick_params(axis='both', which='major', labelsize=tickLabelSize)

            #Get model data
            modelName = str(self.cmbModels.currentText())
            
            arrayTimes = np.array(_concentrationData['Time'], dtype='float')
            ROI = str(self.cmbROI.currentText())
            if ROI != 'Please Select':
                arrayROIConcs = np.array(_concentrationData[ROI], dtype='float')
                ax.plot(arrayTimes, arrayROIConcs, 'b.-', label= ROI)
                if modelName == 'Descriptive':
                    _listModel = TracerKineticModels.ROI_OnlyModel()
                    arrayModel =  np.array(_listModel, dtype='float')
                    ax.plot(arrayTimes, arrayModel, 'g--', label= modelName + ' model')

            AIF = str(self.cmbAIF.currentText())
            VIF = str(self.cmbVIF.currentText())

            logger.info('Function plot called from ' + callingFunction + ' when ROI={}, AIF={} and VIF={}'.format(ROI, AIF, VIF))

            if AIF != 'Please Select':
                arrayAIFConcs = np.array(_concentrationData[AIF], dtype='float')
                ax.plot(arrayTimes, arrayAIFConcs, 'r.-', label= AIF)
                if modelName == 'High-Flow Gadoxetate':
                    parameter1 = self.spinBoxParameter2.value()
                    parameter2 = self.spinBoxParameter1.value()
                    parameter3 = self.spinBoxParameter3.value()
                else:
                    parameter1 = self.spinBoxParameter1.value()
                    parameter2 = self.spinBoxParameter2.value()
                    parameter3 = self.spinBoxParameter3.value()

                if VIF == 'Please Select':
                    logger.info('TracerKineticModels.modelSelector called when model ={} and parameters are {}, {}, {}'. format(modelName, parameter1, parameter2, parameter3))
                    _listModel = TracerKineticModels.modelSelector(modelName, arrayTimes, arrayAIFConcs, parameter1, parameter2, parameter3)
                    arrayModel =  np.array(_listModel, dtype='float')
                    ax.plot(arrayTimes, arrayModel, 'g--', label= modelName + ' model')
            
            if VIF != 'Please Select':
                arrayVIFConcs = np.array(_concentrationData[VIF], dtype='float')
                ax.plot(arrayTimes, arrayVIFConcs, 'k.-', label= VIF)
                parameter1 = self.spinBoxParameter1.value()
                parameter2 = self.spinBoxParameter2.value()
                parameter3 = self.spinBoxParameter3.value()
                _listModel = TracerKineticModels.AIF_VIF_Model()
                arrayModel =  np.array(_listModel, dtype='float')
                ax.plot(arrayTimes, arrayModel, 'g--', label= modelName + ' model')
            
            if ROI != 'Please Select':  
                ax.set_xlabel('Time (mins)', fontsize=xyAxisLabelSize)
                ax.set_ylabel('Concentration (mM)', fontsize=xyAxisLabelSize)
                ax.set_title('Tissue Concentrations', fontsize=titleSize, pad=25)
                ax.grid()
                chartBox = ax.get_position()
                ax.set_position([chartBox.x0*1.1, chartBox.y0, chartBox.width*0.9, chartBox.height])
                ax.legend(loc='upper center', bbox_to_anchor=(1.0, 1.0), shadow=True, ncol=1, fontsize='x-large')
                # refresh canvas
                self.canvas.draw()
            else:
                # draw the graph on the canvas
                self.canvas.draw()
            
        except Exception as e:
                print('Error in function plot when an event associated with ' + str(callingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
                logger.error('Error in function plot when an event associated with ' + str(callingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
    
    def exitApp(self):
        logger.info("Application closed using the Exit button.")
        sys.exit(0)  
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ModelFittingApp()
    main.show()
    sys.exit(app.exec_())
