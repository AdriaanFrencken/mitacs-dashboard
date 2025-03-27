import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import (get_colors, 
                   calculate_first_derivative, 
                   data_extractor, 
                   extract_filename,
                   get_file_name,
                   extract_metadata)
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

# Set page title
st.title("I-V Power Law Analysis")
st.caption("Created by: John Feng")

with st.sidebar:
    show_raw_data = st.checkbox("Show raw data", value=False)
    log_x = st.checkbox("Log x-axis", value=True)
    log_y = st.checkbox("Log y-axis", value=True)
    show_legend = st.checkbox("Show legend", value=True)
    overlay_power_law = st.checkbox("Overlay power law fit", value=False)
    marker_size = st.slider("Marker size", min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider(
        "Line width", min_value=0.5, max_value=5.0, value=1.0, step=0.5
    )
    size_x = st.slider("Plot width", min_value=300, max_value=1200, value=800, step=50)
    size_y = st.slider("Plot height", min_value=300, max_value=1200, value=800, step=50)
    fontsize = st.slider("Axis font size", min_value=10, max_value=50, value=20, step=5)
    color_scheme = st.selectbox(
        "Color scheme", ["Plotly", "Set1", "Set2", "Set3", "D3", "G10", "T10"]
    )
    st.subheader("Plot labels:")

# Data extraction process from uploaded files or sample files
data_source, data_files = data_extractor(measurement_type="I-V")

# Create a figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig2 = go.Figure()
colors = get_colors(len(data_files), color_scheme)

# Process each uploaded file
for idx, data_file in enumerate(data_files):
    file_path = extract_filename(data_source, data_file)
    file_name = get_file_name(file_path)
    try:
        metadata = extract_metadata(data_file)
    except:
        metadata = {}
    # Read the CSV file
    df = pd.read_csv(data_file, comment="#")
    # Filter for positive voltages
    df = df[df["Voltage (V)"] > 0]

    # Calculate first derivative and power law slope
    df = calculate_first_derivative(df)
    power_law_slope = np.gradient(
        np.log10(df["Current (A)"]), np.log10(df["Voltage (V)"])
    )

    df["Current (nA)"] = df["Current (A)"] * 1e9
    df["Power Law Slope"] = power_law_slope
    if show_raw_data:
        with st.expander(f"Raw data for {file_name}"):
            st.write(df)

    with st.sidebar:
        try:
            plot_label = st.text_input(f"Plot {idx+1}", value=f"{metadata['Surface Treatment']}_Guard-{metadata['Guard Ring']}")
        except:
            plot_label = st.text_input(f"Plot {idx+1}", value=f"{file_name}")

    # Add IV curve trace on primary y-axis
    fig.add_trace(
        go.Scatter(
            x=df["Voltage (V)"],
            y=df["Current (A)"],
            name=f"{plot_label} - IV",
            mode="markers+lines",
            line=dict(width=line_width),
            marker=dict(symbol="circle", size=marker_size, color=colors[idx]),
        ),
        secondary_y=False,
    )
    
    fig2.add_trace(
        go.Scatter(
            x=df["Voltage (V)"],
            y=df["Power Law Slope"],
            name=f"{plot_label} - Slope",
            mode="markers+lines",
            line=dict(width=line_width, dash="dot"),
            marker=dict(symbol="circle", size=marker_size, color=colors[idx]),
        )
    )

    if overlay_power_law:
        # Add power law slope trace on secondary y-axis
        fig.add_trace(
            go.Scatter(
                x=df["Voltage (V)"],
                y=power_law_slope,
                name=f"{plot_label} - Slope",
                mode="markers+lines",
                line=dict(width=line_width, dash="dot"),
                marker=dict(symbol="circle", size=marker_size, color=colors[idx]),
            ),
            secondary_y=True,
        )


# Update layout for better visualization
fig.update_layout(
    showlegend=show_legend,
    legend_title_text="Curves",
    title="IV Curves and Power Law Slope",
    height=size_y,
    width=size_x,
    legend=dict(
        yanchor="bottom",
        # y=0.01,
        xanchor="right",
        # x=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)",
        font=dict(size=0.8 * fontsize),
    ),
)

# Update x-axis
fig.update_xaxes(
    title_text="Anode Voltage (V)",
    type="log" if log_x else "linear",
    title_font=dict(size=fontsize),
    tickfont=dict(size=fontsize * 0.8),
    showgrid=True,
    gridwidth=1,
    gridcolor="lightgrey",
)

# Update primary y-axis (Current)
fig.update_yaxes(
    title_text="Absolute Current (A)",
    type="log" if log_y else "linear",
    title_font=dict(size=fontsize),
    tickfont=dict(size=fontsize * 0.8),
    showgrid=True,
    gridwidth=1,
    gridcolor="lightgrey",
    exponentformat="e",
    showexponent="all",
    secondary_y=False,
)

if overlay_power_law:
    # Update secondary y-axis (Power Law Slope)
    fig.update_yaxes(
        title_text="Power Law Slope (d log(I) / d log(V))",
        title_font=dict(size=fontsize),
        tickfont=dict(size=fontsize * 0.8),
        showgrid=True,
        gridwidth=1,
        gridcolor="lightgrey",
        secondary_y=True,
    )

fig2.update_layout(
    title="Power Law Slope",
    height=size_y,
    width=size_x,
    legend=dict(
        yanchor="bottom",
        xanchor="right",
        bgcolor="rgba(255, 255, 255, 0.8)",
        font=dict(size=0.8 * fontsize),
    ),
)

fig2.update_xaxes(
    title_text="Anode Voltage (V)",
    type="log" if log_x else "linear",
    title_font=dict(size=fontsize),
    tickfont=dict(size=fontsize * 0.8),
    showgrid=True,
    gridwidth=1,
    gridcolor="lightgrey",
)
fig2.update_yaxes(
    title_text="Power Law Slope (d log(I) / d log(V))",
    title_font=dict(size=fontsize),
    tickfont=dict(size=fontsize * 0.8),
    showgrid=True,
    gridwidth=1,
    gridcolor="lightgrey",
)

# Display the plot with full width
with st.expander("IV Curves", expanded=True):
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
with st.expander("Power Law Slope", expanded=False):
    st.plotly_chart(fig2, use_container_width=True, config={"responsive": True})


