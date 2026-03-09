import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import networkx as nx
import numpy as np

from predict import LinkFailurePredictor


class MLWeightedDijkstra:

    def __init__(self):

        print("Initializing ML predictor...")
        self.predictor = LinkFailurePredictor()
    
    """
        nodes = list of node ids
        edges = list of tuples (nodeA, nodeB, features)
        features = [neighbor_count, x, y, time]
    """
    def build_graph(self, nodes, edges):

        G = nx.Graph()

        for n in nodes:
            G.add_node(n)

        for (u, v, features) in edges:

            print(f"Evaluating link {u}-{v}")

            X = np.array([features])

            reliability, failure_prob = self.predictor.predict(X)

            reliability = float(reliability[0])

            weight = 1 / (reliability + 1e-6)

            G.add_edge(u, v, weight = weight, reliability = reliability)

        return G

    def find_path(self, G, source, target):

        path = nx.shortest_path(G, source, target, weight = "weight")

        return path


if __name__ == "__main__":

    router = MLWeightedDijkstra()

    nodes = [0,1,2,3,4]

    edges = [
        (0,1,[3,120,200,10]),
        (1,2,[2,200,250,10]),
        (0,3,[1,300,100,10]),
        (3,4,[4,250,150,10]),
        (4,2,[2,260,200,10])
    ]

    G = router.build_graph(nodes, edges)

    path = router.find_path(G, 0, 2)

    print("\nBest path based on ML reliability:")
    print(path)

    print("\nEdge reliabilities:")
    for u,v,data in G.edges(data=True):
        print(f"{u}-{v} reliability:", round(data["reliability"],3))