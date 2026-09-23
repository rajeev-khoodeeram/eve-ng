# verify_lab.py
import paramiko

# 1. Force Paramiko to enable legacy Key Exchange (KEX) algorithms
preferred_kex = list(paramiko.Transport._preferred_kex)
legacy_kex = [
    'diffie-hellman-group1-sha1',
    'diffie-hellman-group14-sha1',
    'diffie-hellman-group-exchange-sha1',
    'diffie-hellman-group-exchange-sha256',
]
for kex in legacy_kex:
    if kex not in preferred_kex:
        preferred_kex.append(kex)
paramiko.Transport._preferred_kex = tuple(preferred_kex)

# 2. Force Paramiko to enable legacy Ciphers and Keys
preferred_ciphers = list(paramiko.Transport._preferred_ciphers)
legacy_ciphers = ['aes128-cbc', 'aes192-cbc', 'aes256-cbc', '3des-cbc']
for cipher in legacy_ciphers:
    if cipher not in preferred_ciphers:
        preferred_ciphers.append(cipher)
paramiko.Transport._preferred_ciphers = tuple(preferred_ciphers)

preferred_keys = list(paramiko.Transport._preferred_keys)
legacy_keys = ['ssh-rsa', 'ssh-dss']
for key in legacy_keys:
    if key not in preferred_keys:
        preferred_keys.append(key)
paramiko.Transport._preferred_keys = tuple(preferred_keys)

# 3. Import Netmiko after patching Paramiko
from netmiko import ConnectHandler

devices = [
    {
        'device_type': 'cisco_ios',
        'host': '10.10.0.1',
        'username': 'cisco',
        'password': 'cisco',
        'fast_cli': False,
    },
    {
        'device_type': 'cisco_ios',
        'host': '10.10.0.2',
        'username': 'cisco',
        'password': 'cisco',
        'fast_cli': False,
    }
]

for dev in devices:
    print(f"--- Connecting to {dev['host']} ---")
    connection = ConnectHandler(**dev)
    output = connection.send_command("show ip interface brief | exclude unassigned")
    print(output)
    connection.disconnect()
