# streamlit_app.py
from asyncio.windows_events import NULL
from xml.etree.ElementTree import tostring
import streamlit as st
from gsheetsdb import connect
import pandas as pd
from IPython.core.display import display, HTML
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml import Loader, Dumper

st.set_page_config(page_title="Dashboard PPGT Galaxi", layout="wide")

# Create a connection object.
conn = connect()

# Perform SQL query on the Google Sheet.
queryy = "SELECT `Nama Lengkap`, `Jenis Kelamin`, `Tempat Lahir`, `Tanggal Lahir (format: BULAN/TANGGAL/TAHUN)`, `Golongan Darah`, `Alamat Sekarang (domisili lengkap)`, `Nomor Handphone` "

def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["public_gsheets_url"]
rows = run_query( 
    f' {queryy} FROM "{sheet_url}"'
    # f'SELECT *  FROM "{sheet_url}"'
)

# AUTHENTICATION
with open('config.yaml') as file:
    config = yaml.load(file, Loader=Loader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login("PPGT Galaxi", "main")
if(authentication_status == False):
    st.error("Username/password is incorrect")
if(authentication_status):
    df = pd.DataFrame(
            rows,
        )
    df.index = df.index + 1
    df.rename(columns={
        '_3':'Tanggal_Lahir',
        '_5':'Alamat'
    }, inplace=True)

    df['Nama_Lengkap'] = df['Nama_Lengkap'].str.title()
    df['Tempat_Lahir'] = df['Tempat_Lahir'].str.title()
    #convert date
    df['Tanggal_Lahir'] = pd.to_datetime(df['Tanggal_Lahir']) # convert date to datetime
    test = df['Tanggal_Lahir'].dt.strftime('%Y')
    df['Tanggal_Lahir'] = df['Tanggal_Lahir'].dt.strftime('%d %B %Y') #convert datetime to custom time


    df["Nomor_Handphone"] = "62"+ df["Nomor_Handphone"]

    df["Nomor_Handphone"] = df["Nomor_Handphone"].apply(lambda x: f'<a href=https://api.whatsapp.com/send/?phone={x}&text&type=phone_number&app_absent=0>{x}</a>')
    

    # SIDEBAR #
    user_input = st.sidebar.text_input("",placeholder='Search by name')
    st.sidebar.header("Filters")
    genderFilter = st.sidebar.multiselect(
        "Filter by Gender:",
        options=df['Jenis_Kelamin'].unique(),
        # default=df['Jenis_Kelamin'].unique()
    )
    birthyearFilter = st.sidebar.multiselect(
        "Filter by Birthyear:",
        options=(test).unique(),
        # default=(test).unique()
    )
    bloodtypeFilter = st.sidebar.multiselect(
        "Filter by Blood Type:",
        options=df['Golongan_Darah'].unique(),
        # default=df['Golongan_Darah'].unique()
    )
    authenticator.logout('Logout', 'sidebar')

    # Print results.
    title_container = st.container()
    col1, col2 = st.columns([2,15])
    with title_container:
        with col1:
            st.image("ppgt.png", width=100)
        with col2:
            st.title("Database PPGT Galaxi")

    if(user_input or genderFilter or birthyearFilter or bloodtypeFilter or
    (user_input and genderFilter) or (genderFilter and birthyearFilter) or 
    (user_input and genderFilter and birthyearFilter) or (user_input and bloodtypeFilter) or (bloodtypeFilter and genderFilter) or
    (bloodtypeFilter and birthyearFilter) or (bloodtypeFilter and birthyearFilter and genderFilter) or (bloodtypeFilter and birthyearFilter and genderFilter and user_input)):
        if(user_input):
            queryy = df.query(f"Nama_Lengkap.str.contains('{user_input}', case=False)").reset_index(drop=True)
        if(genderFilter):
            queryy = df.query(f"Jenis_Kelamin == @genderFilter").reset_index(drop=True)
        if(birthyearFilter):
            year = '|'.join(str(x) for x in birthyearFilter)
            queryy = df.query(f"Tanggal_Lahir.str.contains('{year}')").reset_index(drop=True)
        if(bloodtypeFilter):
            queryy = df.query(f"Golongan_Darah == @bloodtypeFilter").reset_index(drop=True)
        if(user_input and genderFilter):
            queryy = df.query(f"Nama_Lengkap.str.contains('{user_input}', case=False) & Jenis_Kelamin == @genderFilter").reset_index(drop=True)
        if(genderFilter and birthyearFilter):
            year = '|'.join(str(x) for x in birthyearFilter)
            queryy = df.query(f"Tanggal_Lahir.str.contains('{year}') & Jenis_Kelamin == @genderFilter").reset_index(drop=True)
        if(user_input and genderFilter and birthyearFilter):
            year = '|'.join(str(x) for x in birthyearFilter)
            queryy = df.query(f"Nama_Lengkap.str.contains('{user_input}', case=False) & Tanggal_Lahir.str.contains('{year}') & Jenis_Kelamin == @genderFilter").reset_index(drop=True)
        if(user_input and bloodtypeFilter):
            queryy = df.query(f"Nama_Lengkap.str.contains('{user_input}', case=False) & Golongan_Darah == @bloodtypeFilter").reset_index(drop=True)
        if(bloodtypeFilter and genderFilter):
            queryy = df.query(f"Golongan_Darah == @bloodtypeFilter & Jenis_Kelamin == @genderFilter").reset_index(drop=True)
        if(bloodtypeFilter and birthyearFilter):
            year = '|'.join(str(x) for x in birthyearFilter)
            queryy = df.query(f"Golongan_Darah == @bloodtypeFilter & Tanggal_Lahir.str.contains('{year}')").reset_index(drop=True)
        if(bloodtypeFilter and birthyearFilter and genderFilter):
            year = '|'.join(str(x) for x in birthyearFilter)
            queryy = df.query(f"Golongan_Darah == @bloodtypeFilter & Tanggal_Lahir.str.contains('{year}') & Jenis_Kelamin == @genderFilter").reset_index(drop=True)
        if(bloodtypeFilter and birthyearFilter and genderFilter and user_input):
            year = '|'.join(str(x) for x in birthyearFilter)
            queryy = df.query(f"Golongan_Darah == @bloodtypeFilter & Tanggal_Lahir.str.contains('{year}') & Jenis_Kelamin == @genderFilter & Nama_Lengkap.str.contains('{user_input}', case=False)").reset_index(drop=True)
        queryy.index = queryy.index + 1
        if(queryy.empty):
            st.subheader("No Data")
        else:
            st.subheader(f'Total: {queryy.count().values[0]}')
            st.write(queryy.to_html(escape=False, index=False, classes='table table-striped text-center', justify='center', col_space=200), unsafe_allow_html=True)
    else:
        if(df.empty):
            st.subheader("No Data")
        else:
            st.subheader(f'Total: {df.count().values[0]}')
            st.write(df.to_html(escape=False, index=False, classes='table table-striped text-center',justify='center', col_space=200, columns=['Nama_Lengkap', 'Tanggal_Lahir', 'Alamat', 'Nomor_Handphone']), unsafe_allow_html=True)


