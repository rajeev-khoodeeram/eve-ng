
terraform {
  required_providers {
    eveng = {
      source  = "i-am-smolli/eveng"
      version = "~> 0.1.10"
    }
  }
}

provider "eveng" {
  host      = "http://192.168.2.197" # Note: uses 'url' instead of 'host' for this provider registry version
  username = "admin"
  password = "eve"
}


# 1. Create the Isolated Lab Workspace
resource "eveng_lab" "lab2_wan" {
  name        = "LAB2-WAN"
  description = "Independent multi-site enterprise lab with dual internet breakouts and inter-site WAN"
}

# ----------------------------------------------------
# 2. Define Networks & Cloud Bridges
# ----------------------------------------------------

# Internet Breakout Clouds
resource "eveng_network" "internet_site2" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "INTERNET-SITE2"
  type     = "bridge"
  left     = 100
  top      = 50
}

resource "eveng_network" "internet_site3" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "INTERNET-SITE3"
  type     = "bridge"
  left     = 700
  top      = 50
}

# Inter-Site WAN Link (Direct P2P between Site 2 Edge and Site 3 Edge)
resource "eveng_network" "inter_site_wan" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "WAN-SITE2-SITE3"
  type     = "bridge"
  left     = 400
  top      = 200
}

# Internal Transit (Edge <-> Core) per Site
resource "eveng_network" "site2_internal" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE2-INTERNAL-TRANSIT"
  type     = "bridge"
  left     = 100
  top      = 250
}

resource "eveng_network" "site3_internal" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE3-INTERNAL-TRANSIT"
  type     = "bridge"
  left     = 700
  top      = 250
}

# Department Access Switch Trunks per Site
resource "eveng_network" "site2_sw_trunk" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE2-SWITCH-TRUNKS"
  type     = "bridge"
  left     = 100
  top      = 400
}

resource "eveng_network" "site3_sw_trunk" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE3-SWITCH-TRUNKS"
  type     = "bridge"
  left     = 700
  top      = 400
}


# ----------------------------------------------------
# 3. Provision Site 2 Nodes (Edge, Core, 3 Switches)
# ----------------------------------------------------

resource "eveng_node" "site2_edge" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE2-EDGE1"
  template = "vios"
  type     = "qemu"
  left     = 100
  top      = 150
}

resource "eveng_node" "site2_core" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE2-CORE1"
  template = "vios"
  type     = "qemu"
  left     = 100
  top      = 300
}

resource "eveng_node" "site2_sw1" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE2-SW1"
  template = "iol"
  type     = "iol"
  left     = 25
  top      = 500
}

#resource "eveng_node" "site2_sw2" {
#  lab_path = eveng_lab.lab2_wan.path
#  name     = "SITE2-SW2"
#  template = "iol"
#  type     = "iol"
#  left     = 100
#  top      = 500
#}

#resource "eveng_node" "site2_sw3" {
#  lab_path = eveng_lab.lab2_wan.path
#  name     = "SITE2-SW3"
#  template = "iol"
#  type     = "iol"
#  left     = 175
#  top      = 500
#}


# ----------------------------------------------------
# 4. Provision Site 3 Nodes (Edge, Core, 2 Switches)
# ----------------------------------------------------

resource "eveng_node" "site3_edge" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE3-EDGE1"
  template = "vios"
  type     = "qemu"
  left     = 700
  top      = 150
}

resource "eveng_node" "site3_core" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE3-CORE1"
  template = "vios"
  type     = "qemu"
  left     = 700
  top      = 300
}

resource "eveng_node" "site3_sw1" {
  lab_path = eveng_lab.lab2_wan.path
  name     = "SITE3-SW1"
  template = "iol"
  type     = "iol"
  left     = 625
  top      = 500
}

#resource "eveng_node" "site3_sw2" {
#  lab_path = eveng_lab.lab2_wan.path
#  name     = "SITE3-SW2"
#  template = "iol"
#  type     = "iol"
#  left     = 775
#  top      = 500
#}


# --- Pacing Timer for EVE-NG Node Initialization ---
resource "time_sleep" "wait_for_nodes" {
  create_duration = "10s"

  depends_on = [
    eveng_node.site2_edge,
    eveng_node.site2_core,
    eveng_node.site2_sw1,
 #   eveng_node.site2_sw2,
 #   eveng_node.site2_sw3,
    eveng_node.site3_edge,
    eveng_node.site3_core,
    eveng_node.site3_sw1,
  #  eveng_node.site3_sw2,
  ]
}


# ----------------------------------------------------
# 5. Cable Topology (Interfaces & Links)
# ----------------------------------------------------

# --- Site 2 Links ---
resource "eveng_node_link" "s2_internet" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.internet_site2.id
  source_node_id = eveng_node.site2_edge.id
  source_port    = "GigabitEthernet0/0"
  depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s2_wan" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.inter_site_wan.id
  source_node_id = eveng_node.site2_edge.id
  source_port    = "GigabitEthernet0/1"
 depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s2_edge_internal" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site2_internal.id
  source_node_id = eveng_node.site2_edge.id
  source_port    = "GigabitEthernet0/2"
  depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s2_core_internal" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site2_internal.id
  source_node_id = eveng_node.site2_core.id
  source_port    = "GigabitEthernet0/0"
  depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s2_core_sw_trunk" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site2_sw_trunk.id
  source_node_id = eveng_node.site2_core.id
  source_port    = "GigabitEthernet0/1"
depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s2_sw1_trunk" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site2_sw_trunk.id
  source_node_id = eveng_node.site2_sw1.id
  source_port    = "Ethernet0/0"

depends_on     = [time_sleep.wait_for_nodes]
}

#resource "eveng_node_link" "s2_sw2_trunk" {
#  lab_path       = eveng_lab.lab2_wan.path
#  network_id     = eveng_network.site2_sw_trunk.id
#  source_node_id = eveng_node.site2_sw2.id
#  source_port    = "Ethernet0/0"
#depends_on     = [time_sleep.wait_for_nodes]
#}

#resource "eveng_node_link" "s2_sw3_trunk" {
#  lab_path       = eveng_lab.lab2_wan.path
#  network_id     = eveng_network.site2_sw_trunk.id
#  source_node_id = eveng_node.site2_sw3.id
#  source_port    = "Ethernet0/0"
#depends_on     = [time_sleep.wait_for_nodes]
#}


# --- Site 3 Links ---
resource "eveng_node_link" "s3_internet" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.internet_site3.id
  source_node_id = eveng_node.site3_edge.id
  source_port    = "GigabitEthernet0/0"
depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s3_wan" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.inter_site_wan.id
  source_node_id = eveng_node.site3_edge.id
  source_port    = "GigabitEthernet0/1"
depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s3_edge_internal" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site3_internal.id
  source_node_id = eveng_node.site3_edge.id
  source_port    = "GigabitEthernet0/2"
depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s3_core_internal" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site3_internal.id
  source_node_id = eveng_node.site3_core.id
  source_port    = "GigabitEthernet0/0"
depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s3_core_sw_trunk" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site3_sw_trunk.id
  source_node_id = eveng_node.site3_core.id
  source_port    = "GigabitEthernet0/1"
depends_on     = [time_sleep.wait_for_nodes]
}

resource "eveng_node_link" "s3_sw1_trunk" {
  lab_path       = eveng_lab.lab2_wan.path
  network_id     = eveng_network.site3_sw_trunk.id
  source_node_id = eveng_node.site3_sw1.id
  source_port    = "Ethernet0/0"
depends_on     = [time_sleep.wait_for_nodes]
}

#resource "eveng_node_link" "s3_sw2_trunk" {
#  lab_path       = eveng_lab.lab2_wan.path
#  network_id     = eveng_network.site3_sw_trunk.id
#  source_node_id = eveng_node.site3_sw2.id
#  source_port    = "Ethernet0/0"
#depends_on     = [time_sleep.wait_for_nodes]
#}
