"""This module contains functions that calculate the variation 
of MR signal with time according to a tracer kinetic model.
"""
import Tools as tools
import ExceptionHandling as exceptionHandler
import numpy as np
from scipy.optimize import fsolve
from joblib import Parallel, delayed
import logging
logger = logging.getLogger(__name__)

# Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order 
# as they are displayed in the GUI from top (first) to bottom (last) 

####################################################################
####  MR Signal Models 
####################################################################
def Model_Function_Template(xData2DArray, param1, param2, param3,
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

        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        #Uncheck the next line of code if the model is dual inlet
        #signalVIF = xData2DArray[:,2]

        # Unpack SPGR model constants from 
        # a string representation of a dictionary
        # of constants and their values
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
            for p in np.arange(0,len(t)))]

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
 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

def Model_Function_Template1(xData2DArray, param1, param2, param3,
                                 constantsString):
    """This function contains the algorithm for calculating 
       how MR signal varies with time.
        
            Input Parameters
            ----------------
                xData2DArray - time and AIF signals 
                    (and VIR signals if appropriate) 1D arrays 
                    stacked into one 2D array.
                Ve - Plasma Volume Fraction (decimal fraction).
                Khe - Hepatocyte Uptake Rate (mL/min/mL)
                Kbh - Biliary Efflux Rate (mL/min/mL) 
                constantsString - String representation of a dictionary 
                of constant name:value pairs used to convert concentrations 
                predicted by this model to MR signal values.

            Returns
            -------
            St_rel - list of calculated MR signals at each of the 
                time points in array 'time'.
            """ 
    try:
        exceptionHandler.modelFunctionInfoLogger()
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        signalVIF = xData2DArray[:,2]

        # Unpack SPGR model constants from 
        # a string representation of a dictionary
        # of constants and their values
        constantsDict = eval(constantsString) 
        TR, baseline, FA, r1, R10a, R10t = \
        float(constantsDict['TR']), \
        int(constantsDict['baseline']),\
        float(constantsDict['FA']), float(constantsDict['r1']), \
        float(constantsDict['R10a']), float(constantsDict['R10t']) 
               
        # Precontrast signal
        Sa_baseline = 1
        
        # Convert to concentrations
        # n_jobs set to 1 to turn off parallel processing
        # because parallel processing caused a segmentation
        # fault in the compiled version of this application. 
        # This is not a problem in the uncompiled script
        R1a = [Parallel(n_jobs=1)(delayed(fsolve)
           (tools.spgr2d_func, x0=0, 
            args = (r1, FA, TR, R10a, Sa_baseline, signalAIF[p])) 
            for p in np.arange(0,len(t)))]

        R1a = np.squeeze(R1a)
        
        ca = (R1a - R10a)/r1
        
        # Correct for spleen Ve
        ve_spleen = 0.43
        ce = ca/ve_spleen
        
        # if Kbh == 0
        if Kbh != 0:
            Th = (1-Ve)/Kbh
            ct = Ve*ce + Khe*Th*tools.expconv(Th,t,ce, 'HighFlowSingleInletGadoxetate2DSPGR_Rat')
        else:
            ct = Ve*ce + Khe*tools.integrate(ce,t)
        
        # Convert to signal
        St_rel = tools.spgr2d_func_inv(r1, FA, TR, R10t, ct)
        
        #Return tissue signal relative to the baseline St/St_baseline
        return(St_rel) 
 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)
