#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/internet-module.h"
#include "ns3/aodv-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/netanim-module.h"

#include <fstream>
#include <iomanip>
#include <cmath>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("ManetSimulation");

static std::string g_outDir = ".";
static uint32_t g_runId = 0;

// simple log-distance RSSI approximation (d0 = 1m)
double ApproximateRssiDbm(double txPowerDbm, double distanceMeters, double pathLossExp = 3.0)
{
    if (distanceMeters < 0.1) distanceMeters = 0.1;
    // free-space reference at d0 = 1 m is ignored; we use a simple model:
    // RSSI_dBm = txPower_dBm - 10 * n * log10(distance)
    double loss = 10.0 * pathLossExp * std::log10(distanceMeters);
    return txPowerDbm - loss;
}

void SamplePositionsAndWrite(NodeContainer nodes, double sampleTimeSec, double neighborRadius, double txPowerDbm)
{
    std::ostringstream fname;
    fname << g_outDir << "/positions_run" << g_runId << ".csv";

    // If it's the first sample (file may not exist), open append mode but write header if new.
    std::ofstream ofs;
    bool writeHeader = false;
    if (sampleTimeSec <= 1.0) {
        // first sample, overwrite previous results for the run
        ofs.open(fname.str(), std::ofstream::out);
        writeHeader = true;
    } else {
        ofs.open(fname.str(), std::ofstream::out | std::ofstream::app);
    }

    if (!ofs.is_open()) {
        NS_LOG_WARN("Could not open positions file: " << fname.str());
        return;
    }

    if (writeHeader) {
        ofs << "time,nodeId,x,y,neighbor_count,avg_neighbor_rssi_dbm\n";
    }

    uint32_t n = nodes.GetN();

    // collect positions
    std::vector<Vector> pos(n);
    for (uint32_t i = 0; i < n; ++i) {
        Ptr<MobilityModel> mm = nodes.Get(i)->GetObject<MobilityModel>();
        pos[i] = mm->GetPosition();
    }

    // for each node, compute neighbors and average RSSI to neighbors
    for (uint32_t i = 0; i < n; ++i) {
        uint32_t neighbors = 0;
        double rssi_sum = 0.0;
        for (uint32_t j = 0; j < n; ++j) {
            if (i == j) continue;
            double dx = pos[i].x - pos[j].x;
            double dy = pos[i].y - pos[j].y;
            double dist = std::sqrt(dx * dx + dy * dy);
            if (dist <= neighborRadius) {
                neighbors++;
                double rssi = ApproximateRssiDbm(txPowerDbm, dist);
                rssi_sum += rssi;
            }
        }
        double avg_rssi = (neighbors > 0) ? (rssi_sum / neighbors) : -1000.0;
        ofs << std::fixed << std::setprecision(3)
            << sampleTimeSec << ","
            << i << ","
            << pos[i].x << ","
            << pos[i].y << ","
            << neighbors << ","
            << avg_rssi << "\n";
    }

    ofs.close();
}

int main(int argc, char *argv[])
{
    // default params (can tune)
    uint32_t numNodes = 30;
    double simTimeSeconds = 60.0;
    double sampleInterval = 1.0;         // seconds between position samples
    double neighborRadius = 100.0;       // meters
    double txPowerDbm = 16.0;            // approximate transmit power (dBm)
    std::string outDir = ".";
    uint32_t rngRun = 1;

    CommandLine cmd;
    cmd.AddValue("numNodes", "Number of nodes", numNodes);
    cmd.AddValue("simTime", "Simulation time (s)", simTimeSeconds);
    cmd.AddValue("sampleInterval", "Position sampling interval (s)", sampleInterval);
    cmd.AddValue("neighborRadius", "Neighbor distance threshold (m)", neighborRadius);
    cmd.AddValue("txPowerDbm", "Tx power (dBm) used for approximate RSSI", txPowerDbm);
    cmd.AddValue("outDir", "Output directory for CSV/XML", outDir);
    cmd.AddValue("runId", "Run identifier", g_runId);
    cmd.AddValue("RngRun", "RNG run seed", rngRun);
    cmd.Parse(argc, argv);

    g_outDir = outDir;
    // create output dir if needed (ns-3 binary may not have permissions if path doesn't exist)
    // Note: writing directories portably from ns-3 is OS-dependent. We assume outDir exists (the runner creates it).

    // Nodes
    NodeContainer nodes;
    nodes.Create(numNodes);

    // WiFi
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);

    YansWifiChannelHelper channel = YansWifiChannelHelper::Default();
    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());

    WifiMacHelper mac;
    mac.SetType("ns3::AdhocWifiMac");

    NetDeviceContainer devices = wifi.Install(phy, mac, nodes);

    // Mobility
    MobilityHelper mobility;
    Ptr<RandomRectanglePositionAllocator> positionAlloc = CreateObject<RandomRectanglePositionAllocator>();
    positionAlloc->SetAttribute("X", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=500.0]"));
    positionAlloc->SetAttribute("Y", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=500.0]"));
    mobility.SetPositionAllocator(positionAlloc);

    mobility.SetMobilityModel(
        "ns3::RandomWaypointMobilityModel",
        "Speed", StringValue("ns3::UniformRandomVariable[Min=5.0|Max=20.0]"),
        "Pause", StringValue("ns3::ConstantRandomVariable[Constant=1.0]"),
        "PositionAllocator", PointerValue(positionAlloc)
    );

    mobility.Install(nodes);

    // Internet + AODV
    AodvHelper aodv;
    InternetStackHelper internet;
    internet.SetRoutingHelper(aodv);
    internet.Install(nodes);

    // IP addressing
    Ipv4AddressHelper ipv4;
    ipv4.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = ipv4.Assign(devices);

    // Multiple flows
    uint16_t basePort = 9000;
    for (uint32_t i = 0; i < std::min<uint32_t>(10, numNodes/2); ++i) {
        uint32_t sender = i;
        uint32_t receiver = numNodes - 1 - i;

        UdpServerHelper server(basePort + i);
        ApplicationContainer serverApp = server.Install(nodes.Get(receiver));
        serverApp.Start(Seconds(1.0));
        serverApp.Stop(Seconds(simTimeSeconds));

        UdpClientHelper client(interfaces.GetAddress(receiver), basePort + i);
        client.SetAttribute("MaxPackets", UintegerValue(50000));
        client.SetAttribute("Interval", TimeValue(Seconds(0.05))); // 20 pkt/s
        client.SetAttribute("PacketSize", UintegerValue(512));
        ApplicationContainer clientApp = client.Install(nodes.Get(sender));
        clientApp.Start(Seconds(2.0));
        clientApp.Stop(Seconds(simTimeSeconds));
    }

    // FlowMonitor
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    // Schedule periodic sampling of positions
    double t = sampleInterval;
    while (t <= simTimeSeconds) {
        Simulator::Schedule(Seconds(t), &SamplePositionsAndWrite, nodes, t, neighborRadius, txPowerDbm);
        t += sampleInterval;
    }

    // Run
    Simulator::Stop(Seconds(simTimeSeconds));

    AnimationInterface anim("manet_animation.xml");
    Simulator::Run();

    // Serialize flow monitor output to outDir with run id
    std::ostringstream xmlname;
    xmlname << outDir << "/manet_flowmon_run" << g_runId << ".xml";
    monitor->SerializeToXmlFile(xmlname.str(), true, true);

    Simulator::Destroy();

    return 0;
}