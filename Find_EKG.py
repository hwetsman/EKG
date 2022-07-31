import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st
import time
import numpy as np
import seaborn as sns
from scipy.signal import argrelextrema


def Create_EKG_DF(ekgs):
    ekg_df = pd.DataFrame()
    prog_bar = st.progress(0)
    for i in range(len(ekgs)):
        file = dir+'/'+ekgs[i]
        prog_bar.progress(i/len(ekgs))
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

    # st.write('I have finished writing EKGs.csv. Try another function!')
    # st.write(ekg_df)
    return ekg_df


def Get_EKG(name):
    file = dir+'/'+name
    df = pd.read_csv(file)
    # st.write(df)
    return df


def Clean_EKG(ekg):
    time0 = time.time()
    ekg = ekg[1000::]
    ekg.reset_index(inplace=True, drop=False)
    ekg.columns = ['micro_volts', 'ignore']
    ekg.micro_volts = ekg.micro_volts.astype(float)
    ekg['seconds'] = ekg.index * 1/510.227
    ekg = ekg[['micro_volts', 'seconds']]
    ekg['peak'] = ekg.micro_volts - ekg.micro_volts.shift(-7)
    ekg['interval'] = ekg.micro_volts - ekg.micro_volts.shift(-1)
    # ekg = Get_R_Peaks(ekg)
    ekg = Get_alt_r(ekg)
    time1 = time.time()
    # st.write('clean ekg', {time1-time0})
    return ekg


def Get_R_Peaks(ekg):
    time0 = time.time()
    # identify QRS complexes
    ekg['qrs'] = 0
    # size = st.sidebar.slider('first pass size', min_value=1, max_value=35, value=5)
    for i in range(ekg.shape[0]):
        numbers = ekg.interval[i-4:i+4]
        if numbers.max()-numbers.min() > 50:
            ekg.loc[i, 'qrs'] = 1
    # # create 3 empty cols
    ekg['int_peak'] = 0
    ekg['int_peak_2'] = 0
    ekg['r_peak'] = 0
    # identify possible r peaks
    qrs_indices = ekg[ekg.qrs == 1].index.tolist()
    # get interim peak
    for idx in qrs_indices:
        diffs = ekg.micro_volts[idx-5:idx+5]
        if diffs.max()-diffs.min() > 500:
            ekg.loc[diffs.idxmax(), 'int_peak'] = 1

    int_peak_df = ekg[ekg.int_peak == 1]
    int_peak_indices = int_peak_df.index

    for idx in int_peak_indices.tolist():
        # calc_bottom = idx-5
        calc_bottom = idx-50
        abs_bottom = np.min(int_peak_indices)
        # calc_top = idx+5
        calc_top = idx+50
        abs_top = np.max(int_peak_indices)
        if calc_bottom > abs_bottom:
            start = calc_bottom
        else:
            start = abs_bottom
        if calc_top > abs_top:
            end = abs_top
        else:
            end = calc_top

        diffs = ekg.micro_volts[start:end]
        # ekg.loc[diffs.idxmax(), 'int_peak_2'] = 1
        ekg.loc[diffs.idxmax(), 'r_peak'] = 1

    # # st.write('This is ekg going into last pass', ekg)
    # int_2_peak_df = ekg[ekg.int_peak_2 == 1]
    # # st.write(int_2_peak_df)
    # int_2_peak_indices = int_2_peak_df.index
    # # st.write(int_2_peak_indices)
    # for idx in int_2_peak_indices.tolist():
    #     # st.write(idx)
    #     calc_bottom = idx-1
    #     abs_bottom = np.min(int_peak_indices)
    #     calc_top = idx+3
    #     abs_top = np.max(int_peak_indices)
    #     if calc_bottom > abs_bottom:
    #         start = calc_bottom
    #     else:
    #         start = abs_bottom
    #     if calc_top > abs_top:
    #         end = abs_top
    #     else:
    #         end = calc_top
    #     diffs = ekg.micro_volts[start:end]
    #     # st.write(diffs)
    #     # st.write(diffs.idxmax())
    #     ekg.loc[diffs.idxmax(), 'r_peak'] = 1
    #     # st.write(ekg.loc[diffs.idxmax(), :])

    ekg = ekg[['micro_volts', 'seconds', 'peak', 'interval', 'qrs', 'r_peak']]
    time1 = time.time()
    # st.write('r_peak', {time1-time0})
    return ekg


def Get_alt_r(ekg):
    n = 190
    ekg['int_peak'] = ekg.iloc[argrelextrema(ekg.micro_volts.values, np.greater_equal,
                                             order=n)[0]]['micro_volts']
    med = ekg.int_peak.median()
    ekg.int_peak = np.where(ekg.micro_volts < med*.5, 0, ekg.int_peak)
    ekg['r_peak'] = np.where(ekg.int_peak > 0, 1, 0)
    ekg = ekg[['micro_volts', 'seconds', 'interval', 'r_peak']]
    # st.write(ekg)
    return ekg


def Get_Singles(ekg):
    # singles = pd.DataFrame()
    time0 = time.time()
    singles = ekg[ekg.r_peak == 1]
    # while peaks.shape[0] > 0:
    #     peak = peaks.iloc[0, 1]
    #     group = peaks.loc[peaks.seconds < peak+.4]
    #     single = group[group.peak == group.peak.max()]
    #     singles = pd.concat([singles, single])
    #     peaks = pd.concat([peaks, group]).drop_duplicates(keep=False)
    # time1 = time.time()
    # st.write('get singles', {time1-time0})
    # st.write(singles)
    return singles


def Get_PACs(singles):
    time0 = time.time()
    singles['interval'] = singles.seconds.shift(-1) - singles.seconds
    median = singles.interval.median()
    singles['med'] = median
    singles['sq_diff'] = (singles.med-singles.interval)*(singles.med-singles.interval)
    PACs = int((singles[singles.sq_diff > .01].shape[0]/2)+.5)
    time1 = time.time()
    # st.write('get pacs', {time1-time0})
    return PACs


def Get_Rate(singles):
    time0 = time.time()
    singles['r_interval'] = singles.seconds - singles.seconds.shift(1)
    med = singles.r_interval.median()
    rate = int(58.3/med)
    time1 = time.time()
    # st.write('get rate', {time1-time0})
    return rate


# create streamlit page
path = './apple_health_export/'
dir = path + 'electrocardiograms'
ekgs = os.listdir(dir)
function = st.sidebar.selectbox(
    'Select a Function', ['Show an EKG', 'Reset EKG Database',  'Show PACs Over Time'], index=0)
ekg_df = pd.read_csv('EKGs.csv')
# st.write('got this far')
#############skip for now#################
if function == 'Reset EKG Database':
    a = st.empty()
    a.write(f'I am creating an index of your {len(ekgs)} EKGs...')
    ekg_df = Create_EKG_DF(ekgs)
    # poor = ekg_df[ekg_df.clas=='Poor Recording']
    ekg_df = ekg_df[~ekg_df.clas.str.contains('Poor Recording')]
    ekg_df.to_csv('EKGs.csv', index=False)
    st.write(ekg_df)
    a.write(
        f'I have finished writing {ekg_df.shape[0]} EKGs with good recordings to EKGs.csv. Try another function!')
##########################################
elif function == 'Show PACs Over Time':
    ekg_df = pd.read_csv('EKGs.csv')
    # poor = ekg_df[ekg_df.clas == 'Poor Recording']
    # ekg_df = ekg_df[~ekg_df.clas.str.contains('Poor Recording')]
    ekg_df.reset_index(inplace=True, drop=True)

    # st.write(
    #     f'There are {ekg_df.shape[0]} EKGs with good recordings.')

    if 'PACs' not in ekg_df.columns:
        a = st.empty()
        b = st.empty()
        a.write(f'I am working your list of {ekg_df.shape[0]} EKGs with good recordings.')
        prog_bar = st.progress(0)
        for idx, row in ekg_df.iterrows():
            # st.write(idx, f"in ekg_df of {ekg_df.loc[idx,'name']}")
            prog_bar.progress((idx)/ekg_df.shape[0])
            ekg_str = ekg_df.loc[idx, 'name']
            ekg = Get_EKG(ekg_str)
            this_classification = ekg_df.loc[ekg_df[ekg_df.name == ekg_str].index.tolist()[
                0], 'clas']
            # a.write(f'I am working {ekg_str}, classified as {this_classification}')
            # b.write(idx)
            ekg = Clean_EKG(ekg)

            # maxes = ekg.nlargest(200, 'peak')
            # max = maxes.peak.median()
            # peaks = ekg[ekg.peak > 0.5*max]
            singles = Get_Singles(ekg)
            PACs = Get_PACs(singles)
            # a.write(f'The EKG evidences {PACs} PACs')
            ekg_df.loc[idx, 'PACs'] = PACs
        prog_bar.empty()
        a.empty()
        ekg_df.to_csv('EKGs.csv', index=False)
    else:
        pass
    # set days for dataset
    first_day = ekg_df.date.min()
    last_day = ekg_df.date.max()
    # create list of days for x_axis
    x_range = pd.DataFrame(pd.date_range(first_day, last_day, freq='d'))
    x_range.columns = ['date']
    x_range.date = x_range.date.astype(str)
    x_range['day'] = x_range.date.str[0:10]
    x_range.reset_index(inplace=True, drop=True)
    x_range = x_range['day']

    afib = ekg_df[ekg_df.clas == 'Atrial Fibrillation']
    afib['day'] = afib.date.str[0:10]
    afib.day = pd.to_datetime(afib.day)
    afib['afib'] = 1
    afib.drop_duplicates(subset='day', inplace=True)
    afib = afib[['afib', 'day']]

    temp = ekg_df.groupby(by='day').max()
    temp['day'] = temp.date.str[0:10]
    temp.reset_index(inplace=True, drop=True)

    plot_df = pd.merge(temp, x_range, on='day', how='outer')
    plot_df.day = pd.to_datetime(plot_df.day)
    plot_df.sort_values(by='day', inplace=True)
    plot_df.PACs.fillna(0, inplace=True)
    plot_df.PACs = plot_df.PACs.astype(int)

    export = pd.merge(plot_df, afib, on='day', how='outer')
    export.afib = export.afib.fillna(0)
    export.afib = export.afib.astype(int)
    export = export[['day', 'PACs', 'afib']]

    how = st.sidebar.radio('How to Plot PACs', ['Bar', 'Rolling Mean'])

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_ylabel('Number of PACs')
    if how == 'Bar':
        plt.bar(export.day, export.PACs)
    else:
        n = st.sidebar.slider('Number of Days Rolling', min_value=1, max_value=30, value=5)
        plot_df['avg'] = plot_df.PACs.rolling(window=n).mean()
        plt.plot(plot_df.day, plot_df.avg)
    ax.set_xticks(export.day[::20], label=export.day[::20])
    plt.xticks(rotation=70, ha='right')

    if afib.shape[0] > 0:
        for day in list(set(afib.day.tolist())):
            plt.vlines(day, 0, 15, colors='r', alpha=.2)
        ax.set_title('Maximum PACs in 30 Second EKGs by Date - Days with AFib in Red')
    else:
        ax.set_title('Maximum PACs in 30 Second EKGs by Date')
    st.pyplot(fig)
    st.write('I have written the export file for this figure to EKG_by_day.csv')
    export.to_csv('EKG_by_day.csv', index=False)
##########################################
elif function == 'Show an EKG':
    # selection
    year = st.sidebar.selectbox('Year of EKG', ['2019', '2020', '2021', '2022'], index=1)
    month = st.sidebar.selectbox(
        'Month of EKG', ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
    ekgs = ekg_df[ekg_df.name.str.contains(year+'-'+month)]
    type = st.sidebar.selectbox('Classification', list(set(ekgs.clas.tolist())))
    show_df = ekgs[ekgs.clas == type]
    ekg_str = st.sidebar.selectbox('Choose an EKG', show_df.name)
# select and clean EKG to show
    ekg = Get_EKG(ekg_str)
    this_classification = ekg_df.loc[ekg_df[ekg_df.name == ekg_str].index.tolist()[0], 'clas']
    st.write(f'You have selected {ekg_str}, classified as {this_classification}')
    ekg = Clean_EKG(ekg)

# # temporary visualization of feature dev
#     fig, ax = plt.subplots(figsize=(15, 10))
#     plt.plot(ekg.index, ekg.micro_volts)
#     for i in range(ekg.shape[0]):
#         if ekg.loc[i, 'r_peak'] == 1:
#             # if ekg.loc[i, 'qrs'] == 1:
#             plt.vlines(i, ymax=500, ymin=0, colors='r')
#     st.pyplot(fig)
#     st.write(ekg)

    # get single peaks
    singles = Get_Singles(ekg)

    # get rate
    rate = Get_Rate(singles)

    # plot EKG
    x = ekg.seconds
    y = ekg.micro_volts
    time0 = time.time()
    fig, ax = plt.subplots(figsize=(15, 4))
    ax.set_ylim(y.min(), y.max())

    PACs = Get_PACs(singles)

    level = int(round(3*PACs/14, 0))
    color_palette = sns.color_palette('RdYlGn_r')

    if type == 'Atrial Fibrillation':
        ax.set_facecolor(color_palette[5])
        # ax.set_facecolor('xkcd:salmon')
    elif type == 'Inconclusive':
        ax.set_facecolor(color_palette[4])
    elif type == 'Heart Rate Over 120':
        ax.set_facecolor(color_palette[4])
    elif type == 'Heart Rate Under 50':
        ax.set_facecolor(color_palette[4])
    elif type == 'Heart Rate Over 150':
        ax.set_facecolor(color_palette[5])
    else:
        ax.set_facecolor(color_palette[level])

    plt.plot(x, y)
    st.pyplot(fig)
    # time1 = time.time()
    if type not in ['Atrial Fibrillation', 'Heart Rate Over 150', 'Heart Rate Over 120']:
        st.write(f'The EKG evidences {PACs} PACs with a heart rate of {rate}')
    else:
        st.write(f'The EKG appears to have a rate of {rate}')


# st.write(ekg_df)
# fig, ax = plt.subplots(figsize=(15, 4))
# ax.set_title('PACs in 30 Second EKGs by Date')
# ax.set_ylabel('Number of PACs')
# ax.set_xticks(ekg_df.index[::20], labels=ekg_df.date[::20], rotation=70)
# plt.plot(ekg_df.date, ekg_df.PACs)
# st.pyplot(fig)
