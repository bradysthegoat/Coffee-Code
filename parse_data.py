# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 10:18:57 2018

This file contains functoins required to analyze the data. It is fed by start.py which sets up the 
states required for analysis. 

@author: PKellicker
"""

import pandas as pd
import numpy as np
from datetime import datetime 
import os

# find temp target value from recipe
def find_temp_target(temp_string, recipe_cur): 
    temp_target = recipe_cur.filter(items = [temp_string])   
    temp_target = temp_target.values
    return int(temp_target)

# find time target value from recipe
def find_time_target(time_string, recipe_cur):
     time_target = recipe_cur.filter(items = [time_string]) 
     time_target = time_target.values
     return int(time_target)


# compute average based on count/index to eob
def find_ave(count, t0, tf, data_top, data_bot, data_mid, i = 0, time_target = 0):
    
    # create variable to hold range of values
    bot_range = np.zeros((tf-t0))
    mid_range = np.zeros((tf-t0))
    top_range = np.zeros((tf-t0))
    
    one = t0 + count + time_target #- int(i)
    two = tf + count + time_target #- int(i)
  
   
    for o in range(one,two):
        top_range[o-one] = float(data_top[o])
        bot_range[o-one] = float(data_bot[o])
        mid_range[o-one] = float(data_mid[o])
    
    bot_av = bot_range.mean().round(1)
    mid_av = mid_range.mean().round(1)
    top_av = top_range.mean().round(1)
          
    return[bot_av,mid_av,top_av, one, two] # round to 1 decimal place
 
# find max flow rate based on thermo -> for boiler cooldown time -> cycles 30ml to cool down boiler after use 
def find_cool_down(cesar_cur, recipe_cur, temp_target):
    
    # gather necesary data
    power = cesar_cur["Notes/Time/Realtrem"] # W
    tf = temp_target # C 
    ti = cesar_cur["Water Temp"] # C
    dt = tf - ti # C
    target_fr = recipe_cur["Flow Rate Target (ml/min)"] # ml/min
    target_fr = target_fr * 1.66667e-8 # m^3/s
    
    # calculate wax flow rate based on thermo
    max_fr = power / (4200 * dt) # m^3/s
    
    # find lesser fr and calc cooldown time based on that 
    if max_fr < target_fr:
        cool_time = .00003 / max_fr
    else:
         cool_time = .00003/ target_fr
    
    return cool_time

# find correct data channels and analyze data
def parse_data(recipe_cur, data_cur, data_f, cesar_cur, t0 = 5, tf = 15, end_time = False, top = None, mid = None, bot = None):
    
    
    #*** find correct channels ***#
    
    # channel names given
    if top != None and mid != None and bot != None:
        
        data_filter = data_f["Signal name"] == "POWER"
        ch_power = data_f[data_filter]
    
        data_filter = data_f["Signal name"] == top
        ch_top = data_f[data_filter]
    
        data_filter = data_f["Signal name"] == mid
        ch_mid = data_f[data_filter]

        data_filter = data_f["Signal name"] == bot
        ch_bot = data_f[data_filter]
        
        channels =[str(ch_bot['CH'].values)[2:-2], str(ch_mid['CH'].values)[2:-2], str(ch_top['CH'].values)[2:-2], str(ch_power["CH"].values)[2:-2]]
   
    # channel names not given
    else:
        
        channels = find_channel(data_f) # bot mid top power
       
    
    #*** prepare data for analysis ***#
    ch_bot = channels[0] # bot
    ch_mid = channels[1] # mid
    ch_top = channels[2] # top
    ch_power = channels[3] # power

    # find number of data entries
    data_power_1 = data_cur.filter(items = [ch_power])
    data_count = data_power_1.shape[0]
    
    # create series of specific data 
    data_bot = pd.Series(data_cur[ch_bot].values) # bot data
    data_mid = pd.Series(data_cur[ch_mid].values) # mid data                # need condition to check if mid is actually on a ch *update: new files should have mid
    data_top = pd.Series(data_cur[ch_top].values) # top data
    data_power = pd.Series(data_cur[ch_power].values) # power data
    
    # format data for use -> remove begining "+ "
    for i in range(0,data_count):
        data_bot[i] = data_bot[i].replace("+ ", "")
        data_mid[i] = data_mid[i].replace("+ ", "")
        data_top[i] = data_top[i].replace("+ ", "")
    
    
    # find number of block in recipe
    blocks = recipe_cur.filter(items = ["# of Blocks"]) # filter
    blocks = blocks.values # get values
    blocks = blocks.astype(int) # convert to int
    blocks = np.asscalar(blocks) # convert to scalar


    # find data from recipe
    recipe_cur = recipe_cur.fillna(0) # replace nan with 0
    temp_string = "Temp Target (°C)"
    temp_target = find_temp_target(temp_string, recipe_cur) # find 1st temp target
    
    time_string = "Time Target (s)"
    time_target = find_time_target(time_string, recipe_cur) # find 1st time target -> should be nan
  
    # ************************************************************************************************************** #
  
    #*** analyze data ***#
   
    # if user spec end_time -> analyze based on run time provided in KPI
    if end_time:
        
        cesar_end = cesar_cur["end_time"] # find run time from cesar
        cesar_end = str(cesar_end)[5:-33] # format for use
        cesar_end = cesar_end.replace(" ", "") # remove any spaces
        
        #cesar_end = datetime.strptime(str(cesar_end), "%M:%S")
        #cesar_end = cesar_end.values
        
        data_time = data_cur["Date&Time"] # filter for times in data

        
        for i in range(1,data_count): # cycle thru to format
            data_time[i] = data_time[i][14:]
        
        data_time = data_time.drop(0) # remove first value -> = "Time"
        
        data_temp = data_time[1] # assign variable for begining time of when data started recording
        
 
      
        # find end of brew time by adding run time with begining time of data                       ####**** need to add a variable of when daq was started
        cesar_end_1 = int(cesar_end[0]) + int(data_temp[0]) # add msbs                                       e.g. Cesar startes daq after 2 secs of starting brew
        cesar_end_2 = int(cesar_end[1]) + int(data_temp[1])                                 
        cesar_end_3 = int(cesar_end[3]) + int(data_temp[3]) # skip ':'
        cesar_end_4 = int(cesar_end[4]) + int(data_temp[4]) # add lsbs
        
        
        # dealing with ovf the manual way cuz i dont know datetime :/ 
        if cesar_end_4 > 9:
            cesar_end_4 = cesar_end_4 - 10 
            cesar_end_3 = cesar_end_3 +1
        if cesar_end_3 > 5:
            cesar_end_3 = cesar_end_3 - 6
            cesar_end_2 = cesar_end_2 + 1
  
        if cesar_end_2 > 9:
            cesar_end_2 = cesar_end_2 - 10
            cesar_end_1 = cesar_end_1 + 1
        if cesar_end_1 > 5:
            cesar_end_1 = cesar_end_1 - 6 
            
        # concatinate for true end time that can be found in data file
        data_end_time = str(cesar_end_1) + str(cesar_end_2) + ":" + str(cesar_end_3) + str(cesar_end_4)
        
        # filter for end time
        data_filter = data_time == data_end_time
        index = data_filter[data_filter == True].index[0] # find index of correct end time in data
        
        #string = time_string + "." + str(blocks-1)
        
        #  time_target = find_time_target(string, recipe_cur)
        
        # send index to find_ave to calculate values
        
        avs = find_ave(count=index, t0=t0, tf=tf, data_top=data_top, data_bot=data_bot, data_mid=data_mid) #(count, t0, tf, data_top, data_bot, data_mid, i = 0, time_target = 0)
       
        bot_av = avs[0]
        mid_av = avs[1]
        top_av = avs[2]
        
       
        
    # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
    
    # analyze data by recipe and power pattern
    else:
    
        count = 1 # start index at 1 because first value is 'V' for voltage
        for i in range(0,blocks): # last block
            before = count
            
            # first block always 1s but there are always 0s due to delay
            if i == 0:
                for n in range(count,data_count):
                    temp = data_power[n].replace("+ ", "") # format data
                    temp = float(temp) * 1000 # it was throwing error on comparing floats so I removed decimals
                    temp = int(temp) # change to int since no more decimals and need to compare
                    
                    count = count + 1
                    
                    if temp > 120: # no more 0s
                        break 
                        
        
            # hit the end, wait the drip out and average
            if i == blocks-1: 
                
                # send numbers to find_ave and return avs
                avs = find_ave(count=count,t0=t0, tf=tf, data_top=data_top, data_bot=data_bot, data_mid=data_mid, i=i, time_target=time_target) #(count, t0, tf, data_top, data_bot, data_mid, i = 0, time_target = 0)
                
                # store avs into specific variables for return
                bot_av = avs[0]
                mid_av = avs[1]
                top_av = avs[2]
               
                '''
                one = avs[3]
                two = avs[4]
                '''
            
            
            # boiler on - look for 1s
            elif temp_target != 0: 
                
                for j in range(count,data_count): # loop through data to follow patter -> looking for 1 -> 0
                
                    temp = data_power[j].replace("+ ", "") # format data
                    temp = float(temp) * 1000 # it was throwing error on comparing floats so I removed decimals
                    temp = int(temp) # change to int since no more decimals and need to compare
                
                    count = count + 1 # keep track of index 
                
                    if temp < 120: # -> back to 0s -> new block need to cycle temp_target and time_target
                        
                        temp_temp_target = temp_target # create temparary of temp_target to compare for back to back 1 blocks               
                        temp_string_1 = temp_string + "." + str(i+1) # concatinate new name for recipe book -> block 2 time_target = Time Target (°C).1, 3 -> " ".2
                        temp_target = find_temp_target(temp_string_1, recipe_cur) # find new temp_targer
                    
                        # check for back to back 1 blocks  -> *** == not gonna work w/ 98 and 96 
                        if temp_target > 0 and temp_temp_target >0 and i+2 <= blocks: # check for doubles, two blocks of 1s 
                            temp_string_1 = temp_string + "." + str(i+2)
                            temp_target = find_temp_target(temp_string_1, recipe_cur)
                            time_string_1 = time_string + "." + str(i+2) # -> next block means titles add .(block# -1)
                            time_target = find_time_target(time_string_1, recipe_cur)
                            break
                    
                    
                        time_string_1 = time_string + "." + str(i+1) # -> next block means titles add .(block# -1)
                        time_target = find_time_target(time_string_1, recipe_cur) # find new time_target
                        
                        cool_down = find_cool_down(cesar_cur, recipe_cur, temp_target)
                        count = count + cool_down
                        break
         
            # boiler off - look for 0's or wait out drip time                                           ####**** need to imcorporate cool down time
            elif temp_target == 0:                                                                  #  boiler is cooled with ~30 ml water after shutoff 
                                                                                                    # need to figure out time to cycle the 30 and add to time target
                for k in range(count,data_count): # cycle through starting at current index(count)                                                
    
                    count = count + 1  # keep track of index
                    
                
                    if time_target == count - (before + 8): # -> back to 1s -> new block new: just wait out drip time + 8 for delay ^^^^
                        
                        #temp_temp_target = temp_target # dont need to check for duplicates since its not gonna plow through 0s of 2 blocks
                    
                        # concatinate string for next data block
                        temp_string_1 = temp_string + "." + str(i+1)
                        temp_target = find_temp_target(temp_string_1, recipe_cur)
                        
                        time_string_1 = time_string + "." + str(i+1) # -> next block means titles add .(block# -1)
                        time_target = find_time_target(time_string_1, recipe_cur)
                    
                        break
            
    
    return [bot_av,mid_av,top_av] # return values
    

# open file and skip to line specified with 'line' string 
def skip_to(fle, line, folder, **kwargs):
    os.chdir(folder)
    if os.stat(fle).st_size == 0:
        raise ValueError("File is empty")
    with open(fle) as f:
        pos = 0
        cur_line = f.readline()
        while not cur_line.startswith(line):
            pos = f.tell()
            cur_line = f.readline()
        f.seek(pos)
        return pd.read_csv(f, **kwargs)
    
    
# find the channels for power, top, mid, bot
def find_channel(data_table):
    
    data_f = data_table.iloc[0:10, 0:2] # get top of csv file -> channel table
    
    data_filter = data_f["Signal name"] == "POWER"
    data_power_f = data_f[data_filter]
    
    data_filter = data_f["Signal name"] == "TOP"
    data_top_f = data_f[data_filter]
    
    data_filter = data_f["Signal name"] == "MID"
    data_mid_f = data_f[data_filter]

    data_filter = data_f["Signal name"] == "BOT"
    data_bot_f = data_f[data_filter]   
    
    # return channel numbers in correct form
    channels_f = [str(data_bot_f['CH'].values)[2:-2], str(data_mid_f['CH'].values)[2:-2], str(data_top_f['CH'].values)[2:-2], str(data_power_f["CH"].values)[2:-2]]
    
    return channels_f # bot, mid, top, power

#*******************************************************************************#
  
    #data_power = data_power.iloc[10:data_count] # ignore begining 0s -> start delay 
    #data_power = data_power.values
    #data_power = str(data_power).replace("[", "").replace("'", "").replace("]", "").replace("+ ", "")
    #data_power = int(float(data_power))
    #data_power = np.asscalar(data_power)
    
    
    #data_power = data_power.replace("+ ", "")         




    '''
        one = index + t0 + time_target  # find indexes for temp values
        two = index + tf + time_target
                '''


    '''
                one = count + t0 + time_target - i +1
                two = count + tf + time_target - i 
            
                
                if ch_mid != "": # if there is an actual mid channel
               
                    data_mid = pd.Series(data_cur[ch_mid].values)
                    for t in range(0,data_count):
                        data_mid[t] = data_mid[t].replace("+ ", "")
                    
                    mid_av = np.zeros((tf-t0))
                
                    for p in range(one,two+1):
                        mid_av[p-one] = float(data_mid[p])
                
                        mid_av = mid_av.mean()
                
                for o in range(one,two+1):
                    bot_av[o-one] = float(data_bot[o])
                    top_av[o-one] = float(data_top[o])
            
                bot_av = bot_av.mean()
                top_av = top_av.mean()
            
                
                data_range = data_power.iloc[one:two] # should be top, mid, bot not power 
                bot_av = data_bot.iloc[one:two]
                #mid_av = data_mid.iloc[one:two]
                top_av = data_top.iloc[one:two].to_frame().mean()
                
                        '''
    '''
                    temp = data_power[k].replace("+ ", "")
                    temp = float(temp) * 1000
                    temp = int(temp)
                    '''
    '''
                        if temp_target == temp_temp_target and i+2 <= blocks: # check for doubles, two blocks of 0s 
                            temp_string_1 = temp_string + "." + str(i+2)
                            temp_target = find_temp_target(temp_string_1, recipe_cur)
                            time_string_1 = time_string + "." + str(i+2) # -> next block means titles add .(block# -1)
                            time_target = find_time_target(time_string_1, recipe_cur)
                            break
                        '''

    '''
    data = data_table.iloc[0:10, 1:2] # convert to series
    data_0 = data.values
    data_1 = str(data_0)
    data_2 = data_1.split("\n") 
    data_3 = pd.Series(data_2) 
    
    data_filter = data_3.str.contains("BOT", case = False) # find channels -> still errs when other lines have 'bot' 'mid' or 'top'
    data_bot = data_f[data_filter]
    
    data_filter = data_3.str.contains("mid", case = False, regex = False)
    data_mid = data_f[data_filter]
    
    data_filter = data_3.str.contains("TOP", case = False)
    data_top = data_f[data_filter]
    '''
    


'''
path = "C:\\Users\\pkellicker\\Desktop\\Coffee Code\\Code\\files2"
file = "CP300_SER2.csv"

data_table_1 = skip_to(file, "CH", path)
data = skip_to(file, "Number", path)

lol = parse_data(top = "TOP", bot = "BOT", mid = "MID", data_table = data_table_1, data_cur = data)
'''
