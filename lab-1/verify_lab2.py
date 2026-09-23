# verify_lab.py
from netmiko import ConnectHandler

devices = [
    {
        'device_type': 'cisco_ios',
        'host': '10.10.0.1',
        'username': 'cisco',
        'password': 'cisco',
	'disabled_algorithms': {
        'kex': [],        # Do not disable any key exchange algorithms
        'ciphers': [],    # Do not disable legacy ciphers
        'keys': [],       # Do not disable legacy host key types (ssh-rsa/dss)
    },
    'fast_cli': False,
},	
    {
        'device_type': 'cisco_ios',
        'host': '10.10.0.2',
        'username': 'cisco',
        'password': 'cisco',
	'disabled_algorithms': {
        'kex': [],        # Do not disable any key exchange algorithms
        'ciphers': [],    # Do not disable legacy ciphers
        'keys': [],       # Do not disable legacy host key types (ssh-rsa/dss)
    },
    'fast_cli': False,

    }
]

for dev in devices:
    print(f"--- Connecting to {dev['host']} ---")
    connection = ConnectHandler(**dev)
    output = connection.send_command("show ip interface brief | exclude unassigned")
    print(output)
    connection.disconnect()
