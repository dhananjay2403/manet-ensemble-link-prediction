from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras


class LinkFailurePredictor:

    def __init__(self):

        print("Loading models...")

        project_root = Path(__file__).resolve().parent.parent
        models_dir = project_root / "models"

        rf_path = models_dir / "random_forest.pkl"
        nn_path = models_dir / "neural_network.keras"

        if not rf_path.exists():
            raise FileNotFoundError(f"Random Forest model not found: {rf_path}")
        
        if not nn_path.exists():
            raise FileNotFoundError(f"Neural Network model not found: {nn_path}")

        self.rf = joblib.load(rf_path)

        self.nn = keras.models.load_model(nn_path, compile = False)

        print("Models loaded successfully.")
        

    def predict(self, X):

        feature_names = ["neighbor_count", "x", "y", "time"]

        X_df = pd.DataFrame(X, columns=feature_names)

        # Random Forest
        rf_probs = self.rf.predict_proba(X_df)[:,1]

        # Neural Network
        nn_probs = self.nn(X_df.values).numpy().flatten()

        # Ensemble
        ensemble_probs = (0.4 * rf_probs) + (0.6 * nn_probs)

        reliability = 1 - ensemble_probs

        return reliability, ensemble_probs


if __name__ == "__main__":

    predictor = LinkFailurePredictor()

    sample = np.array([
        [3, 120, 200, 10],   # neighbor_count, x, y, time
        [1, 450, 300, 15]
    ])

    reliability, failure_prob = predictor.predict(sample)

    print("\nPredictions")
    print("-----------")

    for i in range(len(sample)):
        print(f"Sample {i + 1}")
        print("Failure probability:", round(failure_prob[i], 3))
        print("Reliability score:", round(reliability[i], 3))
        print()  