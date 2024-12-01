import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
from xgboost import XGBRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet

from src.constants import AvailableModel


def create_prediction(df: pd.DataFrame, model_type: AvailableModel, forecast_horizon: int):
    # Data preprocessing
    df = df.copy(deep=True)
    df['fact'] = pd.to_numeric(df['fact'].str.replace(',', '.', regex=True), errors='coerce')
    df['plan'] = pd.to_numeric(df['plan'].str.replace(',', '.', regex=True), errors='coerce')
    df['cloudiness'] = pd.to_numeric(df['cloudiness'], errors='coerce')
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
    df = df.dropna(subset=['fact', 'cloudiness', 'temperature'])
    df = df.drop(columns=['object_name', 'unit'], errors='ignore')

    # Ensure datetime index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.asfreq('h')

    # Split data into train and test
    series = df['fact']
    total_size = len(series)
    if total_size < 30:
        raise ValueError("Insufficient data. At least 30 observations are required.")
    
    test_size = int(total_size * 0.3)
    train, test = series.iloc[:-test_size], series.iloc[-test_size:]

    if model_type == "SARIMA":
        model = SARIMAX(train, order=(2, 1, 2), seasonal_order=(1, 0, 1, 24))
        model_fit = model.fit(disp=False)
        yhat = model_fit.forecast(steps=forecast_horizon)
        predicted = yhat.tolist()
        observed = test.iloc[:forecast_horizon].tolist()
    
    if model_type == "FB_PROPHET":
        df_prophet = df.reset_index().rename(columns={"date": "ds", "fact": "y"})
        prophet_model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
        prophet_model.add_regressor('cloudiness')
        prophet_model.add_regressor('temperature')
        prophet_model.fit(df_prophet[:-test_size])

        future = prophet_model.make_future_dataframe(periods=forecast_horizon, freq='H')
        future = pd.merge(future, df[['cloudiness', 'temperature']], left_on='ds', right_index=True, how='left')
        forecast = prophet_model.predict(future)
        predicted = forecast['yhat'].iloc[-forecast_horizon:].tolist()
        observed = test.iloc[:forecast_horizon].tolist()
    
    if model_type == "XGBOOST":
        lag_features = ['cloudiness', 'temperature']
        df_lags = df.copy()
        look_back = 24
        for i in range(1, look_back + 1):
            df_lags[f'lag_{i}'] = df_lags['fact'].shift(i)
        df_lags = df_lags.dropna()
        X = df_lags.drop(columns=['fact'])
        y = df_lags['fact']
        X_train, X_test = X.iloc[:-test_size], X.iloc[-test_size:]
        y_train, y_test = y.iloc[:-test_size], y.iloc[-test_size:]

        xgb_model = XGBRegressor(objective='reg:squarederror')
        xgb_model.fit(X_train, y_train)
        yhat = xgb_model.predict(X_test.iloc[:forecast_horizon])
        predicted = yhat.tolist()
        observed = y_test.iloc[:forecast_horizon].tolist()

    # Calculate metrics
    mse = round(mean_squared_error(observed, predicted), 3)
    rmse = round(np.sqrt(mse), 3)
    mae = round(mean_absolute_error(observed, predicted), 3)

    # Visualization
    observed_series = pd.Series(observed, index=test.index[:forecast_horizon])
    predicted_series = pd.Series(predicted, index=test.index[:forecast_horizon])

    fig = go.Figure(
        data=[
            go.Scatter(x=observed_series.index, y=observed_series.values, name='Actual', mode='lines+markers', line=dict(color="royalblue")),
            go.Scatter(x=predicted_series.index, y=predicted_series.values, name='Predicted', mode='lines+markers', line=dict(color="firebrick"))
        ],
        layout=go.Layout(
            title=f'{model_type} predicted vs actual values for {forecast_horizon} hours' + f"<br>MSE: {mse}, RMSE: {rmse}, MAE: {mae}",
            xaxis_title='Time',
            yaxis_title='Fact'
        )
    )
    return fig.to_html()
