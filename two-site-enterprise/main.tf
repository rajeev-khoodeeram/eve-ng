	
terraform {
  required_providers {
    eveng = {
      source  = "i-am-smolli/eveng"
      version = "~>0.1.10"
    }
  }
}

provider "eveng" {
  host     = "http://192.168.2.197"
  username = "admin"
  password = "eve"
}


# ============================================================
# LAB
# ============================================================

resource "eveng_lab" "two_site_enterprise" {
  name = "Two-Site-Enterprise"
}


# ============================================================
# SITE 1 - CISCO IOSv ROUTER
# ============================================================

resource "eveng_node" "site1_router" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE1-R1"
  template = "vios"
  type     = "qemu"

  top  = 300
  left = 450

  ethernet = 4
}


# ============================================================
# SITE 1 - IOL SWITCH 1
# ============================================================

resource "eveng_node" "site1_sw1" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE1-SW1"
  template = "iol"
  type     = "iol"

  top  = 150
  left = 150

  ethernet = 16
}


# ============================================================
# SITE 1 - IOL SWITCH 2
# ============================================================

resource "eveng_node" "site1_sw2" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE1-SW2"
  template = "iol"
  type     = "iol"

  top  = 350
  left = 50

  ethernet = 16
}


# ============================================================
# SITE 1 - IOL SWITCH 3
# ============================================================

resource "eveng_node" "site1_sw3" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE1-SW3"
  template = "iol"
  type     = "iol"

  top  = 550
  left = 150

  ethernet = 16
}


# ============================================================
# SITE 2 - CISCO IOSv ROUTER
# ============================================================

resource "eveng_node" "site2_router" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE2-R1"
  template = "vios"
  type     = "qemu"

  top  = 300
  left = 1050

  ethernet = 4
}


# ============================================================
# SITE 2 - IOL SWITCH 1
# ============================================================

resource "eveng_node" "site2_sw1" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE2-SW1"
  template = "iol"
  type     = "iol"

  top  = 150
  left = 1300

  ethernet = 16
}


# ============================================================
# SITE 2 - IOL SWITCH 2
# ============================================================

resource "eveng_node" "site2_sw2" {
  lab_path = eveng_lab.two_site_enterprise.path

  name     = "SITE2-SW2"
  template = "iol"
  type     = "iol"

  top  = 450
  left = 1300

  ethernet = 16
}


# ============================================================
# SITE-TO-SITE WAN NETWORK
# ============================================================

resource "eveng_network" "site_to_site_wan" {
  lab_path = eveng_lab.two_site_enterprise.path

  name = "SITE1-SITE2-WAN"
  type = "bridge"

  top  = 300
  left = 750

  icon = "01-Cloud-Default.svg"
}


# ============================================================
# SITE 1
# R1 -> SW1
# ============================================================

resource "eveng_node_link" "site1_r1_sw1" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site1_router.id
  source_port    = "Gi0/0"

  target_node_id = eveng_node.site1_sw1.id
  target_port    = "e0/0"
}


# ============================================================
# SITE 1
# SW1 -> SW2
# ============================================================

resource "eveng_node_link" "site1_sw1_sw2" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site1_sw1.id
  source_port    = "e0/1"

  target_node_id = eveng_node.site1_sw2.id
  target_port    = "e0/0"
}


# ============================================================
# SITE 1
# SW1 -> SW3
# ============================================================

resource "eveng_node_link" "site1_sw1_sw3" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site1_sw1.id
  source_port    = "e0/2"

  target_node_id = eveng_node.site1_sw3.id
  target_port    = "e0/0"
}


# ============================================================
# SITE 2
# R1 -> SW1
# ============================================================

resource "eveng_node_link" "site2_r1_sw1" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site2_router.id
  source_port    = "Gi0/0"

  target_node_id = eveng_node.site2_sw1.id
  target_port    = "e0/0"
}


# ============================================================
# SITE 2
# SW1 -> SW2
# ============================================================

resource "eveng_node_link" "site2_sw1_sw2" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site2_sw1.id
  source_port    = "e0/1"

  target_node_id = eveng_node.site2_sw2.id
  target_port    = "e0/0"
}


# ============================================================
# SITE 1 ROUTER -> WAN
# ============================================================

resource "eveng_node_link" "site1_router_wan" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site1_router.id
  source_port    = "Gi0/1"

  network_id = eveng_network.site_to_site_wan.id
}


# ============================================================
# SITE 2 ROUTER -> WAN
# ============================================================

resource "eveng_node_link" "site2_router_wan" {
  lab_path = eveng_lab.two_site_enterprise.path

  source_node_id = eveng_node.site2_router.id
  source_port    = "Gi0/1"

  network_id = eveng_network.site_to_site_wan.id
}

