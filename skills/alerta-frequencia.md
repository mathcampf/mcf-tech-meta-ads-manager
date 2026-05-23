# Skill: alerta-frequencia
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Varre todas as campanhas ativas e emite alertas de frequência contextualizados por tipo de campanha. Considera também o ROAS — uma campanha com frequência alta mas ROAS excelente recebe uma recomendação diferente de uma com ROAS ruim.

---

## Instruções para o Claude

1. Leia o script com o Read tool: `../scripts/alerta_frequencia.py` — anote o caminho absoluto retornado
2. Execute diretamente: `python3 <caminho_absoluto>`
3. Interprete os resultados seguindo as diretrizes abaixo

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
