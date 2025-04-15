import streamlit as st

st.title("📖 README")

st.write("This is the README page for the I-V and Time-Dependent Photocurrent Measurements app.")

# Read and display the README content
with open("README.md", "r") as f:
    readme_content = f.read()
    
st.markdown(readme_content)

