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

    def build_graph(self, snapshot, radius = 150):

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

                    edge_pairs.append((n1,n2))
                    edge_features.append(features)

        if len(edge_features) > 0:

            X = np.array(edge_features)

            reliabilities,_ = self.predictor.predict(X)

            for (u,v), r in zip(edge_pairs, reliabilities):

                weight = 1/(float(r) + 1e-6)

                G.add_edge(u,v, weight = weight, reliability = float(r))

        return G

    def animate(self):

        fig, ax = plt.subplots(figsize = (8,6))

        def update(frame):

            ax.clear()

            t = self.times[frame]

            snapshot = self.df[self.df["time"] == t]

            G = self.build_graph(snapshot)

            pos = {}

            for _,row in snapshot.iterrows():
                pos[int(row["node_id"])] = (row["x"], row["y"])

            source = 0
            target = 5

            try:
                path = nx.shortest_path(G, source, target, weight="weight")
            except:
                path = None

            nx.draw_networkx_nodes(G,pos,node_size = 250,ax = ax)
            nx.draw_networkx_edges(G,pos,alpha = 0.3,ax = ax)
            nx.draw_networkx_labels(G,pos,font_size = 8,ax = ax) 

            if path:

                route_edges = list(zip(path[:-1],path[1:]))

                nx.draw_networkx_edges(
                    G,
                    pos,
                    edgelist = route_edges,
                    width = 3,
                    edge_color = "blue",
                    ax = ax
                )

            ax.set_title(f"ML Routing at time = {t}")
            ax.axis("off")

        anim = FuncAnimation(
            fig,
            update,
            frames = len(self.times),
            interval = 500
        )

        plt.show()


if __name__ == "__main__":

    animation = MANETAnimation("dataset/manet_dataset.csv")

    animation.animate()