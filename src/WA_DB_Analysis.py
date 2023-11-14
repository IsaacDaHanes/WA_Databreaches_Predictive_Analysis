# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy.stats as st
from random import choices
import datetime as dt
import dataframe_image as dfi

def bootstrap(data, num_bootstrap_samples=10000):
   '''
   Inputs: Data of type array, series, list; Numerical

   Outputs: A list of bootstrap samples of data
   '''
   bootstrap_samples = []

   for i in range(num_bootstrap_samples):
      bootstrap_samples.append(choices(list(data), k=len(data)))

   return bootstrap_samples

def to_datetime_date_helpfunction(dataframe):
            '''
            Inputs: dataframe

            Outputs: dataframe with all values in columns that have 'date' in their 
                                                        name as datetime.date objects    
            '''

            colsarray = dataframe.columns.values

            for x in colsarray:
                if 'Date' in x:
                    dataframe[f'{x}'] = pd.to_datetime(dataframe[f'{x}']).dt.date
            return

def get_rate(dataframe, startdate, enddate, column, type):
    '''
    
    '''
    date_filtered = dataframe[(dataframe['DateStart'] > startdate) & (dataframe['DateStart'] < enddate)]
    grouped = date_filtered[[(f'{column}'),'WashingtoniansAffected']].groupby(f'{column}').sum()
    days = (enddate - startdate).days
    return days (grouped.loc[f'{type}'][0])/days

def get_mean_bootstrapped_rate(dataframe, startdate, enddate, column, category, samples=10000):
    '''
    
    '''
    rates = []
    date_filtered = dataframe[(dataframe['DateStart'] > startdate) & (dataframe['DateStart'] < enddate)]
    column_selected = date_filtered[[(f'{column}'),'WashingtoniansAffected']]
    category_selected = column_selected[column_selected[f'{column}'] == category]
    category_selected = category_selected.dropna()
    bootstrap_affected = bootstrap(category_selected['WashingtoniansAffected'], samples)
    days = (enddate - startdate).days
    for x in bootstrap_affected:
        rates.append(sum(x)/days)
    return rates

def to_season(date):
    '''
    
    '''
    winter = ['Winter', 12, 1, 2]
    spring = ['Spring', 3, 4, 5]
    summer = ['Summer', 6, 7, 8]
    fall = ['Fall', 9, 10, 11]
    seasons = [winter, spring, summer, fall]
    for season in seasons:
        for month in season:
            if date.month == month:
                return season[0]