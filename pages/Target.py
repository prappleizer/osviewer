import numpy as np 
import pandas as pd 
import streamlit as st 
import streamlit_echarts
from streamlit_elements import elements, mui, html
from streamlit_elements import lazy
from streamlit_elements import sync
from streamlit_extras import add_vertical_space as avs
from datetime import datetime
from astropy.time import Time 
import astropy.units as u 
from astropy.coordinates import AltAz
from astropy.coordinates import SkyCoord, get_sun, get_moon

if 'selected_target' not in st.session_state.keys():
    st.session_state.selected_target = list(st.session_state.plan.dict.keys())[0]




with st.sidebar:
    st.session_state.selected_target = st.selectbox('Choose Target',options=st.session_state.plan.dict.keys(),key=4)
    st.session_state.config = st.selectbox("Choose Configuration", options=list(st.session_state.plan.dict[st.session_state.selected_target].configs.keys()), key=3)

avs.add_vertical_space(2)
st.title(f'Target Overview: {st.session_state.selected_target}')

colbig1,colbig2 = st.columns([1,1])
with colbig1:
    target_coord = st.session_state.plan.dict[st.session_state.selected_target].coordinates.to_string('hmsdms',sep=' ')
    st.metric('Target Coordinates',target_coord)
    st.header('Rise and Set times')
    col1,col2,col3 = st.columns([1,1,1])
    with col1:
        today=datetime.today()
        st.session_state.date = st.date_input('Select Date',today).strftime('%Y-%m-%d')
    with col2:
        st.session_state.time_show = st.selectbox('Show Times In',options=['UTC','Observatory TZ'])
    with col3:
        alt_compare = st.number_input('Rise/Set Altitude to use',0,89)

    midnight = midnight = Time(f'{st.session_state.date} 00:00:00') - st.session_state.plan.utcoffset*u.hour
    delta_midnight = np.linspace(-12, 12, 400)*u.hour
    obs_times = midnight+delta_midnight

    frame = AltAz(obstime=obs_times,location=st.session_state.plan.obsloc)
    moon = get_moon(obs_times).transform_to(frame)
    sun = get_sun(obs_times).transform_to(frame)
    mask1 = sun.alt.to(u.deg) < -0*u.deg
    mask2 = sun.alt.to(u.deg) < -12*u.deg
    mask3 = sun.alt.to(u.deg) < -18*u.deg
    sunset = obs_times[sun.alt.to(u.deg) < -0*u.deg][0]
    sunrise = obs_times[sun.alt.to(u.deg) < -0*u.deg][-1]
    target_alt = st.session_state.plan.dict[st.session_state.selected_target].coordinates.transform_to(frame).alt
    ind, = np.where((target_alt>alt_compare*u.deg)&(obs_times.to_datetime()>sunset)&(obs_times.to_datetime()<sunrise))
    #set_ind, = np.where(target_alt>alt_compare*u.deg)
    rise_time = obs_times[ind[0]]
    set_time = obs_times[ind[-1]]
    
    if st.session_state.time_show != 'UTC':
        rise_time = (rise_time + st.session_state.plan.utcoffset*u.hr).to_datetime()
        set_time = (set_time + st.session_state.plan.utcoffset*u.hr).to_datetime()
        sunset=(sunset+st.session_state.plan.utcoffset*u.hr).to_datetime()
        sunrise=(sunrise+st.session_state.plan.utcoffset*u.hr).to_datetime()
    else:
        rise_time = rise_time.to_datetime()
        set_time=set_time.to_datetime()
        sunset= sunset.to_datetime()
        sunrise=sunrise.to_datetime()

    col1,col2,col3,col4 = st.columns([1,1,1,1])
    with col1:
        st.metric('Target Rise Time',rise_time.strftime('%H:%M:%S'),delta=rise_time.strftime('%Y-%m-%d'))
    with col2:
        st.metric('Target Set Time',set_time.strftime('%H:%M:%S'),delta=set_time.strftime('%Y-%m-%d'))
    with col3:
        st.metric('Sunset',sunset.strftime('%H:%M:%S'),delta=sunset.strftime('%Y-%m-%d'))
    with col4:
        st.metric('Sunrise',sunrise.strftime('%H:%M:%S'),delta=sunrise.strftime('%Y-%m-%d'))
with colbig2:
    config_coord = st.session_state.plan.dict[st.session_state.selected_target].configs[st.session_state.config]['coordinates'].to_string('hmsdms',sep=' ')
    if config_coord == target_coord:
        delt = 'Same as Target'
    else:
        delt = 'Different from Target'
    st.metric('Configuration Coordinates',config_coord,delta=delt)
    st.header('Configurations Summary')
    st.dataframe(st.session_state.plan.dict[st.session_state.selected_target].configurations)


    