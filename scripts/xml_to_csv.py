import xml.etree.ElementTree as ET
import pandas as pd
import glob

files = glob.glob("dataset/manet_flowmon_*.xml")

rows = []

for file in files:
    tree = ET.parse(file)
    root = tree.getroot()

    for flow in root.iter("FlowStats"):

        rows.append({
            "flow_id": flow.attrib.get("flowId", 0),
            "tx_packets": int(flow.attrib.get("txPackets", 0)),
            "rx_packets": int(flow.attrib.get("rxPackets", 0)),
            "lost_packets": int(flow.attrib.get("lostPackets", 0)),
            "delay_sum": float(flow.attrib.get("delaySum", "0").replace("ns",""))
        })

df = pd.DataFrame(rows)

df.to_csv("dataset/manet_dataset.csv", index=False)

print("Dataset created with", len(df), "rows")