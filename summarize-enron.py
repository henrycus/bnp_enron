"""
Id:          Cushi Henry
Description: Script to read data and produce 3 outputs; a csv, a bar chart visuals and a line graph visual
"""
import pandas as pd
import matplotlib.pyplot as plt
import sys
from dateutil import parser

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Setup
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
sent_counter = 0
received_counter = 0
dict_results = {}
start_date = parser.parse("1998-10-01").date()
end_date = parser.parse("1999-01-01").date()
mlist_recs = []

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

df_raw['sender'] = df_raw['sender'].fillna('blank')
print "DataFrame 'df_raw' created"

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Q1 - This section uses the df_raw to produce a new CSV file
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
df_subset = df_raw[['sender', 'recipients']]

print "Generating CSV in progress..."
lst_person = df_subset['sender'].unique().tolist()
print "unique list of people generated..."

# using distinct list of people, I find their occurrences in the sender and receiver columns
# and then insert results into a dictionary
# todo: needs refactoring for performance (can be done with iterrows; similar to question 3)
for p in lst_person:
    for sender in df_subset['sender']:
        if p == sender:
            sent_counter += 1
            dict_results.update({p: [sent_counter]})

    for receiver in df_subset['recipients'].str.split("|").dropna():
        for item in receiver:
            if p == item:
                received_counter += 1
                dict_results.update({p: [sent_counter, received_counter]})
    sent_counter = 0
    received_counter = 0

# the dictionary may have null values so I am defaulting these values to 0
for k, v in dict_results.items():
    if len(v) < 2:
        dict_results[k].append(0)

# creates a DF from the dictionary with 3 values (converting key to an column) and sort by the 'Sent' column
df_results = pd.DataFrame.from_dict(dict_results, orient='index')
df_results.reset_index(inplace=True)
df_results.columns = ['Person', 'Sent', 'Received']
df_results = df_results.sort_values(['Sent'], ascending=False)

# save the new DF to csv
file_location = file_name.rfind('\\')
df_results.to_csv(file_name[:file_location] + '\enron_t1.csv', sep=',', index=False)
print "CSV file 'enron_t1.csv' saved to: " + file_name[:file_location]

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Q2 - This section produces a bar chart visual and saves it as an PNG
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#I create a series of the top senders, slices it to the top N number then convert to a list
#I then compare the list to the raw dataframe to get a new dataframe with the flitered rows

df_subset = pd.DataFrame() #empty DF for re-use

#slicing raw DF on specified dates
df_raw['time'] = pd.to_datetime(df_raw['time'], unit='ms').dt.date  # Converts milliseconds to date
mask = (df_raw['time'] >= start_date) & (df_raw['time'] < end_date)
df_subset = df_raw.loc[mask]

#Get top 10 senders
subset_of_senders = df_subset.groupby(["sender"]).size().sort_values(ascending=False)
subset_of_senders = subset_of_senders.head(10).index.tolist()
df_png = df_subset[df_subset['sender'].isin(subset_of_senders)]
df_png.is_copy = False
print "Generating PNG bar chart in progress..."

#grouping df on how many emails each person sent on a day then reshaping data for visual
df_png = df_png.groupby(["time","sender"])["sender"].size().reset_index(name='count')
df_png = df_png.pivot(index='time',columns='sender', values='count')
ax = df_png.plot(kind='bar', stacked=True, title='1998 Q4 - Top 10 Senders Email Count', figsize=(15,10))
ax.set_ylabel("# of Emails", fontsize=12)

#plt.show()
plt.savefig(file_name[:file_location] + '\enron_bar_chart_q2.png')
print "PNG file 'enron_bar_chart_q2.png' saved to: " + file_name[:file_location]

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Q3 - This section of code produces a bar chart visual and saves as an PNG
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
dict_results = {}
df_subset = df_raw.loc[mask]  #re-using DF sliced on date

print "Generating PNG line graph in progress..."
df_line = df_subset[df_subset['sender'].isin(subset_of_senders)]
df_line = df_subset[['time', 'sender', 'recipients']]
df_line.is_copy = False
df_line['recipients'] = df_line['recipients'].fillna("")

#loops through DF and extracts all recipients into rows. Adds to a list of lists
for index, row in df_line.iterrows():
    for x in row.recipients.split("|"):
        mlist_recs.append([x, row['time'], row['sender']])

df_results = pd.DataFrame.from_records(mlist_recs, columns=["receiver", "time", "sender"])  # Create DF from the list of lists
df_results = df_results.drop_duplicates(subset=['receiver','time','sender'], keep='first')  # Drop duplicate values
df_results = df_results.groupby(["sender","time"])["receiver"].size().reset_index(name='count')  # Group data
df_line = df_results[df_results['sender'].isin(subset_of_senders)]  # Extract only the senders i'm interested in (top 10)

#Plotting Line Graph
df_line = df_line.pivot(index='time',columns='sender', values='count')
ax = df_line.plot(kind='line', stacked=True, title='1998 Q4 - Top 10 Senders Contacted', figsize=(15,10),)
ax.set_ylabel("# of Unique Emails", fontsize=12)

#plt.show()
plt.savefig(file_name[:file_location] + '\enron_line_graph_q3.png')
print "PNG file 'enron_line_graph_q3.png' saved to: " + file_name[:file_location]
print "Process successfully completed"
exit()
