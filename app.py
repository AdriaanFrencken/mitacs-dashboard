import streamlit as st



pages = [st.Page('app_v1.py', title = 'I-t app v1'),
        #  st.Page('app_v2.py', title = 'I-t app v2'),
         st.Page('IV_app.py', title = 'I-V Curve'),
         st.Page('app_leakage_current.py', title = 'Leakage Current Analysis'),
         st.Page('IV_power_law.py', title = 'I-V Power Law')]

page = st.navigation(pages)
page.run()
