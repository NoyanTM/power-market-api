# Set the frequency to hourly ('h')
series = df['fact']
series.index = pd.to_datetime(series.index)
series = series.asfreq('h')

# Split the data into train and test sets
total_size = len(series)
test_size = int(total_size * 0.3)
train, test = series.iloc[:-test_size], series.iloc[-test_size:]

# Forecast horizon of 2 days (48 hours)
forecast_horizon = 48

# Define a SARIMA model with daily seasonality (assuming s=24 for hourly data)
model = SARIMAX(train, order=(2, 1, 2), seasonal_order=(1, 0, 1, 24))
model_fit = model.fit(disp=False)

# Forecast for the next 48 hours
yhat = model_fit.forecast(steps=forecast_horizon)
predictions = yhat.tolist()

# Get the first 48 hours of actual values for comparison
observed = test.iloc[:forecast_horizon]

# Calculate MSE, RMSE, and MAE
mse = mean_squared_error(observed, predictions)
rmse = np.sqrt(mse)
mae = mean_absolute_error(observed, predictions)

print(f'MSE for 2-Day Forecast: {mse:.3f}')
print(f'RMSE for 2-Day Forecast: {rmse:.3f}')
print(f'MAE for 2-Day Forecast: {mae:.3f}')

# Convert predictions and observed values to pandas Series for easy plotting
predictions_series = pd.Series(predictions, index=test.index[:forecast_horizon])
observed_series = pd.Series(observed.values, index=test.index[:forecast_horizon])

# Plotting
plt.figure(figsize=(10, 6))
observed_series.plot(label='Actual', color='blue', marker='o')
predictions_series.plot(label='Forecast', color='red', linestyle='--', marker='x')

plt.title('SARIMA Forecast (2 days) vs Actual Values')
plt.xlabel('Date')
plt.ylabel('Fact')
plt.legend()
plt.show()
