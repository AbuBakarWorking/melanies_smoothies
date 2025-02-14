# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("My Parents New Healthy Diner")
st.subheader("Breakfast Menu")

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be", name_on_order)

# Get the current credentials
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# API request for watermelon data
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

# Check if the response is successful and parse the response
if smoothiefroot_response.status_code == 200:
    watermelon_data = smoothiefroot_response.json()  # Assuming the response is in JSON format
    st.write("Watermelon data:", watermelon_data)
else:
    st.write("Error fetching watermelon data. Status code:", smoothiefroot_response.status_code)

# Ingredient selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),  # Convert Snowflake DataFrame to pandas DataFrame and then to list
    max_selections=5   
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    
    my_insert_stmt = """ 
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
