# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 08:41:28 2021

@author: 91998
"""


import streamlit as st
from datetime import datetime
from google.cloud import firestore
import pandas as pd
import pytz
import seaborn as sns
from matplotlib import pyplot as plt

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("firestorekey.json")

# Get the current time to filter and get the relevant match as of now
tz_India = pytz.timezone('Asia/Calcutta') 
currtime = datetime.now(tz_India)

# Read the dataset containing information on MatchId, Team1, Team2, Winner and match time as per preannounced schedule
df = pd.read_csv('IPLdata.csv', parse_dates= ['Time'])
s = pd.to_datetime(df['Time'])
matches_total = df.shape[0]

# Need this to make the timestamp timezone aware else it causes error while comparing tz-aware and tz-naive types
df['Time1'] = s.dt.tz_localize('Asia/Calcutta')

# Pick all matches yet to be played and pick the first one for display
dftemp = df[df["Time1"] > currtime ]
row = dftemp.iloc[0]

df_played = df[(df["Time1"] < currtime )  & ( len(df["Winner"]) > 0) ]
matches_played = df_played.shape[0]

# Present the user with information about playing teams and seek response
st.sidebar.write( "Welcome! Please submit you response for ", row['Team1'], " v/s", row['Team2'], " match at ", row['Time'])

# Select user who wants to submit response. There could be more sophisticated setup with login/pwd, but keeping it simple for this example
players = ( 'Player 1', 'Player 2','Player 3')
user = st.sidebar.selectbox( 'Please chose your login name', players )

team_selected = st.sidebar.selectbox( 'Please chose your team', ( 'None', row['Team1'], row['Team2'] ))                                                  

# From the firestore client get the handle for the user
doc_ref = db.collection("users").document(user)
submit = st.sidebar.button('Submit Response')

# If user clicks on submit response then store that selection as an update to existing dataset
if submit: 
  doc_ref.update( {row['MatchId']: team_selected } )
  st.write('Your response has been submitted, good luck!')


# Loop through all players data and show the current selection

choicelist = []
for player in players:
  tempdoc_ref = db.collection("users").document(player)
  tempdoc = tempdoc_ref.get()
  try:
    val = tempdoc.to_dict()[row['MatchId']]   
    choicelist.append({"Player": player, "Choice": val })    
  except:
    print("ignore error")
              
choices = pd.DataFrame(choicelist)
if choices.shape[0] > 0:
  st.write('Player preferences for upcoming match')
  st.write(choices)
else:
  st.write('No player has submitted preference for upcoming match yet!')
                                                 
summary = []
success = []
for player in players:
  tempdoc_ref = db.collection("users").document(player)
  tempdoc = tempdoc_ref.get().to_dict()  
  vals = list(tempdoc.values())    

  successcount = 0
  for i in range(matches_played):
      idx = df_played[df_played['MatchId'] == "Match" + str(i+1)].index
      winner = df_played.iloc[idx]['Winner'].values[0]
      if tempdoc["Match"+ str(i +1)] == winner:
          successcount +=1
        
  tempdict = {"Player": player }  
  success.append( {"Player": player, "SuccessRate": successcount * 100/matches_played } )
  
  freq = {}
  for items in vals:
    freq[items] = vals.count(items)
    
  tempdict.update(freq)
  summary.append( tempdict )

pd.set_option("display.precision", 0)
summary = pd.DataFrame(summary)
success = pd.DataFrame(success)

df = summary.mean(axis = 0)
df.drop(labels= ["None"], inplace = True )
df.sort_values(ascending = False, inplace = True)
df = df *100/max(df)
df = df.to_frame(name = "Relative preference").reset_index()
df.rename(columns = {"index": "Team"}, inplace= True)

fig, ax = plt.subplots() 
ax = sns.barplot(x = 'Team', y = "Relative preference", data = df)
ax.set_title("Relative Team Preferences")
st.pyplot(fig)

fig, ax = plt.subplots(figsize= (12,3) )
ax = sns.barplot(y = 'Player', x = "SuccessRate", data = success)
ax.set_title("Prediction Success Rate(%)")
ax.set_xlim(0,100)
st.pyplot(fig)
