import numpy as np 
import pandas as pd 
import streamlit as st 
import time 
from streamlit_elements import elements, mui, html
from streamlit_elements import lazy
from streamlit_elements import sync
from streamlit_elements import dashboard
import asdf 
from astropy.io import fits
from observing_suite import Target,ObservingPlan
import astropy.units as u 
import plotly.express as px 
from astropy.io import fits
from astropy.time import Time 
import numpy as np 
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, get_sun, get_moon
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from matplotlib import dates
from matplotlib.dates import HourLocator,MinuteLocator
import pandas as pd
from photutils.aperture import SkyRectangularAperture, SkyCircularAperture
import os
from datetime import datetime,timedelta

import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title('Observing-Suite Viewer')


from setup_viewer import plan 

if 'date' not in st.session_state.keys():
    st.session_state.date = datetime.today().strftime('%Y-%m-%d')
if 'targetname' not in st.session_state.keys():
    st.session_state.targetname = plan.targetlist[0].name
if 'time_show' not in st.session_state.keys():
    st.session_state.time_show = 'UTC'

if 'config' not in st.session_state.keys():
    st.session_state.config = list(plan.targetlist[0].configs.keys())[0]
if 'plan' not in st.session_state.keys():
    st.session_state.plan = plan

today = datetime.today()

# with st.sidebar:
#     uploaded_file = st.file_uploader("Choose a file")
#     if uploaded_file is not None:
#         plan = asdf.open(uploaded_file).tree



col1, col2, col3= st.columns([1,1, 2])
with col1:
    st.session_state.date = st.date_input('Select Date',today+timedelta(days=1)).strftime('%Y-%m-%d')
with col2:
    st.session_state.time_show = st.selectbox('Show Times In',options=['UTC','Observatory TZ'])
with col3:
    st.session_state.targetname = st.multiselect("Choose Target(s)",default=list(plan.dict.keys()), options=list(plan.dict.keys()), key=2)
# with col4:
#     st.session_state.config = st.selectbox("Choose Configuration", options=list(plan.dict[st.session_state.targetname].configs.keys()), key=3)



midnight = midnight = Time(f'{st.session_state.date} 00:00:00') - plan.utcoffset*u.hour
delta_midnight = np.linspace(-12, 12, 400)*u.hour
obs_times = midnight+delta_midnight

frame = AltAz(obstime=obs_times,location=plan.obsloc)
moon = get_moon(obs_times).transform_to(frame)
sun = get_sun(obs_times).transform_to(frame)
sunset = obs_times[sun.alt.to(u.deg) < -0*u.deg][0]
sunrise = obs_times[sun.alt.to(u.deg) < -0*u.deg][-1]
mask1 = sun.alt.to(u.deg) < -0*u.deg
mask2 = sun.alt.to(u.deg) < -12*u.deg
mask3 = sun.alt.to(u.deg) < -18*u.deg


if st.session_state.time_show == 'Observatory TZ':
    x = obs_times + plan.utcoffset*u.hr
    x = x.to_datetime()
    sunset=(sunset+st.session_state.plan.utcoffset*u.hr).to_datetime()
    sunrise=(sunrise+st.session_state.plan.utcoffset*u.hr).to_datetime()
else:
    x = obs_times.to_datetime()
    sunset= sunset.to_datetime()
    sunrise=sunrise.to_datetime()
cols = st.columns([1,1,2])
with cols[0]:
    st.metric('Sunset',sunset.strftime('%H:%M:%S'),delta=sunset.strftime('%Y-%m-%d'))
with cols[1]:
    st.metric('Sunrise',sunrise.strftime('%H:%M:%S'),delta=sunrise.strftime('%Y-%m-%d'))
fig = go.Figure()
fig.add_trace(go.Scatter(x=x[mask1], y=[0]*len(obs_times.to_datetime()[mask1]),
    fill=None,
    mode='lines',
    line_color='lightgrey',
    name=None,showlegend=False,
    ))
fig.add_trace(go.Scatter(
    x=x[mask1],
    y=[90]*len(obs_times.to_datetime()[mask1]),
    fill='tonexty', # fill area between trace0 and trace1
    mode='lines', line_color='lightgrey',name=' Sun < 0 deg'))


fig.add_trace(go.Scatter(x=x[mask2], y=[0]*len(obs_times.to_datetime()[mask2]),
    fill=None,
    mode='lines',
    line_color='grey',
    name=None,showlegend=False,
    ))
fig.add_trace(go.Scatter(
    x=x[mask2],
    y=[90]*len(obs_times.to_datetime()[mask2]),
    fill='tonexty', # fill area between trace0 and trace1
    mode='lines', line_color='grey',name=' Sun < 12 deg'))


fig.add_trace(go.Scatter(x=x[mask3], y=[0]*len(obs_times.to_datetime()[mask3]),
    fill=None,
    mode='lines',
    line_color='rgba(0, 0, 55, 1)',showlegend=False,
    ))
fig.add_trace(go.Scatter(
    x=x[mask3],
    y=[90]*len(obs_times.to_datetime()[mask3]),
    fill='tonexty', # fill area between trace0 and trace1
    mode='lines', line_color='rgba(0, 0, 55, 1)',name=' Sun < 18 deg'))



for i in st.session_state.targetname:
    fig.add_trace(go.Scatter(x=x, y=plan.dict[i].coordinates.transform_to(frame).alt,name=i))


fig.add_trace(go.Scatter(x=x,y=moon.alt,name='Moon',line=dict(color='royalblue', width=4, dash='dot')),)

current_time = datetime.utcnow()
if st.session_state.time_show == 'UTC':
    current_time = current_time 
else:
    current_time = (Time(current_time) + plan.utcoffset*u.hr).to_datetime()
fig.add_vline(x=current_time, line_width=3, line_dash="dash", line_color="red")

fig.update_layout(yaxis_range=[0,90],height=700,)

st.plotly_chart(fig, use_container_width=True,)

reload = st.button('Update Time')
if reload:
    st.experimental_rerun()