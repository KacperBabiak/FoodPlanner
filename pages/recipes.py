import streamlit as st
import pandas as pd
from sqlalchemy.sql import text

 

st.set_page_config(
    page_title="Przepisy",
    page_icon="🗊",
)


conn = st.connection('food_planner_db', type='sql')
ingredients = conn.query('select * from ingredients',ttl=1)
ing_list= ingredients.name.to_list()
ing_list.sort()



st.write("Dodaj przepis")
meal_name = st.text_input("Nazwa")
meal_course = st.text_input("Posiłek")
options = st.multiselect(
    'Wybierz składniki',
    ing_list
    )


if st.button("Dodaj posiłek"):
    with conn.session as s:


        #s.execute(text('DROP TABLE recipes;'))
        #s.execute(text('DROP TABLE recipes_ing;'))
        s.execute(text('CREATE TABLE IF NOT EXISTS recipes (recipe_id INTEGER PRIMARY KEY, name TEXT, course TEXT,kcal INTEGER);'))
        s.execute(text('CREATE TABLE IF NOT EXISTS recipes_ing ( recipe INTEGER, ingredient INTEGER);'))
        s.execute(text('INSERT INTO recipes (name,course, kcal) VALUES (:name,:course, :kcal);').bindparams(name= meal_name,course= meal_course,kcal=0))
        
        for ingredient in options:
            s.execute(text('INSERT INTO recipes_ing (recipe, ingredient) VALUES (:rec,:ing);').bindparams(rec=meal_name,ing=ingredient))

        s.commit()
        st.rerun()
        
        

        


# Query and display the data you inserted


st.write("Lista przepisów")

df = conn.query('select * from recipes',ttl=1)
df2 = conn.query('select * from recipes_ing',ttl=1)
df['Ingredients'] = df.apply(lambda x: ', '.join(df2[df2.recipe==x['name']].ingredient.to_list()),axis=1)
st.table(df.drop("recipe_id",axis=1))
