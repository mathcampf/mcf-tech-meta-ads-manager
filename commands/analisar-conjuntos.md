---
description: Analisa os conjuntos de anúncios (ad sets) de uma campanha específica — ranking por spend, funil por conjunto, suporte a CBO, conjuntos para pausar ou escalar. Use quando o usuário quer otimizar ou entender a distribuição de budget entre conjuntos.
allowed-tools: Bash(python3:*), Bash(rm:*)
---
## Descrição
Analisa os conjuntos de anúncios (ad sets) de uma campanha específica. Identifica quais estão performando, quais estão drenando orçamento e onde focar a otimização.

---

## Instruções para o Claude

### Passo 1 — Selecionar a campanha

Se o usuário já mencionou a campanha, use o ID diretamente.
Caso contrário, escreva o script abaixo em `/tmp/mcf_lista_campanhas.py`, execute, mostre a lista e pergunte qual campanha analisar. Delete depois.

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")

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
    icon = "ATIVA  " if c["status"] == "ACTIVE" else "PAUSADA"
    print(f"[{icon}] {c['name']}")
    print(f"         ID: {c['id']} | Gasto 30d: R${spend:.2f}")
    print()
```

### Passo 2 — Analisar os conjuntos

Com o ID da campanha, escreva o script abaixo em `/tmp/mcf_conjuntos.py`, **substituindo `CAMPAIGN_ID_AQUI`** pelo ID correto, execute e delete.

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")
campaign_id = "CAMPAIGN_ID_AQUI"

params = urllib.parse.urlencode({
    "fields": "id,name,status,daily_budget,lifetime_budget,bid_strategy,optimization_goal,insights.date_preset(last_30d){spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,cost_per_action_type}",
    "limit": 50,
    "access_token": token
})

url = f"https://graph.facebook.com/v19.0/{campaign_id}/adsets?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

adsets = data.get("data", [])

def get_purchases(insights):
    actions = insights.get("actions", [])
    action_values = insights.get("action_values", [])
    purchases = next((int(a["value"]) for a in actions if a["action_type"] == "purchase"), 0)
    revenue = next((float(a["value"]) for a in action_values if a["action_type"] == "purchase"), 0.0)
    cart = next((int(a["value"]) for a in actions if a["action_type"] == "add_to_cart"), 0)
    checkout = next((int(a["value"]) for a in actions if a["action_type"] == "initiate_checkout"), 0)
    return purchases, revenue, cart, checkout

total_spend = sum(float(a.get("insights", {}).get("data", [{}])[0].get("spend", 0)) for a in adsets)

print("=" * 60)
print("ANÁLISE DE CONJUNTOS DE ANÚNCIOS")
print("=" * 60)
print(f"Total de conjuntos: {len(adsets)}")
print(f"Gasto total 30d:    R${total_spend:.2f}")
print()

adsets_sorted = sorted(
    adsets,
    key=lambda x: float(x.get("insights", {}).get("data", [{}])[0].get("spend", 0)),
    reverse=True
)

for adset in adsets_sorted:
    insights = adset.get("insights", {}).get("data", [{}])[0]
    spend = float(insights.get("spend", 0))
    if spend == 0 and adset["status"] == "PAUSED":
        continue

    freq = float(insights.get("frequency", 0))
    ctr = float(insights.get("ctr", 0))
    cpc = float(insights.get("cpc", 0))
    cpm = float(insights.get("cpm", 0))
    reach = int(insights.get("reach", 0))
    clicks = int(insights.get("clicks", 0))
    purchases, revenue, cart, checkout = get_purchases(insights)
    roas = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None
    budget = adset.get("daily_budget") or adset.get("lifetime_budget")
    budget_str = f"R${int(budget)/100:.2f}" if budget else "CBO (verba na campanha)"
    pct_total = (spend / total_spend * 100) if total_spend > 0 else 0
    opt_goal = adset.get("optimization_goal", "N/A")

    print(f"[{adset['status']}] {adset['name']}")
    print(f"  Orcamento:   {budget_str} | Gasto: R${spend:.2f} ({pct_total:.1f}% do total)")
    print(f"  Otimizacao:  {opt_goal}")
    print(f"  Alcance:     {reach:,} | Freq: {freq:.2f}x | CPM: R${cpm:.2f}")
    print(f"  CTR:         {ctr:.2f}% | CPC: R${cpc:.2f} | Cliques: {clicks:,}")
    if cart > 0 or purchases > 0:
        funil = []
        if cart > 0: funil.append(f"Carrinho: {cart:,}")
        if checkout > 0: funil.append(f"Checkout: {checkout:,}")
        if purchases > 0: funil.append(f"Compras: {purchases:,}")
        print(f"  Funil:       {' → '.join(funil)}")
    if purchases > 0:
        print(f"  Receita:     R${revenue:.2f} | ROAS: {roas}x | CPA: R${spend/purchases:.2f}")
    print()
```

### Passo 3 — Análise comparativa

Com os dados, apresente:

1. **Ranking de performance** — do melhor ao pior conjunto
2. **Distribuição de orçamento** — se está concentrado demais em um só conjunto
3. **Conjuntos para pausar** — alta frequência + baixo ROAS/CTR
4. **Conjuntos para escalar** — boa performance + frequência saudável
5. **Recomendação de próximos passos**

---

## Critérios de avaliação

**Conjunto saudável para escalar:**
- CTR > 2%
- Frequência dentro do benchmark para o tipo
- ROAS acima de 2x (para campanhas de vendas)

**Conjunto para revisar:**
- CTR < 1%
- Frequência acima do limite de atenção
- Gastando mais de 40% do total sem resultado proporcional

**Conjunto para pausar:**
- Frequência saturada
- ROAS abaixo de 1x
- Alcance estagnado com gasto crescente
