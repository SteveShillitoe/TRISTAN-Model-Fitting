import datetime
from fpdf import FPDF
import os.path
import errno
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog

import logging

#Create logger
logger = logging.getLogger(__name__)

#This is a global variable used to hold the current date and time 
#displayed in the footer of the PDF report.
currentDateTime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

'''
The header and footer methods in FPDF render the page header and footer.
It is automatically called by add_page and close and should not be called directly by the application.
The implementation in FPDF is empty, so we have to subclass it and override the method to define the required functionality.
'''
class PDF(FPDF):

    def __init__(self, title):
        super().__init__() #Inherit functionality from the __init__ method of class FPDF
        self.title = title  #Then add a local property
        logger.info('In module ' + __name__ + '. Created an instance of class PDF.')

    def header(self):
        # Logo
        #self.image('logo_pb.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'BU', 15)
        # Title
        self.cell(w=0, h=0,  txt =self.title,  align = 'C')
        # Line break
        self.ln(5)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number - centred
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')
        # Current Date & Time - Right justified
        self.cell(0, 10, currentDateTime, 0, 0, 'R')

    def createAndSavePDFReport(self, fileName, dataFileName, modelName, imageName, 
                               parameter1Text, parameter1Value,
                               parameter2Text, parameter2Value,
                               parameter3Text = None, parameter3Value = None, 
                               confidenceLimitsArray =[], curveFittingDone=True):
        try:
            logger.info('Function PDFWriter.createAndSavePDFReport called with filename={}, \
            dataFileName={}, modelName={}, imageName={}, parameter1Text={}, parameter1Value={},\
                 parameter2Text={}, parameter2Value={},parameter3Text ={}, parameter3Value ={}, \
                 curveFittingDone = {}' \
             .format(fileName, dataFileName, modelName, imageName,parameter1Text, parameter1Value,
             parameter2Text, parameter2Value,parameter3Text, parameter3Value, curveFittingDone))
            self.add_page() #First Page in Portrait format, A4
            self.set_font('Arial', 'BU', 12)
            self.write(5, modelName + ' model.\n')
            self.set_font('Arial', '', 10)
            self.write(5, 'Data file name = ' + dataFileName + '\n\n')

            #Build table
            if parameter3Text is not None:
                numRowsData = 3
            else:
                numRowsData = 2

            logger.info('In Function PDFWriter.createAndSavePDFReport printing results table with numRowsData ={} from {}'.format(numRowsData, confidenceLimitsArray))
            
            # Effective page width, or just effectivePageWidth
            effectivePageWidth = self.w - 2*self.l_margin
            # Set column width to 1/7 of effective page width to distribute content 
            # evenly across table and page
            col_width = effectivePageWidth/6
            # Text height is the same as current font size
            textHeight = self.font_size
            #Header Row
            self.cell(col_width*3,textHeight, 'Parameter', border=1)
            self.cell(col_width,textHeight, 'Value', border=1)
            self.cell(col_width*2,textHeight, '95% confidence interval', border=1)
            self.ln(textHeight)
            #Body of Table
            #Row 1
            self.cell(col_width*3,textHeight*2, parameter1Text.replace('\n', ''), border=1)
            self.cell(col_width,textHeight*2, str(round(parameter1Value,5)), border=1)
            if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[0][1], confidenceLimitsArray[0][2])
            else:
                confidenceStr = 'N/A'
            self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
            self.ln(textHeight*2)
            #Row 2
            self.cell(col_width*3,textHeight*2, parameter2Text.replace('\n', ''), border=1)
            self.cell(col_width,textHeight*2, str(round(parameter2Value,5)), border=1)
            if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[1][1], confidenceLimitsArray[1][2])
            else:
                confidenceStr = 'N/A'
            self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
            self.ln(textHeight*2)
            if numRowsData == 3:
                #Row 3
                self.cell(col_width*3,textHeight*2, parameter3Text.replace('\n', ''), border=1)
                self.cell(col_width,textHeight*2, str(round(parameter3Value,5)), border=1)
                if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                    confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[2][1], confidenceLimitsArray[2][2])
                else:
                    confidenceStr = 'N/A'
                self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
                self.ln(textHeight*2)

            self.write(10, '\n') #line break

            self.image(imageName, x = None, y = None, w = 170, h = 130, type = '', link = '') #Add image to PDF
            self.output(fileName, 'F')  #Save PDF
        except Exception as e:
            print('PDFWriter.createAndSavePDFReport: ' + str(e)) 
            logger.error('PDFWriter.createAndSavePDFReport: ' + str(e)) 
            self.output(fileName, 'F')  #Save PDF

