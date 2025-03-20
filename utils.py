import plotly.express as px
import pandas as pd

def find_pulse_start(df: pd.DataFrame, pulse_start_current: float = 1e-7) -> tuple[int, float]:
    filter = df['Current (A)'] > pulse_start_current
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

def get_colors(n_files, color_scheme):
    # qualitative color schemes
    if color_scheme == 'Plotly':
        colors = px.colors.qualitative.Plotly
    elif color_scheme == 'G10':
        colors = px.colors.qualitative.G10
    elif color_scheme == 'T10':
        colors = px.colors.qualitative.T10
    elif color_scheme == 'Set1':
        colors = px.colors.qualitative.Set1
    elif color_scheme == 'Set2':
        colors = px.colors.qualitative.Set2
    elif color_scheme == 'Set3':
        colors = px.colors.qualitative.Set3
    # sequential color schemes
    elif color_scheme == 'Viridis':
        colors = px.colors.sequential.Viridis
    elif color_scheme == 'Plasma':
        colors = px.colors.sequential.Plasma
    elif color_scheme == 'Rainbow':
        colors = px.colors.sequential.Rainbow
    elif color_scheme == 'Turbo':
        colors = px.colors.sequential.Turbo
    elif color_scheme == 'D3':
        colors = px.colors.qualitative.D3
    return colors[::max(1, len(colors)//n_files)][:n_files]



