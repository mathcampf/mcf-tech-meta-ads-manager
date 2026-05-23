# Skill: meta-setup

## Descrição
Guia o usuário pelo processo completo de configuração da integração com a API do Meta Ads.
Ao final, verifica se a conexão está funcionando corretamente.

---

## Instruções para o Claude

Quando o usuário invocar este skill, siga **exatamente** esta sequência de passos.
Não pule etapas. Aguarde confirmação do usuário antes de avançar.
Responda sempre em português.

---

## Passo 1 — Verificar o arquivo de configuração

Verifique se o arquivo `~/.claude/settings.json` já possui as variáveis `META_ACCESS_TOKEN` e `META_AD_ACCOUNT_ID`.

- Se **não existirem**, adicione os placeholders automaticamente:

```json
"env": {
  "META_ACCESS_TOKEN": "COLE_SEU_TOKEN_AQUI",
  "META_AD_ACCOUNT_ID": "COLE_SEU_ID_DE_CONTA_AQUI"
}
```

- Se **já existirem com valores reais** (não placeholders), vá direto ao Passo 4 para verificar a conexão.

Informe o usuário o que foi feito e explique que ele precisará preencher os dois valores nos próximos passos.

---

## Passo 2 — Obter o Token de Acesso

Explique ao usuário que ele precisa gerar um token de acesso no Meta. Guie-o assim:

> **Como gerar seu token:**
>
> 1. Acesse [developers.facebook.com](https://developers.facebook.com)
> 2. No menu superior, clique em **Ferramentas** → **Explorador da Graph API**
> 3. No canto superior direito, selecione o app **"API for Development"**
> 4. Clique em **Gerar token de acesso**
> 5. Marque as permissões:
>    - `ads_read`
>    - `ads_management`
>    - `business_management`
> 6. Faça login e autorize
> 7. Copie o token gerado (começa com `EAA...`)
>
> ⚠️ **Não compartilhe este token com ninguém. Trate-o como uma senha.**

Após explicar, peça ao usuário que:
1. Abra o arquivo `~/.claude/settings.json` em qualquer editor de texto
2. Substitua `COLE_SEU_TOKEN_AQUI` pelo token copiado
3. Salve o arquivo
4. Volte e diga **"feito"** quando terminar

Aguarde a confirmação antes de continuar.

---

## Passo 3 — Obter o ID da Conta de Anúncios

Explique ao usuário que ele precisa do ID da conta de anúncios. Guie-o assim:

> **Como encontrar seu ID de conta:**
>
> **Opção A — Pelo Gerenciador de Anúncios:**
> 1. Acesse [business.facebook.com](https://business.facebook.com)
> 2. Abra o **Gerenciador de Anúncios**
> 3. Olhe a URL do navegador — você verá algo como:
>    `act_123456789`
> 4. Esse número é o seu ID de conta
>
> **Opção B — Pelo Business Manager:**
> 1. Acesse [business.facebook.com](https://business.facebook.com)
> 2. Clique em **Configurações** (ícone de engrenagem)
> 3. Vá em **Contas** → **Contas de anúncios**
> 4. O ID aparece abaixo do nome da conta

Após explicar, peça ao usuário que:
1. Abra o arquivo `~/.claude/settings.json` novamente
2. Substitua `COLE_SEU_ID_DE_CONTA_AQUI` pelo ID encontrado, no formato `act_XXXXXXXXX`
3. Salve o arquivo
4. Volte e diga **"feito"** quando terminar

Aguarde a confirmação antes de continuar.

---

## Passo 4 — Verificar a conexão

Execute os seguintes testes em sequência usando bash:

**Teste 1 — Identidade:**
```bash
curl -s "https://graph.facebook.com/v19.0/me?fields=id,name&access_token=$META_ACCESS_TOKEN"
```
Esperado: retornar `id` e `name` do usuário.

**Teste 2 — Acesso à conta de anúncios:**
```bash
curl -s "https://graph.facebook.com/v19.0/$META_AD_ACCOUNT_ID/campaigns?fields=id,name,status&limit=3&access_token=$META_ACCESS_TOKEN"
```
Esperado: retornar lista de campanhas.

---

## Passo 5 — Resultado

**Se os dois testes passarem:**
> ✅ **Configuração concluída com sucesso!**
>
> Sua conta está conectada e pronta para uso. Você já pode usar os outros recursos deste plugin para analisar campanhas, gerar relatórios e muito mais.

**Se o Teste 1 falhar (token inválido):**
> ❌ **Token inválido ou expirado.**
>
> Volte ao Passo 2 e gere um novo token no Explorador da Graph API. Tokens gerados pelo Explorer duram cerca de 1 hora. Se precisar de um token mais duradouro, peça ajuda ao consultor.

**Se o Teste 2 falhar (sem acesso à conta):**
> ❌ **Token válido, mas sem acesso à conta de anúncios.**
>
> Verifique se:
> - O ID da conta está no formato correto: `act_XXXXXXXXX`
> - Você tem acesso a essa conta de anúncios no Meta Business Manager
> - As permissões `ads_read` e `ads_management` foram marcadas ao gerar o token
