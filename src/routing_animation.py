import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from predict import LinkFailurePredictor


class MANETAnimation:

    def __init__(self, dataset_path):

        print("Loading dataset...")
        self.df = pd.read_csv(dataset_path)

        print("Loading ML predictor...")
        self.predictor = LinkFailurePredictor()

        self.times = sorted(self.df["time"].unique())

        # store reliability metrics
        self.ml_scores = []
        self.baseline_scores = []
        self.time_points = []


    def build_graph(self, snapshot, radius = 100):

        G = nx.Graph()

        nodes = snapshot["node_id"].values

        for n in nodes:
            G.add_node(int(n))

        rows = snapshot.to_dict("records")

        edge_features = []
        edge_pairs = []

        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):

                n1 = int(rows[i]["node_id"])
                n2 = int(rows[j]["node_id"])

                if n1 == n2:
                    continue

                x1, y1 = rows[i]["x"], rows[i]["y"]
                x2, y2 = rows[j]["x"], rows[j]["y"]

                dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

                if dist <= radius:

                    features = [
                        rows[i]["neighbor_count"],
                        rows[i]["x"],
                        rows[i]["y"],
                        rows[i]["time"]
                    ]

                    edge_pairs.append((n1, n2))
                    edge_features.append(features)

        if len(edge_features) > 0:

            X = np.array(edge_features)

            reliabilities, _ = self.predictor.predict(X)

            for (u, v), r in zip(edge_pairs, reliabilities):

                # weight = 1 / (float(r) + 1e-6)            # w = 1/R
                weight = -np.log(float(r) + 1e-6)           # w = -log(R + ε)

                G.add_edge(u, v, weight = weight, reliability=float(r))

        return G


    def path_reliability(self, G, path):

        if path is None:
            return None

        reliabilities = []

        for u, v in zip(path[:-1], path[1:]):
            reliabilities.append(G[u][v]["reliability"])

        if len(reliabilities) == 0:
            return None

        return np.mean(reliabilities)


    def animate(self):

        fig, ax = plt.subplots(figsize = (8, 6))

        def update(frame):

            ax.clear()

            t = self.times[frame]

            snapshot = self.df[self.df["time"] == t]

            G = self.build_graph(snapshot)

            pos = {}

            for _, row in snapshot.iterrows():
                pos[int(row["node_id"])] = (row["x"], row["y"])

            source = 0
            target = 5

            # ML reliability path
            try:
                ml_path = nx.shortest_path(G, source, target, weight="weight")
            except nx.NetworkXNoPath:
                ml_path = None

            # Baseline shortest-hop path
            try:
                baseline_path = nx.shortest_path(G, source, target)
            except nx.NetworkXNoPath:
                baseline_path = None


            # Reliability tracking 

            ml_rel = self.path_reliability(G, ml_path)
            baseline_rel = self.path_reliability(G, baseline_path)

            if ml_rel is not None and baseline_rel is not None:

                self.ml_scores.append(ml_rel)
                self.baseline_scores.append(baseline_rel)
                self.time_points.append(t)


            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_size = 150, ax = ax)

            # Edge coloring by reliability
            edge_colors = []
            edge_widths = []

            for u, v, data in G.edges(data = True):

                r = data["reliability"]

                if r > 0.8:
                    edge_colors.append("green")
                    edge_widths.append(2)

                elif r > 0.5:
                    edge_colors.append("orange")
                    edge_widths.append(1.5)

                else:
                    edge_colors.append("red")
                    edge_widths.append(0.8)

            nx.draw_networkx_edges(
                G,
                pos,
                edge_color=edge_colors,
                width=edge_widths,
                alpha=0.5,
                ax=ax
            )

            # Draw baseline route (purple)
            if baseline_path:

                baseline_edges = list(zip(baseline_path[:-1], baseline_path[1:]))

                nx.draw_networkx_edges(
                    G,
                    pos,
                    edgelist=baseline_edges,
                    width=2,
                    edge_color="purple",
                    ax=ax
                )

            # Draw ML route (blue)
            if ml_path:

                ml_edges = list(zip(ml_path[:-1], ml_path[1:]))

                nx.draw_networkx_edges(
                    G,
                    pos,
                    edgelist = ml_edges,
                    width = 3,
                    edge_color = "blue",
                    ax = ax
                )

            nx.draw_networkx_labels(G, pos, font_size = 8, ax = ax)

            ax.set_title(
                f"MANET Routing | time = {t} | blue = ML route | purple = baseline"
            )

            ax.axis("off")


        anim = FuncAnimation(
            fig,
            update,
            frames = len(self.times),
            interval = 500
        )

        plt.show()


        # Reliability comparison plot 

        plt.figure(figsize = (8,5))

        plt.plot(
            self.time_points,
            self.ml_scores,
            label = "ML Routing",
            color = "blue"
        )

        plt.plot(
            self.time_points,
            self.baseline_scores,
            label = "Baseline Routing",
            color = "purple"
        )

        plt.xlabel("Time")
        plt.ylabel("Average Route Reliability")

        plt.title("ML Routing vs Baseline Routing Reliability")

        plt.legend()
        plt.grid(True)

        plt.show()


if __name__ == "__main__":

    animation = MANETAnimation("dataset/manet_dataset.csv")

    animation.animate()