
import Tools as tools
import ExceptionHandling as exceptionHandler
import numpy as np
from scipy.optimize import fsolve
from joblib import Parallel, delayed
import logging
logger = logging.getLogger(__name__)

#  PLEASE READ: The function paramaters in the model function definition
#  are listed in the same order as they are displayed in the GUI 
#  from top (first) to bottom (last).  The maximum number of
#  parameters allowed is 5. 

####################################################################
####  MR Signal Models 
####################################################################
def Model_Function_Template(xData2DArray, param1, param2, param3, param4, param5,
                                 constantsString):
    """This function contains the algorithm for calculating 
       how MR signal varies with time.
        
            Input Parameters
            ----------------
                xData2DArray - time and AIF signal 
                    (and VIR signal if dual inlet model) 1D arrays 
                    stacked into one 2D array.
                param1 - model parameter.
                param2 - model parameter.
                param3 - model parameter.
                param4 - model parameter.
                param5 - model parameter.
                constantsString - String representation of a dictionary 
                of constant name:value pairs used to convert concentrations 
                predicted by this model to MR signal values.

            Returns
            -------
            St_rel - list of calculated MR signals at each of the 
                time points in array 'time'.
            """ 
    try:
        exceptionHandler.modelFunctionInfoLogger #please leave

        times = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        #Uncheck the next line of code if the model is dual inlet
        #and there is a VIF
        #signalVIF = xData2DArray[:,2]

        # Unpack SPGR model constants from 
        # a string representation of a dictionary
        # of constants and their values.
        # If constants are added/removed from the Model Library XML
        # file, this section must be updated accordingly  
        constantsDict = eval(constantsString) 
        TR, baseline, FA, r1, R10a, R10t = \
        float(constantsDict['TR']), \
        int(constantsDict['baseline']),\
        float(constantsDict['FA']), float(constantsDict['r1']), \
        float(constantsDict['R10a']), float(constantsDict['R10t']) 
        
        # Convert AIF MR signals to concentrations
        # n_jobs set to 1 to turn off parallel processing
        # because parallel processing caused a segmentation
        # fault in the compiled version of this application. 
        # This is not a problem in the uncompiled script
        R1a = [Parallel(n_jobs=1)(delayed(fsolve)
           (tools.spgr2d_func, x0=0, 
            args = (r1, FA, TR, R10a, baseline, signalAIF[p])) 
            for p in np.arange(0,len(times)))]

        R1a = np.squeeze(R1a)
        
        ca = (R1a - R10a)/r1
        
        ###########################################
        #
        # Add code here to calculate concentration, ct
        #
        ##############################################
        
        # Convert to signal
        St_rel = tools.spgr2d_func_inv(r1, FA, TR, R10t, ct)
        
        #Return tissue signal relative to the baseline St/St_baseline
        return(St_rel) 
 
    #please leave the next 4 lines of code
    except ZeroDivisionError as zde: 
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)