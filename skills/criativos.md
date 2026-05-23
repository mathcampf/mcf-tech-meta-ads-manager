# Skill: criativos
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Analisa a performance de cada anúncio (criativo) dentro de uma campanha. Identifica quais criativos estão ganhando, quais estão perdendo, concentração de budget, e quando é hora de inserir novos criativos.

---

## Instruções para o Claude

### Passo 1 — Selecionar a campanha

Se o usuário não especificou:
1. Leia o script com o Read tool: `../scripts/lista_campanhas.py` — anote o caminho absoluto
2. Execute diretamente: `python3 <caminho_absoluto>`
3. Mostre a lista ao usuário e pergunte qual campanha analisar

### Passo 2 — Analisar criativos da campanha

1. Leia o script com o Read tool: `../scripts/criativos.py` — anote o caminho absoluto
2. Execute: `python3 <caminho_absoluto> <CAMPAIGN_ID>`
3. Com os dados, apresente ao usuário:
   - **Criativo vencedor** — qual está recebendo mais budget e por quê o algoritmo escolheu ele
   - **Criativos perdedores** — o que os diferencia do vencedor
   - **Concentração de budget** — se está muito concentrado e o que isso significa
   - **Quando renovar** — baseado na frequência do criativo principal
   - **Recomendação de próximo teste** — que tipo de criativo testar a seguir

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
