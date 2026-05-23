# mcf-tech-meta-ads-manager — Planning & Learnings

**Plugin name:** `mcf-tech-meta-ads-manager`
**Skills invocadas como:** `mcf-tech-meta-ads-manager:setup`, `mcf-tech-meta-ads-manager:analisar-campanha`, etc.

## Concept

A Claude Code **skill/plugin** for Facebook Ads management, distributed via **Cowork** to consultancy clients. Clients install it once and get a curated AI assistant built on Matheus's methodology.

---

## Business Model

### Pricing reference
| Oferta | O que inclui | Preço alvo |
|---|---|---|
| Setup único | Diagnóstico + implementação de IA + treinamento | R$3.000–R$8.000 |
| Retainer mensal | Suporte + acesso ao plugin + atualizações | R$800–R$2.000/mês |
| Plugin only | Self-service, sem consultoria | R$150–R$300/mês |

### Access control
- Sem billing/revogação nativa no Cowork
- Começar simples: gestão manual via Stripe/invoice + contrato de serviço
- Escalar depois: validação via backend API com chave por cliente

---

## Technical Architecture

### Token atual: User Access Token (via Graph API Explorer)
- Gerado no Explorador da Graph API usando o app `1829400397730969` (API for Development)
- Armazenado em `~/.claude/settings.json` como variável de ambiente
- Expira em ~1 hora (curto prazo) — trocar por token de longa duração (60 dias) futuramente

### Token ideal (futuro): System User Token (permanente)
- Gerado via Business Manager → Usuários do sistema
- Não expira enquanto o app e o usuário existirem
- A implementar quando os clientes tiverem Business Manager configurado

### MCP Oficial do Meta (futuro)
- Lançado em 29/04/2026 em `mcp.facebook.com/ads`
- 29 ferramentas prontas: campanhas, relatórios, catálogo, diagnóstico
- Ainda em rollout gradual — não disponível para todas as contas
- Quando disponível, será adicionado como caminho alternativo sem quebrar os skills existentes

---

## Token Storage (Client Side)

```json
// ~/.claude/settings.json
{
  "env": {
    "META_ACCESS_TOKEN": "EAAxxxxxxxxxx...",
    "META_AD_ACCOUNT_ID": "act_123456789"
  }
}
```

**Por que é seguro:**
- Token fica só na máquina do cliente
- Consultor nunca vê
- Claude lê em runtime, não armazena nem loga
- Cliente pode revogar/atualizar a qualquer momento

---

## Decisões Tomadas

- ✅ **Nome do plugin:** `mcf-tech-meta-ads-manager`
- ✅ **Idioma:** tudo em **português** — skills, instruções, mensagens de erro, guias. Apenas nomes de variáveis e código ficam em inglês.
- ✅ **Abordagem de dados:** Graph API diretamente via bash (token no settings.json). MCP será adicionado como alternativa futura.
- ✅ **Token:** User Access Token via Graph API Explorer usando o app do Matheus.
- ✅ **App do Meta:** clientes geram o token usando o app `1829400397730969`, garantindo permissões corretas.

---

## Skills

| Skill | Arquivo | Status | Descrição |
|---|---|---|---|
| `setup` | `skills/setup.md` | ✅ Criado | Guia de configuração: token, account ID, verificação de conexão |
| `visao-geral` | `skills/visao-geral.md` | ✅ Criado + Testado | Dashboard de todas as campanhas ativas: spend, ROAS, frequência, alertas |
| `diagnostico-campanha` | `skills/diagnostico-campanha.md` | ✅ Criado + Testado | Deep dive em uma campanha: funil completo, por conjunto e por anúncio |
| `relatorio-semanal` | `skills/relatorio-semanal.md` | ✅ Criado + Testado | Relatório last_7d com comparação vs semana anterior, ROAS delta |
| `funil-conversao` | `skills/funil-conversao.md` | ✅ Criado + Testado | Funil completo de e-commerce: impressões → compra com % por etapa |
| `alerta-frequencia` | `skills/alerta-frequencia.md` | ✅ Criado + Testado | Alerta de saturação de frequência com recomendação ROAS-aware |
| `criativos` | `skills/criativos.md` | ✅ Criado + Testado | Performance de cada anúncio: vencedor, concentração de budget, quando renovar |
| `analisar-conjuntos` | `skills/analisar-conjuntos.md` | ✅ Criado + Testado | Ad sets de uma campanha: ranking, CBO awareness, funil por conjunto |
| `comparar-periodos` | `skills/comparar-periodos.md` | ✅ Criado | Comparação entre dois períodos: esta semana vs passada, este mês vs passado |

### Campos de ação rastreados (Meta Graph API)

| Tipo de campanha | Métricas rastreadas |
|---|---|
| Vendas / Catálogo | `purchase`, `add_to_cart`, `initiate_checkout`, `add_payment_info`, `view_content`, `landing_page_view` |
| Tráfego | `outbound_clicks`, `landing_page_view` |
| Engajamento | `post_reaction`, `post_engagement`, `onsite_conversion.post_save` |
| Vídeo | `video_view`, `video_avg_time_watched_actions`, `video_p100_watched_actions` |
| Leads | `lead` |
| Seguidores ⚠️ | `page_fan` **só é rastreado em campanhas otimizadas para FOLLOWS**. Campanha de tráfego para Instagram não rastreia novos seguidores. |

---

## Learnings de Testes ao Vivo

### Dados da conta `act_863239097433106` (usada para desenvolvimento)

- **CBO**: Campanha "Catalogo Geral" usa Campaign Budget Optimization — conjuntos não têm budget individual. Exibir `"CBO (verba na campanha)"` no lugar de N/A.
- **Frequência alta + ROAS alto**: LAL da Floreart tinha 13x de frequência mas ROAS de 109x. O correto é "EXPANDIR PÚBLICO", não pausar. Skill `alerta-frequencia` trata isso.
- **Seguidores não rastreados**: Campanha "Ganhar Seguidores" é otimizada para TRAFEGO (OUTCOME_TRAFFIC), não para FOLLOWS. Por isso não retorna `page_fan`. Skills avisam sobre isso.
- **Atribuição multi-toque**: `view_content` pode superar 100% de LPV pois conta atribuição de outros canais. Normal.
- **CTR do funil**: campo `ctr` precisa estar explicitamente na query — não vem por padrão dentro de `insights{}`.

### Bugs encontrados e corrigidos

| Bug | Causa | Fix |
|---|---|---|
| Curl quebrando campos com `{spend,impressions,...}` | Bash expande chaves | Migrar 100% para Python urllib |
| CTR = 0.00% em funil-conversao | `ctr` não estava na query | Adicionado ao fields |
| ROAS enganoso em campanha de tráfego | Sem checar objetivo | Adicionado `is_sales_objective` check |
| Budget "N/A" em CBO | Ad set não tem budget próprio | Exibir `"CBO (verba na campanha)"` |
| `get_purchases.__doc__` no funil de conjuntos | Copy/paste bug | Corrigido para exibir cart/checkout/purchases |

---

## Open Questions

- [ ] Como distribuir o plugin para os clientes via Cowork? (processo manual por enquanto)
- [ ] Gestão multi-cliente: como monitorar todos os clientes de um lugar só?
- [ ] Como migrar para o MCP oficial do Meta quando estiver disponível para todas as contas?
- [ ] Como obter token de longa duração (60 dias) para os clientes? (System User Token via Business Manager)
- [ ] Skill de **orçamento**: simular redistribuição de budget entre campanhas com base em ROAS?
- [ ] Skill de **benchmarks do setor**: comparar métricas da conta com médias do segmento?

---

## Próximos Passos

1. ~~Definir o fluxo do skill `setup`~~ ✅
2. ~~Decidir: API conectada vs paste manual~~ ✅
3. ~~Construir o skill `setup`~~ ✅
4. ~~Nomear o plugin~~ ✅ → `mcf-tech-meta-ads-manager`
5. ~~Construir skills de análise~~ ✅ (9 skills criados)
6. ~~Testar ao vivo e corrigir bugs~~ ✅ (3 iterações de loop)
7. Testar o skill `comparar-periodos` ao vivo
8. Implementar token de longa duração no `setup` (System User Token)
9. Criar skill `orcamento` — simulação de redistribuição de budget por ROAS
10. Distribuir para primeiro cliente piloto via Cowork
