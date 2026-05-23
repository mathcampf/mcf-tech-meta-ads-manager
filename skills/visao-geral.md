# Skill: visao-geral
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Snapshot completo de todas as campanhas da conta: gasto, frequência, alertas e métricas contextuais por tipo de campanha (funil de vendas para sales, vídeo para engajamento, tráfego qualificado para tráfego). Ideal para iniciar qualquer sessão de análise.

---

## Instruções para o Claude

1. Escreva o script abaixo em `/tmp/mcf_visao_geral.py`
2. Execute com `python3 /tmp/mcf_visao_geral.py`
3. Delete com `rm /tmp/mcf_visao_geral.py`
4. Interprete o output seguindo as diretrizes abaixo

---

## Script

```python
import urllib.request
import urllib.parse
import json
import os

token = os.environ.get("META_ACCESS_TOKEN")
account_id = os.environ.get("META_AD_ACCOUNT_ID")

if not token or not account_id:
    print("ERRO: META_ACCESS_TOKEN ou META_AD_ACCOUNT_ID nao encontrados.")
    print("Execute o skill 'setup' para configurar suas credenciais.")
    exit(1)

params = urllib.parse.urlencode({
    "fields": "id,name,status,objective,daily_budget,lifetime_budget,insights.date_preset(last_30d){spend,impressions,clicks,ctr,cpc,cpm,reach,frequency,actions,action_values,outbound_clicks,video_avg_time_watched_actions}",
    "limit": 50,
    "access_token": token
})

url = f"https://graph.facebook.com/v19.0/{account_id}/campaigns?{params}"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
except Exception as e:
    print(f"ERRO ao conectar com a API do Meta: {e}")
    exit(1)

campaigns = data.get("data", [])
active = [c for c in campaigns if c["status"] == "ACTIVE"]
paused = [c for c in campaigns if c["status"] == "PAUSED"]

total_spend = sum(float(c.get("insights", {}).get("data", [{}])[0].get("spend", 0)) for c in campaigns)

print("=" * 60)
print("VISAO GERAL DA CONTA — ULTIMOS 30 DIAS")
print("=" * 60)
print(f"Campanhas ativas:   {len(active)}")
print(f"Campanhas pausadas: {len(paused)}")
print(f"Gasto total:        R${total_spend:.2f}")
print()

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
    n = name.upper()
    obj = objective.upper()
    if "RMKT" in n or "REMARKETING" in n: return "remarketing"
    if "LAL" in n or "LOOKALIKE" in n or "PROSPEC" in n: return "prospeccao"
    if "SEGUIDORES" in n or "FOLLOWERS" in n: return "seguidores"
    if "VIDEO" in n: return "video"
    if "ENGAJ" in n or "ENGAGEMENT" in obj: return "engajamento"
    if "LEADS" in n or "LEAD" in obj: return "leads"
    if "SALES" in obj or "CATALOG" in obj: return "vendas"
    if "TRAFFIC" in obj: return "trafego"
    return "geral"

def frequency_alert(frequency, campaign_type):
    thresholds = {
        "prospeccao": (5, 7),
        "seguidores":  (5, 8),
        "trafego":     (4, 6),
        "engajamento": (7, 10),
        "video":       (7, 10),
        "leads":       (5, 8),
        "vendas":      (6, 9),
        "remarketing": (10, 15),
        "geral":       (5, 7),
    }
    warn, crit = thresholds.get(campaign_type, (5, 7))
    if frequency >= crit:
        return "SATURADA"
    if frequency >= warn:
        return "ATENCAO"
    return "OK"

print("CAMPANHAS ATIVAS")
print("-" * 60)

for c in active:
    insights = c.get("insights", {}).get("data", [{}])[0]
    if not insights:
        print(f"\n[SEM DADOS] {c['name']}")
        continue

    actions = insights.get("actions", [])
    action_values = insights.get("action_values", [])
    outbound = insights.get("outbound_clicks", [])
    video_time = insights.get("video_avg_time_watched_actions", [])

    spend       = float(insights.get("spend", 0))
    impressions = int(insights.get("impressions", 0))
    reach       = int(insights.get("reach", 0))
    frequency   = float(insights.get("frequency", 0))
    ctr         = float(insights.get("ctr", 0))
    cpc         = float(insights.get("cpc", 0))
    cpm         = float(insights.get("cpm", 0))
    link_clicks = int(insights.get("clicks", 0))

    outbound_clicks = int(outbound[0]["value"]) if outbound else 0
    avg_video_sec   = int(video_time[0]["value"]) if video_time else 0

    lpv            = get_action(actions, "landing_page_view", "omni_landing_page_view")
    video_views    = get_action(actions, "video_view")
    page_fans      = get_action(actions, "page_fan")
    page_eng       = get_action(actions, "page_engagement", "post_engagement")
    post_saves     = get_action(actions, "onsite_conversion.post_save")
    post_reactions = get_action(actions, "post_reaction")
    purchases      = get_action(actions, "purchase")
    add_to_cart    = get_action(actions, "add_to_cart")
    initiate_chk   = get_action(actions, "initiate_checkout")
    leads          = get_action(actions, "lead", "offsite_conversion.fb_pixel_lead")
    revenue        = get_action_value(action_values, "purchase")

    campaign_type = detect_type(c["name"], c["objective"])
    freq_status   = frequency_alert(frequency, campaign_type)
    roas          = round(revenue / spend, 2) if spend > 0 and revenue > 0 else None

    daily    = c.get("daily_budget")
    lifetime = c.get("lifetime_budget")
    budget_str = f"R${int(daily)/100:.2f}/dia" if daily else f"R${int(lifetime)/100:.2f} total" if lifetime else "N/A"

    print(f"\nNome:        {c['name']}")
    print(f"ID:          {c['id']}")
    print(f"Tipo:        {campaign_type.upper()} | Objetivo: {c['objective']}")
    print(f"Orcamento:   {budget_str} | Gasto 30d: R${spend:.2f}")
    print(f"Alcance:     {reach:,} | Impressoes: {impressions:,} | CPM: R${cpm:.2f}")
    print(f"Frequencia:  {frequency:.2f}x [{freq_status}]")

    if campaign_type in ("vendas", "remarketing", "prospeccao", "geral"):
        print(f"Funil:       Carrinho: {add_to_cart:,} | Checkout: {initiate_chk:,} | Compras: {purchases:,}")
        if revenue > 0:
            cpa = spend / purchases if purchases > 0 else 0
            print(f"Receita:     R${revenue:.2f} | ROAS: {roas}x | CPA: R${cpa:.2f}")
        print(f"Trafego:     Link clicks: {link_clicks:,} | LPV: {lpv:,} | Externos: {outbound_clicks:,}")
        print(f"CTR:         {ctr:.2f}% | CPC: R${cpc:.2f}")

    elif campaign_type in ("engajamento", "video", "seguidores"):
        print(f"Engajamento: Views: {video_views:,} | Reacoes: {post_reactions:,} | Saves: {post_saves:,} | Eng total: {page_eng:,}")
        if avg_video_sec > 0:
            print(f"Video:       Tempo medio: {avg_video_sec}s")
        if page_fans > 0:
            print(f"Seguidores:  +{page_fans:,} novos seguidores/fas")
        else:
            print(f"Seguidores:  Novos seguidores nao rastreados (objetivo nao otimiza para follows)")
        print(f"CTR:         {ctr:.2f}% | CPC: R${cpc:.2f}")

    elif campaign_type == "trafego":
        lpv_rate = (lpv / link_clicks * 100) if link_clicks > 0 else 0
        print(f"Trafego:     Link clicks: {link_clicks:,} | LPV: {lpv:,} ({lpv_rate:.1f}% qualificado) | Externos: {outbound_clicks:,}")
        print(f"CTR:         {ctr:.2f}% | CPC: R${cpc:.2f}")

    elif campaign_type == "leads":
        cpl = spend / leads if leads > 0 else 0
        print(f"Leads:       {leads:,} | CPL: R${cpl:.2f}")
        print(f"CTR:         {ctr:.2f}% | CPC: R${cpc:.2f}")

print()
print("CAMPANHAS PAUSADAS")
print("-" * 60)
for c in paused:
    print(f"- {c['name']} ({c['objective']})")
```

---

## Como interpretar o output

### Frequência por tipo
- `OK` → saudável, continue investindo
- `ATENCAO` → monitorar, audiência começando a saturar
- `SATURADA` → ação necessária: ampliar público, renovar criativos ou pausar

### Seguidores
Se o campo "Novos seguidores não rastreados" aparecer, significa que a campanha não está otimizada para follows — está apenas gerando tráfego para o perfil. Uma campanha real de seguidores precisa usar objetivo de engajamento com otimização para follows.

### Funil de vendas
Analise a taxa de conversão entre etapas:
- Carrinho → Checkout: abaixo de 30% pode indicar problema de UX no site
- Checkout → Compra: abaixo de 50% pode indicar problema no processo de pagamento

### Tráfego qualificado
Landing Page View (LPV) vs Link Click: se LPV for menos de 50% dos cliques, o público pode estar clicando mas abandonando antes de carregar a página.

### O que fazer após
- Destaque alertas de frequência com urgência
- Para campanhas de vendas, destaque ROAS e CPA
- Para engajamento, destaque video views e saves
- Sugira `diagnostico-campanha` para campanhas problemáticas
