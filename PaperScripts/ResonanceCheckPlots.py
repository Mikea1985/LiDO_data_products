import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import os.path
from os import path
import os
import sys
import pandas as pd
import re

def ROI():
    #data for object 11(0224T01)
    Time0, Index0,  SMA0, Ecc0, Inc0, Omega0, omega0, M0, Longitude0 = np.genfromtxt("tp11.out", unpack=True)
    Time1, Index1, SMA1, Ecc1, Inc1, Omega1, omega1, M1, Longitude1 = np.genfromtxt("LN11.out", unpack=True) 

    #data for object 18(0403U07)
    Time2, Index2,  SMA2, Ecc2, Inc2, Omega2, omega2, M2, Longitude2 = np.genfromtxt("tp18.out", unpack=True)
    Time3, Index3, SMA3, Ecc3, Inc3, Omega3, omega3, M3, Longitude3 = np.genfromtxt("LN18.out", unpack=True)
    
    ##### pull out the data for clone 1 from object 11 #####
    j=1
    
    Time0 = Time0[Index0 == j]      
    SMA0 = SMA0[Index0 == j]
    Ecc0 = Ecc0[Index0 == j]
    Inc0 = Inc0[Index0 == j]
    Omega0 = Omega0[Index0 == j]
    omega0 = omega0[Index0 == j]
    M0 = M0[Index0 == j]
    Longitude0 = Longitude0[Index0 == j]
    Index0 = Index0[Index0 == j]

    Pomega0 = (Omega0 + omega0)%360
    
    #resonance to plot
    resonance1 = 28
    resonance2 = 9
    
    #calculate the resonant angle
    ResAng = (resonance1*Longitude0-resonance2*Longitude1-(resonance1-resonance2)*Pomega0)%360
    
    
    ###### pull out the data for clone 0 from object 18 #####
    j=0

    Time2 = Time2[Index2 == j]      
    SMA2 = SMA2[Index2 == j]
    Ecc2 = Ecc2[Index2 == j]
    Inc2 = Inc2[Index2 == j]
    Omega2 = Omega2[Index2 == j]
    omega2 = omega2[Index2 == j]
    M2 = M2[Index2 == j]
    Longitude2 = Longitude2[Index2 == j]
    Index2 = Index2[Index2 == j]
    
    Pomega2 = (Omega2 + omega2)%360
    
    #resonance to plot
    resonance1 = 3
    resonance2 = 2
    
    #calculate the resonant angle
    ResAng2 = (resonance1*Longitude2-resonance2*Longitude3-(resonance1-resonance2)*Pomega2)%360
    
    NumberOfLines = len(SMA0) #number of output data for each clone
       
    year = 2.*np.pi # One year in units where G=1
    Noutputs = 15001 # number of outputs from the sim
    sim_length = 30e6  #length of the simulation
    times = np.linspace(0, sim_length*year, Noutputs)  # Length of simulation (start, end, number of divisions)
    ResonanceWindowNumber = 10 #number of windows used to determine resonance
    ResonanceAngleSize = 5 #resonance angle bin size
    
    #parameters of each box/window used (5 degree angle size x 3 Myr length)
    WindowSize = ResonanceAngleSize
    TimeLength = 30 #Myr
    WindowLength = int(TimeLength/ResonanceWindowNumber) #Myr

    blocks = np.zeros((ResonanceWindowNumber, int(360/WindowSize))) #grid blocks where the resonance argument is found
    blocks2 = np.zeros((ResonanceWindowNumber, int(360/WindowSize))) #grid blocks where the resonance argument is found
    blocks3 = np.zeros(int(360/WindowSize)) #grid blocks where the omega angle is found

    AngleRange = np.arange(0, 360, WindowSize)  # Array of angles 5 degrees increment each step    
    
    WindowStep = int(NumberOfLines / ResonanceWindowNumber) #number of data values in each window
    
    
    ##### determines which grid blocks contain data values for the resonant argument #####
    #loops through checking each grid block to see if the resonant argument data is found there 
    Loop = 0
    Window = int(0)    
    while Window + WindowStep < len(ResAng):
                    
        WindowResAng = ResAng[Window:Window + WindowStep]
        AnglePresent = np.zeros(len(AngleRange)) + 1
                
        for step in np.arange(0, len(AngleRange)): 
            if len(WindowResAng[(WindowResAng > AngleRange[step]) * (WindowResAng < (AngleRange[step]+WindowSize))]) == 0:
                blocks[Loop][step] = 1
                                    
                
        Window += WindowStep  # Increment Window
        Loop += 1  # Increment Loop


    ##### determines which grid blocks contain data values for the resonant argument #####
    #loops through checking each grid block to see if the resonant argument data is found there 
    Loop = 0
    Window = int(0)
    while Window + WindowStep < len(ResAng2):

        WindowResAng = ResAng2[Window:Window + WindowStep]
        AnglePresent = np.zeros(len(AngleRange)) + 1
                
        for step in np.arange(0, len(AngleRange)): 
            if len(WindowResAng[(WindowResAng > AngleRange[step]) * (WindowResAng < (AngleRange[step]+WindowSize))]) == 0:
                blocks2[Loop][step] = 1
                                    
                
        Window += WindowStep  # Increment Window
        Loop += 1  # Increment Loop


    ##### determines which grid blocks contain data values for the omega angle #####
    #loops through checking each grid block to see if the omega angle data is found there 
    Window = int(0)
                    
    WindowResAng = omega2[Window:Window + NumberOfLines]
    AnglePresent = np.zeros(len(AngleRange)) + 1
                
    for step in np.arange(0, len(AngleRange)): 
        if len(WindowResAng[(WindowResAng > AngleRange[step]) * (WindowResAng < (AngleRange[step]+WindowSize))]) == 0:
            blocks3[step] = 1



    #########################################################################################
    ######### create a plot with subplots showing the resonant and omega angles##############
    fig, axs = plt.subplots(3, sharex='col', sharey='row', figsize=(20,22.5))
    
    #create subplot 1
    axs[0].set_title("(a)", size=34)
    axs[0].set_ylabel(r"$\phi$ [$\degree$]", size=34)
    axs[0].set_ylim(0, 360)
    axs[0].set_xlim(0, TimeLength)
    axs[0].tick_params(
        axis='both',          # applies to both x and y axis
        which='major',        # applies to major ticks
        labelsize=34         # font size of the tick labels
    )
    ResAng = ResAng%360 #restrict resonant angle to 360 degrees
    
    #create subplot 2
    axs[1].set_title("(b)", size=34)
    axs[1].set_ylabel(r"$\phi$ [$\degree$]", size=34)
    axs[1].set_ylim(0, 360)
    axs[1].set_xlim(0, TimeLength)
    axs[1].tick_params(
        axis='both',          # applies to both x and y axis
        which='major',        # applies to major ticks
        labelsize=34         # font size of the tick labels
    )
    ResAng2 = ResAng2%360 #restrict resonant angle to 360 degrees
    
    #create subplot 3
    axs[2].set_title("(c)", size=34)
    axs[2].set_xlabel("time [Myr]", size=34)
    axs[2].set_ylabel(r"$\omega$ [$\degree$]", size=34)
    axs[2].set_ylim(0, 360)
    axs[2].set_xlim(0, TimeLength)
    axs[2].tick_params(
        axis='both',          # applies to both x and y axis
        which='major',        # applies to major ticks
        labelsize=34         # font size of the tick labels
    )
    omga2 = omega2%360 #restrict omega angle to 360 degrees
    
    
    #plot the vertical grid lines (every resonance window)
    yline=np.arange(0,360)
    xline=np.ones(360)
    for vertline in np.arange(0,TimeLength+1,WindowLength):
        axs[0].plot(xline*vertline,yline,'-',color='black')
        axs[1].plot(xline*vertline,yline,'-',color='black')
        
    #plot the horizontal grid lines (every resonance angle size 5,10,15 degrees)
    yline=np.ones(TimeLength+1)
    xline=np.arange(0,TimeLength+1,1)
    for horline in np.arange(0,361,WindowSize):
        axs[0].plot(xline,yline*horline,'-',color='black')
        axs[1].plot(xline,yline*horline,'-',color='black')
        axs[2].plot(xline,yline*horline,'-',color='black')
        
    #plot resonance argument/omega on the subplots
    axs[0].plot(times/(year*1e6), ResAng, color='black', marker='o', linestyle='none', linewidth=2, markersize=1)
    
    axs[1].plot(times/(year*1e6), ResAng2, color='black', marker='o', linestyle='none', linewidth=2, markersize=1)
    
    axs[2].plot(times/(year*1e6), omega2, color='black', marker='o', linestyle='none', linewidth=2, markersize=1)
    
    #set the number of ticks on the y-axis for each subplot
    axs[0].yaxis.set_major_locator(ticker.MaxNLocator(5))
    axs[1].yaxis.set_major_locator(ticker.MaxNLocator(5))
    axs[2].yaxis.set_major_locator(ticker.MaxNLocator(5))
    
    #fill in the grid boxes where there is no resonant angle 
    for i in range(0, ResonanceWindowNumber):
        for j in range(0, len(AngleRange)):
            if blocks[i][j] == 1:
                rectangle = matplotlib.patches.Rectangle((i*WindowLength,j*ResonanceAngleSize),WindowLength,ResonanceAngleSize, color ='#3DED97')
                axs[0].add_patch(rectangle)
                
            if blocks2[i][j] == 1:
                rectangle = matplotlib.patches.Rectangle((i*WindowLength,j*ResonanceAngleSize),WindowLength,ResonanceAngleSize, color ='#3DED97')
                axs[1].add_patch(rectangle)
    
    #fill in the grid boxes where there is no resonant angle (for only 1 Window)
    for j in range(0, len(AngleRange)):
        if blocks3[j] == 1:
            rectangle = matplotlib.patches.Rectangle((0,j*ResonanceAngleSize),30,ResonanceAngleSize, color ='#3DED97')
            axs[2].add_patch(rectangle)

    plt.savefig("ResonantArgumentomegaPlot5.png")
    plt.close()

# Main function
if __name__ == '__main__':
    ROI()
