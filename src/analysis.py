# imports
from cleaning import use_dataframe
import pandas as pd
import numpy as np
import scipy.stats as st
import math
import matplotlib.pyplot as plt
from random import choices
import datetime as dt
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import metrics
import seaborn as sns

def bootstrap(data, num_bootstrap_samples=10000):
   '''
   Inputs: Data of type array, series, list; Numerical

   Outputs: A list of bootstrap samples of data
   '''
   bootstrap_samples = []

   for i in range(num_bootstrap_samples):
      bootstrap_samples.append(choices(list(data), k=len(data)))

   return bootstrap_samples

def get_bootstrapped_rates(dataframe, startdate, enddate, column, category, samples=10000):
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
   '''
   Inputs: true values and predicted values for a linear regression model

   outputs: rmse score
   '''
   mse = np.square(np.subtract(true, predicted)).mean()
   rmse = math.sqrt(mse)
   return rmse

def cross_val(X_train, y_train, k=5):
   '''
   Inputs: training data for x and y, and number of folds:default is 5

   Outputs: a list of rmse scores and their mean
   '''
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

def test_hom_variance(means1, means2):
   '''
   Inputs: two sets of data, either original or produced by bootstrapping

   Outputs: True or False based on homogeneity of variance test
   '''
   variance_ratio = np.std(means1)/np.std(means2)
   if variance_ratio > 3:
      return False
   else:
      return True

def plot_dist(column, category1, category2, means1, means2, bins1=10, bins2=10, rate='n'):
   '''
   Inputs: column, 2 categories, 2 distributions, bins for both distributions, and
   whether or not the distributions are based on rate.

   Outputs: a saved figure of two distributions
   '''
   fig,ax = plt.subplots()
   ax.hist(means1, bins=bins1, color='orange')
   ax.hist(means2, bins=bins2, color='green')
   ax.set_xlabel('Number affected')
   ax.set_ylabel('Samples')
   ax.legend([category1, category2])
   if rate == 'n':
      fig.savefig(f'../images/{column}_hypothtest', bbox_inches='tight')
   else:
      fig.savefig(f'../images/{column}_rate_hypothtest', bbox_inches='tight')

def hypothesis_test(dataframe, column, category1, category2, samples=10000, startdate = None, enddate=None, rate='n', alt='two-sided'):

   '''
   Inputs: pandas dataframe, 1 column and 2 categories that belong to said
            column to compare, number of resamples for bootstrap, start and end
            date for comparing rates, rate-option for comparing rates,
            alt for alt hypothesis in t-test.
        
   Outputs: t-test results and saved png dataframe image to images folder
   '''
   if rate == 'n':
      cat1 = dataframe[dataframe[f'{column}'] == f'{category1}']['WashingtoniansAffected']
      cat1 = cat1.dropna()
      cat2 = dataframe[dataframe[f'{column}'] == f'{category2}']['WashingtoniansAffected']
      cat2 = cat2.dropna()

      boot_cat1 = bootstrap(cat1, samples)
      boot_cat2 = bootstrap(cat2, samples)

      boot_cat1_means = []
      boot_cat2_means = []

      for boot in boot_cat1:
         boot_cat1_means.append(np.mean(boot))

      for boot in boot_cat2:
         boot_cat2_means.append(np.mean(boot))
  
      hom_variance = test_hom_variance(boot_cat1_means, boot_cat2_means)

      plot_dist(column, category1, category2, boot_cat1_means, boot_cat2_means, rate=rate)

      return st.ttest_ind(boot_cat1_means, boot_cat2_means, equal_var=hom_variance, alternative=alt)

   else:
      cat1_rates = get_bootstrapped_rates(dataframe, startdate, enddate, column, category1, samples)
      cat2_rates = get_bootstrapped_rates(dataframe, startdate, enddate, column, category2, samples)

      hom_variance = test_hom_variance(cat1_rates, cat2_rates)

      plot_dist(column, category1, category2, cat1_rates, cat2_rates, rate=rate)

      return st.ttest_ind(cat1_rates, cat2_rates, equal_var=hom_variance, alternative=alt)

def plot_years(dataframe):
   '''
   Inputs: Washington databreach dataframe

   Outputs: 3 saved figures displaying number affected, number of incidents, and
            rate over time.
   '''
   grouped_years = dataframe[['ActualYears', 'WashingtoniansAffected']].groupby('ActualYears')
   num_affected = grouped_years.sum()
   num_incidents = grouped_years.count()
   num_incidents['Number Of Incidents'] = num_incidents['WashingtoniansAffected']
   num_incidents.drop('WashingtoniansAffected', axis=1, inplace=True)

   rate_over_time = (grouped_years.sum()/grouped_years.count())

   fig, ax = plt.subplots()
   ax.plot(num_affected)
   ax.set_title('Washingtonians Affected By Year')
   ax.set_ylabel('Number Affected(millions)')
   ax.set_xlabel('Years')
   fig.savefig(f'../images/affectedbyyear', bbox_inches='tight')

   fig, ax = plt.subplots()
   ax.plot(num_incidents)
   ax.set_title('Number of Incidents by Year')
   ax.set_ylabel('Number of Incidents')
   ax.set_xlabel('Years')
   fig.savefig(f'../images/incidentsbyyear', bbox_inches='tight')

   fig, ax = plt.subplots()
   ax.plot(rate_over_time)
   ax.set_title('Number Affected Per Incident by Year')
   ax.set_ylabel('Rates')
   ax.set_xlabel('Years')
   fig.savefig(f'../images/ratesbyyear', bbox_inches='tight')

   return

def seasons(dataframe):
    '''
    Inputs: Wa databreach dataframe

    Outputs: saved figure pieplot of breaches by season(percentage)
    '''
    grouped_seasons = dataframe[['Season','WashingtoniansAffected']].groupby('Season')
    grouped_seasons.sum()
    grouped_seasons.sum()['WashingtoniansAffected']

    fig, ax = plt.subplots()
    ax.pie(grouped_seasons.sum()['WashingtoniansAffected'], labels=grouped_seasons.sum()['WashingtoniansAffected'].index, autopct='%1.1f%%')
    fig.savefig(f'../images/seasons', bbox_inches='tight')

def create_display_model(dataframe):
   '''
   Inputs: Wa databreach dataframe

   Outputs: a saved figure object plotting the performance of predictive model
   '''
   # getting relevant info
   grouped_years = dataframe[['ActualYears', 'WashingtoniansAffected']].groupby('ActualYears')
   # y
   num_affected = grouped_years.sum()
   # X
   num_incidents = grouped_years.count()
   num_incidents['Number Of Incidents'] = num_incidents['WashingtoniansAffected']
   num_incidents.drop('WashingtoniansAffected', axis=1, inplace=True)
   # put data back together for display
   num_affected['Num_incidents'] = num_incidents['Number Of Incidents']
   # display model
   # create fig, ax object and set ax to the regplot to allow saving
   fig, ax = plt.subplots()
   model_display = sns.regplot(data = num_affected, x='Num_incidents', y='WashingtoniansAffected')
   ax = model_display
   ax.set_title('Model Performance')
   # save
   fig.savefig('../images/model')


if __name__ == "__main__":
   
   filepath = '../data/WA_Databreach_20231102.csv'
   cleandf = use_dataframe(filepath)

   hypothesis_test(cleandf, 'IndustryType', 'Government', 'Non-Profit/Charity', samples=10000, startdate = None, enddate=None, rate='n', alt='greater')
   start = dt.date(2018,1,1)
   end = dt.date(2023,12,30)
   hypothesis_test(cleandf, 'IndustryType', 'Government', 'Non-Profit/Charity', samples=10000, startdate = start, enddate= end, rate='y', alt='less')
   create_display_model(cleandf)
   plot_years(cleandf)
   seasons(cleandf)