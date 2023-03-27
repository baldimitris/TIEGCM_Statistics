import Data as D

import numpy as np
import os
import math
import plotly
import chart_studio.plotly as py 
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

def plotAltProfiles( VariableName, Buckets, SuperTitle="", ResultsFilename="" ):
    '''
    Creates a plot of altitude profiles of various percentiles for the variable in the parameters.  
    One sub-figure for each Magnetic Local Time - Kp index combination is created.
    Args:
        VariableName (string): The physical variable on which the calculation has been applied. 
        Buckets (dictionary): The data structure which contains the statistical calculation results. See the function Data.init_ResultDataStructure() for details.
        SuperTitle (string): This title will be displayed at the top of the plot.
        ResultsFilename (string): The netCDF filename into which the statistical calculation results will be stored.
    '''
    
    if VariableName == "Joule Heating" or "JH" in VariableName:
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
    
    # plot
    Color10 = '#c4dfe6'
    Color25 = '#a1d6e2'
    Color50 = '#1995ad'
    Color75 = '#a1d6e2'
    Color90 = '#c4dfe6'
    
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
    elif VariableName == "Pedersen conductivity": 
        XXtitle = 'Pedersen conductivity (mS/m)'
    else:
        XXtitle = VariableName
    fig = make_subplots(rows=len(D.KPsequence), cols=len(D.MLTsequence), x_title=XXtitle, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.035, horizontal_spacing=0.02, subplot_titles=ColumnTitles, specs=mySpecs)
    
    # set font sizes
    fig.update_layout( font=dict( family="arial black", size=22 ) )
    fig.update_annotations( font=dict( family="arial black", size=24 ) )
    #fig.update_xaxes(title_font_family="Arial black", title_font_size=20)
    #fig.update_yaxes(title_font_family="Arial black", title_font_size=20)
    fig.update_xaxes(tickfont_size=22)
    fig.update_yaxes(tickfont_size=22)
    fig.layout.annotations[4]["font"] = {'size': 30}  # this is the XXtitle at the bottom

    figure_hits=0
    
    for aKP in D.KPsequence:
        for aMLT in D.MLTsequence:
            #Means = list()
            Percentiles10 = list()
            Percentiles25 = list()
            Percentiles50 = list()            
            Percentiles75 = list()
            Percentiles90 = list()
            hits  = 0
            
            # compute maximums of median
            PanelMax = 0
            Alt_of_Max = 0
            for anALT in D.ALTsequence:
                if PanelMax < Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor:
                    PanelMax = Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor
                    Alt_of_Max = anALT
            #print( "MAXIMUM at", aKP, aMLT, ":", PanelMax, "at", Alt_of_Max, "km" )
            #fig.add_annotation(xref='x domain', yref='y domain', x=0.97, y=0.90, text=F"max at <b>{int(Alt_of_Max)}-{int(Alt_of_Max+D.ALT_distance_of_a_bucket)}km</b>", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color="red") )
                        
            # compute percentiles
            for anALT in D.ALTsequence:
                Percentiles10.append( Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile10"] * MultiplicationFactor )
                Percentiles25.append( Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile25"] * MultiplicationFactor )
                Percentiles50.append( Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile50"] * MultiplicationFactor )
                Percentiles75.append( Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile75"] * MultiplicationFactor )
                Percentiles90.append( Buckets[aKP, anALT, D.LAT_min, aMLT, "Percentile90"] * MultiplicationFactor )
            
            fig.add_trace( go.Scatter(x=[0]*len(visibleALTsequence), y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color10, line=dict(color='gray',width=1,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
            fig.add_trace( go.Scatter(x=Percentiles10, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color10, line=dict(color='gray',width=1,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
            fig.add_trace( go.Scatter(x=Percentiles25, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color25, line=dict(color='gray',width=1,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
            fig.add_trace( go.Scatter(x=Percentiles50, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color50, line=dict(color='black',width=2,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
            # plot mean
            #fig.add_trace( go.Scatter(x=Means, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor='black', line=dict(color='black',width=1,), showlegend=False), row=KPsequence.index(aKP)+1, col=MLTsequence.index(aMLT)+1 )
            # plot percentiles
            fig.add_trace( go.Scatter(x=Percentiles75, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color75, line=dict(color='gray',width=1,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
            fig.add_trace( go.Scatter(x=Percentiles90, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color90, line=dict(color='gray',width=1,), showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1,  )
            # add a trace in order to display secondary y-axis at the right
            fig.add_trace( go.Scatter(x=[-1000], y=[-1000], showlegend=False), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, secondary_y=True )
            
            # ~~~~ display number of measurements for each sub-figure ~~~~
            subfigure_hits = 0
            fname = "results/" + ResultsFilename[0:-3] + "/" + str(aKP) + "_" + str(aMLT) + ".txt"
            if os.path.exists( fname ):
                f = open( fname, "r" )
                subfigure_hits = int( f.read() )
                f.close()
            figure_hits += subfigure_hits
            s = "N=" + format(subfigure_hits,'.1E')
            fig.add_annotation(xref='x domain', yref='y domain', x=0.99, y=0.00, text=s, showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color="blue") )                
            fig.layout.annotations[-1]["font"] = {'family':'arial', 'size':18}
            
            # CALCULATE the Height_integration-Vaue = area under median curve ~~~~~~~~~~~~~~~~~~~~~~~~~~
            area50 = 0
            for i in range(0, len(Percentiles50)):
                if math.isnan(Percentiles50[i]) == False: 
                    area50 += Percentiles50[i]*D.ALT_distance_of_a_bucket
            #
            if VariableName=="Joule Heating" or "JH" in VariableName:
                area50 = area50 * 0.01     # area50*1000 * math.pow(10,-8) * 1000;
                fig.add_annotation(xref='x domain', yref='y domain', x=0.99, y=1, text=F"<b>{round(area50,2)}&nbsp;mW/m<sup>2</sup></b>", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color="royalblue") )
            elif VariableName == "Pedersen Conductivity":
                fig.add_annotation(xref='x domain', yref='y domain', x=0.99, y=1, text=F"<b>{round(area50,2)}&nbsp;S</b>", showarrow=False, row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1, font=dict(color="blue") )                
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            
    # display legends
    '''
    fig.add_trace( go.Scatter(name='10th Perc.', x=Percentiles10, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color10, line=dict(color='gray',width=1,), showlegend=True), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
    fig.add_trace( go.Scatter(name='25th Perc.', x=Percentiles25, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color25, line=dict(color='gray',width=1,), showlegend=True), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
    fig.add_trace( go.Scatter(name='50th Perc.', x=Percentiles50, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color50, line=dict(color='black',width=2,), showlegend=True), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
    #fig.add_trace( go.Scatter(name='Mean value', x=Means, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor='#5cc5ef', line=dict(color='black',width=1,), showlegend=True), row=KPsequence.index(aKP)+1, col=MLTsequence.index(aMLT)+1 )            
    fig.add_trace( go.Scatter(name='75th Perc.', x=Percentiles75, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color75, line=dict(color='gray',width=1,), showlegend=True), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
    fig.add_trace( go.Scatter(name='90th Perc.', x=Percentiles90, y=visibleALTsequence, mode='lines', fill='tonexty', fillcolor=Color90, line=dict(color='gray',width=1,), showlegend=True), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1 )
    '''
    
    print( "TOTAL number of measruments for the figure N_total= ", figure_hits )

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
    fig.update_yaxes( range=[80, 150], tick0=90, dtick=20 )  
    fig.update_layout( title = 'TIE-GCM (2009-2019)', title_font_color=Color50,
                       width=400+len(D.MLTsequence)*250, height=200+200*len(D.KPsequence), showlegend=True, legend_orientation="h", legend_y=-0.04) 

    
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
