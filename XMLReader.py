import xml.etree.ElementTree as ET  
import logging

logger = logging.getLogger(__name__)

FIRST_ITEM_MODEL_LIST = 'Select a model'

class XMLReader:
    def __init__(self): 
        try:
            self.XMLFileParsedOK = True
            self.fullFilePath = ""
            self.tree = None
            self.root = None
           
            logger.info('In module ' + __name__ + ' Created XML Reader Object')

        except Exception as e:
            print('Error in XMLReader.__init__: ' + str(e)) 
            logger.error('Error in XMLReader.__init__: ' + str(e)) 
            
    def parseConfigFile(self, fullFilePath): 
        try:
            self.XMLFileParsedOK = True
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
            self.XMLFileParsedOK = False
            
        except Exception as e:
            print('Error in XMLReader.parseConfigFile: ' + str(e)) 
            logger.error('Error in XMLReader.parseConfigFile: ' + str(e)) 
            self.XMLFileParsedOK = False

    def XMLFileParsedOK(self) ->bool:
        return self.hasXMLFileParsedOK

    def getListModelShortNames(self):
        try:
            shortModelNames = self.root.findall('./model/name/short')
            tempList = [name.text 
                        for name in shortModelNames]
            tempList.insert(0, FIRST_ITEM_MODEL_LIST)
            
            return tempList

        except ET.ParseError as et:
            print('XMLReader.getListModelShortNames XPath error: ' + str(et)) 
            logger.error('XMLReader.getListModelShortNames XPath error: ' + str(et))
        except Exception as e:
            print('Error in XMLReader.getListModelShortNames: ' + str(e)) 
            logger.error('Error in XMLReader.getListModelShortNames: ' + str(e)) 

    def getImageName(self, shortModelName):
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


    def getParameterDefault(self, shortModelName, positionNumber)->float:
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
        try:
            logger.info('XMLReader.getDataFileFolder')
           
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
        
