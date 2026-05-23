# Skill: diagnostico-campanha
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Análise profunda de uma campanha específica: performance geral, breakdown por conjuntos de anúncios, diagnóstico de frequência contextualizado e recomendações práticas.

---

## Instruções para o Claude

### Passo 1 — Listar campanhas disponíveis

1. Leia o script com o Read tool: `../scripts/lista_campanhas.py` — anote o caminho absoluto
2. Execute diretamente: `python3 <caminho_absoluto>`
3. Mostre a lista ao usuário e pergunte: **"Qual campanha você quer diagnosticar?"**

### Passo 2 — Diagnosticar a campanha escolhida

1. Identifique o ID da campanha na lista mostrada no passo anterior
2. Leia o script com o Read tool: `../scripts/diagnostico_campanha.py` — anote o caminho absoluto
3. Execute: `python3 <caminho_absoluto> <CAMPAIGN_ID>`
4. Com os dados em mãos, apresente ao usuário:
   - **Resumo executivo** — 2-3 linhas sobre o estado geral da campanha
   - **Diagnóstico de frequência** — use os benchmarks abaixo por tipo
   - **Análise dos conjuntos** — quais estão performando, quais estão drenando
   - **Recomendações práticas** — ações concretas que o usuário pode tomar hoje

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
