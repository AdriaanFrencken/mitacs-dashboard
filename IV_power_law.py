import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import get_colors, calculate_first_derivative
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

# Set page title
st.title('IV Curve Analysis')
st.caption('Created by: John Feng')

with st.sidebar:
    marker_size = st.slider('Marker size', min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider('Line width', min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    log_x = st.checkbox('Log x-axis', value=True)
    log_y = st.checkbox('Log y-axis', value=True)
    show_legend = st.checkbox('Show legend', value=True)
    show_power_law_fit = st.checkbox('Show power law fit', value=True)
    size_x = st.slider('Plot width', min_value=300, max_value=1200, value=800, step=50)
    size_y = st.slider('Plot height', min_value=300, max_value=1200, value=800, step=50)
    fontsize = st.slider('Axis font size', min_value=10, max_value=50, value=20, step=5)
    color_scheme = st.selectbox('Color scheme', ['Plotly', 'Set1', 'Set2', 'Set3', 'D3', 'G10', 'T10'])
    st.subheader('Plot labels:')
    # grid_spacing = st.slider('Grid spacing (V)', min_value=50, max_value=500, value=200, step=50)
    # y_grid_spacing = st.slider('Grid spacing (A)', min_value=50, max_value=500, value=200, step=50)


uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

# File uploader
if uploaded_files:
    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = get_colors(len(uploaded_files), color_scheme)
    container_1 = st.container()
    
    # Process each uploaded file
    for i, uploaded_file in enumerate(uploaded_files):
        # Read the CSV file
        df = pd.read_csv(uploaded_file, comment='#')
        # Filter for positive voltages
        df = df[df['Voltage (V)'] > 0]
        
        # Calculate first derivative and power law slope
        df = calculate_first_derivative(df)
        power_law_slope = np.gradient(np.log10(df['Current (A)']), np.log10(df['Voltage (V)']))
        
        with st.expander(f'Raw data for {uploaded_file.name}'):
            df['Current (nA)'] = df['Current (A)'] * 1e9
            df['Power Law Slope'] = power_law_slope
            st.write(df)
    
        file_name = uploaded_file.name.split('.')[0]
        with st.sidebar:
            plot_label = st.text_input(f'{file_name}', value=file_name)
        
        # Add IV curve trace on primary y-axis
        fig.add_trace(
            go.Scatter(
                x=df['Voltage (V)'], 
                y=df['Current (A)'],
                name=f"{plot_label} - IV", 
                mode='markers+lines',
                line=dict(width=line_width),
                marker=dict(symbol='circle', size=marker_size, color=colors[i])
            ),
            secondary_y=False
        )
        
        if show_power_law_fit:
            # Add power law slope trace on secondary y-axis
            fig.add_trace(
                go.Scatter(
                    x=df['Voltage (V)'],
                    y=power_law_slope,
                    name=f"{plot_label} - Slope",
                    mode='markers+lines',
                    line=dict(width=line_width, dash='dot'),
                    marker=dict(symbol='circle', size=marker_size, color=colors[i])
                ),
                secondary_y=True
            )

    # Update layout for better visualization
    fig.update_layout(
        showlegend=show_legend,
        legend_title_text='Curves',
        title='IV Curves and Power Law Slope',
        height=size_y,
        width=size_x,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.7,
            bgcolor='rgba(255, 255, 255, 0.8)',
            font=dict(size=0.8*fontsize)
        )
    )

    # Update x-axis
    fig.update_xaxes(
        title_text='Anode Voltage (V)',
        type='log' if log_x else 'linear',
        title_font=dict(size=fontsize),
        tickfont=dict(size=fontsize*0.8),
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgrey'
    )

    # Update primary y-axis (Current)
    fig.update_yaxes(
        title_text='Absolute Current (A)',
        type='log' if log_y else 'linear',
        title_font=dict(size=fontsize),
        tickfont=dict(size=fontsize*0.8),
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgrey',
        exponentformat='e',
        showexponent='all',
        secondary_y=False
    )

    if show_power_law_fit:
        # Update secondary y-axis (Power Law Slope)
        fig.update_yaxes(
            title_text='Power Law Slope (d log(I) / d log(V))',
            title_font=dict(size=fontsize),
            tickfont=dict(size=fontsize*0.8),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgrey',
            secondary_y=True
        )

    # Display the plot with full width
    with container_1:
        st.plotly_chart(fig, use_container_width=True, config={'responsive': True})

else:
    st.write("Please upload CSV files to begin analysis")

