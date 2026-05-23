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
    "fields": "id,name,status,objective,daily_budget,lifetime_budget,insights.date_preset(last_30d){spend,impressions,reach,frequency,clicks,ctr,cpc,actions,action_values,outbound_clicks}",
    "limit": 50,
    "access_token": token
})

url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

def get_action(actions, *types):
    for t in types:
        val = next((a["value"] for a in actions if a["action_type"] == t), None)
        if val is not None:
            return int(val)
    return 0

def get_value(action_values, *types):
    for t in types:
        val = next((a["value"] for a in action_values if a["action_type"] == t), None)
        if val is not None:
            return float(val)
    return 0.0

def pct(num, den):
    return f"{(num/den*100):.1f}%" if den > 0 else "N/A"

def cpa_str(spend, qty):
    return f"R${spend/qty:.2f}" if qty > 0 else "N/A"

print("=" * 60)
print("FUNIL DE CONVERSAO — ULTIMOS 30 DIAS")
print("=" * 60)

totals = {"spend":0,"impressions":0,"reach":0,"clicks":0,"lpv":0,"vc":0,"cart":0,"chk":0,"buy":0,"revenue":0.0}

sales_campaigns = []
for c in data.get("data", []):
    obj = c.get("objective", "")
    if "SALES" not in obj and "CATALOG" not in obj:
        continue
    insights = c.get("insights", {}).get("data", [{}])[0]
    if not insights:
        continue

    actions = insights.get("actions", [])
    action_values = insights.get("action_values", [])
    outbound = insights.get("outbound_clicks", [])

    spend       = float(insights.get("spend", 0))
    impressions = int(insights.get("impressions", 0))
    reach       = int(insights.get("reach", 0))
    frequency   = float(insights.get("frequency", 0))
    clicks      = int(insights.get("clicks", 0))
    outb        = int(outbound[0]["value"]) if outbound else 0

    lpv     = get_action(actions, "landing_page_view", "omni_landing_page_view")
    vc      = get_action(actions, "view_content")
    cart    = get_action(actions, "add_to_cart")
    chk     = get_action(actions, "initiate_checkout")
    payment = get_action(actions, "add_payment_info")
    buy     = get_action(actions, "purchase")
    revenue = get_value(action_values, "purchase")
    roas    = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None

    totals["spend"]       += spend
    totals["impressions"] += impressions
    totals["reach"]       += reach
    totals["clicks"]      += clicks
    totals["lpv"]         += lpv
    totals["vc"]          += vc
    totals["cart"]        += cart
    totals["chk"]         += chk
    totals["buy"]         += buy
    totals["revenue"]     += revenue

    budget = c.get("daily_budget") or c.get("lifetime_budget")
    budget_str = f"R${int(budget)/100:.2f}" if budget else "N/A"

    print(f"\nCampanha: {c['name']}  [{c['status']}]")
    print(f"Orcamento: {budget_str} | Gasto: R${spend:.2f} | Freq: {frequency:.2f}x")
    print()
    print(f"  Impressoes       {impressions:>10,}")
    print(f"  Alcance          {reach:>10,}  ({pct(reach,impressions)} das impressoes)")
    ctr = float(insights.get("ctr", 0))
    cpc = float(insights.get("cpc", 0))
    print(f"  Cliques          {clicks:>10,}  CTR: {ctr:.2f}% | CPC: R${cpc:.2f}")
    print(f"  Externos         {outb:>10,}  ({pct(outb,clicks)} dos cliques)")
    print(f"  Landing Page     {lpv:>10,}  ({pct(lpv,outb if outb else clicks)} chegaram)")
    print(f"  Ver produto      {vc:>10,}  (atrib. multi-toque — pode passar 100%)")
    print(f"  Add carrinho     {cart:>10,}  ({pct(cart,vc if vc else lpv)} de quem viu)")
    print(f"  Checkout         {chk:>10,}  ({pct(chk,cart)} do carrinho)")
    print(f"  Pagamento        {payment:>10,}  ({pct(payment,chk)} do checkout)")
    print(f"  COMPRA           {buy:>10,}  ({pct(buy,chk)} do checkout)")
    if revenue > 0:
        print()
        print(f"  Receita:  R${revenue:.2f}")
        print(f"  ROAS:     {roas}x")
        print(f"  CPA:      {cpa_str(spend,buy)}")
        print(f"  CPL:      {cpa_str(spend,lpv)} por visita qualificada")

if not sales_campaigns and totals["spend"] == 0:
    print("Nenhuma campanha de vendas ativa com dados nos ultimos 30 dias.")
    exit(0)

if len([c for c in data.get("data",[]) if "SALES" in c.get("objective","") or "CATALOG" in c.get("objective","")]) > 1:
    print()
    print("=" * 60)
    print("CONSOLIDADO — TODAS AS CAMPANHAS DE VENDAS")
    print("=" * 60)
    t = totals
    print(f"Gasto total:   R${t['spend']:.2f}")
    print(f"Alcance:       {t['reach']:,}")
    print(f"Cliques:       {t['clicks']:,}")
    print(f"Landing Pages: {t['lpv']:,}  ({pct(t['lpv'],t['clicks'])} qualificado)")
    print(f"Ver produto:   {t['vc']:,}")
    print(f"Carrinho:      {t['cart']:,}  ({pct(t['cart'],t['vc'])} de quem viu)")
    print(f"Checkout:      {t['chk']:,}  ({pct(t['chk'],t['cart'])} do carrinho)")
    print(f"COMPRAS:       {t['buy']:,}  ({pct(t['buy'],t['chk'])} do checkout)")
    if t['revenue'] > 0:
        roas_total = round(t['revenue'] / t['spend'], 2) if t['spend'] > 0 else 0
        print(f"Receita:       R${t['revenue']:.2f}")
        print(f"ROAS total:    {roas_total}x")
        print(f"CPA medio:     {cpa_str(t['spend'], t['buy'])}")
