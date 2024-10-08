import pandas as pd
import streamlit as st
import numpy as np
import jdatetime
from datetime import datetime, timedelta
import itertools


# Page setting
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
category_list = ['All categories'] + merged_df['category'].unique().tolist()
selected_category = st.selectbox('Select Category', category_list)

if selected_category != 'All categories':
    filtered_df = merged_df[merged_df['category'] == selected_category]
else:
    filtered_df = merged_df

# -----
product_list = ['All products'] + filtered_df['DLP'].unique().tolist()
selected_product = st.selectbox('Select Product', product_list) 

if selected_category != 'All products':
    filtered_df = filtered_df[filtered_df['DLP'] == selected_product]

st.write(f'Selected Category: {selected_category} / selected Product: {selected_product}')

# Filter DataFrame by selected category

# ---- SECTION: Display Metrics in Three Rectangles ----
# Calculated summary based on filtered df of category and DLP
df_last_day = filtered_df[(filtered_df['gregorian_date'] >= last_day) | (filtered_df['gregorian_date'].isnull())]
df_last_week = filtered_df[(filtered_df['gregorian_date'] >= last_week) | (filtered_df['gregorian_date'].isnull())]
df_last_month = filtered_df[(filtered_df['gregorian_date'] >= last_month) | (filtered_df['gregorian_date'].isnull())]

# calculate total quantity per each time period
total_quantity_last_day = df_last_day['total_quantity'].sum()
total_quantity_last_week = df_last_week['total_quantity'].sum()
total_quantity_last_month = df_last_month['total_quantity'].sum()

# Create 3 columns for the metrics
col1, col2, col3 = st.columns(3)

# Display the metric for the last day
with col1:
    st.metric(label="Total Quantity (Last Day)", value=total_quantity_last_day)

# Display the metric for the last week
with col2:
    st.metric(label="Total Quantity (Last Week)", value=total_quantity_last_week)

# Display the metric for the last month
with col3:
    st.metric(label="Total Quantity (Last Month)", value=total_quantity_last_month)




# selecting color and store accordingly to the selected DLP
color_list = ['All colors'] + filtered_df['color'].unique().tolist()
store_list = ['All stores'] + filtered_df['store'].unique().tolist()

# Create two columns
col1, col2 = st.columns(2)
# Select box for stores in the first column
with col1:
    selected_store = st.selectbox('Select the Store', store_list)

# Select box for colors in the second column
with col2:
    selected_color = st.selectbox('Select the color', color_list)

# Display the selected values
st.write(f'Selected Store: {selected_store} / selected color: {selected_color}')



# Filter DataFrame by selected category
if selected_color != 'All colors':
    filtered_df = filtered_df[filtered_df['color'] == selected_color]

if selected_store != 'All store':
    filtered_df = filtered_df[filtered_df['store'] == selected_color]

