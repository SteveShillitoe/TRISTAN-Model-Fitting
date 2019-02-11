import xml.etree.ElementTree as ET  
import logging

logger = logging.getLogger(__name__)

class XMLReader():
    def __init__(self, fullFilePath): 
        try:
            self.XMLFileParsedOK = True
            self.fullFilePath = fullFilePath
            self.tree = ET.parse(fullFilePath)
            self.root = self.tree.getroot()

            #Uncomment to test XML file loaded OK
            #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
           
            logger.info('In module ' + __name__ 
                    + '. parsed ' + fullFilePath)

        except ET.ParseError as et:
            print('XMLReader.__init__ parse error: ' + str(et)) 
            logger.error('XMLReader.__init__parse error: ' + str(et))
            self.XMLFileParsedOK = False
            
        except Exception as e:
            print('Error in XMLReader.__init__: ' + str(e)) 
            logger.error('Error in XMLReader.__init__: ' + str(e)) 
            self.XMLFileParsedOK = False

    def XMLFileParsedOK(self) ->bool:
        return self.hasXMLFileParsedOK

    def returnListModelShortNames(self):
        try:
            tempList = []
            shortModelNames = self.root.findall('./model/name/short')
            tempList = [name.text 
                        for name in shortModelNames]
            return tempList

        except ET.ParseError as et:
            print('XMLReader.returnListModelShortNames XPath error: ' + str(et)) 
            logger.error('XMLReader.returnListModelShortNames XPath error: ' + str(et))
        except Exception as e:
            print('Error in XMLReader.returnListModelShortNames: ' + str(e)) 
            logger.error('Error in XMLReader.returnListModelShortNames: ' + str(e)) 


