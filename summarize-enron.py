"""
Id:          Cushi Henry
Description: Script to read data and produce 3 outputs; a csv and two bar chart visuals
"""
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import numpy
import sys

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Inserting CSV file into a DataFrame
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
file_name = sys.argv[1]
print 'file location: %s' % str(sys.argv[1])

try:
    df_raw = pd.read_csv(file_name,
                           sep=',',
                           na_values='-',
                           names=
                            ['time',
                             'message_identifer',
                             'sender',
                             'recipients',
                             'topic',
                             'mode']
                         )
except IOError:
    print "Error: Please verify your file location"
    sys.exit(1)

print "DataFrame 'df_raw' created"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This section uses the df_raw to produce a new CSV file
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
sent_counter = 0
received_counter = 0
lst_person = []
dict_results = {}
df_results = pd.DataFrame()

print "Generating CSV in progress..."
lst_person = df_raw['sender'].unique().tolist()

# using distinct list of people, I find their occurances in the sender and receiver columns
# and then insert results into a dictionary
for p in lst_person:
    for sender in df_raw['sender']:
        if p in sender:
            sent_counter += 1
            dict_results.update({p: [sent_counter]})

    for receiver in df_raw['recipients'].str.split("|").dropna():
        for item in receiver:
            if p in item:
                received_counter += 1
                dict_results.update({p : [sent_counter, received_counter]})
    sent_counter = 0
    received_counter = 0

# the dictionary may have null values so I am defaulting these values to 0
for k, v in dict_results.items():
    if len(v) < 2:
        dict_results[k].append(0)

# creates a DF from the dictionary with the 3 values and sort by the 'Sent' column
df_results = pd.DataFrame.from_dict(dict_results, orient='index')
df_results.columns = ['Sent', 'Received']
df_results = df_results.sort_values(['Sent'], ascending=False)

# save the new DF to csv
file_location = file_name.rfind('\\')
df_results.to_csv(file_name[:file_location] + '\enron_t1.csv', sep=',')
print "CSV file 'enron_t1.csv' saved to: " + file_name[:file_location]

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This section produces a bar chart visual and saves it as an PNG
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
print "Generating PNG bar chart in progress..."
df_png = pd.DataFrame()
df_raw['time'] = pd.to_datetime(df_raw['time'], unit='ms').dt.date  # Converts milliseconds to date
df_png = df_raw.iloc[:, [0, 2]]
df_png = df_raw.groupby(["time","sender"])["sender"].size().reset_index(name='count')
df_png = df_png.head(1000)

ax = df_png.plot(x=['time'], y=['count'], kind='bar', title='First 1000 Emails Sent Over Time', figsize=(15, 10), stacked=True)
ax.set_ylabel("Num of Emails", fontsize=12)
#plt.show()
plt.savefig(file_name[:file_location] + '\enron_bar_chart_t1.png')
print "PNG file 'enron_bar_chart_t1.png' saved to: " + file_name[:file_location]

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This section of code produces a bar chart visual and saves as an PNG
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# todo: pretty difficult but a solution is only possible once the second question is fully completed