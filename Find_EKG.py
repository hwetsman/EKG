import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st


def Create_EKG_DF(ekgs):
    ekg_df = pd.DataFrame()
    for i in range(len(ekgs)):
        file = dir+'/'+ekgs[i]
        example = pd.read_csv(file)
        dob = example.loc['Date of Birth', 'Name']
        date = example.loc['Recorded Date', 'Name']
        classification = example.loc['Classification', 'Name']
        version = example.loc['Software Version', 'Name']
        ekg_df.loc[i, 'name'] = ekgs[i]
        ekg_df.loc[i, 'date'] = date
        ekg_df.loc[i, 'clas'] = classification
        ekg_df.loc[i, 'vers'] = version
    ekg_df.date = pd.to_datetime(ekg_df.date)
    ekg_df.sort_values(by='date', inplace=True)
    ekg_df.to_csv('EKGs.csv', index=False)


print('\n\nGood Morning, Dave. I am reading your exported EKGs...')
path = './apple_health_export/'
dir = path + 'electrocardiograms'


ekgs = os.listdir(dir)
print(f'I am creating an index of your {len(ekgs)} EKGs...')
Create_EKG_DF(ekgs)
ekg_df = pd.read_csv('EKGs.csv')

print(ekg_df)


# get data from individual df
# example = example.iloc[9::]
# example.columns = ['micro_volts', 'ignore']

# print(example.head(10))
