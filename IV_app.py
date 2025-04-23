import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px
from utils import (get_colors, 
                   calculate_first_derivative, 
                   data_extractor, 
                   extract_filename,
                   get_file_name,
                   extract_metadata)

st.set_page_config(layout="wide")

# Set page title
st.title("IV Curve Analysis")
st.caption("Created by: John Feng")

with st.sidebar:
    st.subheader("Data selection:")
    convert_absolute_current = st.checkbox("Convert to absolute current", value=True)
    log_x = st.checkbox("Log x-axis", value=False)
    log_y = st.checkbox("Log y-axis", value=True)
    show_legend = st.checkbox("Show legend", value=True)
    only_positive_voltage = st.checkbox("Voltage > 0", value=False)
    only_negative_voltage = st.checkbox("Voltage < 0", value=False)
    log_bar_chart = st.checkbox("Log y-axis for bar chart", value=True)
    st.subheader("Plot settings:")
    marker_size = st.slider("Marker size", min_value=1, max_value=10, value=5, step=1)
    line_width = st.slider(
        "Line width", min_value=0.5, max_value=5.0, value=1.0, step=0.5
    )
    size_x = st.slider("Plot width", min_value=300, max_value=1200, value=800, step=50)
    size_y = st.slider("Plot height", min_value=300, max_value=1200, value=800, step=50)
    # fontsize = st.slider("Axis font size", min_value=10, max_value=50, value=20, step=5)
    axis_label_size = st.slider("Axis label size", min_value=10, max_value=50, value=25, step=1)
    axis_tick_size = st.slider("Axis tick size", min_value=10, max_value=50, value=25, step=1)
    axis_tick_color = st.color_picker("Axis tick color", value="#4A4A4A")
    color_scheme = st.selectbox(
        "Color scheme", ["Plotly", "Set1", "Set2", "Set3", "D3", "G10", "T10"]
    )
    st.subheader("Plot labels:")
    # Add new controls for negative voltage style
    negative_marker_symbol = st.selectbox(
        "Negative voltage marker",
        ["circle", "square", "diamond", "triangle-down", "x"],
        index=2
    )
    negative_line_style = st.selectbox(
        "Negative voltage line style",
        ["solid", "dash", "dot", "dashdot"],
        index=1
    )

# Data extraction process from uploaded files or sample files
data_source, data_files = data_extractor(measurement_type="I-V")

# Create a figure for all curves
fig_IV = go.Figure()
fig_power_law = go.Figure()
colors = get_colors(color_scheme)
df_bar_chart = pd.DataFrame()

for idx, data_file in enumerate(data_files):
    file_path = extract_filename(data_source, data_file)
    file_name = get_file_name(file_path)
    
    try:
        metadata = extract_metadata(data_file)
    except:
        metadata = {}
        
    # Read the CSV file
    df = pd.read_csv(data_file, comment="#")
    df["Voltage sign"] = np.sign(df["Voltage (V)"])
    # Calculate first derivative
    df = calculate_first_derivative(df)

    # with st.expander("Raw Data", expanded=False):
    #     st.write(df)

    if only_positive_voltage:
        df_IV = df[df["Voltage (V)"] > 0].copy()
    elif only_negative_voltage:
        df_IV = df[df["Voltage (V)"] < 0].copy()
    elif log_x:
        df_IV = df.copy()
        df_IV['Voltage (V)'] = df_IV["Voltage (V)"].abs()
    else:
        df_IV = df.copy()

    if convert_absolute_current:
        df_IV["Current (A)"] = df["Current (A)"].abs()

    with st.sidebar:
        try:
            plot_label = st.text_input(f"Plot {idx+1}", 
                                       value=f"{metadata['Surface Treatment']}_Guard-{metadata['Guard Ring']}")
        except:
            plot_label = st.text_input(f"Plot {idx+1}", 
                                       value=f"{file_name}")

    # Split data into positive and negative voltage parts
    df_positive = df_IV[df_IV["Voltage sign"] >= 0]
    df_negative = df_IV[df_IV["Voltage sign"] < 0]

    # Add positive voltage trace
    if not df_positive.empty:
        fig_IV.add_scatter(
            x=df_positive["Voltage (V)"],
            y=df_positive["Current (A)"],
            name=plot_label + " (V ≥ 0)",
            # name=plot_label,
            mode="markers+lines",
            line=dict(width=line_width, color=colors[idx]),
            marker=dict(symbol="circle", size=marker_size, color=colors[idx]),
            showlegend=True,
        )
        
        fig_power_law.add_scatter(
            x=df_positive["Voltage (V)"],
            y=df_positive["power_law_slope"],
            name=plot_label + " (V ≥ 0)",
            mode="markers+lines",
            line=dict(width=line_width, color=colors[idx]),
        )

    # Add negative voltage trace
    if not df_negative.empty:
        fig_IV.add_scatter(
            x=df_negative["Voltage (V)"],
            y=df_negative["Current (A)"],
            name=plot_label + " (V < 0)",
            mode="markers+lines",
            line=dict(width=line_width, color=colors[idx], dash=negative_line_style),
            marker=dict(symbol=negative_marker_symbol, size=marker_size, color=colors[idx]),
            showlegend=True,
        )
        
        fig_power_law.add_scatter(
            x=df_negative["Abs Voltage (V)"],
            y=df_negative["power_law_slope"],
            name=plot_label + " (V < 0)",
            mode="markers+lines",
            line=dict(width=line_width, color=colors[idx], dash=negative_line_style),
            marker=dict(symbol=negative_marker_symbol, size=marker_size, color=colors[idx]),
            showlegend=True,
        )

    if "Surface Treatment" in metadata:
        current_at_1000V = df[df["Voltage (V)"] == 1000]["Current (A)"]
        df_bar_chart = pd.concat(
            [
            df_bar_chart,
            pd.DataFrame(
                {
                    "Index": [idx],
                    "File Name": file_name,
                    "Device ID": df["Device ID"].iloc[0],
                    "Contact ID": df["Contact ID"].iloc[0],
                    "Current at 1000V": current_at_1000V,
                    "Color": colors[idx],
                    "Surface Treatment": metadata["Surface Treatment"],
                    "Guard Ring": metadata["Guard Ring"],
                }
            ),
            ]
        )
    else:
        current_at_1000V = df[df["Voltage (V)"] == 1000]["Current (A)"]
        df_bar_chart = pd.concat(
            [
            df_bar_chart,
            pd.DataFrame(
                {
                    "Index": [idx],
                    "File Name": file_name,
                    "Device ID": df["Device ID"].iloc[0],
                    "Contact ID": df["Contact ID"].iloc[0],
                    "Current at 1000V": current_at_1000V,
                    "Color": colors[idx],
                }
            ),
            ]
        )
        
# Update layout for better visualization
fig_IV.update_layout(
    showlegend=show_legend,
    legend_title_text="",
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
        font=dict(size=axis_label_size, color=axis_tick_color),  # Legend font size
    ),
    # Add font settings for axis labels and ticks
    xaxis=dict(
        title_font=dict(
            size=axis_label_size, color=axis_tick_color),  # Increase axis label font size
        tickfont=dict(size=axis_tick_size, color=axis_tick_color),  # Increase tick label font size
        type="log" if log_x else "linear",  # Toggle log scale based on checkbox
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
    ),
    yaxis=dict(
        title_font=dict(size=axis_label_size, color=axis_tick_color),  # Increase axis label font size
        tickfont=dict(size=axis_tick_size, color=axis_tick_color),  # Increase tick label font size
        type="log" if log_y else "linear",  # Toggle log scale based on checkbox
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
        exponentformat="e",
        showexponent="all",  # Grid line spacing
    ),
)

fig_power_law.update_layout(
    showlegend=show_legend,
    legend_title_text="",
    xaxis_title="Anode Voltage (V)",
    yaxis_title="Power Law Slope",
    title="Power Law Slope for All Files",
    height=size_y,  # Make figure taller
    width=size_x,  # Make figure wider
    xaxis=dict(
        type="log",
        title_font=dict(size=axis_label_size, color=axis_tick_color),  # Increase axis label font size
        tickfont=dict(size=axis_tick_size, color=axis_tick_color),  # Increase tick label font size
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
    ),
    yaxis=dict(
        title_font=dict(size=axis_label_size, color=axis_tick_color),  # Increase axis label font size
        tickfont=dict(size=axis_tick_size, color=axis_tick_color),  # Increase tick label font size
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
    ),
    legend=dict(
        yanchor="bottom",
        y=1.0,
        xanchor="right",
        x=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)",  # Semi-transparent white background
        font=dict(size=axis_label_size, color=axis_tick_color),  # Legend font size
    ),
)

st.plotly_chart(fig_IV, use_container_width=True, config={"responsive": True})

with st.expander("Power Law Slope", expanded=True):
    st.plotly_chart(fig_power_law, use_container_width=True)


with st.expander("Bar Chart of Dark Current at 1000V", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        x_choice = st.radio("X-axis", ["Device ID", "Contact ID", "Surface Treatment", "Guard Ring"], index=0)
    with col2:
        group_choice = st.radio("Group by", ["Device ID", "Contact ID", "Surface Treatment", "Guard Ring"], index=1)
    fig_bar = px.bar(
        df_bar_chart,
        x=x_choice,
        y="Current at 1000V",
        color=group_choice,
        color_discrete_map=dict(zip(df_bar_chart["Device ID"], df_bar_chart["Color"])),
        barmode='group'  # Show bars side by side
    )
    
    fig_bar.update_layout(
        title="Dark Current at 1000V",
        showlegend=True,
        bargap=0.15,  # Reduce space between bars in different groups
        bargroupgap=0.1,  # Reduce space between bars in the same group
        legend=dict(
            yanchor="bottom",
            y=0.99,
            xanchor="right", 
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.8)",
            font=dict(size=axis_label_size, color=axis_tick_color),
        ),

        yaxis=dict(
            title="Current (A) - log scale" if log_bar_chart else "Current (A)",
            type="log" if log_bar_chart else "linear",  # Set y-axis to logarithmic scale
            exponentformat="e",  # Use scientific notation
            showexponent="all",  # Show exponent for all numbers
            tickfont=dict(size=axis_tick_size, color=axis_tick_color),  # Increase tick label font size
            title_font=dict(size=axis_label_size, color=axis_tick_color),  # Increase axis label font size
        ),
        xaxis=dict(
            title_font=dict(size=axis_label_size, color=axis_tick_color),  # Increase axis label font size
            tickfont=dict(size=axis_tick_size, color=axis_tick_color),  # Increase tick label font size
        ),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"responsive": True})


