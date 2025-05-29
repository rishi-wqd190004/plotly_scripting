import pickle
import pandas as pd
import numpy as np

def load_model(path='rf_co2_mdl.pkl'):
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_training_cols(path='training_cols.txt'):
    with open(path, 'rb') as fp:
        return pickle.load(fp)
    
def parse_years_input(input_str):
    try:
        # Split by comma, strip spaces, convert to int
        years = [int(year.strip()) for year in input_str.split(',') if year.strip().isdigit()]
        return sorted(set(years))  # Remove duplicates and sort
    except Exception:
        return []
    
def predict_future_emissions_v3(selected_country, base_df, mdl, training_cols, years_to_predict=[2022, 2023, 2024]):
    # Filter for the country and sort by year
    country_df = base_df[base_df['Nation'] == selected_country].sort_values('Year')

    if len(country_df) < 2:
        # Not enough data to compute trend
        return pd.DataFrame()

    last_known = country_df.iloc[-1].copy()
    prev_known = country_df.iloc[-2].copy()

    # Emission columns
    emission_cols = [
        'Emissions from solid fuel consumption',
        'Emissions from liquid fuel consumption',
        'Emissions from gas fuel consumption',
        'Emissions from cement production',
        'Emissions from gas flaring',
        'Emissions from bunker fuels (not included in the totals)'
    ]

    # Estimate safe percent changes
    pct_changes = {}
    for col in emission_cols:
        prev_val = prev_known[col]
        last_val = last_known[col]

        if prev_val == 0 or pd.isna(prev_val) or pd.isna(last_val):
            pct_changes[col] = 0.0
        else:
            pct_changes[col] = (last_val - prev_val) / abs(prev_val)

    future_preds = []

    for year in years_to_predict:
        future_row = last_known.copy()
        future_row['Year'] = year

        for col in emission_cols:
            future_val = future_row[col] * (1 + pct_changes[col])
            # Clamp to 0 if negative due to extrapolation
            future_row[col] = max(future_val, 0)

        # Create input DataFrame
        input_df = pd.DataFrame([future_row])

        # One-hot encode
        input_df_encoded = pd.get_dummies(input_df)
        input_df_encoded = input_df_encoded.reindex(columns=training_cols, fill_value=0)

        # Ensure no infinite or NaN
        input_df_encoded.replace([np.inf, -np.inf], np.nan, inplace=True)
        input_df_encoded.fillna(0, inplace=True)

        # Predict
        pred_value = mdl.predict(input_df_encoded)[0]

        future_preds.append({
            'Nation': selected_country,
            'Year': year,
            'Predicted_CO2': pred_value
        })

        # Use this row for next year prediction
        last_known = future_row.copy()

    return pd.DataFrame(future_preds)

    
def predict_all_countries(df, training_cols=None, model=None, years_to_predict=[2022, 2023, 2024]):
    if model is None:
        model = load_model()
    
    if training_cols is None:
        training_cols = load_training_cols()

    all_preds = []

    for country in df['Nation'].unique():
        country_preds = predict_future_emissions_v3(
            selected_country=country,
            base_df=df,
            mdl=model,
            training_cols=training_cols,
            years_to_predict=years_to_predict
        )

        if not country_preds.empty:
            country_preds['Source'] = 'Predicted'
            country_preds.rename(columns={'Predicted_CO2': 'CO2'}, inplace=True)
            all_preds.append(country_preds)

    return pd.concat(all_preds, ignore_index=True)

def get_combined_df(df, model, training_cols):
    # Historical
    hist = df[['Nation', 'Year', 'Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)']].copy()
    hist.rename(columns={'Total CO2 emissions from fossil-fuels and cement production (thousand metric tons of C)': 'CO2'}, inplace=True)
    hist['Source'] = 'Actual'

    # Predicted
    future = predict_all_countries(df, training_cols, model)

    # Combine
    return pd.concat([hist, future], ignore_index=True)
