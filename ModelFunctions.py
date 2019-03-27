"""This module contains functions that calculate the variation 
of concentration with time according to a tracer kinetic model.
"""
import Tools as tools
import ExceptionHandling as exceptionHandler
import numpy as np
from scipy.optimize import fsolve
from joblib import Parallel, delayed
import logging
logger = logging.getLogger(__name__)

def spgr3d_func(x, FA, TR, R10, S0, S):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        E0 = np.exp(-TR*R10)
        E1 = np.exp(-TR*x)
        c = np.cos(FA*np.pi/180)
        out = S - S0*(1-E1)*(1-c*E0)/((1-E0)*(1-c*E1))
        return(out)
    
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

def spgr3d_func_inv(r1, FA, TR, R10, conc):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        s = np.sin(FA*np.pi/180)
        c = np.cos(FA*np.pi/180)
        E0 = np.exp(-TR*R10)
        E1 = np.exp(-TR*r1*conc)
        Srel = s*(1-E0*E1)/(1-c*E0*E1)
        return(Srel)
   
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)
    
def spgr2d_func(x, FA, TR, R10, S0, S):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        E0 = np.exp(-TR*R10)
        E1 = np.exp(-TR*x/2)
        c = np.cos(FA*np.pi/180)
        # Derive the actual S0 from the baseline signal
        p0 = np.sqrt(E0)
        p1 = 1-p0
        p2 = 1+p0
        p3 = 1-(c**3)*E0*E0
        sf = p1*(1 + (c**2)*p0*p2*(1+E0*c)/p3)
        S_0 = S0/sf
    
        k0 = np.sqrt(E1)
        k1 = 1-k0
        k2 = 1+k0
        k3 = 1-(c**3)*E1*E1
        out = S - S_0*k1*(1 + (c**2)*k0*k2*(1+E1*c)/k3)
        return(out)
    
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)


def spgr2d_func_inv(r1, FA, TR, R10, conc):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        s = np.sin(FA*np.pi/180)
        c = np.cos(FA*np.pi/180)
        E0 = np.exp(-TR*R10)
        E1 = np.exp(-TR*r1*conc/2)
    
        k0 = np.sqrt(E1*E0)
        k1 = 1-k0
        k2 = 1+k0
        k3 = 1-(c**3)*E1*E1*E0*E0   
        Srel = s*k1*(1 + (c**2)*k0*k2*(1+E1*E0*c)/k3)
        return(Srel) 
    
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

# Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last) 

####################################################################
####  MR Signal Models 
####################################################################
def DualInletTwoCompartmentGadoxetateAnd2DSPGRModel(xData2DArray, Fa, Ve, Fp, Kbh, Khe):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        funcName = 'DualInletTwoCompartmentGadoxetateAnd2DSPGRModel'
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        signalVIF = xData2DArray[:,2]
        fv = 1 - Fa
    
        # SPGR model parameters
        TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
        dt = 16 #temporal resolution in sec
        t0 = 5*dt # Duration of baseline scans
        FA = 15 #degrees
        r1 = 5.9 # Hz/mM
        R10a = 1/1.500 # Hz
        R10v = 1/1.500 # Hz
        R10t = 1/0.800 # Hz
    
        # Precontrast signal
        Sa_baseline = np.mean(signalAIF[0:int(t0/t[1])-1])
        Sv_baseline = np.mean(signalVIF[0:int(t0/t[1])-1])
    
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, signalAIF[p])) for p in np.arange(0,len(t)))]
        R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, signalVIF[p])) for p in np.arange(0,len(t)))]
    
        R1a = np.squeeze(R1a)
        R1v = np.squeeze(R1v)

        concAIF = (R1a - R10a)/r1 
        concVIF = (R1v - R10v)/r1
    
        c_if = Fp*(Fa*concAIF + fv*concVIF)
      
        Th = (1-Ve)/Kbh
        Te = Ve/(Fp + Khe)
    
        alpha = np.sqrt( ((1/Te + 1/Th)/2)**2 - 1/(Te*Th) )
        beta = (1/Th - 1/Te)/2
        gamma = (1/Th + 1/Te)/2
    
        # conc = (Ve + Khe(1+Kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*Fp/Ve (Fa concAIF(t)+fv concVIF(t))
        # Let ce(t) = exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*c_if(t) then
        # conc = (Ve + Khe(1+Kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*ce(t)
        Tc1 = 1/(gamma-alpha)
        Tc2 = 1/(gamma+alpha)
    
        ce = (1/(2*Ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1, t, c_if, funcName) + (1-beta/alpha)*Tc2*tools.expconv(Tc2, t, c_if, funcName) )
        ct = Ve*ce + Khe*Th*tools.expconv(Th, t, ce, funcName)
    
        # Convert to signal
        St_rel = spgr2d_func_inv(r1, FA, TR, R10t, ct)
        
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)


def DualInletTwoCompartmentGadoxetateAnd3DSPGRModel(xData2DArray, Fa, Ve, Fp, Kbh, Khe):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        funcName = 'DualInletTwoCompartmentGadoxetateAnd3DSPGRModel'
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        signalVIF = xData2DArray[:,2]
        fv = 1 - Fa
    
        # SPGR model parameters
        TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
        dt = 16 #temporal resolution in sec
        t0 = 5*dt # Duration of baseline scans
        FA = 15 #degrees
        r1 = 5.9 # Hz/mM
        R10a = 1/1.500 # Hz
        R10v = 1/1.500 # Hz
        R10t = 1/0.800 # Hz
    
        # Precontrast signal
        Sa_baseline = np.mean(signalAIF[0:int(t0/t[1])-1])
        Sv_baseline = np.mean(signalVIF[0:int(t0/t[1])-1])
    
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, signalAIF[p])) for p in np.arange(0,len(t)))]
        R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, signalVIF[p])) for p in np.arange(0,len(t)))]
        
        R1a = np.squeeze(R1a)
        R1v = np.squeeze(R1v)

        concAIF = (R1a - R10a)/r1
        concVIF = (R1v - R10v)/r1
    
        c_if = Fp*(Fa*concAIF + fv*concVIF)
      
        Th = (1-Ve)/Kbh
        Te = Ve/(Fp + Khe)
    
        alpha = np.sqrt( ((1/Te + 1/Th)/2)**2 - 1/(Te*Th) )
        beta = (1/Th - 1/Te)/2
        gamma = (1/Th + 1/Te)/2
    
        # conc = (Ve + Khe(1+Kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*Fp/Ve (Fa concAIF(t)+fv concVIF(t))
        # Let ce(t) = exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*c_if(t) then
        # conc = (Ve + Khe(1+Kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*ce(t)
        Tc1 = 1/(gamma-alpha)
        Tc2 = 1/(gamma+alpha)
    
        ce = (1/(2*Ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1, t, c_if, funcName) + (1-beta/alpha)*Tc2*tools.expconv(Tc2, t, c_if, funcName) )
        ct = Ve*ce + Khe*Th*tools.expconv(Th, t, ce, funcName)
    
        # Convert to signal
        St_rel = spgr3d_func_inv(r1, FA, TR, R10t, ct)
        print("Signal from model {} = {}".format(funcName, St_rel))
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)


def HighFlowDualInletTwoCompartmentGadoxetateAnd3DSPGRModel(xData2DArray, Fa, Ve, Kbh, Khe):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        funcName = 'HighFlowDualInletTwoCompartmentGadoxetateAnd3DSPGRModel'
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        signalVIF = xData2DArray[:,2]
        fv = 1 - Fa
    
        # SPGR model parameters
        TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
        dt = 16 #temporal resolution in sec
        t0 = 5*dt # Duration of baseline scans
        FA = 15 #degrees
        r1 = 5.9 # Hz/mM
        R10a = 1/1.500 # Hz
        R10v = 1/1.500 # Hz
        R10t = 1/0.800 # Hz
    
        # Precontrast signal
        Sa_baseline = np.mean(signalAIF[0:int(t0/t[1])-1])
        Sv_baseline = np.mean(signalVIF[0:int(t0/t[1])-1])
    
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, signalAIF[p])) for p in np.arange(0,len(t)))]
        R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, signalVIF[p])) for p in np.arange(0,len(t)))]
    
        R1a = np.squeeze(R1a)
        R1v = np.squeeze(R1v)

        concAIF = (R1a - R10a)/r1
        concVIF = (R1v - R10v)/r1
    
        c_if = Fa*concAIF + fv*concVIF
      
        Th = (1-Ve)/Kbh
    
        ce = c_if
        ct = Ve*ce + Khe*Th*tools.expconv(Th, t, ce, funcName)
    
        # Convert to signal
        St_rel = spgr3d_func_inv(r1, FA, TR, R10t, ct)
    
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

def HighFlowDualInletTwoCompartmentGadoxetateAnd2DSPGRModel(xData2DArray, Fa, Ve, Khe, Kbh):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        funcName = 'HighFlowDualInletTwoCompartmentGadoxetateAnd2DSPGRModel'
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
        signalVIF = xData2DArray[:,2]
        fv = 1 - Fa
    
        # SPGR model parameters
        TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
        dt = 16 #temporal resolution in sec
        t0 = 5*dt # Duration of baseline scans
        FA = 15 #degrees
        r1 = 5.9 # Hz/mM
        R10a = 1/1.500 # Hz
        R10v = 1/1.500 # Hz
        R10t = 1/0.800 # Hz
    
        # Precontrast signal
        Sa_baseline = np.mean(signalAIF[0:int(t0/t[1])-1])
        Sv_baseline = np.mean(signalVIF[0:int(t0/t[1])-1])
    
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, signalAIF[p])) for p in np.arange(0,len(t)))]
        R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, signalVIF[p])) for p in np.arange(0,len(t)))]
    
        R1a = np.squeeze(R1a)
        R1v = np.squeeze(R1v)

        concAIF = (R1a - R10a)/r1
        concVIF = (R1v - R10v)/r1
    
        c_if = Fa*concAIF + fv*concVIF
      
        Th = (1-Ve)/Kbh
    
        ce = c_if
        ct = Ve*ce + Khe*Th*tools.expconv(Th, t, ce, funcName)
    
        # Convert to signal
        St_rel = spgr2d_func_inv(r1, FA, TR, R10t, ct)
    
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)


def HighFlowSingleInletTwoCompartmentGadoxetateAnd2DSPGRModel(xData2DArray, Ve, Kbh, Khe):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        funcName = 'HighFlowSingleInletTwoCompartmentGadoxetateAnd2DSPGRMode'
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
    
        # SPGR model parameters
        TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
        dt = 16 #temporal resolution in sec
        t0 = 5*dt # Duration of baseline scans
        FA = 15 #degrees
        r1 = 5.9 # Hz/mM
        R10a = 1/1.500 # Hz
        R10t = 1/0.800 # Hz
    
        # Precontrast signal
        Sa_baseline = np.mean(signalAIF[0:int(t0/t[1])-1])
    
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, signalAIF[p])) for p in np.arange(0,len(t)))]
        R1a = np.squeeze(R1a)
        
        concAIF = (R1a - R10a)/r1
    
        c_if = concAIF
      
        Th = (1-Ve)/kbh
    
        ce = c_if
        ct = Ve*ce + Khe*Th*tools.expconv(Th, t, ce, funcName)
    
        # Convert to signal
        St_rel = spgr2d_func_inv(r1, FA, TR, R10t, ct)
    
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)


def HighFlowSingleInletTwoCompartmentGadoxetateAnd3DSPGRModel(xData2DArray, Ve, Kbh, Khe):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        funcName = 'HighFlowSingleInletTwoCompartmentGadoxetateAnd3DSPGRMode'
        t = xData2DArray[:,0]
        signalAIF = xData2DArray[:,1]
    
        # SPGR model parameters
        TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
        dt = 16 #temporal resolution in sec
        t0 = 5*dt # Duration of baseline scans
        FA = 15 #degrees
        r1 = 5.9 # Hz/mM
        R10a = 1/1.500 # Hz
        R10t = 1/0.800 # Hz
    
        # Precontrast signal
        Sa_baseline = np.mean(signalAIF[0:int(t0/t[1])-1])
    
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, signalAIF[p])) for p in np.arange(0,len(t)))]
        R1a = np.squeeze(R1a)
        
        concAIF = (R1a - R10a)/r1
    
        c_if = concAIF
      
        Th = (1-Ve)/Kbh
    
        ce = c_if
        ct = Ve*ce + Khe*Th*tools.expconv(Th, t, ce, funcName)
    
        # Convert to signal
        St_rel = spgr3d_func_inv(r1, FA, TR, R10t, ct)
    
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

####################################################################
####  Concentration Models 
####################################################################
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
        ce = (1/(2*Ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1, times, combinedConcentration, funcName + '- 1') + \
                        (1-beta/alpha)*Tc2*tools.expconv(Tc2, times, combinedConcentration, funcName + '- 2')) 
   
        modelConcs = Ve*ce + Khe*Th*tools.expconv(Th, times, ce, funcName + '- 3')
    
        return(modelConcs)

    # Exception handling and logging code.
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)
 

def HighFlowDualInletTwoCompartmentGadoxetateModel(xData2DArray, Fa: float, Ve: float, Kbh: float, Khe: float):
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
        Khe*Th*tools.expconv(Th, times, combinedConcentration, 'HighFlowDualInletTwoCompartmentGadoxetateModel'))
        
        return(modelConcs)

    # Exception handling and logging code. 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

def HighFlowSingleInletTwoCompartmentGadoxetateModel(xData2DArray, Ve: float, Kbh: float, Khe: float):
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
        modelConcs = (Ve*AIFconcentrations + Khe*Th*tools.expconv(Th, times, AIFconcentrations, 'HighFlowSingleInletTwoCompartmentGadoxetateModel'))
    
        return(modelConcs)

    # Exception handling and logging code. 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)

##############################################################
### Model Function Template
##############################################################
def modelFunctionName(xData2DArray, param1, param2, param3, param4, param5):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        #model logic goes here
    
        #return(Concentration Array) 

    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)