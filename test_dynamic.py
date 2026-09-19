from python.dynamic_forecasting import forecast_insurer


forecast = forecast_insurer(
    insurer="LIC",
    months=6,
    model_name="Auto Select"
)

print(forecast)