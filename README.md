# TIEGCM_Statistics
This repository contains the software which executed the statistical calculations for:  
<em>
&emsp;A comparative assessment of the distribution of Joule heating in altitude as estimated in TIE-GCM and EISCAT over one solar cycle.  
&emsp;Baloukidis D., Sarris T., Tourgaidis S., Pirnaris P., Aikio A., Virtanen I., Buchert S., Papadakis K.
</em>

## Contributors
The contributors for this software are: Baloukidis Dimitris, Sarris Theodoros, Tourgaidis Stelios, Pirnaris Panagiotis, from the Democritus University of Thrace, Xanthi, Greece and Papadakis Konstantinos from the University of Helsinki, Helsinki, Finland.

## Introduction
The software reads TIE-GCM result files, separates the data into bins and calculates percentiles for each bin. The bins are defined by ranges of Magnetic Local Time, solar activity Kp index, latitude and altitude. The results are stored into netCDF files and can be plotted as altitude profiles in order to be compared with similar plots based on data from the Tromsø EISCAT Incoherent Scatter Radar. 

The software is written in Python and utilizes Jupyter Notebooks.

## Data
The data for this project originate from two sources: a TIE-GCM 11 year simulation for the whole duration of the solar cycle 24 (2009-2019) and several campaigns of the Tromsø EISCAT Incoherent Scatter Radar during the same period. The TIEGCM_DATA folder contains sample data files from the TIE-GCM model and the EISCAT_DATA folder contains the altitude profiles as caluclated based on the radar data. The most important physical variables which concern this project are Joule heating with and without the contribution of neutral winds and Pedersen conductivity. 

We thank the EISCAT Scientific Association for providing the incoherent scatter radar data used in this study. EISCAT is an international association supported by research organisations in China (CRIRP), Finland (SA), Japan (NIPR and ISEE), Norway (NFR), Sweden (VR), and the United Kingdom (UKRI). The EISCAT data are available in the Madrigal database: \url{https://madrigal.eiscat.se/madrigal/}. This work was supported by the Kvantum Institute of the University of Oulu and by the Academy of Finland (347796 and 24304299). 

## Plot examples
<img src="/images/TIEGCM_JH.png" alt="TIE-GCM Joule Heating Altitude Profiles" width=30%>
![TIE-GCM Joule Heating Altitude Profiles](/images/TIEGCM_JH.png "TIE-GCM Joule Heating Altitude Profiles").
![EISCAT Joule Heating Altitude Profiles](/images/EISCAT_JH.png "EISCAT Joule Heating Altitude Profiles").
![Pedersen Conductivity Medians Comparison](/images/PED_medians.png "Pedersen Conductivity Medians Comparison").
