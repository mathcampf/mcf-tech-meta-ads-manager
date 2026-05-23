# Skill: comparar-periodos
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

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

Mapeie a resposta para os argumentos do script:
- "Esta semana vs semana passada" → `last_7d last_week_mon_sun "Esta semana" "Semana passada"`
- "Este mês vs mês passado" → `this_month last_month "Este mês" "Mês passado"`

### Passo 2 — Executar a comparação

1. Leia o script com o Read tool: `../scripts/comparar_periodos.py` — anote o caminho absoluto
2. Execute com os argumentos do período escolhido:

   ```
   python3 <caminho_absoluto> <PRESET_A> <PRESET_B> "<LABEL_A>" "<LABEL_B>"
   ```

   Exemplos:
   - Esta semana vs passada: `python3 <caminho> last_7d last_week_mon_sun "Esta semana" "Semana passada"`
   - Este mês vs passado: `python3 <caminho> this_month last_month "Este mês" "Mês passado"`

3. Apresente conforme as diretrizes abaixo

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
