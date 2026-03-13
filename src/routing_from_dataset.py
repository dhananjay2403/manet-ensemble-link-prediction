import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from predict import LinkFailurePredictor


class DatasetRouter:

    def __init__(self):

        print("Initializing predictor...")
        self.predictor = LinkFailurePredictor()

    def load_snapshot(self, csv_path, time_step):

        df = pd.read_csv(csv_path)

        snapshot = df[df["time"] == time_step]

        return snapshot

    def build_graph(self, snapshot, radius = 150):

        G = nx.Graph()

        nodes = snapshot["node_id"].unique()

        for n in nodes:
            G.add_node(int(n))

        rows = snapshot.to_dict("records")

        edge_features = []
        edge_pairs = []

        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):

                n1 = int(rows[i]["node_id"])
                n2 = int(rows[j]["node_id"])

                # remove self loops
                if n1 == n2:
                    continue

                x1, y1 = rows[i]["x"], rows[i]["y"]
                x2, y2 = rows[j]["x"], rows[j]["y"]

                dist = np.sqrt((x1 - x2)**2 + (y1 - y2) ** 2)

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

        X = np.array(edge_features)

        reliabilities, _ = self.predictor.predict(X)

        for (u,v), r in zip(edge_pairs, reliabilities):

            # weight = 1 / (float(r) + 1e-6)        # w = 1/R
            weight = -np.log(float(r) + 1e-6)       # w = -log(R + ε)

            G.add_edge(u, v, weight = weight, reliability = float(r))

        return G


    def visualize_graph(self, G, snapshot, path = None):

        pos = {}

        for _, row in snapshot.iterrows():
            pos[int(row["node_id"])] = (row["x"], row["y"])

        plt.figure(figsize = (8,6))

        nx.draw_networkx_nodes(G, pos, node_size = 300)

        nx.draw_networkx_edges(G, pos, edge_color = "gray", alpha = 0.4)

        # highlight ML route
        if path:

            edges = list(zip(path[:-1], path[1:]))

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist = edges,
                edge_color = "blue",
                width = 3
            )

        nx.draw_networkx_labels(G, pos)

        plt.title("MANET Topology with ML-based Routing")
        plt.axis("off")
        plt.show()


if __name__ == "__main__":

    router = DatasetRouter()

    snapshot = router.load_snapshot(
        "dataset/manet_dataset.csv",
        time_step = 1.0
    )

    G = router.build_graph(snapshot)

    source = 0
    target = 5

    path = nx.shortest_path(G, source, target, weight = "weight")

    print("\nBest ML route from", source, "->", target)
    print(path)

    router.visualize_graph(G, snapshot, path)