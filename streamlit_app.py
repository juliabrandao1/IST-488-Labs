import streamlit as st

lab1_page = st.Page('Lab1.py', title='Lab 1', icon=':material/description:')
lab2_page = st.Page('Lab2.py', title='Lab 2', icon=':material/summarize:', default=True)

pg = st.navigation([lab1_page, lab2_page])
st.set_page_config(page_title='IST-488 Labs', page_icon=':material/school:')
pg.run()