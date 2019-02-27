"""This module contains functions that coordinate the calling of functions
in the class module Models.py that calculate the variation of concentration
with time according to tracer kinetic models.  

The function ModelSelector coordinates the execution of the 
appropriate function according to the model selected on the GUI.

The function, CurveFit calls the curve_fit function imported from scipy.optimize 
to fit any of the models in this module to actual concentration/time data 
using non-linear least squares.  
"""

#from scipy.optimize import curve_fit
from lmfit import Parameters, Model
import numpy as np
import logging
import ModelFunctions as modelFunctions

#Create logger
logger = logging.getLogger(__name__)

def ModelSelector(functionName: str, inletType:str, times, 
                  AIFConcentration, 
                  parameterArray,
                  VIFConcentration=[]):
    """Function called in the GUI of the model fitting application to 
    run the function corresponding to each model and return a list of
    calculated concentrations.

    Input Parameters
    ----------------
        functionName - Name of the function corresponding to the model.

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
        Returns a list of concentrations calculated using the selected model at the times in the array time.
        """
    logger.info("In ModelFunctionsHelper.ModelSelector. Called with model {} and parameters {}".format(functionName, parameterArray))
    try:
        if inletType == 'single':
            timeInputConcs2DArray = np.column_stack((times, AIFConcentration))
        elif inletType == 'dual':
            timeInputConcs2DArray = np.column_stack((times, AIFConcentration, VIFConcentration))
       
        modelFunction=getattr(modelFunctions, functionName)
        
        return modelFunction(timeInputConcs2DArray, *parameterArray)

    except Exception as e:
        logger.error('Error in ModelFunctionsHelper.ModelSelector: ' + str(e))
        print('ModelFunctionsHelper.ModelSelector: ' + str(e))  

def CurveFit(functionName: str, paramList, times, AIFConcs, 
             VIFConcs, concROI, inletType):
    """This function calls the curve_fit function imported from scipy.optimize 
    to fit the time/conconcentration data calculated by a model in this module 
    to actual Region of Interest (ROI) concentration/time data using   
    non-linear least squares. 

    In the function calls to curve_fit, bounds are set on the input parameters to 
    avoid division by zero errors.

    Input Parameters
    ----------------
        functionName - The name of the function corresponding to the model.

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

        Returns
        ------
        optimumParams - An array of optimum values of the model input parameters
                that achieve the best curve fit.
        paramCovarianceMatrix - The estimated covariance of the values in optimumParams.
            Used to calculate 95% confidence limits.
    """
    try:
        logger.info(
            'Function ModelFunctionsHelper.CurveFit called with function name={} & parameters = {}'
            .format(functionName, paramList) )
        
        if inletType == 'dual':
            timeInputConcs2DArray = np.column_stack((times, AIFConcs, VIFConcs))
        elif inletType == 'single':
            timeInputConcs2DArray = np.column_stack((times, AIFConcs))

        modelFunction=getattr(modelFunctions, functionName)

        params = Parameters()
        params.add_many(*paramList)
        #Uncomment the statement below to check parameters 
        #loaded ok into the Parameter object
       #print(params.pretty_print())

        objModel = Model(modelFunction)
        #print(objModel.param_names, objModel.independent_vars)

        result = objModel.fit(concROI, params=params, xData2DArray=timeInputConcs2DArray)
        
        #print('best fit={}'.format(result.best_fit))
        print('best values={}'.format(result.best_values))
       
        return result.best_values
            
    except ValueError as ve:
        print ('ModelFunctionsHelper.CurveFit Value Error: ' + str(ve))
    except RuntimeError as re:
        print('ModelFunctionsHelper.CurveFit runtime error: ' + str(re))
    except Exception as e:
        print('Error in ModelFunctionsHelper.CurveFit: ' + str(e))   

#def CurveFit_SciPy(functionName: str, times, AIFConcs, VIFConcs, concROI, 
#             paramArray, inletType):
#    """This function calls the curve_fit function imported from scipy.optimize 
#    to fit the time/conconcentration data calculated by a model in this module 
#    to actual Region of Interest (ROI) concentration/time data using   
#    non-linear least squares. 
#    In the function calls to curve_fit, bounds are set on the input parameters to 
#    avoid division by zero errors.

#    Input Parameters
#    ----------------
#        functionName - The name of the function corresponding to the model.

#        time - NumPy Array of time values stored as floats. Created from a 
#            Python list.

#        AIFConcs - NumPy Array of concentration values stored as floats. 
#            Created from a Python list.  These concentrations are the Arterial
#            Input Function input to the model.

#        VIFConcs - NumPy Array of concentration values stored as floats. 
#            Created from a Python list.  These concentrations are the Venous
#            Input Function input to the model.

#        concROI - NumPy Array of concentration values stored as floats. 
#            Created from a Python list.  These concentrations belong to
#            the Region of Interest (ROI).

#        paramArray - list of model input parameter values.

#        Returns
#        ------
#        optimumParams - An array of optimum values of the model input parameters
#                that achieve the best curve fit.
#        paramCovarianceMatrix - The estimated covariance of the values in optimumParams.
#            Used to calculate 95% confidence limits.
#    """
#    try:
#        logger.info(
#            'Function ModelFunctionsHelper.CurveFit called with function name={} & parameters = {}'
#            .format(functionName, paramArray) )
        
#        if inletType == 'dual':
#            timeInputConcs2DArray = np.column_stack((times, AIFConcs, VIFConcs))
#        elif inletType == 'single':
#            timeInputConcs2DArray = np.column_stack((times, AIFConcs))

#        modelFunction=getattr(objModel, functionName)

#        return curve_fit(modelFunction, 
#                           timeInputConcs2DArray, concROI, paramArray)
        
#    #,bounds=([0.0,0.0001,0.0,0.0,0.0001], [1., 0.9999, 100.0, 100.0, 100.0])

#        #elif functionName == 'HF2-2CFM':
#        #    return curve_fit(HighFlowDualInletTwoCompartmentGadoxetateModel, 
#        #                     timeInputConcs2DArray, concROI, paramArray,
#        #                    bounds=([0.0,0.0001,0.0,0.0001], [1., 0.9999, 100.0, 100.0]))
            
#        #elif functionName == 'HF1-2CFM':
#        #    return curve_fit(HighFlowSingleInletTwoCompartmentGadoxetateModel, 
#        #                     timeInputConcs2DArray, concROI, paramArray,
#        #                     bounds=([0.0001,0.0,0.0001], [0.9999, 100.0, 100.0]))
            
#    except ValueError as ve:
#        print ('ModelFunctionsHelper.CurveFit Value Error: ' + str(ve))
#    except RuntimeError as re:
#        print('ModelFunctionsHelper.CurveFit runtime error: ' + str(re))
#    except Exception as e:
#        print('ModelFunctionsHelper.CurveFit: ' + str(e))        
##  For more information on 
#      scipy.optimize.curve_fit(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False,
#      check_finite=True, bounds=(-inf, inf), method=None, jac=None, **kwargs)[source]    
#  See
#   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
#    
    
   

    
    
