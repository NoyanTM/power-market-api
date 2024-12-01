import sys
import pandas as pd
import matplotlib.pyplot as plt

# Retrieve start and end dates from command-line arguments
start_date = pd.to_datetime(sys.argv[1])
end_date = pd.to_datetime(sys.argv[2])

# Specify the full path to your dataset
file_path = 'data.csv'  # Ensure 'data.csv' is in the same directory

# Load the data into a DataFrame
df = pd.read_csv(file_path, index_col='date', parse_dates=True)

# Convert 'plan' and 'fact' columns to numeric, handling commas and coercing errors
df['plan'] = pd.to_numeric(df['plan'].replace(',', '', regex=True), errors='coerce')
df['fact'] = pd.to_numeric(df['fact'].replace(',', '', regex=True), errors='coerce')

# Debug: Print the first few rows to verify data structure
print("DataFrame Head:")
print(df.head())

# Debug: Print start and end dates
print(f"Start Date: {start_date}, End Date: {end_date}")

# Filter data for the specified date range and object name
obj_name = 'Zadarya'
df_filtered = df[(df.index >= start_date) & (df.index <= end_date) & (df['object_name'] == obj_name)]

# Filter out rows where both 'plan' and 'fact' are zero or NaN
df_filtered = df_filtered[(df_filtered['plan'].notna() & df_filtered['plan'] != 0) |
                          (df_filtered['fact'].notna() & df_filtered['fact'] != 0)]

# Debug: Print the filtered data to check if it's correct
print("Filtered DataFrame (after removing zero-only rows):")
print(df_filtered)

# Check if the filtered DataFrame is empty
if df_filtered.empty:
    print(f"No data found for {obj_name} between {start_date.date()} and {end_date.date()}.")
    sys.exit(0)  # Exit if no data is available

# Optional: Aggregate data to daily means if there are many timestamps
df_daily = df_filtered[['plan', 'fact']].resample('D').mean()

# Plotting
plt.figure(figsize=(15, 6))
plt.plot(df_daily.index, df_daily['plan'], label='Plan', color='blue')
plt.plot(df_daily.index, df_daily['fact'], label='Fact', color='orange')
plt.xlabel('Time')
plt.ylabel('Value (MWh)')
plt.legend()
plt.title(f"Plan vs Fact for {obj_name} from {start_date.date()} to {end_date.date()}")
plt.grid(True)
plt.show()
