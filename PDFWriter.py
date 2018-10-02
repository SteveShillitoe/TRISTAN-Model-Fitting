import datetime
from fpdf import FPDF
import os.path
import errno
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog

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
                               parameter3Text = None, parameter3Value = None):
        try:
            self.add_page() #First Page in Portrait format, A4
            self.set_font('Arial', 'BU', 12)
            self.write(5, modelName + ' model.\n')
            self.set_font('Arial', '', 10)
            if parameter3Text is not None:
                parameter3Str =  '\n' + str(parameter3Text) + ' = ' + str(parameter3Value)
            else:
                parameter3Str = ''
                
            self.write(5, 'Data file name = ' + dataFileName + '\n' + parameter1Text + ' = ' + str(parameter1Value) + '\n' + parameter2Text + ' = ' + str(parameter2Value) + parameter3Str + '\n')
            
            self.image(imageName, x = None, y = None, w = 170, h = 130, type = '', link = '') #Add image to PDF
            self.output(fileName, 'F')  #Save PDF
        except Exception as e:
            print('PDFWriter.createAndSavePDFReport: ' + str(e))    

