import xml.etree.ElementTree as ET  
import logging

logger = logging.getLogger(__name__)

class XMLReader():
    def __init__(self, fullFilePath): 
        try:
            self.fullFilePath = fullFilePath
            self.tree = ET.parse(fullFilePath)
            self.root = tree.getroot()
           
            logger.info('In module ' + __name__ 
                    + '. parsed ' + fullFilePath)

        except ET.ParseError as et:
            print('XMLReader.__init__ parse error: ' + str(et)) 
            logger.error('XMLReader.__init__parse error: ' + str(et))
        except Exception as e:
            print('XMLReader.__init__: ' + str(e)) 
            logger.error('XMLReader.__init__: ' + str(e)) 




