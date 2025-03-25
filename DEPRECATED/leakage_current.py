# %%
import pandas as pd
import numpy as np
from utils import find_pulse_start
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# data_path = r"DATA\\TiO2\\I-t_31AF25_unguardedtest_5800mV10kR_unguarded_centerpixel_10min_2025-03-18_1.csv"
# data_path = r"DATA\TiO2\I-t_31AF25_guardedtest_5800mV10kR_guarded_centerpixel_10min_2025-03-18_1.csv"
data_path = r"DATA\\CdS\\I-t_56AF25_10mT12nmCdSOXIDELESS_guarded_REDLED10000mV10kR_guarded_centerpixel_10min_2025-03-18_1.csv"
df = pd.read_csv(data_path, comment="#")

print(df.head())


# %%
def find_pulse_end(
    df: pd.DataFrame, threshold_current: float = 2e-6, pulse_start_index: int = 0
) -> tuple[int, float]:
    df = df.iloc[pulse_start_index:]
    filter = df["Current (A)"] < threshold_current
    if filter.any():
        pulse_end_index = df[filter].index[0] - 1
        pulse_end_time = df.loc[pulse_end_index, "Time (s)"]
        return pulse_end_index, pulse_end_time
    else:
        return df.index[-1], df.loc[df.index[-1], "Time (s)"]


# %%
threshold_current = 2e-6
pulse_start_index, pulse_start_time = find_pulse_start(df, threshold_current)
print(pulse_start_index, pulse_start_time)

pulse_end_index, pulse_end_time = find_pulse_end(
    df, threshold_current, pulse_start_index
)
print(pulse_end_index, pulse_end_time)

# %%
df["Aligned_time (s)"] = df["Time (s)"] - pulse_start_time
time_min, time_max = -0.2, 1.5
df_slice = df[
    (df["Aligned_time (s)"] >= time_min) & (df["Aligned_time (s)"] <= time_max)
]
# Create plotly figure
fig = go.Figure()

# Add scatter plot of current vs time
fig.add_trace(
    go.Scatter(
        x=df_slice["Aligned_time (s)"],
        y=df_slice["Current (A)"],
        mode="markers+lines",
        name="Current vs Time",
    )
)

fig.add_vline(
    x=pulse_end_time - pulse_start_time,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Pulse end: {(pulse_end_time - pulse_start_time):.3f} s",
    annotation_position="bottom right",
)
fig.add_hline(
    y=threshold_current,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Threshold: {threshold_current} A",
    annotation_position="bottom right",
)
# Update layout for better visualization
fig.update_layout(
    title="Current vs Time",
    xaxis_title="Time (s)",
    yaxis_title="Current (A)",
    # height=600,
    # width=1000,
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

right_edge_margin = 10
df_rise = df.iloc[(pulse_start_index) : (pulse_end_index - right_edge_margin)]

# Add scatter plot of current vs time
fig.add_trace(
    go.Scatter(
        x=df_rise["Aligned_time (s)"],
        y=df_rise["Current (A)"],
        mode="markers+lines",
        name="Top Curve",
    )
)

n_time_points = 400
df_fall = df.iloc[(pulse_end_index) : (pulse_end_index + n_time_points)]

# Add scatter plot of current vs time
fig.add_trace(
    go.Scatter(
        x=df_fall["Aligned_time (s)"],
        y=df_fall["Current (A)"],
        mode="markers+lines",
        name="Falling Edge",
    )
)

fig.show()

# %%
n_time_points = 400
df_fall = df.iloc[(pulse_end_index + 2) : (pulse_end_index + n_time_points)]


def exponential_fit(x, a, b, c):
    return np.exp(-a * x + b) + c

def power_law_fit(x, a, n, c):
    return (x - a) ** n + c - a

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_fall["Aligned_time (s)"],
        y=df_fall["Current (A)"],
        mode="markers+lines",
        name="Current vs Time",
    )
)

popt, _ = curve_fit(
    power_law_fit,
    df_fall["Aligned_time (s)"],
    df_fall["Current (A)"],
    p0=(0.1, -1e-7, 5e-8),
)
a, b, c = popt
print(a, b, c)

fig.add_trace(
    go.Scatter(
        x=df_fall["Aligned_time (s)"],
        y=power_law_fit(df_fall["Aligned_time (s)"], a, b, c),
        mode="lines",
        name="Power Law Fit",
    )
)

popt, _ = curve_fit(
    exponential_fit,
    df_fall["Aligned_time (s)"],
    df_fall["Current (A)"],
    p0=(1e2, 1e2, 5e-8),
)
a, b, c = popt
print(a, b, c)

fig.add_trace(
    go.Scatter(
        x=df_fall["Aligned_time (s)"],
        y=exponential_fit(df_fall["Aligned_time (s)"], a, b, c),
        mode="lines",
        name="Exponential Fit",
    )
)
fig.show()

# %%
