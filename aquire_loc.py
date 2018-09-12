# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 11:15:24 2018

This function is designed to prompt user input for the locations of the necessary data files

It takes no input and returns a list of the three locations


@author: PKellicker
"""
import os 

def acquire_loc():
    # loop for user input
    while(True):
   
        # Prompt user input
        prompt = "Hello, welcome to Coffee Code. I need three excell files to analyze the data: the KPI sheet, the recipe sheet, and the raw data sheets. Type 'cont' if these files are in the cwd and the data files are in a foler named 'Data'. Type 'spec' to specify locations for the files. Type 'exit' to quit. \n"
        answer = input(prompt)

        # Specify new file locations
        if answer == "spec":
            # loop to ensure accuracy
            while(True):
                cesar_loc = input("\nPlease provide the path of the KPI file including the file name \n")
                recipe_loc = input("Please provide the path of the recipe file including the file name \n")
                data_loc = input("Please provide the path of the data folder \n")
        
                # confirm locations 
                print("\nKPI file: ", cesar_loc)
                print("\nrecipe file: ", recipe_loc)
                print("\ndata folder: ", data_loc, "\n")
            
                confirm = input("Are these correct? 'y' or 'n' \n")
            
                if confirm == "y":
                    break
                elif confirm == "n":
                    print("Please try again")
                    continue
                else:
                    print("\nInvalid input. Please try again \n")
            break
    
        # Specify std file locations
        elif answer == "cont":
            cesar_loc = os.getcwd() + "\\" + input("Please specify the KPI file name \n")
            recipe_loc = os.getcwd() + "\\" + input("Please specify the recipe file's name \n") # *recipe book name - may not actually change*
            data_loc = os.getcwd() + "\\Data"
            break
    
        # Exit program 
        elif answer == "exit":
            print("\nGood Bye!")
            quit()
        
        # if typo 
        else:
            print("\nInvalid input. Please try again \n")

    locations = [cesar_loc, recipe_loc, data_loc]    
    return locations 