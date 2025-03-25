import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils import get_colors, calculate_first_derivative

st.set_page_config(layout="wide")

# Set page title
st.title("IV Curve Analysis")
st.caption("Created by: John Feng")

with st.sidebar:
    marker_size = st.slider("Marker size", min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider(
        "Line width", min_value=0.5, max_value=5.0, value=1.0, step=0.5
    )
    log_x = st.checkbox("Log x-axis", value=False)
    log_y = st.checkbox("Log y-axis", value=True)
    show_legend = st.checkbox("Show legend", value=True)
    only_positive_voltage = st.checkbox("Voltage > 0", value=False)
    only_negative_voltage = st.checkbox("Voltage < 0", value=False)
    size_x = st.slider("Plot width", min_value=300, max_value=1200, value=800, step=50)
    size_y = st.slider("Plot height", min_value=300, max_value=1200, value=800, step=50)
    fontsize = st.slider("Axis font size", min_value=10, max_value=50, value=20, step=5)
    color_scheme = st.selectbox(
        "Color scheme", ["Plotly", "Set1", "Set2", "Set3", "D3", "G10", "T10"]
    )
    st.subheader("Plot labels:")
    # grid_spacing = st.slider('Grid spacing (V)', min_value=50, max_value=500, value=200, step=50)
    # y_grid_spacing = st.slider('Grid spacing (A)', min_value=50, max_value=500, value=200, step=50)

container_1 = st.container()  # for IV curves

uploaded_files = st.file_uploader(
    "Upload CSV files", type=["csv"], accept_multiple_files=True
)

df_bar_chart = pd.DataFrame()

# File uploader
if uploaded_files:
    # Create a figure for all curves
    fig = go.Figure()

    colors = get_colors(len(uploaded_files), color_scheme)
    # container_1 = st.container()
    # Process each uploaded file
    for i, uploaded_file in enumerate(uploaded_files):
        # Read the CSV file
        df = pd.read_csv(uploaded_file, comment="#")
        # Calculate first derivative
        df = calculate_first_derivative(df)

        # with st.expander(f'Raw data for {uploaded_file.name}'):
        #     df['Current (nA)'] = df['Current (A)'] * 1e9
        #     st.write(df)
        current_at_1000V = df[df["Voltage (V)"] == 1000]["Current (A)"]
        df_bar_chart = pd.concat(
            [
                df_bar_chart,
                pd.DataFrame(
                    {
                        "Index": [i],
                        "File Name": uploaded_file.name,
                        "Device ID": df["Device ID"].iloc[0],
                        "Contact ID": df["Contact ID"].iloc[0],
                        "Current at 1000V": current_at_1000V,
                        "Color": colors[i],
                    }
                ),
            ]
        )

        if only_positive_voltage:
            df = df[df["Voltage (V)"] > 0]
        elif only_negative_voltage:
            df = df[df["Voltage (V)"] < 0]
        # Align time to pulse start
        file_name = uploaded_file.name.split(".")[0]
        with st.sidebar:
            plot_label = st.text_input(f"{file_name}", value=file_name)

        fig.add_scatter(
            x=df["Voltage (V)"],
            y=df["Current (A)"],
            name=plot_label,
            mode="markers+lines",
            line=dict(width=line_width),
            marker=dict(symbol="circle", size=marker_size, color=colors[i]),
        )

    # Update layout for better visualization
    fig.update_layout(
        showlegend=show_legend,
        legend_title_text="File Name",
        xaxis_title="Anode Voltage (V)",
        yaxis_title="Absolute Current (A)",
        title="IV Curves for All Files",
        height=size_y,  # Make figure taller
        width=size_x,  # Make figure wider
        legend=dict(
            yanchor="bottom",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.8)",  # Semi-transparent white background
            font=dict(size=0.8 * fontsize),  # Legend font size
        ),
        # Add font settings for axis labels and ticks
        xaxis=dict(
            title_font=dict(size=fontsize),  # Increase axis label font size
            tickfont=dict(size=fontsize * 0.8),  # Increase tick label font size
            type="log" if log_x else "linear",  # Toggle log scale based on checkbox
            showgrid=True,  # Show grid lines
            gridwidth=1,  # Grid line width
            gridcolor="lightgrey",  # Grid line color
            # dtick=grid_spacing         # Grid line spacing
        ),
        yaxis=dict(
            title_font=dict(size=fontsize),  # Increase axis label font size
            tickfont=dict(size=fontsize * 0.8),  # Increase tick label font size
            type="log" if log_y else "linear",  # Toggle log scale based on checkbox
            showgrid=True,  # Show grid lines
            gridwidth=1,  # Grid line width
            gridcolor="lightgrey",  # Grid line color
            # dtick=y_grid_spacing,
            exponentformat="e",
            showexponent="all",  # Grid line spacing
        ),
    )

    # Display the plot with full width
    with container_1:
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    # with st.expander("Current at 1000V"):
    #     st.write(df_bar_chart)

    fig_bar = px.bar(
        df_bar_chart,
        x="Index",
        y="Current at 1000V",
        color="Device ID",
        color_discrete_map=dict(zip(df_bar_chart["Device ID"], df_bar_chart["Color"])),
    )
    
    fig_bar.update_layout(
        title="Dark Current at 1000V",
        height=size_y,  # Make figure taller
        width=size_x,  # Make figure wider
        showlegend=True,
        legend=dict(
            yanchor="bottom",
            y=0.99,
            xanchor="right", 
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.8)",
            font=dict(size=0.8 * fontsize),
        ),

        yaxis=dict(
            type="log",  # Set y-axis to logarithmic scale
            exponentformat="e",  # Use scientific notation
            showexponent="all",  # Show exponent for all numbers
            tickfont=dict(size=fontsize * 0.8),  # Increase tick label font size
            title_font=dict(size=fontsize),  # Increase axis label font size
        ),
        xaxis=dict(
            title_font=dict(size=fontsize),  # Increase axis label font size
            tickfont=dict(size=fontsize * 0.8),  # Increase tick label font size
        ),
    )
    with st.expander("Bar Chart of Dark Current at 1000V"):
        st.plotly_chart(fig_bar, use_container_width=True, config={"responsive": True})


else:
    st.write("Please upload CSV files to begin analysis")
