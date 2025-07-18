from statistics import covariance
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
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import math


st.set_page_config(layout="wide")

st.title("Two-Term Fit Analysis")
st.caption("Created by: Adriaan Frencken")

# File uploader to drop CSV data files
uploaded_file = st.sidebar.file_uploader("Upload CSV Data File", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded data from: {uploaded_file.name}")
else:
    # Default file if nothing uploaded
    st.header("No file uploaded")
    st.warning("Please upload a CSV file to visualize data.")


st.sidebar.header("Plot Settings")
fig_width = st.sidebar.slider("Figure Width", min_value=400, max_value=1000, value=800, step=50)
fig_height = st.sidebar.slider("Figure Height", min_value=400, max_value=1000, value=600, step=50)
marker_size = st.sidebar.slider("Marker Size", min_value=4, max_value=24, value=12, step=4)
log_x = st.sidebar.checkbox("Log X Axis", value=False)
log_y = st.sidebar.checkbox("Log Y Axis", value=False)

# Current multiplier
#current_multiplier = st.sidebar.number_input("Current Multiplier", value=1.0, format="%1f")

# Number inputs for initial guesses
init_N1 = st.sidebar.number_input("Initial N₁", value=1.0E11, format="%.2e")
init_E1p = st.sidebar.number_input("Initial E₁", value=0.65, format="%.2e")
init_N2 = st.sidebar.number_input("Initial N₂", value=1.0E10, format="%.2e")
init_E2p = st.sidebar.number_input("Initial E₂", value=0.58, format="%.2e")


# Replace 'x_column' and 'y_column' with your actual column names
x1 = 1E-6 * abs(df['Total Current (uA)'])
y1 = df['rho (e/cm^3)']

def two_term_function(x, N_1, E1p, N_2, E2p):
    return (N_1*1.3E-6*x)/(1.3E-6*x+math.exp(-E1p/0.025))-(N_2*math.exp(-E2p/0.025))/(1.3E-6*x+math.exp(-E2p/0.025))

# Fit function with positive constraints
def fit_two_term_from_csv(x1, y1, init_N1, init_E1p, init_N2, init_E2p):

    x = x1
    y = y1

    # Initial guess (all positive)
    initial_guess = [init_N1, init_E1p, init_N2, init_E2p]

    # Set bounds: lower bound 0 for all parameters, upper bound inf
    lower_bounds = [0, 0, 0, 0]
    upper_bounds = [np.inf, np.inf, np.inf, np.inf]

    # Fit the function to data
    params, covariance = curve_fit(
        two_term_function,
        x, y,
        p0=initial_guess,
        bounds=(lower_bounds, upper_bounds),maxfev=200000
    )
    fitted_y = two_term_function(x, *params)

    return fitted_y, params

# Predict y using the fitted function
fitted_y, params = fit_two_term_from_csv(x1, y1, init_N1, init_E1p, init_N2, init_E2p)

st.header(
    r"Fitted Equation: $y = \frac{N_1 \cdot a \cdot x}{a \cdot x + \exp\left(-\frac{E_1}{0.025}\right)} - \frac{N_2 \cdot \exp\left(-\frac{E_2}{0.025}\right)}{a \cdot x + \exp\left(-\frac{E_2}{0.025}\right)}$"
)

st.header( r" where $a = 1.3 \times 10^{-6}$"
)

# Calculate and display root mean-square error (RMSE) for fit quality
rmse = np.sqrt(np.mean((y1 - fitted_y) ** 2))
st.subheader(f"RMSE: {rmse:.3e}")

# Calculate and display R squared
ss_res = np.sum((y1 - fitted_y) ** 2)
ss_tot = np.sum((y1 - np.mean(y1)) ** 2)
r_squared = 1 - (ss_res / ss_tot)
st.subheader(f"R²: {r_squared:.4f}")

# Prepare figure and axis
fig, ax = plt.subplots(figsize=(fig_width / 100, fig_height / 100))

# Scatter plot for data points
ax.scatter(x1, y1, c='black', s=marker_size**2, label='Data', edgecolors='none')

# Plot continuous fitted function as a smooth line
x_fit = np.linspace(np.min(x1), np.max(x1), 500)
y_fit = two_term_function(x_fit, *params)
ax.plot(x_fit, y_fit, c='red', linewidth=2, label='Fit')

# Set axis scales
ax.set_xscale('log' if log_x else 'linear')
ax.set_yscale('log' if log_y else 'linear')

# Set axis labels and title
ax.set_xlabel('Total Current (A)', fontsize=20, color='black')
ax.set_ylabel('Rho (e/cm$^3$)', fontsize=20, color='black')
ax.set_title(
    f"Fit Parameters:\n"
    f"N₁: {params[0]:e}\n"
    f"E₁: {params[1]:e}\n"
    f"N₂: {params[2]:e}\n"
    f"E₂: {params[3]:e}\n",
    fontsize=20, color='black'
)

# Set tick parameters
ax.tick_params(axis='x', labelsize=20, colors='black')
ax.tick_params(axis='y', labelsize=20, colors='black')

# Set grid
ax.grid(True, which='both', color='LightGray', linewidth=1)

# Use scientific notation for y-axis
if log_x == False:
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

# Show plot in Streamlit
st.pyplot(fig)

