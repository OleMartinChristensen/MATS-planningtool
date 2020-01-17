# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 16:06:10 2019

@author: David Skånberg
"""

import pickle, os

def Plot_Timeline_Plotter_Plots(FigureDirectory, FilesToPlot):
    """
    
    
    """
    
    for File in FilesToPlot:
        
        FigurePath = os.path.join(FigureDirectory, File+'.fig.pickle')
        try:
            figx = pickle.load(open(FigurePath, 'rb'))
            figx.show()
        except FileNotFoundError:
            pass
    
    