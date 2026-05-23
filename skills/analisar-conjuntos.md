# Skill: analisar-conjuntos
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Analisa os conjuntos de anúncios (ad sets) de uma campanha específica. Identifica quais estão performando, quais estão drenando orçamento e onde focar a otimização.

---

## Instruções para o Claude

### Passo 1 — Selecionar a campanha

Se o usuário já mencionou a campanha, use o ID diretamente e pule para o Passo 2.

Caso contrário:
1. Leia o script com o Read tool: `../scripts/lista_campanhas.py` — anote o caminho absoluto
2. Execute diretamente: `python3 <caminho_absoluto>`
3. Mostre a lista ao usuário e pergunte qual campanha analisar

### Passo 2 — Analisar os conjuntos

1. Leia o script com o Read tool: `../scripts/analisar_conjuntos.py` — anote o caminho absoluto
2. Execute: `python3 <caminho_absoluto> <CAMPAIGN_ID>`
3. Com os dados, apresente:
   - **Ranking de performance** — do melhor ao pior conjunto
   - **Distribuição de orçamento** — se está concentrado demais em um só conjunto
   - **Conjuntos para pausar** — alta frequência + baixo ROAS/CTR
   - **Conjuntos para escalar** — boa performance + frequência saudável
   - **Recomendação de próximos passos**

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
