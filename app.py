yaxis=dict(
    title_font=dict(size=20),  # Increase axis label font size
    tickfont=dict(size=16),    # Increase tick label font size
    type='log' if log_y else 'linear',  # Toggle log scale based on checkbox
    showgrid=True,             # Show grid lines
    gridwidth=1,               # Grid line width
    gridcolor='lightgrey',     # Grid line color
    exponentformat='e',        # Use scientific notation
    showexponent='all'         # Show exponent for all numbers
) 