import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit as st
import time


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
    st.write(df)
    return df


def Clean_EKG(ekg):
    ekg = ekg[1000::]
    ekg.reset_index(inplace=True, drop=False)
    ekg.columns = ['micro_volts', 'ignore']
    ekg.micro_volts = ekg.micro_volts.astype(float)
    # st.write(ekg)
    return ekg


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
ekg_str = st.sidebar.selectbox('Select EKG', ekg_df.name.tolist(), index=0)
# st.write(ekg_str)
st.write(f'There are {ekg_df.shape[0]} EKGs after eliminating the {poor.shape[0]} poor recordings.')
a.write(ekg_df.head(1))

# select and clean EKG to show
st.write(list(set(ekg_df.clas.tolist())))
ekg = Get_EKG(ekg_str)
this_classification = ekg_df.loc[ekg_df[ekg_df.name == ekg_str].index.tolist()[0], 'clas']
st.write(f'You have selected {ekg_str}, classified as {this_classification}')
ekg = Clean_EKG(ekg)

# plot EKG
ekg['seconds'] = ekg.index * 1/510.227
ekg = ekg[['micro_volts', 'seconds']]
ekg['peak'] = ekg.micro_volts - ekg.micro_volts.shift(-7)
max = ekg.peak.max()
peaks = ekg[ekg.peak > 0.65*max]
# st.write(peaks.seconds)
singles = pd.DataFrame()
while peaks.shape[0] > 0:
    # for i in range(4):
    # st.write('peaks', peaks)
    peak = peaks.iloc[0, 1]
    # st.write(peak, peak+.4, peak-.4)
    group = peaks.loc[peaks.seconds < peak+.4]
    # st.write('group', group)
    # find max row of group
    single = group[group.peak == group.peak.max()]
    # st.write('single', single)
    # add max row to new df
    singles = pd.concat([singles, single])
    # st.write('singles', singles)
    # subtract group from peaks
    peaks = pd.concat([peaks, group]).drop_duplicates(keep=False)
    # st.write(peaks)
    # go again
    # st.write(peak, peaks.loc[peaks[peaks.peak == peak.index.tolist()[0]], 'micro_volts'])
# st.write(max, peaks.shape[0], peaks)

# st.write(ekg)
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
