# Skill: funil-conversao
**Plugin:** mcf-tech-meta-ads-manager
**Idioma:** Português

## Descrição
Analisa o funil completo de conversão de e-commerce: de visualização de produto até compra. Identifica em qual etapa o funil está quebrando e onde está o maior desperdício de orçamento.

---

## Instruções para o Claude

1. Leia o script com o Read tool: `../scripts/funil_conversao.py` — anote o caminho absoluto retornado
2. Execute diretamente: `python3 <caminho_absoluto>`
3. Apresente a análise do funil com interpretação das taxas de conversão

---

## Como interpretar o funil

### Taxas de conversão saudáveis (e-commerce)

| Etapa | Taxa esperada | Abaixo disso = problema |
|---|---|---|
| Clique → Landing Page | > 60% | Público ruim ou página lenta |
| Landing Page → Ver produto | > 40% | Página inicial pouco atrativa |
| Ver produto → Carrinho | > 5% | Produto, preço ou descrição |
| Carrinho → Checkout | > 40% | UX, frete surpresa |
| Checkout → Compra | > 50% | Pagamento, confiança, frete |

### O que apresentar ao usuário

1. **Onde está o maior vazamento do funil** — a etapa com a maior queda percentual
2. **Se o problema é no anúncio** (CTR baixo, LPV baixo) ou **no site** (cart/checkout baixos)
3. **CPA por etapa** — quanto custa trazer alguém até o carrinho, até o checkout, até a compra
4. **Recomendação prioritária** — 1 ação concreta para atacar o maior gargalo

### Distinção importante: problema de mídia vs problema de site
- **CTR baixo / LPV baixo** → problema no anúncio (criativo, público, copy)
- **LPV alto / Carrinho baixo** → problema na página de produto
- **Carrinho alto / Checkout baixo** → problema de UX (frete, valor mínimo, login obrigatório)
- **Checkout alto / Compra baixa** → problema de pagamento (parcelamento, boleto, confiança)
