import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objects as go
from utils import get_colors, find_pulse_end, find_pulse_start

st.set_page_config(layout="wide")

def exponential_fit(x, a, b, c):
    return np.exp(-a * x + b) + c

def power_law_fit(x, a, n, c):
    return (x - a) ** n + c - a

def calculate_current_difference(df_top_edge, first_n_points=10, last_n_points=10):
    """Calculate the change in current between the beginning and end of the top edge. The calculation averages the first and last n points.
    """
    start = df_top_edge["Current (A)"].iloc[:first_n_points].mean()
    end = df_top_edge["Current (A)"].iloc[-last_n_points:].mean()
    difference = end-start
    leakage_stats = {'start': start, 'end': end, 'difference': difference}
    return leakage_stats

def calculate_falling_time(df_falling_edge, percent_drop=0.98):
    """Calculate the time it takes for the current to drop to a certain percentage of its initial value.
    """
    try:
        current_A = df_falling_edge["Current (A)"].iloc[0]
        current_B = df_falling_edge["Current (A)"].iloc[-10:].mean()
        initial_current = abs(current_A - current_B)
        threshold_drop = initial_current * (1.0-percent_drop)
        
        first_index = df_falling_edge.index[0]
        last_index = df_falling_edge.index[-1]
        # st.write(f"First index: {first_index}, Last index: {last_index} of Falling Edge")
        # Find the first index where current drops below threshold
        threshold_indices = df_falling_edge[df_falling_edge["Current (A)"] <= threshold_drop].index
        if len(threshold_indices) == 0:
            st.warning("Current did not drop below threshold within the selected time range")
            return None
            
        threshold_index = threshold_indices[0]
        # st.write(f"Threshold index: {threshold_index}")
        time_index = df_falling_edge["Aligned_time (s)"].iloc[threshold_index-first_index]
        time_drop = time_index - df_falling_edge["Aligned_time (s)"].iloc[0]
        afterglow_stats = {'threshold_drop': threshold_drop, 'time_index': time_index, 'time_drop': time_drop}
        
        return afterglow_stats
    except Exception as e:
        st.error(f"Error calculating falling time: {str(e)}")
        return None

# Set page title
st.title("Leakage Current Analysis")
st.caption("Created by: John Feng")

# Sidebar controls
with st.sidebar:
    st.subheader("Analysis Parameters")
    threshold_current = st.number_input(
        "Threshold Current (A)",
        min_value=1e-8,
        max_value=1e-5,
        value=2e-6,
        format="%.2e",
    )

    time_min = st.number_input(
        "Time Range Min (s)", min_value=-1.0, max_value=10.0, value=-0.2, step=0.1
    )
    time_max = st.number_input(
        "Time Range Max (s)", min_value=-1.0, max_value=10.0, value=1.5, step=0.1
    )

    color_scheme = st.selectbox(
        "Color Scheme", ["Plotly", "Set1", "Set2", "Set3", "D3", "G10", "T10"]
    )

    left_edge_margin = st.number_input(
        "Left Edge Margin", min_value=0, max_value=100, value=0, step=1
    )
    right_edge_margin = st.number_input(
        "Right Edge Margin", min_value=0, max_value=100, value=0, step=1
    )
    falling_edge_margin = st.number_input(
        "Falling Edge Margin", min_value=0, max_value=10, value=0
    )
    n_time_points = st.number_input(
        "Number of Time Points for Fall",
        min_value=100,
        max_value=1000,
        value=400,
        step=100,
    )

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

colors = get_colors(10, color_scheme)

if uploaded_file:
    with st.expander("Control Panel", expanded=False):
        plot_title = st.text_input("Plot Title", value=uploaded_file.name)
        col1, col2 = st.columns(2)
        with col1:
            show_top_edge = st.checkbox("Overlay Top Edge", value=True)
        with col1:
            show_falling_edge = st.checkbox("Overlay Falling Edge", value=True)
        with col2:
            calculate_leakage = st.checkbox("Calculate Leakage Current", value=True)
            c1, c2 = st.columns(2)
            with c1:
                first_n_points = st.number_input("First n Points to average", min_value=1, max_value=100, value=10, step=1)
            with c2:
                last_n_points = st.number_input("Last n Points to average", min_value=1, max_value=100, value=10, step=1)
        with col1:
            c1, c2 = st.columns(2)
            with c1:
                calculate_afterglow = st.checkbox("Calculate Falling Time of Afterglow", value=True)
            with c2:
                percent_drop_input = st.number_input("Percent Drop", min_value=0.80, max_value=1.0, value=0.98, step=0.01)
    
    # Read the CSV file
    df = pd.read_csv(uploaded_file, comment="#")

    # Find pulse start and end
    pulse_start_index, pulse_start_time = find_pulse_start(df, threshold_current)
    pulse_end_index, pulse_end_time = find_pulse_end(
        df, threshold_current, pulse_start_index
    )

    # Align time
    df["Aligned_time (s)"] = df["Time (s)"] - pulse_start_time
    df_slice = df[
        (df["Aligned_time (s)"] >= time_min) & (df["Aligned_time (s)"] <= time_max)
    ]

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
    fig.add_vline(
        x=pulse_end_time - pulse_start_time,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Pulse end: {(pulse_end_time - pulse_start_time):.3f} s",
        annotation_position="top left",
    )
    fig.add_hline(
        y=threshold_current,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Threshold: {threshold_current:.2e} A",
        annotation_position="bottom right",
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
    fig.update_layout(
        title=plot_title,
        xaxis_title="Aligned Time (s)",
        yaxis_title="Current (A)",
        height=600,
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

    if calculate_leakage:
        with col2:
            leakage_stats = calculate_current_difference(df_top_edge, first_n_points, last_n_points)
            # st.write(leakage_stats)
            st.write(f"Start: **{leakage_stats['start']:.2e}** A, End: **{leakage_stats['end']:.2e}** A, Difference: **{leakage_stats['difference']:.2e}** A")
        
        fig.add_hline(
            y=leakage_stats['start'],
            line_dash="dash",
            line_color="grey",
            annotation_text=f"Start: {leakage_stats['start']:.2e} A",
            annotation_position="bottom right",
        )
        fig.add_hline(
            y=leakage_stats['end'],
            line_dash="dash",
            line_color="grey",
            annotation_text=f"End: {leakage_stats['end']:.2e} A",
            annotation_position="top right",
        )

    if calculate_afterglow:
        afterglow_stats = calculate_falling_time(df_falling_edge, percent_drop=percent_drop_input)
        if afterglow_stats is not None:  # Only add lines if calculation was successful
            with col1:
                st.write(f"Falling Time: {afterglow_stats['time_drop']:.4f} s")
            fig.add_hline(
                y=afterglow_stats['threshold_drop'],
                line_dash="dash",
                line_color="grey",
                annotation_text=f"{percent_drop_input*100}% Drop: {afterglow_stats['threshold_drop']:.2e} A",
                annotation_position="top right",
            )
            fig.add_vline(
                x=afterglow_stats['time_index'],
                line_dash="dash",
                line_color="grey",
                annotation_text=f"Time Drop: {afterglow_stats['time_drop']:.4f} s",
                annotation_position="bottom right",
            )

    # Display main plot
    with st.expander("Full Curve", expanded=False):
        st.plotly_chart(fig, use_container_width=True)

    curve_fit_falling_edge = st.checkbox("Curve Fit Falling Edge", value=True)
    # Show fits if requested
    if curve_fit_falling_edge:
        st.subheader("Falling Edge Analysis")

        # Create fit plot
        fig_fit = go.Figure()

        # Add data trace
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
            popt, _ = curve_fit(
                power_law_fit,
                df_falling_edge["Aligned_time (s)"],
                df_falling_edge["Current (A)"],
                p0=(0.1, -1e-7, 5e-8),
            )
            a, b, c = popt
            fig_fit.add_trace(
                go.Scatter(
                    x=df_falling_edge["Aligned_time (s)"],
                    y=power_law_fit(df_falling_edge["Aligned_time (s)"], a, b, c),
                    mode="lines",
                    name=f"Power Law Fit (n={b:.3f})",
                )
            )
        except:
            st.warning("Power law fit failed")
        st.write(f"Power law fit: {a:.5f}, {b:.5f}, {c:.5f}")
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
else:
    st.write("Please upload a CSV file to begin analysis")
