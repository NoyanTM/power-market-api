# plot_execution.py
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Check if command-line arguments for dates are provided
if len(sys.argv) < 3:
    print("Please provide both start and end dates as arguments.")
    sys.exit(1)

# Retrieve start and end dates from command-line arguments
start_date = pd.to_datetime(sys.argv[1])
end_date = pd.to_datetime(sys.argv[2])

# Specify the full path to your dataset
file_path = 'data.csv'  # Ensure 'data.csv' is in the same directory

# Load the data into a DataFrame
df = pd.read_csv(file_path, index_col='date', parse_dates=True)

# Filter data for the specified date range and object name
obj_name = 'Zadarya'
df_filtered = df[(df.index >= start_date) & (df.index <= end_date) & (df['object_name'] == obj_name)]

if df_filtered.empty:
    print("No data available for the selected period.")
else:
    # Plotting
    plt.figure(figsize=(15, 6))
    plt.plot(df_filtered.index, df_filtered['plan'], label='Plan', color='blue')
    plt.plot(df_filtered.index, df_filtered['fact'], label='Fact', color='orange')
    plt.xlabel('Time')
    plt.ylabel('Value (MWh)')
    plt.legend()
    plt.title(f"Plan vs Fact for {obj_name} from {start_date.date()} to {end_date.date()}")
    plt.show()
