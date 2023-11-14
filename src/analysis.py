# imports
from cleaning import use_dataframe
import pandas as pd
import numpy as np
import math
from random import choices
import datetime as dt
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import metrics

def bootstrap(data, num_bootstrap_samples=10000):
   '''
   Inputs: Data of type array, series, list; Numerical

   Outputs: A list of bootstrap samples of data
   '''
   bootstrap_samples = []

   for i in range(num_bootstrap_samples):
      bootstrap_samples.append(choices(list(data), k=len(data)))

   return bootstrap_samples

def get_mean_bootstrapped_rate(dataframe, startdate, enddate, column, category, samples=10000):
    '''
    Inputs: Pandas dataframe, startdate(dt.datetime object), enddate(dt.datetime object), column to be be utilized,
            category, value within column to be calculated, samples (number of resamples to be created with bootstrap)

    Outputs: A list containing a number of rates equal to the number of resamples.
    --------------------------------------------------------------------------------------------
    startdate and enddate define period of time to calculate rate over, the column/category calculate the number of occurences
    of the given category over the defined period of time. Only for use with Washington Databreach Dataframe.
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


def rmse(true, predicted):
   mse = np.square(np.subtract(true, predicted)).mean()
   rmse = math.sqrt(mse)
   return rmse

def cross_val(X_train, y_train, k=5):
   kf = KFold(n_splits = k, shuffle=True, random_state = None)
   rmse_list = []
   i = 1

   for train_index, test_index in kf.split(X_train):
      X_train_fold, X_test_fold = X_train.iloc[train_index], X_train.iloc[test_index]
      y_train_fold, y_test_fold = y_train.iloc[train_index], y_train.iloc[test_index]
      model = LinearRegression()
      results = model.fit(X_train_fold, y_train_fold)
      predictions = results.predict(X_test_fold)
      print(f'train_fold{i} has an rmse of:{rmse(y_test_fold, predictions)}')
      i+=1
      rmse_list.append(rmse(y_test_fold, predictions))

   print(f'The mean rmse is: {np.mean(rmse_list)}')