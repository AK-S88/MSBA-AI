# Streamlit app placeholder
import streamlit as st
st.title('UML Business Analytics Assistant')
query = st.text_input('Ask me anything about UML BA program')
if query:
    st.write('Processing...')
