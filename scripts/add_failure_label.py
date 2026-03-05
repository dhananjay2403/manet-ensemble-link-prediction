import pandas as pd

INPUT_FILE = "dataset/manet_raw_dataset.csv"
OUTPUT_FILE = "dataset/manet_dataset.csv"

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print("Rows loaded:", len(df))

# Link failure rule based on signal + density
df["link_failure"] = (
    (df["avg_rssi"] < -75) |
    (df["neighbor_count"] < 2)
).astype(int)

# reliability score (optional)
df["reliability_score"] = (
    df["neighbor_count"] / (df["neighbor_count"].max() + 1)
)

print("Failure distribution:")
print(df["link_failure"].value_counts())

df.to_csv(OUTPUT_FILE, index=False)

print("ML dataset saved to:", OUTPUT_FILE)