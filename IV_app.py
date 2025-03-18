import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide")

# Set page title
st.title('I-t Curve Analysis')
st.caption('Created by: John Feng')

with st.sidebar:
    marker_size = st.slider('Marker size', min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider('Line width', min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    grid_spacing = st.slider('Grid spacing (V)', min_value=50, max_value=500, value=200, step=50)
    log_x = st.checkbox('Log x-axis', value=False)
    log_y = st.checkbox('Log y-axis', value=False)
    size_x = st.slider('Plot width', min_value=300, max_value=1200, value=800, step=50)
    size_y = st.slider('Plot height', min_value=300, max_value=1200, value=800, step=50)
    fontsize = st.slider('Axis font size', min_value=10, max_value=50, value=20, step=5)
    st.subheader('Plot labels:')


uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

# File uploader
if uploaded_files:
    # Create a figure for all curves
    fig = go.Figure()

    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Read the CSV file
        df = pd.read_csv(uploaded_file, comment='#')

        with st.expander(f'Raw data for {uploaded_file.name}'):
            df['Current (nA)'] = df['Current (A)'] * 1e9
            st.write(df)
        # Align time to pulse start
        file_name = uploaded_file.name.split('.')[0]
        with st.sidebar:
            plot_label = st.text_input(f'{file_name}', value=file_name)
        
        fig.add_scatter(x=df['Voltage (V)'], y=df['Current (A)'],
                        name=plot_label, mode='markers+lines', 
                        line=dict(width=line_width),
                        marker=dict(symbol='circle', size=marker_size))

    # Update layout for better visualization
    fig.update_layout(
        showlegend=True,
        legend_title_text='File Name',
        xaxis_title='Voltage (V)',
        yaxis_title='Current (A)',
        title='IV Curves for All Files',
        height=size_y,  # Make figure taller
        width=size_x,  # Make figure wider
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.8)',  # Semi-transparent white background
            font=dict(size=0.8*fontsize)  # Legend font size
        ),
        # Add font settings for axis labels and ticks
        xaxis=dict(
            title_font=dict(size=fontsize),  # Increase axis label font size
            tickfont=dict(size=fontsize*0.8),    # Increase tick label font size
            type='log' if log_x else 'linear',  # Toggle log scale based on checkbox
            showgrid=True,             # Show grid lines
            gridwidth=1,               # Grid line width
            gridcolor='lightgrey',     # Grid line color
            dtick=grid_spacing         # Grid line spacing
        ),
        yaxis=dict(
            title_font=dict(size=fontsize),  # Increase axis label font size
            tickfont=dict(size=fontsize*0.8),    # Increase tick label font size
            type='log' if log_y else 'linear',  # Toggle log scale based on checkbox
            showgrid=True,             # Show grid lines
            gridwidth=1,               # Grid line width
            gridcolor='lightgrey'      # Grid line color
        )
    )

    # Display the plot with full width
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
else:
    st.write("Please upload CSV files to begin analysis")
