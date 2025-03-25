import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
from utils import get_colors, find_pulse_start, data_extractor, extract_filename

st.set_page_config(layout="wide")

# Set page title
st.title("I-t Curve Analysis")
st.caption("Created by: John Feng")


with st.sidebar:
    align_pulse_start = st.checkbox("Align pulse start", value=True)
    if align_pulse_start:
        time_min, time_max = st.slider(
            "Time range", min_value=-1.0, max_value=10.0, value=(-0.2, 1.8), step=0.1
        )
    else:
        time_min, time_max = st.slider(
            "Time range", min_value=-1.0, max_value=10.0, value=(-0.2, 10.0), step=0.1
        )

    threshold_input = st.number_input(
        "Pulse Start Threshold (nA)", min_value=1, max_value=10000, value=2000
    )
    marker_size = st.slider("Marker size", min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider(
        "Line width", min_value=0.5, max_value=5.0, value=1.0, step=0.5
    )
    grid_spacing = st.slider(
        "Grid spacing (seconds)", min_value=0.1, max_value=1.0, value=0.2, step=0.1
    )
    log_y = st.checkbox("Log y-axis", value=False)
    log_x = st.checkbox("Log x-axis", value=False)

    # Add color scheme selector
    color_scheme = st.selectbox(
        "Color scheme",
        [
            "Plotly",
            "Set1",
            "Set2",
            "Set3",
            "D3",
            "G10",
            "T10",
        ],
        index=0,
    )
    st.subheader("Plot labels:")

# Add radio button for data source selection
data_source, data_files = data_extractor(measurement_type="I-t")

# Create a figure for all curves
fig = go.Figure()

# Get color sequence based on selection
colors = get_colors(len(data_files), color_scheme)

# Process each uploaded file
for idx, data_file in enumerate(data_files):
    file_name = extract_filename(data_source, data_file)

    color_idx = idx % len(colors)  # Fallback in case we have more files than colors
    # Read the CSV file
    df = pd.read_csv(data_file, comment="#")

    pulse_start_index, pulse_start_time = find_pulse_start(df, threshold_input * 1e-9)
    with st.expander(f"Raw data for {file_name}"):
        df["Current (nA)"] = df["Current (A)"] * 1e9
        st.write(
            f"Pulse start index: {pulse_start_index}, Pulse start time: {pulse_start_time}"
        )
        st.write(df)
    # Align time to pulse start
    if align_pulse_start:
        df["Aligned_time (s)"] = df["Time (s)"] - pulse_start_time
    else:
        df["Aligned_time (s)"] = df["Time (s)"]

    df_slice = df[
        (df["Aligned_time (s)"] >= time_min) & (df["Aligned_time (s)"] <= time_max)
    ]

    with st.sidebar:
        plot_label = st.text_input(f"{file_name}", value=file_name)

    fig.add_scatter(
        x=df_slice["Aligned_time (s)"],
        y=df_slice["Current (A)"],
        name=plot_label,
        mode="markers+lines",
        line=dict(width=line_width, color=colors[color_idx]),
        marker=dict(symbol="circle", size=marker_size, color=colors[color_idx]),
    )

# Add horizontal line for threshold current
fig.add_hline(
    y=threshold_input * 1e-9,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Threshold: {threshold_input} nA",
    annotation_position="bottom right",
)
# Update layout for better visualization
fig.update_layout(
    showlegend=True,
    legend_title_text="File Name",
    xaxis_title="Time (s)",
    yaxis_title="Current (A)",
    title="I-t Curves for All Files",
    height=800,  # Make figure taller
    width=1200,  # Make figure wider
    # Add font settings for axis labels and ticks
    xaxis=dict(
        title_font=dict(
            size=20, color="black"
        ),  # Increase axis label font size and set color
        tickfont=dict(
            size=16, color="black"
        ),  # Increase tick label font size and set color
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
        type="log" if log_x else "linear",  # Toggle log scale based on checkbox
    ),
    yaxis=dict(
        title_font=dict(
            size=20, color="black"
        ),  # Increase axis label font size and set color
        tickfont=dict(
            size=16, color="black"
        ),  # Increase tick label font size and set color
        type="log" if log_y else "linear",  # Toggle log scale based on checkbox
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
        exponentformat="e",
        showexponent="all",
    ),
)
fig.update_layout(
    legend=dict(
        yanchor="bottom",
        y=0.99,
        xanchor="right",
        x=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)",  # Semi-transparent white background
        font=dict(size=16),  # Increase legend font size
    )
)

# Display the plot with full width
st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
# else:
#     st.write("Please upload CSV files to begin analysis")
