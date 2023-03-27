# local imports
import Data

# system imports
import netCDF4
from netCDF4 import Dataset 
import os
import datetime
import time
import glob
import shutil
import math
import numpy as np
import multiprocessing
from pathlib import Path
import random
from array import array

NUM_OF_PROCESSORS = 14
TMP_FOLDER =  "./results/tmp/"  "/media/balukid/STATStmp/"
USE_WEIGHTED_AVERAGE = False

global theResultFile_folder
global theResultFile_simplename

def StartCalculating( NetCDF_files_path, ResultFilename, TypeOfCalculation, TmpFilesPath="/media/balukid/STATStmp/" ):
    '''
    This function manages the statistical calulation:  
      - For each TIE-GCM netCDF file it spawns a process which will store its results into temporary files at its own folder. Many procecess are utilised in order to accelerate the calculation by leveraging multiple cores. 
      - After all processes finish, this function merges all temporary files, calculates percentiles etc for each bin and creates a results netCDF file.  
    This function should be called after the Data.setDataParams() function has initialized the bin ranges.
    Args:
        NetCDF_files_path (string): The path where all the TIE-GCM netCDF files are stored. In wildcard format. Example: "./data/*/*.nc".
        ResultFilename (string): The filename where the final calculation results will be stored.
        TypeOfCalculation (string): The variable which upon which the calculation will be applied. See Data.setDataParams() for more.
        TmpFilesPath (string): The path where the temporary files will be stores
    '''
    global TMP_FOLDER
    global theResultFile_folder
    global theResultFile_simplename
    theResultFile_folder   = ResultFilename[ 0 : ResultFilename.rfind('/')  ]
    theResultFile_simplename = ResultFilename[ ResultFilename.rfind('/')+1 :  ][0:-3]
    if not os.path.exists(theResultFile_folder+"/"+theResultFile_simplename): os.makedirs(theResultFile_folder+"/"+theResultFile_simplename)
    
    startSecs = time.time()
    print( "START", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") )
    TMP_FOLDER = TmpFilesPath
    
    Allprocesses = list()
    AllCDFfiles = sorted( glob.glob( NetCDF_files_path, recursive=True ) )
    print( "I will calculate '" + TypeOfCalculation + "' on", len(AllCDFfiles), "files:\n    ", NetCDF_files_path, "\n" )
    print( "Results will be stored in '" + ResultFilename + "'\n" )
    
    n = 0
    for CDF_file in AllCDFfiles:
        n += 1
        Data.Progress = int( 100 * n/221)

        # spawn new process
        P = multiprocessing.Process(target=PROC_StatsCalculator, args=(n,CDF_file,TypeOfCalculation))
        Allprocesses.append(P)
        P.start()

        pause_spawning = True
        while pause_spawning:
            Num_of_alive_processes = 0
            for P in Allprocesses:
                if P.is_alive():
                    Num_of_alive_processes += 1            
            if Num_of_alive_processes >= NUM_OF_PROCESSORS:
                pause_spawning = True
                time.sleep(12)
            else:
                pause_spawning = False


        # wait for all processes to terminate
        for T in Allprocesses: T.join()
        
    # every process creates a partial file, merge all of them into one
    print( "Merging partial data files and calculating result values...",  datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    ResultBuckets = Data.init_ResultDataStructure()
    NumOfBins = len(Data.KPsequence) * len(Data.ALTsequence) * len(Data.LATsequence) * len(Data.MLTsequence)
    CurrBinNum = 0
    
    print( "Data.KPsequence: ", Data.KPsequence)
    print( "Data.ALTsequence", Data.ALTsequence)
    print( "Data.LATsequence", Data.LATsequence)
    print( "Data.MLTsequence", Data.MLTsequence)
    
    for aKP in Data.KPsequence:
        for aMLT in Data.MLTsequence:
            RegionHits = 0
            for anALT in Data.ALTsequence:
                for aLat in Data.LATsequence:
                    CurrBinNum += 1
                    Data.Progress = int( 100 * CurrBinNum/NumOfBins )
                    AllBinValues = list()
                    All_partialData_folders = sorted( glob.glob( TMP_FOLDER+"proc*", recursive=False ) )
                    for partialDataFolder in All_partialData_folders: # read all partial files for this bin 
                        partialDataFolder = partialDataFolder + "/"
                        if os.path.isdir(partialDataFolder)==False:
                            continue
                        partialDataFilename = partialDataFolder + str(aKP)+"_"+str(anALT)+"_"+str(aLat)+"_"+str(aMLT)+".dat"
                        if os.path.exists(partialDataFilename) == False: # no hits for this bin from this process
                            continue
                            
                        f = open(partialDataFilename, "rb")
                        float_array = array('d')
                        float_array.frombytes(f.read())
                        AllBinValues += float_array.tolist()
                        f.close()
                        
                    print("BIN", "Kp"+str(aKP), "Alt"+str(anALT), "Lat"+str(aLat), "MLT"+str(aMLT), "", len(AllBinValues), "items" )
                    RegionHits += len(AllBinValues)
                        
                    if len(AllBinValues) > 0:
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Sum"] = np.sum(AllBinValues)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Len"] = len(AllBinValues)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Percentile10"] = np.percentile(AllBinValues, 10)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Percentile25"] = np.percentile(AllBinValues, 25)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Percentile50"] = np.percentile(AllBinValues, 50)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Percentile75"] = np.percentile(AllBinValues, 75)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Percentile90"] = np.percentile(AllBinValues, 90)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Variance"] = np.var(AllBinValues)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Minimum"] = np.nanmin(AllBinValues)
                        ResultBuckets[aKP, anALT, aLat, aMLT, "Maximum"] = np.nanmax(AllBinValues)
                        
                        # calculate distribution
                        if Data.DistributionNumOfSlots > 0:
                            histo_values, histo_ranges = np.histogram(AllBinValues, Data.DistributionNumOfSlots, (0, 0.0000001))
                            for i in range(0, Data.DistributionNumOfSlots):
                                ResultBuckets[aKP, anALT, aLat, aMLT, "Distribution"][i] = histo_values[i]
            print( "REGION:", "Kp"+str(aKP), "MLT"+str(aMLT), ":", RegionHits, "measurements." )
            print("BIN", "Kp"+str(aKP), "Alt"+str(anALT), "Lat"+str(aLat), "MLT"+str(aMLT), "", len(AllBinValues), "items" )
            
    if "Ohmic" in TypeOfCalculation:
        Data.WriteResultsToCDF(ResultBuckets, ResultFilename, "Joule Heating", "W/m3")
    elif "SIGMA_PED" in TypeOfCalculation:
        Data.WriteResultsToCDF(ResultBuckets, ResultFilename, "Pedersen Conductivity", "S/m")
    else:
        Data.WriteResultsToCDF(ResultBuckets, ResultFilename, TypeOfCalculation, "")
    
    # DO NOT DELL PARTIAL FILES - THEY CAN BE USED TO CONTINUE THE CALCULATION AFTER AN INTERMEDIATE HALT
    #try: # delete temporary files, which contain all values for each bin
    #    shutil.rmtree( TMP_FOLDER )
    #except:
    #    pass
    
    finishSecs = time.time()
    print( "FINISH",  datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), " (", finishSecs-startSecs, "sec )")

                  
                  
    

def PROC_StatsCalculator(ProcessNum, CDF_filename, TypeOfCalculation):
    '''
    Reads a NetCDF file and separates all the values of the variable into different files according to the bin they fall in.  
    The variable is chosen by the <TypeOfCalculation> argument.  
    The process saves several files in its own folder with the name: TMP_FOLDER+"proc"+<ProcessNum>+"/".  
    The folder contains one binary file for each bin. The file contains all values of the variable which fall inside the bin.
    The function also saves into the result files the Number Of Measurements per bin it has processed.
    Args:
        ProcessNum (int):
        CDF_filename (string):
        TypeOfCalculation (string):
    '''
    # check if the data of this process have already been calculated
    procfolder = TMP_FOLDER+"proc"+ f"{ProcessNum:03}" +"/"
    if os.path.isdir(procfolder):
        print( "Proc ", ProcessNum, "already calculated.", flush=True )
        return # <<<<
    else:
        if os.path.isdir(TMP_FOLDER)==False: os.mkdir( TMP_FOLDER )
        os.mkdir( procfolder )    
    
    # open netCDF file 
    print("Proc",ProcessNum,"reading ",CDF_filename[CDF_filename.rfind('/')+1:], datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), flush=True)
    try:
        CDFroot = Dataset( CDF_filename, 'r' )
    except:
        print ( " !!! WRONG FORMAT:", CDF_filename, flush=True )
        #os.remove("ReadingFile.flag") # lower the reading-file flag
        return
        
    # read the data from the netCDF file
    #TIMEs  = CDFroot.variables['time'][:] 
    if "Ohmic" in TypeOfCalculation or "JH" in TypeOfCalculation:        Ohmics = CDFroot.variables['Ohmic'][:, :, :, :]  # m/s
    if "SIGMA_PED" in TypeOfCalculation:   PEDs   = CDFroot.variables['SIGMA_PED'][:, :, :, :]
    if "SIGMA_HAL" in TypeOfCalculation:  HALs   = CDFroot.variables['SIGMA_HAL'][:, :, :, :]
    if "EEX_si" in TypeOfCalculation:    EEXs   = CDFroot.variables['EEX_si'][:, :, :, :]
    if "EEY_si" in TypeOfCalculation:    EEYs   = CDFroot.variables['EEY_si'][:, :, :, :]
    if "Convection_heating" in TypeOfCalculation:  ConvH  = CDFroot.variables['Convection_heating'][:, :, :, :]
    if "Wind_heating" in TypeOfCalculation:  WindH  = CDFroot.variables['Wind_heating'][:, :, :, :]
    if "JHminusWindHeat" in TypeOfCalculation:  WindH  = CDFroot.variables['Wind_heating'][:, :, :, :]        
        
    #
    LATs   = CDFroot.variables['lat'][:] 
    #MLATs   = CDFroot.variables['mlat_qdf'][:, :, :, :] 
    MLTs    = CDFroot.variables['mlt_qdf'][:, :, :, :]         
    ALTs    = CDFroot.variables['ZGMID'][:, :, :, :] / 100000 # Geometric height stored in cm, converted to km
    KPs     = CDFroot.variables['Kp'][:]
    
    hits = 0   # num of instances that fit in any of the defined bins

    ResultBuckets = Data.init_ResultDataStructure().copy()
    num_of_unbinned_items = 0
    step = 1
    for idx_time in range(0, len(ALTs), step):
        # $$$$$$$$ for each moment in time put the values in their bins and calculate the mean of each bin. 
        SingleMomentBuckets = Data.init_ResultDataStructure().copy()
        for idx_lev in range(0, len(ALTs[0]), step):
            for idx_lat in range(0, len(ALTs[0,0]), step):
                for idx_lon in range(0, len(ALTs[0,0,0]), step):
                    
                    curr_alt_km = ALTs[idx_time, idx_lev, idx_lat, idx_lon] 
                    
                    # ignore values for out-of-range positions 
                    if curr_alt_km<Data.ALT_min or curr_alt_km>Data.ALT_max:
                        continue
                        
                    curr_kp     = KPs[idx_time]
                    curr_mlt    = MLTs[idx_time, idx_lev, idx_lat, idx_lon]
                    curr_lat    = LATs[idx_lat]
                    
                    kp_to_fall,alt_to_fall,lat_to_fall,mlt_to_fall = Data.LocatePositionInBuckets(curr_kp,curr_alt_km,curr_lat,curr_mlt)
                    
                    if kp_to_fall is None or alt_to_fall is None or lat_to_fall is None or mlt_to_fall is None:
                        num_of_unbinned_items += 1
                        break # no other longitude can have a hit either
                    else:
                        if TypeOfCalculation=="JHminusWindHeat" or TypeOfCalculation=="JHminusWindHeatEISCAT":
                            aValue = Ohmics[idx_time, idx_lev, idx_lat, idx_lon] - WindH[idx_time, idx_lev, idx_lat, idx_lon]
                            if aValue > 100: continue # ignore faulty large values
                        elif TypeOfCalculation=="Ohmic":
                            aValue = Ohmics[idx_time, idx_lev, idx_lat, idx_lon]
                            if aValue > 100: continue # ignore faulty large values
                        elif "SIGMA_PED" in TypeOfCalculation:
                            aValue = PEDs[idx_time, idx_lev, idx_lat, idx_lon]
                        elif "HallCond" in TypeOfCalculation:
                            aValue = HALs[idx_time, idx_lev, idx_lat, idx_lon]
                        elif "EEX_si" in TypeOfCalculation:
                            aValue = EEXs[idx_time, idx_lev, idx_lat, idx_lon]
                        elif "EEY_si" in TypeOfCalculation:
                            aValue = EEYs[idx_time, idx_lev, idx_lat, idx_lon]
                        elif "Convection_heating" in TypeOfCalculation:
                            aValue = ConvH[idx_time, idx_lev, idx_lat, idx_lon]
                            if aValue > 100: continue # ignore faulty large values
                        elif "Wind_heating" in TypeOfCalculation:
                            aValue = WindH[idx_time, idx_lev, idx_lat, idx_lon]
                        else:
                            print("ERROR: UNRECOGNISED TypeOfCalculation '" + TypeOfCalculation + "'")
                            CDFroot.close()
                            return
                        
                        # bin this value
                        SingleMomentBuckets[ kp_to_fall, alt_to_fall, lat_to_fall, mlt_to_fall, "Vals" ].append( aValue )
                        
                        # if weights are enabled then store the value's weight as well
                        '''
                        TIEGCM latitudes are: 68.75,  71.25,  73.75,  76.25,  78.75
                        https://en.wikipedia.org/wiki/Spherical_segment
                        Area of a sphere segment = 2 * pi * R * height of the segment (the distance from one parallel plane to the other) 
                        R = 6477km
                        sin(angleFrom) = h_from / R
                        sin(angleTo)   = h_to   / R
                        '''
                        if USE_WEIGHTED_AVERAGE:
                            weight = 1
                            if curr_lat == 68.75:
                                weight = 0.0410
                            elif curr_lat == 71.25:
                                weight = 0.381
                            elif curr_lat == 73.75:
                                weight = 0.328
                            elif curr_lat == 76.25:
                                weight = 0.249
                            else:
                                print( ">>>> ", curr_lat )
                            SingleMomentBuckets[ kp_to_fall, alt_to_fall, lat_to_fall, mlt_to_fall, "Weights" ].append( weight )
                        
                        # keep tracks of the number of the total binned values 
                        hits +=1
                        
        # $$$$$$$$ the averages of each time moment are stored in their bin. The percentiles will be calculated on them at the end 
        if USE_WEIGHTED_AVERAGE: # weighted average
            for aKP in Data.KPsequence:
                for anALT in Data.ALTsequence:
                    for aLat in Data.LATsequence:
                        for aMLT in Data.MLTsequence: 
                            L = len(SingleMomentBuckets[aKP,anALT,aLat,aMLT,"Vals"])
                            if L > 0:
                                S = 0
                                sum_of_weights = 0
                                BinVals    = SingleMomentBuckets[aKP,anALT,aLat,aMLT,"Vals"]
                                BinWeights = SingleMomentBuckets[aKP,anALT,aLat,aMLT,"Weights"]
                                for i in range(0, len(SingleMomentBuckets[aKP,anALT,aLat,aMLT,"Vals"])):
                                    S +=  BinWeights[i] * BinVals[i]
                                    sum_of_weights += BinWeights[i]
                                ResultBuckets[aKP,anALT,aLat,aMLT,"Vals"].append( S / sum_of_weights )
                                
        else: # normal average
            for aKP in Data.KPsequence:
                for aMLT in Data.MLTsequence: 
                    subfigure_N = 0
                    for aLat in Data.LATsequence:
                        for anALT in Data.ALTsequence:
                            L = len(SingleMomentBuckets[aKP,anALT,aLat,aMLT,"Vals"])
                            if L > 0:
                                S = sum(SingleMomentBuckets[aKP,anALT,aLat,aMLT,"Vals"])
                                ResultBuckets[aKP,anALT,aLat,aMLT,"Vals"].append( S / L )
                                subfigure_N += L
                                
                    if subfigure_N > 0: Store_NumOfMeasurements(aKP,aMLT, subfigure_N)

    # close cdf
    CDFroot.close()
    
    # ---- save results
    # save values of each bin in a binary file
    for aKP in Data.KPsequence:
        for anALT in Data.ALTsequence:
            for aLat in Data.LATsequence:
                for aMLT in Data.MLTsequence:    
                    if len( ResultBuckets[ aKP, anALT, aLat, aMLT, "Vals" ] ) > 0:
                        fname = str(aKP) + "_" + str(anALT) + "_" + str(aLat) + "_" + str(aMLT) + ".dat"
                        f = open( procfolder + fname, "wb" )
                        float_array = array('d', ResultBuckets[aKP, anALT, aLat, aMLT, "Vals"])
                        float_array.tofile(f)
                        f.close()

    # -------- print result message
    msg = "Proc " + str(ProcessNum) + " " + CDF_filename[-20:] +  " Hits=" + str(hits)
    for aKP in Data.KPsequence:
        msg += "\n"
        for aMLT in Data.MLTsequence: 
            n = 0
            for aLat in Data.LATsequence:
                for anALT in Data.ALTsequence:
                    n += len(ResultBuckets[aKP,anALT,aLat,aMLT,"Vals"])
            msg += " " + str(n)
    msg += "    " + datetime.datetime.now().strftime("%H:%M:%S") + "\n"
    print(msg, flush=True)
    
    
    
    
def Store_NumOfMeasurements(aKP, aMLT, curr_num):
    '''
    Stores the number of measurements that fall inside each sub-region defined by its lower Kp limit and lower MLT limit. 
    There is one file per sub-region.
    This function is necessary because the data are processed by different processes.
    Args:
        aKP (float):
        aMLT (float):
        curr_num (int):
    '''
    # LOCK
    wait = True
    while( wait ):
        if os.path.exists( theResultFile_folder + "/" + theResultFile_simplename + "/" + "lock.tmp" ) == False: 
            try:
                f = open( theResultFile_folder + "/" + theResultFile_simplename + "/" + "lock.tmp", "x" )
                f.close()
                wait = False
            except:
                wait = True
        if wait: time.sleep( random.randint(0,1) )
    # WORK
    prev_num = 0
    fname = str(aKP) + "_" + str(aMLT) + ".txt"
    if os.path.exists( theResultFile_folder + "/" + theResultFile_simplename + "/" + fname ):
        f = open( theResultFile_folder + "/" + theResultFile_simplename + "/" + fname, "r" )
        prev_num = int( f.read() )
        f.close()
    f = open( theResultFile_folder + "/" + theResultFile_simplename + "/" + fname, "w" )
    f.write( str(prev_num + curr_num) )
    f.close()
    # UNLOCK
    try:
        os.remove( theResultFile_folder + "/" + theResultFile_simplename + "/" + "lock.tmp" )
    except:
        pass