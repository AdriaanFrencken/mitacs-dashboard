import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objects as go
import plotly.express as px
import os
from utils import (get_colors, 
                   find_pulse_end, 
                   find_pulse_start, 
                   data_extractor, 
                   extract_filename, 
                   get_file_name,
                   extract_metadata)
from leakage_current_functions import (calculate_current_difference, 
                                       calculate_falling_time, 
                                       exponential_fit, 
                                       power_law_fit)
st.set_page_config(layout="wide")

# Set page title
st.title("I-t Curve Analysis")
st.caption("Created by: John Feng")


with st.sidebar:
    show_raw_data = st.checkbox("Show raw data", value=False)
    # align_pulse_start = st.checkbox("Align pulse start", value=True)
    align_pulse = st.radio("Align pulse", options=["Start", "End", "raw"], index=0)
    alignment_shift = st.number_input("Alignment shift (ms)", min_value=-100, max_value=100, value=0, step=1)
    alignment_shift = alignment_shift * 1e-3 # Convert to seconds
    log_y = st.checkbox("Log y-axis", value=False)
    log_x = st.checkbox("Log x-axis", value=False)
    show_threshold_line = st.checkbox("Show current threshold line", value=True)
    if align_pulse == "Start":
        time_min, time_max = st.slider(
            "Time range", min_value=-1.0, max_value=10.0, value=(-0.2, 1.8), step=0.1
        )
    elif align_pulse == "End":
        time_min, time_max = st.slider(
            "Time range", min_value=-2.0, max_value=10.0, value=(-0.2, 1.5), step=0.1
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

    axis_label_size = st.slider("Axis label size", min_value=10, max_value=50, value=25, step=1)
    axis_tick_size = st.slider("Axis tick size", min_value=10, max_value=50, value=25, step=1)
    axis_tick_color = st.color_picker("Axis tick color", value="#000000")
    annotation_font_size = st.slider("Annotation text size", min_value=10, max_value=50, value=16, step=1)
    annotation_font_color = st.color_picker("Annotation text color", value="#7F7F7F")

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

st.subheader("Plot all I-t Photocurrents")
# Get color sequence based on selection
colors = get_colors(color_scheme)

if "data_files" not in st.session_state:
    st.session_state.data_files = []

# Add radio button for data source selection
data_source, data_files = data_extractor(measurement_type="I-t")
st.session_state.data_files = data_files

with st.expander("I-t plots expander", expanded=True):
    # Display the plot with full width
    main_plot_container = st.container()

st.subheader("Leakage Current and Afterglow Analysis")

with st.expander("Leakage Current and Afterglow Analysis Control Panel", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        show_top_edge = st.checkbox("Overlay Top Edge", value=True)
        show_falling_edge = st.checkbox("Overlay Falling Edge", value=True)
        show_threshold_line = st.checkbox("Current Threshold Line", value=True)
        show_pulse_end_line = st.checkbox("Pulse End Line", value=True)
    with col2:
        calculate_afterglow = st.checkbox("Calculate Falling Time of Afterglow", value=True)
        percent_drop_input = st.number_input("Percent Drop", min_value=0.80, max_value=1.0, value=0.98, step=0.01)
    
    with col3:
        calculate_leakage = st.checkbox("Calculate Leakage Current", value=True)
        c1, c2 = st.columns(2)
        with c1:
            first_n_points = st.number_input("First n Points to average", min_value=1, max_value=100, value=10, step=1)
        with c2:
            last_n_points = st.number_input("Last n Points to average", min_value=1, max_value=100, value=10, step=1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        left_edge_margin = st.number_input(
            "Left Edge Margin", min_value=0, max_value=100, value=0, step=1)
    with c2:
        right_edge_margin = st.number_input(
            "Right Edge Margin", min_value=0, max_value=100, value=0, step=1)
    with c3:
        falling_edge_margin = st.number_input(
            "Falling Edge Margin", min_value=0, max_value=10, value=0)
    with c4:
        n_time_points = st.number_input(
            "Number of Time Points for Fall",
            min_value=100,
            max_value=1000,
            value=400,
            step=100,)

with st.expander("Leakage Current Analysis Data", expanded=False):
    stats_container = st.container()
    
stats_df = pd.DataFrame()
# Create a figure for all curves
fig_main = go.Figure()

# Process each uploaded file
for idx, data_file in enumerate(st.session_state.data_files):
    file_path = extract_filename(data_source, data_file)
    file_name = get_file_name(file_path)
    try:
        metadata = extract_metadata(data_file)
    except:
        metadata = {}
    
    color_idx = idx % len(colors)  # Fallback in case we have more files than colors
    # Read the CSV file
    df = pd.read_csv(data_file, comment="#")

    pulse_start_index, pulse_start_time = find_pulse_start(df, threshold_input * 1e-9)
    pulse_end_index, pulse_end_time = find_pulse_end(df, threshold_input * 1e-9, pulse_start_index)
    if show_raw_data:
        with st.expander(f"Raw data for {file_name}"):
            df["Current (nA)"] = df["Current (A)"] * 1e9
            st.write(
                f"Pulse start index: {pulse_start_index}, Pulse start time: {pulse_start_time}"
            )
            st.write(df)
    # Align time to pulse start
    if align_pulse == "Start":
        df["Aligned_time (s)"] = df["Time (s)"] - pulse_start_time - alignment_shift
    elif align_pulse == "End":
        df["Aligned_time (s)"] = df["Time (s)"] - pulse_end_time - alignment_shift
    else:
        df["Aligned_time (s)"] = df["Time (s)"]

    df_slice = df[
        (df["Aligned_time (s)"] >= time_min) & (df["Aligned_time (s)"] <= time_max)
    ]

    with st.sidebar: # PLOT LABELS INPUT
        try:
            plot_label = st.text_input(f"Plot {idx+1}", value=f"{metadata['Surface Treatment']}_Guard-{metadata['Guard Ring']}")
        except:
            plot_label = st.text_input(f"Plot {idx+1}", value=f"{file_name}")

    fig_main.add_scatter(
        x=df_slice["Aligned_time (s)"],
        y=df_slice["Current (A)"],
        name=plot_label,
        mode="markers+lines",
        line=dict(width=line_width, color=colors[color_idx]),
        marker=dict(symbol="circle", size=marker_size, color=colors[color_idx]),
    )

    # Create main plot
    fig = go.Figure()

    # Add main trace
    fig.add_trace(
        go.Scatter(
            x=df_slice["Aligned_time (s)"],
            y=df_slice["Current (A)"],
            mode="markers+lines",
            name="Full Curve",
            line=dict(color=colors[0]),
            marker=dict(color=colors[0]),
        )
    )

    # Add vertical and horizontal lines
    if show_pulse_end_line:
        fig.add_vline(
            x=pulse_end_time - pulse_start_time,
            line_dash="dash",
            line_color="grey",
            annotation_text=f"Pulse end: {(pulse_end_time - pulse_start_time):.3f} s",
            annotation_position="top left",
            annotation_font_size=annotation_font_size,
            annotation_font_color=annotation_font_color,
        )
    if show_threshold_line:
        fig.add_hline(
            y=threshold_input * 1e-9,
            line_dash="dash",
            line_color=colors[0],
            annotation_text=f"Threshold: {(threshold_input*1e-9):.2e} A",
            annotation_position="bottom right",
            annotation_font_size=annotation_font_size,
            annotation_font_color=annotation_font_color,
        )

    df_top_edge = df.iloc[(pulse_start_index + left_edge_margin) : (pulse_end_index - right_edge_margin)]
    if show_top_edge:
        fig.add_trace(
            go.Scatter(
                x=df_top_edge["Aligned_time (s)"],
                y=df_top_edge["Current (A)"],
                mode="markers+lines",
                name="Top Edge",
                line=dict(color=colors[1]),
                marker=dict(color=colors[1]),
            )
        )

    df_falling_edge = df.iloc[(pulse_end_index + falling_edge_margin) : (pulse_end_index + n_time_points)]
    if show_falling_edge:
        fig.add_trace(
            go.Scatter(
                x=df_falling_edge["Aligned_time (s)"],
                y=df_falling_edge["Current (A)"],
                mode="markers+lines",
                name="Falling Edge",
                line=dict(color=colors[2]),
                marker=dict(color=colors[2]),
            )
        )
    # Update layout
    try:
        plot_title = f"{metadata['Surface Treatment']} Guard-{metadata['Guard Ring']}"
    except:
        plot_title = file_name
    fig.update_layout(
        title=plot_title,
        xaxis_title="Aligned Time (s)",
        yaxis_title="Current (A)",
        height=600,
        xaxis=dict(
            title_font=dict(size=axis_label_size, color=axis_tick_color),
            tickfont=dict(size=axis_tick_size, color=axis_tick_color),
            type="log" if log_x else "linear",
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgrey",
        ),
        yaxis=dict(
            title_font=dict(size=axis_label_size, color=axis_tick_color),
            tickfont=dict(size=axis_tick_size, color=axis_tick_color),
            type="log" if log_y else "linear",
            showgrid=True,
            gridwidth=1,
            gridcolor="lightgrey",
            exponentformat="e",
            showexponent="all",
        ),
    )

    if calculate_leakage:
        with col2:
            leakage_stats = calculate_current_difference(df_top_edge, first_n_points, last_n_points)
            # st.write(f"Start: **{leakage_stats['start']:.2e}** A, End: **{leakage_stats['end']:.2e}** A, Difference: **{leakage_stats['difference']:.2e}** A")
        
        fig.add_hline(
            y=leakage_stats['start'],
            line_dash="dash",
            line_color=colors[1],
            annotation_text=f"Start: {leakage_stats['start']:.2e} A",
            annotation_position="bottom right",
            annotation_font_size=annotation_font_size,
            annotation_font_color=annotation_font_color,
        )
        fig.add_hline(
            y=leakage_stats['end'],
            line_dash="dash",
            line_color=colors[1],
            annotation_text=f"End: {leakage_stats['end']:.2e} A",
            annotation_position="top right",
            annotation_font_size=annotation_font_size,
            annotation_font_color=annotation_font_color,
        )

    if calculate_afterglow:
        afterglow_stats = calculate_falling_time(df_falling_edge, percent_drop=percent_drop_input)
        if afterglow_stats is not None:  # Only add lines if calculation was successful
            # with col1:
            #     st.write(f"Falling Time at {percent_drop_input*100}% Drop = {afterglow_stats['time_drop']*1e3:.2f} ms")
            fig.add_hline(
                y=afterglow_stats['threshold_drop']+afterglow_stats['end_current'],
                line_dash="dash",
                line_color="grey",
                annotation_text=f"{percent_drop_input*100}% Drop: {afterglow_stats['threshold_drop']:.2e} A",
                annotation_position="top right",
                annotation_font_size=annotation_font_size,
                annotation_font_color=annotation_font_color,
            )
            fig.add_vline(
                x=afterglow_stats['time_index'],
                line_dash="dash",
                line_color=colors[2],
                annotation_text=f"Time Drop: {afterglow_stats['time_drop']*1e3:.2f} ms",
                annotation_position="bottom right",
                annotation_font_size=annotation_font_size,
                annotation_font_color=annotation_font_color,
            )

    # Display main plot
    with st.expander("Full Curve", expanded=True):
        st.plotly_chart(fig, use_container_width=True)

    stats = {'file_name': file_name, 
            'Device ID': df.iloc[0]['Device ID'],
            'Contact ID': df.iloc[0]['Contact ID'],
            }
    if 'leakage_stats' in locals() and leakage_stats is not None:
        stats['photocurrent_start'] = f"{leakage_stats['start']:.2e}"
        stats['photocurrent_end'] = f"{leakage_stats['end']:.2e}" 
        stats['leakage_current'] = f"{leakage_stats['difference']:.2e}"
        stats['percent_drop_threshold'] = percent_drop_input
    if 'afterglow_stats' in locals() and afterglow_stats is not None:
        stats['afterglow_time_ms'] = np.round(afterglow_stats['time_drop']*1e3, 2)
        stats['afterglow_time'] = np.round(afterglow_stats['time_drop'], 5)

    stats_df = pd.concat([stats_df, pd.DataFrame([stats])], ignore_index=True)



    
    #########################################################
    ## SCIPY OPTIMIZE CURVE FIT
    #########################################################
    
    curve_fit_falling_edge = st.checkbox("Curve Fit Falling Edge", value=False, key=f"curve_fit_{file_name}")
    # Show fits if requested
    if curve_fit_falling_edge:
        with st.expander("Falling Edge Analysis", expanded=True):
            # Create fit plot
            fig_fit = go.Figure()
            # Raw data trace
            fig_fit.add_trace(
                go.Scatter(
                    x=df_falling_edge["Aligned_time (s)"],
                    y=df_falling_edge["Current (A)"],
                    mode="markers+lines",
                    name="Current vs Time",
                    line=dict(width=1),
                )
            )

            # Power law fit
            try:
                popt, pcov = curve_fit(
                    power_law_fit,
                    df_falling_edge["Aligned_time (s)"],
                    df_falling_edge["Current (A)"],
                    p0=(0.1, -1e-7, 5e-8),
                )
                a, n, c = popt
                fig_fit.add_trace(
                    go.Scatter(
                        x=df_falling_edge["Aligned_time (s)"],
                        y=power_law_fit(df_falling_edge["Aligned_time (s)"], a, n, c),
                        mode="lines",
                        name=f"Power Law Fit (n={n:.3f})",
                    )
                )
            except:
                st.warning("Power law fit failed")
            st.write("Power law equation: I(t) = (t - a)^n + c - a")
            st.write(f"Power law fit: a={a:.5f}, n={n:.5f}, c={c:.5f}")
            # Exponential fit
            try:
                popt, _ = curve_fit(
                    exponential_fit,
                    df_falling_edge["Aligned_time (s)"],
                    df_falling_edge["Current (A)"],
                    p0=(1e2, 1e2, 5e-8),
                )
                a, b, c = popt
                fig_fit.add_trace(
                    go.Scatter(
                        x=df_falling_edge["Aligned_time (s)"],
                        y=exponential_fit(df_falling_edge["Aligned_time (s)"], a, b, c),
                        mode="lines",
                        name=f"Exponential Fit (τ={1 / a:.3f}s)",
                    )
                )
            except:
                st.warning("Exponential fit failed")
            st.write("Exponential equation: I(t) = exp(-a*t + b) + c")
            st.write(f"Exponential fit: a={a:.3f}, b={b:.3f}, c={c:.3f}")

            # Update fit plot layout
            fig_fit.update_layout(
                title="Falling Edge Fits",
                xaxis_title="Time (s)",
                yaxis_title="Current (A)",
                height=400,
                xaxis=dict(
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="lightgrey",
                ),
                yaxis=dict(
                    title_font=dict(size=16),
                    tickfont=dict(size=14),
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="lightgrey",
                    exponentformat="e",
                    showexponent="all",
                ),
            )

            # Display fit plot
            st.plotly_chart(fig_fit, use_container_width=True)

with stats_container:
    # Format numeric columns to scientific notation
    formatted_df = stats_df.copy()
    st.write(formatted_df)
    # Convert DataFrame to CSV for download
    csv = formatted_df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="leakage_current_stats.csv",
        mime="text/csv",
    )

# Add horizontal line for threshold current
if show_threshold_line:
    fig_main.add_hline(
        y=threshold_input * 1e-9,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Threshold: {threshold_input} nA",
        annotation_position="bottom right",
    )

fig_main.add_hline(
    y=0,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Current = 0",
    annotation_position="bottom right",
)
# Update layout for better visualization
fig_main.update_layout( # General layout configuration
    showlegend=True,
    legend_title_text="",
    xaxis_title="Time (s)",
    yaxis_title="Current (A)",
    title="I-t Curves for All Files",
    height=800,  # Make figure taller
    width=1200,  # Make figure wider
    # Add font settings for axis labels and ticks
    xaxis=dict(
        title_font=dict(
            size=axis_label_size, color=axis_tick_color
        ),  # Increase axis label font size and set color
        tickfont=dict(
            size=axis_tick_size, color=axis_tick_color
        ),  # Increase tick label font size and set color
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
        type="log" if log_x else "linear",  # Toggle log scale based on checkbox
    ),
    yaxis=dict(
        title_font=dict(
            size=axis_label_size, color=axis_tick_color
        ),  # Increase axis label font size and set color
        tickfont=dict(
            size=axis_tick_size, color=axis_tick_color
        ),  # Increase tick label font size and set color
        type="log" if log_y else "linear",  # Toggle log scale based on checkbox
        showgrid=True,  # Show grid lines
        gridwidth=1,  # Grid line width
        gridcolor="lightgrey",  # Grid line color
        exponentformat="e",
        showexponent="all",
    ),
)
fig_main.update_layout( # Legend configuration
    legend=dict(
        yanchor="bottom",
        y=0.99,
        xanchor="right",
        x=0.99,
        bgcolor="rgba(255, 255, 255, 0.8)",  # Semi-transparent white background
        font=dict(size=24),  # Increase legend font size
    )
)

with main_plot_container:
    st.plotly_chart(fig_main, use_container_width=True, config={"responsive": True})