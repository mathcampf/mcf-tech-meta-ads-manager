# Skill: criativos
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Analisa a performance de cada anúncio (criativo) dentro de uma campanha. Identifica quais criativos estão ganhando, quais estão perdendo, concentração de budget, e quando é hora de inserir novos criativos.

---

## Instruções para o Claude

### Passo 1 — Selecionar a campanha

Se o usuário não especificou, escreva o script abaixo em `/tmp/mcf_lista_camp.py`, execute, mostre e pergunte. Delete depois.

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

### Passo 2 — Analisar criativos da campanha

Com o ID da campanha, escreva o script abaixo em `/tmp/mcf_criativos.py`, **substituindo `CAMPAIGN_ID_AQUI`** pelo ID correto, execute e delete.

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
campaign_id = "CAMPAIGN_ID_AQUI"

params = urllib.parse.urlencode({
    "fields": "id,name,status,creative{id,name,object_type},insights.date_preset(last_30d){spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,outbound_clicks,video_avg_time_watched_actions,video_p100_watched_actions}",
    "limit": 50,
    "access_token": token
})

url = f"https://graph.facebook.com/v19.0/{campaign_id}/ads?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

ads = data.get("data", [])

def get_action(actions, *types):
    for t in types:
        val = next((a["value"] for a in actions if a["action_type"] == t), None)
        if val is not None:
            return int(val)
    return 0

def get_value(avs, *types):
    for t in types:
        val = next((a["value"] for a in avs if a["action_type"] == t), None)
        if val is not None:
            return float(val)
    return 0.0

total_spend = sum(float(a.get("insights", {}).get("data", [{}])[0].get("spend", 0)) for a in ads)

print("=" * 60)
print("ANALISE DE CRIATIVOS")
print("=" * 60)
print(f"Total de anuncios: {len(ads)}")
print(f"Gasto total 30d:   R${total_spend:.2f}")
print()

rows = []
for ad in ads:
    insights = ad.get("insights", {}).get("data", [{}])[0]
    if not insights:
        continue

    actions  = insights.get("actions", [])
    avs      = insights.get("action_values", [])
    outbound = insights.get("outbound_clicks", [])
    vtime    = insights.get("video_avg_time_watched_actions", [])
    vp100    = insights.get("video_p100_watched_actions", [])
    creative = ad.get("creative", {})

    spend       = float(insights.get("spend", 0))
    impressions = int(insights.get("impressions", 0))
    reach       = int(insights.get("reach", 0))
    frequency   = float(insights.get("frequency", 0))
    ctr         = float(insights.get("ctr", 0))
    cpc         = float(insights.get("cpc", 0))
    cpm         = float(insights.get("cpm", 0))
    clicks      = int(insights.get("clicks", 0))

    outb          = int(outbound[0]["value"]) if outbound else 0
    avg_vid_sec   = int(vtime[0]["value"]) if vtime else 0
    vid_complete  = int(vp100[0]["value"]) if vp100 else 0
    lpv           = get_action(actions, "landing_page_view", "omni_landing_page_view")
    purchases     = get_action(actions, "purchase")
    add_to_cart   = get_action(actions, "add_to_cart")
    video_views   = get_action(actions, "video_view")
    revenue       = get_value(avs, "purchase")
    roas          = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None
    cpa           = round(spend / purchases, 2) if purchases > 0 else None
    pct_spend     = (spend / total_spend * 100) if total_spend > 0 else 0
    fmt_type      = creative.get("object_type", "N/A")

    rows.append({
        "id": ad["id"], "name": ad["name"], "status": ad["status"],
        "format": fmt_type, "spend": spend, "pct_spend": pct_spend,
        "impressions": impressions, "reach": reach, "frequency": frequency,
        "ctr": ctr, "cpc": cpc, "cpm": cpm, "clicks": clicks,
        "lpv": lpv, "outb": outb, "purchases": purchases,
        "add_to_cart": add_to_cart, "revenue": revenue, "roas": roas,
        "cpa": cpa, "video_views": video_views, "avg_vid_sec": avg_vid_sec,
        "vid_complete": vid_complete,
    })

rows.sort(key=lambda x: x["spend"], reverse=True)

for i, r in enumerate(rows):
    rank = "VENCEDOR" if i == 0 else f"#{i+1}"
    roas_str = f"{r['roas']}x" if r['roas'] else "N/A"
    cpa_str  = f"R${r['cpa']:.2f}" if r['cpa'] else "N/A"

    print(f"[{rank}] [{r['status']}] {r['name']}")
    print(f"  Formato:    {r['format']}")
    print(f"  Gasto:      R${r['spend']:.2f} ({r['pct_spend']:.1f}% do total)")
    print(f"  Alcance:    {r['reach']:,} | Freq: {r['frequency']:.2f}x | CPM: R${r['cpm']:.2f}")
    print(f"  CTR:        {r['ctr']:.2f}% | CPC: R${r['cpc']:.2f}")
    if r["purchases"] > 0:
        print(f"  Compras:    {r['purchases']:,} | Carrinho: {r['add_to_cart']:,}")
        print(f"  Receita:    R${r['revenue']:.2f} | ROAS: {roas_str} | CPA: {cpa_str}")
    if r["video_views"] > 0:
        compl_rate = (r['vid_complete'] / r['video_views'] * 100) if r['video_views'] > 0 else 0
        print(f"  Video:      {r['video_views']:,} views | Tempo medio: {r['avg_vid_sec']}s | Completos: {compl_rate:.1f}%")
    if r["lpv"] > 0:
        print(f"  LPV:        {r['lpv']:,} | Externos: {r['outb']:,}")
    print()

print("=" * 60)
print("CONCENTRACAO DE BUDGET")
print("=" * 60)
if rows:
    top = rows[0]
    print(f"Criativo principal: {top['name']}")
    print(f"Concentracao:       {top['pct_spend']:.1f}% do gasto total")
    if top['pct_spend'] > 80:
        print("ALERTA: Budget muito concentrado em 1 criativo.")
        print("        Meta esta otimizando agressivamente. Considere:")
        print("        - Inserir novos criativos para testar")
        print("        - Verificar se os outros anuncios estao com status ATIVO")
        print(f"        - O criativo principal tem frequencia de {top['frequency']:.1f}x — renovar em breve")
    elif top['pct_spend'] > 60:
        print("Concentracao moderada. Normal em campanhas maduras.")
        print("Monitore a frequencia do criativo principal para saber quando renovar.")
    else:
        print("Budget bem distribuido entre os criativos.")
```

### Passo 3 — Análise e recomendações

Com os dados, apresente ao usuário:

1. **Criativo vencedor** — qual está recebendo mais budget e por quê o algoritmo escolheu ele
2. **Criativos perdedores** — o que os diferencia do vencedor
3. **Concentração de budget** — se está muito concentrado e o que isso significa
4. **Quando renovar** — baseado na frequência do criativo principal
5. **Recomendação de próximo teste** — que tipo de criativo testar a seguir

---

## Benchmarks de performance criativa

| Métrica | Bom | Atenção | Ruim |
|---|---|---|---|
| CTR (feed) | > 2% | 1–2% | < 1% |
| CTR (stories/reels) | > 1% | 0.5–1% | < 0.5% |
| Video completion rate | > 25% | 10–25% | < 10% |
| Tempo médio vídeo | > 15s | 5–15s | < 5s |
| Frequência criativo | < 5x | 5–8x | > 8x |

## Quando inserir novos criativos

- Frequência do vencedor > 6x → testar novo criativo
- CTR caindo semana a semana → criativo esgotado
- CPM subindo sem aumento de conversão → audiência cansada do criativo
- ROAS caindo enquanto spend permanece → sinal clássico de creative fatigue

## Tipos de teste recomendados

- **Mesmo produto, novo ângulo**: diferente benefit highlight
- **UGC vs produzido**: conteúdo de cliente vs produção profissional
- **Estático vs vídeo**: testar formato diferente
- **Copy longa vs curta**: testar quantidade de texto
