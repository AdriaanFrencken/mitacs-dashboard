import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
from utils import get_colors, find_pulse_start

st.set_page_config(layout="wide")

# Set page title
st.title('I-t Curve Analysis')
st.caption('Created by: John Feng')

with st.sidebar:
    align_pulse_start = st.checkbox('Align pulse start', value=True)
    if align_pulse_start:
        time_min, time_max = st.slider('Time range', min_value=-1.0, max_value=10.0, 
                                       value=(-0.2, 1.8), step=0.1)
    else:
        time_min, time_max = st.slider('Time range', min_value=-1.0, max_value=10.0, 
                                       value=(-0.2, 10.0), step=0.1)
        
    threshold_input = st.number_input('Pulse Start Threshold (nA)', min_value=1, max_value=10000, value=100)
    marker_size = st.slider('Marker size', min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider('Line width', min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    grid_spacing = st.slider('Grid spacing (seconds)', min_value=0.1, max_value=1.0, value=0.2, step=0.1)
    log_y = st.checkbox('Log y-axis', value=False)
    
    # Add color scheme selector
    color_scheme = st.selectbox(
        'Color scheme',
        ['Set1', 'Set2', 'Set3', 'D3', 'G10', 'T10', 'Plotly', 'Viridis', 'Plasma', 'Rainbow', 'Turbo'],
        index=0
    )

    x_legend_position = st.number_input('Legend position X', min_value=0.0, max_value=1.0, value=0.9, step=0.1)
    y_legend_position = st.number_input('Legend position Y', min_value=0.0, max_value=1.0, value=0.2, step=0.1)

    st.subheader('Plot labels:')


uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

# File uploader
if uploaded_files:
    # Create a figure for all curves
    fig = go.Figure()
    
    # Get color sequence based on selection
    n_files = len(uploaded_files)
    colors = get_colors(n_files, color_scheme)

    # Process each uploaded file
    for idx, uploaded_file in enumerate(uploaded_files):
        color_idx = idx % len(colors)  # Fallback in case we have more files than colors
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
                        line=dict(width=line_width, color=colors[color_idx]),
                        marker=dict(symbol='circle', size=marker_size, color=colors[color_idx]))

    # Update layout for better visualization
    fig.update_layout(
        showlegend=True,
        legend_title_text='File Name',
        xaxis_title='Time (s)',
        yaxis_title='Current (A)',
        title='I-t Curves for All Files',
        height=800,  # Make figure taller
        width=1200,  # Make figure wider

        # Add font settings for axis labels and ticks
        xaxis=dict(
            title_font=dict(size=20),  # Increase axis label font size
            tickfont=dict(size=16),    # Increase tick label font size
            showgrid=True,             # Show grid lines
            gridwidth=1,               # Grid line width
            gridcolor='lightgrey',     # Grid line color
            dtick=grid_spacing         # Grid line spacing
        ),
        yaxis=dict(
            title_font=dict(size=20),  # Increase axis label font size
            tickfont=dict(size=16),    # Increase tick label font size
            type='log' if log_y else 'linear',  # Toggle log scale based on checkbox
            showgrid=True,             # Show grid lines
            gridwidth=1,               # Grid line width
            gridcolor='lightgrey'      # Grid line color
        )
    )
    fig.update_layout(
        legend=dict(
            yanchor='bottom',
            y=y_legend_position,
            xanchor='right',
            x=x_legend_position,
            bgcolor='rgba(255, 255, 255, 0.8)',  # Semi-transparent white background
            font=dict(size=16)  # Increase legend font size
        )
    )

    # Display the plot with full width
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})
else:
    st.write("Please upload CSV files to begin analysis")