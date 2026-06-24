from diagrams import Cluster, Diagram, Edge
from diagrams.azure.network import VirtualNetworks, VirtualNetworkGateways, RouteTables
from diagrams.azure.compute import VM

# Adjust diagram properties
graph_attr = {
    "splines": "spline",
    "fontsize": "14",
    "bgcolor": "transparent",
    "fontcolor": "white"
}

with Diagram("Azure Dual-Region Hub & Spoke Lab", show=True, direction="RL", graph_attr=graph_attr):

    # --- WEST US REGION ---
    with Cluster("West US Region", graph_attr={"fontcolor": "black"}):
        
        with Cluster("OnPrem-LA (192.168.2.0/24)"):
            la_gw = VirtualNetworkGateways("GW-LA")
            la_wl = VM("LA Workload")
            la_gw << la_wl

        with Cluster("Hub-West VNet (10.2.0.0/16)"):
            hub_west_gw = VirtualNetworkGateways("GW-HubWest")
            nva_west = VM("NVA-West\n(10.2.1.4)")

        with Cluster("Spoke-West VNet (10.20.0.0/16)"):
            spoke_west_wl = VM("Workload Subnet")
            rt_west = RouteTables("RT-SpokeWest\n(Next-Hop: 10.2.1.4)")
            spoke_west_wl >> rt_west

    # --- EAST US REGION ---
    with Cluster("East US Region", graph_attr={"fontcolor": "black"}):
        
        with Cluster("OnPrem-Miami (192.168.1.0/24)"):
            miami_gw = VirtualNetworkGateways("GW-Miami")
            miami_wl = VM("Miami Workload")
            miami_wl >> miami_gw

        with Cluster("Hub-East VNet (10.1.0.0/16)"):
            hub_east_gw = VirtualNetworkGateways("GW-HubEast")
            nva_east = VM("NVA-East\n(10.1.1.4)")
            
        with Cluster("Spoke-East VNet (10.10.0.0/16)"):
            spoke_east_wl = VM("Workload Subnet")
            rt_east = RouteTables("RT-SpokeEast\n(Next-Hop: 10.1.1.4)")
            rt_east << spoke_east_wl
       

   # --- CONNECTIONS & ROUTING LOGIC ---
    
    # 1. Site-to-Site VPN Tunnels (Bidirectional)
    miami_gw - Edge(color="darkgreen", style="bold", label="S2S IPsec VPN", dir="both") - hub_east_gw
    hub_west_gw - Edge(color="darkgreen", style="bold", label="S2S IPsec VPN", dir="both") - la_gw

    # 2. Local VNet Peering with Gateway Transit (Bidirectional)
    hub_west_gw - Edge(color="blue", label="Local Peering\n(Transit)", dir="both") - spoke_west_wl
    spoke_east_wl - Edge(color="blue", label="Local Peering\n(Transit)", dir="both") - hub_east_gw


    # 3. Transitive Routing Path via NVAs over Global VNet Peering
    rt_east >> Edge(color="red", style="dashed", label="UDR Path") >> nva_east
    nva_east - Edge(color="purple", style="bold", label="Global Peering\n(Forwarded Traffic)", fontcolor="white", dir="both") - nva_west
    nva_west << Edge(color="red", style="dashed", label="UDR Path", constraint="false") << rt_west
