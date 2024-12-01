from prophet import Prophet
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt
import matplotlib.pyplot as plt

# Load data (update the path to your actual file path)
file_path = 'data.csv'
df = pd.read_csv(file_path, index_col='date', parse_dates=True)

# Preprocess data
df['fact'] = pd.to_numeric(df['fact'].replace(',', '.', regex=True), errors='coerce')
df['Cloudiness'] = pd.to_numeric(df['Cloudiness'], errors='coerce')
df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
df = df.dropna(subset=['fact', 'Cloudiness', 'Temperature'])  # Drop rows with NaNs in key columns

# Prepare data in the format expected by Prophet
df_prophet = pd.DataFrame({
    'ds': df.index,
    'y': df['fact'],
    'Cloudiness': df['Cloudiness'],
    'Temperature': df['Temperature']
})

# Split the data into training and test sets
train_size = int(len(df_prophet) * 0.7)
train_df = df_prophet.iloc[:train_size]
test_df = df_prophet.iloc[train_size:]

# Set the forecast horizon to 48 hours (2 days)
forecast_horizon = 48

# Initialize and fit the Prophet model on the training data
model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
model.add_regressor('Cloudiness')
model.add_regressor('Temperature')
model.fit(train_df)

# Prepare the future DataFrame for forecasting the next 2 days
future = test_df.iloc[:forecast_horizon][['ds', 'Cloudiness', 'Temperature']]

# Forecast the next 2 days
forecast = model.predict(future)

# Extract predictions and observed values
predictions = forecast['yhat'].values
observed = test_df.iloc[:forecast_horizon]['y'].values

# Calculate MSE, RMSE, and MAE for the 2-day forecast
mse = mean_squared_error(observed, predictions)
rmse = sqrt(mse)
mae = mean_absolute_error(observed, predictions)

print(f'MSE for 2-Day Forecast: {mse:.3f}')
print(f'RMSE for 2-Day Forecast: {rmse:.3f}')
print(f'MAE for 2-Day Forecast: {mae:.3f}')

# Plotting the 2-day forecast vs actual values
plt.figure(figsize=(10, 6))
plt.plot(future['ds'], observed, label='Observed', color='blue', marker='o')
plt.plot(future['ds'], predictions, label='Predicted', color='red', linestyle='--', marker='x')
plt.legend()
plt.xlabel('Date')
plt.ylabel('Fact')
plt.title('FB Prophet 2-Day Forecast vs Actual')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
