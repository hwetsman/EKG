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
    ekg_df['day'] = ekg_df.date.str[0:10]
    ekg_df.date = pd.to_datetime(ekg_df.date)
    ekg_df.sort_values(by='date', inplace=True)
    ekg_df.to_csv('EKGs.csv', index=False)
    st.write('I have finished writing EKGs.csv. Try another function!')
    st.write(ekg_df)
    return ekg_df


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
function = st.sidebar.selectbox(
    'Select a Function', ['Show an EKG', 'Reset EKG Database',  'Show PACs Over Time'])
a.write(f'I am creating an index of your {len(ekgs)} EKGs...')
ekg_df = pd.read_csv('EKGs.csv')
# create ekg df
#############skip for now#################
if function == 'Reset EKG Database':
    ekg_df = Create_EKG_DF(ekgs)
##########################################
elif function == 'Show PACs Over Time':
    ekg_df = pd.read_csv('EKGs.csv')
    poor = ekg_df[ekg_df.clas == 'Poor Recording']
    ekg_df = ekg_df[~ekg_df.clas.str.contains('Poor Recording')]
    st.write(
        f'There are {ekg_df.shape[0]} EKGs after eliminating the {poor.shape[0]} poor recordings.')

    if 'PACs' not in ekg_df.columns:
        for idx, row in ekg_df.iterrows():
            ekg_str = ekg_df.loc[idx, 'name']
            ekg = Get_EKG(ekg_str)
            this_classification = ekg_df.loc[ekg_df[ekg_df.name == ekg_str].index.tolist()[
                0], 'clas']
            a.write(f'I am working {ekg_str}, classified as {this_classification}')
            ekg = Clean_EKG(ekg)
            maxes = ekg.nlargest(200, 'peak')
            max = maxes.peak.median()
            peaks = ekg[ekg.peak > 0.5*max]
            singles = Get_Singles(peaks)
            PACs = Get_PACs(singles)
            a.write(f'The EKG evidences {PACs} PACs')
            ekg_df.loc[idx, 'PACs'] = PACs

        # st.write(ekg_df)
        # ekg_df['label'] = ekg_df.name + str(ekg_df.PACs)
        ekg_df.to_csv('EKGs.csv', index=False)

        # try to get PACs and number of EKG by day

        # grouper = ekg_df.groupby([pd.Grouper(freq='1D'), 'PACs'])

        afib = ekg_df[ekg_df.clas == 'Atrial Fibrillation']
        st.write(afib)
        hist_df = ekg_df.groupby(by='day').max()
        fig, ax = plt.subplots(figsize=(15, 4))
        ax.set_title('Maximum PACs in 30 Second EKGs by Date')
        ax.set_ylabel('Number of PACs')
        # ax.set_xticks(ekg_df.index[::20], labels=ekg_df.day[::20], rotation=70, ha='right')
        # plt.bar(ekg_df.date, ekg_df.PACs)
        plt.bar(hist_df.index, hist_df.PACs)
        st.pyplot(fig)
    else:
        afib = ekg_df[ekg_df.clas == 'Atrial Fibrillation']
        st.write(afib)
        hist_df = ekg_df.groupby(by='day').max()
        # st.write(hist_df)
        fig, ax = plt.subplots(figsize=(15, 4))
        ax.set_title('Maximum PACs in 30 Second EKGs by Date')
        ax.set_ylabel('Number of PACs')
        # ax.set_xticks(ekg_df.index[::20], labels=ekg_df.day[::20], rotation=70, ha='right')
        plt.bar(hist_df.index, hist_df.PACs)
        # plt.bar(ekg_df.date, ekg_df.PACs)
        st.pyplot(fig)


elif function == 'Show an EKG':
    year = st.sidebar.selectbox('Year of EKG', ['2019', '2020', '2021', '2022'], index=1)
    month = st.sidebar.selectbox(
        'Month of EKG', ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
    ekgs = ekg_df[ekg_df.name.str.contains(year+'-'+month)]
    ekg_str = st.sidebar.selectbox('Choose an EKG', ekgs)
# select and clean EKG to show
    ekg = Get_EKG(ekg_str)
    this_classification = ekg_df.loc[ekg_df[ekg_df.name == ekg_str].index.tolist()[0], 'clas']
    st.write(f'You have selected {ekg_str}, classified as {this_classification}')
    ekg = Clean_EKG(ekg)

    # find the ekg peaks
    maxes = ekg.nlargest(200, 'peak')
    max = maxes.peak.median()
    peaks = ekg[ekg.peak > 0.5*max]
    # get single peaks
    singles = Get_Singles(peaks)

    # plot EKG
    x = ekg.seconds
    y = ekg.micro_volts
    time0 = time.time()
    fig, ax = plt.subplots(figsize=(15, 4))
    ax.set_ylim(y.min(), y.max())
    plt.plot(x, y)
    st.pyplot(fig)
    # time1 = time.time()

    PACs = Get_PACs(singles)
    st.write(f'The EKG evidences {PACs} PACs')

# st.write(ekg_df)
# fig, ax = plt.subplots(figsize=(15, 4))
# ax.set_title('PACs in 30 Second EKGs by Date')
# ax.set_ylabel('Number of PACs')
# ax.set_xticks(ekg_df.index[::20], labels=ekg_df.date[::20], rotation=70)
# plt.plot(ekg_df.date, ekg_df.PACs)
# st.pyplot(fig)
