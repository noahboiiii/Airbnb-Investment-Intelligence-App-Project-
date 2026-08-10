# Import python packages
import streamlit as st
import os



# Write directly to the app
st.set_page_config(page_title="Airbnb Investment Intelligence App", layout="wide")
st.title(f"Airbnb Investment Intelligence App")
st.markdown("App to explore the market, compare locations, review property types, understand guest preferences and generate clear investment recommendations")

# st.sidebar.header()

st.sidebar.selectbox("Personas", 
                     ("High", "Low", "Medium")
)


## To be modified to be variable to the cities in the airbnb data
st.sidebar.selectbox("Cities", 
                     ("London", "Manchester", "Birmingham")
)

## Multi select (for boroughs and room types)
st.sidebar.multiselect("Boroughs",
                       ("Westminster", "Hayes", "Tower Hamlets")
)

## 
## Start value, end value, default
# st.select_slider("Price?", 0, 200, 25)

st.slider(
    "Price Range",
    min_value=0,
    max_value=600,
    value=(0, 200),
    step=100,
    format="$%d",
)

## Room type filter (home, private room, shared room, hotel room)
## Review Count filter (number of guest reviews)
## Availiable days in a calendar year
## Filters for bedrooms, bathrooms and beds if possible





## ----------------- Notes from default streamlit app ----------------------

# # Create a database connection to Snowflake
# conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
# session = conn.session()

# # Use an interactive slider to get user input
# hifives_val = st.slider(
#   "Number of high-fives in Q3",
#   min_value=0,
#   max_value=90,
#   value=60,
#   help="Use this to enter the number of high-fives you gave in Q3",
# )

# #  Create an example dataframe
# #  Note: this is just some dummy data, but you can easily connect to your Snowflake data
# #  It is also possible to query data using raw SQL using session.sql() e.g. session.sql("select * from table")
# created_dataframe = session.create_dataframe(
#   [[50, 25, "Q1"], [20, 35, "Q2"], [hifives_val, 30, "Q3"]],
#   schema=["HIGH_FIVES", "FIST_BUMPS", "QUARTER"],
# )

# # Execute the query and convert it into a Pandas dataframe
# queried_data = created_dataframe.to_pandas()

# # Create a simple bar chart
# # See docs.streamlit.io for more types of charts
# st.subheader("Number of high-fives")
# st.bar_chart(data=queried_data, x="QUARTER", y="HIGH_FIVES")

# st.subheader("Underlying data")
# st.dataframe(queried_data, use_container_width=True)
