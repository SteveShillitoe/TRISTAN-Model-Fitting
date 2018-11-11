import Tools as tools
from scipy.optimize import curve_fit
from lmfit import Model, Parameters
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

def modelSelector(modelName, times, AIFConcentration, parameterArray, boolDualInput, VIFConcentration=[]):
    """Function called in the GUI of the model fitting tool to select the function corresponding
        to each model"""
    logger.info("In TracerKineticModels.modelSelector. Called with model {} and parameters {}".format(modelName, parameterArray))
    
    parameter1 = parameterArray[0]
    parameter2 = parameterArray[1]
    
    if boolDualInput == True:
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration, VIFConcentration))
    else:
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration))

    if modelName ==  'Extended Tofts':
        parameter3 = parameterArray[2]
        if boolDualInput == True:
            fractionAIF = parameterArray[3]
            fractionVIF = parameterArray[4]
            return extendedTofts_DualInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3, fractionAIF, fractionVIF)
        else:
            return extendedTofts_SingleInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3)
    elif modelName ==  'One Compartment':
        if boolDualInput == True:
            fractionAIF = parameterArray[2]
            fractionVIF = parameterArray[3]
            return oneCompartment_DualInput(timeInputConcs2DArray, parameter1, parameter2, 
              fractionAIF, fractionVIF)
        else:
            return oneCompartment_SingleInput(timeInputConcs2DArray, parameter1, parameter2)
    elif modelName ==  'High-Flow Gadoxetate':
        parameter3 = parameterArray[2]
        fractionAIF = parameterArray[3]
        fractionVIF = parameterArray[4]
        if boolDualInput == True:
            return highFlowGadoxetate_DualInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3, fractionAIF, fractionVIF)
        else:
            return highFlowGadoxetate_SingleInput(timeInputConcs2DArray, parameter1, parameter2, 
              parameter3)

#Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last) 
#       
def extendedTofts_SingleInput(xData2DArray, Vp, Ve, Ktrans):
    """This function contains the algorithm for calculating how concentration varies with time
        using the Extended Tofts model""" 
    try:
        logger.info('In function TracerKineticModels.extendedTofts_SingleInput with Vp={}, Ve={} & Ktrans={}'.format(Vp, Ve, Ktrans))
        #print('Extended Tofts. Vp={}, Ve={} and Ktrans={}'.format(Vp, Ve, Ktrans))
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

def extendedTofts_DualInput(xData2DArray, Vp, Ve, Ktrans, fAIF, fVIF):
    """This function contains the algorithm for calculating how concentration varies with time
        using the Extended Tofts model""" 
    try:
        logger.info('In function TracerKineticModels.extendedTofts_DualInput with Vp={}, Ve={},Ktrans={}, fA={} and fV={}'.format(Vp, Ve, Ktrans, fAIF, fVIF))
        #print('Extended Tofts. Vp={}, Ve={} and Ktrans={}'.format(Vp, Ve, Ktrans))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]
           
        #Calculate Intracellular transit time, Tc
        Tc = Ve/Ktrans
        
        listConcentrationsFromModel = []
        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*((fAIF * AIFconcentrations) + (fVIF * VIFconcentrations)) \
            + Ve*tools.expconv(Tc, times, ((fAIF * AIFconcentrations) + (fVIF * VIFconcentrations)), 'Extended Tofts')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.extendedTofts_DualInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.extendedTofts_DualInput:' + str(e) )
            
def oneCompartment_SingleInput(xData2DArray, Vp, Fp):
    """This function contains the algorithm for calculating how concentration varies with time
        using the One Compartment model"""
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

def oneCompartment_DualInput(xData2DArray, Vp, Fp, fAIF, fVIF):
    """This function contains the algorithm for calculating how concentration varies with time
        using the One Compartment model"""
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
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*tools.expconv(Tc, times, 
                 ((fAIF * AIFconcentrations) + (fVIF * VIFconcentrations)), 'One Compartment')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.oneCompartment_DualInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.oneCompartment_DualInput:' + str(e) )

def highFlowGadoxetate_SingleInput(xData2DArray, Ve, Kce, Kbc):
    """This function contains the algorithm for calculating how concentration varies with time
        using the High Flow Gadoxetate model"""
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
    

def highFlowGadoxetate_DualInput(xData2DArray, Ve, Kce, Kbc, fAIF, fVIF):
    """This function contains the algorithm for calculating how concentration varies with time
        using the High Flow Gadoxetate model"""
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
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Ve*((fAIF * AIFconcentrations) + (fVIF * VIFconcentrations)) \
                + Kce*Tc*tools.expconv(Tc, times, ((fAIF * AIFconcentrations) + (fVIF * VIFconcentrations)), 'High Flow Gadoxetate')
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.highFlowGadoxetate_DualInput: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.highFlowGadoxetate_DualInput:' + str(e) )
    

def curveFit(modelName, times, AIFConcs, VIFConcs, concROI, paramArray, constrain, boolDualInput):
    """This function calls the curve_fit function imported from scipy.optimize to fit any of
    the models in this module to actual concentration/time data using non-linear least squares"""
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
    
   

    
    
