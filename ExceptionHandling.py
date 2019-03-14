import sys
import inspect
from PyQt5.QtWidgets import QMessageBox
import logging
logger = logging.getLogger(__name__)

def modelFunctionInfoLogger():
    try: 
        funcName = sys._getframe().f_back.f_code.co_name
        modName = sys._getframe().f_back.f_globals['__name__']
        args, _, _, values = inspect.getargvalues(sys._getframe(1))
        argStr = ""
        for i in args:
            # As xData2DArray is a large 2D array of data
            # exclude it from the list of parameters and 
            # their values.
            if i != "xData2DArray":
                argStr += " %s = %s" % (i, values[i])
        logger.info('Function ' + modName + '.' + funcName +
            ' called with input parameters: ' + argStr)
    except Exception as e:
        print('Error - ' + modName + '.modelFunctionInfoLogger ' + str(e))
        logger.error('Error -'  + modName + '.modelFunctionInfoLogger ' + str(e))

def handleDivByZeroException(exceptionObj):
    funcName = sys._getframe().f_back.f_code.co_name
    modName = sys._getframe().f_back.f_globals['__name__']
    QMessageBox().warning(None, "Division by zero", 
        "Division by zero when input parameters: " + argStr, 
        QMessageBox.Ok)
    logger.error('Zero Division Error when input parameters:' + argStr + ' in '
               + modName + '.' + funcName + '. Error = ' + str(exceptionObj))

def handleGeneralException(exceptionObj):
    funcName = sys._getframe().f_back.f_code.co_name
    modName = sys._getframe().f_back.f_globals['__name__']
    print('Error - ' + modName + '.' + funcName + ' ' + str(exceptionObj))
    logger.error('Error -'  + modName + '.' + funcName + ' ' + str(exceptionObj))