import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import os


def find_pulse_start(df, baseline_interval=[0.0, 1.0]):
    # Find the index of the first row where the current is greater than 0.1 A
    df_slice = df[(df['Time (s)'] >= baseline_interval[0]) & (df['Time (s)'] <= baseline_interval[1])]
    average_baseline_current = df_slice['Current (A)'].mean()
    print(f"Average baseline current: {average_baseline_current} A")
    pulse_start_index = df[df['Current (A)'] > 1e-7].index[0]
    pulse_start_time = df.loc[pulse_start_index - 1, 'Time (s)']
    return pulse_start_index, pulse_start_time

# Get list of CSV files from DATA folder
data_folder = 'DATA'
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
print(csv_files)

# Create a figure for all curves
fig = go.Figure()

# Process each CSV file
for csv_file in csv_files:
    data_path = os.path.join(data_folder, csv_file)
    # Read the CSV file
    df = pd.read_csv(data_path, comment='#')
    
    pulse_start_index, pulse_start_time = find_pulse_start(df)
    print(f"Pulse start index: {pulse_start_index}")
    print(f"Pulse start time: {pulse_start_time} seconds")
    
    # Slice dataframe for time between 2-4 seconds
    time_min = -0.2
    time_max = 1.2
    
    # Align time to pulse start
    df['Aligned_time (s)'] = df['Time (s)'] - pulse_start_time
    
    df_slice = df[(df['Aligned_time (s)'] >= time_min) & (df['Aligned_time (s)'] <= time_max)]
    
    fig.add_scatter(x=df_slice['Aligned_time (s)'], y=df_slice['Current (A)'],
                    name=csv_file, mode='markers+lines', 
                    line=dict(width=1),
                    marker=dict(symbol='circle', size=3))

# Update layout for better visualization
fig.update_layout(
    showlegend=True,
    legend_title_text='File Name',
    xaxis_title='Time (s)',
    yaxis_title='Current (A)',
    font = dict(size=30)
)

# Show the figure
fig.show()
