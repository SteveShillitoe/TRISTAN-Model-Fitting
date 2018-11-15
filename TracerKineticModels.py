"""This module contains functions that calculate the variation of concentration
with time according to several tracer kinetic models.  

The list modelNames holds the names of these models for display in a dropdown list.

The function modelSelector coordinates the execution of the appropriate function 
according to the model selected on the GUI.

For each model there are two functions.  A single input version (AIF only) and
a dual input version (AIF & VIF).

The function, curveFit calls the curve_fit function imported from scipy.optimize 
to fit any of the models in this module to actual concentration/time data 
using non-linear least squares.  
"""

import Tools as tools
from scipy.optimize import curve_fit
import numpy as np
import logging

#Create logger
logger = logging.getLogger(__name__)


#List of names of models for display in a dropdown list.
modelNames = ['Select a model','Extended Tofts','One Compartment','High-Flow Gadoxetate']

#Constants
PARAMETER_UPPER_BOUND_VOL_FRACTION = 1.0
PARAMETER_UPPER_BOUND_RATE = np.inf

def modelSelector(modelName, times, AIFConcentration, parameterArray, boolDualInput, 
                  VIFConcentration=[]):
    """Function called in the GUI of the model fitting tool to select the 
    function corresponding to each model.

    Input Parameters
    ----------------
        modelName - Name of the model taken from the selected value in the  
            model name drop-down list on the GUI.  Used to select the 
            function corresponding to that model.

        time - NumPy Array of time values stored as floats. Created from a 
            Python list.

        AIFConcentration - NumPy Array of concentration values stored as floats. 
            Created from a Python list.  These concentrations are the Arterial
            Input Function input to the model.

        parameterArray - list of model input parameter values.

        boolDualInput - boolean indicating if the input to the model is 
            single(=False) AIF only or dual(=True) AIF & VIR.

        VIFConcentration - Optional NumPy Array of concentration values stored as floats. 
            Created from a Python list.  These concentrations are the Venal
            Input Function input to the model.

        Returns
        ------
        Returns the return value from the selected model function that is a list of
        concentrations calculated at the times in the array time.
        """
    logger.info("In TracerKineticModels.modelSelector. Called with model {} and parameters {}".format(modelName, parameterArray))
    
    parameter1 = parameterArray[0]
    parameter2 = parameterArray[1]
    
    #time and concentration arrays must be stacked into one input variable
    #to meet the requirements of the SciPy library curve fitting function.
    if boolDualInput == True:
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration, VIFConcentration))
    else:
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration))

    if modelName ==  'Extended Tofts':
        parameter3 = parameterArray[2]
        if boolDualInput == True:
            arterialFlowFraction = parameterArray[3]
            return extendedTofts_DualInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3, arterialFlowFraction)
        else:
            return extendedTofts_SingleInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3)
    elif modelName ==  'One Compartment':
        if boolDualInput == True:
            arterialFlowFraction = parameterArray[2]
            return oneCompartment_DualInput(timeInputConcs2DArray, parameter1, parameter2, 
              arterialFlowFraction)
        else:
            return oneCompartment_SingleInput(timeInputConcs2DArray, parameter1, parameter2)
    elif modelName ==  'High-Flow Gadoxetate':
        parameter3 = parameterArray[2]
        if boolDualInput == True:
            arterialFlowFraction = parameterArray[3]
            return highFlowGadoxetate_DualInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3, arterialFlowFraction)
        else:
            return highFlowGadoxetate_SingleInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3)

#Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last) 
#       
def extendedTofts_SingleInput(xData2DArray, Vp, Ve, Ktrans):
    """This function contains the algorithm for calculating how concentration varies with time
        using the Extended Tofts model when it takes just an arterial input.
        
        Input Parameters
        ----------------
            xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array.
            Vp - Plasma Volume Fraction (decimal fraction).
            Ve - Extracellular Volume Fraction (decimal fraction).
            Ktrans - Transfer Rate Constant, (1/min).

        Returns
        -------
        listConcentrationsFromModel - list of calculated concentrations at each of the 
            time points in array 'time'.
        """ 
    try:
        logger.info('In function TracerKineticModels.extendedTofts_SingleInput with Vp={}, Ve={} & Ktrans={}'.format(Vp, Ve, Ktrans))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        
        #Calculate Intracellular transit time, Tc
        Tc = Ve/Ktrans
        
        listConcentrationsFromModel = []
        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*AIFconcentrations + Ve*tools.expconv(Tc, times, AIFconcentrations, 'Extended Tofts')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.extendedTofts_SingleInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.extendedTofts_SingleInput:' + str(e) )

def extendedTofts_DualInput(xData2DArray, Vp, Ve, Ktrans, fAFF):
    """This function contains the algorithm for calculating how concentration varies with time
        using the Extended Tofts model when it takes both an arterial and a venal input.
        
        Input Parameters
        ----------------
            xData2DArray - time, AIF & VIF concentration 1D arrays stacked into one 2D array.
            Vp - Plasma Volume Fraction (decimal fraction).
            Ve - Extracellular Volume Fraction (decimal fraction).
            Ktrans - Transfer Rate Constant, (1/min).
            fAFF - Arterial flow factor (decimal fraction).

        Returns
        -------
        listConcentrationsFromModel - list of calculated concentrations at each of the 
            time points in array 'time'.
        """ 
    try:
        logger.info('In function TracerKineticModels.extendedTofts_DualInput with Vp={}, Ve={},Ktrans={}, fA={} '.format(Vp, Ve, Ktrans, fAFF))
        #print('Extended Tofts. Vp={}, Ve={} and Ktrans={}'.format(Vp, Ve, Ktrans))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]
           
        #Calculate Intracellular transit time, Tc
        Tc = Ve/Ktrans
        #Calculate Venal Flow Factor
        fVFF = 1 - fAFF
        
        listConcentrationsFromModel = []
        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*((fAFF * AIFconcentrations) + (fVFF * VIFconcentrations)) \
            + Ve*tools.expconv(Tc, times, ((fAFF * AIFconcentrations) + (fVFF * VIFconcentrations)), 'Extended Tofts')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.extendedTofts_DualInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.extendedTofts_DualInput:' + str(e) )
            
def oneCompartment_SingleInput(xData2DArray, Vp, Fp):
    """This function contains the algorithm for calculating how concentration varies with time
        using the One Compartment model when it takes just an arterial input.
        
        Input Parameters
        ----------------
            xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array.
            Vp - Plasma Volume Fraction (decimal fraction).
            Fp - Plasma Flow Rate, (ml/min).

        Returns
        -------
        listConcentrationsFromModel - list of calculated concentrations at each of the 
            time points in array 'time'.
        """
    try:
        logger.info('In function TracerKineticModels.oneCompartment_SingleInput with Vp={} and Fp={}'.format(Vp, Fp))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        
        #Calculate Intracellular transit time, Tc
        Tc = Vp/Fp
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*tools.expconv(Tc, times, AIFconcentrations, 'One Compartment')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.oneCompartment_SingleInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.oneCompartment_SingleInput:' + str(e) )

def oneCompartment_DualInput(xData2DArray, Vp, Fp, fAFF):
    """This function contains the algorithm for calculating how concentration varies with time
        using the One Compartment model when it takes both an arterial and a venal input.
        
        Input Parameters
        ----------------
            xData2DArray - time, AIF & VIF concentration 1D arrays stacked into one 2D array.
            Vp - Plasma Volume Fraction (decimal fraction).
            Fp - Plasma Flow Rate, (ml/min).
            fAFF - Arterial flow factor (decimal fraction).

        Returns
        -------
        listConcentrationsFromModel - list of calculated concentrations at each of the 
            time points in array 'time'.
        """
    try:
        logger.info('In function TracerKineticModels.oneCompartment_DualInput with Vp={} and Fp={}'.format(Vp, Fp))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]
        
        #Calculate Intracellular transit time, Tc
        Tc = Vp/Fp

        fVFF = 1 - fAFF
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*tools.expconv(Tc, times, 
                 ((fAFF * AIFconcentrations) + (fVFF * VIFconcentrations)), 'One Compartment')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.oneCompartment_DualInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.oneCompartment_DualInput:' + str(e) )

def highFlowGadoxetate_SingleInput(xData2DArray, Ve, Kce, Kbc):
    """This function contains the algorithm for calculating how concentration varies with time
        using the High Flow Gadoxetate model when it takes just an arterial input.
        
        Input Parameters
        ----------------
            xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array
            Ve - Extracellular Volume Fraction (decimal fraction)
            Kce - Hepatocellular Uptake Rate,(mL/100m L/min)
            Kbc - Biliary Efflux Rate (mL/100mL/min)

        Returns
        -------
        listConcentrationsFromModel - list of calculated concentrations at each of the 
            time points in array 'time'.
        
        """
    try:
        logger.info('In function TracerKineticModels.highFlowGadoxetate_DualInput with Kce={}, Ve={} and Kbc={}'.format(Kce, Ve, Kbc))
        
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        
        #Calculate Intracellular transit time, Tc
        Tc = (1-Ve)/Kbc
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Ve*AIFconcentrations + Kce*Tc*tools.expconv(Tc, times, AIFconcentrations, 'High Flow Gadoxetate')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.highFlowGadoxetate_SingleInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.highFlowGadoxetate_SingleInput:' + str(e) )
    

def highFlowGadoxetate_DualInput(xData2DArray, Ve, Kce, Kbc, fAFF):
    """This function contains the algorithm for calculating how concentration varies with time
        using the High Flow Gadoxetate model when it takes both an arterial and a venal input.
        
        Input Parameters
        ----------------
            xData2DArray - time, AIF & VIF concentration 1D arrays stacked into one 2D array
            Ve - Extracellular Volume Fraction (decimal fraction)
            Kce - Hepatocellular Uptake Rate,(mL/100m L/min)
            Kbc - Biliary Efflux Rate (mL/100mL/min)
            fAFF - Arterial flow factor (decimal fraction).

        Returns
        -------
        listConcentrationsFromModel - list of calculated concentrations at each of the 
            time points in array 'time'.
        
        """
    try:
        logger.info('In function TracerKineticModels.highFlowGadoxetate_DualInput with Kce={}, Ve={} and Kbc={}'.format(Kce, Ve, Kbc))
        
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]
        
        #Calculate Intracellular transit time, Tc
        Tc = (1-Ve)/Kbc
        #Calculate Venal Flow Factor
        fVFF = 1 - fAFF
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Ve*((fAFF * AIFconcentrations) + (fVFF * VIFconcentrations)) \
                + Kce*Tc*tools.expconv(Tc, times, ((fAFF * AIFconcentrations) + (fVFF * VIFconcentrations)), 'High Flow Gadoxetate')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.highFlowGadoxetate_DualInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.highFlowGadoxetate_DualInput:' + str(e) )
    

def curveFit(modelName, times, AIFConcs, VIFConcs, concROI, paramArray, constrain, 
             boolDualInput):
    """This function calls the curve_fit function imported from scipy.optimize 
    to fit a model in this module to actual Region of Interest (ROI)
    concentration/time data using non-linear least squares.  
    During curve fitting, it allows parameter
    values to be constrained by imposing an upper and lower limit on their values.
    
    Input Parameters
    ----------------
        modelName - Name of the model taken from the selected value in the  
            model name drop-down list on the GUI.  Used to select the 
            function corresponding to that model.

        time - NumPy Array of time values stored as floats. Created from a 
            Python list.

        AIFConcs - NumPy Array of concentration values stored as floats. 
            Created from a Python list.  These concentrations are the Arterial
            Input Function input to the model.

        VIFConcs - NumPy Array of concentration values stored as floats. 
            Created from a Python list.  These concentrations are the Venal
            Input Function input to the model.

        concROI - NumPy Array of concentration values stored as floats. 
            Created from a Python list.  These concentrations belong to
            the Region of Interest (ROI).

        paramArray - list of model input parameter values.

        constrain - Boolean that indicates if a contraint should be 
            applied to the input parameters during curve fitting.

        boolDualInput - boolean indicating if the input to the model is 
            single(=False) AIF only or dual(=True) AIF & VIR.

        Returns
        ------
        optimumParams - An array of optimum values of the model input parameters
                that achieve the best curve fit.
        paramCovarianceMatrix - The estimated covariance of the values in optimumParams.
            Used to calculate 95% confidence limits.
    """
    try:
        logger.info('Function TracerKineticModels.curveFit called with model={}, parameters = {} and constrain={}'.format(modelName,paramArray, constrain) )
        
        if boolDualInput == True:
            timeInputConcs2DArray = np.column_stack((times, AIFConcs, VIFConcs))
        else:
            timeInputConcs2DArray = np.column_stack((times, AIFConcs))

        if modelName ==  'Extended Tofts':
            if boolDualInput == True:
                    if constrain == True:
                        return curve_fit(extendedTofts_DualInput, timeInputConcs2DArray, concROI, 
                                  paramArray, bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
                    else:
                        return curve_fit(extendedTofts_DualInput, timeInputConcs2DArray, concROI, 
                                         paramArray)
            else:
                    if constrain == True:
                        return curve_fit(extendedTofts_SingleInput, timeInputConcs2DArray, concROI, 
                                  paramArray, bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
                    else:
                        return curve_fit(extendedTofts_SingleInput, timeInputConcs2DArray, concROI, 
                                         paramArray)
        elif modelName ==  'One Compartment':
            if boolDualInput == True:
                    if constrain == True:
                        return curve_fit(oneCompartment_DualInput, timeInputConcs2DArray, concROI, 
                                  paramArray, bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
                    else:
                        return curve_fit(oneCompartment_DualInput, timeInputConcs2DArray, concROI, 
                                         paramArray)
            else:
                    if constrain == True:
                        return curve_fit(oneCompartment_SingleInput, timeInputConcs2DArray, concROI, 
                                  paramArray, bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
                    else:
                        return curve_fit(oneCompartment_SingleInput, timeInputConcs2DArray, concROI, 
                                         paramArray)   
        elif modelName ==  'High-Flow Gadoxetate':
            if boolDualInput == True:
                    if constrain == True:
                        return curve_fit(highFlowGadoxetate_DualInput, timeInputConcs2DArray, concROI, 
                                  paramArray, bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
                    else:
                        return curve_fit(highFlowGadoxetate_DualInput, timeInputConcs2DArray, concROI, 
                                         paramArray)
            else:
                    if constrain == True:
                        return curve_fit(highFlowGadoxetate_SingleInput, timeInputConcs2DArray, concROI, 
                                  paramArray, bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
                    else:
                        return curve_fit(highFlowGadoxetate_SingleInput, timeInputConcs2DArray, concROI, 
                                         paramArray)   

    except ValueError as ve:
        print ('TracerKineticModels.curveFit Value Error: ' + str(ve))
    except RuntimeError as re:
        print('TracerKineticModels.curveFit runtime error: ' + str(re))
    except Exception as e:
        print('TracerKineticModels.curveFit: ' + str(e))        
##  For more information on 
#      scipy.optimize.curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
#      check_finite=True, bounds=(-inf, inf), method=None, jac=None, **kwargs)[source]    
#  See
#   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
#    
    
   

    
    
