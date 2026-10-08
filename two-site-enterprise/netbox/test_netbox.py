import os
import pynetbox

NETBOX_URL = os.getenv("NETBOX_URL", "http://localhost:8000")
NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]

nb = pynetbox.api(NETBOX_URL)

nb.http_session.headers.update({
    "Authorization": f"Bearer {NETBOX_TOKEN}",
    "Accept": "application/json",
})

print("\nDEVICE TYPES")
print("=" * 60)

for x in nb.dcim.device_types.all():
    print(
        f"id={x.id:<4} "
        f"model={getattr(x, 'model', ''):<30} "
        f"slug={getattr(x, 'slug', '')}"
    )

print("\nDEVICE ROLES")
print("=" * 60)

for x in nb.dcim.device_roles.all():
    print(
        f"id={x.id:<4} "
        f"name={getattr(x, 'name', ''):<30} "
        f"slug={getattr(x, 'slug', '')}"
    )
