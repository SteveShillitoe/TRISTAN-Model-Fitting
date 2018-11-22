"""This module creates and saves a report of a model fitting session in PDF. 
In addition to a table of model parameter data, this report contains an image
of the concentration/time plot at the time the createAndSavePDFReport method
was called.

This is done using the functionality in the FPDF library.

"""
import datetime
from fpdf import FPDF
import logging

#Create logger
logger = logging.getLogger(__name__)

#This is a global variable used to hold the current date and time 
#displayed in the footer of the PDF report.
currentDateTime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


#header and footer methods in FPDF render the page header and footer.
#They are automatically called by add_page and close and should not be called 
#directly by the application.  The implementation in FPDF is empty, 
#so we have to subclass it and override the method to define the required functionality.
class PDF(FPDF):
    def __init__(self, title):
        super().__init__() #Inherit functionality from the __init__ method of class FPDF
        self.title = title  #Then add a local property
        logger.info('In module ' + __name__ + '. Created an instance of class PDF.')

    def header(self):
        """Prints a header at the top of every page of the report.
        It includes the TRISTAN Logo and the title of the report. """
        # Logo
        self.image('TRISTAN LOGO.jpg', 10, 8, 33, 10)
        # Arial bold 15
        self.set_font('Arial', 'BU', 15)
        # Title
        self.cell(w=0, h=0,  txt =self.title,  align = 'C')
        # Line break
        self.ln(10)

    def footer(self):
        """Prints a footer at the bottom of every page of the report.
        It includes the page number and date/time when the report was created. """
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
                               parameter3Text, parameter3Value,
                               parameter4Text, parameter4Value,
                               arterialFlowFractionValue,
                               confidenceLimitsArray =[], curveFittingDone=True):
        """Creates and saves a copy of a curve fitting report.
        It includes the name of the file containing the data to be plotted and the name
        of the model used for curve fitting.  A table of input parameters, their values
        and their confidence limits is displayed above an image of the concentration/time
        plot.
        
        Input Parameters
        ----------------
        fileName - file path and name of the PDF report.
        dataFileName - file path and name of the CSV file containing the 
            time/concentration data that has been analysed.
        modelName - Name of the model used to curve fit the time/concentration data.
        imageName - Name of the PNG file holding an image of the plot of time/concentration
            data on the GUI.
        parameter1Text - Name of the first model input parameter.
        parameter1Value - Value of the first model input parameter.
        parameter2Text - Name of the second model input parameter.
        parameter2Value - Value of the second model input parameter.
        parameter3Text - Name of the third model input parameter.
        parameter3Value - Value of the third model input parameter.
        The third model input parameter is optional.
        confidenceLimitsArray - Optional array of lower and upper confidence limits 
            for each model input parameter.
        curveFittingDone - Optional boolean that indicates if curve fitting has just 
            performed (value=True), so there will be a set of confidence limits. 
            Or if the user has been manually setting the values of the model input
            parameters (value = False).
        """
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
            logger.info('In Function PDFWriter.createAndSavePDFReport printing results table with confidence limits array = {}'.format(confidenceLimitsArray))
            
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
            if arterialFlowFractionValue is not None:
                self.cell(col_width*3,textHeight*2, 'Arterial Flow Fraction', border=1)
                self.cell(col_width,textHeight*2, str(round(arterialFlowFractionValue,2)), border=1)
                if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                    confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[0][1], confidenceLimitsArray[0][2])
                else:
                    confidenceStr = 'N/A'
                self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
                self.ln(textHeight*2)
                nextIndex = 1
            else:
                nextIndex = 0

            #Row 2
            self.cell(col_width*3,textHeight*2, parameter1Text.replace('\n', ''), border=1)
            self.cell(col_width,textHeight*2, str(round(parameter1Value,5)), border=1)
            if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[nextIndex][1], 
                                                     confidenceLimitsArray[nextIndex][2])
            else:
                confidenceStr = 'N/A'
            self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
            self.ln(textHeight*2)
            nextIndex +=1

            #Row 3
            self.cell(col_width*3,textHeight*2, parameter2Text.replace('\n', ''), border=1)
            self.cell(col_width,textHeight*2, str(round(parameter2Value,5)), border=1)
            if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[nextIndex][1], 
                                                     confidenceLimitsArray[nextIndex][2])
            else:
                confidenceStr = 'N/A'
            self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
            self.ln(textHeight*2)
            nextIndex +=1

            if parameter3Text is not None:
                #Row 4
                self.cell(col_width*3,textHeight*2, parameter3Text.replace('\n', ''), border=1)
                self.cell(col_width,textHeight*2, str(round(parameter3Value,5)), border=1)
                if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                    confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[nextIndex][1], 
                                                         confidenceLimitsArray[nextIndex][2])
                else:
                    confidenceStr = 'N/A'
                self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
                self.ln(textHeight*2)
                nextIndex +=1

            if parameter4Text is not None:
                #Row 5
                self.cell(col_width*3,textHeight*2, parameter4Text.replace('\n', ''), border=1)
                self.cell(col_width,textHeight*2, str(round(parameter4Value,5)), border=1)
                if len(confidenceLimitsArray) > 0 and curveFittingDone == True:
                    confidenceStr = '[{}     {}]'.format(confidenceLimitsArray[nextIndex][1], 
                                                         confidenceLimitsArray[nextIndex][2])
                else:
                    confidenceStr = 'N/A'
                self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
                self.ln(textHeight*2)

            self.write(10, '\n') #line break

            #Add an image of the plot to the report
            self.image(imageName, x = None, y = None, w = 170, h = 130, type = '', link = '') 
            #Save report PDF
            self.output(fileName, 'F')  
        except Exception as e:
            print('PDFWriter.createAndSavePDFReport: ' + str(e)) 
            logger.error('PDFWriter.createAndSavePDFReport: ' + str(e)) 
            self.output(fileName, 'F')  #Save PDF

