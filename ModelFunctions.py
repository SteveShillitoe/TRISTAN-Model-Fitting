"""This class module contains functions that calculate the variation 
of concentration with time according to a tracer kinetic model.
"""
import Tools as tools
import numpy as np
import logging

#Create logger
logger = logging.getLogger(__name__)

#Note: The input paramaters for the volume fractions and rate constants in
# the following model function definitions are listed in the same order as they are 
# displayed in the GUI from top (first) to bottom (last) 

class Models:
    @staticmethod
    def DualInputTwoCompartmentFiltrationModel(xData2DArray, Fa: float, 
                                               Ve: float, Fp: float, Kbh: float, Khe: float):
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
            logger.info('In function Models.DualInputTwoCompartmentFiltrationModel ' +
              'with Fa={}, Ve={}, Fp={}, Khe={} & Kbh={}'.format(Fa, Ve, Fp, Khe, Kbh))
            #In order to use scipy.optimize.curve_fit, time and concentration must be
            #combined into one function input parameter, a 2D array, then separated into individual
            #1 D arrays 
            times = xData2DArray[:,0]
            AIFconcentrations = xData2DArray[:,1]
            VIFconcentrations = xData2DArray[:,2]
    
            #Calculate Venous Flow Factor, fVFF
            fVFF = 1 - Fa

            #Determine an overall concentration
            combinedConcentration = Fp*(Fa*AIFconcentrations + fVFF*VIFconcentrations)
      
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
                print('Error - ModelFunctionsHelper.DualInputTwoCompartmentFiltrationModel: ' + str(e))
                logger.error('ModelFunctionsHelper.DualInputTwoCompartmentFiltrationModel:' + str(e) )
 

    def HighFlowDualInletTwoCompartmentGadoxetateModel(self, xData2DArray, Fa: float, 
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
            logger.info('In function ModelFunctionsHelper.HighFlowDualInletTwoCompartmentGadoxetateModel ' +
              'with Fa={}, Ve={}, Khe={} & Kbh={}'.format(Fa, Ve, Khe, Kbh))
            #print('In function ModelFunctionsHelper.HighFlowDualInletTwoCompartmentGadoxetateModel ' +
            #  'with Fa={}, Ve={}, Khe={} & Kbh={}'.format(Fa, Ve,  Khe, Kbh))
            #In order to use scipy.optimize.curve_fit, time and concentration must be
            #combined into one function input parameter, a 2D array, then separated into individual
            #1 D arrays 
            times = xData2DArray[:,0]
            AIFconcentrations = xData2DArray[:,1]
            VIFconcentrations = xData2DArray[:,2]

            #Calculate Venous Flow Factor, fVFF
            fVFF = 1 - Fa

            Th = (1-Ve)/Kbh
    
            #Determine an overall concentration
            combinedConcentration = Fa*AIFconcentrations + fVFF*VIFconcentrations 
    
            modelConcs = []
            modelConcs = (Ve*combinedConcentration + 
          Khe*Th*tools.expconv(Th,times,combinedConcentration,'HighFlowDualInletTwoCompartmentGadoxetateModel'))
        
            return(modelConcs)
        except Exception as e:
                print('Error - ModelFunctionsHelper.HighFlowDualInletTwoCompartmentGadoxetateModel: ' + str(e))
                logger.error('ModelFunctionsHelper.HighFlowDualInletTwoCompartmentGadoxetateModel:' + str(e) )
 

    def HighFlowSingleInletTwoCompartmentGadoxetateModel(self, xData2DArray, Ve: float, 
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
            logger.info('In function ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModel ' +
              'with Ve={}, Khe={} & Kbh={}'.format( Ve, Khe, Kbh))
            #print('In function ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModel ' +
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
                print('Error - ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModel: ' + str(e))
                logger.error('ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModel:' + str(e) )


    def HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe(self, 
              xData2DArray, Khe: float, Kbh: float):
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
            logger.info('In function ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe ' +
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
                print('Error - ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe: ' + str(e))
                logger.error('ModelFunctionsHelper.HighFlowSingleInletTwoCompartmentGadoxetateModelFixedVe:' + str(e) )





