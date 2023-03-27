import numpy as np
import pandas as pd
import netCDF4
from netCDF4 import Dataset 
import datetime
import glob
import os
import random


MLT_min = 0 
''' The lower limit of the Region Of Interest regarding the Magnetic Local Time (hours). '''
MLT_max = 24
''' The upper limit of the Region Of Interest regarding the Magnetic Local Time (hours). '''
MLT_duration_of_a_bucket = 1
''' The Region Of Interest will be split into sub-bins of this size regarding the Magnetic Local Time (hours). '''

LAT_min = -90
''' The lower limit of the Region Of Interest regarding the Geographic Latitude (degrees). '''
LAT_max = +90
''' The upper limit of the Region Of Interest regarding the Geographic Latitude (degrees). '''
LAT_degrees_of_a_bucket = 2.5
''' The Region Of Interest will be split into sub-bins of this size regarding the Geographic Latitude (degrees). '''

ALT_min = 100
''' The lower limit of the Region Of Interest regarding the Altitude (km). '''
ALT_max = 500
''' The upper limit of the Region Of Interest regarding the Altitude (km). '''
ALT_distance_of_a_bucket   = 5
''' The Region Of Interest will be split into sub-bins of this size regarding the Altitude (km).  '''

num_of_KP_bins = 2
''' The number of sub-bins into which the Region Of Interest will be split regarding the solar acticity Kp index. 1 for Kp bin 0-9, 2 for Kp bins 0-3, 3-9 and 3 for Kp bins 0-2, 2-4, 4-9.  '''

TypeOfCalculation = ""
''' Defines the physical variable on which the calculation will be applied. Valid values are: "Ohmic" for Joule Heating (Ohmic), "JHminusWindHeat" for Ohmic minus Neutral Wind heating, "SIGMA_PED" for Pedersen Conductivity, "SIGMA_HAL" for Hall Conductivity, "EEX_si" for Electric Field East, "EEY_si" for Electric Field North, "Convection_heating" for Convection heating, "Wind_heating" for Wind heating. The respective variables inside the TIE-GCM netCDF file must be named with identical names (except of JHminusWindHeat which is compound). '''

DistributionNumOfSlots = 0
''' Each sub-bin will be separated into this number of slots in order for a histogram to be calculated. '''

ResultFilename = ""
''' The netCDF filename into which the statistical calculation results will be stored. '''

KPsequence     = [ 0, 3 ] 
''' a list which stores the bin limits regarding the solar acticity Kp index (from 0 to 9). '''
ALTsequence    = list( range( ALT_min,    ALT_max,    ALT_distance_of_a_bucket  ) )
''' a list which stores the bin limits regarding the altitude (Km). '''
LATsequence = list( np.arange( LAT_min,   LAT_max,    LAT_degrees_of_a_bucket) )
''' a list which stores the bin limits regarding the geographic latitude (degrees). '''
MLTsequence    = list( range( MLT_min,    MLT_max,    MLT_duration_of_a_bucket ) )
''' a list which stores the bin limits regarding the Magnetic Local Time (hours). '''

Progress = 0  
''' An integer from 0 to 100, which trucks the calculation progress. It can be read from the GUI to display progress to the user. '''



def setDataParams( _MLT_min, _MLT_max, _MLT_duration_of_a_bucket, _LAT_min, _LAT_max, _LAT_degrees_of_a_bucket, _ALT_min, _ALT_max, _ALT_distance_of_a_bucket, _num_of_KP_bins,_TypeOfCalculation, _DistributionNumOfSlots ):
    '''
    Initializes all Bin ranges, the variable which is going to be calculated, and the number of distribution slots.  
    The values passed as parameters are stored into global variables in order to be used by all processes at a later stage.  
    It also constructs the results filename automatically based on the parameters.  
    This function has to be called before any calculation of statistics starts.  
    Args:
        _MLT_min (float): The lower limit of the Region Of Interest regarding the Magnetic Local Time (hours).
        _MLT_max (float): The upper limit of the Region Of Interest regarding the Magnetic Local Time (hours).
        _MLT_duration_of_a_bucket (float): The Region Of Interest will be split into sub-bins of this size regarding the Magnetic Local Time (hours).
        _LAT_min (float): The lower limit of the Region Of Interest regarding the Geographic Latitude (degrees).
        _LAT_max (float): The upper limit of the Region Of Interest regarding the Geographic Latitude (degrees).
        _LAT_degrees_of_a_bucket (float): The Region Of Interest will be split into sub-bins of this size regarding the Geographic Latitude  (degrees).
        _ALT_min (float): The lower limit of the Region Of Interest regarding the Altitude (km).
        _ALT_max (float): The upper limit of the Region Of Interest regarding the Altitude (km).
        _ALT_distance_of_a_bucket (float): The Region Of Interest will be split into sub-bins of this size regarding the Altitude (km).  
        _num_of_KP_bins (int): The number of sub-bins into which the Region Of Interest will be split regarding the solar acticity Kp index. 1 for Kp bin 0-9, 2 for Kp bins 0-3, 3-9 and 3 for Kp bins 0-2, 2-4, 4-9.
        _TypeOfCalculation (string): Defines the physical variable on which the calculation will be applied. Valid values are: "Ohmic" for Joule Heating (Ohmic), "JHminusWindHeat" for Ohmic minus Neutral Wind heating, "SIGMA_PED" for Pedersen Conductivity, "SIGMA_HAL" for Hall Conductivity, "EEX_si" for Electric Field East, "EEY_si" for Electric Field North, "Convection_heating" for Convection heating, "Wind_heating" for Wind heating. The respective variables inside the TIE-GCM netCDF file must be named with identical names (except of JHminusWindHeat which is compound).
        _DistributionNumOfSlots (int): Each sub-bin will be separated into this number of slots in order for a histogram to be calculated. 
    '''    
    global MLT_min, MLT_max, MLT_duration_of_a_bucket, ALT_min, ALT_max, ALT_distance_of_a_bucket, LAT_min, LAT_max, LAT_degrees_of_a_bucket, num_of_KP_bins,  TypeOfCalculation, DistributionNumOfSlots, KPsequence, ALTsequence, LATsequence, MLTsequence, ResultFilename
    ####
    MLT_duration_of_a_bucket   = _MLT_duration_of_a_bucket
    LAT_degrees_of_a_bucket    = _LAT_degrees_of_a_bucket
    ALT_distance_of_a_bucket   = _ALT_distance_of_a_bucket
    MLT_min = _MLT_min
    MLT_max = _MLT_max
    LAT_min = _LAT_min
    LAT_max = _LAT_max
    ALT_min = _ALT_min
    ALT_max = _ALT_max
    num_of_KP_bins = _num_of_KP_bins
    MLTsequence    = list( np.arange( MLT_min,    MLT_max,    MLT_duration_of_a_bucket ) )
    LATsequence    = list( np.arange( LAT_min, LAT_max, LAT_degrees_of_a_bucket) )
    ALTsequence    = list( np.arange( ALT_min,    ALT_max,    ALT_distance_of_a_bucket  ) )
    if num_of_KP_bins == 1:
        KPsequence     = [ 0 ] 
    elif num_of_KP_bins == 2:
        KPsequence     = [ 0, 3 ] 
    elif num_of_KP_bins == 3:    
        KPsequence     = [ 0, 2, 4 ] 
    #
    TypeOfCalculation = _TypeOfCalculation
    DistributionNumOfSlots = _DistributionNumOfSlots
    # construct the results filename and check if exists so that you do not overwrite it
    ResultFilename = "results/" + TypeOfCalculation + "__"
    ResultFilename += "MLT" + "_" + str(MLT_min) + "_" + str(MLT_max) + "_" + str(MLT_duration_of_a_bucket) + "_"
    ResultFilename += "LAT" + "_" + str(LAT_min) + "_" + str(LAT_max) + "_" + str(LAT_degrees_of_a_bucket) + "_"
    ResultFilename += "ALT" + "_" + str(ALT_min) + "_" + str(ALT_max) + "_" + str(ALT_distance_of_a_bucket) + "_"
    ResultFilename += "Kp" + str(num_of_KP_bins) + "Bins"
    ResultFilename += ".nc"
    ResultFilename = ResultFilename.replace(".0", "")
    
    
                    
def init_ResultDataStructure():
    '''
    Returns:
        A data structure (python dictionary) which will contain the results of the statistical calculation.  
        It contains for each bin the summary of values inside the bin, their number, their percentiles and more.  
        Inside this data structure the calculation results are stored or loaded from a file.  
        The bins must have been defined earlier from setDataParams() function.
    '''
    Buckets = dict()
    for aKP in KPsequence:
        for anALT in ALTsequence:
            for aLat in LATsequence:
                for aMLT in MLTsequence:
                    Buckets[(aKP, anALT, aLat, aMLT, "Sum")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Len")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Vals")] = list()
                    Buckets[(aKP, anALT, aLat, aMLT, "Weights")] = list() # each weight is associated with each value
                    Buckets[(aKP, anALT, aLat, aMLT, "Percentile10")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Percentile25")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Percentile50")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Percentile75")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Percentile90")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Variance")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Minimum")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Maximum")] = 0
                    Buckets[(aKP, anALT, aLat, aMLT, "Distribution")] = [0] * DistributionNumOfSlots
                    
    return Buckets




def LocatePositionInBuckets( aKp, anALT, aLat, aMLT ):
    '''
    It decides into which bin the position given in the parameters should be placed.  
    In case the position falls outside of all bins then some of the returned values will be null.  
    The bins must have been defined earlier from setDataParams() function.
    Args:
        aKp (float):  The position's solar acticity Kp index. 
        anALT (float): The position's Altitude (km).
        aLat (float): The position's Geographic Latitude (degrees).
        aMLT (float): The position's Magnetic Local Time (hours).
    Returns: 4 values (kp_to_fall, alt_to_fall, lat_to_fall, mlt_to_fall), representing the lower limit of the bin inside which the position given in the parameters falls. If some value is null then the position falls outside all predefined bins.
    '''
    kp_to_fall = alt_to_fall = lat_to_fall = mlt_to_fall = None
    # find correct Alt
    for tmp in ALTsequence:
        if anALT>=tmp and anALT<tmp+ALT_distance_of_a_bucket:
            alt_to_fall=tmp
            break
    if alt_to_fall is None and anALT==ALTsequence[-1]+ALT_distance_of_a_bucket: alt_to_fall=ALTsequence[-1]
    # find correct kp
    if num_of_KP_bins == 1:
        kp_to_fall = 0
    elif num_of_KP_bins == 2:
        if aKp < 3: 
            kp_to_fall = 0
        else:
            kp_to_fall = 3
    elif num_of_KP_bins == 3:
        if aKp < 2: 
            kp_to_fall = 0
        elif aKp < 4: 
            kp_to_fall = 2
        else:
            kp_to_fall = 4
    # find correct MLT
    if MLTsequence[-1] < 24:
        for tmp in MLTsequence:
            if aMLT>=tmp and aMLT<tmp+MLT_duration_of_a_bucket: 
                mlt_to_fall=tmp
                break
        if mlt_to_fall is None and aMLT==MLTsequence[-1]+MLT_duration_of_a_bucket: mlt_to_fall=MLTsequence[-1] # for last position
    else:
        MLT_to_check = aMLT
        if MLT_to_check < MLTsequence[0]: MLT_to_check+=24
        for tmp in MLTsequence:
            if MLT_to_check>=tmp and MLT_to_check<tmp+MLT_duration_of_a_bucket: 
                mlt_to_fall=tmp
                break
        if mlt_to_fall is None and MLT_to_check==MLTsequence[-1]+MLT_duration_of_a_bucket: mlt_to_fall=MLTsequence[-1] # for last position
    # find correct Lat
    for tmp in LATsequence:
        if aLat>=tmp and aLat<tmp+LAT_degrees_of_a_bucket:
            lat_to_fall=tmp
            break
    if lat_to_fall is None and aLat==LATsequence[-1]+LAT_degrees_of_a_bucket: lat_to_fall=LATsequence[-1]
    #
    return  kp_to_fall, alt_to_fall, lat_to_fall, mlt_to_fall




def WriteResultsToCDF(ResultBuckets, ResultFilename, VariableName, Units):
    '''
    Args:
        ResultBuckets (dictionary): The data structure which contains the statistical calculation results. See the function init_ResultDataStructure() for details.
        ResultFilename (string): The netCDF filename into which the statistical calculation results will be stored.
        VariableName (string): The physical variable on which the calculation has been applied. It will be stored as property of the netCDF file.
        Units (string): The units of the physical variable on which the calculation has been applied. It will be stored as property of the netCDF file.
    '''
    resultsCDF = Dataset( ResultFilename, 'w' )
    # add attributes defining the results file - TODO: add more attributes
    resultsCDF.DateOfCreation = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    resultsCDF.VariableName = VariableName
    resultsCDF.Units = Units
    resultsCDF.TypeOfCalculation = TypeOfCalculation
    # Create dimensions
    resultsCDF.createDimension( "dim_MLT", len(MLTsequence) )
    resultsCDF.createDimension( "dim_LAT", len(LATsequence) )
    resultsCDF.createDimension( "dim_KP", len(KPsequence) )
    resultsCDF.createDimension( "dim_ALT", len(ALTsequence) )
    resultsCDF.createDimension( "dim_distribution", DistributionNumOfSlots )
    # Create variables
    VAR_MLT = resultsCDF.createVariable( "MLT", "f4", "dim_MLT" )
    VAR_MLT[:] = MLTsequence
    VAR_LAT = resultsCDF.createVariable( "LAT", "f4", "dim_LAT" )
    VAR_LAT[:] = LATsequence
    VAR_KP = resultsCDF.createVariable( "KP", "f4", "dim_KP" )
    VAR_KP[:] = KPsequence
    VAR_ALT = resultsCDF.createVariable( "ALT", "f4", "dim_ALT" )
    VAR_ALT[:] = ALTsequence
    #
    VAR_BinSums = resultsCDF.createVariable( "BinSums", "f4", ('dim_KP', 'dim_ALT', 'dim_LAT', 'dim_MLT') )
    VAR_BinLens = resultsCDF.createVariable( "BinLens", "f4", ('dim_KP', 'dim_ALT', 'dim_LAT', 'dim_MLT') )
    VAR_Percentile10=resultsCDF.createVariable( "Percentile10", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Percentile25=resultsCDF.createVariable( "Percentile25", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Percentile50=resultsCDF.createVariable( "Percentile50", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Percentile75=resultsCDF.createVariable( "Percentile75", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Percentile90=resultsCDF.createVariable( "Percentile90", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Variance=resultsCDF.createVariable( "Variance", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Minimum=resultsCDF.createVariable( "Minimum", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    VAR_Maximum=resultsCDF.createVariable( "Maximum", "f4", ('dim_KP','dim_ALT','dim_LAT','dim_MLT'))
    if DistributionNumOfSlots > 0:
        VAR_Distribution=resultsCDF.createVariable( "Distribution", "i4",('dim_KP','dim_ALT','dim_LAT','dim_MLT','dim_distribution'))
    for aKP in KPsequence:
        for anALT in ALTsequence:
            for aLat in LATsequence:
                for aMLT in MLTsequence:
                    vector = (KPsequence.index(aKP), ALTsequence.index(anALT), LATsequence.index(aLat), MLTsequence.index(aMLT))
                    VAR_BinSums[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Sum")]
                    VAR_BinLens[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Len")]
                    VAR_Percentile10[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile10")]
                    VAR_Percentile25[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile25")]
                    VAR_Percentile50[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile50")]
                    VAR_Percentile75[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile75")]
                    VAR_Percentile90[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile90")]
                    VAR_Variance[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Variance")]
                    VAR_Minimum[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Minimum")]
                    VAR_Maximum[vector] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Maximum")]
                    if DistributionNumOfSlots > 0:
                        for i in range(0, DistributionNumOfSlots):
                            VAR_Distribution[vector+(i,)] = ResultBuckets[(aKP, anALT, aLat, aMLT, "Distribution")][i]
                    
    resultsCDF.close()
    
    

    
def LoadResultsCDF( _ResultFilename ):
    '''
    Args:
        _ResultFilename (string): The netCDF filename from which the statistical calculation results will be loaded.
    Returns:
        ResultBuckets (dictionary): the data structure which contains all the calcultion result data. See the function  init_ResultDataStructure() for details.  
        BinSums (4D list): The summary of values of each bin.  
        BinLens (4D list): The number of values of each bin.  
        VariableName (string): The physical variable on which the calculation has been applied.  
        Units (string): The units of the physical variable on which the calculation has been applied.
    '''
    global MLT_min, MLT_max, MLT_duration_of_a_bucket
    global ALT_min, ALT_max, ALT_distance_of_a_bucket 
    global LAT_min, LAT_max, LAT_degrees_of_a_bucket
    global num_of_KP_bins, ResultFilename, TypeOfCalculation
    global KPsequence, ALTsequence, LATsequence, MLTsequence
    
    ResultFilename = _ResultFilename
    
    # open result file
    try:
        CDFroot = Dataset( ResultFilename, 'r' )
    except:
        print ( " !!!!!!!! WRONG FORMAT:", ResultFilename )

    # read atributes
    DateOfCreation = CDFroot.DateOfCreation
    VariableName = CDFroot.VariableName
    Units = CDFroot.Units
    TypeOfCalculation = CDFroot.TypeOfCalculation
    
    # read results
    MLTs    = CDFroot.variables['MLT'][:]         
    LATs    = CDFroot.variables['LAT'][:] 
    ALTs    = CDFroot.variables['ALT'][:]
    KPs     = CDFroot.variables['KP'][:]        
    BinSums = CDFroot.variables['BinSums'][:, :, :, :] 
    BinLens = CDFroot.variables['BinLens'][:, :, :, :]
    P10 = CDFroot.variables['Percentile10'][:, :, :, :]
    P25 = CDFroot.variables['Percentile25'][:, :, :, :]
    P50 = CDFroot.variables['Percentile50'][:, :, :, :]
    P75 = CDFroot.variables['Percentile75'][:, :, :, :]
    P90 = CDFroot.variables['Percentile90'][:, :, :, :]
    try:
        Variances = CDFroot.variables['Variance'][:, :, :, :]
        Minimums = CDFroot.variables['Minimum'][:, :, :, :]
        Maximums = CDFroot.variables['Maximum'][:, :, :, :]
        Distribution = CDFroot.variables['Distribution'][:, :, :, :, :]    
    except:
        pass
    
    # apply loaded info to data structures
    MLT_duration_of_a_bucket = MLTs[1] - MLTs[0]
    MLT_min = MLTs[0]
    MLT_max = MLTs[-1] + MLT_duration_of_a_bucket
    #
    if len(LATs)==1:
        LAT_degrees_of_a_bucket = 180
    else:
        LAT_degrees_of_a_bucket = LATs[1] - LATs[0]
    LAT_min = LATs[0]
    LAT_max = LATs[-1] + LAT_degrees_of_a_bucket
    #
    if len(ALTs)==1:
        ALT_distance_of_a_bucket = 5
    else:
        ALT_distance_of_a_bucket = ALTs[1] - ALTs[0]
    ALT_min = ALTs[0]
    ALT_max = ALTs[-1] + ALT_distance_of_a_bucket
    #
    num_of_KP_bins = len(KPs)

    # reconstruct sequences
    MLTsequence  = list( np.arange( MLT_min,  MLT_max,  MLT_duration_of_a_bucket ) )
    LATsequence = list( np.arange( LAT_min, LAT_max, LAT_degrees_of_a_bucket) )
    ALTsequence  = list( np.arange( ALT_min,  ALT_max,  ALT_distance_of_a_bucket  ) )
    
    if num_of_KP_bins == 1:
        KPsequence     = [ 0 ] 
    elif num_of_KP_bins == 2:
        KPsequence     = [ 0, 3 ] 
    elif num_of_KP_bins == 3:    
        KPsequence     = [ 0, 2, 4 ] 
        
    # assign data to the buckets
    ResultBuckets = init_ResultDataStructure()
    for idx_kp in range(0, len(BinSums)):
        for idx_alt in range(0, len(BinSums[0])):
            for idx_mlat in range(0, len(BinSums[0,0])):
                for idx_mlt in range(0, len(BinSums[0,0,0])):
                    aKP     = KPs[idx_kp]
                    anALT   = ALTs[idx_alt]
                    aLat = LATs[idx_mlat]
                    aMLT    = MLTs[idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Sum")] = BinSums[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Len")] = BinLens[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile10")] = P10[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile25")] = P25[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile50")] = P50[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile75")] = P75[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    ResultBuckets[(aKP, anALT, aLat, aMLT, "Percentile90")] = P90[idx_kp, idx_alt, idx_mlat, idx_mlt]
                    try:
                        ResultBuckets[(aKP, anALT, aLat, aMLT, "Variance")] = Variances[idx_kp, idx_alt, idx_mlat, idx_mlt]
                        ResultBuckets[(aKP, anALT, aLat, aMLT, "Minimum")] = Minimums[idx_kp, idx_alt, idx_mlat, idx_mlt]
                        ResultBuckets[(aKP, anALT, aLat, aMLT, "Maximum")] = Maximums[idx_kp, idx_alt, idx_mlat, idx_mlt]
                        
                        # for distribution
                        ResultBuckets[(aKP, anALT, aLat, aMLT, "Distribution")] = [0] * len(Distribution[0,0,0,0,:])
                        for i in range(0, len(Distribution[0,0,0,0,:])):
                            ResultBuckets[(aKP, anALT, aLat, aMLT, "Distribution")][i] = Distribution[idx_kp, idx_alt, idx_mlat, idx_mlt, i]
                    except:
                        pass
                    
    # be verbose
    print( "Opened ", ResultFilename, ":"  )
    print("   DateOfCreation:", DateOfCreation, " TypeOfCalculation:", TypeOfCalculation )
    print("   Variable:", VariableName, " Units:", Units, " filled bins:", np.count_nonzero(BinSums), "/", len(BinSums)*len(BinSums[0])*len(BinSums[0][0])*len(BinSums[0][0][0]), " Num of Kp bins:", num_of_KP_bins)
    print("   MLT:", MLT_min, "-", MLT_max, "step", MLT_duration_of_a_bucket, "  Alt.:", ALT_min, "-", ALT_max, "step", ALT_distance_of_a_bucket, "  Mag.Lat.:", LAT_min, "-", LAT_max, "step", LAT_degrees_of_a_bucket)
    print("\n")
    
    # clean up
    CDFroot.close()
    return ResultBuckets, BinSums, BinLens, VariableName, Units
    

    

def mergeResultCDFs( CDF_filenames, mergedFilename ):
    '''
    Merges several netCDF result files into a single one.
    Args:
        CDF_filenames (string): string with wildcards, describing the files to be merged
        mergedFilename (string): string with the filename of the final merged file
    '''
    AllCDFfilenames = sorted( glob.glob( CDF_filenames ) )
    MergedBuckets = init_ResultDataStructure()
    for CDF_filename in AllCDFfilenames:
        # read a file
        ResultBuckets, BinSums, BinLens, VariableName, Units = LoadResultsCDF( CDF_filename )
        # merge it 
        for aKP in KPsequence:
            for anALT in ALTsequence:
                for aLat in LATsequence:
                    for aMLT in MLTsequence:
                        MergedBuckets[(aKP, anALT, aLat, aMLT, "Sum")] += ResultBuckets[(aKP, anALT, aLat, aMLT, "Sum")]
                        MergedBuckets[(aKP, anALT, aLat, aMLT, "Len")] += ResultBuckets[(aKP, anALT, aLat, aMLT, "Len")]
        # delete file
        os.remove( CDF_filename )
    # save merged data
    WriteResultsToCDF(MergedBuckets, mergedFilename, VariableName, Units)
        
        
