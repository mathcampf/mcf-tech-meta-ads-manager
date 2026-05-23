---
description: Compara a performance de todas as campanhas entre dois períodos — esta semana vs semana passada, este mês vs mês passado, ou datas personalizadas. Identifica tendências de melhora ou queda. Use quando o usuário quer comparar períodos, ver se o mês foi melhor ou pior, ou avaliar o impacto de uma mudança.
allowed-tools: Bash(python3:*), Bash(rm:*)
---
## Descrição
Compara a performance de todas as campanhas entre dois períodos: este mês vs mês passado, esta semana vs semana passada, ou qualquer período personalizado. Identifica tendências de melhora ou queda antes que virem problemas.

---

## Instruções para o Claude

### Passo 1 — Definir os períodos

Se o usuário não especificou, pergunte:
> "Qual comparação você quer fazer?"
> - Esta semana vs semana passada
> - Este mês vs mês passado
> - Últimos 30 dias vs 30 dias anteriores
> - Período personalizado (informe as datas)

Mapeie a resposta para os `date_preset` da API ou datas customizadas:
- "Esta semana vs semana passada" → `this_week_mon_today` vs `last_week_mon_sun`
- "Este mês vs mês passado" → `this_month` vs `last_month`
- "Últimos 30 dias vs 30 anteriores" → use datas calculadas

### Passo 2 — Executar a comparação

Escreva o script abaixo em `/tmp/mcf_comparar.py`, **ajustando `PRESET_A` e `PRESET_B`** conforme o período escolhido, execute e delete.

Para períodos pré-definidos use os presets. Para datas customizadas, substitua `date_preset(PRESET)` por `time_range` na URL (exemplo ao final do script).

```python
import urllib.request
import urllib.parse
import json
import os
from datetime import datetime, timedelta

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")

PRESET_A = "last_7d"
PRESET_B = "last_week_mon_sun"
LABEL_A  = "Esta semana"
LABEL_B  = "Semana passada"

def fetch(date_preset):
    params = urllib.parse.urlencode({
        "fields": f"id,name,status,objective,insights.date_preset({date_preset}){{spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,outbound_clicks}}",
        "limit": 50,
        "access_token": token
    })
    url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"
    with urllib.request.urlopen(url) as r:
        return {c["id"]: c for c in json.loads(r.read()).get("data", [])}

def get_action(actions, *types):
    for t in types:
        val = next((a["value"] for a in actions if a["action_type"] == t), None)
        if val is not None: return int(val)
    return 0

def get_value(avs, *types):
    for t in types:
        val = next((a["value"] for a in avs if a["action_type"] == t), None)
        if val is not None: return float(val)
    return 0.0

def pct_change(new, old):
    if old == 0: return None
    return ((new - old) / old) * 100

def fmt(val, old, unit="", inverse=False, decimals=2):
    change = pct_change(val, old)
    if change is None:
        return f"{val:.{decimals}f}{unit} (novo)"
    arrow = "+" if change > 0 else ""
    sentiment = ""
    if inverse:
        sentiment = " (melhor)" if change < 0 else " (pior)" if change > 2 else ""
    else:
        sentiment = " (melhor)" if change > 2 else " (pior)" if change < 0 else ""
    return f"{val:.{decimals}f}{unit} vs {old:.{decimals}f}{unit} [{arrow}{change:.1f}%{sentiment}]"

data_a = fetch(PRESET_A)
data_b = fetch(PRESET_B)

all_ids = set(data_a.keys()) | set(data_b.keys())

totals = {"a": {"spend":0,"clicks":0,"buy":0,"revenue":0.0}, "b": {"spend":0,"clicks":0,"buy":0,"revenue":0.0}}

print("=" * 60)
print(f"COMPARACAO DE PERIODOS")
print(f"  Periodo A: {LABEL_A}")
print(f"  Periodo B: {LABEL_B}")
print("=" * 60)
print()

improvements, declines, stable = [], [], []

for cid in all_ids:
    ca = data_a.get(cid, {})
    cb = data_b.get(cid, {})

    name = ca.get("name") or cb.get("name", "?")
    status = ca.get("status") or cb.get("status", "?")
    objective = ca.get("objective") or cb.get("objective", "")
    is_sales = "SALES" in objective.upper() or "CATALOG" in objective.upper()

    ia = ca.get("insights", {}).get("data", [{}])[0]
    ib = cb.get("insights", {}).get("data", [{}])[0]

    aa, ava = ia.get("actions", []), ia.get("action_values", [])
    ab, avb = ib.get("actions", []), ib.get("action_values", [])
    oa, ob_ = ia.get("outbound_clicks", []), ib.get("outbound_clicks", [])

    spend_a = float(ia.get("spend", 0))
    spend_b = float(ib.get("spend", 0))
    ctr_a   = float(ia.get("ctr", 0))
    ctr_b   = float(ib.get("ctr", 0))
    cpc_a   = float(ia.get("cpc", 0))
    cpc_b   = float(ib.get("cpc", 0))
    freq_a  = float(ia.get("frequency", 0))
    freq_b  = float(ib.get("frequency", 0))
    lpv_a   = get_action(aa, "landing_page_view", "omni_landing_page_view")
    lpv_b   = get_action(ab, "landing_page_view", "omni_landing_page_view")
    buy_a   = get_action(aa, "purchase")
    buy_b   = get_action(ab, "purchase")
    rev_a   = get_value(ava, "purchase")
    rev_b   = get_value(avb, "purchase")
    roas_a  = round(rev_a / spend_a, 2) if spend_a > 0 and rev_a > 0 else 0
    roas_b  = round(rev_b / spend_b, 2) if spend_b > 0 and rev_b > 0 else 0

    if spend_a == 0 and spend_b == 0:
        continue

    totals["a"]["spend"]   += spend_a
    totals["a"]["buy"]     += buy_a
    totals["a"]["revenue"] += rev_a
    totals["b"]["spend"]   += spend_b
    totals["b"]["buy"]     += buy_b
    totals["b"]["revenue"] += rev_b

    roas_change = pct_change(roas_a, roas_b)
    spend_change = pct_change(spend_a, spend_b)
    ctr_change = pct_change(ctr_a, ctr_b)

    if is_sales and roas_change and roas_change > 10:
        improvements.append(name)
    elif is_sales and roas_change and roas_change < -10:
        declines.append(name)
    elif ctr_change and ctr_change > 10:
        improvements.append(name)
    elif ctr_change and ctr_change < -10:
        declines.append(name)
    else:
        stable.append(name)

    print(f"[{status}] {name}")
    print(f"  Gasto:      {fmt(spend_a, spend_b, 'R$', inverse=True, decimals=2)}")
    print(f"  CTR:        {fmt(ctr_a, ctr_b, '%', decimals=2)}")
    print(f"  CPC:        {fmt(cpc_a, cpc_b, 'R$', inverse=True, decimals=2)}")
    print(f"  Frequencia: {freq_a:.2f}x vs {freq_b:.2f}x")
    if lpv_a > 0 or lpv_b > 0:
        print(f"  LPV:        {lpv_a:,} vs {lpv_b:,}")
    if is_sales and (buy_a > 0 or buy_b > 0):
        print(f"  Compras:    {buy_a:,} vs {buy_b:,}")
        print(f"  Receita:    R${rev_a:.2f} vs R${rev_b:.2f}")
        print(f"  ROAS:       {fmt(roas_a, roas_b, 'x', decimals=2)}")
    print()

t = totals
print("=" * 60)
print("CONSOLIDADO GERAL")
print("=" * 60)
print(f"Gasto:   {fmt(t['a']['spend'], t['b']['spend'], 'R$', inverse=True, decimals=2)}")
if t['a']['buy'] > 0 or t['b']['buy'] > 0:
    roas_total_a = round(t['a']['revenue'] / t['a']['spend'], 2) if t['a']['spend'] > 0 else 0
    roas_total_b = round(t['b']['revenue'] / t['b']['spend'], 2) if t['b']['spend'] > 0 else 0
    print(f"Compras: {t['a']['buy']:,} vs {t['b']['buy']:,}")
    print(f"Receita: R${t['a']['revenue']:.2f} vs R${t['b']['revenue']:.2f}")
    print(f"ROAS:    {fmt(roas_total_a, roas_total_b, 'x', decimals=2)}")
print()
print(f"Melhoraram: {len(improvements)} campanha(s): {', '.join(improvements) if improvements else 'nenhuma'}")
print(f"Pioraram:   {len(declines)} campanha(s): {', '.join(declines) if declines else 'nenhuma'}")
print(f"Estaveis:   {len(stable)} campanha(s)")
```

**Para datas customizadas**, substitua a função `fetch` por:
```python
def fetch_custom(since, until, label):
    # since/until no formato "YYYY-MM-DD"
    fields = f"id,name,status,objective,insights{{spend,impressions,clicks,ctr,cpc,reach,frequency,actions,action_values}}"
    time_range = json.dumps({"since": since, "until": until})
    params = urllib.parse.urlencode({"fields": fields, "time_range": time_range, "access_token": token})
    url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"
    with urllib.request.urlopen(url) as r:
        return {c["id"]: c for c in json.loads(r.read()).get("data", [])}
```

---

## Como apresentar

1. **Headline** — em uma frase: a conta melhorou, piorou ou ficou estável?
2. **Destaques positivos** — campanhas que melhoraram ROAS/CTR significativamente
3. **Alertas** — campanhas que pioraram e precisam de atenção
4. **Tendência de frequência** — se está subindo em todas as campanhas
5. **Recomendação para a próxima semana/mês**

### Variações de comparação mais úteis

| Pergunta do cliente | Comparação |
|---|---|
| "Como foi essa semana?" | `last_7d` vs `last_week_mon_sun` |
| "Esse mês tá melhor que o anterior?" | `this_month` vs `last_month` |
| "Black Friday foi melhor que o ano normal?" | datas customizadas |
| "Valeu a pena aumentar o orçamento?" | antes e depois da mudança |
