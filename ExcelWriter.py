from openpyxl import Workbook
import logging

logger = logging.getLogger(__name__)

class ExcelWriter:
    def __init__(self, fullFilePath): 
        try:
            self.fullFilePath = fullFilePath
            #print ("Excel fullFilePath = " + fullFilePath)
            self.wb = Workbook()
            
            logger.info('In module ' + __name__ 
                    + '. Created an instance of class ExcelWriter.')
        except Exception as e:
            print('ExcelWriter.__init__: ' + str(e)) 
            logger.error('ExcelWriter.__init__: ' + str(e)) 

    def isWorksheet(self, title) -> bool:
        boolWSExists = False
        for sheet in self.wb:
            if sheet.title == title:
                boolWSExists = True
                break
        
        return boolWSExists

    def RecordSkippedFiles(self, fileName, failureReason):
        try:
            if not self.isWorksheet("Skipped files"):
                #Skipped files tab does not exist.
                #Create it and add first skipped file info.
                self.ws = self.wb.active
                self.ws.title = "Skipped files"
                self.ws['A1'] = "File"
                self.ws['B1'] = "Failure Reason"
                self.ws['A2'] = fileName
                self.ws['B2'] = failureReason
            else:
                thisWS = self.wb["Skipped files"]
                #get next empty row
                row_count = thisWS.max_row
                nextRow = row_count + 1
                thisWS['A' + str(nextRow)] = fileName
                thisWS['B' + str(nextRow)] = failureReason
                    
            logger.info('In module ' + __name__ 
                    + '.RecordSkippedFiles.')

        except Exception as e:
            print('ExcelWriter.RecordSkippedFiles: ' + str(e)) 
            logger.error('ExcelWriter.RecordSkippedFiles: ' + str(e)) 

    def RecordParameterValues(self, fileName, modelName, paramName, 
                              paramValue, paramLower, paramUpper):
        try:
            paramName = paramName.partition(',')
            paramName = paramName[0] 
            paramName = paramName.replace('\'', '')
            paramName = paramName[0:31] #worksheet title max 31 chars 
                
            if not self.isWorksheet(paramName):
                #This parameter tab does not exist.
                #Create it and add first parameter value data.
                thisWS = self.wb.create_sheet(paramName)
                #thisWS.title = paramName
                thisWS['A1'] = "File"
                thisWS['B1'] = "Model"
                thisWS['C1'] = "Parameter"
                thisWS['D1'] = "Value"
                thisWS['E1'] = "Lower"
                thisWS['F1'] = "Upper"
                
                thisWS['A2'] = fileName
                thisWS['B2'] = modelName
                thisWS['C2'] = paramName
                thisWS['D2'] = str(paramValue)
                thisWS['E2'] = str(paramLower)
                thisWS['F2'] = str(paramUpper)
            else:
                thisWS = self.wb[paramName]
                #get next empty row
                row_count = thisWS.max_row
                nextRow = row_count + 1
                thisWS['A' + str(nextRow)] = fileName
                thisWS['B' + str(nextRow)] = modelName
                thisWS['C' + str(nextRow)] = paramName
                thisWS['D' + str(nextRow)] = str(paramValue)
                thisWS['E' + str(nextRow)] = str(paramLower)
                thisWS['F' + str(nextRow)] = str(paramUpper)
                        
            logger.info('In module ' + __name__ 
                    + '.RecordParameterValues when paramater = ' + paramName)
        except Exception as e:
            print('ExcelWriter.RecordParameterValues when paramater = ' 
                  + paramName + str(e)) 
            logger.error('ExcelWriter.RecordParameterValues when paramater = ' 
                         + paramName + str(e)) 

    def SaveSpreadSheet(self): 
        try:
            self.wb.save(self.fullFilePath)
            logger.info('In module ' + __name__ 
                    + '. SaveSpreadSheet.')
        except Exception as e:
            print('ExcelWriter.SaveSpreadSheet: ' + str(e)) 
            logger.error('ExcelWriter.SaveSpreadSheet: ' + str(e)) 
            





