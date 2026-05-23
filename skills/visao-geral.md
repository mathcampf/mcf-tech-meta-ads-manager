# Skill: visao-geral
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Snapshot completo de todas as campanhas da conta: gasto, frequência, alertas e métricas contextuais por tipo de campanha (funil de vendas para sales, vídeo para engajamento, tráfego qualificado para tráfego). Ideal para iniciar qualquer sessão de análise.

---

## Instruções para o Claude

1. Leia o script com o Read tool: `../scripts/visao_geral.py` — anote o caminho absoluto retornado
2. Execute diretamente: `python3 <caminho_absoluto>`
3. Interprete o output seguindo as diretrizes abaixo

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
