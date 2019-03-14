"""This module contains functions that calculate the variation 
of concentration with time according to a tracer kinetic model.
"""
import Tools as tools
import ExceptionHandling as exceptionHandler
import numpy as np
import logging
logger = logging.getLogger(__name__)

# Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last) 

def DualInputTwoCompartmentFiltrationModel(xData2DArray, Fa: float, Ve: float, Fp: float, Kbh: float, Khe: float):
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
        # Logging and exception handling function. 
        exceptionHandler.modelFunctionInfoLogger()

        # Used by logging in tools.expconv mathematical operation
        # function
        funcName = 'DualInputTwoCompartmentFiltrationModel'

        # Start of model logic.
        # In order to use lmfit curve_fit, time and concentration must be
        # combined into one function input parameter, a 2D array, 
        # then separated into individual 1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]
    
        # Calculate Venous Flow Factor, fVFF
        fVFF = 1 - Fa

        # Determine an overall concentration
        combinedConcentration = Fp*(Fa*AIFconcentrations 
                                    + fVFF*VIFconcentrations)
      
        # Calculate Intracellular transit time, Th
        Th = (1-Ve)/Kbh
        Te = Ve/(Fp + Khe)
        
        alpha = np.sqrt( ((1/Te + 1/Th)/2)**2 - 1/(Te*Th) )
        beta = (1/Th - 1/Te)/2
        gamma = (1/Th + 1/Te)/2
    
        Tc1 = 1/(gamma-alpha)
        Tc2 = 1/(gamma+alpha)
    
        modelConcs = []
        ce = (1/(2*Ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1,times,combinedConcentration, funcName + '- 1') + \
                        (1-beta/alpha)*Tc2*tools.expconv(Tc2,times,combinedConcentration, funcName + '- 2')) 
   
        modelConcs = Ve*ce + Khe*Th*tools.expconv(Th,times,ce, funcName + '- 3')
    
        return(modelConcs)

    # Exception handling and logging code.
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)
 

def HighFlowDualInletTwoCompartmentGadoxetateModel(xData2DArray, Fa: float, Ve: float, Khe: float, Kbh: float):
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
        # Logging and exception handling function. 
        exceptionHandler.modelFunctionInfoLogger()

        # In order to use scipy.optimize.curve_fit, time and concentration must be
        # combined into one function input parameter, a 2D array, then separated into individual
        # 1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]
        VIFconcentrations = xData2DArray[:,2]

        # Calculate Venous Flow Factor, fVFF
        fVFF = 1 - Fa

        Th = (1-Ve)/Kbh
    
        # Determine an overall concentration
        combinedConcentration = Fa*AIFconcentrations + fVFF*VIFconcentrations 
    
        modelConcs = []
        modelConcs = (Ve*combinedConcentration + \
        Khe*Th*tools.expconv(Th,times,combinedConcentration,'HighFlowDualInletTwoCompartmentGadoxetateModel'))
        
        return(modelConcs)

    # Exception handling and logging code. 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

def HighFlowSingleInletTwoCompartmentGadoxetateModel(xData2DArray, Ve: float, Khe: float, Kbh: float):
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
        # Logging and exception handling function. 
        exceptionHandler.modelFunctionInfoLogger()

        # In order to use lmfit curve fitting, time and concentration must be
        # combined into one function input parameter, a 2D array, then separated into individual
        # 1 D arrays 
        times = xData2DArray[:,0]
        AIFconcentrations = xData2DArray[:,1]

        Th = (1-Ve)/Kbh
    
        modelConcs = []
        modelConcs = (Ve*AIFconcentrations + Khe*Th*tools.expconv(Th,times,AIFconcentrations,'HighFlowSingleInletTwoCompartmentGadoxetateModel'))
    
        return(modelConcs)

    # Exception handling and logging code. 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)