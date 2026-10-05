from pathlib import Path

# Base Ansible directory
#BASE = Path.home() / "eve-terraform" / "two-site-enterprise" / "ansible"

BASE = Path.cwd()

# Directories to create
directories = [
    "inventory",
    "group_vars",
    "host_vars",
    "playbooks",

    "roles/router_baseline/tasks",
    "roles/router_baseline/handlers",
    "roles/router_baseline/templates",
    "roles/router_baseline/files",
    "roles/router_baseline/vars",
    "roles/router_baseline/defaults",

    "roles/switch_baseline/tasks",
    "roles/switch_baseline/handlers",
    "roles/switch_baseline/templates",
    "roles/switch_baseline/files",
    "roles/switch_baseline/vars",
    "roles/switch_baseline/defaults",

    "vault",
    "backups",
]

# Empty files to create
files = [
    "ansible.cfg",
    "requirements.yml",
    "README.md",

    "inventory/hosts.yml",

    "group_vars/all.yml",
    "group_vars/routers.yml",
    "group_vars/switches.yml",

    "playbooks/baseline.yml",
    "playbooks/interfaces.yml",
    "playbooks/wan.yml",
    "playbooks/ospf.yml",
    "playbooks/vlans.yml",
    "playbooks/validation.yml",
    "playbooks/backup.yml",

    "roles/router_baseline/tasks/main.yml",
    "roles/router_baseline/handlers/main.yml",
    "roles/router_baseline/vars/main.yml",
    "roles/router_baseline/defaults/main.yml",

    "roles/switch_baseline/tasks/main.yml",
    "roles/switch_baseline/handlers/main.yml",
    "roles/switch_baseline/vars/main.yml",
    "roles/switch_baseline/defaults/main.yml",
]


def create_structure():
    # Create directories
    for directory in directories:
        path = BASE / directory
        path.mkdir(parents=True, exist_ok=True)

    # Create empty files
    for file in files:
        path = BASE / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)

    print(f"\nAnsible structure created at:")
    print(BASE)
    print("\nDirectories and empty files created successfully.")


if __name__ == "__main__":
    create_structure()
