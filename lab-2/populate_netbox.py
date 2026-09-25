import pynetbox

NETBOX_URL = "http://192.168.2.198:8000"  # Adjust port if needed
TOKEN = "nbt_ym4SNfFofImH.Hi5TWwGn1nHUYUsr252P63prZphMAgrhPuKEXL2A"

nb = pynetbox.api(NETBOX_URL, token=TOKEN)


def setup_sites_with_switches():
  print("Initializing Site 2 and Site 3 Infrastructure in NetBox...")

  # 1. Create Independent Sites
  site2 = nb.dcim.sites.get(slug="site-2")
  if not site2:
    site2 = nb.dcim.sites.create(
        name="Site 2", slug="site-2", status="active"
    )

  site3 = nb.dcim.sites.get(slug="site-3")
  if not site3:
    site3 = nb.dcim.sites.create(
        name="Site 3", slug="site-3", status="active"
    )

  # 2. Ensure Manufacturer Exists
  mfg = nb.dcim.manufacturers.get(slug="cisco")
  if not mfg:
    mfg = nb.dcim.manufacturers.create(name="Cisco", slug="cisco")

  # 3. Ensure a Generic Device Type Exists
  dev_type = nb.dcim.device_types.get(slug="generic-router-switch")
  if not dev_type:
    dev_type = nb.dcim.device_types.create(
        model="Generic Virtual Node",
        slug="generic-router-switch",
        manufacturer=mfg.id,
    )

  # 4. Ensure Device Roles Exist
  edge_role = nb.dcim.device_roles.get(slug="edge-router")
  if not edge_role:
    edge_role = nb.dcim.device_roles.create(
        name="Edge Router", slug="edge-router", color="ff0000"
    )

  core_role = nb.dcim.device_roles.get(slug="core-router")
  if not core_role:
    core_role = nb.dcim.device_roles.create(
        name="Core Router", slug="core-router", color="00ff00"
    )

  switch_role = nb.dcim.device_roles.get(slug="access-switch")
  if not switch_role:
    switch_role = nb.dcim.device_roles.create(
        name="Access Switch", slug="access-switch", color="0000ff"
    )

  # 5. Create Devices (Including the required device_type ID)
  devices = [
      # Site 2
      {
          "name": "SITE2-EDGE1",
          "role": edge_role.id,
          "site": site2.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE2-CORE1",
          "role": core_role.id,
          "site": site2.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE2-SW1",
          "role": switch_role.id,
          "site": site2.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE2-SW2",
          "role": switch_role.id,
          "site": site2.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE2-SW3",
          "role": switch_role.id,
          "site": site2.id,
          "device_type": dev_type.id,
      },
      # Site 3
      {
          "name": "SITE3-EDGE1",
          "role": edge_role.id,
          "site": site3.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE3-CORE1",
          "role": core_role.id,
          "site": site3.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE3-SW1",
          "role": switch_role.id,
          "site": site3.id,
          "device_type": dev_type.id,
      },
      {
          "name": "SITE3-SW2",
          "role": switch_role.id,
          "site": site3.id,
          "device_type": dev_type.id,
      },
  ]

  for dev in devices:
    if not nb.dcim.devices.get(name=dev["name"]):
      nb.dcim.devices.create(dev)
      print(f"Created device: {dev['name']}")
    else:
      print(f"Device {dev['name']} already exists.")


# 6. Allocate IPAM Prefixes for the Sites
  prefixes = [
      {
          "prefix": "10.20.0.0/22",
          "site": site2.id,
          "description": "Site 2 Supernet (Departments)",
      },
      {
          "prefix": "10.30.0.0/22",
          "site": site3.id,
          "description": "Site 3 Supernet (Departments)",
      },
      {
          "prefix": "10.100.0.0/30",
          "description": "Inter-Site WAN Link (Site 2 to Site 3)",
      },
  ]

  for pref in prefixes:
    if not nb.ipam.prefixes.get(prefix=pref["prefix"]):
      nb.ipam.prefixes.create(pref)
      print(f"Created IP prefix: {pref['prefix']}")
    else:
      print(f"IP prefix {pref['prefix']} already exists.")


if __name__ == "__main__":
  setup_sites_with_switches()
