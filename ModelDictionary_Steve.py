#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 10:48:00 2019

@author: sirishatadimalla
"""

#Import libraries
import Library.Tools as tools
import numpy as np
from scipy.optimize import fsolve
from joblib import Parallel, delayed

def spgr3d_func(x, FA, TR, R10, S0, S):
    E0 = np.exp(-TR*R10)
    E1 = np.exp(-TR*x)
    c = np.cos(FA*np.pi/180)
    out = S - S0*(1-E1)*(1-c*E0)/((1-E0)*(1-c*E1))
    return(out)

def spgr3d_func_inv(r1, FA, TR, R10, c):
    s = np.sin(FA*np.pi/180)
    c = np.cos(FA*np.pi/180)
    E0 = np.exp(-TR*R10)
    E1 = np.exp(-TR*r1*c)
    Srel = s*(1-E0*E1)/(1-c*E0*E1)
    return(Srel)
    
def spgr2d_func(x, FA, TR, R10, S0, S):
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

def spgr2d_func_inv(r1, FA, TR, R10, c):
    s = np.sin(FA*np.pi/180)
    c = np.cos(FA*np.pi/180)
    E0 = np.exp(-TR*R10)
    E1 = np.exp(-TR*r1*c/2)
    
    k0 = np.sqrt(E1*E0)
    k1 = 1-k0
    k2 = 1+k0
    k3 = 1-(c**3)*E1*E1*E0*E0   
    Srel = s*k1*(1 + (c**2)*k0*k2*(1+E1*E0*c)/k3)
    return(Srel)    
    
############################### Gadoxetate models #######################################
def DualInletTwoCompartmentGadoxetateAnd3DSPGRModel(X, ve, Fp, fa, khe, kbh):
    t = X[:,0]
    Sa = X[:,1]
    Sv = X[:,2]
    fv = 1 - fa
    
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
    Sa_baseline = np.mean(Sa[0:int(t0/t[1])-1])
    Sv_baseline = np.mean(Sv[0:int(t0/t[1])-1])
    
    # Convert to concentrations
    R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
    R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, Sv[p])) for p in np.arange(0,len(t)))]
    
    ca = (R1a - R10a)/r1
    cv = (R1v - R10v)/r1
    
    c_if = Fp*(fa*ca + fv*cv)
      
    Th = (1-ve)/kbh
    Te = ve/(Fp + khe)
    
    alpha = np.sqrt( ((1/Te + 1/Th)/2)**2 - 1/(Te*Th) )
    beta = (1/Th - 1/Te)/2
    gamma = (1/Th + 1/Te)/2
    
    # conc = (ve + khe(1+kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*Fp/ve (fa ca(t)+fv cv(t))
    # Let ce(t) = exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*c_if(t) then
    # conc = (ve + khe(1+kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*ce(t)
    Tc1 = 1/(gamma-alpha)
    Tc2 = 1/(gamma+alpha)
    
    ce = (1/(2*ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1,t,c_if) + (1-beta/alpha)*Tc2*tools.expconv(Tc2,t,c_if) )
    ct = ve*ce + khe*Th*tools.expconv(Th,t,ce)
    
    # Convert to signal
    St_rel = spgr3d_func_inv(r1, FA, TR, R10t, ct)
    
    return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    
def HighFlowDualInletTwoCompartmentGadoxetateAnd3DSPGRModel(X, ve, fa, khe, kbh):
    t = X[:,0]
    Sa = X[:,1]
    Sv = X[:,2]
    fv = 1 - fa
    
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
    Sa_baseline = np.mean(Sa[0:int(t0/t[1])-1])
    Sv_baseline = np.mean(Sv[0:int(t0/t[1])-1])
    
    # Convert to concentrations
    R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
    R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, Sv[p])) for p in np.arange(0,len(t)))]
    
    ca = (R1a - R10a)/r1
    cv = (R1v - R10v)/r1
    
    c_if = fa*ca + fv*cv
      
    Th = (1-ve)/kbh
    
    ce = c_if
    ct = ve*ce + khe*Th*tools.expconv(Th,t,ce)
    
    # Convert to signal
    St_rel = spgr3d_func_inv(r1, FA, TR, R10t, ct)
    
    return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline

def HighFlowSingleInletTwoCompartmentGadoxetateAnd3DSPGRModel(X, ve, khe, kbh):
    t = X[:,0]
    Sa = X[:,1]
    
    # SPGR model parameters
    TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
    dt = 16 #temporal resolution in sec
    t0 = 5*dt # Duration of baseline scans
    FA = 15 #degrees
    r1 = 5.9 # Hz/mM
    R10a = 1/1.500 # Hz
    R10t = 1/0.800 # Hz
    
    # Precontrast signal
    Sa_baseline = np.mean(Sa[0:int(t0/t[1])-1])
    
    # Convert to concentrations
    R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr3d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
    
    ca = (R1a - R10a)/r1
    
    c_if = ca
      
    Th = (1-ve)/kbh
    
    ce = c_if
    ct = ve*ce + khe*Th*tools.expconv(Th,t,ce)
    
    # Convert to signal
    St_rel = spgr3d_func_inv(r1, FA, TR, R10t, ct)
    
    return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    
def DualInletTwoCompartmentGadoxetateAnd2DSPGRModel(X, ve, Fp, fa, khe, kbh):
    t = X[:,0]
    Sa = X[:,1]
    Sv = X[:,2]
    fv = 1 - fa
    
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
    Sa_baseline = np.mean(Sa[0:int(t0/t[1])-1])
    Sv_baseline = np.mean(Sv[0:int(t0/t[1])-1])
    
    # Convert to concentrations
    R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
    R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, Sv[p])) for p in np.arange(0,len(t)))]
    
    ca = (R1a - R10a)/r1
    cv = (R1v - R10v)/r1
    
    c_if = Fp*(fa*ca + fv*cv)
      
    Th = (1-ve)/kbh
    Te = ve/(Fp + khe)
    
    alpha = np.sqrt( ((1/Te + 1/Th)/2)**2 - 1/(Te*Th) )
    beta = (1/Th - 1/Te)/2
    gamma = (1/Th + 1/Te)/2
    
    # conc = (ve + khe(1+kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*Fp/ve (fa ca(t)+fv cv(t))
    # Let ce(t) = exp(-gamma.t)(cosh(alpha.t)+beta/gamma sinh(alpha.t))*c_if(t) then
    # conc = (ve + khe(1+kbh/(vh(1/Tb-1/Th)))exp(-t/Th)-kbhkhe/(vh(1/Tb-1/Th))exp(-t/Tb))*ce(t)
    Tc1 = 1/(gamma-alpha)
    Tc2 = 1/(gamma+alpha)
    
    ce = (1/(2*ve))*( (1+beta/alpha)*Tc1*tools.expconv(Tc1,t,c_if) + (1-beta/alpha)*Tc2*tools.expconv(Tc2,t,c_if) )
    ct = ve*ce + khe*Th*tools.expconv(Th,t,ce)
    
    # Convert to signal
    St_rel = spgr2d_func_inv(r1, FA, TR, R10t, ct)
    
    return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline
    
def HighFlowDualInletTwoCompartmentGadoxetateAnd2DSPGRModel(X, ve, fa, khe, kbh):
    t = X[:,0]
    Sa = X[:,1]
    Sv = X[:,2]
    fv = 1 - fa
    
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
    Sa_baseline = np.mean(Sa[0:int(t0/t[1])-1])
    Sv_baseline = np.mean(Sv[0:int(t0/t[1])-1])
    
    # Convert to concentrations
    R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
    R1v = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10v, Sv_baseline, Sv[p])) for p in np.arange(0,len(t)))]
    
    ca = (R1a - R10a)/r1
    cv = (R1v - R10v)/r1
    
    c_if = fa*ca + fv*cv
      
    Th = (1-ve)/kbh
    
    ce = c_if
    ct = ve*ce + khe*Th*tools.expconv(Th,t,ce)
    
    # Convert to signal
    St_rel = spgr2d_func_inv(r1, FA, TR, R10t, ct)
    
    return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline

def HighFlowSingleInletTwoCompartmentGadoxetateAnd2DSPGRModel(X, ve, khe, kbh):
    t = X[:,0]
    Sa = X[:,1]
    
    # SPGR model parameters
    TR = 3.78/1000 # Repetition time of dynamic SPGR sequence in seconds
    dt = 16 #temporal resolution in sec
    t0 = 5*dt # Duration of baseline scans
    FA = 15 #degrees
    r1 = 5.9 # Hz/mM
    R10a = 1/1.500 # Hz
    R10t = 1/0.800 # Hz
    
    # Precontrast signal
    Sa_baseline = np.mean(Sa[0:int(t0/t[1])-1])
    
    # Convert to concentrations
    R1a = [Parallel(n_jobs=4)(delayed(fsolve)(spgr2d_func, x0=0, args = (FA, TR, R10a, Sa_baseline, Sa[p])) for p in np.arange(0,len(t)))]
    
    ca = (R1a - R10a)/r1
    
    c_if = ca
      
    Th = (1-ve)/kbh
    
    ce = c_if
    ct = ve*ce + khe*Th*tools.expconv(Th,t,ce)
    
    # Convert to signal
    St_rel = spgr2d_func_inv(r1, FA, TR, R10t, ct)
    
    return(St_rel) #Returns tissue signal relative to the baseline St/St_baseline