import sys
import os
import pathlib
import json
import urllib.request
import urllib.parse

_plugin_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_plugin_root / "scripts"))
from credentials import require_credentials

token, account_id = require_credentials()

url = f"https://graph.facebook.com/v19.0/me?fields=id,name&access_token={token}"
try:
    r = urllib.request.urlopen(url)
    d = json.loads(r.read())
    print(f"Token valido — usuario: {d.get('name')}")
except Exception as e:
    print(f"Token invalido: {e}")
    exit(1)

params = urllib.parse.urlencode({"fields": "id,name,status", "limit": 3, "access_token": token})
url2 = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"
try:
    r2 = urllib.request.urlopen(url2)
    d2 = json.loads(r2.read())
    campanhas = d2.get("data", [])
    print(f"Conta acessivel — {len(campanhas)} campanha(s) encontrada(s)")
except Exception as e:
    print(f"Sem acesso a conta: {e}")
    exit(1)
