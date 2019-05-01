"""
This class module contains functionality for loading and 
parsing an XML configuration file that describes the model(s)
to be used for curve fitting time/concentration data.

It also contains functions for retrieving data from 
parsed XML tree held in memory.

It uses the functionality provided by the xml.etree.ElementTree
package.
"""
import xml.etree.ElementTree as ET  
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

FIRST_ITEM_MODEL_LIST = 'Select a model'

# User-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class ValueNotDefinedInConfigFile(Error):
   """Raised when no model constants are defined in 
   the XML configuration file."""
   pass

class CannotFormFullParameterName(Error):
   """Raised if the short and long names of a parameter 
   are not defined in the XML configuration file."""
   pass


class XMLReader:
    def __init__(self): 
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = ""
            self.tree = None # Points to XML tree in memory
            self.root = None # Points to the root node of the above XML tree
           
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in XMLReader.__init__: ' + str(e)) 
            logger.error('Error in XMLReader.__init__: ' + str(e)) 
            
    def parseConfigFile(self, fullFilePath): 
        """Loads and parses the XML configuration file at fullFilePath.
       After successful parsing, the XML tree and its root node
      is stored in memory."""
        try:
            self.hasXMLFileParsedOK = True
            self.fullFilePath = fullFilePath
            self.tree = ET.parse(fullFilePath)
            self.root = self.tree.getroot()

            # Uncomment to test XML file loaded OK
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


    def getListModelShortNames(self):
        """Returns a list of model short names for display
        in a combo dropdown list on the application GUI """
        try:
            shortModelNames = self.root.findall('./model/name/short')
            if shortModelNames is None:
                tempList.append('No models defined in config file.')
                raise ValueNotDefinedInConfigFile
            else:
                tempList = [name.text 
                        for name in shortModelNames]

            # Insert string 'Select a model' as the start of the list
            tempList.insert(0, FIRST_ITEM_MODEL_LIST)
            return tempList

        except ValueNotDefinedInConfigFile:
            warningString = 'Error - No models defined in the configuration file.'
            print(warningString)
            logger.error('XMLReader.getListModelShortNames - ' + warningString)
            return tempList
        except ET.ParseError as et:
            print('XMLReader.getListModelShortNames XPath error: ' + str(et)) 
            logger.error('XMLReader.getListModelShortNames XPath error: ' + str(et))
        except Exception as e:
            print('Error in XMLReader.getListModelShortNames: ' + str(e)) 
            logger.error('Error in XMLReader.getListModelShortNames: ' + str(e)) 
    

    def getFunctionName(self, shortModelName):
        """Returns the name of the function that 
        contains the logic corresponding to the model
       with a short name in the string variable shortModelName"""
        try:
            logger.info('XMLReader.getFunctionName called with short model name= ' + shortModelName)
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + ']/function'
                functionName = self.root.find(xPath)
                if functionName is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    logger.info('XMLReader.getFunctionName found function name ' + functionName.text)
                    return functionName.text
            else:
                return None

        except ValueNotDefinedInConfigFile:
            warningString = 'Error - No function defined for model {}'.format(shortModelName)
            print(warningString)
            logger.info('XMLReader.getFunctionName - ' + warningString)
            return None
        except Exception as e:
            print('Error in XMLReader.getFunctionName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            logger.error('Error in XMLReader.getFunctionName when shortModelName ={}: '.format(shortModelName) 
                  + str(e)) 
            return None


    def getYAxisLabel(self):
        """Returns the text of the Y Axis Label use
       with the model with a short name 
        in the string variable shortModelName when
        its output is plotted against time."""
        try:
            logger.info('XMLReader.getYAxisLabel called')
            
            xPath='./plot/y_axis_label'
            yAxisLabel = self.root.find(xPath)
            if yAxisLabel is None:
                raise ValueNotDefinedInConfigFile
            else:
                logger.info('XMLReader.getYAxisLabel found Y Axis Label' 
                            + yAxisLabel.text)
                return yAxisLabel.text
            
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - XMLReader.getYAxisLabel - No Y axis label defined'
            print(warningString)
            logger.info(warningString)
            return 'No Y Axis Label defined in the configuration file.'
        except Exception as e:
            print('Error in XMLReader.getYAxisLabel: ' + str(e)) 
            logger.error('Error in XMLReader.getYAxisLabel: ' + str(e)) 
            return ''


    def getImageName(self, shortModelName):
        """Returns the name of the image that represents the model
       with a short name in the string variable shortModelName"""
        try:
            logger.info('XMLReader.getImageName called with short model name= ' + shortModelName)
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + ']/image'
                imageName = self.root.find(xPath)
                if imageName is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    logger.info('XMLReader.getImageName found image ' + imageName.text)
                    return imageName.text
            else:
                return None

        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - The name of an image describing model {}' \
                .format(shorModelName) +' is not defined in the configuration file.'
            print(warningString)
            logger.info('XMLReader.getImageName - ' + waringString)
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
                if modelName is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    logger.info('XMLReader.getLongModelName found long model name ' + \
                        modelName.text)
                    return modelName.text
            else:
                return None
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - No long name defined for this model in the configuration file'
            print(warningString)
            logger.info('XMLReader.getLongModel - '   + NamewarningString)
            return 'No long name defined for this model'
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
                if modelInletType is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    logger.info('XMLReader.getModelInletType found model inlet type ' + modelInletType.text)
                    return modelInletType.text
            else:
                return None

        except ValueNotDefinedInConfigFile:  
            warningString = 'Error - No model inlet type defined in the config file'
            print(warningString)
            logger.info('XMLReader.getModelInletType - ' + warningString)
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
            isPercentage = False
            missingShortName = False
            missingLongName = False

            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/name/short'
                shortName = self.root.find(xPath)
                if shortName is None:
                    missingShortName = True
                    print('short name for parameter at position {} is missing.'.format(str(positionNumber)))

                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/name/long'
                longName = self.root.find(xPath)
                if longName is None:
                    missingLongName = True
                    print('Long name for parameter at position {} is missing.'.format(str(positionNumber)))

                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/units'
                units = self.root.find(xPath)
                if units is None:
                    print('Units for parameter at position {} are missing.'.format(str(positionNumber)))
                else:
                    if units.text == '%':
                        isPercentage = True
                
                if missingShortName and missingLongName:
                    raise CannotFormFullParameterName
                else:
                    fullName = longName.text + ', \n' + \
                            shortName.text + \
                            '(' + units.text + ')'

                return isPercentage, fullName
        except CannotFormFullParameterName:
            warningString = 'Warning - Cannot form the full name for parameter at position {}'.format(str(positionNumber))
            print (warningString)
            logger.info('XMLReader.getParameterLabel - ' + warningString)
            return False, 'Cannot form full parameter name'
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
            else:
                return ''

            if shortName is None:
                raise ValueNotDefinedInConfigFile
            else:
                return shortName.text

        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - No short name defined for the parameter '  + \
                    'at position {} when the model short = {}'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getParameterShortName - ' + warningString)
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
                if default is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return float(default.text)
            else:
                return 0.0

        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - No default value defined for the parameter '  + \
                    'at position {} when the model short = {}'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getParameterDefault - ' + warningString)
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

                if step is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return float(step.text)
            else:
                return 0.0

        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - No increment/decrement step value defined for the parameter '  + \
                    'at position {} when the model short = {}'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getParameterStep - ' + warningString)
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

                if precision is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return int(precision.text)
            else:
                return 0

        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - Number of decimal places is not defined for the parameter '  + \
                    'at position {} when the model short = {}'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getParameterPrecision - ' + warningString)
            return 0
        except Exception as e:
            print('Error in XMLReader.getParameterPrecision when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getParameterPrecision when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return 0.0


    def getMaxParameterDisplayValue(self, shortModelName, positionNumber)->float:
        """
        Returns the maximum value allowed 
        in the spinbox for the parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName. Parameter values are displayed in a
        spinbox on the application GUI.
        """
        try:
            logger.info('XMLReader.getMaxParameterDisplayValue called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/display_value/max'
                max = self.root.find(xPath)

                if max is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return float(max.text)
                
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - Maximum value allowed in the spinbox for the parameter '  + \
                    'at position {} when the model short = {} is not defined'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getMaxParameterDisplayValue - ' + warningString)
            return None
        except Exception as e:
            print('Error in XMLReader.getMaxParameterDisplayValue when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getMaxParameterDisplayValue when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return None


    def getMinParameterDisplayValue(self, shortModelName, positionNumber)->float:
        """
        Returns the maximum value allowed 
        in the spinbox for the parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName. Parameter values are displayed in a
        spinbox on the application GUI.
        """
        try:
            logger.info('XMLReader.getMinParameterDisplayValue called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/display_value/min'
                min = self.root.find(xPath)

                if min is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return float(min.text)
                
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - Minimum value allowed in the spinbox for the parameter '  + \
                    'at position {} when the model short = {} is not defined'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getMinParameterDisplayValue - ' + warningString)
            return None
        except Exception as e:
            print('Error in XMLReader.getMinParameterDisplayValue when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getMinParameterDisplayValue when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return None
    

    def getUpperParameterConstraint(self, shortModelName, positionNumber)->float:
        """
        Returns the upper constraint value for curve fitting
        for the parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName. Parameter values are displayed in a
        spinbox on the application GUI.
        """
        try:
            logger.info('XMLReader.getUpperParameterConstraint called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/constraints/upper'
                upper = self.root.find(xPath)

                if upper is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return float(upper.text)
                
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - Upper constraint for curve fitting for the parameter '  + \
                    'at position {} when the model short = {} is not defined'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getUpperParameterConstraint - ' + warningString)
            return None
        except Exception as e:
            print('Error in XMLReader.getUpperParameterConstraint when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getUpperParameterConstraint when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return None


    def getLowerParameterConstraint(self, shortModelName, positionNumber)->float:
        """
        Returns the lower constraint value for curve fitting
        for the parameter in ordinal position,
        positionNumber, of the parameter collection of the model whose
        short name is shortModelName. Parameter values are displayed in a
        spinbox on the application GUI.
        """
        try:
            logger.info('XMLReader.getLowerParameterConstraint called with short model name= {} and position={} '.format(shortModelName,positionNumber) )
            
            if len(shortModelName) > 0:
                xPath='./model[@id=' + chr(34) + shortModelName + chr(34) + \
                    ']/parameters/parameter[' + str(positionNumber) + ']/constraints/lower'
                lower = self.root.find(xPath)

                if lower is None:
                    raise ValueNotDefinedInConfigFile
                else:
                    return float(lower.text)
                
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - Lower constraint for curve fitting for the parameter '  + \
                    'at position {} when the model short = {} is not defined'.format(positionNumber, shortModelName)
            print(warningString)
            logger.info('XMLReader.getLowerParameterConstraint - ' + warningString)
            return None
        except Exception as e:
            print('Error in XMLReader.getLowerParameterConstraint when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            logger.error('Error in XMLReader.getLowerParameterConstraint when shortModelName ={} and xPath={}: '.format(shortModelName, xPath) 
                  + str(e)) 
            return None


    def getDataFileFolder(self)->str:
        """ Returns the path to the folder where the data files are stored"""
        try:
            logger.info('XMLReader.getDataFileFolder called')
           
            xPath='./data_file_path'
            dataFileFolder = self.root.find(xPath)

            if dataFileFolder:
                return dataFileFolder.text
            else:
                raise ValueNotDefinedInConfigFile

        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - Path to folder containing data files is not defined'
            print(warningString)
            logger.info('XMLReader.getDataFileFolder - ' + warningString)
            return ''
        except Exception as e:
            print('Error in XMLReader.getDataFileFolder:' 
                  + str(e)) 
            logger.error('Error in XMLReader.getDataFileFolder:' 
                  + str(e)) 
            return ''
        

    def getStringOfConstants(self):
        """ Returns a string representation of a dictionary of
            model constant name:value pairs."""
        try:
            logger.info('XMLReader.getStringOfConstants called')
           
            xPath='./constants/constant'
            collectionConstants = self.root.findall(xPath)

            if collectionConstants is None:
                raise ValueNotDefinedInConfigFile
            else:
                constantsDict = {}
                for constant in collectionConstants:
                    name = constant.find('name').text
                    value = constant.find('value').text
                    constantsDict[name] = value

            #Return a string representation of the
            #dictionary
            return str(constantsDict)
        
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - XMLReader.getStringOfConstants - No model constants defined.'
            print(warningString)
            logger.info(warningString)
            return ''
        except Exception as e:
            print('Error in XMLReader.getStringOfConstants:' 
                  + str(e)) 
            logger.error('Error in XMLReader.getStringOfConstants:' 
                  + str(e)) 
            return ''

    def getNumBaselineScans(self):
        """ Gets the number of the baseline scans."""
        try:
            logger.info('XMLReader.getNumBaselineScans called')
           
            xPath="./constants/constant[name ='baseline']/value"
            baselineValue = self.root.find(xPath)

            if baselineValue is None:
                raise ValueNotDefinedInConfigFile
            else:
                return int(baselineValue.text)
        
        except ValueNotDefinedInConfigFile:
            warningString = 'Warning - XMLReader.getNumBaselineScans - No baseline value defined.'
            print(warningString)
            logger.info(warningString)
            return ''
        except Exception as e:
            print('Error in XMLReader.getNumBaselineScans: ' 
                  + str(e)) 
            logger.error('Error in XMLReader.getNumBaselineScans: ' 
                  + str(e)) 
            return ''