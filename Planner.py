import streamlit as st
import datetime
import pandas as pd

st.set_page_config(
    page_title="Planer",
    page_icon="📅",
)

st.write("Planer jedzenia")

d_beg = st.date_input("Data początkowa", datetime.date(2023, 11, 9))
d_end = st.date_input("Data końcowa", datetime.date(2023, 11, 16))


df = pd.DataFrame()
edited_df = st.data_editor(df)


st.table(df)


