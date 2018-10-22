import Tools as tools
from scipy.optimize import curve_fit
import numpy as np
import logging

#Create logger
logger = logging.getLogger(__name__)

#############################################
##          TracerKineticModels module    ###
#############################################
"""This module contains functions that perform the calculation of concentration according
to several tracer kinetic models.  

The global list variable modelNames lists these models
for display in a dropdown list."""


modelNames = ['Select a model','Extended Tofts','One Compartment','High-Flow Gadoxetate']
PARAMETER_LOWER_BOUND = 0
PARAMETER_UPPER_BOUND = 5.0


def modelSelector(modelName, times, inputConcentration, parameter1, parameter2, parameter3):
    """Function called in the GUI of the model fitting tool to select the function corresponding
        to each model"""
    logger.info("In TracerKineticModels.modelSelector. Called with model {} and parameters {}, {}, {}".format(modelName, parameter1, parameter2, parameter3 ))
    timeInputConc2DArray = np.column_stack((times, inputConcentration,))
    if modelName ==  'Extended Tofts':
        return extendedTofts(timeInputConc2DArray, parameter1, parameter2, parameter3)
    elif modelName ==  'One Compartment':
        return oneCompartment(timeInputConc2DArray, parameter1, parameter2)
    elif modelName ==  'High-Flow Gadoxetate':
        return highFlowGadoxetate(timeInputConc2DArray, parameter1, parameter2, parameter3)
    elif modelName ==  'Descriptive':
        return ROI_OnlyModel()
    elif modelName ==  'AIF & VIF':
        return AIF_VIF_Model()
    

#def ROI_OnlyModel():
#        listConcentrationsFromModel = []
#        for i in range(0,60):
#            x = random.random()
#            listConcentrationsFromModel.append(x)
#        return listConcentrationsFromModel

#def AIF_VIF_Model():
#        listConcentrationsFromModel = []
#        for i in range(0,60):
#            x = random.random()
#            listConcentrationsFromModel.append(x)
#        return listConcentrationsFromModel
        
def extendedTofts(xData2DArray, Vp, Ve, Ktrans):
    """This function contains the algorithm for calculating how concentration varies with time
        using the Extended Tofts model"""
    try:
        logger.info('In function TracerKineticModels.extendedTofts with Vp={}, Ve={} and Ktrans={}'.format(Vp, Ve, Ktrans))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        concentrations = xData2DArray[:,1]
        #Convert Ve from % to ml/ml of tissue
        #Ve = Ve/100
        #Calculate Intracellular transit time, Tc
        Tc = Ve/Ktrans
        listConcentrationsFromModel = []
        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*concentrations + Ve*tools.expconv(Tc, times, concentrations)
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
        #Convert Vp from % to ml/ml of tissue
        #Vp = Vp/100
        #Calculate Intracellular transit time, Tc
        Tc = Vp/Fp
        listConcentrationsFromModel = []

        # expconv calculates convolution of ca and (1/Tc)exp(-t/Tc)
        listConcentrationsFromModel = Vp*tools.expconv(Tc, times, concentrations)
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.oneCompartment: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.oneCompartment:' + str(e) )

def highFlowGadoxetate(xData2DArray, Kce, Ve, Kbc):
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
        listConcentrationsFromModel = Ve*concentrations + Kce*Tc*tools.expconv(Tc, times, concentrations)
        return listConcentrationsFromModel
    except Exception as e:
        print('TracerKineticModels.highFlowGadoxetate: ' + str(e))
        logger.error('Runtime error in function TracerKineticModels.highFlowGadoxetate:' + str(e) )

def curveFit(modelName, times, inputConcentration, concROI, paramArray, constrain):
    """This function calls the curve_fit function imported from scipy.optimize to fit any of
    the models in this module to actual concentration/time data using non-linear least squares"""
    try:
        logger.info('In function TracerKineticModels.curveFit with model={}, parameters = {} and constrain={}'.format(modelName,paramArray, constrain) )
        if constrain == True:
            lowerBound = PARAMETER_LOWER_BOUND
            upperBound = PARAMETER_UPPER_BOUND
        else:
            lowerBound = -np.inf
            upperBound = np.inf

        timeInputConc2DArray = np.column_stack((times, inputConcentration,))
        if modelName ==  'Extended Tofts':
            return curve_fit(extendedTofts, timeInputConc2DArray, concROI, paramArray, bounds=(lowerBound, upperBound))
        elif modelName ==  'One Compartment':
            return curve_fit(oneCompartment, timeInputConc2DArray, concROI, paramArray, bounds=(lowerBound, upperBound))
        elif modelName ==  'High-Flow Gadoxetate':
            return curve_fit(highFlowGadoxetate, timeInputConc2DArray, concROI, paramArray, bounds=(lowerBound, upperBound))
    except ValueError as ve:
        print ('TracerKineticModels.curveFit Value Error: ' + str(ve))
    except RuntimeError as re:
        print('TracerKineticModels.curveFit runtime error: ' + str(re))
    except OptimizeWarning as ow:
        print('TracerKineticModels.curveFit Optimize Warning: ' + str(ow))
    except Exception as e:
        print('TracerKineticModels.curveFit: ' + str(e))


        
##  For more information on 
##      scipy.optimize.curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
##      check_finite=True, bounds=(-inf, inf), method=None, jac=None, **kwargs)[source]    
##  See
##   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html


##    def patlakModel(self, Vp, Ve, Ktrans, objectGUI):
##        print('patlakModel model selected')
##        objectGUI.spinBoxKtrans.setEnabled(True)
##        listConcentrationsFromModel = []
##        for i in range(0,60):
##            x = random.random()
##            listConcentrationsFromModel.append(x)
##        return listConcentrationsFromModel
##    
    
   

    
    
