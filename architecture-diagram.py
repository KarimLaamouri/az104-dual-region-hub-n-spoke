from diagrams import Cluster, Diagram, Edge
from diagrams.azure.network import VirtualNetworks, VpnGateways, RouteTables
from diagrams.azure.compute import VM

# Adjust diagram properties
graph_attr = {
    "splines": "spline",
    "fontsize": "14",
    "bgcolor": "transparent"
}

with Diagram("Azure Dual-Region Hub & Spoke Lab", show=True, direction="LR", graph_attr=graph_attr):

    # --- EAST US REGION ---
    with Cluster("East US Region"):
        
        with Cluster("OnPrem-Miami (192.168.1.0/24)"):
            miami_gw = VpnGateways("GW-Miami")
            miami_wl = VM("Miami Workload")
            miami_wl >> miami_gw

        with Cluster("Hub-East VNet (10.1.0.0/16)"):
            hub_east_gw = VpnGateways("GW-HubEast")
            nva_east = VM("NVA-East\n(10.1.1.4)")
            
        with Cluster("Spoke-East VNet (10.10.0.0/16)"):
            spoke_east_wl = VM("Workload Subnet")
            rt_east = RouteTables("RT-SpokeEast\n(Next-Hop: 10.1.1.4)")
            spoke_east_wl >> rt_east

    # --- WEST US REGION ---
    with Cluster("West US Region"):
        
        with Cluster("Spoke-West VNet (10.20.0.0/16)"):
            spoke_west_wl = VM("Workload Subnet")
            rt_west = RouteTables("RT-SpokeWest\n(Next-Hop: 10.2.1.4)")
            spoke_west_wl >> rt_west

        with Cluster("Hub-West VNet (10.2.0.0/16)"):
            hub_west_gw = VpnGateways("GW-HubWest")
            nva_west = VM("NVA-West\n(10.2.1.4)")

        with Cluster("OnPrem-LA (192.168.2.0/24)"):
            la_gw = VpnGateways("GW-LA")
            la_wl = VM("LA Workload")
            la_gw << la_wl

    # --- CONNECTIONS & ROUTING LOGIC ---
    
    # 1. Site-to-Site VPN Tunnels
    miami_gw <>> Edge(color="darkgreen", style="bold", label="S2S IPsec VPN") << hub_east_gw
    hub_west_gw <>> Edge(color="darkgreen", style="bold", label="S2S IPsec VPN") << la_gw

    # 2. Local VNet Peering with Gateway Transit
    hub_east_gw <>> Edge(color="blue", label="Peering\n(Transit)") << spoke_east_wl
    hub_west_gw <>> Edge(color="blue", label="Peering\n(Transit)") << spoke_west_wl

    # 3. Transitive Routing Path via NVAs over Global VNet Peering
    rt_east >> Edge(color="red", style="dashed", label="UDR Path") >> nva_east
    nva_east <>> Edge(color="purple", style="bold", label="Global Peering\n(Forwarded Traffic)") << nva_west
    nva_west << Edge(color="red", style="dashed", label="UDR Path") << rt_west
