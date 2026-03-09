import pandas as pd
import numpy as np
import networkx as nx

from predict import LinkFailurePredictor


class DatasetRouter:

    def __init__(self):

        print("Initializing predictor...")
        self.predictor = LinkFailurePredictor()

    def load_snapshot(self, csv_path, time_step):

        df = pd.read_csv(csv_path)

        snapshot = df[df["time"] == time_step]

        return snapshot

    def build_graph(self, snapshot, radius=150):

        G = nx.Graph()

        nodes = snapshot["node_id"].unique()

        for n in nodes:
            G.add_node(int(n))

        rows = snapshot.to_dict("records")

        edge_features = []
        edge_pairs = []

        # collect all candidate edges
        for i in range(len(rows)):
            for j in range(i+1, len(rows)):

                n1 = int(rows[i]["node_id"])
                n2 = int(rows[j]["node_id"])

                x1, y1 = rows[i]["x"], rows[i]["y"]
                x2, y2 = rows[j]["x"], rows[j]["y"]

                dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)

                if dist <= radius:

                    features = [
                        rows[i]["neighbor_count"],
                        rows[i]["x"],
                        rows[i]["y"],
                        rows[i]["time"]
                    ]

                    edge_pairs.append((n1, n2))
                    edge_features.append(features)

        if len(edge_features) == 0:
            return G

        # batch prediction
        X = np.array(edge_features)

        reliabilities, _ = self.predictor.predict(X)

        for (u,v), r in zip(edge_pairs, reliabilities):

            weight = 1 / (float(r) + 1e-6)

            G.add_edge(u, v, weight=weight, reliability=float(r))

        return G


if __name__ == "__main__":

    router = DatasetRouter()

    snapshot = router.load_snapshot(
        "dataset/manet_dataset.csv",
        time_step=1.0
    )

    G = router.build_graph(snapshot)

    path = nx.shortest_path(G, 0, 5, weight = "weight")

    print("\nBest ML route from 0 → 5:")
    print(path)

    print("\nEdge reliabilities:")

    for u,v,data in G.edges(data = True):
        print(f"{u}-{v}:", round(data["reliability"],3))