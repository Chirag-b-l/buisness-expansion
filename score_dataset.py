import pandas as pd
import numpy as np

# Input and output file paths
input_file = "bengaluru_restaurant_grid_10k_gridded.csv"
output_file = "bengaluru_restaurant_grid_10k_scored.csv"

# Load dataset
df = pd.read_csv(input_file)

# Normalization function (min-max scaling)
def normalize(series):
    return (series - series.min()) / (series.max() - series.min() + 1e-9)

# Columns needed for calculation
cols_needed = [
    "population_density", "avg_income", "avg_bill_per_person",
    "restaurant_star_rating", "review_count", "avg_review_score",
    "same_cuisine_competitors_1km", "other_cuisine_competitors_1km",
    "office_density", "nightlife_density", "mall_proximity",
    "college_proximity", "parking_availability", "public_transport_connectivity"
]

# Normalize all required features
norm_data = {}
for col in cols_needed:
    if col in df.columns:
        norm_data[col] = normalize(df[col])
    else:
        print(f"⚠️ Warning: Column {col} not found in dataset. Using zeros.")
        norm_data[col] = pd.Series([0] * len(df))

# Apply weighted formula
df["location_score"] = (
    2 * norm_data["population_density"] +
    2 * norm_data["avg_income"] +
    1 * norm_data["avg_bill_per_person"] +
    1 * norm_data["restaurant_star_rating"] +
    0.5 * norm_data["review_count"] +
    1 * norm_data["avg_review_score"] -
    2 * norm_data["same_cuisine_competitors_1km"] -
    0.5 * norm_data["other_cuisine_competitors_1km"] +
    1.5 * norm_data["office_density"] +
    1 * norm_data["nightlife_density"] +
    1 * (1 / (norm_data["mall_proximity"] + 1e-9)) +
    1 * (1 / (norm_data["college_proximity"] + 1e-9)) +
    1 * norm_data["parking_availability"] +
    1 * norm_data["public_transport_connectivity"]
)

# Scale location_score to 1–100 range
df["location_score"] = normalize(df["location_score"]) * 100

# Save new dataset
df.to_csv(output_file, index=False)

print(f"✅ Done! New dataset saved as {output_file}")
