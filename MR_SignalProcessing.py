import pandas
import numpy as np
from scipy.optimize import fsolve
from joblib import Parallel, delayed


def spgr_func(x, *spgr_params):
    FA, TR, R10, S0, S = spgr_params
    E0 = np.exp(-TR*R10)
    E1 = np.exp(-TR*x)
    c = np.cos(FA*np.pi/180)
    out = S - S0*(1-E1)*(1-c*E0)/(1-E0)/(1-c*E1)
    return(out)
    
    
#Constants
# MR parameters - Bayer, Sanofi, MSD
FA = 20
TR = 5.8/1000 # in seconds     

# Relaxivity
r1 = 5.5 #mm/Hz #at 4.7T
#r1 = 5.1 #mm/Hz #at 7T

# Study population R1 to be used
## At 7T
#R10_liver = 1.042
#R10_spleen = 0.672
#R10_blood = 0.973

# At 4.7T
R10_liver = 1.275
R10_spleen = 0.779
R10_blood = 2.61

def MR_SignalProcessing(fileName):
    df = pandas.read_csv(filename)

    time = df.Time
    S_liver = df.Liver
    S_spleen = df.Spleen
    S_blood = df.Blood

    # set baseline
    baseline = 5
    S_liver_baseline = np.mean(S_liver[0:baseline])
    S_spleen_baseline = np.mean(S_spleen[0:baseline])
    S_blood_baseline = np.mean(S_blood[0:baseline])

    # Convert signal to R1 - Bayer, Sanofi, MSD
    blood_R1_initial = R10_blood*np.ones(len(time))
    blood_R1 = [Parallel(n_jobs=4)(delayed(fsolve)(spgr_func, x0=blood_R1_initial[p], args = (FA, TR, R10_blood, S_blood_baseline, S_blood[p])) for p in np.arange(0,len(time)))]
    blood_R1 = np.squeeze(np.array(blood_R1))

    spleen_R1_initial = R10_spleen*np.ones(len(time))
    spleen_R1 = [Parallel(n_jobs=4)(delayed(fsolve)(spgr_func, x0=spleen_R1_initial[p], args = (FA, TR, R10_spleen, S_spleen_baseline, S_spleen[p])) for p in np.arange(0,len(time)))]
    spleen_R1 = np.squeeze(np.array(spleen_R1))

    liver_R1_initial = R10_liver*np.ones(len(time))
    liver_R1 = [Parallel(n_jobs=4)(delayed(fsolve)(spgr_func, x0=liver_R1_initial[p], args = (FA, TR, R10_liver, S_liver_baseline, S_liver[p])) for p in np.arange(0,len(time)))]
    liver_R1 = np.squeeze(np.array(liver_R1))

    # Convert relaxation rates to concentrations 
    blood_conc = (blood_R1 - R10_blood)/r1
    spleen_conc = (spleen_R1 - R10_spleen)/r1
    liver_conc = (liver_R1 - R10_liver)/r1

    # Convert spleen concentration to extracellular concentration
    ve_spleen = 0.43
    c_es_spleen = spleen_conc/ve_spleen

    # Convert blood concentration to extracellular concentration
    Hct = 0.45
    c_es_blood = blood_conc/(1-Hct)

    # Write to csv file
    data_out = [('time',time),
            ('liver',liver_conc),
            ('spleen',spleen_conc),
            ('blood',blood_conc),
            ('spleen_ECS',c_es_spleen),
            ('blood_ECS',c_es_blood),
            ]

    df_out = pandas.DataFrame.from_dict(dict(data_out))
    #print(df_out)

    out_filename = filename.replace('.csv','_conc.csv')
    df_out.to_csv(out_filename,index=False)

