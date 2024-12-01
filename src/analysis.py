import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_analysis(df: pd.DataFrame) -> str:
    df_correlation_matrix = df.copy(deep=True)
    for col in ['plan', 'fact', 'cloudiness', 'temperature', 'wind_speed']:
        df_correlation_matrix[col] = df_correlation_matrix[col].astype(str).str.replace(',', '.').astype(float)
    correlation_matrix = df_correlation_matrix[['plan', 'fact', 'cloudiness', 'temperature', 'wind_speed']].corr()
    # matrix_json_str: str = correlation_matrix.to_json(orient="records")
    # matrix_dict: list[dict] = json.loads(matrix_json_str)

    df_weather_temperature = df.copy(deep=True)
    df_weather_temperature['year'] = df_weather_temperature['date'].dt.year
    df_weather_temperature['hour'] = df_weather_temperature['date'].dt.hour
    df_weather_temperature['day_of_year'] = df_weather_temperature['date'].dt.dayofyear
    weather_pivot = df_weather_temperature.reset_index().pivot_table(index='hour', columns='day_of_year', values='temperature')
    weather_pivot = weather_pivot.fillna(0)
    x_weather = weather_pivot.columns.values
    y_weather = weather_pivot.index.values
    x_weather, y_weather = np.meshgrid(x_weather, y_weather)
    z_weather = weather_pivot.values
    # weather_dict = {"x": X.tolist(), "y": Y.tolist(), "z": Z.tolist()} # x, y, z
    
    df_solar_generation = df.copy(deep=True)
    df_solar_generation['fact'] = df_solar_generation['fact'].str.replace(',', '.').astype(float)
    df_solar_generation['year'] = df_solar_generation['date'].dt.year
    df_solar_generation['hour'] = df_solar_generation['date'].dt.hour
    df_solar_generation['month'] = df_solar_generation['date'].dt.month
    df_solar_generation['day_of_year'] = df_solar_generation['date'].dt.dayofyear
    solar_pivot = df_solar_generation.reset_index().pivot_table(index='hour', columns='day_of_year', values='fact')
    x_solar = solar_pivot.columns.values
    y_solar = solar_pivot.index.values
    x_solar, y_solar = np.meshgrid(x_solar, y_solar)
    z_solar = solar_pivot.values
    # solar_dict = {"x": X.tolist(), "y": Y.tolist(), "z": Z.tolist()}
    
    df_comparison = df.copy(deep=True)
    df_comparison["plan"] = pd.to_numeric(df_comparison["plan"].replace(',', '', regex=True), errors="coerce")
    df_comparison["fact"] = pd.to_numeric(df_comparison["fact"].replace(',', '', regex=True), errors="coerce")
    # comparison_dict
    
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Correlation matrix",
            "Weather data",
            "Solar generation",
            "Plan and fact comparison",
        ),
        specs=[[{"type": "xy"}, {"type": "scene"}],
           [{"type": "scene"}, {"type": "xy"}]],
    )
    fig.add_trace(
        go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            zmin=-1,
            zmax=1,
            text=np.round(correlation_matrix.values, 4),
            hoverinfo="text",
            showscale=False,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Surface(
            z=z_weather,
            x=x_weather,
            y=y_weather,
            showscale=False,
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Surface(
            z=z_solar,
            x=x_solar,
            y=y_solar,
            showscale=False,
        ),
        row=2,
        col=1,
    ),
    fig.add_trace(
        go.Scatter(
            x=df_comparison.index,
            y=df_comparison["plan"],
            mode="lines",
            name="Plan (Blue)",
            line=dict(color="royalblue"),
        ),
        row=2,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=df_comparison.index,
            y=df_comparison["fact"],
            mode="lines",
            name="Fact (Red)",
            line=dict(color="firebrick"),
        ),
        row=2,
        col=2,
    )
    fig.update_layout(
        title="Analysis results",
        title_x=0.5,
        scene1=dict(
            xaxis=dict(title_text="Day of Year", autorange="reversed"),
            yaxis=dict(title_text="Hour of Day", autorange="reversed"),
            zaxis=dict(title_text="Temperature (°C)"),
        ),
        scene2=dict(
            xaxis=dict(title_text="Day of Year", autorange="reversed"),
            yaxis=dict(title_text="Hour of Day", autorange="reversed"),
            zaxis=dict(title_text="Solar generation (MWh)"),
        ),
        xaxis2=dict(title_text="Time"),
        yaxis2=dict(title_text="Value (MWh)"),
        showlegend=False,
    )
    
    html_content = fig.to_html()
    return html_content
