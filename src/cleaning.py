# imports
import pandas as pd
import datetime as dt

# import dataframe using pandas
def import_dataframe(filepath):
    '''
    Inputs: A filepath to a csv file

    Outputs: A pandas dataframe object
    '''
    return pd.read_csv(filepath)

# fix all columns that have dates
def to_datetime_date_helpfunction(dataframe):
    '''
    Inputs: Pandas dataframe

    Outputs: None
    ----------------------------------------------------------------------
    Transforms all values in all columns in a Pandas Dataframe that have 'Date' 
                                    in their name into datetime.date objects.    
        '''

    # create list of columns
    colsarray = dataframe.columns.values

    # read through and change
    for x in colsarray:
        if 'Date' in x:
            dataframe[f'{x}'] = pd.to_datetime(dataframe[f'{x}']).dt.date
    return

def to_season(date):
    '''
    Inputs: datetime.date object

    Outputs: Name of season that month of date is in. (str)
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
            
def use_dataframe(filepath):
    '''
    Inputs: filepath

    Outputs: a clean dataframe
    ------------------------------
    Only for use with the Washington databreach dataframe. Implements the import_dataframe
    function and the to_datetime_date_helpfunction.
    '''
    # import dataframe from filepath
    unclean_df = import_dataframe(filepath)
    # grab only neccessary columns in desired order
    cleandf = unclean_df[['DateStart', 'DataBreachCause', 'CyberattackType', 'WashingtoniansAffected', 'IndustryType', 'BusinessType']]
    # if Databreach Cause is cyberattack and cyberattacktype is nan put unreported
    cleandf.loc[:, 'CyberattackType'][(cleandf['DataBreachCause'] == 'Cyberattack') 
                                                & (cleandf['CyberattackType'].isnull())] = 'Unreported'
    # enact datetime adjustments
    to_datetime_date_helpfunction(cleandf)
    # add usable(non-fiscal) years column
    cleandf['ActualYears'] = [x.year for x in cleandf['DateStart']]
    # add seasons column
    cleandf['Season'] = cleandf['DateStart'].apply(to_season)

    return cleandf


if __name__ == "__main__":
    filepath = '../data/WA_Databreach_20231102.csv'
    use_dataframe(filepath)