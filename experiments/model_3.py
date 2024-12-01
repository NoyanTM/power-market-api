import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from math import sqrt

# Load the dataset
file_path = 'data.csv'  # Replace with your actual file path
df = pd.read_csv(file_path, index_col='date', parse_dates=True)

# Convert 'fact' and 'plan' columns to numeric
df['fact'] = pd.to_numeric(df['fact'].str.replace(',', '.'), errors='coerce')
df['plan'] = pd.to_numeric(df['plan'].str.replace(',', '.'), errors='coerce')
df = df.drop(columns=['object_name', 'unit'], errors='ignore')

# Create lag features for 'fact'
look_back = 24
for i in range(1, look_back + 1):
    df[f'lag_{i}'] = df['fact'].shift(i)

# Drop rows with NaN values created by lag features
df = df.dropna()

# Define train and test sizes
total_size = len(df)
test_size = int(total_size * 0.3)
train_size = total_size - test_size

# Initialize model and lists to store predictions and observed values
model = XGBRegressor(objective='reg:squarederror')

# Set forecast horizon to 48 hours (2 days)
forecast_horizon = 48

# Split data into training and test sets
train_df = df.iloc[:train_size]
test_df = df.iloc[train_size:train_size + forecast_horizon]  # Limit test set to only the next 48 hours

# Define training and testing data
X_train = train_df.drop(['fact'], axis=1)
y_train = train_df['fact']
X_test = test_df.drop(['fact'], axis=1)
y_test = test_df['fact']

# Train the model and forecast the next 2 days (48 hours)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# Calculate RMSE, MSE, and MAE for the 2-day forecast
mse = mean_squared_error(y_test, predictions)
rmse = sqrt(mse)
mae = mean_absolute_error(y_test, predictions)

print(f'MSE for 2-Day Forecast: {mse:.3f}')
print(f'RMSE for 2-Day Forecast: {rmse:.3f}')
print(f'MAE for 2-Day Forecast: {mae:.3f}')

# Plotting the 2-day forecast vs actual values
plt.figure(figsize=(10, 6))
plt.plot(y_test.values, label='Actual', color='blue', marker='o')
plt.plot(predictions, label='Predicted', color='red', linestyle='--', marker='x')
plt.title('XGBoost 2-Day Forecast vs Actual')
plt.xlabel('Time (Hourly)')
plt.ylabel('Fact')
plt.legend()
plt.tight_layout()
plt.show()
