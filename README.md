# RouteCast | Reliability-Aware Routing for MANETs

<p align="center">

<img src="https://img.shields.io/badge/Python-3.11-blue?logo=python">
<img src="https://img.shields.io/badge/Framework-TensorFlow-orange?logo=tensorflow">
<img src="https://img.shields.io/badge/ML-ScikitLearn-F7931E?logo=scikitlearn">
<img src="https://img.shields.io/badge/Simulation-NS--3-green">
<img src="https://img.shields.io/badge/Visualization-Matplotlib-blue">

</p>

<p align="center">
Predicting unreliable wireless links and using those predictions to choose more stable routes in dynamic mobile networks.
</p>

---

## Project Overview

Mobile Ad Hoc Networks (MANETs) are decentralized wireless networks where nodes communicate directly without fixed infrastructure. Because nodes are constantly moving, wireless links frequently degrade or fail.

Traditional routing algorithms (like shortest-path routing) assume all links are equally reliable. In highly dynamic MANET environments, this assumption often leads to unstable routes and frequent packet loss.

**RouteCast** introduces a machine learning–assisted routing approach that predicts link reliability and integrates those predictions into routing decisions.

The pipeline combines:

- **NS-3 network simulation** to generate realistic MANET mobility traces  
- **Machine learning models** to predict link reliability  
- **Reliability-weighted routing** to avoid unstable links  

By incorporating predicted link reliability into routing decisions, the system can select **more stable routes compared to traditional shortest-path routing.**

---

## Demo

*(Add your animation GIF here)*


`![demo](assets/demo.gif)`


**Link colors**

| Color | Meaning |
|------|------|
| 🟢 | Reliable link |
| 🟠 | Medium reliability |
| 🔴 | Unstable link |

**Routing paths**

| Color | Meaning |
|------|------|
| 🔵 | ML-selected route |
| 🟣 | Baseline shortest-path route |

---

## Architecture
Add the architecture image at `assets/architecture.jpg`. 

Flow (left → right):  
`ns-3 simulation → dataset (XML→CSV) → feature extraction (neighbor_count, x, y, t) → RandomForest & NeuralNet → ensemble → reliability-weighted Dijkstra → visualization (Matplotlib / NetAnim)`

Also add:
1️⃣ **Architecture diagram**  
2️⃣ **Routing animation GIF**  
3️⃣ **Reliability comparison plot**

---

## Running the project

```bash
# 1. create a virtual environment
python -m venv venv
source venv/bin/activate
```

```bash
# 2. install dependencies
pip install -r requirements.txt
```

```bash
# 3. run the MANET routing animation (uses dataset/manet_dataset.csv)
python src/routing_animation.py
```

```bash
# 4. you can also explore model training and evaluation:
jupyter lab notebooks/training.ipynb
```

If you want to re-run simulations with your local ns-3:

```bash
# copy simulation to your ns-3 scratch folder (script already does this)
./scripts/run_simulations.sh
```

---

## Dataset (summary)

<!-- - ~54,000 samples from 30 runs (30 runs × 1,800 samples each)
- Features: neighbor_count, x, y, time
- Target: link_failure (binary, thresholded on lost packets) -->


| Property | Value |
|--------|--------|
| Simulation runs | 30 |
| Nodes | 30 |
| Timesteps | 60 |
| Total samples | ~54,000 |

### Features

| Feature | Description |
|------|------|
| neighbor_count | number of neighboring nodes |
| x, y | node position |
| time | simulation timestep |

### Target

| Label | Meaning |
|------|------|
| link_failure | binary indicator of link breakage |



---

## Key Contributions

• Built a full pipeline from **network simulation → dataset generation → ML model training → routing evaluation**

• Designed an **ensemble model (Random Forest + Neural Network)** to predict MANET link reliability

• Integrated ML predictions into **reliability-weighted Dijkstra routing**

• Demonstrated **~10% improvement in route reliability** over traditional shortest-path routing

• Developed a **dynamic MANET topology visualization** to compare routing strategies

---

## Results (summary)

#### Model Performance

| Metric | Value |
|------|------|
| Ensemble AUC | 0.79 |

#### Routing Performance

| Routing Metric | Baseline | ML Routing |
|------|------|------|
| Avg Route Reliability | 0.658 | **0.723** |
| Avg Hop Count | 3.75 | 3.82 |

**Reliability improvement:** ~9.8%

The ML-assisted routing consistently avoids unstable links and selects routes with higher reliability.

Detailed evaluation plots are available in:

```bash
notebooks/evaluate_routing.ipynb
```

---

## Future work

- Incorporating wireless signal features (RSSI, link duration, signal strength).
- Exploring reinforcement learning–based routing.
- Evaluating performance on larger network sizes.
- Integrating reliability prediction directly into NS-3 routing protocols.

---

## References

[Add primary research paper]


<!-- ---

## TL;DR

| Problem | Solution |
|-------|-------|
| MANET links are unstable and shortest-path routing ignores link quality | Predict link failures using ML and route packets through the most reliable paths | -->