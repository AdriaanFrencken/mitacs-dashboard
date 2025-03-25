# Mitacs Data Dashboard

A Streamlit web application for analyzing and visualizing IV (Current-Voltage) curves from CSV data files.

## Features

- Upload and analyze multiple CSV files simultaneously
- Interactive plot visualization using Plotly
- Adjustable plot parameters:
  - Line width
  - Marker size
  - Time range selection
  - Pulse start alignment
  - Threshold adjustment
- Raw data viewing capability for each uploaded file
- Responsive plot layout with customizable dimensions

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)

3. Use the application:
   - Upload one or more CSV files using the file uploader
   - Adjust visualization parameters in the sidebar:
     - Toggle pulse start alignment
     - Set time range for the plot
     - Adjust threshold current value
     - Modify marker size and line width
   - View raw data for each file by expanding the corresponding section
   - Interact with the plot (zoom, pan, hover for details)

## Input File Format

The application expects CSV files with the following columns:
- `Time (s)`: Time values in seconds
- `Current (A)`: Current values in amperes

Comments in the CSV files should be preceded by '#'.

## Requirements

- Python 3.7+
- Streamlit
- Pandas
- NumPy
- Plotly
- Scipy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your chosen license here]


