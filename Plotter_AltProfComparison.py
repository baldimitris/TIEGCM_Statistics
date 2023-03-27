import Data as D

import numpy as np
import plotly
import chart_studio.plotly as py 
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import scipy.io
import scipy
import math

def plotAltProf_MedianComparison( VariableName, Buckets, CurveColor="dodgerblue", Buckets2=None, CurveColor2="dodgerblue", SuperTitle="" ):
    '''
    Creates comparison plots of two data sets.  
    The median values of each dataset are plotted together as altitude profiles for each MLT-Kp bin.
    In case the second dataset (Buckets2) is None, then the function reads data produced by the Tromso EISCAT radar.
    Args:
        VariableName (string): The physical variable on which the calculation has been applied. 
        Buckets (dictionary): The data structure which contains the statistical calculation results of the 1st dataset. See the function Data.init_ResultDataStructure() for details.
        CurveColor (string): The 1st dataset will be plotted with this color.
        Buckets2 (dictionary): The data structure which contains the statistical calculation results of the 2nd dataset. See the function Data.init_ResultDataStructure() for details.
        CurveColor2 (string): The 2nd dataset will be plotted with this color.
        SuperTitle (string): This title will be displayed at the top of the plot.
    '''
    HEIGHT_INTEGRATED_RATIO_ALL_average = 0
    HEIGHT_INTEGRATED_RATIO_UPPER_average = 0
    HEIGHT_INTEGRATED_RATIO_LOWER_average = 0
    TIEGCMarea_Upper = 0
    TIEGCMarea_Lower = 0
    TIEGCMarea2_Upper = 0
    TIEGCMarea2_Lower = 0
    EISCATcolor = CurveColor2 
    print("------------------ TIEGCM info start ------------------\n")
    print( "ALT_distance_of_a_bucket:", D.ALT_distance_of_a_bucket )
    print( "ALTsequence:", D.ALTsequence )
    print("------------------ TIEGCM info finish ------------------\n\n")
    
    if VariableName == "Joule Heating" or "JH" in VariableName:
        if Buckets2 != None:
            x_axes_range=[0, 3]
        else:
            x_axes_range=[0, 20]
        MultiplicationFactor = 10**8 
        new_units = "10^-8 W/m3"
    elif VariableName == "Pedersen Conductivity":
        x_axes_range=[0, 0.4]
        MultiplicationFactor = 10**3 
        new_units = "mS/m"
    else:
        x_axes_range=[0, 10]
        MultiplicationFactor = 1
        new_units = "?"

    
    # alter visibleALTsequence so that the point is displayed in the middle of the sub-bin
    visibleALTsequence = D.ALTsequence.copy()
    for i in range(1, len(visibleALTsequence)-1):
        visibleALTsequence[i] += D.ALT_distance_of_a_bucket/2
    visibleALTsequence[0] = D.ALTsequence[0]
    visibleALTsequence[-1] = D.ALTsequence[-1] + D.ALT_distance_of_a_bucket
    
    # construct the column MLT titles #("0-3", "3-6", "6-9", "9-12", "12-15", "15-18", "18-21", "21-24")
    ColumnTitles = list()
    
    for i in range(0, len(D.MLTsequence)):
        MLTfrom = int(D.MLTsequence[i])
        if MLTfrom > 24: MLTfrom -=24
        MLTto = int(D.MLTsequence[i]+D.MLT_duration_of_a_bucket)
        if MLTto > 24: MLTto -=24
        ColumnTitles.append( "MLT " + str(MLTfrom) + "-"  + str(MLTto) )
    # define secondary y-axis at the right of the plot
    mySpecs = list()
    for row in range(0, len(D.KPsequence)):
        mySpecs.append( list() )
        for col in range(0, len(D.MLTsequence)):
            mySpecs[row].append( {"secondary_y": True} )

    #make plot
    if VariableName == "Joule Heating": 
        XXtitle = 'Joule heating (10<sup>-8</sup> W/m<sup>3</sup>)'
    elif VariableName == "Pedersen Conductivity":
        XXtitle = 'Pedersen conductivity (mS/m)'
    else:
        XXtitle = VariableName
    fig = make_subplots(rows=len(D.KPsequence), cols=len(D.MLTsequence), x_title=XXtitle, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.035, horizontal_spacing=0.02, subplot_titles=ColumnTitles, specs=mySpecs)
    
    fig.update_layout( font=dict( family="arial black", size=24 ) )
    fig.update_annotations( font=dict( family="arial black", size=24) )
    #fig.update_xaxes(title_font_family="Arial black", title_font_size=20)
    #fig.update_yaxes(title_font_family="Arial black", title_font_size=20)
    fig.update_xaxes(tickfont_size=22)
    fig.update_yaxes(tickfont_size=22)
    fig.layout.annotations[4]["font"] = {'size': 30}  # this is the XXtitle at the bottom
    
    for aKP in D.KPsequence:
        for aMLT in D.MLTsequence:
            #Means = list()
            TIEGCMmedian = list()
            TIEGCMmedian2 = list()
            hits  = 0

            # compute TIEGCM 2ND RESULT percentiles
            if Buckets2 != None:
                TIEGCMarea_Upper = 0
                TIEGCMarea_Lower = 0
                TIEGCMarea2_Upper = 0
                TIEGCMarea2_Lower = 0
    
                for anALT in D.ALTsequence:
                    TIEGCMmedian2.append( Buckets2[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor )
                #
                for anALT in D.ALTsequence:
                    if anALT >= 120:
                        TIEGCMarea2_Upper += Buckets2[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor * D.ALT_distance_of_a_bucket * 0.01 # area*1000 * math.pow(10,-8) * 1000;
                    else:
                        TIEGCMarea2_Lower += Buckets2[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor * D.ALT_distance_of_a_bucket * 0.01 # area*1000 * math.pow(10,-8) * 1000;
                # plot TIEGCM 2ND RESULT median
                if CurveColor==CurveColor2:
                    linetype = 'dot'
                else:
                    linetype = 'solid'
                fig.add_trace( go.Scatter(x=TIEGCMmedian2, y=visibleALTsequence, mode='lines', fill=None, fillcolor=None, line=dict(color=CurveColor,width=4,dash=linetype,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
                # CALCULATE the Height_integration-Vaue for TIEGCM 2ND RESULT= area under median curve
                TIEGCMarea2 = 0
                for i in range(0, len(TIEGCMmedian2)):
                    if math.isnan(TIEGCMmedian2[i]) == False: 
                        TIEGCMarea2 += TIEGCMmedian2[i]*D.ALT_distance_of_a_bucket * 0.01 # area*1000 * math.pow(10,-8) * 1000;

            # compute TIEGCM percentiles
            for anALT in D.ALTsequence:
                TIEGCMmedian.append( Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor )
            #
            for anALT in D.ALTsequence:
                if anALT >= 120:
                    TIEGCMarea_Upper += Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor * D.ALT_distance_of_a_bucket * 0.01 # area*1000 * math.pow(10,-8) * 1000;
                else:
                    TIEGCMarea_Lower += Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor * D.ALT_distance_of_a_bucket * 0.01 # area*1000 * math.pow(10,-8) * 1000;
            # plot TIEGCM median
            fig.add_trace( go.Scatter(x=TIEGCMmedian, y=visibleALTsequence, mode='lines', fill=None, fillcolor=None, line=dict(color=CurveColor,width=4,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
            
            # CALCULATE the Height_integration-Vaue for TIEGCM = area under median curve
            TIEGCMarea = 0
            for i in range(0, len(TIEGCMmedian)):
                if math.isnan(TIEGCMmedian[i]) == False: 
                    if VariableName == "Joule Heating" or "JH" in VariableName: 
                        TIEGCMarea += TIEGCMmedian[i]*D.ALT_distance_of_a_bucket * 0.01 # area*1000 * math.pow(10,-8) * 1000;
                    elif VariableName == "Pedersen Conductivity":
                        TIEGCMarea += TIEGCMmedian[i]*D.ALT_distance_of_a_bucket # area*1000 * math.pow(10,-8) * 1000;

            # read the median curve of EISCAT
            [EISCATmedian, EISCATmedianTHIN] = getEISCAT_MedianCurve(VariableName, aKP, aMLT)
            
            # CALCULATE the Height_integration-Vaue for EISCAT = area under median curve
            EISCATarea = 0.0
            for i in range(0, len(EISCATmedian)):
                if math.isnan(EISCATmedian[i]) == False: 
                    if VariableName == "Joule Heating" or "JH" in VariableName: 
                        EISCATarea += EISCATmedian[i]*0.01  #area += EISCATmedian[i]*1000 * math.pow(10,-8) * 1000;
                    elif VariableName == "Pedersen Conductivity":
                        EISCATarea += EISCATmedian[i]

            # Calculate the Percentage Difference
            try:
                SimilarityFactor_eiscat = (TIEGCMarea-EISCATarea) / ((TIEGCMarea+EISCATarea)/2)
                SimilarityFactor_eiscat = int(round(100*SimilarityFactor_eiscat,   0)) # %
            except:
                SimilarityFactor_eiscat = 0
            if Buckets2 != None:
                try:
                    SimilarityFactor_winds =  (TIEGCMarea2-TIEGCMarea) / TIEGCMarea 
                    SimilarityFactor_winds = int(round(100*SimilarityFactor_winds, 0)) # %    
                    #print ( "HEIGHT_INTEGRATED_RATIO_ALL", aMLT, aKP, "\t", round(TIEGCMarea/TIEGCMarea2,2) )
                    #print ( "HEIGHT_INTEGRATED_RATIO_UPPER", aMLT, aKP, "\t", round(TIEGCMarea_Upper/TIEGCMarea2_Upper ,2) )
                    #print ( "HEIGHT_INTEGRATED_RATIO_LOWER", aMLT, aKP, "\t", round(TIEGCMarea_Lower/TIEGCMarea2_Lower ,2) )
                    HEIGHT_INTEGRATED_RATIO_ALL_average += TIEGCMarea/TIEGCMarea2
                    HEIGHT_INTEGRATED_RATIO_UPPER_average += TIEGCMarea_Upper/TIEGCMarea2_Upper
                    HEIGHT_INTEGRATED_RATIO_LOWER_average += TIEGCMarea_Lower/TIEGCMarea2_Lower
                except:
                    pass
                #
                
            
                
            sim_factor_color = "purple"    

            # add annotations
            if VariableName=="Joule Heating":
                if Buckets2 != None:
                    fig.add_annotation(xref='x domain', yref='y domain', x=0.99, y=1, text=F"<b>{SimilarityFactor_winds}%</b>", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color=CurveColor) )
                    #fig.add_annotation(xref='x domain',yref='y domain', x=0.5, y=1, text=F"{round(TIEGCMarea_Upper/TIEGCMarea2_Upper,2)}", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color='black') )
                    #fig.add_annotation(xref='x domain',yref='y domain', x=0.5, y=0.5, text=F"{round(TIEGCMarea/TIEGCMarea2,2)}", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color='black') )
                    #fig.add_annotation(xref='x domain',yref='y domain', x=0.5, y=0, text=F"{round(TIEGCMarea_Lower/TIEGCMarea2_Lower,2)}", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color='black') )
                
                
            # add a trace in order to display secondary y-axis at the right
            fig.add_trace( go.Scatter(x=[-1000], y=[-1000], line=dict(color=CurveColor,width=1), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, secondary_y=True )
            
            
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    print ( "HEIGHT_INTEGRATED_RATIO_ALL", "average", "\t", round(HEIGHT_INTEGRATED_RATIO_ALL_average/12 ,2) )
    print ( "HEIGHT_INTEGRATED_RATIO_UPPER", "average", "\t", round(HEIGHT_INTEGRATED_RATIO_UPPER_average/12 ,2) )
    print ( "HEIGHT_INTEGRATED_RATIO_LOWER", "average", "\t", round(HEIGHT_INTEGRATED_RATIO_LOWER_average/12 ,2) )
    
    fig.update_xaxes( range=x_axes_range, row=1, col=1)
    fig.update_xaxes( range=x_axes_range, row=1, col=2)
    fig.update_xaxes( range=x_axes_range, row=1, col=3)
    fig.update_xaxes( range=x_axes_range, row=1, col=4)
    
    fig.update_xaxes( range=x_axes_range, row=2, col=1)
    fig.update_xaxes( range=x_axes_range, row=2, col=2)
    fig.update_xaxes( range=x_axes_range, row=2, col=3)
    fig.update_xaxes( range=x_axes_range, row=2, col=4)
    
    fig.update_xaxes( range=x_axes_range, row=3, col=1)
    fig.update_xaxes( range=x_axes_range, row=3, col=2)
    fig.update_xaxes( range=x_axes_range, row=3, col=3)
    fig.update_xaxes( range=x_axes_range, row=3, col=4)
    
    for aKP in D.KPsequence:
        fig.update_yaxes( title_text="Altitude(km)", row=D.KPsequence.index(aKP)+1, col=1, side='left', secondary_y=False)
        row_title = "Kp " + str(aKP) + " - "
        if aKP == 0:
            row_title +=  "2"
        elif aKP == 2:
            row_title +=  "4"
        else:
            row_title +=  "9"
        fig.update_yaxes( title_text=row_title, row=D.KPsequence.index(aKP)+1, col=len(D.MLTsequence),  side='right', secondary_y=True, showticklabels=False )
        for aMLT in D.MLTsequence:
            fig.update_yaxes( row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, secondary_y=True, showticklabels=False )
    #fig.update_xaxes( range=x_axes_range )
    fig.update_yaxes( range=[80, 150], tick0=90, dtick=20 )  
    fig.update_layout( title = SuperTitle,
                       width=400+len(D.MLTsequence)*250, height=200+200*len(D.KPsequence), showlegend=False, legend_orientation="h", legend_y=-0.04) 

    if Buckets2 == None:
        plotEISCAT( VariableName, fig )
    
    plotly.offline.init_notebook_mode(connected=True)
    plotly.offline.iplot(fig) 

    # plot more zoom versions
    '''
    new_x_axes_range = [x * (2/3) for x in x_axes_range]
    fig.update_xaxes( range=new_x_axes_range )
    plotly.offline.iplot(fig) 
    new_x_axes_range = [x * (1/2) for x in x_axes_range]
    fig.update_xaxes( range=new_x_axes_range )
    plotly.offline.iplot(fig) 
    new_x_axes_range = [x * (3/2) for x in x_axes_range]
    fig.update_xaxes( range=new_x_axes_range )
    plotly.offline.iplot(fig) 
    new_x_axes_range = [x * (2.5) for x in x_axes_range]
    fig.update_xaxes( range=new_x_axes_range )
    plotly.offline.iplot(fig) 
    new_x_axes_range = [x * (10) for x in x_axes_range]
    fig.update_xaxes( range=new_x_axes_range )
    plotly.offline.iplot(fig) 
    '''

    
    
    

def getEISCAT_MedianCurve( VariableName, aKP, aMLT ):
    '''
    Args:
        VariableName (string): The physical variable on which the calculation has been applied. 
        aKP (float): A Kp index value (0-9)
        aMLT (float): A Magnetic Local Time value 
    Returns:
        A list of points representing an altitude profile median curve for the desired KP and MLT combination
    '''
    if aMLT > 24: aMLT -= 24
    
    Values = None
    matlabStruct = scipy.io.loadmat('./EISCAT_DATA/data_2009_2019_TS.mat')
    
    allALTs = np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][0] ).flatten()
    allKPs  = list( np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][1][0] ) )
    allMLTs = list( np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][2][0] )[:-1] )
    allJHs  = np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][3] )
    allPEDs = np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][4] )
    
    if VariableName == "Pedersen Conductivity":
        Values = allPEDs
        MultiplicationFactor = 10**3 
        new_units = "mS/m"
    else:
        Values = allJHs
        MultiplicationFactor = 10**8 
        new_units = "10^-8 W/m3"
    
    ALTsequence =  allALTs
    MLTsequence = allMLTs
    KPsequence = [ 0, 2, 4 ]
    MLT_duration_of_a_profile = 6
    
    # alter visibleALTsequence so that the point is displayed in the middle of the sub-bin
    visibleALTsequence = ALTsequence.copy()
    for i in range(1, len(visibleALTsequence)-1):
        visibleALTsequence[i] += 0.5
    
    MedianCurve = Values[KPsequence.index(aKP), MLTsequence.index(aMLT), :, 2] * MultiplicationFactor
    
    #print( "~~~~~~~~~~~~Thinning EISCAT median to compare with TIEGCM median", len(ALTsequence) )
    EISCATmedianTHIN = []
    for i in range( 0, len(MedianCurve) ):
        if ALTsequence[i] in D.ALTsequence:
            EISCATmedianTHIN.append( MedianCurve[i] )
    
    return [ MedianCurve, EISCATmedianTHIN ]

    

def plotEISCAT( VariableName, fig ):
    '''
    Adds altitude profile curves of the median value of a variable as calculated by EISCAT
    Args:
        VariableName (string): The physical variable on which the calculation has been applied. 
        fig (plotly object): the plotly figure upon which the EISCAT altitude profiles of the median value will be plotted.
    '''
    EISCATcolor = "limegreen"
    
    matlabStruct = scipy.io.loadmat('./EISCAT_DATA/data_2009_2019_TS.mat')
    
    allALTs = np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][0] ).flatten()
    allKPs  = list( np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][1][0] ) )
    allMLTs = list( np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][2][0] )[:-1] )
    allJHs  = np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][3] )
    allPEDs = np.array( matlabStruct[ 'data_2009_2019_TS' ][0][0][4] )
    
    print("------------------ EISCAT info start ------------------")
    print( "Altitudes:", allALTs[0], allALTs[1], "...", allALTs[-1] )
    print( "KPs:", allKPs  )
    print( "MLTs:", allMLTs )
    print( "JHs shape:", allJHs.shape )
    print( "PEDs shape:", allPEDs.shape )    
    print("------------------ EISCAT info finish ------------------\n\n")
    
    if VariableName == "Pedersen Conductivity":
        Values = allPEDs
        x_axes_range=[0, 0.4]
        MultiplicationFactor = 10**3 
        new_units = "mS/m"
    else:
        Values = allJHs
        x_axes_range=[0, 20]
        MultiplicationFactor = 10**8 
        new_units = "10^-8 W/m3"
    
    ALTsequence =  allALTs
    MLTsequence = allMLTs
    KPsequence = [ 0, 2, 4 ]  #list( mat_medians[ 'jouleMedians' ][0][0][3] )
    MLT_duration_of_a_profile = 6
    
    # alter visibleALTsequence so that the point is displayed in the middle of the sub-bin
    visibleALTsequence = ALTsequence.copy()
    for i in range(1, len(visibleALTsequence)-1):
        visibleALTsequence[i] += 0.5
    
    for aKP in KPsequence:
        for aMLT in MLTsequence:
            #Means = list()
            EISCATmedian = list()            
            hits  = 0
            
            # compute percentiles
            EISCATmedian = Values[KPsequence.index(aKP), MLTsequence.index(aMLT), :, 2] * MultiplicationFactor #EISCATmedian = JHmedians[1,1,:] * MultiplicationFactor 

            fig.add_trace( go.Scatter(x=EISCATmedian, y=visibleALTsequence, mode='lines', fill=None, fillcolor=EISCATcolor, line=dict(color=EISCATcolor,width=4,), showlegend=False), row=KPsequence.index(aKP)+1, col=MLTsequence.index(aMLT)+1 )
            
      