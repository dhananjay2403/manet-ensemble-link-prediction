import pandas as pd
import glob
import xml.etree.ElementTree as ET
import os

DATASET_DIR = "dataset"

dataset_rows = []
flow_stats = {}

print("Scanning dataset directory...")

# Parse FlowMonitor XML files 
xml_files = glob.glob(os.path.join(DATASET_DIR, "manet_flowmon_run*.xml"))
print("XML files found:", len(xml_files))

for xml_file in xml_files:

    filename = os.path.basename(xml_file)
    run_id = int(filename.replace("manet_flowmon_run", "").replace(".xml", ""))

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for flow in root.findall(".//FlowStats"):

        tx = int(flow.attrib.get("txPackets", 0))
        rx = int(flow.attrib.get("rxPackets", 0))
        lost = int(flow.attrib.get("lostPackets", 0))

        delay = flow.attrib.get("delaySum", "0ns").replace("ns", "")
        delay = float(delay)

        flow_stats[run_id] = {
            "tx_packets": tx,
            "rx_packets": rx,
            "lost_packets": lost,
            "delay_sum": delay
        }

print("Flow stats parsed:", len(flow_stats))



# Parse position CSV files 
pos_files = glob.glob(os.path.join(DATASET_DIR, "positions_run*.csv"))
print("Position files found:", len(pos_files))

for pos_file in pos_files:

    filename = os.path.basename(pos_file)
    run_id = int(filename.replace("positions_run", "").replace(".csv", ""))

    df = pd.read_csv(pos_file)

    stats = flow_stats.get(run_id, {
        "tx_packets": 0,
        "rx_packets": 0,
        "lost_packets": 0,
        "delay_sum": 0
    })

    for _, row in df.iterrows():

        dataset_rows.append({
            "run_id": run_id,
            "time": row["time"],
            "node_id": row["nodeId"],
            "x": row["x"],
            "y": row["y"],
            "neighbor_count": row["neighbor_count"],
            "avg_rssi": row["avg_neighbor_rssi_dbm"],
            "tx_packets": stats["tx_packets"],
            "rx_packets": stats["rx_packets"],
            "lost_packets": stats["lost_packets"],
            "delay_sum": stats["delay_sum"]
        })

print("Rows generated:", len(dataset_rows))

df = pd.DataFrame(dataset_rows)

output_path = os.path.join(DATASET_DIR, "manet_dataset.csv")
df.to_csv(output_path, index=False)

print("Dataset saved:", output_path)
print("Total rows:", len(df))