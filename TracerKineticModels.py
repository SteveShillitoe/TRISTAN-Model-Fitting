"""This module contains functions that calculate the variation of concentration
with time according to several tracer kinetic models.  

The dictionary modelDict holds the names of these models for display in a dropdown list.

The function ModelSelector coordinates the execution of the appropriate function 
according to the model selected on the GUI.

The function, CurveFit calls the curve_fit function imported from scipy.optimize 
to fit any of the models in this module to actual concentration/time data 
using non-linear least squares.  
"""

import Tools as tools
from scipy.optimize import curve_fit
from lmfit import minimize, Parameters, Model
import numpy as np
import logging

#Create logger
logger = logging.getLogger(__name__)

#Dictionary of model names - short name:long name pairs
modelDict = {'Select a model':'Select a model',
                   '2-2CFM':'2 Inlet - Two Compartment Filtration Model',
                   'HF2-2CFM':'High Flow 2 Inlet - Two Compartment Filtration Model',
                   'HF1-2CFM':'High Flow 1 Inlet - Two Compartment Filtration Model'}

#Dictionary linking the model with a graphic file containing its visual representation.
modelImageDict = {'2-2CFM':'images\\DualInletTwoCompartmentGadoxetateModel.png',
                   'HF2-2CFM':'images\\HighFlowDualInletTwoCompartmentGadoxetateModel.png',
                   'HF1-2CFM':'images\\HighFlowSingleInletTwoCompartmentGadoxetateModel.png',
                   'HF1-2CFM-FixVe':'images\\HighFlowSingleInletTwoCompartmentGadoxetateModel_fixedve.png'}

#Dictionary linking a model with its input type:single or dual
modelInletTypeDict = {'2-2CFM':'dual',
                    'HF2-2CFM':'dual',
                     'HF1-2CFM':'single'}

#Constants
PARAMETER_UPPER_BOUND_VOL_FRACTION = 1.0
PARAMETER_UPPER_BOUND_RATE = np.inf

def GetListModels():
    return list(modelDict.keys())

def GetLongModelName(shortModelName, fixVe:bool = False) -> str:
    """Returns the full name of a model whose short name is shortModelName."""
    longName =  modelDict.get(shortModelName)
    if fixVe:
       longName = longName + '-Fixed Ve'
    return longName

def GetModelImageName(shortModelName, fixVe:bool = False) -> str:
    """Returns the file path and name of the image that represents schematically
    the model whose short name is shortModelName."""
    if fixVe:
        shortModelName = shortModelName + '-FixVe'
    return modelImageDict.get(shortModelName)

def GetModelInletType(shortModelName) -> str:
    """Returns the inlet type (single or dual) of the model whose short name is shortModelName."""
    return modelInletTypeDict.get(shortModelName)

def ModelSelector(modelName: str, times, AIFConcentration, parameterArray, fixVe: bool,
                  VIFConcentration=[]):
    """Function called in the GUI of the model fitting application to select the 
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
            Created from a Python list.  These concentrations are the Venous
            Input Function input to the model.

        Returns
        ------
        Returns the return value from the selected model function that is a list of
        concentrations calculated at the times in the array time.
        """
    logger.info("In TracerKineticModels.ModelSelector. Called with model {} and parameters {}".format(modelName, parameterArray))

    if modelName == '2-2CFM':
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration, VIFConcentration))
        arterialFlowFraction = parameterArray[0]
        Ve = parameterArray[1]
        Fp = parameterArray[2]
        Khe = parameterArray[3]
        Kbh = parameterArray[4]
        return DualInputTwoCompartmentFiltrationModel(timeInputConcs2DArray, arterialFlowFraction,
            Ve, Fp, Khe, Kbh)
    elif modelName == 'HF2-2CFM':
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration, VIFConcentration))
        arterialFlowFraction = parameterArray[0]
        Ve = parameterArray[1]
        Khe = parameterArray[2]
        Kbh = parameterArray[3]
        return HighFlowDualInletTwoCompartmentGadoxetateModel(timeInputConcs2DArray, arterialFlowFraction,
              Ve, Khe, Kbh)
    elif modelName == 'HF1-2CFM':
        timeInputConcs2DArray = np.column_stack((times, AIFConcentration))
        Ve = parameterArray[0]
        Khe = parameterArray[1]
        Kbh = parameterArray[2]
        if fixVe:
            return HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe(
                timeInputConcs2DArray, Khe, Kbh)
        else:
            return HighFlowSingleInletTwoCompartmentGadoxetateModel(
                timeInputConcs2DArray, Ve, Khe, Kbh)
        
#Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last) 
# 
def DualInputTwoCompartmentFiltrationModel(xData2DArray, fAFF: float, 
                                           Ve: float, Fp: float, Khe: float, Kbh: float):
    """This function contains the algorithm for calculating how concentration varies with time
            using the Dual Input Two Compartment Filtration Model model.
        
            Input Parameters
            ----------------
                xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array.
                Vp - Plasma Volume Fraction (decimal fraction).
                Fp - Total Plasma Inflow (mL/min/mL)
                Khe - Hepatocyte Uptake Rate (mL/min/mL)
                Kbh - 'Biliary Efflux Rate (mL/min/mL)'

            Returns
            -------
            modelConcs - list of calculated concentrations at each of the 
                time points in array 'time'.
            """ 
    try:
        logger.info('In function TracerKineticModels.DualInputTwoCompartmentFiltrationModel ' +
          'with fAFF={}, Ve={}, Fp={}, Khe={} & Kbh={}'.format(fAFF, Ve, Fp, Khe, Kbh))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]
    
        #Calculate Venous Flow Factor, fVFF
        fVFF = 1 - fAFF

        #Determine an overall concentration
        combinedConcentration = Fp*(fAFF*AIFconcentrations + fVFF*VIFconcentrations)
      
        #Calculate Intracellular transit time, Th
        Th = (1-Ve)/Kbh
        Te = Ve/(Fp + Khe)
        
        alpha = np.sqrt( ((1/Te + 1/Th)/2)**2 - 1/(Te*Th) )
        beta = (1/Th - 1/Te)/2
        gamma = (1/Th + 1/Te)/2
    
        Tc1 = 1/(gamma-alpha)
        Tc2 = 1/(gamma+alpha)
    
        modelConcs = []
        ce = (1/(2*Ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1,times,combinedConcentration,'DualInputTwoCompartmentFiltrationModel - 1') + 
                        (1-beta/alpha)*Tc2*tools.expconv(Tc2,times,combinedConcentration,'DualInputTwoCompartmentFiltrationModel - 2')) 
   
        modelConcs = Ve*ce + Khe*Th*tools.expconv(Th,times,ce,'DualInputTwoCompartmentFiltrationModel - 3')
    
        return(modelConcs)
    except Exception as e:
            print('Error - TracerKineticModels.TracerKineticModels.DualInputTwoCompartmentFiltrationModel: ' + str(e))
            logger.error('TracerKineticModels.DualInputTwoCompartmentFiltrationModel:' + str(e) )
 
def HighFlowDualInletTwoCompartmentGadoxetateModel(xData2DArray, fAFF: float, 
                                                   Ve: float, Khe: float, Kbh: float):
    """This function contains the algorithm for calculating how concentration varies with time
            using the High Flow Dual Inlet Two Compartment Gadoxetate Model model.
        
            Input Parameters
            ----------------
                xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array.
                Vp - Plasma Volume Fraction (decimal fraction).
                Khe - Hepatocyte Uptake Rate (mL/min/mL)
                Kbh - 'Biliary Efflux Rate (mL/min/mL)' 

            Returns
            -------
            modelConcs - list of calculated concentrations at each of the 
                time points in array 'time'.
            """ 
    try:
        logger.info('In function TracerKineticModels.HighFlowDualInletTwoCompartmentGadoxetateModel ' +
          'with fAFF={}, Ve={}, Khe={} & Kbh={}'.format(fAFF, Ve, Khe, Kbh))
        #print('In function TracerKineticModels.HighFlowDualInletTwoCompartmentGadoxetateModel ' +
        #  'with fAFF={}, Ve={}, Khe={} & Kbh={}'.format(fAFF, Ve,  Khe, Kbh))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]

        #Calculate Venous Flow Factor, fVFF
        fVFF = 1 - fAFF

        Th = (1-Ve)/Kbh
    
        #Determine an overall concentration
        combinedConcentration = fAFF*AIFconcentrations + fVFF*VIFconcentrations 
    
        modelConcs = []
        modelConcs = (Ve*combinedConcentration + 
      Khe*Th*tools.expconv(Th,times,combinedConcentration,'HighFlowDualInletTwoCompartmentGadoxetateModel'))
        
        return(modelConcs)
    except Exception as e:
            print('Error - TracerKineticModels.TracerKineticModels.HighFlowDualInletTwoCompartmentGadoxetateModel: ' + str(e))
            logger.error('TracerKineticModels.HighFlowDualInletTwoCompartmentGadoxetateModel:' + str(e) )
 
def HighFlowSingleInletTwoCompartmentGadoxetateModel(xData2DArray, Ve: float, 
                                                     Khe: float, Kbh: float):
    """This function contains the algorithm for calculating how concentration varies with time
            using the High Flow Single Inlet Two Compartment Gadoxetate Model model.
        
            Input Parameters
            ----------------
                xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array.
                Ve - Plasma Volume Fraction (decimal fraction)
                Khe - Hepatocyte Uptake Rate (mL/min/mL)
                Kbh - 'Biliary Efflux Rate (mL/min/mL)'- 

            Returns
            -------
            modelConcs - list of calculated concentrations at each of the 
                time points in array 'time'.
            """ 
    try:
        logger.info('In function TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModel ' +
          'with Ve={}, Khe={} & Kbh={}'.format( Ve, Khe, Kbh))
        #print('In function TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModel ' +
        #  'with Ve={}, Khe={} & Kbh={}'.format( Ve,  Khe, Kbh))
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]

        Th = (1-Ve)/Kbh
    
        modelConcs = []
        modelConcs = (Ve*AIFconcentrations +
       Khe*Th*tools.expconv(Th,times,AIFconcentrations,'HighFlowSingleInletTwoCompartmentGadoxetateModel'))
    
        return(modelConcs)
    except Exception as e:
            print('Error - TracerKineticModels.TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModel: ' + str(e))
            logger.error('TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModel:' + str(e) )

def HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe(xData2DArray, 
                                                     Khe: float, Kbh: float):
    """This function contains the algorithm for calculating how concentration varies with time
            using the High Flow Single Inlet Two Compartment Gadoxetate Model model with FixedVe.
        
            Input Parameters
            ----------------
                xData2DArray - time and AIF concentration 1D arrays stacked into one 2D array.
                Khe - Hepatocyte Uptake Rate (mL/min/mL)
                Kbh - 'Biliary Efflux Rate (mL/min/mL)'- 

            Returns
            -------
            modelConcs - list of calculated concentrations at each of the 
                time points in array 'time'.
            """ 
    try:
        logger.info('In function TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe ' +
          'with Khe={} & Kbh={}'.format(Khe, Kbh))
        
        #In order to use scipy.optimize.curve_fit, time and concentration must be
        #combined into one function input parameter, a 2D array, then separated into individual
        #1 D arrays 
        times = xData2DArray[:,0]
        AIFconcs = xData2DArray[:,1]
        Tc = 1/Kbh
    
        modelConcs = []
        modelConcs = Khe*Tc*tools.expconv(Tc,times,AIFconcs,'HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe')
    
        return(modelConcs)

    except Exception as e:
            print('Error - TracerKineticModels.TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe: ' + str(e))
            logger.error('TracerKineticModels.HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe:' + str(e) )

def CurveFit(modelName: str, times, AIFConcs, VIFConcs, concROI, 
             paramArray, constrain: bool, fixVe: bool):
    """This function calls the curve_fit function imported from scipy.optimize 
    to fit the time/conconcentration data calculated by a model in this module 
    to actual Region of Interest (ROI) concentration/time data using   
    non-linear least squares. 

    In the function calls to curve_fit, bounds are set on the input parameters to 
    avoid division by zero errors.

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
            Created from a Python list.  These concentrations are the Venous
            Input Function input to the model.

        concROI - NumPy Array of concentration values stored as floats. 
            Created from a Python list.  These concentrations belong to
            the Region of Interest (ROI).

        paramArray - list of model input parameter values.

        constrain - Boolean that indicates if a contraint should be 
            applied to the input parameters during curve fitting.

        Returns
        ------
        optimumParams - An array of optimum values of the model input parameters
                that achieve the best curve fit.
        paramCovarianceMatrix - The estimated covariance of the values in optimumParams.
            Used to calculate 95% confidence limits.
    """
    try:
        logger.info('Function TracerKineticModels.CurveFit called with model={}, parameters = {} and constrain={}'.format(modelName,paramArray, constrain) )
        
        if GetModelInletType(modelName) == 'dual':
            timeInputConcs2DArray = np.column_stack((times, AIFConcs, VIFConcs))
        else:
            timeInputConcs2DArray = np.column_stack((times, AIFConcs))

        if modelName ==  '2-2CFM':
            return curve_fit(DualInputTwoCompartmentFiltrationModel, 
                             timeInputConcs2DArray, concROI, paramArray,
                             bounds=([0.0,0.0001,0.0,0.0,0.0001], [1., 0.9999, 100.0, 100.0, 100.0]))
        #fAFF, Ve, Fp, Khe, Kbh

        elif modelName == 'HF2-2CFM':
            return curve_fit(HighFlowDualInletTwoCompartmentGadoxetateModel, 
                             timeInputConcs2DArray, concROI, paramArray,
                            bounds=([0.0,0.0001,0.0,0.0001], [1., 0.9999, 100.0, 100.0]))
            
        elif modelName == 'HF1-2CFM':
            if fixVe:
                Ve = paramArray[0] 
                Khe = paramArray[1]
                Kbh = paramArray[2]
                params = []
                params.append(Khe)
                params.append(Kbh)
            
                hep_conc = (concROI - Ve*AIFConcs)/(1-Ve)
                return curve_fit(HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe, 
                             timeInputConcs2DArray, hep_conc, params,
                             bounds=([0.0,0.0001], [100.0, 100.0]))
            else:
                return curve_fit(HighFlowSingleInletTwoCompartmentGadoxetateModel, 
                             timeInputConcs2DArray, concROI, paramArray,
                             bounds=([0.0001,0.0,0.0001], [0.9999, 100.0, 100.0]))
            
    except ValueError as ve:
        print ('TracerKineticModels.CurveFit Value Error: ' + str(ve))
    except RuntimeError as re:
        print('TracerKineticModels.CurveFit runtime error: ' + str(re))
    except Exception as e:
        print('TracerKineticModels.CurveFit: ' + str(e))        
##  For more information on 
#      scipy.optimize.curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
#      check_finite=True, bounds=(-inf, inf), method=None, jac=None, **kwargs)[source]    
#  See
#   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
#    
    
   

    
    
