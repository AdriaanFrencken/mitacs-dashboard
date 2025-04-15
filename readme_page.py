import streamlit as st

st.title("📖 README")

# Read and display the README content
with open("README.md", "r") as f:
    readme_content = f.read()

col1, col2 = st.columns(2)
with col1:
    st.image("ASSETS/WaferProber.png")
with col2:
    st.image("ASSETS/mitacs_dashboard.png")
st.write(readme_content)

