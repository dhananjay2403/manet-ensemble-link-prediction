#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/internet-module.h"
#include "ns3/aodv-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

int main(int argc, char *argv[])
{
    uint32_t numNodes = 30;

    NodeContainer nodes;
    nodes.Create(numNodes);

    // WIFI
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);

    YansWifiChannelHelper channel = YansWifiChannelHelper::Default();

    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());

    WifiMacHelper mac;
    mac.SetType("ns3::AdhocWifiMac");

    NetDeviceContainer devices = wifi.Install(phy, mac, nodes);

    // MOBILITY
    MobilityHelper mobility;

    Ptr<RandomRectanglePositionAllocator> positionAlloc =
        CreateObject<RandomRectanglePositionAllocator>();

    positionAlloc->SetAttribute(
        "X", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=500.0]"));
    positionAlloc->SetAttribute(
        "Y", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=500.0]"));

    mobility.SetPositionAllocator(positionAlloc);

    mobility.SetMobilityModel(
        "ns3::RandomWaypointMobilityModel",
        "Speed",
        StringValue("ns3::UniformRandomVariable[Min=5.0|Max=20.0]"),
        "Pause",
        StringValue("ns3::ConstantRandomVariable[Constant=1.0]"),
        "PositionAllocator",
        PointerValue(positionAlloc));

    mobility.Install(nodes);

    // INTERNET + AODV
    AodvHelper aodv;
    InternetStackHelper internet;
    internet.SetRoutingHelper(aodv);
    internet.Install(nodes);

    // IP ADDRESSES
    Ipv4AddressHelper ipv4;
    ipv4.SetBase("10.1.1.0", "255.255.255.0");

    Ipv4InterfaceContainer interfaces = ipv4.Assign(devices);

    // TRAFFIC FLOWS
    uint16_t port = 9;

    for (uint32_t i = 0; i < 10; i++)
    {
        uint32_t sender = i;
        uint32_t receiver = numNodes - 1 - i;

        UdpServerHelper server(port + i);
        ApplicationContainer serverApp = server.Install(nodes.Get(receiver));
        serverApp.Start(Seconds(1.0));
        serverApp.Stop(Seconds(60.0));

        UdpClientHelper client(interfaces.GetAddress(receiver), port + i);
        client.SetAttribute("MaxPackets", UintegerValue(5000));
        client.SetAttribute("Interval", TimeValue(Seconds(0.05)));
        client.SetAttribute("PacketSize", UintegerValue(512));

        ApplicationContainer clientApp = client.Install(nodes.Get(sender));
        clientApp.Start(Seconds(2.0));
        clientApp.Stop(Seconds(60.0));
    }

    std::cout << "MANET simulation running with " << numNodes << " nodes" << std::endl;

    // FLOW MONITOR
    FlowMonitorHelper flowmon;
    Ptr<FlowMonitor> monitor = flowmon.InstallAll();

    Simulator::Stop(Seconds(60.0));
    Simulator::Run();

    monitor->SerializeToXmlFile("manet_flowmon.xml", true, true);

    Simulator::Destroy();

    return 0;
}