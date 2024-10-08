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

if selected_product != 'All products':
    filtered_df = filtered_df[filtered_df['DLP'] == selected_product]

st.write(f'Selected Category: {selected_category} / selected Product: {selected_product}')

# Filter DataFrame by selected category

# ---- SECTION6: Display Metrics in Three Rectangles ----
# Calculated summary based on filtered df of category and DLP
df_last_day = filtered_df[(filtered_df['gregorian_date'] >= last_day) | (filtered_df['gregorian_date'].isnull())]
df_last_week = filtered_df[(filtered_df['gregorian_date'] >= last_week) | (filtered_df['gregorian_date'].isnull())]
df_last_month = filtered_df[(filtered_df['gregorian_date'] >= last_month) | (filtered_df['gregorian_date'].isnull())]

# calculate total quantity per each time period
total_quantity_last_day = int(df_last_day['total_quantity'].sum())
total_quantity_last_week = int(df_last_week['total_quantity'].sum())
total_quantity_last_month = int(df_last_month['total_quantity'].sum())

# ---- SECTION7: Display Metrics in Rounded Rectangles ----
# CSS styling for rounded rectangles
rounded_style = """
    <style>
        .rounded-rectangle {
            border: 2px solid #007BFF; /* Border color */
            border-radius: 15px; /* Rounded corners */
            padding: 20px; /* Padding inside the rectangle */
            margin: 10px; /* Margin outside the rectangle */
            background-color: #1b2933; /* Background color */
            text-align: center; /* Center text alignment */
            font-size: 20px; /* Font size */
            color: #f2f5f7; /* Font color - change this value to your desired color */
        }
    </style>
"""

# Injecting CSS into the Streamlit app
st.markdown(rounded_style, unsafe_allow_html=True)

# Create 3 columns for the metrics
col1, col2, col3 = st.columns(3)

# Display the metric for the last day in a rounded rectangle
with col1:
    st.markdown(f'<div class="rounded-rectangle">Total Quantity (Last Day): {total_quantity_last_day}</div>', unsafe_allow_html=True)

# Display the metric for the last week in a rounded rectangle
with col2:
    st.markdown(f'<div class="rounded-rectangle">Total Quantity (Last Week): {total_quantity_last_week}</div>', unsafe_allow_html=True)

# Display the metric for the last month in a rounded rectangle
with col3:
    st.markdown(f'<div class="rounded-rectangle">Total Quantity (Last Month): {total_quantity_last_month}</div>', unsafe_allow_html=True)



# Create 3 columns with empty space on both sides for centering the buttons
col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 2, 1, 2])

with col1:
    butt1 = st.button('1 Day Selection')
    if butt1:
        st.write("Selecting 1 day ago")
    else:
        st.write('Not Selecting 1 day ago')
        
with col2:
    butt2 = st.button('1 Week Selection')
    if butt2:
        st.write("Selecting 1 week ago")
    else:
        st.write('Not Selecting 1 week ago')

with col3:
    butt3 = st.button('1 Month Ago')
    if butt3:
        st.write("Selecting 1 month ago")
    else:
        st.write('Not Selecting 1 month ago')
        
with col4:
    butt3 = st.button('1 Month Ago')
    if butt3:
        st.write("Selecting 1 month ago")
    else:
        st.write('Not Selecting 1 month ago')
        
with col5:
    butt3 = st.button('1 Month Ago')
    if butt3:
        st.write("Selecting 1 month ago")
    else:
        st.write('Not Selecting 1 month ago')
        
with col6:
    butt3 = st.button('1 Month Ago')
    if butt3:
        st.write("Selecting 1 month ago")
    else:
        st.write('Not Selecting 1 month ago')


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

if selected_store != 'All stores':
    filtered_df = filtered_df[filtered_df['store'] == selected_store]


# ----- SECTION 8: caclculating essential metrics based on values selected in color, DLP, DLPC, and store
filtered_df = filtered_df.groupby(['DLP', 'DLPC', 'store', 'color']).agg({'total_quantity': 'sum', 'total_inventory': 'max'}).reset_index()
filtered_df['total_quantity'].fillna(0, inplace=True)
filtered_df['total_inventory'].fillna(0, inplace=True)

filtered_df['avg_demand'] = filtered_df['total_quantity'] / len(merged_df['date'].unique())
filtered_df['days_to_out_stock'] = np.ceil(filtered_df['total_inventory'] / filtered_df['avg_demand'])


filtered_df['short_term_reorder'] = np.ceil((filtered_df['avg_demand'] * 3) + (filtered_df['avg_demand'] * 5) / 2)
filtered_df['medium_term_reorder'] = np.ceil((filtered_df['avg_demand'] * 12) + (filtered_df['avg_demand'] * 15) / 2)
filtered_df['long_term_reorder'] = np.ceil((filtered_df['avg_demand'] * 21) + (filtered_df['avg_demand'] * 30) / 2)



final_table = filtered_df[['DLP', 'store', 'color', 'total_quantity', 'total_inventory', 'avg_demand', 'days_to_out_stock', 'short_term_reorder', 'medium_term_reorder', 'long_term_reorder']]
st.write(final_table)


# final_second = final_table.groupby(['DLP', 'store', 'color']).agg({'total_quantity': 'sum', 'total_inventory': 'sum', 'avg_demand': 'avg'}).reset_index()
# st.write(final_second)
