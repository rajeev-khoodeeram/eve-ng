# main.tf
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

resource "eveng_lab"  "Lab1" {
  name = "Lab1"
}

resource "eveng_node" "par_r1" {
  lab_path    = eveng_lab.Lab1.path
  name      = "PAR-R1"
  template  = "vios"
  type      = "qemu"
  left      = 200
  top       = 200
}

resource "eveng_node" "par_r2" {
  lab_path    = eveng_lab.Lab1.path
  name      = "PAR-R2"
  template  = "vios"
  type     = "qemu"
  left      = 500
  top       = 200
}






