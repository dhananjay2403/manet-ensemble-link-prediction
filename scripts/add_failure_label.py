import pandas as pd
import numpy as np

INPUT_FILE = "dataset/manet_raw_dataset.csv"
OUTPUT_FILE = "dataset/manet_dataset.csv"

df = pd.read_csv(INPUT_FILE)

# base failure condition
base_failure = (
    (df["avg_rssi"] < -75) |
    (df["neighbor_count"] < 2)
)

# introduce randomness (10%)
noise = np.random.rand(len(df)) < 0.10

df["link_failure"] = (base_failure ^ noise).astype(int)

df.to_csv(OUTPUT_FILE, index=False)

print("Dataset saved:", OUTPUT_FILE)
print(df["link_failure"].value_counts())