---
description: 'Faz um diagnóstico profundo de uma campanha específica: funil de conversão, performance por conjuntos de anúncios, benchmarks de frequência e recomendações práticas. Use quando o usuário quer analisar, diagnosticar ou entender melhor uma campanha específica.'
allowed-tools: Bash(python3:*), Bash(rm:*)
---
## Descrição
Análise profunda de uma campanha específica: performance geral, breakdown por conjuntos de anúncios, diagnóstico de frequência contextualizado e recomendações práticas.

---

## Instruções para o Claude

### Passo 1 — Listar campanhas disponíveis

Escreva o script abaixo em `/tmp/mcf_lista_campanhas.py`, execute e delete.
Mostre a lista ao usuário e pergunte: **"Qual campanha você quer diagnosticar?"**

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
    status_icon = "ATIVA" if c["status"] == "ACTIVE" else "PAUSADA"
    print(f"[{status_icon}] {c['name']}")
    print(f"  ID: {c['id']} | Gasto 30d: R${spend:.2f}")
    print()
```

### Passo 2 — Diagnosticar a campanha escolhida

Após o usuário escolher, identifique o ID da campanha pela lista.
Escreva o script abaixo em `/tmp/mcf_diagnostico.py`, **substituindo `CAMPAIGN_ID_AQUI`** pelo ID correto, execute e delete.

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")
campaign_id = "CAMPAIGN_ID_AQUI"

def get_url(endpoint, fields):
    params = urllib.parse.urlencode({
        "fields": fields,
        "access_token": token
    })
    return f"https://graph.facebook.com/v19.0/{endpoint}?{params}"

with urllib.request.urlopen(get_url(campaign_id, "id,name,status,objective,daily_budget,lifetime_budget,start_time,insights.date_preset(last_30d){spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,outbound_clicks,video_avg_time_watched_actions,video_p100_watched_actions}")) as r:
    campaign = json.loads(r.read())

with urllib.request.urlopen(get_url(f"{campaign_id}/adsets", "id,name,status,daily_budget,lifetime_budget,insights.date_preset(last_30d){spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,outbound_clicks}") + "&limit=20") as r:
    adsets_data = json.loads(r.read())

def get_action(actions, *types):
    for t in types:
        val = next((a["value"] for a in actions if a["action_type"] == t), None)
        if val is not None:
            return int(val)
    return 0

def get_action_value(action_values, *types):
    for t in types:
        val = next((a["value"] for a in action_values if a["action_type"] == t), None)
        if val is not None:
            return float(val)
    return 0.0

def detect_type(name, objective):
    n, obj = name.upper(), objective.upper()
    if "RMKT" in n or "REMARKETING" in n: return "REMARKETING"
    if "LAL" in n or "LOOKALIKE" in n or "PROSPEC" in n: return "PROSPECCAO"
    if "SEGUIDORES" in n or "FOLLOWERS" in n: return "SEGUIDORES"
    if "VIDEO" in n: return "VIDEO"
    if "ENGAJ" in n or "ENGAGEMENT" in obj: return "ENGAJAMENTO"
    if "LEADS" in n or "LEAD" in obj: return "LEADS"
    if "SALES" in obj or "CATALOG" in obj: return "VENDAS"
    if "TRAFFIC" in obj: return "TRAFEGO"
    return "GERAL"

insights = campaign.get("insights", {}).get("data", [{}])[0]
actions      = insights.get("actions", [])
action_values = insights.get("action_values", [])
outbound_raw  = insights.get("outbound_clicks", [])
video_time    = insights.get("video_avg_time_watched_actions", [])
video_p100    = insights.get("video_p100_watched_actions", [])

spend       = float(insights.get("spend", 0))
impressions = int(insights.get("impressions", 0))
reach       = int(insights.get("reach", 0))
frequency   = float(insights.get("frequency", 0))
ctr         = float(insights.get("ctr", 0))
cpc         = float(insights.get("cpc", 0))
cpm         = float(insights.get("cpm", 0))
link_clicks = int(insights.get("clicks", 0))

outbound_clicks  = int(outbound_raw[0]["value"]) if outbound_raw else 0
avg_video_sec    = int(video_time[0]["value"]) if video_time else 0
video_completions = int(video_p100[0]["value"]) if video_p100 else 0

lpv          = get_action(actions, "landing_page_view", "omni_landing_page_view")
video_views  = get_action(actions, "video_view")
page_fans    = get_action(actions, "page_fan")
page_eng     = get_action(actions, "page_engagement", "post_engagement")
post_saves   = get_action(actions, "onsite_conversion.post_save")
reactions    = get_action(actions, "post_reaction")
purchases    = get_action(actions, "purchase")
add_to_cart  = get_action(actions, "add_to_cart")
initiate_chk = get_action(actions, "initiate_checkout")
view_content = get_action(actions, "view_content")
leads        = get_action(actions, "lead", "offsite_conversion.fb_pixel_lead")
revenue      = get_action_value(action_values, "purchase")

campaign_type = detect_type(campaign["name"], campaign["objective"])
roas = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None
daily = campaign.get("daily_budget")
lifetime = campaign.get("lifetime_budget")
budget_str = f"R${int(daily)/100:.2f}/dia" if daily else f"R${int(lifetime)/100:.2f} total" if lifetime else "N/A"

print("=" * 60)
print(f"DIAGNOSTICO: {campaign['name']}")
print("=" * 60)
print(f"Status:      {campaign['status']}")
print(f"Tipo:        {campaign_type}")
print(f"Objetivo:    {campaign['objective']}")
print(f"Orcamento:   {budget_str}")
print()
print("PERFORMANCE — ULTIMOS 30 DIAS")
print("-" * 40)
print(f"Gasto:       R${spend:.2f}")
print(f"Alcance:     {reach:,} pessoas | Impressoes: {impressions:,}")
print(f"Frequencia:  {frequency:.2f}x")
print(f"CPM:         R${cpm:.2f}")
print()

if campaign_type in ("VENDAS", "REMARKETING", "PROSPECCAO", "GERAL"):
    lpv_rate = (lpv / link_clicks * 100) if link_clicks > 0 else 0
    cart_rate = (initiate_chk / add_to_cart * 100) if add_to_cart > 0 else 0
    buy_rate  = (purchases / initiate_chk * 100) if initiate_chk > 0 else 0
    print("FUNIL DE CONVERSAO")
    print(f"  Visualizou produto: {view_content:,}")
    print(f"  Adicionou carrinho: {add_to_cart:,}")
    print(f"  Iniciou checkout:   {initiate_chk:,}  ({cart_rate:.1f}% do carrinho)")
    print(f"  Comprou:            {purchases:,}  ({buy_rate:.1f}% do checkout)")
    if revenue > 0:
        cpa = spend / purchases if purchases > 0 else 0
        print(f"  Receita total:      R${revenue:.2f} | ROAS: {roas}x | CPA: R${cpa:.2f}")
    print()
    print("TRAFEGO")
    print(f"  Link clicks:        {link_clicks:,}")
    print(f"  Landing page views: {lpv:,}  ({lpv_rate:.1f}% qualificado)")
    print(f"  Cliques externos:   {outbound_clicks:,}")
    print(f"  CTR: {ctr:.2f}% | CPC: R${cpc:.2f}")

elif campaign_type in ("ENGAJAMENTO", "VIDEO", "SEGUIDORES", "TRAFEGO"):
    print("ENGAJAMENTO E ALCANCE")
    print(f"  Video views:        {video_views:,}")
    if avg_video_sec > 0:
        print(f"  Tempo medio video:  {avg_video_sec}s")
    if video_completions > 0:
        print(f"  Videos completos:   {video_completions:,}")
    print(f"  Engajamento total:  {page_eng:,}")
    print(f"  Reacoes:            {reactions:,}")
    print(f"  Saves:              {post_saves:,}")
    if page_fans > 0:
        print(f"  Novos seguidores:   +{page_fans:,}")
    else:
        print(f"  Novos seguidores:   Nao rastreado")
        print(f"  AVISO: Campanha otimizada para {campaign['objective']}, nao para follows.")
        print(f"         Para rastrear seguidores reais, use objetivo com otimizacao para follows.")
    print()
    print("TRAFEGO")
    lpv_rate = (lpv / link_clicks * 100) if link_clicks > 0 else 0
    print(f"  Link clicks:        {link_clicks:,}")
    print(f"  Landing page views: {lpv:,}  ({lpv_rate:.1f}% qualificado)")
    print(f"  Cliques externos:   {outbound_clicks:,}")
    print(f"  CTR: {ctr:.2f}% | CPC: R${cpc:.2f}")

elif campaign_type == "LEADS":
    cpl = spend / leads if leads > 0 else 0
    print("GERACAO DE LEADS")
    print(f"  Leads:              {leads:,}")
    print(f"  CPL:                R${cpl:.2f}")
    print(f"  CTR: {ctr:.2f}% | CPC: R${cpc:.2f}")

print()
print("CONJUNTOS DE ANUNCIOS")
print("-" * 40)
adsets = adsets_data.get("data", [])
for adset in sorted(adsets, key=lambda x: float(x.get("insights", {}).get("data", [{}])[0].get("spend", 0)), reverse=True):
    ai = adset.get("insights", {}).get("data", [{}])[0]
    if not ai:
        continue
    aa = ai.get("actions", [])
    av = ai.get("action_values", [])
    ob = ai.get("outbound_clicks", [])
    a_spend   = float(ai.get("spend", 0))
    a_freq    = float(ai.get("frequency", 0))
    a_ctr     = float(ai.get("ctr", 0))
    a_reach   = int(ai.get("reach", 0))
    a_lpv     = get_action(aa, "landing_page_view", "omni_landing_page_view")
    a_cart    = get_action(aa, "add_to_cart")
    a_buy     = get_action(aa, "purchase")
    a_rev     = get_action_value(av, "purchase")
    a_vviews  = get_action(aa, "video_view")
    a_outb    = int(ob[0]["value"]) if ob else 0
    a_budget  = adset.get("daily_budget") or adset.get("lifetime_budget")
    a_bstr    = f"R${int(a_budget)/100:.2f}" if a_budget else "N/A"
    a_roas    = round(a_rev / a_spend, 2) if a_spend > 0 and a_rev > 0 else None

    print(f"\n[{adset['status']}] {adset['name']}")
    print(f"  Orcamento: {a_bstr} | Gasto: R${a_spend:.2f}")
    print(f"  Alcance:   {a_reach:,} | Freq: {a_freq:.2f}x | CTR: {a_ctr:.2f}%")
    if a_buy > 0:
        print(f"  Funil:     Carrinho: {a_cart:,} | Compras: {a_buy:,} | Receita: R${a_rev:.2f} | ROAS: {a_roas}x")
    if a_vviews > 0:
        print(f"  Video:     {a_vviews:,} views")
    if a_lpv > 0:
        print(f"  LPV:       {a_lpv:,} | Externos: {a_outb:,}")
```

### Passo 3 — Gerar diagnóstico completo

Com os dados em mãos, apresente ao usuário:

1. **Resumo executivo** — 2-3 linhas sobre o estado geral da campanha
2. **Diagnóstico de frequência** — use os benchmarks abaixo por tipo
3. **Análise dos conjuntos** — quais estão performando, quais estão drenando
4. **Recomendações práticas** — ações concretas que o usuário pode tomar hoje

---

## Benchmarks de frequência por tipo

| Tipo | Saudável | Atenção | Saturado |
|---|---|---|---|
| Prospecção / LAL | até 5x | 5–7x | acima de 7x |
| Engajamento | até 7x | 7–10x | acima de 10x |
| Remarketing | até 10x | 10–15x | acima de 15x |

## Benchmarks de ROAS (referência geral e-commerce)

| ROAS | Interpretação |
|---|---|
| Abaixo de 1x | Prejuízo — ação imediata |
| 1x–2x | Abaixo do ideal — revisar |
| 2x–4x | Aceitável |
| Acima de 4x | Boa performance |

## Recomendações padrão por problema

**Frequência saturada (prospecção):**
- Ampliar o público-alvo (LAL maior, novos interesses)
- Renovar criativos
- Aumentar orçamento para alcançar mais pessoas

**Frequência saturada (remarketing):**
- Reduzir janela do público (ex: de 30 para 7 dias)
- Adicionar exclusão de compradores recentes
- Renovar criativos

**CTR baixo (abaixo de 1%):**
- Revisar copy e criativo
- Testar novos formatos (vídeo vs imagem)
- Revisar segmentação

**CPC alto:**
- Verificar se o público está muito restrito
- Testar criativos mais relevantes para o público
- Revisar lance e otimização
