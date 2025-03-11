import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide")

def find_pulse_start(df, threshold_current=1e-7):
    filter = df['Current (A)'] > threshold_current
    if filter.any():
        above_threshold_index = df[filter]
        pulse_start_index = above_threshold_index.index[0]
        if pulse_start_index == 0: # if the first index is 0, then the pulse start index is 0
            return 0, 0
        else:
            pulse_start_time = df.loc[pulse_start_index - 1, 'Time (s)']
            return pulse_start_index, pulse_start_time
    else: # if no index is above the threshold, then the pulse start index is 0
        return 0, 0

# Set page title
st.title('IV Curve Analysis')
st.caption('Created by: John Feng')

with st.sidebar:
    align_pulse_start = st.checkbox('Align pulse start', value=True)
    if align_pulse_start:
        time_min, time_max = st.slider('Time range', min_value=-1.0, max_value=10.0, 
                                       value=(-0.2, 1.8), step=0.1)
    else:
        time_min, time_max = st.slider('Time range', min_value=-1.0, max_value=10.0, 
                                       value=(-0.2, 10.0), step=0.1)
        
    threshold_input = st.number_input('Threshold current (nA)', min_value=1, max_value=10000, value=100)
    marker_size = st.slider('Marker size', min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider('Line width', min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    log_y = st.checkbox('Log y-axis', value=False)
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
        
        pulse_start_index, pulse_start_time = find_pulse_start(df, threshold_input*1e-9)
        with st.expander(f'Raw data for {uploaded_file.name}'):
            df['Current (nA)'] = df['Current (A)'] * 1e9
            st.write(f"Pulse start index: {pulse_start_index}, Pulse start time: {pulse_start_time}")
            st.write(df)
        # Align time to pulse start
        if align_pulse_start:
            df['Aligned_time (s)'] = df['Time (s)'] - pulse_start_time
        else:
            df['Aligned_time (s)'] = df['Time (s)']
        
        df_slice = df[(df['Aligned_time (s)'] >= time_min) & (df['Aligned_time (s)'] <= time_max)]
        
        file_name = uploaded_file.name.split('.')[0]
        with st.sidebar:
            plot_label = st.text_input(f'{file_name}', value=file_name)
        
        fig.add_scatter(x=df_slice['Aligned_time (s)'], y=df_slice['Current (A)'],
                        name=plot_label, mode='markers+lines', 
                        line=dict(width=line_width),
                        marker=dict(symbol='circle', size=marker_size))

    # Update layout for better visualization
    fig.update_layout(
        showlegend=True,
        legend_title_text='File Name',
        xaxis_title='Time (s)',
        yaxis_title='Current (A)',
        title='IV Curves for All Files',
        height=800,  # Make figure taller
        width=1200,  # Make figure wider
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.8)'  # Semi-transparent white background
        ),
        # Add font settings for axis labels and ticks
        xaxis=dict(
            title_font=dict(size=20),  # Increase axis label font size
            tickfont=dict(size=16)     # Increase tick label font size
        ),
        yaxis=dict(
            title_font=dict(size=20),  # Increase axis label font size
            tickfont=dict(size=16),    # Increase tick label font size
            type='log' if log_y else 'linear'  # Toggle log scale based on checkbox
        )
    )

    # Display the plot with full width
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
else:
    st.write("Please upload CSV files to begin analysis")
