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

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("firestorekey.json")

# Get the current time to filter and get the relevant match as of now
tz_India = pytz.timezone('Asia/Calcutta') 
currtime = datetime.now(tz_India)

# Read the dataset containing information on MatchId, Team1, Team2 and match time as per preannounced schedule
df = pd.read_csv('IPLdata.csv', parse_dates= ['Time'])
s = pd.to_datetime(df['Time'])

# Need this to make the timestamp timezone aware else it causes error while comparing tz-aware and tz-naive types
df['Time1'] = s.dt.tz_localize('Asia/Calcutta')

# Pick all matches yet to be played and pick the first one for display
dftemp = df[df["Time1"] > currtime ]
row = dftemp.iloc[0]

# Present the user with information about playing teams and seek response
st.write( "Welcome! Please submit you response for ", row['Team1'], " v/s", row['Team2'], " match at ", row['Time'])

# Select user who wants to submit response. There could be more sophisticated setup with login/pwd, but keeping it simple for this example
players = ( 'Player 1', 'Player 2','Player 3')
user = st.selectbox( 'Please chose your login name', players )

team_selected = st.selectbox( 'Please chose your team', ( 'None', row['Team1'], row['Team2'] ))                                                  

# From the firestore client get the handle for the user
doc_ref = db.collection("users").document(user)
submit = st.button('Submit Response')

# If user clicks on submit response then store that selection as an update to existing dataset
if submit: 
  doc_ref.update( {row['MatchId']: team_selected } )
  st.write('Your response has been submitted, good luck!')


# Loop through all players data and show the current selection
st.write('Player preferences for upcoming match')
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
  st.write(choices)
                                                 

st.write('Player preferences historical summary')

summary = []
for player in players:
  tempdoc_ref = db.collection("users").document(player)
  tempdoc = tempdoc_ref.get()

  vals = list(tempdoc.to_dict().values())  
  tempdict = {"Player": player }
  freq = {}
  for items in vals:
    freq[items] = vals.count(items)
    
  tempdict.update(freq)
  summary.append( tempdict )

pd.set_option("display.precision", 0)
summary = pd.DataFrame(summary)
summary.fillna(0)
st.write(summary)
