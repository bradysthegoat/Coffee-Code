# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 13:34:01 2018

@author: PKellicker
"""

import pandas as pd
import numpy as np
import os
import re

def find_curr_recipe(cesar_a, recipe_a, tea_a):
    
    ### need to find what brew ###
    cesar_brew = cesar_a.filter(items = ['Brew Type.1','Brew Size','Brew Type'])
    
    brew_deets = cesar_brew.values
    #brew_deets = np.ndarray.tolist(brew_deets)
    
    brew_type = str(brew_deets[0,0]) # tea type
    size = str(brew_deets[0,1]) # size
    brew_method = str(brew_deets[0,2]) # actual brew type
    
     # clean up strings for matching
    brew_type = brew_type.lower() # convert to lower
    size = size.lower()
    brew_method = brew_method.lower()
    
    brew_type = brew_type.replace(" ", "") # remove spaces
    size = size.replace(" ","")
    brew_method = brew_method.replace(" ","")
    
    if brew_method == "overice": # one misalignment 
        brew_method = "ice" 
        
    
    #FIlter
    
    recipe_curr = recipe_a
    
    if tea_a == 0:
         # filter for coffee -> if coffee, need another field since brew type is nan
         recipe_filter = recipe_curr["Family"] == "coffee"
         recipe_curr = recipe_curr[recipe_filter]
    else:
         # filter for tea -> need brew type for tea -> oolong, green etc
        brew_type = str(brew_type)[:-3] # remove "Tea" if tea
        # filter by type
        recipe_filter = recipe_curr["Type"] == brew_type
        recipe_curr = recipe_curr[recipe_filter]
    
     # filter by size
    recipe_filter = recipe_curr["Size"] == size
    recipe_curr = recipe_curr[recipe_filter]
    
     # filter by brew method
    recipe_filter = recipe_curr["Style"] == brew_method
    recipe_curr = recipe_curr[recipe_filter]
    
   
    
 ### need to work through csv ###

    cur = [recipe_curr, brew_type]
    return cur
   