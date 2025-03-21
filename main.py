import streamlit as st


pages = [st.Page('app_v1.py', title = 'I-t app v1'),
         st.Page('app_v2.py', title = 'I-t app v2'),
         st.Page('IV_app.py', title = 'IV app')]

page = st.navigation(pages)
page.run()
