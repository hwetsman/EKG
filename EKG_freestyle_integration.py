import pandas as pd

ekg_file = 'EKG_by_day.csv'
freestyle_file = 'freestyle_by_day.csv'
ekg = pd.read_csv(ekg_file)
freestyle = pd.read_csv(freestyle_file)

ekg.date = pd.to_datetime(ekg.date)
ekg.sort_values(by='date')
freestyle.date = pd.to_datetime(freestyle.date)
freestyle.sort_values(by='date')
print(freestyle)
print(ekg)
df = pd.merge(ekg, freestyle, on='date', how='outer')
df = df.dropna()

cols = df.columns
floats = ['max_glucose', 'mean_glucose']
times = ['date']
ints = [x for x in cols if x not in floats+times]
for col in ints:
    df[col] = df[col].astype(int)

print(df)
