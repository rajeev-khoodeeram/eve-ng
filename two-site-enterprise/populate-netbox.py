import pynetbox

NETBOX_URL = "http://192.168.2.198:8000"

# IMPORTANT:
# Replace this with your NEW NetBox API token.
TOKEN = "nbt_ym4SNfFofImH.Hi5TWwGn1nHUYUsr252P63prZphMAgrhPuKEXL2A"

nb = pynetbox.api(NETBOX_URL, token=TOKEN)


def setup_lab3():
    print("==============================================")
    print(" Initializing LAB-3 in NetBox")
    print(" Two-Site Enterprise Network")
    print("==============================================")

    # ============================================================
    # 1. CREATE SITES
    # ============================================================

    site1 = nb.dcim.sites.get(slug="site-1")

    if not site1:
        site1 = nb.dcim.sites.create(
            name="Site 1",
            slug="site-1",
            status="active"
        )
        print("Created Site 1")
    else:
        print("Site 1 already exists.")

    site2 = nb.dcim.sites.get(slug="site-2")

    if not site2:
        site2 = nb.dcim.sites.create(
            name="Site 2",
            slug="site-2",
            status="active"
        )
        print("Created Site 2")
    else:
        print("Site 2 already exists.")


    # ============================================================
    # 2. MANUFACTURER
    # ============================================================

    cisco = nb.dcim.manufacturers.get(slug="cisco")

    if not cisco:
        cisco = nb.dcim.manufacturers.create(
            name="Cisco",
            slug="cisco"
        )
        print("Created Cisco manufacturer.")
    else:
        print("Cisco manufacturer already exists.")


    # ============================================================
    # 3. DEVICE TYPES
    # ============================================================

    iosv_type = nb.dcim.device_types.get(slug="cisco-iosv")

    if not iosv_type:
        iosv_type = nb.dcim.device_types.create(
            model="Cisco IOSv",
            slug="cisco-iosv",
            manufacturer=cisco.id
        )
        print("Created Cisco IOSv device type.")
    else:
        print("Cisco IOSv device type already exists.")


    iol_type = nb.dcim.device_types.get(slug="cisco-iol-l2")

    if not iol_type:
        iol_type = nb.dcim.device_types.create(
            model="Cisco IOL-L2",
            slug="cisco-iol-l2",
            manufacturer=cisco.id
        )
        print("Created Cisco IOL-L2 device type.")
    else:
        print("Cisco IOL-L2 device type already exists.")


    # ============================================================
    # 4. DEVICE ROLES
    # ============================================================

    router_role = nb.dcim.device_roles.get(slug="edge-router")

    if not router_role:
        router_role = nb.dcim.device_roles.create(
            name="Edge Router",
            slug="edge-router",
            color="ff0000"
        )
        print("Created Edge Router role.")
    else:
        print("Edge Router role already exists.")


    switch_role = nb.dcim.device_roles.get(slug="access-switch")

    if not switch_role:
        switch_role = nb.dcim.device_roles.create(
            name="Access Switch",
            slug="access-switch",
            color="0000ff"
        )
        print("Created Access Switch role.")
    else:
        print("Access Switch role already exists.")


    # ============================================================
    # 5. CREATE DEVICES
    # ============================================================

    devices = [

        # --------------------------------------------------------
        # SITE 1
        # --------------------------------------------------------

        {
            "name": "SITE1-R1",
            "role": router_role.id,
            "site": site1.id,
            "device_type": iosv_type.id,
            "status": "active",
        },

        {
            "name": "SITE1-SW1",
            "role": switch_role.id,
            "site": site1.id,
            "device_type": iol_type.id,
            "status": "active",
        },

        {
            "name": "SITE1-SW2",
            "role": switch_role.id,
            "site": site1.id,
            "device_type": iol_type.id,
            "status": "active",
        },

        {
            "name": "SITE1-SW3",
            "role": switch_role.id,
            "site": site1.id,
            "device_type": iol_type.id,
            "status": "active",
        },


        # --------------------------------------------------------
        # SITE 2
        # --------------------------------------------------------

        {
            "name": "SITE2-R1",
            "role": router_role.id,
            "site": site2.id,
            "device_type": iosv_type.id,
            "status": "active",
        },

        {
            "name": "SITE2-SW1",
            "role": switch_role.id,
            "site": site2.id,
            "device_type": iol_type.id,
            "status": "active",
        },

        {
            "name": "SITE2-SW2",
            "role": switch_role.id,
            "site": site2.id,
            "device_type": iol_type.id,
            "status": "active",
        },
    ]


    for dev in devices:

        existing = nb.dcim.devices.get(name=dev["name"])

        if not existing:
            nb.dcim.devices.create(dev)
            print(f"Created device: {dev['name']}")
        else:
            print(f"Device {dev['name']} already exists.")


    # ============================================================
    # 6. CREATE SITE PREFIXES
    # ============================================================

    prefixes = [

        {
            "prefix": "10.10.0.0/16",
            "site": site1.id,
            "description": "LAB-3 Site 1 Supernet",
        },

        {
            "prefix": "10.20.0.0/16",
            "site": site2.id,
            "description": "LAB-3 Site 2 Supernet",
        },

        {
            "prefix": "10.255.0.0/30",
            "description": "LAB-3 Site 1 to Site 2 WAN",
        },
    ]


    for pref in prefixes:

        existing = nb.ipam.prefixes.get(
            prefix=pref["prefix"]
        )

        if not existing:
            nb.ipam.prefixes.create(pref)
            print(f"Created IP prefix: {pref['prefix']}")
        else:
            print(f"IP prefix {pref['prefix']} already exists.")


    # ============================================================
    # 7. CREATE VLANs
    # ============================================================

    vlans = [

        # Site 1
        {
            "vid": 10,
            "name": "SITE1-USERS",
            "site": site1.id,
            "status": "active",
        },

        {
            "vid": 20,
            "name": "SITE1-SERVERS",
            "site": site1.id,
            "status": "active",
        },

        {
            "vid": 30,
            "name": "SITE1-MANAGEMENT",
            "site": site1.id,
            "status": "active",
        },


        # Site 2
        {
            "vid": 10,
            "name": "SITE2-USERS",
            "site": site2.id,
            "status": "active",
        },

        {
            "vid": 20,
            "name": "SITE2-SERVERS",
            "site": site2.id,
            "status": "active",
        },

        {
            "vid": 30,
            "name": "SITE2-MANAGEMENT",
            "site": site2.id,
            "status": "active",
        },
    ]


    for vlan in vlans:

        existing = nb.ipam.vlans.get(
            vid=vlan["vid"],
            site_id=vlan["site"]
        )

        if not existing:
            nb.ipam.vlans.create(vlan)

            print(
                f"Created VLAN {vlan['vid']} - "
                f"{vlan['name']}"
            )

        else:
            print(
                f"VLAN {vlan['vid']} "
                f"already exists at site."
            )


    # ============================================================
    # COMPLETE
    # ============================================================

    print()
    print("==============================================")
    print(" LAB-3 NetBox population complete")
    print("==============================================")
    print()
    print("Site 1:")
    print("  SITE1-R1")
    print("  SITE1-SW1")
    print("  SITE1-SW2")
    print("  SITE1-SW3")
    print()
    print("Site 2:")
    print("  SITE2-R1")
    print("  SITE2-SW1")
    print("  SITE2-SW2")
    print()
    print("WAN:")
    print("  10.255.0.0/30")
    print()
    print("VLANs:")
    print("  VLAN 10 - Users")
    print("  VLAN 20 - Servers")
    print("  VLAN 30 - Management")
    print()


if __name__ == "__main__":
    setup_lab3()
