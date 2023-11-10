import streamlit as st
from datetime import date, timedelta
import pandas as pd
from sqlalchemy.sql import text

st.set_page_config(
    page_title="Planer",
    page_icon="📅",
    layout='wide'
)



st.write("Planer jedzenia")

d_beg = st.date_input("Data początkowa", date.today())
d_end = st.date_input("Data końcowa", date.today() + timedelta(days=5))
dates = pd.date_range(d_beg,d_end,freq='d')

conn = st.connection('food_planner_db', type='sql')
recipe_df = conn.query('select * from recipes',ttl=1)
recipe_ing = conn.query('select * from recipes_ing',ttl=1)

df_dict = {}
with conn.session as s:
        #s.execute(text('DROP TABLE meal_plan;'))
        s.execute(text('CREATE TABLE IF NOT EXISTS meal_plan (date TEXT PRIMARY KEY, meal1 TEXT DEFAULT "Nic", meal2 TEXT DEFAULT "Nic", meal3 TEXT DEFAULT "Nic", meal4 TEXT DEFAULT "Nic", meal5 TEXT DEFAULT "Nic");'))
        
        
        for date in dates.date:
            query = 'SELECT EXISTS(SELECT 1 FROM meal_plan WHERE date="20' + date.strftime("%y-%m-%d") + '");'
            check_date = conn.query(query,ttl=1)
            
            #jeśli data jest nowa to wyświetla domyślne i dodaje ją
            
            if(check_date.values[0][0]==0):
                df_dict[date] = ["Nic" for x in range(5)]
                s.execute(text('INSERT INTO meal_plan (date) VALUES (:date);').bindparams(date=date))
            else: #w innym wypadku pobiera z sql
                query = 'SELECT meal1,meal2,meal3,meal4,meal5 FROM meal_plan WHERE date="20' + date.strftime("%y-%m-%d") + '";'
                df = conn.query(query,ttl=1)
                df_dict[date] = df.values.tolist()[0]
        s.commit()



    
columns = ['Posiłek 1','Posiłek 2','Posiłek 3','Posiłek 4','Posiłek 5']
plan_df = pd.DataFrame.from_dict(df_dict,columns=columns,orient='index')
recipe_df['Ingredients'] = recipe_df.apply(lambda x: ', '.join(recipe_ing[recipe_ing.recipe==x['name']].ingredient.to_list()),axis=1)
     

col1, col2 = st.columns([2, 1])

col1.subheader("Plan")
edited_df = col1.data_editor(plan_df,
                 column_config={
                     "Posiłek 1":st.column_config.SelectboxColumn(
                        width="medium",
                        options = recipe_df[recipe_df.course=="Śniadanie"].name.to_list(),
                        required=True
                        ),
                    "Posiłek 2":st.column_config.SelectboxColumn(
                        width="medium",
                        options = recipe_df[(recipe_df.course=="Przekąska") | (recipe_df.course=="Śniadanie")].name.to_list(),
                        required=True
                        ),
                    "Posiłek 3":st.column_config.SelectboxColumn(
                        width="medium",
                        options = recipe_df[recipe_df.course=="Obiad"].name.to_list(),
                        required=True
                        ),
                    "Posiłek 4":st.column_config.SelectboxColumn(
                        width="medium",
                        options = recipe_df[(recipe_df.course=="Przekąska") | (recipe_df.course=="Śniadanie")].name.to_list(),
                        required=True
                        ),
                    "Posiłek 5":st.column_config.SelectboxColumn(
                        width="medium",
                        options = recipe_df[recipe_df.course=="Kolacja"].name.to_list(),
                        required=True
                        )
                 }
)


col2.subheader("Posiłki")
col2.dataframe(recipe_df.drop(['kcal','recipe_id'],axis=1),hide_index=True)

if st.button('Prześlij plan'):
    with conn.session as s:
        for index, row in edited_df.iterrows():
              s.execute(
                   text('UPDATE meal_plan \
                        SET meal1 = (:meal1), meal2 = :meal2, meal3 = :meal3, meal4 = :meal4, meal5 = :meal5 \
                        WHERE date = (:date) \
                        ;').bindparams(
                             date = '20' + index.strftime("%y-%m-%d"),
                             meal1 = row['Posiłek 1'],
                             meal2 = row['Posiłek 2'],
                             meal3 = row['Posiłek 3'],
                             meal4 = row['Posiłek 4'],
                             meal5 = row['Posiłek 5']))
              
              
        
        s.commit()
              
              


if st.button('Stwórz liste zakupów'):
     grocery_dict = {}
     set = set()
     for index, row in edited_df.iterrows():
        meal_list = [row[column] for column in edited_df.columns if row[column] != 'Nic']
        grocery_list=[]
        for meal in meal_list:
             grocery_list.append(recipe_df[recipe_df.name == meal].Ingredients.values[0])
        grocery_dict[index.strftime("%y-%m-%d")] = grocery_list

        for gr in grocery_list:
            for g in gr.split(', '):
                set.add(g)
        
         


     st.table(grocery_dict)
     st.text(set)


     






