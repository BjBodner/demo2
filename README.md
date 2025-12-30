# Demo2 Project

A collection of data analysis tools and interactive visualizations for financial and mathematical data.

## Overview

This project includes:
- **Data Analysis Module**: Python utilities for loading and cleaning data from CSV files
- **Israeli Stocks Tracker**: Real-time visualization of Tel Aviv Stock Exchange (TASE) data
- **Interactive Parabola Visualization**: Mathematical tool for exploring quadratic functions

## Project Structure

```
demo2/
├── analyze_data.py          # Python data analysis utilities
├── db_connector.py          # Database connection module (placeholder)
├── index.html               # Main project dashboard
├── israeli_stocks.html      # Israeli stocks market tracker
└── parabola_viz.html        # Interactive parabola visualization
```

## Features

### 1. Data Analysis Module (`analyze_data.py`)

Python utilities for data processing and cleaning:

- **`load_data(file_path)`**: Load data from CSV files into pandas DataFrames
- **`clean_data_issues_from_db(df_raw)`**: Clean data by:
  - Removing duplicate rows
  - Converting negative values to absolute values
  - Filling missing numeric values with column means
  - Filling missing categorical values with column modes

**Requirements:**
- Python 3.x
- NumPy
- Pandas

**Usage:**
```python
import analyze_data

# Load data from CSV
df = analyze_data.load_data('data.csv')

# Clean the data
df_cleaned = analyze_data.clean_data_issues_from_db(df)
```

### 2. Israeli Stocks Tracker

An interactive dashboard for monitoring Israeli stock market data using TradingView widgets.

**Features:**
- Real-time ticker tape with major Israeli indices (TA-35, TA-125)
- Market overview with leading Israeli stocks
- Hot lists showing trending securities on TASE
- Hebrew (RTL) interface support

**Tracked Securities:**
- Bank Leumi (TASE:LUMI)
- Bank Hapoalim (TASE:POLI)
- Teva Pharmaceutical (NYSE:TEVA)
- NICE Systems (NASDAQ:NICE)
- ICL Group (NYSE:ICL)
- Bezeq (TASE:BEZQ)
- Elbit Systems (NASDAQ:ESLT)
- And more...

**Access:** Open `israeli_stocks.html` in a web browser

### 3. Interactive Parabola Visualization

A mathematical visualization tool for exploring quadratic functions of the form: **y = ax² + bx + c**

**Features:**
- Real-time graph updates
- Interactive sliders for coefficients a, b, and c
- Visual coordinate axes
- Responsive canvas rendering

**Controls:**
- **a slider**: Adjust the quadratic coefficient (-5 to 5)
- **b slider**: Adjust the linear coefficient (-10 to 10)
- **c slider**: Adjust the constant term (-100 to 100)

**Access:** Open `parabola_viz.html` in a web browser

## Getting Started

### Prerequisites

For Python modules:
```bash
pip install numpy pandas
```

For HTML visualizations:
- Any modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Project

1. **View the Dashboard:**
   ```bash
   # Open index.html in your browser
   open index.html  # macOS
   start index.html # Windows
   xdg-open index.html # Linux
   ```

2. **Use Python Data Analysis:**
   ```bash
   python3
   >>> import analyze_data
   >>> df = analyze_data.load_data('your_data.csv')
   >>> cleaned_df = analyze_data.clean_data_issues_from_db(df)
   ```

## Navigation

The project includes a central dashboard (`index.html`) with links to all visualizations:
- Israeli Stocks Analysis
- Interactive Parabola Visualization

Each visualization page includes a "Back to Index" button for easy navigation.

## Technologies Used

- **Python**: NumPy, Pandas
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Canvas API for rendering
- **TradingView**: Financial market widgets
- **Hebrew (RTL) Support**: Internationalization for Israeli markets

## Notes

- Israeli stocks data is provided by TradingView and may be delayed
- The parabola visualization uses HTML5 Canvas for rendering
- Data cleaning utilities handle both numeric and categorical data types

## License

This project is for demonstration purposes.

## Contributing

Feel free to fork this repository and submit pull requests for improvements.
