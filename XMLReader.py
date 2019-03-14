"""
This class module contains functionality for loading and 
parsing an XML configuration file that describes the model
to be used for curve fitting time/concentration data.

It also contains functions for retrieving data from 
parsed XML tree held in memory.

It uses the functionality provided by the xml.etree.ElementTree
package.
"""
import xml.etree.ElementTree as ET  
import logging

logger = logging.getLogger(__name__)

FIRST_ITEM_MODEL_LIST = 'Select a model'

class XMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = ""
            self.tree = None
            self.root = None
           
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in XMLReader.__init__: ' + str(e)) 
            logger.error('Error in XMLReader.__init__: ' + str(e)) 
            
    def parseConfigFile(self, fullFilePath): 
        """Loads and parses the XML configuration file at fullFilePath.
       After successful parsing, the XML tree is stored in memory."""
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = fullFilePath
            self.tree = ET.parse(fullFilePath)
            self.root = self.tree.getroot()

            #Uncomment to test XML file loaded OK
            #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
           
            logger.info('In module ' + __name__ 
                    + '.parseConfigFile ' + fullFilePath)

        except ET.ParseError as et:
            print('XMLReader.parseConfigFile error: ' + str(et)) 
            logger.error('XMLReader.parseConfigFile error: ' + str(et))
            self.hasXMLFileParsedOK = False
            
        except Exception as e:
            print('Error in XMLReader.parseConfigFile: ' + str(e)) 
            logger.error('Error in XMLReader.parseConfigFile: ' + str(e)) 
            self.hasXMLFileParsedOK = False

    def hasXMLFileParsedOK(self) ->bool:
        return self.hasXMLFileParsedOK

    def getListModelShortNames(self):
        """Returns a list of model short names for display
        in a combo dropdown list on the application GUI """
        try:
            shortModelNames = self.root.findall('./model/name/short')
            tempList = [name.text 
                        for name in shortModelNames]
            #Insert string 'Select a model' as the start of the list
            tempList.insert(0, FIRST_ITEM_MODEL_LIST)
            
            return tempList

        except ET.ParseError as et:
            print('XMLReader.getListModelShortNames XPath error: ' + str(et)) 
            logger.error('XMLReader.getListModelShortNames XPath error: ' + str(et))
        except Exception as e:
            print('Error in XMLReader.getListModelShortNames: ' + str(e)) 
            logger.error('Error in XMLReader.getListModelShortNames: ' + str(e)) 
    
    def getFunctionName(self, shortModelName):
        """Returns the name of the function that corresponds to the model
       with a short name in the string variable shortModelName"""
        try:
            logger.info('XMLReader.getFunctionName called with short model name= ' + shortModelName)
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + ']/function'
                functionName = self.root.find(xPath)
                if functionName.text:
                    logger.info('XMLReader.getFunctionName found function name ' + functionName.text)
                    return functionName.text
                else:
                    return None
            else:
                return None
           
        except Exception as e:
            print('Error in XMLReader.getFunctionName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            logger.error('Error in XMLReader.getFunctionName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            return None

    def getImageName(self, shortModelName):
        """Returns the name of the image that represents the model
       with a short name in the string variable shortModelName"""
        try:
            logger.info('XMLReader.getImageName called with short model name= ' + shortModelName)
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + ']/image'
                imageName = self.root.find(xPath)
                if imageName.text:
                    logger.info('XMLReader.getImageName found image ' + imageName.text)
                    return imageName.text
                else:
                    return None
            else:
                return None
           
        except Exception as e:
            print('Error in XMLReader.getImageName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            logger.error('Error in XMLReader.getImageName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            return None

    def getLongModelName(self, shortModelName):
        """Returns the long name of the model
       with a short name in the string variable shortModelName"""
        try:
            logger.info('XMLReader.getLongModelName called with short model name= ' + shortModelName)
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/name/long'
                modelName = self.root.find(xPath)
                if modelName.text:
                    logger.info('XMLReader.getLongModelName found long model name ' + \
                        modelName.text)
                    return modelName.text
                else:
                    return None
            else:
                return None
           
        except Exception as e:
            print('Error in XMLReader.getLongModelName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            logger.error('Error in XMLReader.getLongModelName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            return None


    def getModelInletType(self, shortModelName):
        """Returns the inlet type (single or dual) of the model
       with a short name in the string variable shortModelName"""
        try:
            logger.info('XMLReader.getModelInletType called with short model name= ' + shortModelName)
            if len(shortModelName) > 0 and shortModelName != FIRST_ITEM_MODEL_LIST:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + ']/inlet_type'
                modelInletType= self.root.find(xPath)
                if modelInletType.text:
                    logger.info('XMLReader.getModelInletType found model inlet type ' + modelInletType.text)
                    return modelInletType.text
                else:
                    return None
            else:
                return None
           
        except Exception as e:
            print('Error in XMLReader.getModelInletType when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            logger.error('Error in XMLReader.getModelInletType when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            return None


    def getNumberOfParameters(self, shortModelName) ->int:
        """Returns the number of input parameters to the model whose
       short name is stored in the string variable shortModelName."""
        try:
            logger.info('XMLReader.getNumberOfParameters called with short model name= ' + shortModelName)
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter'
                parameters = self.root.findall(xPath)
                if parameters:
                    numParams = len(self.root.findall(xPath))
                    return numParams
                else:
                    return 0
            else:
                return 0

        except Exception as e:
            print('Error in XMLReader.getNumberOfParameters when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getNumberOfParameters when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return 0


    def getParameterLabel(self, shortModelName, positionNumber):
        """Returns the full name and units of the parameter to be
        displayed in the parameter label on the application GUI.

        Input Parameters
        ----------------
        shortModelName - Identifies the model.
        positionNumber - The ordinal position of the parameter in the 
                        model's parameter collection. Numbers from one."""
        try:
            logger.info('XMLReader.getParameterLabel called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            boolIsPercentage = False
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/name/short'
                shortName = self.root.find(xPath)

                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/name/long'
                longName = self.root.find(xPath)

                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/units'
                units = self.root.find(xPath)
                if units.text == '%':
                    boolIsPercentage = True

                fullName = longName.text + ', \n' + \
                            shortName.text + \
                            '(' + units.text + ')'

                return boolIsPercentage, fullName
             
        except Exception as e:
            print('Error in XMLReader.getParameterLabel when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterLabel when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return None, ''

    def getParameterShortName(self, shortModelName, positionNumber):
        """Returns the short name of a parameter.

        Input Parameters
        ----------------
        shortModelName - Identifies the model.
        positionNumber - The ordinal position of the parameter in the 
                        model's parameter collection. Numbers from one."""
        try:
            logger.info('XMLReader.getParameterShortName called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/name/short'
                shortName = self.root.find(xPath)

            if shortName.text:
                return shortName.text
            else:
                return ''
             
        except Exception as e:
            print('Error in XMLReader.getParameterShortName when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterShortName when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return ''

    def getParameterDefault(self, shortModelName, positionNumber)->float:
        """
        Returns the default value for parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName.
        """
        try:
            logger.info('XMLReader.getParameterDefault called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/default'
                default = self.root.find(xPath)
                #print('Default ={} when position={}'.format(default.text, positionNumber))
                if default.text:
                    return float(default.text)
                else:
                    return 0.0

        except Exception as e:
            print('Error in XMLReader.getParameterDefault when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterDefault when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return 0.0


    def getParameterStep(self, shortModelName, positionNumber)->float:
        """
        Returns the spinbox step value for parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName. Parameter values are displayed in a
        spinbox on the application GUI. When the spinbox arrows are clicked,
        the parameter value is changed by the value of step.
        """
        try:
            logger.info('XMLReader.getParameterStep called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/step'
                step = self.root.find(xPath)

                if step.text:
                    return float(step.text)
                else:
                    return 0.0

        except Exception as e:
            print('Error in XMLReader.getParameterStep when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterStep when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return 0.0

    def getParameterPrecision(self, shortModelName, positionNumber)->int:
        """
        Returns the number of decimal places to be displayed in the spinbox 
        for parameter in ordinal position, positionNumber, of the parameter 
        collection of the model whose short name is shortModelName. 
        Parameter values are displayed in a spinbox on the application GUI.
        """
        try:
            logger.info('XMLReader.getParameterPrecision called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/precision'
                precision = self.root.find(xPath)

                if precision.text:
                    return int(precision.text)
                else:
                    return 0.0

        except Exception as e:
            print('Error in XMLReader.getParameterPrecision when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterPrecision when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return 0.0

    def getParameterConstraints(self, shortModelName, positionNumber)->float:
        """
        Returns the upper and lower limits of the range of values 
        in the spinbox for the parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName. Parameter values are displayed in a
        spinbox on the application GUI.
        """
        try:
            logger.info('XMLReader.getParameterConstraints called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/constraints/lower'
                lower = self.root.find(xPath)

                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/constraints/upper'
                upper = self.root.find(xPath)

                if lower.text and upper.text:
                    return float(lower.text), float(upper.text)
                else:
                    return 0.0, 0.0

        except Exception as e:
            print('Error in XMLReader.getParameterConstraints when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterConstraints when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return 0.0, 0.0
    
    def getDataFileFolder(self)->str:
        """ Returns the path to the folder where the data files are stored"""
        try:
            logger.info('XMLReader.getDataFileFolder called')
           
            xPath='./data_file_path'
            dataFileFolder = self.root.find(xPath)

            if dataFileFolder.text:
                return dataFileFolder.text
            else:
                return ''

        except Exception as e:
            print('Error in XMLReader.getDataFileFolder:' 
                  + str(e)) 
            logger.error('Error in XMLReader.getDataFileFolder:' 
                  + str(e)) 
            return ''
        
