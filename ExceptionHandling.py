"""
This module provides functionality for 
logging and the handling of exceptions in the model functions
in the module ModelFunctions.py.  
"""
import sys
import inspect
from PyQt5.QtWidgets import QMessageBox
import logging
logger = logging.getLogger(__name__)

def modelFunctionInfoLogger():
    """
    It is intended that this function is called at the start
    of every model function.  It logs the module name.function name
    combination and the input parameters and their values passed
    into this function.
    """
    try: 
        #  the call stack to get the name, host module
        # and input arguments of the function
        # from which a call is made to this function. 
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
    """
    This function handles division by zero exceptions in a
    model function. A pop-up modal dialog box is displayed
    warning the use about this error. Details of this exceptiona 
    are also logged and printed in the Python kernal black screen.
    """
    # Inspect the call stack to get the name, host module
    # and input arguments of the function
    # from which a call is made to this function. 
    funcName = sys._getframe().f_back.f_code.co_name
    modName = sys._getframe().f_back.f_globals['__name__']
    QMessageBox().warning(None, "Division by zero", 
        "Division by zero when input parameters: " + argStr, 
        QMessageBox.Ok)
    print('Zero Division Error when input parameters:' + argStr + ' in '
               + modName + '.' + funcName + '. Error = ' + str(exceptionObj))
    logger.error('Zero Division Error when input parameters:' + argStr + ' in '
               + modName + '.' + funcName + '. Error = ' + str(exceptionObj))


def handleGeneralException(exceptionObj):
    """
    When called immediately after the above handleDivByZeroException
    function, this function handles all other exceptions apart from
    the division by zero exception. Details of the exceptiona are 
    logged and printed in the Python kernal black screen.
    """
    # Inspect the call stack to get the name, host module
    # and input arguments of the function
    # from which a call is made to this function. 
    funcName = sys._getframe().f_back.f_code.co_name
    modName = sys._getframe().f_back.f_globals['__name__']
    print('Error - ' + modName + '.' + funcName + ' ' + str(exceptionObj))
    logger.error('Error -'  + modName + '.' + funcName + ' ' + str(exceptionObj))