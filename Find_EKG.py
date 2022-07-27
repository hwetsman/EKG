import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st
import time
import numpy as np


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


def Get_EKG(name):
    file = dir+'/'+name
    df = pd.read_csv(file)
    # st.write(df)
    return df


def Clean_EKG(ekg):
    ekg = ekg[1000::]
    ekg.reset_index(inplace=True, drop=False)
    ekg.columns = ['micro_volts', 'ignore']
    ekg.micro_volts = ekg.micro_volts.astype(float)
    ekg['seconds'] = ekg.index * 1/510.227
    ekg = ekg[['micro_volts', 'seconds']]
    ekg['peak'] = ekg.micro_volts - ekg.micro_volts.shift(-7)
    return ekg


def Get_Singles(peaks):
    singles = pd.DataFrame()
    while peaks.shape[0] > 0:
        peak = peaks.iloc[0, 1]
        group = peaks.loc[peaks.seconds < peak+.4]
        single = group[group.peak == group.peak.max()]
        singles = pd.concat([singles, single])
        peaks = pd.concat([peaks, group]).drop_duplicates(keep=False)
    return singles


def Get_PACs(singles):
    singles['interval'] = singles.seconds.shift(-1) - singles.seconds
    median = singles.interval.median()
    singles['med'] = median
    singles['sq_diff'] = (singles.med-singles.interval)*(singles.med-singles.interval)
    PACs = int((singles[singles.sq_diff > .01].shape[0]/2)+.5)
    return PACs


# create streamlit page
a = st.empty()
path = './apple_health_export/'
dir = path + 'electrocardiograms'
ekgs = os.listdir(dir)
a.write(f'I am creating an index of your {len(ekgs)} EKGs...')

# create ekg df
#############skip for now#################
# Create_EKG_DF(ekgs)
##########################################
ekg_df = pd.read_csv('EKGs.csv')
poor = ekg_df[ekg_df.clas == 'Poor Recording']
ekg_df = ekg_df[~ekg_df.clas.str.contains('Poor Recording')]
year = st.sidebar.selectbox('Year of EKG', ['2019', '2020', '2021', '2022'])
select_df = ekg_df[ekg_df.name.str.contains(year)]
ekg_str = st.sidebar.selectbox('Select EKG', select_df.name.tolist(), index=0)
# st.write(ekg_str)
st.write(f'There are {ekg_df.shape[0]} EKGs after eliminating the {poor.shape[0]} poor recordings.')
# a.write(ekg_df.head(1))

# select and clean EKG to show
ekg = Get_EKG(ekg_str)
this_classification = ekg_df.loc[ekg_df[ekg_df.name == ekg_str].index.tolist()[0], 'clas']
st.write(f'You have selected {ekg_str}, classified as {this_classification}')
ekg = Clean_EKG(ekg)

# plot EKG

# find the ekg peaks
maxes = ekg.nlargest(200, 'peak')
max = maxes.peak.median()
peaks = ekg[ekg.peak > 0.5*max]
# get single peaks
singles = Get_Singles(peaks)

# plot EKG and single peaks
x = ekg.seconds
y = ekg.micro_volts
time0 = time.time()
fig, ax = plt.subplots(figsize=(15, 4))
for peak in singles.seconds.tolist():
    plt.vlines(peak, -500, 1500, colors='r')
ax.set_ylim(y.min(), y.max())
plt.plot(x, y)
st.pyplot(fig)
time1 = time.time()
st.write(time1-time0)

# Get PACs


# def Get_PACs(singles):
#     singles['interval'] = singles.seconds.shift(-1) - singles.seconds
#     median = singles.interval.median()
#     singles['med'] = median
#     singles['sq_diff'] = (singles.med-singles.interval)*(singles.med-singles.interval)
#     PACs = singles[singles.sq_diff > .01].shape[0]/2
#     return PACs


# add interval to singles
# singles['interval'] = singles.seconds.shift(-1) - singles.seconds
# median = singles.interval.median()
# singles['med'] = median
# singles['sq_diff'] = (singles.med-singles.interval)*(singles.med-singles.interval)
st.write(singles)
# PACs = singles[singles.sq_diff > .01].shape[0]/2
PACs = Get_PACs(singles)
st.write(PACs)
# st.write(round(.5, 1), round(.5, 0), round(.5, 2))

# fig, ax = plt.subplots(figsize=(15, 4))
# plt.hist(singles.sq_diff, bins=30)
# plt.vlines(singles.sq_diff.median(), 0, 10, colors='r')
# st.pyplot(fig)
