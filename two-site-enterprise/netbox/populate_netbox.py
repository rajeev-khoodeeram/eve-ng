#!/usr/bin/env python3

"""
Populate NetBox for the Two-Site Enterprise Lab.

SAFE DESIGN
-----------
- Does NOT delete anything.
- Does NOT modify devices in other tenants.
- Existing Lab-1 SITE1-R1 remains untouched.
- Device lookup is scoped by:
      Device Name + Site + Tenant
- Missing devices are created only in the target tenant.
- Missing interfaces are created.
- Missing IPs are created.
- Existing IPs are verified before assignment.
- An IP already assigned to another device causes a safety stop.
- Primary IPv4 is configured where required.
- Running the script repeatedly is intended to be idempotent.

Usage:

    export NETBOX_URL="http://localhost:8000"
    export NETBOX_TOKEN="YOUR_NEW_NETBOX_TOKEN"

    python3 populate_netbox.py

    python3 populate_netbox.py --apply
"""

import argparse
import os
import sys
from typing import Any, Dict, Optional

import pynetbox


# ============================================================
# NETBOX CONNECTION
# ============================================================

NETBOX_URL = os.getenv(
    "NETBOX_URL",
    "http://localhost:8000"
)

NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")


# ============================================================
# TARGET TENANT
# ============================================================

TARGET_TENANT_NAME = "Two-Site-Enterprise-Lab"
TARGET_TENANT_SLUG = "two-site-enterprise-lab"


# ============================================================
# SITES
# ============================================================

SITES = {
    "site1": {
        "name": "Site 1",
        "slug": "site-1",
    },
    "site2": {
        "name": "Site 2",
        "slug": "site-2",
    },
}


# ============================================================
# NETBOX DEVICE TYPES
# These match your NetBox installation.
# ============================================================

DEVICE_TYPES = {
    "router": {
        "slug": "cisco-iosv",
    },
    "switch": {
        "slug": "cisco-iol-l2",
    },
}


# ============================================================
# NETBOX DEVICE ROLES
# These match your NetBox installation.
# ============================================================

DEVICE_ROLES = {
    "router": {
        "slug": "edge-router",
    },
    "switch": {
        "slug": "access-switch",
    },
}


# ============================================================
# TWO-SITE LAB DEFINITIONS
# ============================================================

LAB_DEVICES: Dict[str, Dict[str, Any]] = {

    # --------------------------------------------------------
    # SITE 1 ROUTER
    # --------------------------------------------------------

    "SITE1-R1": {
        "site": "site1",
        "device_type": "router",
        "device_role": "router",
        "status": "active",

        "interfaces": [
            {
                "name": "GigabitEthernet0/0",
                "type": "1000base-t",
                "ip": "10.10.10.1/24",
                "primary": False,
            },

            {
                "name": "GigabitEthernet0/1",
                "type": "1000base-t",
                "ip": "10.255.0.1/30",
                "primary": False,
            },

            {
                "name": "GigabitEthernet0/2",
                "type": "1000base-t",
                "ip": "192.168.2.200/24",
                "primary": True,
            },
        ],
    },


    # --------------------------------------------------------
    # SITE 1 SWITCH 1
    # --------------------------------------------------------

    "SITE1-SW1": {
        "site": "site1",
        "device_type": "switch",
        "device_role": "switch",
        "status": "active",

        "interfaces": [
            {
                "name": "Vlan99",
                "type": "virtual",
                "ip": "10.10.10.11/24",
                "primary": True,
            },
        ],
    },


    # --------------------------------------------------------
    # SITE 1 SWITCH 2
    # --------------------------------------------------------

    "SITE1-SW2": {
        "site": "site1",
        "device_type": "switch",
        "device_role": "switch",
        "status": "active",

        "interfaces": [
            {
                "name": "Vlan99",
                "type": "virtual",
                "ip": "10.10.10.12/24",
                "primary": True,
            },
        ],
    },


    # --------------------------------------------------------
    # SITE 1 SWITCH 3
    # --------------------------------------------------------

    "SITE1-SW3": {
        "site": "site1",
        "device_type": "switch",
        "device_role": "switch",
        "status": "active",

        "interfaces": [
            {
                "name": "Vlan99",
                "type": "virtual",
                "ip": "10.10.10.13/24",
                "primary": True,
            },
        ],
    },


    # --------------------------------------------------------
    # SITE 2 ROUTER
    # --------------------------------------------------------

    "SITE2-R1": {
        "site": "site2",
        "device_type": "router",
        "device_role": "router",
        "status": "active",

        "interfaces": [
            {
                "name": "GigabitEthernet0/0",
                "type": "1000base-t",
                "ip": "10.20.10.1/24",
                "primary": True,
            },

            {
                "name": "GigabitEthernet0/1",
                "type": "1000base-t",
                "ip": "10.255.0.2/30",
                "primary": False,
            },
        ],
    },


    # --------------------------------------------------------
    # SITE 2 SWITCH 1
    # --------------------------------------------------------

    "SITE2-SW1": {
        "site": "site2",
        "device_type": "switch",
        "device_role": "switch",
        "status": "active",

        "interfaces": [
            {
                "name": "Vlan99",
                "type": "virtual",
                "ip": "10.20.10.11/24",
                "primary": True,
            },
        ],
    },


    # --------------------------------------------------------
    # SITE 2 SWITCH 2
    # --------------------------------------------------------

    "SITE2-SW2": {
        "site": "site2",
        "device_type": "switch",
        "device_role": "switch",
        "status": "active",

        "interfaces": [
            {
                "name": "Vlan99",
                "type": "virtual",
                "ip": "10.20.10.12/24",
                "primary": True,
            },
        ],
    },
}


# ============================================================
# HELPERS
# ============================================================

def log(message: str) -> None:
    print(message)


def get_single(recordset, description: str):
    records = list(recordset)

    if len(records) == 0:
        return None

    if len(records) > 1:
        raise RuntimeError(
            f"Expected exactly one {description}, "
            f"but found {len(records)}."
        )

    return records[0]


# ============================================================
# CONNECT TO NETBOX
# ============================================================

def connect_netbox():

    if not NETBOX_TOKEN:

        print(
            "\nERROR: NETBOX_TOKEN is not set.\n\n"
            "Set it with:\n"
            "  export NETBOX_TOKEN='YOUR_NEW_TOKEN'\n"
        )

        sys.exit(1)

    nb = pynetbox.api(NETBOX_URL)

    nb.http_session.headers.update(
        {
            "Authorization": f"Bearer {NETBOX_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )

    return nb


# ============================================================
# TENANT
# ============================================================

def get_or_create_tenant(nb, apply: bool):

    log("")
    log("=" * 72)
    log("TENANT")
    log("=" * 72)

    tenant = get_single(
        nb.tenancy.tenants.filter(
            slug=TARGET_TENANT_SLUG
        ),
        f"tenant '{TARGET_TENANT_NAME}'"
    )

    if tenant:

        log(
            f"Found tenant: {tenant.name} "
            f"(id={tenant.id})"
        )

        return tenant

    log(
        f"Tenant does not exist: "
        f"{TARGET_TENANT_NAME}"
    )

    if not apply:

        log(
            f"DRY RUN: would create tenant "
            f"'{TARGET_TENANT_NAME}'"
        )

        return None

    tenant = nb.tenancy.tenants.create(
        {
            "name": TARGET_TENANT_NAME,
            "slug": TARGET_TENANT_SLUG,
        }
    )

    log(
        f"CREATED tenant: {tenant.name} "
        f"(id={tenant.id})"
    )

    return tenant


# ============================================================
# SITES
# ============================================================

def get_sites(nb):

    sites = {}

    log("")
    log("=" * 72)
    log("SITES")
    log("=" * 72)

    for key, config in SITES.items():

        site = get_single(
            nb.dcim.sites.filter(
                slug=config["slug"]
            ),
            f"site '{config['name']}'"
        )

        if not site:

            raise RuntimeError(
                f"Site '{config['name']}' "
                f"(slug={config['slug']}) "
                f"does not exist in NetBox."
            )

        sites[key] = site

        log(
            f"{site.name} "
            f"(id={site.id}, slug={site.slug})"
        )

    return sites


# ============================================================
# DEVICE TYPE
# ============================================================

def get_device_type(nb, device_type_key: str):

    slug = DEVICE_TYPES[
        device_type_key
    ]["slug"]

    device_type = get_single(
        nb.dcim.device_types.filter(
            slug=slug
        ),
        f"device type '{slug}'"
    )

    if not device_type:

        raise RuntimeError(
            f"Device type '{slug}' "
            f"does not exist."
        )

    return device_type


# ============================================================
# DEVICE ROLE
# ============================================================

def get_device_role(nb, role_key: str):

    slug = DEVICE_ROLES[
        role_key
    ]["slug"]

    role = get_single(
        nb.dcim.device_roles.filter(
            slug=slug
        ),
        f"device role '{slug}'"
    )

    if not role:

        raise RuntimeError(
            f"Device role '{slug}' "
            f"does not exist."
        )

    return role


# ============================================================
# FIND TARGET DEVICE
#
# CRITICAL:
# Name + Site + Tenant
#
# This is what protects your Lab-1 SITE1-R1.
# ============================================================

def find_target_device(
    nb,
    device_name: str,
    site,
    tenant,
):

    devices = nb.dcim.devices.filter(
        name=device_name,
        site_id=site.id,
        tenant_id=tenant.id,
    )

    return get_single(
        devices,
        (
            f"device '{device_name}' "
            f"in site '{site.name}' "
            f"and tenant '{tenant.name}'"
        )
    )


# ============================================================
# CREATE OR GET DEVICE
# ============================================================

def get_or_create_device(
    nb,
    device_name: str,
    config: Dict[str, Any],
    site,
    tenant,
    apply: bool,
):

    device = find_target_device(
        nb=nb,
        device_name=device_name,
        site=site,
        tenant=tenant,
    )

    if device:

        log(
            f"  FOUND target device: "
            f"{device.name} "
            f"(id={device.id})"
        )

        log(
            f"  Site:   {site.name}"
        )

        log(
            f"  Tenant: {tenant.name}"
        )

        return device


    log(
        f"  Target device does not exist: "
        f"{device_name}"
    )


    if not apply:

        log(
            f"  DRY RUN: would create "
            f"{device_name}"
        )

        return None


    device_type = get_device_type(
        nb,
        config["device_type"]
    )

    device_role = get_device_role(
        nb,
        config["device_role"]
    )


    device = nb.dcim.devices.create(
        {
            "name": device_name,
            "device_type": device_type.id,
            "role": device_role.id,
            "site": site.id,
            "tenant": tenant.id,
            "status": config.get(
                "status",
                "active"
            ),
        }
    )


    log(
        f"  CREATED device: "
        f"{device.name} "
        f"(id={device.id})"
    )

    return device


# ============================================================
# INTERFACE
# ============================================================

def find_interface(
    nb,
    device,
    interface_name: str,
):

    return get_single(
        nb.dcim.interfaces.filter(
            device_id=device.id,
            name=interface_name,
        ),
        (
            f"interface '{interface_name}' "
            f"on '{device.name}'"
        )
    )


# ============================================================
# CREATE OR GET INTERFACE
# ============================================================

def get_or_create_interface(
    nb,
    device,
    interface_config: Dict[str, Any],
    apply: bool,
):

    interface_name = interface_config["name"]

    interface = find_interface(
        nb,
        device,
        interface_name,
    )


    if interface:

        log(
            f"    Interface exists: "
            f"{interface_name}"
        )

        return interface


    log(
        f"    Interface missing: "
        f"{interface_name}"
    )


    if not apply:

        log(
            f"    DRY RUN: would create "
            f"{interface_name}"
        )

        return None


    interface = nb.dcim.interfaces.create(
        {
            "device": device.id,
            "name": interface_name,
            "type": interface_config["type"],
        }
    )


    log(
        f"    CREATED interface: "
        f"{interface_name}"
    )

    return interface


# ============================================================
# FIND IP ADDRESS
# ============================================================

def find_ip(nb, address: str):

    return get_single(
        nb.ipam.ip_addresses.filter(
            address=address
        ),
        f"IP address '{address}'"
    )


# ============================================================
# GET DEVICE/INTERFACE FROM ASSIGNED IP
# ============================================================

def describe_ip_assignment(ip) -> str:

    assigned_object = getattr(
        ip,
        "assigned_object",
        None
    )

    if not assigned_object:

        return "UNASSIGNED"


    interface_name = getattr(
        assigned_object,
        "name",
        "UNKNOWN"
    )

    assigned_device = getattr(
        assigned_object,
        "device",
        None
    )

    if assigned_device:

        device_name = getattr(
            assigned_device,
            "name",
            "UNKNOWN"
        )

        return (
            f"{device_name}/"
            f"{interface_name}"
        )


    return interface_name


# ============================================================
# CREATE OR GET IP
# ============================================================

def get_or_create_ip(
    nb,
    device,
    interface,
    interface_config: Dict[str, Any],
    tenant,
    apply: bool,
):

    address = interface_config["ip"]

    ip = find_ip(
        nb,
        address
    )


    # --------------------------------------------------------
    # IP ALREADY EXISTS
    # --------------------------------------------------------

    if ip:

        assignment = describe_ip_assignment(ip)


        # Correct assignment
        if assignment == (
            f"{device.name}/{interface.name}"
        ):

            log(
                f"      IP exists and is correctly "
                f"assigned: {address}"
            )

            return ip


        # Unassigned IP
        if assignment == "UNASSIGNED":

            log(
                f"      IP exists but is unassigned: "
                f"{address}"
            )


            if not apply:

                log(
                    f"      DRY RUN: would assign "
                    f"{address} to "
                    f"{device.name}/{interface.name}"
                )

                return ip


            ip.update(
                {
                    "tenant": tenant.id,
                    "assigned_object_type":
                        "dcim.interface",
                    "assigned_object_id":
                        interface.id,
                }
            )


            log(
                f"      ASSIGNED existing IP: "
                f"{address}"
            )

            return ip


        # ----------------------------------------------------
        # CRITICAL SAFETY STOP
        # ----------------------------------------------------

        raise RuntimeError(
            "\n"
            "SAFETY STOP\n"
            "--------------------------------------------------\n"
            f"IP address {address} already belongs to:\n"
            f"    {assignment}\n\n"
            f"Requested assignment:\n"
            f"    {device.name}/{interface.name}\n\n"
            "The script will NOT steal or move the IP.\n"
            "--------------------------------------------------"
        )


    # --------------------------------------------------------
    # IP DOES NOT EXIST
    # --------------------------------------------------------

    log(
        f"      IP missing: {address}"
    )


    if not apply:

        log(
            f"      DRY RUN: would create "
            f"{address}"
        )

        return None


    ip = nb.ipam.ip_addresses.create(
        {
            "address": address,
            "status": "active",
            "tenant": tenant.id,
            "assigned_object_type":
                "dcim.interface",
            "assigned_object_id":
                interface.id,
        }
    )


    log(
        f"      CREATED IP: "
        f"{address}"
    )

    return ip


# ============================================================
# PRIMARY IP
# ============================================================

def configure_primary_ip(
    device,
    ip,
    apply: bool,
):

    if not ip:
        return


    address = str(ip.address)


    current_primary = getattr(
        device,
        "primary_ip4",
        None
    )


    current_primary_id = (
        getattr(
            current_primary,
            "id",
            None
        )
        if current_primary
        else None
    )


    if current_primary_id == ip.id:

        log(
            f"      Primary IPv4 already correct: "
            f"{address}"
        )

        return


    log(
        f"      Primary IPv4 should be: "
        f"{address}"
    )


    if not apply:

        log(
            f"      DRY RUN: would set primary "
            f"IPv4 to {address}"
        )

        return


    device.update(
        {
            "primary_ip4": ip.id
        }
    )


    log(
        f"      SET primary IPv4: "
        f"{address}"
    )


# ============================================================
# PROCESS ONE DEVICE
# ============================================================

def process_device(
    nb,
    device_name: str,
    config: Dict[str, Any],
    sites,
    tenant,
    apply: bool,
):

    site = sites[
        config["site"]
    ]


    print("")
    print("=" * 72)
    print(
        f"DEVICE: {device_name}"
    )
    print(
        f"SITE:   {site.name}"
    )
    print(
        f"TENANT: {tenant.name}"
    )
    print("=" * 72)


    device = get_or_create_device(
        nb=nb,
        device_name=device_name,
        config=config,
        site=site,
        tenant=tenant,
        apply=apply,
    )


    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if device is None:

        for interface_config in config[
            "interfaces"
        ]:

            log(
                f"    DRY RUN: "
                f"{interface_config['name']}"
                f" -> "
                f"{interface_config['ip']}"
            )

            if interface_config.get(
                "primary",
                False
            ):

                log(
                    f"    DRY RUN: "
                    f"{interface_config['ip']} "
                    f"would become primary IPv4"
                )

        return


    # --------------------------------------------------------
    # PROCESS INTERFACES
    # --------------------------------------------------------

    primary_ip = None


    for interface_config in config[
        "interfaces"
    ]:

        interface = get_or_create_interface(
            nb=nb,
            device=device,
            interface_config=interface_config,
            apply=apply,
        )


        if interface is None:
            continue


        ip = get_or_create_ip(
            nb=nb,
            device=device,
            interface=interface,
            interface_config=interface_config,
            tenant=tenant,
            apply=apply,
        )


        if interface_config.get(
            "primary",
            False
        ):

            primary_ip = ip


    # --------------------------------------------------------
    # PRIMARY IP
    # --------------------------------------------------------

    if primary_ip:

        configure_primary_ip(
            device=device,
            ip=primary_ip,
            apply=apply,
        )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Populate NetBox for the "
            "Two-Site Enterprise Lab."
        )
    )


    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually modify NetBox. "
            "Without this flag the script "
            "runs in dry-run mode."
        ),
    )


    args = parser.parse_args()


    apply = args.apply


    print("")
    print("=" * 72)
    print(
        "TWO-SITE ENTERPRISE LAB -> NETBOX"
    )
    print("=" * 72)


    if apply:

        print(
            "MODE: APPLY"
        )

        print(
            "NetBox WILL be modified."
        )

    else:

        print(
            "MODE: DRY RUN"
        )

        print(
            "No NetBox changes will be made."
        )

        print(
            "Use --apply to make changes."
        )


    print("")
    print(
        f"NetBox URL: {NETBOX_URL}"
    )

    print(
        f"Target tenant: "
        f"{TARGET_TENANT_NAME}"
    )


    # ========================================================
    # CONNECT
    # ========================================================

    nb = connect_netbox()


    try:

        status = nb.status()

        version = status.get(
            "netbox-version",
            "unknown"
        )

        print(
            f"NetBox API: OK "
            f"(version={version})"
        )

    except Exception as exc:

        print(
            "\nERROR: Could not connect to NetBox:"
        )

        print(exc)

        sys.exit(1)


    # ========================================================
    # TENANT
    # ========================================================

    tenant = get_or_create_tenant(
        nb=nb,
        apply=apply,
    )


    # In dry run mode, if tenant doesn't exist,
    # there is nothing more to query.
    if tenant is None:

        print("")
        print(
            "DRY RUN COMPLETE."
        )

        print(
            "The tenant would be created first, "
            "followed by the seven devices."
        )

        return


    # ========================================================
    # SITES
    # ========================================================

    sites = get_sites(nb)


    # ========================================================
    # PROCESS ALL DEVICES
    # ========================================================

    for device_name, config in LAB_DEVICES.items():

        process_device(
            nb=nb,
            device_name=device_name,
            config=config,
            sites=sites,
            tenant=tenant,
            apply=apply,
        )


    # ========================================================
    # COMPLETE
    # ========================================================

    print("")
    print("=" * 72)


    if apply:

        print(
            "COMPLETED: "
            "Two-Site NetBox population finished."
        )

    else:

        print(
            "DRY RUN COMPLETE: "
            "No changes were made."
        )

        print(
            "Run with --apply to execute the changes."
        )


    print("=" * 72)
    print("")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
