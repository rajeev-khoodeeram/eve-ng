import pynetbox

# 1. Initialize NetBox URL and Token String
NETBOX_URL = "http://localhost:8000"
# Strip out "Bearer " or "Token " from the raw token string
RAW_TOKEN = "nbt_ym4SNfFofImH.Hi5TWwGn1nHUYUsr252P63prZphMAgrhPuKEXL2A"

# 2. Instantiate Client
nb = pynetbox.api(NETBOX_URL, token=RAW_TOKEN)

# 3. Explicitly set Bearer Token header for NetBox v4 API
nb.http_session.headers.update({"Authorization": f"Bearer {RAW_TOKEN}"})

# 1. Define Interface Mappings per Device
device_interfaces = {
    # NYC Site
    "NYC-R1": ["GigabitEthernet0/0"],
    "NYC-R2": ["GigabitEthernet0/0"],
    "NYC-F5-01": ["1.1", "1.2"],
    "NYC-PA01": ["ethernet1/1", "ethernet1/2"],

    # LON Site
    "LON-PA01": ["ethernet1/1", "ethernet1/2"],
    "LON-F5-01": ["1.1", "1.2"],
    "LON-R1": ["GigabitEthernet0/0"],
    "LON-R2": ["GigabitEthernet0/0"],
}

# 2. Define IP Address Allocations
ip_allocations = [
    # NYC-DC1
    {"address": "10.10.0.1/24", "device": "NYC-R1", "interface": "GigabitEthernet0/0", "description": "NYC Core Router 1 LAN"},
    {"address": "10.10.0.2/24", "device": "NYC-R2", "interface": "GigabitEthernet0/0", "description": "NYC Core Router 2 LAN"},
    {"address": "10.10.0.100/24", "device": "NYC-F5-01", "interface": "1.1", "description": "NYC LTM Web VIP", "role": "vip"},
    {"address": "10.10.0.253/24", "device": "NYC-F5-01", "interface": "1.2", "description": "NYC LTM Self-IP"},
    {"address": "10.10.0.254/24", "device": "NYC-PA01", "interface": "ethernet1/2", "description": "NYC Palo Alto LAN Gateway"},

    # WAN Transit Link
    {"address": "172.16.1.1/30", "device": "NYC-PA01", "interface": "ethernet1/1", "description": "NYC WAN IPsec Gateway"},
    {"address": "172.16.1.2/30", "device": "LON-PA01", "interface": "ethernet1/1", "description": "LON WAN IPsec Gateway"},

    # LON-DC1
    {"address": "10.20.0.1/24", "device": "LON-R1", "interface": "GigabitEthernet0/0", "description": "LON Core Router 1 LAN"},
    {"address": "10.20.0.2/24", "device": "LON-R2", "interface": "GigabitEthernet0/0", "description": "LON Core Router 2 LAN"},
    {"address": "10.20.0.100/24", "device": "LON-F5-01", "interface": "1.1", "description": "LON LTM Web VIP", "role": "vip"},
    {"address": "10.20.0.253/24", "device": "LON-F5-01", "interface": "1.2", "description": "LON LTM Self-IP"},
    {"address": "10.20.0.254/24", "device": "LON-PA01", "interface": "ethernet1/2", "description": "LON Palo Alto LAN Gateway"},
]

print("--- Step 1: Creating Device Interfaces ---")
for device_name, interfaces in device_interfaces.items():
    device = nb.dcim.devices.get(name=device_name)
    if not device:
        print(f"[!] Device '{device_name}' not found. Ensure it was created in NetBox first.")
        continue

    for iface_name in interfaces:
        # Check if interface already exists
        existing_iface = nb.dcim.interfaces.get(device_id=device.id, name=iface_name)
        if not existing_iface:
            nb.dcim.interfaces.create({
                "device": device.id,
                "name": iface_name,
                "type": "virtual"
            })
            print(f"[+] Created interface '{iface_name}' on {device_name}")
        else:
            print(f"[*] Interface '{iface_name}' on {device_name} already exists.")

print("\n--- Step 2: Creating and Assigning IP Addresses ---")
for alloc in ip_allocations:
    device = nb.dcim.devices.get(name=alloc["device"])
    if not device:
        continue

    interface = nb.dcim.interfaces.get(device_id=device.id, name=alloc["interface"])
    if not interface:
        print(f"[!] Interface '{alloc['interface']}' on {alloc['device']} not found.")
        continue

    # Check if IP already exists
    existing_ip = nb.ipam.ip_addresses.get(address=alloc["address"])
    if not existing_ip:
        ip_payload = {
            "address": alloc["address"],
            "status": "active",
            "description": alloc["description"],
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": interface.id,
        }
        if "role" in alloc:
            ip_payload["role"] = alloc["role"]

        nb.ipam.ip_addresses.create(ip_payload)
        print(f"[+] Assigned {alloc['address']} to {alloc['device']} ({alloc['interface']})")
    else:
        print(f"[*] IP {alloc['address']} already exists.")

print("\n[✔] NetBox Interface and IP Address Automation Complete!")
