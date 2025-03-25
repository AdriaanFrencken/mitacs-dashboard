import numpy as np
import streamlit as st

def exponential_fit(t, a, b, c):
    return np.exp(-a * t + b) + c

def power_law_fit(t, a, n, c):
    return (t - a) ** n + c - a

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
            st.warning("Fall time too fast to resolve.")
            afterglow_stats = {'threshold_drop': threshold_drop, 'time_index': 0, 'time_drop': 0}
            return afterglow_stats
            
        threshold_index = threshold_indices[0]
        # st.write(f"Threshold index: {threshold_index}")
        time_index = df_falling_edge["Aligned_time (s)"].iloc[threshold_index-first_index]
        time_drop = time_index - df_falling_edge["Aligned_time (s)"].iloc[0]
        afterglow_stats = {'threshold_drop': threshold_drop, 'time_index': time_index, 'time_drop': time_drop}
        
        return afterglow_stats
    except Exception as e:
        st.error(f"Error calculating falling time: {str(e)}")
        return None
