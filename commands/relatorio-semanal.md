---
description: Gera o relatório semanal de Meta Ads com comparação semana a semana — gasto, ROAS, compras, alertas de frequência e destaques positivos. Ideal para usar toda segunda-feira ou quando o usuário quer saber como foi a semana.
allowed-tools: Bash(python3:*), Bash(rm:*)
---
## Descrição
Gera um relatório semanal completo com comparação semana a semana: o que melhorou, o que piorou, quanto foi gasto e quais campanhas precisam de atenção. Ideal para usar toda segunda-feira.

---

## Instruções para o Claude

1. Escreva o script abaixo em `/tmp/mcf_relatorio_semanal.py`
2. Execute com `python3 /tmp/mcf_relatorio_semanal.py`
3. Delete com `rm /tmp/mcf_relatorio_semanal.py`
4. Apresente o relatório de forma estruturada e em tom consultivo

---

## Script

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")

def fetch_campaigns(date_preset):
    params = urllib.parse.urlencode({
        "fields": f"id,name,status,objective,insights.date_preset({date_preset}){{spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,outbound_clicks,video_avg_time_watched_actions}}",
        "limit": 50,
        "access_token": token
    })
    url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read()).get("data", [])

def get_insights(campaign, date_preset):
    return campaign.get("insights", {}).get("data", [{}])[0]

def get_purchases(insights):
    actions = insights.get("actions", [])
    action_values = insights.get("action_values", [])
    purchases = next((int(a["value"]) for a in actions if a["action_type"] == "purchase"), 0)
    revenue = next((float(a["value"]) for a in action_values if a["action_type"] == "purchase"), 0.0)
    return purchases, revenue

def variation(current, previous):
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100

def fmt_var(pct, inverse=False):
    if pct is None:
        return "N/A"
    symbol = "+" if pct > 0 else ""
    arrow = ""
    if inverse:
        arrow = " (melhor)" if pct < 0 else " (pior)" if pct > 0 else ""
    else:
        arrow = " (melhor)" if pct > 0 else " (pior)" if pct < 0 else ""
    return f"{symbol}{pct:.1f}%{arrow}"

this_week = fetch_campaigns("last_7d")
last_week = fetch_campaigns("last_week_mon_sun")

last_week_map = {c["id"]: c for c in last_week}

total_this = {"spend": 0, "clicks": 0, "impressions": 0, "reach": 0, "purchases": 0, "revenue": 0}
total_last = {"spend": 0, "clicks": 0, "impressions": 0, "reach": 0, "purchases": 0, "revenue": 0}

print("=" * 60)
print("RELATÓRIO SEMANAL — META ADS")
print("=" * 60)
print()

alerts = []
highlights = []
campaign_rows = []

for c in this_week:
    if c["status"] not in ["ACTIVE", "PAUSED"]:
        continue

    this = get_insights(c, "last_7d")
    prev_campaign = last_week_map.get(c["id"], {})
    prev = get_insights(prev_campaign, "last_week_mon_sun") if prev_campaign else {}

    spend = float(this.get("spend", 0))
    clicks = int(this.get("clicks", 0))
    impressions = int(this.get("impressions", 0))
    ctr = float(this.get("ctr", 0))
    cpc = float(this.get("cpc", 0))
    reach = int(this.get("reach", 0))
    frequency = float(this.get("frequency", 0))
    purchases, revenue = get_purchases(this)

    p_spend = float(prev.get("spend", 0))
    p_clicks = int(prev.get("clicks", 0))
    p_ctr = float(prev.get("ctr", 0))
    p_cpc = float(prev.get("cpc", 0))
    p_purchases, p_revenue = get_purchases(prev)

    total_this["spend"] += spend
    total_this["clicks"] += clicks
    total_this["impressions"] += impressions
    total_this["reach"] += reach
    total_this["purchases"] += purchases
    total_this["revenue"] += revenue

    total_last["spend"] += p_spend
    total_last["clicks"] += p_clicks
    total_last["purchases"] += p_purchases
    total_last["revenue"] += p_revenue

    if spend == 0:
        continue

    this_actions = this.get("actions", [])
    this_av = this.get("action_values", [])
    prev_actions = prev.get("actions", []) if prev else []
    prev_av = prev.get("action_values", []) if prev else []
    outbound = this.get("outbound_clicks", [])
    vtime = this.get("video_avg_time_watched_actions", [])

    lpv          = next((int(a["value"]) for a in this_actions if a["action_type"] in ("landing_page_view","omni_landing_page_view")), 0)
    video_views  = next((int(a["value"]) for a in this_actions if a["action_type"] == "video_view"), 0)
    add_to_cart  = next((int(a["value"]) for a in this_actions if a["action_type"] == "add_to_cart"), 0)
    outb_clicks  = int(outbound[0]["value"]) if outbound else 0
    avg_vid_sec  = int(vtime[0]["value"]) if vtime else 0

    p_revenue = next((float(a["value"]) for a in prev_av if a["action_type"] == "purchase"), 0.0)
    roas = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None
    p_roas = round(p_revenue / p_spend, 2) if p_spend > 0 and p_revenue > 0 else None

    var_spend = variation(spend, p_spend)
    var_ctr = variation(ctr, p_ctr)
    var_cpc = variation(cpc, p_cpc)
    var_roas = variation(roas, p_roas) if roas and p_roas else None

    if frequency > 7 and c["status"] == "ACTIVE":
        alerts.append(f"FREQUENCIA ALTA: {c['name']} ({frequency:.1f}x)")
    if purchases > 0 and p_purchases > 0 and purchases > p_purchases * 1.2:
        highlights.append(f"COMPRAS +{((purchases/p_purchases)-1)*100:.0f}%: {c['name']}")
    if roas and p_roas and roas > p_roas * 1.15:
        highlights.append(f"ROAS melhorou {fmt_var(var_roas)}: {c['name']} ({p_roas}x -> {roas}x)")

    campaign_rows.append({
        "name": c["name"],
        "status": c["status"],
        "objective": c.get("objective",""),
        "spend": spend, "p_spend": p_spend,
        "ctr": ctr, "p_ctr": p_ctr,
        "cpc": cpc, "p_cpc": p_cpc,
        "frequency": frequency,
        "purchases": purchases, "revenue": revenue,
        "roas": roas, "p_roas": p_roas,
        "lpv": lpv, "video_views": video_views,
        "add_to_cart": add_to_cart, "outb_clicks": outb_clicks,
        "avg_vid_sec": avg_vid_sec,
        "var_spend": var_spend, "var_ctr": var_ctr,
        "var_cpc": var_cpc, "var_roas": var_roas,
    })

print("RESUMO GERAL")
print("-" * 40)
print(f"Gasto esta semana:   R${total_this['spend']:.2f}  (semana passada: R${total_last['spend']:.2f})  [{fmt_var(variation(total_this['spend'], total_last['spend']), inverse=True)}]")
print(f"Cliques:             {total_this['clicks']:,}  (semana passada: {total_last['clicks']:,})")
print(f"Alcance total:       {total_this['reach']:,}")
if total_this["purchases"] > 0:
    roas = total_this["revenue"] / total_this["spend"] if total_this["spend"] > 0 else 0
    print(f"Compras:             {total_this['purchases']} | Receita: R${total_this['revenue']:.2f} | ROAS: {roas:.2f}x")
print()

if alerts:
    print("ALERTAS")
    print("-" * 40)
    for a in alerts:
        print(f"  {a}")
    print()

if highlights:
    print("DESTAQUES POSITIVOS")
    print("-" * 40)
    for h in highlights:
        print(f"  {h}")
    print()

print("PERFORMANCE POR CAMPANHA")
print("-" * 40)
for row in sorted(campaign_rows, key=lambda x: x["spend"], reverse=True):
    obj = row["objective"].upper()
    is_sales = "SALES" in obj or "CATALOG" in obj
    is_engagement = "ENGAGEMENT" in obj or "TRAFFIC" in obj

    print(f"\n[{row['status']}] {row['name']}")
    print(f"  Gasto:      R${row['spend']:.2f} vs R${row['p_spend']:.2f} [{fmt_var(row['var_spend'], inverse=True)}]")
    print(f"  CTR:        {row['ctr']:.2f}% vs {row['p_ctr']:.2f}% [{fmt_var(row['var_ctr'])}]")
    print(f"  CPC:        R${row['cpc']:.2f} vs R${row['p_cpc']:.2f} [{fmt_var(row['var_cpc'], inverse=True)}]")
    print(f"  Frequencia: {row['frequency']:.2f}x")
    if is_sales and row["purchases"] > 0:
        roas_prev = f"{row['p_roas']}x" if row['p_roas'] else "N/A"
        roas_curr = f"{row['roas']}x" if row['roas'] else "N/A"
        print(f"  Funil:      Carrinho: {row['add_to_cart']:,} | Compras: {row['purchases']:,} | Receita: R${row['revenue']:.2f}")
        print(f"  ROAS:       {roas_curr} vs {roas_prev} [{fmt_var(row['var_roas'])}]")
        print(f"  LPV:        {row['lpv']:,} | Externos: {row['outb_clicks']:,}")
    if is_engagement and row["video_views"] > 0:
        print(f"  Video:      {row['video_views']:,} views | Tempo medio: {row['avg_vid_sec']}s")
```

---

## Como apresentar o relatório

### Estrutura da resposta ao usuário

1. **Abertura** — breve contexto da semana (bom, regular, preocupante?)
2. **Números principais** — gasto, compras, ROAS comparados com semana anterior
3. **Alertas** — frequência alta, queda de performance, gasto acima do esperado
4. **Destaques** — o que melhorou, o que está funcionando bem
5. **Campanhas em detalhe** — resumo por campanha com variações
6. **Ação recomendada para a semana** — 2-3 ações práticas e priorizadas

### Tom
- Consultivo e direto
- Destaque o que é urgente vs o que pode esperar
- Termine sempre com ações claras
