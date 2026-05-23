---
description: Varre todas as campanhas ativas e emite alertas de saturação de frequência contextualizados por tipo, cruzando com ROAS para dar a recomendação correta (expandir público, renovar criativos ou pausar). Use quando o usuário quer checar fadiga de anúncios, saturação de audiência ou frequência.
allowed-tools: Bash(python3:*), Bash(rm:*)
---
## Descrição
Varre todas as campanhas ativas e emite alertas de frequência contextualizados por tipo de campanha. Considera também o ROAS — uma campanha com frequência alta mas ROAS excelente recebe uma recomendação diferente de uma com ROAS ruim.

---

## Instruções para o Claude

1. Escreva o script abaixo em `/tmp/mcf_alerta_frequencia.py`
2. Execute com `python3 /tmp/mcf_alerta_frequencia.py`
3. Delete com `rm /tmp/mcf_alerta_frequencia.py`
4. Interprete os resultados seguindo as diretrizes abaixo

---

## Script

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")

params = urllib.parse.urlencode({
    "fields": "id,name,status,objective,daily_budget,insights.date_preset(last_30d){spend,reach,frequency,impressions,actions,action_values}",
    "limit": 50,
    "access_token": token
})

url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

def detect_type(name, objective):
    n, obj = name.upper(), objective.upper()
    if "RMKT" in n or "REMARKETING" in n: return "remarketing"
    if "LAL" in n or "LOOKALIKE" in n or "PROSPEC" in n: return "prospeccao"
    if "SEGUIDORES" in n or "FOLLOWERS" in n: return "seguidores"
    if "ENGAJ" in n or "ENGAGEMENT" in obj: return "engajamento"
    if "VIDEO" in n: return "video"
    if "LEADS" in n: return "leads"
    return "geral"

thresholds = {
    "prospeccao": (5, 7),
    "seguidores":  (5, 8),
    "engajamento": (7, 10),
    "video":       (7, 10),
    "leads":       (5, 8),
    "remarketing": (10, 15),
    "geral":       (5, 7),
}

saturadas = []
atencao = []
saudaveis = []

for c in data.get("data", []):
    if c["status"] != "ACTIVE":
        continue

    insights = c.get("insights", {}).get("data", [{}])[0]
    if not insights:
        continue

    actions = insights.get("actions", [])
    action_values = insights.get("action_values", [])

    frequency   = float(insights.get("frequency", 0))
    spend       = float(insights.get("spend", 0))
    reach       = int(insights.get("reach", 0))
    impressions = int(insights.get("impressions", 0))
    purchases   = int(next((a["value"] for a in actions if a["action_type"] == "purchase"), 0))
    revenue     = float(next((a["value"] for a in action_values if a["action_type"] == "purchase"), 0))
    roas        = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None

    campaign_type = detect_type(c["name"], c.get("objective",""))
    warn, crit = thresholds.get(campaign_type, (5, 7))

    freq_status = "saturada" if frequency >= crit else "atencao" if frequency >= warn else "ok"

    is_sales_objective = "SALES" in c.get("objective","").upper() or "CATALOG" in c.get("objective","").upper()
    roas_status = None
    if roas is not None and is_sales_objective:
        if roas >= 10:   roas_status = "excelente"
        elif roas >= 3:  roas_status = "bom"
        elif roas >= 1:  roas_status = "abaixo"
        else:            roas_status = "prejuizo"

    if freq_status == "saturada" and roas_status == "excelente":
        recommendation = "EXPANDIR PUBLICO: alta frequencia, mas ROAS excelente. Audiencia pequena e convertendo bem — ampliar LAL ou adicionar novos publicos, nao pausar."
    elif freq_status == "saturada" and roas_status == "bom":
        recommendation = "RENOVAR CRIATIVOS: frequencia alta com ROAS bom. Trocar criativos pode manter performance enquanto reduz saturacao."
    elif freq_status == "saturada" and roas_status in ("abaixo", "prejuizo"):
        recommendation = "PAUSAR OU REESTRUTURAR: frequencia alta + ROAS ruim = desperdicio claro. Rever publico, criativos e estrategia de lance."
    elif freq_status == "saturada" and roas_status is None:
        recommendation = "MONITORAR: frequencia saturada, mas campanha nao e de vendas. Avaliar se engajamento/alcance justifica o investimento."
    elif freq_status == "atencao":
        recommendation = "MONITORAR: entrando na zona de saturacao. Preparar novos criativos e avaliar expansao de publico."
    else:
        recommendation = "Saudavel."

    entry = {
        "name": c["name"],
        "id": c["id"],
        "type": campaign_type,
        "frequency": frequency,
        "spend": spend,
        "reach": reach,
        "warn": warn,
        "crit": crit,
        "roas": roas if is_sales_objective else None,
        "roas_status": roas_status,
        "freq_status": freq_status,
        "recommendation": recommendation,
    }

    if freq_status == "saturada":
        saturadas.append(entry)
    elif freq_status == "atencao":
        atencao.append(entry)
    else:
        saudaveis.append(entry)

saturadas.sort(key=lambda x: x["frequency"], reverse=True)
atencao.sort(key=lambda x: x["frequency"], reverse=True)

print("=" * 60)
print("ALERTA DE FREQUENCIA — CAMPANHAS ATIVAS")
print("=" * 60)
print()

if saturadas:
    print(f"FREQUENCIA SATURADA ({len(saturadas)} campanha(s))")
    print("-" * 60)
    for c in saturadas:
        roas_str = f"{c['roas']}x" if c['roas'] else "N/A"
        print(f"\nCampanha:   {c['name']}")
        print(f"Tipo:       {c['type'].upper()} | Limite: {c['crit']}x")
        print(f"Frequencia: {c['frequency']:.2f}x | ROAS: {roas_str}")
        print(f"Alcance:    {c['reach']:,} pessoas | Gasto 30d: R${c['spend']:.2f}")
        print(f"ACAO:       {c['recommendation']}")
    print()

if atencao:
    print(f"ATENCAO ({len(atencao)} campanha(s)) — MONITORAR")
    print("-" * 60)
    for c in atencao:
        roas_str = f"{c['roas']}x" if c['roas'] else "N/A"
        print(f"\nCampanha:   {c['name']}")
        print(f"Tipo:       {c['type'].upper()} | Zona: {c['warn']}x–{c['crit']}x")
        print(f"Frequencia: {c['frequency']:.2f}x | ROAS: {roas_str}")
        print(f"ACAO:       {c['recommendation']}")
    print()

if saudaveis:
    print(f"SAUDAVEIS ({len(saudaveis)} campanha(s))")
    print("-" * 60)
    for c in saudaveis:
        roas_str = f"ROAS {c['roas']}x" if c['roas'] else ""
        print(f"- {c['name']} | Freq: {c['frequency']:.2f}x {roas_str}")

print()
print("=" * 60)
print(f"RESUMO: {len(saturadas)} saturada(s) | {len(atencao)} em atencao | {len(saudaveis)} saudavel(is)")
```

---

## Como interpretar e apresentar

### Lógica de recomendação (frequência + ROAS)

| Frequência | ROAS | Recomendação |
|---|---|---|
| Saturada | Excelente (10x+) | Expandir público — audiência pequena mas convertendo bem |
| Saturada | Bom (3x–10x) | Renovar criativos — manter performance, reduzir fadiga |
| Saturada | Ruim (<3x) | Pausar/reestruturar — desperdício claro |
| Saturada | N/A (não-vendas) | Avaliar se engajamento/alcance justifica |
| Atenção | Qualquer | Preparar novos criativos, monitorar |
| Saudável | Qualquer | Continuar, escalar se ROAS for bom |

### Tom ao apresentar

- Nunca diga apenas "pause a campanha" sem verificar o ROAS primeiro
- Frequência alta com ROAS alto = oportunidade de escala, não problema
- Frequência alta com ROAS baixo = emergência, agir imediatamente
- Sempre termine com a ação específica a tomar
