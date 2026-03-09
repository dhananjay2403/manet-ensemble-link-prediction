# Machine Learning–Driven Link Reliability Prediction for MANET Routing

<p align="center">
ML-assisted routing framework for Mobile Ad Hoc Networks using simulation, ensemble learning, and reliability-aware graph algorithms.
</p>

---

## Overview

Mobile Ad Hoc Networks (MANETs) operate in highly dynamic environments where wireless links frequently degrade or fail due to mobility and interference. Traditional routing algorithms typically assume uniform link reliability, which can lead to unstable routes.

This project introduces a **machine learning–assisted routing framework** that predicts link reliability and integrates those predictions into routing decisions.

The system combines **network simulation, machine learning, and graph algorithms** to evaluate how reliability-aware routing compares against traditional shortest-path routing.

---

## System Architecture
# Machine Learning–Driven Link Reliability Prediction for MANET Routing

<p align="center">
ML-assisted routing framework for Mobile Ad Hoc Networks using simulation, ensemble learning, and reliability-aware graph algorithms.
</p>

---

## Overview

Mobile Ad Hoc Networks (MANETs) operate in highly dynamic environments where wireless links frequently degrade or fail due to mobility and interference. Traditional routing algorithms typically assume uniform link reliability, which can lead to unstable routes.

This project introduces a **machine learning–assisted routing framework** that predicts link reliability and integrates those predictions into routing decisions.

The system combines **network simulation, machine learning, and graph algorithms** to evaluate how reliability-aware routing compares against traditional shortest-path routing.

---

## System Architecture


NS-3 MANET Simulation
        ↓
Dataset Generation
        ↓
Feature Extraction
        ↓
ML Link Failure Prediction
(Random Forest + Neural Network)
        ↓
Reliability-Weighted Routing
(Dijkstra)
        ↓
Dynamic Network Visualization


---

## Key Features

- **ML-assisted routing** using link reliability prediction  
- **Ensemble model** combining Random Forest and Neural Network  
- **MANET simulation** with dynamic node mobility  
- **Routing comparison** between ML-driven and baseline shortest-path routing  
- **Animated network topology visualization**  
- **Quantitative evaluation of routing reliability over time**

---

## Visualization

The system animates the network topology and routing behavior over time.

**Link colors**

- 🟢 Reliable link  
- 🟠 Medium reliability  
- 🔴 Unstable link  

**Routing paths**

- 🔵 ML-selected route  
- 🟣 Baseline shortest-path route  

The project also generates a **reliability comparison plot**, showing how ML-based routing performs relative to traditional routing across simulation timesteps.

---

## Technologies

- NS-3 Network Simulator  
- NetAnim (network simulation visualization)
- Python  
- Scikit-learn  
- TensorFlow / Keras  
- NetworkX  
- NumPy, Pandas, Matplotlib  

---

## Running the Project

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the routing animation:
```bash
python src/routing_animation.py
```


This will:

1. Animate the MANET topology  
2. Show ML and baseline routing paths  
3. Generate a reliability comparison plot.

---

## Results

The ML-assisted routing approach demonstrates:

- improved route reliability in many network conditions
- adaptive routing decisions as topology changes
- better avoidance of unstable links compared to baseline routing

---

## Future Work

Potential extensions include:

- incorporating additional wireless features (RSSI, link duration, signal strength)
- exploring reinforcement learning or evolutionary routing algorithms
- evaluating scalability across larger network sizes
- integrating routing decisions directly into NS-3 protocols
