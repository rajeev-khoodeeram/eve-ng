terraform {
  required_providers {
    eveng = {
      source  = "qmuntal/eveng"
      version = "0.1.0"
    }
  }
}

provider "eveng" {
  host     = "http://192.168.2.197"
  username = "admin"
  password = "eve"
}

resource "eveng_lab" "enterprise_lab" {
  name = "enterprise_lab"
}

# ------------------------------------------------------------------------------
# SHARED NETWORKS (BRIDGES)
# ------------------------------------------------------------------------------
resource "eveng_network" "wan_transit" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "WAN_Transit"
  type     = "bridge"
}

resource "eveng_network" "nyc_lan" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "NYC_LAN"
  type     = "bridge"
}

resource "eveng_network" "lon_lan" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "LON_LAN"
  type     = "bridge"
}

# ------------------------------------------------------------------------------
# NYC-DC1 SITE NODES
# ------------------------------------------------------------------------------
resource "eveng_node" "nyc_r1" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "nyc_r1"
  type     = "qemu"
  template = "vios"
}

resource "eveng_node" "nyc_r2" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "nyc_r2"
  type     = "qemu"
  template = "vios"
}

resource "eveng_node" "nyc_pa01" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "nyc_pa01"
  type     = "qemu"
  template = "paloalto"
  config   = "0"
  lifecycle {
    ignore_changes = [config]
  }
}

 resource "eveng_node" "nyc_f5_01" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "nyc_f5_01"
  type     = "qemu"
  template = "bigip"
    lifecycle {
    ignore_changes = [config]
  }
}

# ------------------------------------------------------------------------------
# LON-DC1 SITE NODES
# ------------------------------------------------------------------------------
resource "eveng_node" "lon_pa01" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "lon_pa01"
  type     = "qemu"
  template = "paloalto"
  config   = "0"
  lifecycle {
    ignore_changes = [config]
  }
}

resource "eveng_node" "lon_f5_01" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "lon_f5_01"
  type     = "qemu"
  template = "bigip"
  lifecycle {
    ignore_changes = [config]
  }
}

resource "eveng_node" "lon_r1" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "lon_r1"
  type     = "qemu"
  template = "vios"
}

resource "eveng_node" "lon_r2" {
  lab_path = eveng_lab.enterprise_lab.path
  name     = "lon_r2"
  type     = "qemu"
  template = "vios"
}
