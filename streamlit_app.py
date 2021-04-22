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

tz_India = pytz.timezone('Asia/Calcutta') 
currtime = datetime.now(tz_India)

df = pd.read_csv('IPLdata.csv', parse_dates= ['Time'])
s = pd.to_datetime(df['Time'])
df['Time1'] = s.dt.tz_localize('Asia/Calcutta')
dftemp = df[df["Time1"] > currtime ]
row = dftemp.iloc[0]
print(row['Team1'])

st.write( "Welcome! Please submit you response for ", row['Team1'], " v/s", row['Team2'], " match at ", row['Time'])

players = ( 'Bot', 'Chetan', 'Rajat', 'Sethu', 'Shivam', 'Havish', 'Utsav', 'Kshitiz' , 'Rajesh' )
user = st.selectbox( 'Please chose your login name', players )

team_selected = st.selectbox( 'Please chose your team', ( 'None', row['Team1'], row['Team2'] ))                                                  

doc_ref = db.collection("users").document(user)
submit = st.button('Submit Response')

if submit: 
  doc_ref.update( {row['MatchId']: team_selected } )
  st.write('Your response has been submitted, good luck!')

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
                                                 

# st.write('Hold on, generating a summary')

# summary = []
# for player in players:
#   tempdoc_ref = db.collection("users").document(player)
#   tempdoc = tempdoc_ref.get()

#   vals = list(tempdoc.to_dict().values())  
#   tempdict = {"Player": player }
#   freq = {}
#   for items in vals:
#     freq[items] = vals.count(items)
    
#   tempdict.update(freq)
#   summary.append( tempdict )

# pd.set_option("display.precision", 0)
# summary = pd.DataFrame(summary)
# st.write(summary)
