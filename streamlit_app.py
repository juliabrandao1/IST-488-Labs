import streamlit as st

st.markdown('# IST 488 Labs')
st.markdown('# Júlia Brandão')

lab1_page = st.Page('Lab1.py', title='Lab 1', icon=':material/description:')
lab2_page = st.Page('Lab2.py', title='Lab 2', icon=':material/summarize:')
lab3_page = st.Page('Lab3.py', title='Lab 3', icon=':material/chat:')
lab4_page = st.Page('Lab4.py', title='Lab 4', icon=':material/search:', default=True)

pg = st.navigation([lab1_page, lab2_page, lab3_page, lab4_page])
st.set_page_config(page_title='IST-488 Labs', page_icon=':material/school:')
pg.run()