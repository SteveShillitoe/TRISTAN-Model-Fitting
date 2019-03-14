"""This module contains functions for the creation and saving 
of a report of a model fitting session in a PDF file. 
In addition to a table of model parameter data, this report contains an image
of the concentration/time plot at the time the CreateAndSavePDFReport method
was called.

This is done using the functionality in the FPDF library.
"""
import datetime
from fpdf import FPDF
import logging

#Constant - Images
TRISTAN_LOGO = 'images\\TRISTAN LOGO.jpg'

#Create logger
logger = logging.getLogger(__name__)

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
        self.image(TRISTAN_LOGO, 10, 8, 33, 10)
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
        currentDateTime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.cell(0, 10, currentDateTime, 0, 0, 'R')

    def CreateAndSavePDFReport(self, fileName, dataFileName, modelName, imageName, 
                               parameterDictionary):
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
        parameterDictionary - A dictionary of parameter names (keys) linked to a 3 element list
            containing the parameter value, its lower 95% confidence limit and upper 95%
            confidence limit.

        Action
        ------
        Creates and saves a PDF report at fileName.  This report lists the name of the data file
        containing the data being analyses, displays the values of the model input parameters in 
        a table. If curve fitting has been done, this table also displays the 95% confidence limits
        of the predicted parameter values.  The report also displays the time/concentration plots.
        """
        try:
            logger.info('Function PDFWriter.CreateAndSavePDFReport called with filename={}, \
            dataFileName={}, modelName={} & imageName={}.' \
             .format(fileName, dataFileName, modelName, imageName))
            
            self.add_page() #First Page in Portrait format, A4
            self.set_font('Arial', 'BU', 12)
            self.write(5, modelName + ' model.\n')
            self.set_font('Arial', '', 10)
            self.write(5, 'Data file name = ' + dataFileName + '\n\n')

            # Effective page width, or just effectivePageWidth
            effectivePageWidth = self.w - 2*self.l_margin
            # Set column width to 1/7 of effective page width to distribute content 
            # evenly across table and page
            col_width = effectivePageWidth/6
            # Text height is the same as current font size
            textHeight = self.font_size
            #Parameter Table - Header Row
            self.cell(col_width*3,textHeight, 'Parameter', border=1)
            self.cell(col_width,textHeight, 'Value', border=1)
            self.cell(col_width*2,textHeight, '95% confidence interval', border=1)
            self.ln(textHeight)

            #Parameter Table - Rows of parameter data
            for paramName, paramList in parameterDictionary.items():
                #print('paramName = {}, value={}, lower={}, upper={}'.format(paramName, 
                #        paramList[0], paramList[1], paramList[2]))
                #Create a row in the table
                self.cell(col_width*3,textHeight*2, paramName.replace('\n', ''), border=1)
                self.cell(col_width,textHeight*2, str(paramList[0]), border=1)
                
                if paramList[1] == '' and paramList[2] == '':
                    confidenceStr = '(fixed)'
                else:
                    confidenceStr = '[{}     {}]'.format(paramList[1], paramList[2])
                
                self.cell(col_width*2,textHeight*2, confidenceStr, border=1)
                self.ln(textHeight*2)    

            self.write(10, '\n') #line break

            #Add an image of the plot to the report
            self.image(imageName, x = None, y = None, w = 170, h = 130, type = '', link = '') 
            #Save report PDF
            self.output(fileName, 'F')  
        except Exception as e:
            print('PDFWriter.CreateAndSavePDFReport: ' + str(e)) 
            logger.error('PDFWriter.CreateAndSavePDFReport: ' + str(e)) 
            self.output(fileName, 'F')  #Save PDF

