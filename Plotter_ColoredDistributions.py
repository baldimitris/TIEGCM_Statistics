# local imports
import Data as D #from Data import *
from scicolorscales import *
import scicolorscales

# system imports
import math
import datetime
import numpy as np
import plotly
import chart_studio.plotly as py 
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots


def plotColoredDistributions( VariableName, Buckets, LogScale=True, SuperTitle="", ColorMap=lajolla ):    
    '''
    Creates color-spread plots with several sub-plots.  
    Color represents the mean value of the variable at the certain space-time area.
    Args:
       VariableName (string): The name of the variable to be plotted
       Buckets (dictionary): The data structure which contains the statistical calculation results. See the function Data.init_ResultDataStructure() for details.
       LogScale (boolean): if True then the mean values colors will be plotted in logarithmic scale
       SuperTitle (string): a title to be added at the top of the plot
       ColorMap: the name of the colormap ot use for ploting.
                 color neutral colormaps: (http://www.fabiocrameri.ch/colourmaps.php): acton, bamako, batlow, berlin, bilbao, broc, buda, cork, davos, devon, grayC, hawaii, imola, lajolla, lapaz, lisbon, nuuk, oleron , oslo, roma, tofino, tokyo, turku, vik - romaO, brocO, corkO, vikO 
                 plotly colormaps: Blackbody, Bluered, Blues, Earth, Electric, Greens, Greys, Hot, Jet, Picnic, Portland, Rainbow, RdBu, Reds, Viridis, YlGnBu, YlOrRd
    '''
    print( "Colored Distributions Plot creation started", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") )
    MultiplicationFactor = 1
        
    # construct the column MLT titles #("0-3", "3-6", "6-9", "9-12", "12-15", "15-18", "18-21", "21-24")
    ColumnTitles = list()    
    for i in range(0, len(D.MLTsequence)):
        MLTfrom = int(D.MLTsequence[i])
        if MLTfrom > 24: MLTfrom -=24
        MLTto = int(D.MLTsequence[i]+D.MLT_duration_of_a_bucket)
        if MLTto > 24: MLTto -=24
        ColumnTitles.append( "<b>MLT " + str(MLTfrom) + "-"  + str(MLTto) + "</b>" )
    # define secondary y-axis at the right of the plot
    mySpecs = list()
    for row in range(0, len(D.KPsequence)):
        mySpecs.append( list() )
        for col in range(0, len(D.MLTsequence)):
            mySpecs[row].append( {"secondary_y": True} )
            
    #make plot
    HitsStr = ""
    fig = make_subplots(rows=len(D.KPsequence), cols=len(D.MLTsequence), shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.035, horizontal_spacing=0.02, subplot_titles=ColumnTitles, specs=mySpecs)
    
    
    # bundle data, min and max values
    localHits_min = allHits_min = allHits_logscale_min = 999999
    localHits_max = allHits_max = allHits_logscale_max = -99999
    for aKP in D.KPsequence:
        for aMLT in D.MLTsequence:
            Hits = None
            for anALT in D.ALTsequence:            
            
                if Hits is None:
                    Hits = [ Buckets[(aKP, anALT, D.LAT_min, aMLT, "Distribution")] ]
                else:
                    Hits = np.append(Hits, [Buckets[(aKP, anALT, D.LAT_min, aMLT, "Distribution")]] , axis=0)
            
            localHits_min = np.min( Hits )
            localHits_max = np.max( Hits )
            if localHits_min < allHits_min:
                allHits_min = localHits_min
            if localHits_max > allHits_min:
                allHits_min = localHits_max
            
            # compute logScale
            Hits_logscale = np.zeros( Hits.shape )
            for i in range(0, len(Hits)):
                for j in range(0, len(Hits[0])):
                    if Hits[i,j] > 0:
                        Hits_logscale[i,j] = np.log10(Hits[i,j])
                    else:
                        Hits_logscale[i,j] = None
            
            localHits_logscale_min = np.nanmin( Hits_logscale )
            localHits_logscale_max = np.nanmax( Hits_logscale )            
            if localHits_logscale_min < allHits_logscale_min:
                allHits_logscale_min = localHits_logscale_min                
            if localHits_logscale_max > allHits_logscale_min:
                allHits_logscale_min = localHits_logscale_max
            
            print("Min:", localHits_min, "Max:", localHits_max, " Log Min:", localHits_logscale_min, "Log Max:", localHits_logscale_max)
            
            # plot heatmap
            if LogScale:
                fig.add_trace( go.Heatmap(z=Hits_logscale, x=np.linspace(0,10,100), y=D.ALTsequence, zsmooth=False, showlegend=False, coloraxis="coloraxis1",zmin=localHits_logscale_min, zmax=localHits_logscale_max), row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1,  )
            else:
                fig.add_trace( go.Heatmap(z=Hits, x=np.linspace(0,10,100), y=D.ALTsequence, zsmooth=False, showlegend=False, coloraxis="coloraxis1", zmin=localHits_min, zmax=localHits_max),row=D.KPsequence.index(aKP)+1, col=D.MLTsequence.index(aMLT)+1,  )

    print("allHits_logscale_min", "allHits_logscale_max", "allHits_min", "allHits_max" )
    print(allHits_logscale_min, allHits_logscale_max, allHits_min, allHits_max )
    
    fig.update_layout(coloraxis=dict(colorscale=ColorMap), showlegend=False) 
    # display titles
    fig.update_yaxes( title_text="<b>" + "Kp 0-2" + "</b>" + "<br><br>" + "Altitude (km)", row=1, col=1, side='left', secondary_y=False)
    fig.update_yaxes( title_text="<b>" + "Kp 2-4" + "</b>" + "<br><br>" + "Altitude (km)", row=2, col=1, side='left', secondary_y=False)
    fig.update_yaxes( title_text="<b>" + "Kp 4-9" + "</b>" + "<br><br>" + "Altitude (km)", row=3, col=1, side='left', secondary_y=False)
    for anAlt in D.ALTsequence: fig.update_xaxes( title_text="JH (10^-8 W/m3)", row=len(D.KPsequence), col=D.ALTsequence.index(anAlt)+1)
        
    # Set the same min/max for all figures
    if LogScale:
        fig.update_traces(zmin=allHits_min, zmax=allHits_max)
    else:
        fig.update_traces(zmin=allHits_logscale_min, zmax=allHits_logscale_max)
    # tick values at the color bar
    if LogScale:
        my_Tickvals    = np.linspace(allHits_min, allHits_max, 5, endpoint=True)
        my_logTickvals = list()
        my_Ticktexts   = list()
        for t in range( 0, len(my_Tickvals) ):
            try:
                my_logTickvals.append( math.log10(my_Tickvals[t]) )
                my_Ticktexts.append( "{:.3e}".format(my_Tickvals[t]) )                
            except Exception as e:
                #print(e)
                pass
        fig.update_layout(coloraxis_colorbar=dict( title="Log scale",  tickvals=my_logTickvals,  ticktext=my_Ticktexts, ))
    #
    #fig.update_yaxes( range=[D.MLAT_min,  D.MLAT_max], dtick=D.MLAT_degrees_of_a_bucket )
    #fig.update_xaxes( range=[D.MLT_min, D.MLT_max], dtick=D.MLT_duration_of_a_bucket )
    # font
    fig.update_layout(font_family="Helvetica",)
    # Set title
    mainTitle = SuperTitle
    mainTitle += "<br>Distribution: Color indicates how many values lie inside each bin."
    fig.update_layout( title = mainTitle, width=400+len(D.MLTsequence)*180, height=150+180*len(D.KPsequence), showlegend=True, legend_orientation="h", legend_y=-0.04) 
    plotly.offline.init_notebook_mode(connected=True)
    plotly.offline.iplot(fig)
    
    
