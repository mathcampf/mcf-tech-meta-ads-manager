import sys
import os
import pathlib
import urllib.request
import urllib.parse
import json

_plugin_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_plugin_root / "scripts"))
from credentials import require_credentials

token, account_id = require_credentials()

params = urllib.parse.urlencode({
    "fields": "id,name,status,objective,insights.date_preset(last_30d){spend}",
    "limit": 50,
    "access_token": token
})

url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

print("CAMPANHAS DISPONÍVEIS")
print("-" * 50)
for c in data.get("data", []):
    insights = c.get("insights", {}).get("data", [{}])[0]
    spend = float(insights.get("spend", 0))
    status_icon = "ATIVA  " if c["status"] == "ACTIVE" else "PAUSADA"
    print(f"[{status_icon}] {c['name']}")
    print(f"         ID: {c['id']} | Gasto 30d: R${spend:.2f}")
    print()
