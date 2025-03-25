import streamlit as st

pages = [st.Page('I-t_app.py', title = 'I-t Photocurrent Plots'),
         st.Page('app_leakage_current.py', title = 'I-t Leakage Current Analysis'),
         st.Page('IV_app.py', title = 'I-V Curve Plots'),
         st.Page('IV_power_law.py', title = 'I-V Power Law Analysis')]

page = st.navigation(pages)
page.run()
