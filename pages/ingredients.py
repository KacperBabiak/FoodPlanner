import streamlit as st
import pandas as pd
from sqlalchemy.sql import text
import sqlalchemy




st.set_page_config(
    page_title="Składniki",
    page_icon="🍎",
)


conn = st.connection('food_planner_db', type='sql')



st.write("Dodaj skladnik")
ing_name = st.text_input("Nazwa")
ing_kcal = st.number_input("Kalorie na 100 gram")

if st.button("Dodaj składnik"):
    with conn.session as s:
        #s.execute(text('DROP TABLE ingredients;'))
        s.execute(text('CREATE TABLE IF NOT EXISTS ingredients (ing_id INTEGER PRIMARY KEY, name TEXT, kcal INTEGER);'))
        s.execute(text('INSERT INTO ingredients (name, kcal) VALUES (:name, :kcal);').bindparams(name=ing_name, kcal=ing_kcal))
        
        
        s.commit()
        st.rerun()
        #st.session_state['rerun_counter'] += 1
        

        


# Query and display the data you inserted


st.write("Lista składników")
#df = dbfunction(conn, st.session_state['rerun_counter'])
df = conn.query('select * from ingredients',ttl=1)
st.table(df.drop('ing_id',axis=1))



