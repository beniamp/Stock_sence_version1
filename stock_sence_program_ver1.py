import pandas as pd
import streamlit as st
import numpy as np
import jdatetime
from datetime import datetime, timedelta
import itertools


# Page setting
st.set_page_config(layout="wide")

st.set_page_config(
    page_title="Stock Sence-Koroush Khan",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inject custom CSS to style the select box
# Display various filtered and calculated data
st.markdown("""
    <style>
    .custom-box {
        padding: 20px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        font-size: 18px;
        color: #ffffff; /* White text color */
        margin-bottom: 10px; /* Space between the box and table */
    }
    .box-brown { background-color: #803400; }
    .box-red { background-color: #db2c12; }
    .box-yellow { background-color: #fae525; }
    .box-green { background-color: #1aba47; }
    .box-grey { background-color: #d6d6d6; }
    .box-brown2 { background-color: #cc7700; }
    .box-dark { background-color: #2f2959; }

    /* Make tables displayed by st.write() take the full width */
    table {
        width: 100% !important;
    }

    /* Optionally adjust padding and margins if necessary */
    th, td {
        padding: 10px; /* Adjust padding for table cells */
    }
    </style>
""", unsafe_allow_html=True)


# importing csv file into predestined dataframe
df = pd.read_csv('stock_sence_714.csv')


# ---- SECTION 1: DATE CONVERSION FUNCTION 

# function for conveting the jalali datetime values into gregorian
def jalali_to_gregorian(date):
    if isinstance(date, str):
        year, month, day = date.split("/")
        gregorian_date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        return gregorian_date
    else:
        return None

# defining new column as gregorian_date which is the the converted values of date column
df['gregorian_date'] = df["date"].apply(jalali_to_gregorian)



# ----- SECTION 2: CREATING DIMENSIONAL TABLE 

# creating a dimension table for better tracking the diversity of each store

unique_dim_items = df[['DLP', 'DLPC', 'name', 'code', 'color', 'category']].drop_duplicates()
stores_val = df['store'].drop_duplicates().tolist()

# performing acrtesian product combination for each stores
store_combination= pd.DataFrame(list(itertools.product(stores_val)), columns=['store'])

# creating a dimensional table consisting DLP, DLPC, name, code, color, store
dim_table = unique_dim_items.merge(store_combination, how='cross')


# ----- SECTION 3: joining the dimension table to the main (fact table; df) which contains the information of 
# -----            date, total_inventory, total_quantity



merged_df = df.merge(dim_table, on=['DLP', 'DLPC', 'name', 'code', 'category', 'store', 'color'], 
                     how='right').reset_index(drop=True)


# ----- SECTION 4: defining gregorian_date column, filtering out the date values into 3 time intervals (1day, 7day, 30days)

# converting the gregorian date to datetime
merged_df['gregorian_date'] = pd.to_datetime(merged_df['gregorian_date'], errors='coerce')

# assigning 4 time values for filtering 
today = merged_df['gregorian_date'].max()

last_day = today - timedelta(days=1)
last_week = today - timedelta(days=7)
last_month = today - timedelta(days=30)


# creating 3 major dataframe based on 3 defined time values
df_last_day = merged_df[(merged_df['gregorian_date'] >= last_day) | ( merged_df['gregorian_date'].isnull())]
df_last_week = merged_df[(merged_df['gregorian_date'] >= last_week) | ( merged_df['gregorian_date'].isnull())]
df_last_month = merged_df[(merged_df['gregorian_date'] >= last_month) | ( merged_df['gregorian_date'].isnull())]


# calculate total quantity per each time period
total_quantity_last_day = df_last_day['total_quantity'].sum()
total_quantity_last_week = df_last_week['total_quantity'].sum()
total_quantity_last_month = df_last_month['total_quantity'].sum()
total_quantity_overall = df['total_quantity'].sum()



# ----- SECTION 5: displayment to selection widget on DLP, DLPC, and stores unique values 

# Select box widget values, in order; DLP, store, DLPC
dlp_list = list(merged_df['DLP'].unique())
selected_dlp = st.selectbox('Select Product', dlp_list)  
st.write(selected_dlp)
