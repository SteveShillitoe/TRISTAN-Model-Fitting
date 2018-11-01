import Tools as tools
from scipy.optimize import curve_fit
import numpy as np
import logging

#Create logger
logger = logging.getLogger(__name__)

"""This module contains functions that perform the calculation of concentration according
to several tracer kinetic models.  

The list modelNames holds the names of these models for display in a dropdown list."""


modelNames = ['Select a model','Extended Tofts','One Compartment','High-Flow Gadoxetate']

PARAMETER_UPPER_BOUND_VOL_FRACTION = 1.0
PARAMETER_UPPER_BOUND_RATE = np.inf

def modelSelector(modelName, times, inputConcentration, parameterArray):
    """Function called in the GUI of the model fitting tool to select the function corresponding
        to each model"""
    logger.info("In TracerKineticModels.modelSelector. Called with model {} and parameters {}".format(modelName, parameterArray))
    timeInputConc2DArray = np.column_stack((times, inputConcentration,))
    parameter1 = parameterArray[0]
    parameter2 = parameterArray[1]
    if len(parameterArray) == 3:
        parameter3 = parameterArray[2]

    if modelName ==  'Extended Tofts':
        return extendedTofts(timeInputConc2DArray, parameter1, parameter2, parameter3)
    elif modelName ==  'One Compartment':
        return oneCompartment(timeInputConc2DArray, parameter1, parameter2)
    elif modelName ==  'High-Flow Gadoxetate':
        return highFlowGadoxetate(timeInputConc2DArray, parameter1, parameter2, parameter3)
    
#Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last)        
def extendedTofts(xData2DArray, Vp, Ve, Ktrans):
    """This function contains the algorithm for calculating how concentration varies with time
        using the Extended Tofts model"""
    try:
        logger.info('In function TracerKineticModels.extendedTofts with Vp={}, Ve={} and Ktrans={}'.format(Vp, Ve, Ktrans))
        #print('Extended Tofts. Vp={}, Ve={} and Ktrans={}'.format(Vp, Ve, Ktrans))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        concentrations = xData2DArray[:,1]
        #Calculate Intracellular transit time, Tc
        Tc = Ve/Ktrans
        listConcentrationsFromModel = []
        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*concentrations + Ve*tools.expconv(Tc, times, concentrations, 'Extended Tofts')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.extendedTofts: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.extendedTofts:' + str(e) )
            
def oneCompartment(xData2DArray, Vp, Fp):
    """This function contains the algorithm for calculating how concentration varies with time
        using the One Compartment model"""
    try:
        logger.info('In function TracerKineticModels.oneCompartment with Vp={} and Fp={}'.format(Vp, Fp))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays
        times = xData2DArray[:,0]
        concentrations = xData2DArray[:,1]
        #Calculate Intracellular transit time, Tc
        Tc = Vp/Fp
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*tools.expconv(Tc, times, concentrations, 'One Compartment')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.oneCompartment: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.oneCompartment:' + str(e) )

def highFlowGadoxetate(xData2DArray, Ve, Kce, Kbc):
    """This function contains the algorithm for calculating how concentration varies with time
        using the High Flow Gadoxetate model"""
    try:
        logger.info('In function TracerKineticModels.highFlowGadoxetate with Kce={}, Ve={} and Kbc={}'.format(Kce, Ve, Kbc))
        
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays
        times = xData2DArray[:,0]
        concentrations = xData2DArray[:,1]
        #Calculate Intracellular transit time, Tc
        Tc = (1-Ve)/Kbc
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Ve*concentrations + Kce*Tc*tools.expconv(Tc, times, concentrations, 'High Flow Gadoxetate')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.highFlowGadoxetate: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.highFlowGadoxetate:' + str(e) )

def curveFit(modelName, times, inputConcentration, concROI, paramArray, constrain):
    """This function calls the curve_fit function imported from scipy.optimize to fit any of
    the models in this module to actual concentration/time data using non-linear least squares"""
    try:
        logger.info('Function TracerKineticModels.curveFit called with model={}, parameters = {} and constrain={}'.format(modelName,paramArray, constrain) )

        timeInputConc2DArray = np.column_stack((times, inputConcentration,))
        if constrain == True:
            if modelName ==  'Extended Tofts':
                return curve_fit(extendedTofts, timeInputConc2DArray, concROI, paramArray, 
                                  bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                             PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                             PARAMETER_UPPER_BOUND_RATE]))
            elif modelName ==  'One Compartment':
                return curve_fit(oneCompartment, timeInputConc2DArray, concROI, paramArray,
                                bounds=(0,[PARAMETER_UPPER_BOUND_VOL_FRACTION,
                                                PARAMETER_UPPER_BOUND_RATE]))
            elif modelName ==  'High-Flow Gadoxetate':
                return curve_fit(highFlowGadoxetate, timeInputConc2DArray, concROI, paramArray, 
                                 bounds=(0.000001,[PARAMETER_UPPER_BOUND_VOL_FRACTION, 
                                            PARAMETER_UPPER_BOUND_RATE,
                                            PARAMETER_UPPER_BOUND_RATE]))
        else:  #No Constraints
            if modelName ==  'Extended Tofts':
                return curve_fit(extendedTofts, timeInputConc2DArray, concROI, paramArray, bounds=(-np.inf, np.inf))
            elif modelName ==  'One Compartment':
                return curve_fit(oneCompartment, timeInputConc2DArray, concROI, paramArray, bounds=(-np.inf, np.inf))
            elif modelName ==  'High-Flow Gadoxetate':
                return curve_fit(highFlowGadoxetate, timeInputConc2DArray, concROI, paramArray, bounds=(-np.inf, np.inf))
            
    except ValueError as ve:
        print ('TracerKineticModels.curveFit Value Error: ' + str(ve))
    except RuntimeError as re:
        print('TracerKineticModels.curveFit runtime error: ' + str(re))
    except Exception as e:
        print('TracerKineticModels.curveFit: ' + str(e))
    

        
##  For more information on 
##      scipy.optimize.curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
##      check_finite=True, bounds=(-inf, inf), method=None, jac=None, **kwargs)[source]    
##  See
##   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
##    
    
   

    
    
