
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:39:00 2019

@author: sirishatadimalla
"""

import Tools as tools
import ExceptionHandling as exceptionHandler
import numpy as np
from scipy.optimize import fsolve
from joblib import Parallel, delayed
import logging
logger = logging.getLogger(__name__)

####################### Signal models ######################################### 
def HighFlowGadoxetate3DSPGR_Rat(xData2DArray, Ve, Kbh, Khe, 
                                 constantsString):
    try:
        exceptionHandler.modelFunctionInfoLogger()
        t = xData2DArray[:,0]
        Sa = xData2DArray[:,1]

        # Unpack SPGR model constants from 
        # a string representation of a dictionary
        # of constants and their values
        constantsDict = eval(constantsString) 
        TR, baseline, FA, r1, R10a, R10t = \
        constantsDict['TR'], \
        constantsDict['baseline'],\
        constantsDict['FA'], constantsDict['r1'], \
        constantsDict['R10a'], constantsDict['R10t'] 
        
        # Precontrast signal
        Sa_baseline = np.mean(Sa[0:baseline])
        
        # Convert to concentrations
        R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
        R1a = np.squeeze(R1a)
        
        ca = (R1a - R10a)/r1
        
        # Correct for spleen Ve
        ve_spleen = 0.43
        ce = ca/ve_spleen
        
        if Kbh != 0:
            Th = (1-Ve)/Kbh
            ct = Ve*ce + Khe*Th*tools.expconv(Th,t,ce)
        else:
            ct = Ve*ce + Khe*tools.integrate(ce,t)
        
        # Convert to signal
        St_rel = tools.spgr3d_func_inv(r1, FA, TR, R10t, ct)
        
        return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
 
    except ZeroDivisionError as zde:
        exceptionHandler.handleDivByZeroException(zde)
    except Exception as e:
        exceptionHandler.handleGeneralException(e)
        

    